# This will ensure that Python looks inside the src directory for your modules when running tests.
# This is used to dynamically modify Python’s import path at runtime so that the src directory is included.
# No need to manually set PYTHONPATH every time you run the tests.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
#print(sys.path)


import unittest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
from src.data_ingestion import load_invoices
import json

class TestInvoiceProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Spark session for testing."""
        cls.spark = SparkSession.builder.master("local[1]").appName("TestInvoiceProcessing").getOrCreate()

        cls.test_file = "test_invoices.json"
        # Sample JSON Data (simulating data/invoicing_data.json)
        data = {
                        "data": {
                            "invoices": [
                            {
                                "id": "e1e1e1e1",
                                "orderId": "479",
                                "companyId": "09d12dddfbbd",
                                "grossValue": "324222",
                                "vat": "0"
                            },
                            {
                                "id": "e2e2e2e2",
                                "orderId": "480",
                                "companyId": "4c9b58f04898",
                                "grossValue": "193498",
                                "vat": "19"
                            }
                            ]
                        }
                        }

        # Convert dictionary to a JSON string
        json_data = json.dumps(data)

        # Write the JSON string to the file
        with open(cls.test_file, "w") as f:
            f.write(json_data)

    @classmethod
    def tearDownClass(cls):
        """Stop Spark session after tests."""
        cls.spark.stop()
        os.remove(cls.test_file)
        if cls.spark:
            cls.spark.stop()
            cls.spark = None

    def test_load_invoices(self):
        """Test if JSON data is loaded correctly."""
        df_flattened = load_invoices(self.test_file, self.spark )
        # rows = df_flattened.collect()
        # print(rows)

        self.assertIsNotNone(df_flattened, "DataFrame should not be None")
        self.assertEqual(df_flattened.count(), 2, "Should have one top-level row")

    def test_flattened_schema(self):
        """Test if flattening logic produces the correct schema."""
        df_flattened = load_invoices(self.test_file, self.spark )

        expected_schema = ["invoice_id", "order_id", "company_id", "gross_value", "vat"]
        actual_schema = [field.name for field in df_flattened.schema.fields]

        self.assertEqual(actual_schema, expected_schema, "Schema does not match expected structure")

if __name__ == "__main__":
    unittest.main()
