import unittest

from Client import Client


class ClientTests(unittest.TestCase):

    def setUp(self):
        self.test_client = Client(
            1, "Ivo", 200000.00, "Bitcoin mining makes me rich", "jobanana75@yahoo.com")

    def test_client_id(self):
        self.assertEqual(self.test_client.get_id(), 1)

    def test_client_name(self):
        self.assertEqual(self.test_client.get_username(), "Ivo")

    def test_client_balance(self):
        self.assertEqual(self.test_client.get_balance(), 200000.00)

    def test_client_message(self):
        self.assertEqual(
            self.test_client.get_message(), "Bitcoin mining makes me rich")

    def test_cllient(self):
        self.assertEqual(self.test_client.get_mail(), "jobanana75@yahoo.com")


if __name__ == '__main__':
    unittest.main()
