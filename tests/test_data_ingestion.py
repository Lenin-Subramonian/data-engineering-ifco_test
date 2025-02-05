# This will ensure that Python looks inside the src directory for your modules when running tests.
# This is used to dynamically modify Python’s import path at runtime so that the src directory is included.
# No need to manually set PYTHONPATH every time you run the tests.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
#print(sys.path)


import unittest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from src.data_ingestion import load_csv

class TestDataIngestion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize Spark session before tests."""
        cls.spark = SparkSession.builder.master("local[1]").appName("TestOrderProcessing").getOrCreate()

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
    def tearDownClass(cls):
        """Stop Spark session and remove test file."""
        cls.spark.stop()
        os.remove(cls.test_file)
        if cls.spark:
            cls.spark.stop()
            cls.spark = None

    def test_load_csv(self):
        """Test loading CSV with a real test file."""
        df = load_csv(self.test_file, self.spark )
        self.assertIsNotNone(df)
        self.assertEqual(df.count(), 5)  # Should have 5 row

    def test_schema_validation(self):
        """Test if the DataFrame has the expected schema after processing."""
        processed_df = load_csv(self.test_file, self.spark )
        expected_schema = ["order_id", "date", "company_id", "company_name", "crate_type",
                           "contact_name", "contact_surname", "contact_city", "contact_cp", "salesowners"]
        self.assertEqual(processed_df.columns, expected_schema)

    def test_row_count(self):
        """Ensure the correct number of rows are returned after processing."""
        processed_df = load_csv(self.test_file, self.spark )  
        self.assertEqual(processed_df.count(), 5)  # Should match input rows

    def test_data_cleaning(self):
        """Ensure data transformations are applied correctly."""
        processed_df = load_csv(self.test_file, self.spark )

         # Print all order_ids for debugging
        # order_ids = processed_df.select("order_id").collect()
        # print([row['order_id'] for row in order_ids])  # Printing the list of order_ids

        # rows = processed_df.collect()
        # print(rows)

        row = processed_df.filter(processed_df.order_id == "481").collect()[0]

        # Check if names are correctly extracted
        self.assertEqual(row.contact_name[0], "Para")
        self.assertEqual(row.contact_surname[0], "Cetamol")
        self.assertEqual(row.contact_city[0], "Frankfurt am Oder")
        self.assertEqual(row.contact_cp[0], "3934")

    def test_empty_contact_data(self):
        """Ensure empty or missing contact_data is handled properly."""
        processed_df = load_csv(self.test_file, self.spark )

        # Row where contact_data was an empty JSON array
        row_empty_json = processed_df.filter(processed_df.order_id == "482").collect()[0]
        self.assertIsNone(row_empty_json.contact_name)  # Should be None

        # Row where contact_data was missing
        row_missing_json = processed_df.filter(processed_df.order_id == "483").collect()[0]
        self.assertIsNone(row_missing_json.contact_name)  # Should be None

if __name__ == "__main__":
    unittest.main()
