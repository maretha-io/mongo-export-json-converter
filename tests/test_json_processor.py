import os
import unittest
import json

from src.json_processor import process_ndjson


class TestJsonProcessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up paths for test files."""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.input_path = os.path.join(cls.test_dir, "data", "test_input.ndjson")
        cls.output_path = os.path.join(cls.test_dir, "output", "test_output.ndjson")
        cls.expected_output_path = os.path.join(cls.test_dir, "data", "expected_output.ndjson")

        # Ensure output directory exists
        os.makedirs(os.path.join(cls.test_dir, "output"), exist_ok=True)

    def test_process_ndjson(self):
        """Test processing a MongoDB-exported NDJSON file against expected NDJSON output."""

        # Run the function
        process_ndjson(self.input_path, self.output_path)

        # Load processed output (NDJSON)
        with open(self.output_path, "r", encoding="utf-8") as output_file:
            processed_json = [json.loads(line) for line in output_file if line.strip()]

        # Load expected output (NDJSON)
        with open(self.expected_output_path, "r", encoding="utf-8") as expected_file:
            expected_json = [json.loads(line) for line in expected_file if line.strip()]

        # Compare line-by-line documents
        self.assertEqual(processed_json, expected_json)


if __name__ == "__main__":
    unittest.main()
