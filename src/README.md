
# IFCO Data Application
  ## Problem Statement

Analyze and assisting IFCO's Data Team in the analysis of some business data. For this purpose, you have been provided with two files:
1. orders.csv (which contains facmtual information regarding the orders received)
2. invoicing_data.json (which contains invoicing information)
  
For this exercise, you can only use Python, PySpark or SQL (e.g. in dbt). Unit testing is essential for ensuring the reliability and correctness of your code. 
Please include appropriate unit tests for each task.

## Highlevel Solution & Approach
  1. Data Ingestion.
     -  Ingest orders data (CSV) into a dataframe.
         - Clean the source data for ingestion such as removing special characters etc. 
     -  Ingest invoices data (JSON) into a data frame, and create a view, invoices.
  2. Transform, apply business rules and create views. 
     - `ORDERS_VW` - Create base view with business rules. 
     - `SALESOWNERS_VW` - Create a de-normalized view of sales owners.
     - `SALES_OWNER_COMMISSION_VW` - Create a salesowners commission View
     - `ORDER_SALES_OWNER_VW` - Create a de-normalised view of order and sales owners - a record per order & sales owner.
 3. Generate datasets for each use case using the views. 
    -  Test 1: Distribution of Crate Type per Company
    -  Test 2: DataFrame of Orders with Full Name of the Contact
    -  Test 3: DataFrame of Orders with Contact Address
    -  Test 4: Calculation of Sales Team Commissions
    -  Test 5: DataFrame of Companies with Sales Owners
    -  Test 6: Data Visualization

## Getting Started

### Dependencies
  - Ubuntu 24.04.1 LTS or Ensure WSL 2 (Windows Subsystem for Linux)
  - Java openjdk-11-jdk and set JAVA_HOME=/usr/lib/jvm/java-1.11.0-openjdk-amd64
  - Set PYTHONPATH=$(pwd)/src:$PYTHONPATH (to execute the /src files. 

**Core dependencies**
  - pandas
  - pyspark
  - urllib3
  - streamlit
    
**Jupyter dependencies**
  - notebook
  - jupyterlab
  - ipykernel
  - ipywidgets
  - matplotlib

**Additional dependencies**
  - requests


### Installing
  **Install Docker on Windows**
    - Install Docker Desktop for Windows.
    - Ensure WSL 2 (Windows Subsystem for Linux) is enabled, as it's recommended for running Linux containers.
Pull the Image from a Registry
```
docker pull mooney042/ifco-data-app:latest
```
Run the Image on Windows:
If the image is a Linux-based image, it will run fine on Windows if Docker is set to run Linux containers (which is the default with WSL 2).
```
docker run -it --rm -p 8888:8888 -p 8501:8501 mooney042/ifco-data-app:latest
```


### Executing Program
Access Jupyter and Streamlit by navigating to:
Jupyter: http://localhost:8888
Streamlit: http://localhost:8501

### Assumptions




Orders
  root
   |-- order_id: string (nullable = true)
   |-- date: string (nullable = true)
   |-- company_id: string (nullable = true)
   |-- company_name: string (nullable = true)
   |-- crate_type: string (nullable = true)
   |-- contact_name: array (nullable = true)
   |    |-- element: string (containsNull = true)
   |-- contact_surname: array (nullable = true)
   |    |-- element: string (containsNull = true)
   |-- contact_city: array (nullable = true)
   |    |-- element: string (containsNull = true)
   |-- contact_cp: array (nullable = true)
   |    |-- element: string (containsNull = true)
   |-- salesowners: string (nullable = true)
Invoices

  root
 |-- invoice_id: string (nullable = true)
 |-- order_id: string (nullable = true)
 |-- company_id: string (nullable = true)
 |-- gross_value: string (nullable = true)
 |-- vat: string (nullable = true)

## Create a Order View (ORDER_VW)
Apply below transformations:
1. The contact_full_name field must contain the full name of the contact. In case this information is not available, the placeholder "John Doe" should be utilized.
2. The field for contact_address should adhere to the following information and format: "city name, postal code". 
3. In the event that the city name is not available, the placeholder "Unknown" should be used. 
4. Similarly, if the postal code is not known, the placeholder "UNK00" should be used.
root
 |-- order_id: string (nullable = true)
 |-- date: string (nullable = true)
 |-- company_id: string (nullable = true)
 |-- company_name: string (nullable = true)
 |-- crate_type: string (nullable = true)
 |-- contact_name: string (nullable = true)
 |-- contact_surname: string (nullable = true)
 |-- contact_full_name: string (nullable = false)
 |-- contact_city: string (nullable = false)
 |-- contact_cp: string (nullable = false)
 |-- salesowners: string (nullable = true)
   
Order_vw

## Create a Salesowners View (SALESOWNERS_VW)¶
Create a de-normalized view of sales owners.
Highlevel Approach:
1. SPLIT(salesowners, ', ') → Splits the salesowners string into an array based on , (comma and space).
2. EXPLODE() → Converts the array into multiple rows (one for each name).
3. TRIM(salesowner) → Removes any leading or trailing spaces from names

   root
 |-- Company_id: string (nullable = true)
 |-- company_name: string (nullable = true)
 |-- salesowner: string (nullable = false)

   
salesowners_vw

## Create a Salesowners Commission View (sales_owner_commission_vw)¶
Create a view of sales owners.
Highlevel Approach:
Identify the primary sales owner, Co-owner 1 (second in the list), Co-owner 2 (third in the list) who have contributed to the acquisition process.
Join Orders and Invoices based on the order ID, and get the invoiced value. * - Assumption: VAT is not included in the calculation as the details are not clear. *
Calculate the commissions based on the below procedure:
Main Owner: 6% of the net invoiced value.
Co-owner 1 (second in the list): 2.5% of the net invoiced value.
Co-owner 2 (third in the list): 0.95% of the net invoiced value.
The rest of the co-owners do not receive anything.
Raw amounts are represented in cents. Provide euro amounts with two decimal places in the results
Columns for the view: Order_id, Company_id, company_name, primary_owner, co_owner_1, co_owner_2, invoice_id, gross_value, primary_commission_euro, co_owner_1_commission_euro, co_owner_2_commission_euro

sales_owner_commission_vw
root
 |-- Order_id: string (nullable = true)
 |-- Company_id: string (nullable = true)
 |-- company_name: string (nullable = true)
 |-- primary_owner: string (nullable = true)
 |-- co_owner_1: string (nullable = true)
 |-- co_owner_2: string (nullable = true)
 |-- invoice_id: string (nullable = true)
 |-- gross_value: string (nullable = true)
 |-- vat: string (nullable = true)
 |-- primary_commission_euro: double (nullable = true)
 |-- co_owner_1_commission_euro: double (nullable = true)
 |-- co_owner_2_commission_euro: double (nullable = true)

## Create a Order_Sales_owner View (order_sales_owner_vw)¶
Create a de-normalized view of sales owners and orders.
Columns:
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
    salesowner (one sale owner per row) 
order_sales_owner_vw

root
 |-- order_id: string (nullable = true)
 |-- formatted_date: date (nullable = true)
 |-- month: integer (nullable = true)
 |-- company_id: string (nullable = true)
 |-- company_name: string (nullable = true)
 |-- crate_type: string (nullable = true)
 |-- contact_name: string (nullable = true)
 |-- contact_surname: string (nullable = true)
 |-- contact_full_name: string (nullable = false)
 |-- contact_city: string (nullable = false)
 |-- contact_cp: string (nullable = false)
 |-- salesowner: string (nullable = false)

 
