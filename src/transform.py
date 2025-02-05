from pyspark.sql import SparkSession
from src.data_ingestion import load_csv, load_invoices

def transform_orders(spark: SparkSession):
    """
    Transforms the orders dataset and creates a SQL view for downstream usage.
    :param spark: SparkSession object

    """
    sql_query = f"""
        SELECT 
            order_id, 
            date, 
            company_id,
            company_name, 
            crate_type,
            contact_name[0] AS contact_name,  
            contact_surname[0] AS contact_surname, 
            NVL((contact_name[0] || ' ' || contact_surname[0]), 'John Doe') AS contact_full_name,
            NVL(contact_city[0], 'Unknown') AS contact_city, 
            NVL(contact_cp[0], 'UNK00') AS contact_cp, 
            salesowners
        FROM orders
    """
    
    # Execute SQL query
    df_trans = spark.sql(sql_query)
    
    # Register as a temporary view
    df_trans.createOrReplaceTempView("orders_vw")
    
    return df_trans  # Return the transformed DataFrame if needed

def salesowners_normalized_view(spark: SparkSession):
    """
    Create a normalized view of sales owners. One row per sales owner,
    :param spark: SparkSession object

    """
    sql_query = f"""
        WITH get_salesowners as 
            (
            SELECT 
                Company_id,
                company_name,
                TRIM(salesowner) AS salesowner
            FROM (
                SELECT 
                    Company_id, 
                    company_name, 
                    EXPLODE(SPLIT(salesowners, ',')) AS salesowner
                FROM orders_vw 
                    )
                group by 1,2,3
            ),
            get_unique_salesowners as 
            (
            SELECT 
                Company_id, 
                salesowner
                FROM get_salesowners 
                group by 1,2
            ),
            get_unique_company as 
            (
            select Company_id, company_name 
            from (
                select Company_id, company_name, ROW_NUMBER() OVER (PARTITION BY Company_id ORDER BY company_name) AS row_num 
                from get_salesowners
                )
            where row_num=1
            )
            Select gs.Company_id, gc.company_name, gs.salesowner
            from get_unique_salesowners gs inner join get_unique_company gc on gs.Company_id = gc.Company_id
            order by 1, 3 asc
    """
    
    # Execute SQL query
    df_sales_owners = spark.sql(sql_query)
    
    # Register as a temporary view
    df_sales_owners.createOrReplaceTempView("salesowners_vw")
    
    # Return the transformed DataFrame if needed
    return df_sales_owners 

def sales_owner_commission_view(spark: SparkSession):
    """
    1. Identify the primary sales owner, Co-owner 1 (second in the list), Co-owner 2 (third in the list) who have contributed to the acquisition process.
    2. Join Orders and Invoices based on the order ID, and get the invoiced value. * - Assumption: VAT is not included in the calculation as the details are not clear. *
    3. Calculate the commissions based on the below procedure:
            - Main Owner: 6% of the net invoiced value.
            - Co-owner 1 (second in the list): 2.5% of the net invoiced value.
            - Co-owner 2 (third in the list): 0.95% of the net invoiced value.
            - The rest of the co-owners do not receive anything.
    4. Raw amounts are represented in cents. Provide euro amounts with two decimal places in the results

    Dependency: Orders, Orders_vw, invoices
    
    :param spark: SparkSession object

    """
    sql_query = f"""
            with get_salesowners as 
    (
        SELECT 
            Order_id,
            Company_id, 
            company_name, 
            salesowners
        FROM orders_vw 
    ),
    sales_commission_team as
     (
         SELECT 
            Order_id,
            Company_id,
            company_name,
            SPLIT(salesowners, ', ')[0] AS primary_owner,
            SPLIT(salesowners, ', ')[1] AS co_owner_1,
            SPLIT(salesowners, ', ')[2] AS co_owner_2
        FROM get_salesowners
        ), 
    get_invoice 
    (
        SELECT 
            sct.Order_id,
            sct.Company_id,
            sct.company_name,
            sct.primary_owner,
            sct.co_owner_1,
            sct.co_owner_2,
            inv.invoice_id,
            inv.gross_value,
            inv.vat
        from sales_commission_team sct inner join invoices inv on sct.Order_id=inv.order_id           
    )
    select 
        Order_id,
        Company_id,
        company_name,
        primary_owner,
        co_owner_1,
        co_owner_2,
        invoice_id,
        gross_value,
        vat,
        (case when primary_owner is not null 
            then round((gross_value * .06)/100,2) else 0 end) as primary_commission_euro,
        (case when co_owner_1 is not null 
            then round((gross_value * .025)/100,2) else 0 end) as co_owner_1_commission_euro,
        (case when co_owner_2 is not null 
            then round((gross_value * .0095)/100,2) else 0 end) as co_owner_2_commission_euro
    from get_invoice
    """
    
    # Execute SQL query
    df_sales_owner_commission = spark.sql(sql_query)
    
    # Register as a temporary view
    df_sales_owner_commission.createOrReplaceTempView("sales_owner_commission_vw")
    
    # Return the transformed DataFrame if needed
    return df_sales_owner_commission 

def order_sales_owners_view(spark: SparkSession):
    """
    Create a normalized view of sales owners and orders..
    :param spark: SparkSession object

    """
    sql_query = f"""
        WITH aa as 
        (
        SELECT 
            order_id, 
            date, 
            company_id,
            company_name, 
            crate_type,
            contact_name,  
            contact_surname, 
            contact_full_name,
            contact_city, 
            contact_cp, 
            EXPLODE(SPLIT(salesowners, ', ')) AS salesowner
        FROM orders_vw 
        )
        SELECT distinct 
            order_id, 
            CAST(TO_TIMESTAMP(date, 'dd.MM.yy') AS DATE) as formatted_date, 
            month(CAST(TO_TIMESTAMP(date, 'dd.MM.yy') AS DATE)) as month,
            company_id,
            company_name, 
            crate_type,
            contact_name,  
            contact_surname, 
            contact_full_name,
            contact_city, 
            contact_cp, 
            TRIM(salesowner) AS salesowner
        FROM aa
    """
    
    # Execute SQL query
    df_order_sales_owner = spark.sql(sql_query)
    
    # Register as a temporary view
    df_order_sales_owner.createOrReplaceTempView("order_sales_owner_vw")
    
    # Return the transformed DataFrame if needed
    return df_order_sales_owner  

# # Usage example:
# df_orders = load_csv("data/orders.csv", spark, register_sql_view=True)
# df_trans = transform_orders(spark)

# df_trans.show(truncate=False)
# df_trans.describe().show()
