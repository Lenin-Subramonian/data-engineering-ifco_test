import pandas as pd
from pyspark.sql import SparkSession
from src.data_ingestion import load_csv
from src.data_ingestion import load_csv, load_invoices
from src.transform import transform_orders,salesowners_normalized_view,sales_owner_commission_view, order_sales_owners_view
import src.data_analysis as da 

def main():
    """Main function to orchestrate the data processing workflow."""
    
    # Step 1: Initialize Spark Session
    spark = SparkSession.builder.master("local").appName("IFCO-OrderInvoiceProcessing").getOrCreate()
    
    # Step 2: Ingest order data
    df_orders = load_csv("data/orders.csv", spark, register_sql_view=True)
    
    # Step 2.1: Ingest invoice data
    df_orders = load_invoices("data/invoicing_data.json", spark, register_sql_view=True)
    
    # Step 3: Transform data & Register as a temporary view for analysis. 
    df_trans = transform_orders (spark)
    df_trans.createOrReplaceTempView("orders_vw")
    
    df_sales_owners = salesowners_normalized_view(spark)
    df_sales_owners.createOrReplaceTempView("salesowners_vw")

    df_sales_owner_commission = sales_owner_commission_view (spark)
    df_sales_owner_commission.createOrReplaceTempView("sales_owner_commission_vw")
    
    # Step 4: Execute the data analysis result (or save it as needed)
        
    df_company_crate_distribution = da.get_company_crate_distribution(spark)
    df_company_crate_distribution.show(truncate=False)

    df_1 = da.get_orders_contact_full_name(spark)
    df_1.show(truncate=False)

    df_2 = da.get_orders_contact_address(spark)
    df_2.show(truncate=False)

    df_3 = da.get_company_saleowner_list(spark)
    df_3.show(truncate=False)

    df_total_sales_commission = da.get_saleowner_commission(spark)
    df_total_sales_commission.show(truncate=False)

    # Step 5: Data for Streamlit Visualization. 
    # 5.1  Create data set for "What is the distribtion of orders by crate type.
    df_crate_order_distribution = da.get_crate_order_distribution (spark)
    df_crate_order_distribution.show(truncate=False)
    # Convert to Pandas for Streamlit
    df_crate_order = df_crate_order_distribution.toPandas()
    # Save DataFrame as CSV inside the container
    df_crate_order.to_csv("/app/data/crate_order_distribution.csv", index=False)

    # 5.2  Create data set for "Which sales owners need most training to improve selling on plastic crates, based on the last 12 months orders?"
    df_order_sales_owner= order_sales_owners_view(spark)
    df_order_sales_owner.show(truncate=False)
    df_order_sales_owner.createOrReplaceTempView("order_sales_owner_vw")

    df_salesowner_list_for_training = da.get_salesowner_list_for_training (spark)
    df_salesowner_list_for_training.show(truncate=False)
    # Convert to Pandas for Streamlit
    df_sales_crate_distribution = df_salesowner_list_for_training.toPandas()
    # Save DataFrame as CSV inside the container
    df_sales_crate_distribution.to_csv("/app/data/crate_sale_distribution.csv", index=False)

    # 5.2  Create data set for "Understand who are by month the top 5 performers selling plastic crates for a rolling 3 months evaluation window."
    df_top_5 = da.get_salesowner_top_5(spark)
    df_top_5.show(truncate=False)
    # Convert to Pandas for Streamlit
    df_top_5_sales = df_salesowner_list_for_training.toPandas()
    # Save DataFrame as CSV inside the container
    df_top_5_sales.to_csv("/app/data/sales_top_5.csv", index=False)

    # Optional: Stop Spark session (only if running standalone)
    spark.stop()

if __name__ == "__main__":
    main()