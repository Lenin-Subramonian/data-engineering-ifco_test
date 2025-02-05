from pyspark.sql import SparkSession

def get_company_crate_distribution(spark: SparkSession):
    """
    Calculates the distribution of crate types per company (number of orders per type) and registers it as a temporary view.
    In case of duplicate companies stored under multiple IDs, one name of the company is used - 
    (for eg: Healthy Snacks v/s Healthy Snacks Co, selected one name for the report to eliminate duplicate. 

    :param spark: SparkSession object
    :return: Transformed DataFrame with crate type distribution per company.
    """
    sql_query = f"""
        WITH get_unique_company_name as 
        (
            select Company_id, company_name 
            from (
                select company_id, company_name, ROW_NUMBER() OVER (PARTITION BY Company_id ORDER BY company_name asc) AS row_num 
                from orders_vw
                )
            where row_num=1
        )
        SELECT 
            ord.company_id,
            gc.company_name, 
            ord.crate_type, 
            count(ord.order_id) as crate_type_distribution 
        FROM orders_vw ord inner join get_unique_company_name gc on ord.company_id = gc.company_id
        GROUP BY 1, 2, 3
        ORDER BY 1, 2
    """

    df_company_crate_distribution = spark.sql(sql_query)
    # df_company_crate_distribution.createOrReplaceTempView("crate_distribution_vw")
    
    return df_company_crate_distribution  # Return DataFrame for further use

def get_orders_contact_full_name(spark: SparkSession):
    """
    DataFrame containing the following columns:
    1. order_id - The order_id field must contain the unique identifier of the order.
    2. contact_full_name - The contact_full_name field must contain the full name of the contact. 
    In case this information is not available, the placeholder "John Doe" should be utilized.

    :param spark: SparkSession object
    :return: Transformed DataFrame order and full name.
    """
    df_1 = spark.sql("SELECT order_id, contact_full_name  FROM orders_vw group by 1, 2")

    # df_1.createOrReplaceTempView("crate_distribution_vw")
    
    return df_1  # Return DataFrame for further use

def get_orders_contact_address(spark: SparkSession):
    """
    DataFrame containing the following columns:
    1. order_id - The order_id field must contain the unique identifier of the order.
    2. contact_full_name - The field for contact_address should adhere to the following information and format: "city name, postal code". 
            In the event that the city name is not available, the placeholder "Unknown" should be used. 
            Similarly, if the postal code is not known, the placeholder "UNK00" should be used.

    :param spark: SparkSession object
    :return: Transformed DataFrame order and contact address.
    """
    df_2 = spark.sql("SELECT order_id, contact_city || ','||contact_cp as contact_address FROM orders_vw")

    # df_2.createOrReplaceTempView("crate_distribution_vw")
    
    # Return DataFrame for further use
    return df_2  

def get_company_saleowner_list(spark: SparkSession):
    """
    DataFrame of Companies with Sales Owners
        Requirements:
        1. company_id - The company_id field must contain the unique identifier of the company.
        2. company_name - The company_name field must contain the name of the company.
        3. list_salesowners - The list_salesowners field should contain a unique and comma-separated list of salespeople 
            who have participated in at least one order of the company. 
        4. Please ensure that the list is sorted in ascending alphabetical order of the first name. 

    :param spark: SparkSession object
    :return: Transformed DataFrame with crate type distribution per company.
    """
    sql_query = f"""
        SELECT 
            Company_id, 
            company_name, 
            CONCAT_WS(', ', SORT_ARRAY(COLLECT_LIST(salesowner))) AS list_salesowners
        FROM salesowners_vw
            GROUP BY Company_id, company_name
            order by 3 asc
    """

    df_3 = spark.sql(sql_query)
    # df_3.createOrReplaceTempView("crate_distribution_vw")
    
    # Return DataFrame for further use
    return df_3  

def get_saleowner_commission(spark: SparkSession):
    """
    Calculation of Sales Team Commissions¶
    Requirements:
    - Provide a list of the distinct sales owners and their respective commission earnings. 
    - The list should be sorted in order of descending performance, with the sales owners who have generated the highest commissions appearing first.
    - Raw amounts are represented in cents. Please provide euro amounts with two decimal places in the results 

    :param spark: SparkSession object
    :return: Transformed DataFrame with sales and commission in EURO.
    """
    sql_query = f"""
        WITH aa as (
            select 
             primary_owner, co_owner_1, co_owner_2, gross_value, primary_commission_euro, 
             co_owner_1_commission_euro, co_owner_2_commission_euro
            from sales_owner_commission_vw
            ),
            bb as (
            SELECT primary_owner AS sales_owner, primary_commission_euro AS commission 
            FROM aa
            WHERE primary_owner IS NOT NULL
            
            UNION ALL
            
            SELECT co_owner_1 AS sales_owner, co_owner_1_commission_euro AS commission 
            FROM aa
            WHERE co_owner_1 IS NOT NULL
            
            UNION ALL
            
            SELECT co_owner_2 AS sales_owner, co_owner_2_commission_euro AS commission 
            FROM aa
            WHERE co_owner_2 IS NOT NULL
            )
            select sales_owner, round(sum(commission), 2) as total_commission
            from bb
            group by 1
            order by 2 desc
    """

    df_total_sales_comm = spark.sql(sql_query)
    # df_total_sales_comm.createOrReplaceTempView("total_sales_comm_vw")
    
    # Return DataFrame for further use
    return df_total_sales_comm  

def get_salesowner_list_for_training(spark: SparkSession):
    """
    Create data set for "Which sales owners need most training to improve selling on plastic crates, based on the last 12 months orders?". 

    :param spark: SparkSession object
    """
    sql_query = f"""
        SELECT 
            salesowner,
            crate_type,
            count(order_id) as order_count
        FROM order_sales_owner_vw 
            where formatted_date >= add_months(current_date(), -12)
        group by 1,2
    """

    df_salesowner_list_for_training = spark.sql(sql_query)
    # df_3.createOrReplaceTempView("crate_distribution_vw")
    
    # Return DataFrame for further use
    return df_salesowner_list_for_training 

def get_salesowner_top_5(spark: SparkSession):
    """
    Create data set for "Understand who are by month the top 5 performers selling plastic crates for a rolling 3 months evaluation window?

    :param spark: SparkSession object
    """
    sql_query = f"""
        WITH ranked_sales AS 
     (
        SELECT
            month,
            salesowner,
            crate_type,
            count(order_id) AS total_sales,
            ROW_NUMBER() OVER (PARTITION BY month ORDER BY count(order_id) DESC) AS rank
        FROM
                order_sales_owner_vw
        WHERE
            crate_type = 'Plastic'
            and formatted_date >= add_months(current_date(), -12)
            -- and company_id='1e2b47e6-499e-41c6-91d3-09d12dddfbbd'
            -- company_id in ('27c59f76-5d26-4b82-a89b-59f8dfd2e9a7', '20dfef10-8f4e-45a1-82fc-123f4ab2a4a5')
        group by 1,2,3
        ),
      rolling_sales AS 
      (
            SELECT
                month,
                salesowner,
                crate_type,
                total_sales,
                rank,
                COUNT(*) OVER (PARTITION BY salesowner ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_sales
            FROM
                ranked_sales
        )
        SELECT
            month,
            salesowner,
            total_sales
        FROM
            rolling_sales
        WHERE
            rank <= 5
        ORDER BY
            total_sales desc  
        limit 5
    """

    df_top_5 = spark.sql(sql_query)
    # df_3.createOrReplaceTempView("crate_distribution_vw")
    
    # Return DataFrame for further use
    return df_top_5 

def get_crate_order_distribution(spark: SparkSession):
    """
    Create data set for "What is the distribtion of orders by crate type 

    :param spark: SparkSession object
    :return: Transformed DataFrame with crate type distribution per company.
    """
    df_crate_order_distribution = spark.sql("SELECT crate_type, count(order_id) as order_count FROM orders_vw group by 1")
    
    # Return DataFrame for further use
    return df_crate_order_distribution  
