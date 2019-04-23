from app import app
from flask import url_for
import unittest



class Flask_Tests(unittest.TestCase):


    def test_basic_test(self):
        # Test unit tests are properly functioning
        result = 2 + 2
        self.assertEqual(result, 4)


    def test_home(self):
        """Test home page"""
        test = app.test_client(self)
        result = test.get('/')
        self.assertEqual(result.status_code, 200)


    def test_log(self):
        """Test log page"""
        test = app.test_client(self)
        result = test.get('/log')
        self.assertEqual(result.status_code, 200)


    def test_lookup(self):
        """Test log page"""
        test = app.test_client(self)
        result = test.get('/lookup')
        self.assertEqual(result.status_code, 200)



if __name__ == "__main__":
    unittest.main()
