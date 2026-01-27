"""This script analyzes patterns for translating Indic grammatical constructs.
"""

import argparse
import cszjj
import os
import sys

cszjj_path = "data/chusanzangjiji.csv"
file_index_path = "data/canonical_summaries.csv"
output_filename = "data/style_indic.csv"

DEFAULT_STYLE = {
    "subject_wu": 0,
    "subject_wo": 0,
    "subject_ru": 0,
    "plural_zhu": 0,
    "past_tense_yi": 0,
    "past_tense_xi": 0,
    "present_tense_jin": 0,
    "future_tense_dang": 0,
    "future_tense_danglai": 0,
    "char_count": 0,
    "is_indiginous": 0
}

def analyze_style(nti, entry, catalog):
    """Analyze style of the given text.

    Returns:
        dictionary: a dictionary following the rubric in the prompt.
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
    # Initialize with default style values for the success case.
    result.update(DEFAULT_STYLE)

    if "filepath" not in entry:
        result["error"] = "filepath not given"
    else:
        fname = entry["filepath"]
        filepath = fname
        if fname.startswith("$nti"):
            filepath = nti + fname[4:]

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                content = cszjj.strip_boiler_plate(content)
                result["subject_wu"] = cszjj.phrase_count(content, "吾")
                result["subject_wo"] = cszjj.phrase_count(content, "我")
                result["subject_ru"] = cszjj.phrase_count(content, "汝")
                result["plural_zhu"] = cszjj.phrase_count(content, "諸")
                result["past_tense_yi"] = cszjj.phrase_count(content, "已")
                result["past_tense_xi"] = cszjj.phrase_count(content, "昔")
                result["present_tense_jin"] = cszjj.phrase_count(content, "今")
                result["future_tense_danglai"] = cszjj.phrase_count(content, "當來")
                result["future_tense_dang"] = cszjj.phrase_count(content, "當") - result["future_tense_danglai"]
                result["char_count"] = len(content)
                result["is_indiginous"] = is_indiginous(nti, entry, catalog)
        except FileNotFoundError:
            result["error"] = f"The file '{filepath}' was not found."
        except Exception as e:
            result["error"] = f"An error occurred: {e}"

    if result["error"]:
        print(f"Error for entry {title_zh}: {result['error']}")
    return result


def is_indiginous(nti, entry, catalog):
    """Retrieve whether the text is indiginous from the catalog.

    Returns:
        int64: 0 if not indiginous, 1 if indiginous.
    """
    if "title_zh" not in entry:
        print(f"title_zh not in entry {entry}")
        return {}

    title_zh = entry["title_zh"]
    cat_entry = catalog[title_zh]
    # print(cat_entry)
    classification = cat_entry["secondary_lit_classification"]
    if classification and "Chinese indigenous" in classification:
        return 1
    return 0


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
           entry["subject_wu"],
           entry["subject_wo"],
           entry["subject_ru"],
           entry["plural_zhu"],
           entry["past_tense_yi"],
           entry["past_tense_xi"],
           entry["present_tense_jin"],
           entry["future_tense_dang"],
           entry["future_tense_danglai"],
           entry["char_count"],
           entry["is_indiginous"],
           entry["error"],
    ]
    cszjj.append_to_csv(filename, [row])
    # print(f"Result appended for {title_zh}")


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
            result = analyze_style(nti, entry)
            append_result(output_filename, result)
        sys.exit()

    if not args.restart_at:
        headers = ["CSZJJ",
                   "taisho_no",
                   "subject_wu",
                   "subject_wo",
                   "subject_ru",
                   "past_tense_yi",
                   "past_tense_xi",
                   "present_tense_jin",
                   "future_tense_dang",
                   "future_tense_danglai",
                   "char_count",
                   "is_indiginous",
                   "error",
                   ]
        print(f"Starting at the beginning\n")
        cszjj.write_headers_to_csv(output_filename, headers)
    else:
        print(f"Starting at {args.restart_at}\n")
    entries = cszjj.parse_file_index(file_index_path, args.restart_at)
    catalog = cszjj.index_cszjj_file(cszjj_path)
    for entry in entries:
        result = analyze_style(nti, entry, catalog)
        append_result(output_filename, result)
    print(f"Results written to {output_filename}")
