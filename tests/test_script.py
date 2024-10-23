import unittest

from main import is_valid_company


class TestCompanyFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_is_valid_company_valid(self):
        company = {
            'ogrn': '1234567890123',
            'inn': '1234567890',
            'date': '2022-01-01'
        }
        self.assertTrue(is_valid_company(company), 'Данные добавленны в бд')

    def test_is_valid_company_invalid_ogrn(self):
        company = {
            'ogrn': '12345',
            'inn': '1234567890',
            'date': '2022-01-01'
        }
        self.assertFalse(is_valid_company(company))

    def test_is_valid_company_invalid_inn(self):
        company = {
            'ogrn': '1234567890123',
            'inn': '12345',
            'date': '2022-01-01'
        }
        self.assertFalse(is_valid_company(company))

    def test_is_valid_company_invalid_date(self):
        company = {
            'ogrn': '1234567890123',
            'inn': '1234567890',
            'date': 'invalid-date'
        }
        self.assertFalse(is_valid_company(company))


if __name__ == '__main__':
    unittest.main()
