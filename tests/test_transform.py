# This will ensure that Python looks inside the src directory for your modules when running tests.
# This is used to dynamically modify Python’s import path at runtime so that the src directory is included.
# No need to manually set PYTHONPATH every time you run the tests.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


import unittest
import gc
import atexit
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from src.data_ingestion import load_csv, load_invoices
from src.transform import transform_orders

class TestTransformOrders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize Spark session for tests"""
        cls.spark = SparkSession.builder.master("local[1]").appName("TestOrderTransform").getOrCreate()
        atexit.register(cls.cleanup_spark)  # Ensure Spark stops on exit

        cls.test_file = "test_orders.csv"
        # Create a small sample CSV file
        data = """order_id;date;company_id;company_name;crate_type;contact_data;salesowners
                479;29.01.22;09d12dddfbbd;Fresh Fruits Co;Plastic;"[{""contact_name"":""Curtis"", ""contact_surname"":""Jackson"", ""city"":""Chicago"", ""cp"": ""12345""}]";Leonard Cohen, Luke Skywalker, Ammy Winehouse
                480;21.02.22;4c9b58f04898;Veggies Inc;Wood;"[{""contact_name"":""Maria"", ""contact_surname"":""Theresa"", ""city"":""Calcutta""}]";Luke Skywalker, David Goliat, Leon Leonov
                481;03.04.22;09d12dddfbbd;Fresh Fruits c.o;Metal;"[{""contact_name"":""Para"", ""contact_surname"":""Cetamol"", ""city"":""Frankfurt am Oder"", ""cp"": ""3934""}]";Luke Skywalker
                482;14.07.21;1a6fd3aeb7d6;Seafood Supplier;Plastic;;David Goliat, Leonard Cohen
                483;23.10.22;3c94146e6f16;Meat Packers Ltd;Plastic;;Chris Pratt, David Henderson, Marianov Merschik, Leon Leonov
               """

        with open(cls.test_file, "w") as f:
            f.write(data)

    @classmethod
    def cleanup_spark(cls):
        """Properly stop Spark session"""
        if cls.spark:
            cls.spark.stop()
            cls.spark = None
        gc.collect()  # Force garbage collection
    
    @classmethod
    def tearDownClass(cls):
        """Stop Spark session and remove test file."""
        cls.spark.stop()
        os.remove(cls.test_file)
        """Stop Spark session after tests"""
        cls.cleanup_spark()

    def setUp(self):
        """Prepare test data before each test case""" 
        self.df_orders = load_csv(self.test_file, self.spark, register_sql_view=True)
        self.df_orders.createOrReplaceTempView("orders")  # Register the view    
    
    def test_row_count(self):
        """Ensure the correct number of rows are returned after processing."""
        df_result = transform_orders(self.spark)
        self.assertEqual(df_result.count(), 5)  # Should match input rows
    
    def test_transform_orders(self):
        """Test the transform_orders function"""
        
        df_result = transform_orders(self.spark)

        # Collect results for assertion
        row_data = df_result.filter(col("order_id") == "481").select(
        "order_id", "contact_name", "contact_surname", "contact_full_name", "contact_city", "contact_cp"
            ).collect()[0]

        # Check if names are correctly extracted
        self.assertEqual(row_data.contact_name, "Para")
        self.assertEqual(row_data.contact_surname, "Cetamol")
        self.assertEqual(row_data.contact_full_name, "Para Cetamol")
        self.assertEqual(row_data.contact_city, "Frankfurt am Oder")
        self.assertEqual(row_data.contact_cp, "3934")

    def test_missing_fullname(self):
        """
        Ensures that missing names default to "John Doe" if not present.
        Ensures missing city values default to "Unknown" if not present.
        Ensures missing postal codes default to "UNK00" if not present.
        """
        
        df_result = transform_orders(self.spark)

        # Collect results for assertion
        row_data = df_result.filter(col("order_id") == "482").select(
        "order_id", "contact_name", "contact_surname", "contact_full_name", "contact_city", "contact_cp"
            ).collect()[0]

        # Check if names are correctly extracted
        self.assertEqual(row_data.contact_full_name, "John Doe")
        self.assertEqual(row_data.contact_city, "Unknown")
        self.assertEqual(row_data.contact_cp, "UNK00")
    
    def test_contact_address(self):
        """
        Ensures missing city values default to "Unknown" if not present. 
        Ensures missing postal codes default to "UNK00" if not present. 
        """  
        df_result = transform_orders(self.spark)

        # Collect results for assertion
        row_data = df_result.filter(col("order_id") == "480").select(
        "order_id", "contact_name", "contact_surname", "contact_full_name", "contact_city", "contact_cp"
            ).collect()[0]

        # Check if names are correctly extracted
        self.assertEqual(row_data.contact_full_name, "Maria Theresa")
        self.assertEqual(row_data.contact_city, "Calcutta")
        self.assertEqual(row_data.contact_cp, "UNK00")

    @classmethod
    def tearDownClass(cls):
        """Stop Spark session after tests"""
        cls.spark.stop()

# Run the test
if __name__ == "__main__":
    unittest.main()

