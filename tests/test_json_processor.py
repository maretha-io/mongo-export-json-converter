import os
import unittest
import json
from src.json_processor import process_large_json


class TestJsonProcessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up paths for test files."""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.input_path = os.path.join(cls.test_dir, "data", "test_input.json")
        cls.output_path = os.path.join(cls.test_dir, "output", "test_output.json")
        cls.expected_output_path = os.path.join(cls.test_dir, "data", "expected_output.json")

        # Ensure output directory exists
        os.makedirs(os.path.join(cls.test_dir, "output"), exist_ok=True)

    def test_process_large_json(self):
        """Test processing a MongoDB exported JSON file from a real input file."""

        # Run the function on the real file
        process_large_json(self.input_path, self.output_path)

        # Read the actual output
        with open(self.output_path, "r", encoding="utf-8") as output_file:
            processed_json = json.load(output_file)

        # Read the expected output
        with open(self.expected_output_path, "r", encoding="utf-8") as expected_file:
            expected_json = json.load(expected_file)

        # Compare actual vs expected
        self.assertEqual(processed_json, expected_json)


if __name__ == '__main__':
    unittest.main()
