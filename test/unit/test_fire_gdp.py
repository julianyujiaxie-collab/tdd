import os
import tempfile
import unittest
import fire_gdp


class TestGetData(unittest.TestCase):

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.file_name = os.path.join(temp_dir.name, 'emissions.csv')
        with open(self.file_name, 'w', newline='', encoding='utf-8') as output:
            output.write(
                'Area,Year,Forest fires\n'
                'Canada,1990,1.5\n'
                'Brazil,1990,2.5\n'
                'Canada,1991,\n'
                '"Congo, Republic of",1991,3.0\n'
            )
        self.header = ['Area', 'Year', 'Forest fires']
        self.rows = [
            ['Canada', '1990', '1.5'],
            ['Brazil', '1990', '2.5'],
            ['Canada', '1991', ''],
            ['Congo, Republic of', '1991', '3.0'],
        ]

    def test_returns_all_rows_without_header(self):
        self.assertEqual(fire_gdp.get_data(self.file_name), self.rows)

    def test_filters_by_column_and_value(self):
        cases = [
            (0, 'Canada', [self.rows[0], self.rows[2]]),
            (1, '1990', [self.rows[0], self.rows[1]]),
            (2, '', [self.rows[2]]),
        ]
        for column, value, expected in cases:
            with self.subTest(column=column, value=value):
                self.assertEqual(
                    fire_gdp.get_data(self.file_name, column, value),
                    expected,
                )

    def test_returns_empty_list_when_no_exact_match(self):
        for value in ['Unknown', 'Can', 'canada']:
            with self.subTest(value=value):
                self.assertEqual(
                    fire_gdp.get_data(self.file_name, 0, value), [],
                )

    def test_returns_header_with_rows(self):
        cases = [
            (None, None, self.rows),
            (0, 'Canada', [self.rows[0], self.rows[2]]),
            (0, 'Unknown', []),
        ]
        for column, value, expected in cases:
            with self.subTest(column=column, value=value):
                self.assertEqual(
                    fire_gdp.get_data(
                        self.file_name, column, value, return_header=True,
                    ),
                    (expected, self.header),
                )

    def test_does_not_filter_when_query_is_incomplete(self):
        for query in [{'query_column': 0}, {'query_value': 'Canada'}]:
            with self.subTest(query=query):
                self.assertEqual(
                    fire_gdp.get_data(self.file_name, **query), self.rows,
                )


class TestGetColumnIndex(unittest.TestCase):

    def test_name_present(self):
        pass

if __name__ == '__main__':
    unittest.main()
