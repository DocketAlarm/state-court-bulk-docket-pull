import sys
sys.path.insert(0,".")
from modules import get_json
import unittest
import os
from modules import global_variables


global_variables.JSON_INPUT_OUTPUT_PATH = global_variables.JSON_INPUT_OUTPUT_PATH

class TestGetJson(unittest.TestCase):

    def test_write_to_json_file(self):
        get_json.write_to_json_file("test", {'test':'yes'})
        bool_ = os.path.isfile(os.path.join(global_variables.JSON_INPUT_OUTPUT_PATH,'test.json'))
        self.assertTrue(bool_)
        os.remove(os.path.join(global_variables.JSON_INPUT_OUTPUT_PATH, 'test.json'))

    def test_authenticate(self):
        result = get_json.authenticate()
        self.assertTrue((len(result) > 10) and (isinstance(result, str)))

    def test_get_docket(self):
        result = get_json.get_docket("17-645","Supreme Court of the United States")
        self.assertTrue(result['success'])

    def test_format_case_number(self):
        result = get_json.format_case_number("16-2013-CF-006932-AXXX-MA")
        self.assertEqual(result, "2013-CF-006932")


if __name__ == '__main__':
    unittest.main()