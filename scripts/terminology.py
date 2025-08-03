"""This script extracts Buddhist terminology from Taisho texts and saves the result.
"""

import argparse
import cszjj
import os
import sys


file_index_path = "data/canonical_summaries.csv"
terminology_filename = "data/terminology.csv"
prompt_terminology = """
Which of the terms in the attached text are Buddhist terminology?
Return a comma separated list only. Do not add your own comments.
"""

def extract_terminology(nti, entry):
    """Extract terminology from a text.

    Returns:
        dictionary: a dictionary with a list of terminology
    """
    if "title_zh" not in entry:
        print(f"title_zh not in entry {entry}")
        return {}
    title_zh = entry["title_zh"]
    if "filepath" not in entry:
        print(f"filepath not in {title_zh}")
        return {
            "title_zh": title_zh,
            "taisho_no": entry["taisho_no"],
            "terminology": [],
            "error": "filepath not given",
            "notes": "",
        }
    fname = entry["filepath"]
    filepath = fname
    if fname.startswith("$nti"):
        filepath = nti + fname[4:]
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            error = ""
            content = file.read()
            try:
                result = cszjj.send_prompt(prompt_terminology, file_path=filepath)
            except Exception as e:
                error += f"Got a error from the model: {e}"
            return {
                "title_zh": title_zh,
                "taisho_no": entry["taisho_no"],
                "terminology": result,
                "error": error,
                "notes": "",
            }
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return {
            "title_zh": title_zh,
            "taisho_no": entry["taisho_no"],
            "terminology": [],
            "error": f"The file '{filepath}' was not found.",
            "notes": "",
        }
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return {
            "title_zh": title_zh,
            "taisho_no": entry["taisho_no"],
            "terminology": [],
            "error": f"An error occurred while reading the file: {e}",
            "notes": "",
        }
    return {}


def append_result(filename, entry):
    """
    Writes data to a CSV file.

    Args:
        filename (str): The name of the CSV file to write to.
        data (list of dictionaries): The data to write.
    """
    if "title_zh" not in entry:
        return
    title_zh = entry["title_zh"]
    row = [title_zh,
           entry["taisho_no"],
           entry["terminology"],
           entry["error"],
    ]
    cszjj.append_to_csv(filename, [row])
    print(f"Result appended for {title_zh}")


if __name__ == "__main__":
    nti = os.environ.get("NTI", "")
    if len(nti) == 0:
        sys.exit("NTI not in environment.") 

    # Process command line arguments
    parser = argparse.ArgumentParser(
        description="Extracts Buddhist terminology from Taisho texts"
    )
    parser.add_argument(
        '-t', '--title',
        type=str,
        required=False,
        help='Process only a single text with the given CSZJJ title'
    )
    args = parser.parse_args()
    if args.title:
        print(f"Processing {args.title}")
        entry = cszjj.find_entry(file_index_path, args.title)
        result = extract_terminology(nti, entry)
        append_result(terminology_filename, result)
        sys.exit()

    headers = ["CSZJJ",
               "Taisho No.",
               "terminology",
               "error",
               "notes",
               ]
    print("Starting at the beginning\n")
    cszjj.write_headers_to_csv(terminology_filename, headers)
    entries = cszjj.parse_file_index(file_index_path, args.restart)
    num = len(entries)
    for entry in entries:
        result = extract_terminology(nti, entry)
        append_result(terminology_filename, result)
        
    print(f"Results written to {terminology_filename}")
