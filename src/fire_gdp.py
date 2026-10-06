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
    """Return the zero-based column index, or None if the name is absent."""
    try:
        return header.index(column_name)
    except ValueError:
        return None


def get_fire_gdp_year_data(co2_file, gdp_file, country):
    """Return [int year, float forest fires, float GDP] rows for one country.

    Match years using the GDP header and preserve the CO2 row order. Skip
    missing values or years, and return [] if either file lacks the country.
    """
    co2_rows, co2_header = get_data(
        co2_file, query_column=0, query_value=country, return_header=True,
    )
    gdp_rows, gdp_header = get_data(
        gdp_file, query_column=0, query_value=country, return_header=True,
    )
    if not co2_rows or not gdp_rows:
        return []

    fire_column = get_column_index(co2_header, 'Forest fires')
    gdp_row = gdp_rows[0]
    result = []
    for co2_row in co2_rows:
        year = co2_row[1]
        gdp_column = get_column_index(gdp_header, year)
        if gdp_column is None:
            continue

        forest_fires = co2_row[fire_column]
        gdp = gdp_row[gdp_column]
        if forest_fires == '' or gdp == '':
            continue

        result.append([int(year), float(forest_fires), float(gdp)])

    return result
