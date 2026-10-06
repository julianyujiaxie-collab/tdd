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
        header = ['Area', 'Year', 'Forest fires']
        for name, expected in [('Area', 0), ('Year', 1), ('Forest fires', 2)]:
            with self.subTest(name=name):
                self.assertEqual(
                    fire_gdp.get_column_index(header, name), expected,
                )

    def test_name_absent(self):
        self.assertIsNone(
            fire_gdp.get_column_index(['Area', 'Year', 'Forest fires'], 'GDP'),
        )

    def test_empty_header(self):
        self.assertIsNone(fire_gdp.get_column_index([], 'Area'))


class TestGetFireGDPYearData(unittest.TestCase):

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.co2_file = os.path.join(temp_dir.name, 'co2.csv')
        self.gdp_file = os.path.join(temp_dir.name, 'gdp.csv')
        self.write_csv(
            self.co2_file,
            'Area,Year,Savanna fires,Forest fires\n'
            'Canada,2005,80,99\n'
            'Brazil,2005,90,1.5\n'
            'Brazil,2006,91,2.5\n'
            'Chile,2005,40,4.0\n',
        )
        self.write_csv(
            self.gdp_file,
            'Country,2006,2005\n'
            'Canada,888,999\n'
            'Brazil,2300000,2170584.50\n'
            'Peru,500,400\n',
        )

    def write_csv(self, file_name, content):
        with open(file_name, 'w', newline='', encoding='utf-8') as output:
            output.write(content)

    def test_matches_country_and_year_with_numeric_values(self):
        result = fire_gdp.get_fire_gdp_year_data(
            self.co2_file, self.gdp_file, 'Brazil',
        )
        self.assertEqual(result, [
            [2005, 1.5, 2170584.50],
            [2006, 2.5, 2300000.0],
        ])
        for year, forest_fires, gdp in result:
            self.assertIsInstance(year, int)
            self.assertIsInstance(forest_fires, float)
            self.assertIsInstance(gdp, float)

    def test_skips_missing_fire_values(self):
        self.write_csv(
            self.co2_file,
            'Area,Year,Savanna fires,Forest fires\n'
            'Brazil,2005,90,1.5\n'
            'Brazil,2006,91,\n',
        )
        self.assertEqual(
            fire_gdp.get_fire_gdp_year_data(
                self.co2_file, self.gdp_file, 'Brazil',
            ),
            [[2005, 1.5, 2170584.50]],
        )

    def test_skips_missing_gdp_values(self):
        self.write_csv(
            self.gdp_file,
            'Country,2006,2005\n'
            'Brazil,,2170584.50\n',
        )
        self.assertEqual(
            fire_gdp.get_fire_gdp_year_data(
                self.co2_file, self.gdp_file, 'Brazil',
            ),
            [[2005, 1.5, 2170584.50]],
        )

    def test_skips_years_absent_from_gdp_header(self):
        self.write_csv(
            self.gdp_file,
            'Country,2005\n'
            'Brazil,2170584.50\n',
        )
        self.assertEqual(
            fire_gdp.get_fire_gdp_year_data(
                self.co2_file, self.gdp_file, 'Brazil',
            ),
            [[2005, 1.5, 2170584.50]],
        )

    def test_keeps_zero_values(self):
        self.write_csv(
            self.co2_file,
            'Area,Year,Forest fires\n'
            'Brazil,2005,0\n'
            'Brazil,2006,2.5\n',
        )
        self.write_csv(
            self.gdp_file,
            'Country,2006,2005\n'
            'Brazil,0,2170584.50\n',
        )
        self.assertEqual(
            fire_gdp.get_fire_gdp_year_data(
                self.co2_file, self.gdp_file, 'Brazil',
            ),
            [[2005, 0.0, 2170584.50], [2006, 2.5, 0.0]],
        )

    def test_returns_empty_list_when_country_is_missing(self):
        for country in ['Chile', 'Peru', 'Unknown']:
            with self.subTest(country=country):
                self.assertEqual(
                    fire_gdp.get_fire_gdp_year_data(
                        self.co2_file, self.gdp_file, country,
                    ),
                    [],
                )


if __name__ == '__main__':
    unittest.main()
