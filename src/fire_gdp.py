import csv


def get_data(file_name,
             query_column=None,
             query_value=None,
             return_header=False):
    """Read CSV rows, optionally filtering by a zero-based column index.

    Filter only when both query arguments are provided, using exact string
    equality. Cells remain strings, including empty strings for missing values.
    Return rows without the header, or (rows, header) if return_header is True.
    """
    with open(file_name, newline='', encoding='utf-8') as data_file:
        reader = csv.reader(data_file)
        header = next(reader)
        rows = []
        for row in reader:
            if query_column is not None and query_value is not None:
                if row[query_column] != query_value:
                    continue
            rows.append(row)

    if return_header:
        return rows, header
    return rows


def get_column_index(header, column_name):
    pass


def get_fire_gdp_year_data(co2_file, gdp_file, country):
    pass
