"""This script searches texts for Buddhist terminology and archaic useage based on Zurcher (2013).

Zürcher, Erik. “A New Look at the Earliest Chinese Buddhist Texts.” In
*Buddhism in China: Collected Papers of Erik Zürcher*, edited by Jonathan A. Silk. Sinica Leidensia,
vol. 112. Brill, 2013, 419-445.
"""

import argparse
import cszjj
import os
import sys


cszjj_path = "data/chusanzangjiji.csv"
file_index_path = "data/canonical_summaries.csv"
analysis_filename = "data/language_zurcher.csv"


def check_patterns(nti, entry):
    """Check patterns and return results.

    Returns:
        dictionary: a dictionary with the analysis results.

    """
    if "title_zh" not in entry:
        print(f"title_zh not in entry {entry}")
        return {}
    title_zh = entry["title_zh"]
    if "filepath" not in entry:
        print(f"filepath not in {title_zh}")
        return {}
    fname = entry["filepath"]
    filepath = fname
    if fname.startswith("$nti"):
        filepath = nti + fname[4:]
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            content = cszjj.strip_boiler_plate(content)
            return {
                "title_zh": title_zh,
                "taisho_no": entry["taisho_no"],
                "huanfu": count_substring_occurrences(content, "還復"),
                "songqu": count_substring_occurrences(content, "送出"),
                "shequ": count_substring_occurrences(content, "捨去"),
                "daodizi": count_substring_occurrences(content, "道弟子"),
                "dushiwuwei": count_substring_occurrences(content, "度世無為"),
                "gougang": count_substring_occurrences(content, "溝港"),
                "nihuan": count_substring_occurrences(content, "泥洹"),
                "chujin": count_substring_occurrences(content, "除饉"),
                "niedu": count_substring_occurrences(content, "滅度"),
                "mingshi": count_substring_occurrences(content, "明士"),
                "kaishi": count_substring_occurrences(content, "開士"),
                "benwu": count_substring_occurrences(content, "本無"),
                "chue": count_substring_occurrences(content, "除惡"),
                "wenwuguo": count_substring_occurrences(content, "聞物國"),
                "error": "",
            }
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return {
            "title_zh": title_zh,
            "taisho_no": entry["taisho_no"],
            "error": "The file '{filepath}' was not found",
        }
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return {
            "title_zh": title_zh,
            "taisho_no": entry["taisho_no"],
            "error": "An error occurred while reading the file: {e}",
        }
    return {}


def count_substring_occurrences(main_string, sub_string):
    """
    Counts the non-overlapping occurrences of a substring within a main string.

        Returns:
        int: The number of times the substring appears in the main string.
    """
    if not sub_string:
        return 0

    count = 0
    start_index = 0
    while True:
        index = main_string.find(sub_string, start_index)
        if index == -1:
            break
        count += 1
        start_index = index + len(sub_string)
    return count


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
           entry["huanfu"],
           entry["songchu"],
           entry["shequ"],
           entry["daodizi"],
           entry["dushiwuwei"],
           entry["gougang"],
           entry["nihuan"],
           entry["chujin"],
           entry["miedu"],
           entry["mingshi"],
           entry["kaishi"],
           entry["benwu"],
           entry["chue"],
           entry["wenwuguo"],
           entry["error"],
           "",
    ]
    cszjj.append_to_csv(filename, [row])
    print(f"Result appended for {title_zh}")


if __name__ == "__main__":
    nti = os.environ.get("NTI", "")
    if len(nti) == 0:
        sys.exit("NTI not in environment.") 

    # Process command line arguments
    parser = argparse.ArgumentParser(
        description="Searches texts for Buddhist terminology and language useage based on Zurcher (2013)"
    )
    parser.add_argument(
        '-t', '--title',
        type=str,
        required=False,
        help='Process only a single text with the given CSZJJ title'
    )
    parser.add_argument(
        '-r', '--restart',
        type=str,
        required=False,
        help='Restart processing all records at the given CSZJJ title'
    )
    args = parser.parse_args()
    if args.title:
        print(f"Processing {args.title}")
        entry = cszjj.find_entry(file_index_path, args.title)
        result = check_patterns(nti, entry)
        append_result(analysis_filename, result)
        sys.exit()

    headers = ["CSZJJ",
               "Taisho No.",
               "huanfu",
               "songchu",
               "shequ",
               "daodizi",
               "dushiwuwei",
               "gougang",
               "nihuan",
               "chujin",
               "miedu",
               "mingshi",
               "kaishi",
               "benwu",
               "chue",
               "wenwuguo",
               "error",
               "notes",
               ]
    if not args.restart:
        print("Starting at the beginning\n")
        cszjj.write_headers_to_csv(analysis_filename, headers)
    else:
        print(f"Restarting at {args.restart}\n")
    entries = cszjj.parse_file_index(file_index_path, args.restart)
    num = len(entries)
    for entry in entries:
        result = check_patterns(nti, entry)
        append_result(analysis_filename, result)
        
    print(f"Results written to {analysis_filename}")
