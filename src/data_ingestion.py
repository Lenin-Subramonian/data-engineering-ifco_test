from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, StringType
from pyspark.sql.functions import col, from_json, trim, when, explode, explode_outer, regexp_replace
from pyspark.sql import functions as F

def load_csv(file_path: str, spark_session: SparkSession, register_sql_view=False):
    """
    Load a CSV file into a PySpark DataFrame, clean the data for ingestion, and extract nested the JSON column.
    
    Args:
        file_path (str): Path to the CSV file.
    
    Returns:
        pyspark.sql.DataFrame: Processed DataFrame with structured contact data.

        Optionally register as SQL view.
    """
    
    # Initialize Spark session if not provided
    spark = spark_session or SparkSession.builder.appName("OrderProcessing").getOrCreate()

    # Define schema for the DataFrame
    schema = StructType([
        StructField("order_id", StringType(), True),
        StructField("date", StringType(), True),
        StructField("company_id", StringType(), True),
        StructField("company_name", StringType(), True),
        StructField("crate_type", StringType(), True),
        StructField("contact_data", StringType(), True),
        StructField("salesowners", StringType(), True)
    ])

    # Define schema for contact_data (JSON array)
    contact_schema = ArrayType(
        StructType([
            StructField("contact_name", StringType(), True),
            StructField("contact_surname", StringType(), True),
            StructField("city", StringType(), True),
            StructField("cp", StringType(), True)  # Ensuring cp is treated as String for consistency
        ])
    )

    # Read CSV file
    df = spark.read.option("header", True).option("delimiter", ";").schema(schema).csv(file_path)

    # # Clean the contact_data column by replacing "" with "
    # df_cleaned = df.withColumn("contact_data", regexp_replace(col("contact_data"), '""', '"')) \
    #                .withColumn("contact_data", regexp_replace(col("contact_data"), '^"|"$', '')) \
    #                .withColumn("contact_data", when(col("contact_data") == "", 'Unknown').otherwise(col("contact_data")))
    
    # Clean the contact_data column by replacing "" with "
    df_temp2 = df.withColumn("contact_data", regexp_replace(col("contact_data"), '""', '"'))

    # Clean the contact_data column by replacing the enclosing " with empty string
    df_temp3 = df_temp2.withColumn("contact_data", regexp_replace(col("contact_data"), '^"|"$',''))

    # Ensure empty or null values are handled before parsing
    df_cleaned = df_temp3.withColumn(
        "contact_data",
        when(col("contact_data") == "", 'Unknown').otherwise(col("contact_data")))  
    
    # After reading the CSV file, clean the 'order_id' column
    df_cleaned = df_cleaned.withColumn("order_id", F.trim(F.col("order_id")))  # Remove quotes and trim spaces)

    # Parse the contact_data column into a structured format
    df_parsed = df_cleaned.withColumn("contact_data_parsed", from_json(col("contact_data"), contact_schema))

    # Flatten JSON using explode_outer
    df_flattened = df_parsed.select(
        "order_id", 
        "date", 
        "company_id",
        "company_name", 
        "crate_type", 
        "contact_data",
        "contact_data_parsed",
        explode_outer(col("contact_data_parsed")),
        "salesowners"
    )

    # Extract fields from the parsed JSON
    df_final = df_flattened.select(
        "order_id",
        "date",
        "company_id",
        "company_name",
        "crate_type",
        col("contact_data_parsed.contact_name").alias("contact_name"),
        col("contact_data_parsed.contact_surname").alias("contact_surname"),
        col("contact_data_parsed.city").alias("contact_city"),
        col("contact_data_parsed.cp").alias("contact_cp"),
        "salesowners"  
    )

    # **Optionally register as a SQL view**
    if register_sql_view:
        df_final.createOrReplaceTempView("orders")

    return df_final  # Returns the transformed DataFrame

def load_invoices(file_path: str, spark_session: SparkSession, register_sql_view=False):

    # Initialize Spark Session
    # spark = SparkSession.builder.appName("InvoiceProcessing").getOrCreate()
    # Initialize Spark session if not provided
    spark = spark_session or SparkSession.builder.appName("OrderProcessing").getOrCreate()

    # Load JSON file
    # df = spark.read.option("multiline", "true").json("data/invoicing_data.json")
    df = spark.read.option("multiline", "true").json(file_path)

    # Extract invoices array and flatten it
    df_flattened = df.select(explode(col("data.invoices")).alias("invoice")).select(
        col("invoice.id").alias("invoice_id"),
        col("invoice.orderId").alias("order_id"),
        col("invoice.companyId").alias("company_id"),
        col("invoice.grossValue").alias("gross_value"),
        col("invoice.vat").alias("vat")
    )

    # # Register DataFrame as a SQL temporary view
    # df_flattened.createOrReplaceTempView("invoices")

    # **Optionally register as a SQL view**
    if register_sql_view:
        df_flattened.createOrReplaceTempView("invoices")

    # # # Run a Spark SQL query
    # df_invoices = spark.sql("SELECT * FROM invoices")

    # # # Show the results
    # df_invoices.show(truncate=False)
    # df_invoices.describe().show()
    
    return df_flattened  # Returns the DataFrame

# Execution for standalone script testing
# if __name__ == "__main__":
#     processed_df = load_and_process_csv("data/orders.csv")
#     processed_df = load_and_process_csv("data/orders.csv")
#     processed_df.show(truncate=False)