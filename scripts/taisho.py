"""This script reads Taisho numbers and titles from the NTI Reader collections.csv file.
"""

import csv
import re
import io

def extract_number_from_mixed_string(data_string):
    """
    Extracts the first sequence of digits from a string that may contain
    a mix of letters and numbers.

    Args:
        data_string (str): The string to parse (e.g., "taisho/t0001.csv").

    Returns:
        int or None: The extracted number as an integer, or None if no number is found.
    """
    # Use a regular expression to find one or more digits
    match = re.search(r'\d+', data_string)
    if match:
        return int(match.group(0))
    return None


def extract_chinese(text):
    """
    Extracts Chinese characters from a given string.

    Args:
        text (str): The input string which may contain mixed English and Chinese characters.

    Returns:
        str: A string containing only the Chinese characters found in the input text.
    """
    chinese_characters = re.findall(r'[\u4e00-\u9fff]+', text)
    return ''.join(chinese_characters)


def process_csv_rows(filename):
    """
    Reads CSV data from a file, keeping only the numerical part of the first column
    and the Chinese part of the third column.

    Args:
        filename (str): A file containing the CSV data.

    Returns:
        list: A list of lists, where each inner list represents a processed row.
    """
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        processed_rows = []

        for i, row in enumerate(reader):
            processed_row = []
            if len(row) > 2:
                num = row[0]
                title = extract_chinese(row[2])
                extracted_num = extract_number_from_mixed_string(num)
                processed_row.append(extracted_num)
                processed_row.append(title)
                processed_rows.append(processed_row)
        return processed_rows


def write_to_csv(filename, data, header=None):
    """
    Writes data to a CSV file.

    Args:
        filename (str): The name of the CSV file to write to.
        data (list of lists): The data to write. Each inner list represents a row.
        header (list, optional): A list of strings for the header row. Defaults to None.
    """
    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write the header if provided
            if header:
                csv_writer.writerow(header)

            # Write the data rows
            csv_writer.writerows(data)
        print(f"Data successfully written to {filename}")
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")


if __name__ == "__main__":
    filename = "tmp/collections.csv"
    processed_results = process_csv_rows(filename)
    write_to_csv("data/taisho.csv", processed_results, header=["taisho_no", "title"])
