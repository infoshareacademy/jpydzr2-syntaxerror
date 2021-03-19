import unittest
import covid_helper
import os

class CovidHelperTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.path = os.path.join(os.getcwd(), 'input')

    def test_reader__not_none(self):
        result = covid_helper.read_covid_data()

        self.assertIsNotNone(result)

    def test_reader__columns_no__positive(self):
        result = covid_helper.read_covid_data()

        self.assertEqual(len(result.columns), 16)

    def test_reader__columns_name__positive(self):
        df_result = covid_helper.read_covid_data()

        result = df_result.columns[1]
        expected = 'powiat_miasto'

        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()