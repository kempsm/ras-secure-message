import unittest
from app.exception.exceptions import MessageSaveException


class ExceptionsTestCase(unittest.TestCase):


    def test_message(self):
        ex = MessageSaveException("Test", 200)
        rv = ex.to_dict()
        self.assertTrue(rv['message'] == "Test")

    def test_status_code(self):
        ex = MessageSaveException("", 200)
        self.assertTrue(ex.status_code == 200)