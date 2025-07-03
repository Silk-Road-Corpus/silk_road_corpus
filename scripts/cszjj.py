"""This module provides utilities for working with Chu San Zan Ji Ji data.
"""

import csv


def parse_cszjj_file(file_path):
    """
    Parses the CSZJJ CSV file and returns its content as a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row.
    """
    data = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvfile) # Skip header row
            i = 0
            for row in csvreader:
                if len(row) > 2:
                    entry = {
                        "id": row[0],
                        "title_zh": row[1],
                        "fascicle": int(row[2]),
                        "taisho_title_zh": row[19],
                    }
                    data.append(entry)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
    return data
