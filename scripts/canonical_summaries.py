"""This script generates summaries of corpus texts.
"""

import argparse
import cszjj
import os
import sys


file_index_path = "data/canonical_summaries.csv"
output_filename = "data/canonical_summaries.csv"
prompt_template = """
You are a Buddhist scholar specializing in early Chinese Buddhist texts.

Write a summary of the given text in English in 3-4 sentences. Do not
insert any newlines or use markdown.
"""

def generate_summary(nti, entry):
    """Generate a summary of the given text.

    Returns:
        dictionary: a dictionary including the summary.
    """
    if "title_zh" not in entry:
        print(f"title_zh not in entry {entry}")
        return {}

    title_zh = entry["title_zh"]
    taisho_no = entry.get("taisho_no")

    result = {
        "title_zh": title_zh,
        "taisho_no": taisho_no,
        "error": None,
    }

    if "filepath" not in entry:
        result["error"] = "filepath not given"
    else:
        fname = entry["filepath"]
        filepath = fname
        if fname.startswith("$nti"):
            filepath = nti + fname[4:]
        try:
            summary = cszjj.send_prompt(prompt_template, file_path=filepath)
            result = {
                "title_zh": title_zh,
                "taisho_no": taisho_no,
                "summary": summary,
            }
        except FileNotFoundError:
            result["error"] = f"The file '{filepath}' was not found."
        except Exception as e:
            result["error"] = f"An error occurred: {e}"
    if "error" in result:
        print(f"Error for entry {title_zh}: {result['error']}")
    return result


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
    row = [0,                  # Placeholder for CSZJJ number
           title_zh,
           entry["taisho_no"],
           entry["summary"],
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
    parser.add_argument(
        '-f', '--fascicle',
        type=int,
        required=False,
        help='Process only a single fascicle of a text'
    )
    parser.add_argument(
        '-s', '--restart_at',
        type=str,
        required=False,
        help='Begin processing starting at the given title'
    )
    args = parser.parse_args()
    if args.title:
        print(f"Processing args, title: {args.title}, fascicle: {args.fascicle}, "
              f"start_title: {args.restart_at}")
        entries = cszjj.find_entry(file_index_path, args.title, args.fascicle, None)
        for entry in entries:
            result = generate_summary(nti, entry)
            append_result(output_filename, result)
        sys.exit()

    if not args.restart_at:
        headers = ["cszjj_id",
                   "cszjj_title",
                   "taisho_no",
                   "summary",
                   "error",
                   ]
        print(f"Starting at the beginning\n")
        cszjj.write_headers_to_csv(output_filename, headers)
    else:
        print(f"Starting at {args.restart_at}\n")
    entries = cszjj.parse_file_index(file_index_path, args.restart_at)
    num = len(entries)
    for entry in entries:
        result = generate_summary(nti, entry)
        append_result(output_filename, result)
        
    print(f"Results written to {output_filename}")
