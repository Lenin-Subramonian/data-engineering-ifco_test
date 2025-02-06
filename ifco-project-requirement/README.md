<br />
<br />

<p align="center">
  <img src=".images/video-call.png" alt="ifco data engineering test challenge" width="80" height="80">
</p>


<h1 align="center">
  <b>
    IFCO Data Engineering Challenge
  </b>
</h1>

<br />


## Problem Statement

You have been assigned the responsibility of assisting IFCO's Data Team in the analysis of some business data. For this purpose, you have been provided with two files:

* [orders.csv](resources/orders.csv) (which contains factual information regarding the orders received)
* [invoicing_data.json](resources/invoicing_data.json) (which contains invoicing information)

Explore the raw data and provide the code (well-commented) to answer the following questions/scenarios. For this exercise, you can only use Python, PySpark or SQL (e.g. in dbt). **Unit testing is essential** for ensuring the reliability and correctness of your code. Please include appropriate unit tests for each task.

### Test 1: Distribution of Crate Type per Company

Calculate the distribution of crate types per company (number of orders per type). **Ensure to include unit tests** to validate the correctness of your calculations.

### Test 2: DataFrame of Orders with Full Name of the Contact

Provide a DataFrame (`df_1`) containing the following columns:

| Column            | Description                                                                                                                                                                |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| order_id          | The `order_id` field must contain the unique identifier of the order.                                                                                                       |
| contact_full_name | The `contact_full_name` field must contain the full name of the contact. In case this information is not available, the placeholder "John Doe" should be utilized. |

**Include unit tests** to verify that the full names are correctly extracted and the placeholder is used appropriately.

### Test 3: DataFrame of Orders with Contact Address

Provide a DataFrame (`df_2`) containing the following columns:

| Column          | Description                                                                                                                                                                                                                                                                                    |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| order_id        | The `order_id` field must contain the unique identifier of the order.                                                                                                                                                                                                                            |
| contact_address | The field for `contact_address` should adhere to the following information and format: "city name, postal code". In the event that the city name is not available, the placeholder "Unknown" should be used. Similarly, if the postal code is not known, the placeholder "UNK00" should be used. |

**Ensure to include unit tests** to validate the address formatting and placeholder logic.

### Test 4: Calculation of Sales Team Commissions

The Sales Team requires your assistance in computing the commissions. It is possible for multiple salespersons to be associated with a single order, as they may have participated in different stages of the order. The `salesowners` field comprises a ranked list of the salespeople who have ownership of the order. The first individual on the list represents the primary owner, while the subsequent individuals, if any, are considered co-owners who have contributed to the acquisition process. The calculation of commissions follows a specific procedure:

- Main Owner: 6% of the net invoiced value.
- Co-owner 1 (second in the list): 2.5% of the net invoiced value.
- Co-owner 2 (third in the list): 0.95% of the net invoiced value.
- The rest of the co-owners do not receive anything.

Provide a list of the distinct sales owners and their respective commission earnings. The list should be sorted in order of descending performance, with the sales owners who have generated the highest commissions appearing first.

**Hint:** Raw amounts are represented in cents. Please provide euro amounts with two decimal places in the results.

**Include unit tests** to verify the correctness of the commission calculations and sorting order.

### Test 5: DataFrame of Companies with Sales Owners

Provide a DataFrame (`df_3`) containing the following columns:

| Column           | Description                                                                                                                                                                                                                                       |
|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| company_id       | The `company_id` field must contain the unique identifier of the company.                                                                                                                                                                         |
| company_name     | The `company_name` field must contain the name of the company.                                                                                                                                                                                    |
| list_salesowners | The `list_salesowners` field should contain a unique and comma-separated list of salespeople who have participated in at least one order of the company. Please ensure that the list is sorted in ascending alphabetical order of the first name. |

**Hint:** Consider the possibility of duplicate companies stored under multiple IDs in the database. Take this into account while devising a solution to this exercise.

**Ensure to include unit tests** to validate the uniqueness and sorting of the sales owners list, and the handling of duplicate companies.

### Test 6: Data Visualization (you don't need to submit a solution to this test if not explicitly asked for)

The Sales team wants to understand which sales owners are particularly successful in creating orders in plastic crates. Create a set of appropriate visualizations / reports that help your stakeholders to understand the following aspects better:

- What is the distribtion of orders by crate type.
- Which sales owners need most training to improve selling on plastic crates, based on the last 12 months orders.
- Understand who are by month the top 5 performers selling plastic crates for a rolling 3 months evaluation window.

You can use Python or Power BI for this test.

## Additional Instructions

1. **Deliverables**: Ensure your code is well-commented and structured. Provide a complete execution environment as a deliverable. This should include:
   - All the source code and scripts necessary to reproduce the results.
   - Clear instructions for setting up and running the environment, including any necessary configurations.
   - A Dockerfile, if applicable, for containerized execution.
   - A link to a Git repository containing all the above elements and ensure that access is granted to @theUniC, @carlosbuenosvinos and @ahue.
2. **Evaluation**: Your solution will be evaluated based on accuracy, efficiency, code clarity, the comprehensiveness of your unit tests, and the completeness of the provided execution environment.

Good luck!
