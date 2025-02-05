import unittest
from pyspark.sql import SparkSession
from pyspark.sql import Row
from src.data_ingestion import load_csv, load_invoices
from src.transform import transform_orders,salesowners_normalized_view,sales_owner_commission_view
from src.data_analysis import get_company_crate_distribution, get_company_saleowner_list, get_saleowner_commission

class TestCrateDistribution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize Spark session for testing"""
        cls.spark = SparkSession.builder.master("local").appName("TestDataAnalysis").getOrCreate()

    def setUp(self):
        """Prepare test data before each test"""
        self.test_data = [
            Row(order_id=1, company_id=101, company_name="ABC Corp", crate_type="Plastic", salesowners ="Leonard Cohen, Luke Skywalker, Ammy Winehouse"),
            Row(order_id=2, company_id=101, company_name="ABC Corp", crate_type="Plastic", salesowners ="Luke Skywalker, Chris Pratt"),
            Row(order_id=3, company_id=101, company_name="ABC Corp", crate_type="Wood", salesowners ="Leonard Cohen, Luke Skywalker, Ammy Winehouse"),
            Row(order_id=4, company_id=102, company_name="XYZ Ltd", crate_type="Plastic", salesowners ="Luke Skywalker"),
            Row(order_id=5, company_id=102, company_name="XYZ Ltd z", crate_type="Metal", salesowners ="David Henderson, Leon Leonov"),
            Row(order_id=6, company_id=102, company_name="XYZ Ltd", crate_type="Metal", salesowners ="Leonard Cohen"),
        ]

        self.test_invoices = [
            Row(invoice_id=11, order_id=1,company_id=101, gross_value="341315", vat="0"),
            Row(invoice_id=22, order_id=2,company_id=101, gross_value="291315", vat="10"),
            Row(invoice_id=33, order_id=3,company_id=101, gross_value="45100", vat="21"),
            Row(invoice_id=44, order_id=4,company_id=102, gross_value="245412", vat="19"),
            Row(invoice_id=55, order_id=5,company_id=102, gross_value="324222", vat="12"),
            Row(invoice_id=66, order_id=6,company_id=102, gross_value="145467", vat="0"),
        ]

        self.df_orders = self.spark.createDataFrame(self.test_data)
        self.df_orders.createOrReplaceTempView("orders_vw")  # Register as a view

    def test_company_crate_distribution(self):
        """Test crate type distribution calculation
        In case of duplicate companies stored under same ID but different names, the name that comes first in alphabatical order is selected. 
        """
        df_result = get_company_crate_distribution(self.spark)

        # Collect results for assertions
        result_data = df_result.select("company_id", "company_name", "crate_type", "crate_type_distribution").collect()

        # Expected output
        expected_data = [
            Row(company_id=101, company_name="ABC Corp", crate_type="Plastic", crate_type_distribution=2),
            Row(company_id=101, company_name="ABC Corp", crate_type="Wood", crate_type_distribution=1),
            Row(company_id=102, company_name="XYZ Ltd", crate_type="Plastic", crate_type_distribution=1),
            Row(company_id=102, company_name="XYZ Ltd", crate_type="Metal", crate_type_distribution=2),
        ]

        self.assertEqual(result_data, expected_data)

    def test_get_company_saleowner_list(self):
        """
        Test companies and sales owners
        In case of duplicate companies stored under same ID but different names, the name that comes first in alphabatical order is selected. 
        The list_salesowners field should contain a unique and comma-separated list of salespeople who have participated in at least one order of the company. 
        Please ensure that the list is sorted in ascending alphabetical order of the first name.
        """
        #self.df_orders.show()
        df_sale_owner = salesowners_normalized_view (self.spark)
        df_sale_owner.createOrReplaceTempView("salesowners_vw")
        #df_sale_owner.show()

        df_result = get_company_saleowner_list(self.spark)

        # Collect results for assertions
        result_data = df_result.select("company_id", "company_name", "list_salesowners").collect()

        # Expected output
        expected_data = [
            Row(company_id=101, company_name="ABC Corp", list_salesowners="Ammy Winehouse, Chris Pratt, Leonard Cohen, Luke Skywalker"),
            Row(company_id=102, company_name="XYZ Ltd", list_salesowners="David Henderson, Leon Leonov, Leonard Cohen, Luke Skywalker"),
        ]

        self.assertEqual(result_data, expected_data)

    def test_get_saleowner_commission(self): 
        """
        Test companies and sales owners
        In case of duplicate companies stored under same ID but different names, the name that comes first in alphabatical order is selected. 
        The list_salesowners field should contain a unique and comma-separated list of salespeople who have participated in at least one order of the company. 
        Please ensure that the list is sorted in ascending alphabetical order of the first name.
        """
        # self.df_orders.show()
        df_invoices = self.spark.createDataFrame(self.test_invoices)
        df_invoices.createOrReplaceTempView("invoices")  # Register as a view
        # df_invoices.show()

        df_sale_owner_comm = sales_owner_commission_view (self.spark)
        df_sale_owner_comm.createOrReplaceTempView("sales_owner_commission_vw")
        # df_sale_owner_comm.show()

        df_result = get_saleowner_commission(self.spark)
        # df_result.show()

        # Collect results for assertions
        result_data = df_result.select("sales_owner","total_commission").collect()

        # Expected output
        expected_data = [
            Row(sales_owner="Luke Skywalker", total_commission=418.65),
            Row(sales_owner="Leonard Cohen", total_commission=319.13),
            Row(sales_owner="David Henderson", total_commission=194.53),
            Row(sales_owner="Leon Leonov", total_commission=81.06),
            Row(sales_owner="Chris Pratt", total_commission=72.83),
            Row(sales_owner="Ammy Winehouse", total_commission=36.7)
        ]

        self.assertEqual(result_data, expected_data)

    @classmethod
    def tearDownClass(cls):
        """Stop Spark session after tests"""
        if cls.spark:
            cls.spark.stop()
            cls.spark = None

# Run the test
if __name__ == "__main__":
    unittest.main()