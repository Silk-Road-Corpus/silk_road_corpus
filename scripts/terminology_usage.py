"""Transform the terminology collected from Taisho entries into a an index of term usage
"""

import csv
import cszjj

cszjj_path = "data/chusanzangjiji.csv"
terminology_filename = "data/terminology.csv"
terminology_dict = "data/terminology_usage.csv"

def parse_terminology_file(file_path):
    """
    Parses the terminology CSV file and returns its content as a list of dictionaries.

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
                    terms = [field.strip() for field in row[2].split(',')]
                    entry = {
                        "title_zh": row[0],
                        "taisho_no": row[1],
                        "terms": terms,
                    }
                    data.append(entry)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
        raise
    return data

def introduced_by(rows, catalog):
    """
    Finds which text and translator first introduced the terms.

    Args:
        rows (list): The rows of the language analysis file (in chronological order).
        catalog (dict): A dictionary of the CSZJJ catalog file.

    Returns:
        dict: A dictioinary of term usage
    """
    terms_introduced = {}
    for row in rows:
        title_zh = row["title_zh"]
        if title_zh not in catalog:
            print(f"Title {title_zh} is not in the catalog")
            continue
        cat_entry = catalog[title_zh]
        # id = cat_entry["id"]
        # print(f"Adding title {title_zh} CSZJJ No. {id}")
        if "attribution_analysis" not in cat_entry:
            print(f"Title {title_zh} does not have _attribution")
            attribution_analysis = "anonymous"
        attribution_analysis = cat_entry["attribution_analysis"]
        if not attribution_analysis:
            print(f"Title {title_zh} has empty attribution")
            attribution_analysis = "anonymous"
        terms = row["terms"]
        for term in terms:
            if term not in terms_introduced:
                terms_introduced[term] = {
                    "attribution_analysis": attribution_analysis,
                    "document_frequency": 1,
                }
            else:
                t = terms_introduced[term]
                document_frequency = t["document_frequency"]
                if t["attribution_analysis"] == "anonymous":
                    terms_introduced[term] = {
                        "attribution_analysis": attribution_analysis,
                        "document_frequency": document_frequency + 1,
                    }
                else:
                    terms_introduced[term] = {
                        "attribution_analysis": t["attribution_analysis"],
                        "document_frequency": document_frequency + 1,
                    }
    return terms_introduced

def write_terms_to_csv(filename, data, terms_introduced, catalog):
    """
    Writes data to a CSV file.

    Args:
        filename (str): The name of the CSV file to write to.
        data (dictionary of fields): The data to write. Each inner list represents a row.
        header (list, optional): A list of strings for the header row. Defaults to None.
    """
    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            header = ["czjj_no", "title_zh", "taisho_no", "attribution", "term", "term_introduced_by", "document_frequency"]
            csv_writer.writerow(header)
            for row in data:
                title_zh = row["title_zh"]
                taisho_no = row["taisho_no"]
                terms = row["terms"]
                if title_zh not in catalog:
                    print(f"write_terms_to_csv, title {title_zh} is not in the catalog")
                    continue
                cat_entry = catalog[title_zh]
                id = cat_entry["id"]
                attribution = cat_entry["attribution_analysis"]
                for term in terms:
                    # Skip terms containing punctuation
                    if "、" in term:
                        continue
                    term_introduced = ""
                    if term in terms_introduced:
                        t = terms_introduced[term]
                        term_introduced = t["attribution_analysis"]
                        document_frequency = t["document_frequency"]
                    r = [id, title_zh, taisho_no, attribution, term, term_introduced, document_frequency]
                    csv_writer.writerow(r)
    except IOError as e:
        print(f"Error writing header to file {filename}: {e}")


if __name__ == "__main__":
    print("Processing terminology")
    rows = parse_terminology_file(terminology_filename)
    catalog = cszjj.index_cszjj_file(cszjj_path)
    print(f"len(catalog): {len(catalog)}")
    terms_introduced = introduced_by(rows, catalog)
    print(f"len(usage): { len(terms_introduced)}")
    write_terms_to_csv(terminology_dict, rows, terms_introduced, catalog)