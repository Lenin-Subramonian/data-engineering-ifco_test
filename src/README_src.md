
# IFCO Data Application

## main.py 
  Main function to orchestrate the data processing workflow.

## Data Ingestion.
     
  ### data_ingestion.py
  
  **load_csv**
  
  -  Ingest order data (CSV) into a data frame, clean the data to flatten the nested JSON (contact_data) , and optionally create a view, `orders`.
  -  param:file_path (str): Path to the CSV file, SparkSession, view creation flag
  -  returns: pyspark.sql.DataFrame: Processed DataFrame with structured order and contact data.
          
![image](https://github.com/user-attachments/assets/1ac03995-f186-4819-8a9c-f05eebe11b01)
     
  **load_invoices**
  -  Ingest invoices data (JSON) into a data frame, and create a view, `invoices`.
  -  param:file_path (str): Path to the CSV file, SparkSession, view creation flag
  -  Returns: pyspark.sql.DataFrame: Processed DataFrame with structured order and contact data.

  ![image](https://github.com/user-attachments/assets/6673db69-99db-4cd8-8296-89ce65739c09)

     
## Transform and business rules.

  ###  transform.py**
  
  **transform_orders** 
  
  -  Transforms the orders dataset and creates a SQL view, `ORDERS_VW` for downstream usage. Param: SparkSession object
  -  Below transformations and data quality rules are applied. 
    -  The contact_full_name field must contain the full name of the contact. In case this information is not available, the placeholder "John Doe" should be utilized.
    -  The field for contact_address should adhere to the following information and format: "city name, postal code". 
    -  In the event that the city name is not available, the placeholder "Unknown" should be used. 
    -  Similarly, if the postal code is not known, the placeholder "UNK00" should be used.
      
  ![image](https://github.com/user-attachments/assets/d519fc83-356a-4cdb-851e-9152a504f7d1)
    
  **salesowners_normalized_view**
  
  - `SALESOWNERS_VW` - Create a de-normalized view of sales owners. One row per sales owner, :param spark: SparkSession object
  - Highlevel Approach:
            1. SPLIT(salesowners, ', ') → Splits the salesowners string into an array based on , (comma and space).
            2. EXPLODE() → Converts the array into multiple rows (one for each name).
            3. TRIM(salesowner) → Removes any leading or trailing spaces from names
            
 ![image](https://github.com/user-attachments/assets/63f588bb-898d-4584-be5a-02d1ba9d32a6)

  **sales_owner_commission_view**
  
  -  `SALES_OWNER_COMMISSION_VW` - Create a salesowners commission View.
  -  Logic: 
        1. Identify the primary sales owner, Co-owner 1 (second in the list), Co-owner 2 (third in the list) who have contributed to the acquisition process.
        2. Join Orders and Invoices based on the order ID, and get the invoiced value. * - Assumption: VAT is not included in the calculation as the details are not clear. *
        3. Calculate the commissions based on the below procedure:
                - Main Owner: 6% of the net invoiced value.
                - Co-owner 1 (second in the list): 2.5% of the net invoiced value.
                - Co-owner 2 (third in the list): 0.95% of the net invoiced value.
                - The rest of the co-owners do not receive anything.
        4. Raw amounts are represented in cents. Provide euro amounts with two decimal places in the results
        
  ![image](https://github.com/user-attachments/assets/3f3e1060-cfb0-429c-ada7-c41eb1eb7450)

  **order_sales_owners_view** 
  
  - Create a de-normalized view, `ORDER_SALES_OWNER_VW` of sales owners and orders - one sale owner per row, :param spark: SparkSession object
     
  ![image](https://github.com/user-attachments/assets/34bb46c1-86f0-431d-bbb5-a8253da6893d)

### data_analysis.py

**get_company_crate_distribution**

-  Calculates the distribution of crate types per company (number of orders per type) and registers it as a temporary view.
-  In case of duplicate companies stored under same IDs with different name, one name of the company is used - for eg: Healthy Snacks v/s Healthy Snacks Co, selected one name for the report to eliminate duplicate. 
- :param spark: SparkSession object, :return: Transformed DataFrame with crate type distribution per company.
	
	
**get_orders_contact_full_name**

-  Returns DataFrame containing the following columns:
    1. order_id - The order_id field must contain the unique identifier of the order.
    2. contact_full_name - The contact_full_name field must contain the full name of the contact. In case this information is not available, the placeholder "John Doe" should be utilized.
-  :param spark: SparkSession object, :return: Transformed DataFrame.
  
**get_orders_contact_address**

- Returns DataFrame containing the following columns:
    1. order_id - The order_id field must contain the unique identifier of the order.
    2. contact_full_name - The field for contact_address should adhere to the following information and format: "city name, postal code". In the event that the city name is not available, the placeholder "Unknown" should be used.
    3. Similarly, if the postal code is not known, the placeholder "UNK00" should be used.
	
**get_company_saleowner_list** 

- Returns DataFrame of Companies with Sales Owners
    1. company_id - The company_id field must contain the unique identifier of the company.
    2. company_name - The company_name field must contain the name of the company.
    3. list_salesowners - The list_salesowners field should contain a unique and comma-separated list of salespeople who have participated in at least one order of the company. 
    4. Please ensure that the list is sorted in ascending alphabetical order of the first name. 

**get_saleowner_commission** 

-  Calculation of Sales Team Commissions¶
-  Provide a list of the distinct sales owners and their respective commission earnings.
-  The list should be sorted in order of descending performance, with the sales owners who have generated the highest commissions appearing first.
-  Raw amounts are represented in cents. Please provide euro amounts with two decimal places in the results 

    :param spark: SparkSession object, :return: Transformed DataFrame with sales and commission in EURO.

**get_salesowner_list_for_training**

-  Create data set for "Which sales owners need most training to improve selling on plastic crates, based on the last 12 months orders?". 
    :param spark: SparkSession object

**get_salesowner_top_5**

- Create data set for "Understand who are by month the top 5 performers selling plastic crates for a rolling 3 months evaluation window?
- :param spark: SparkSession object
	
**get_crate_order_distribution**

- Create data set for "What is the distribtion of orders by crate type
- :param spark: SparkSession object, :return: Transformed DataFrame with crate type distribution per company.










 
