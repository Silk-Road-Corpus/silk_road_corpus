"""This script searches texts for Buddhist terminology and language useage.
"""

import argparse
import csv
import cszjj
import os
import sys


cszjj_path = "data/chusanzangjiji.csv"
file_index_path = "data/canonical_summaries.csv"
analysis_filename = "data/language_analysis.csv"
prompt_template = """
How many times does the character {given_char} used as a final particle at the end of declarative sentences in the given text [text uploaded]?
Return only the integer number and no other output.
"""
ye2_prompt = """
How many times does the character '耶' appear at end of yes or no questions or as a final particle at the end of declarative sentences in
the given text [text uploaded]? Return only the integer number and no other output.
"""


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
            content = strip_boiler_plate(content)
            ye2_count = char_count(content, "耶")
            ye2_final_count = 0
            error = ""
            if ye2_count > 0:
                try:
                    r1 = cszjj.send_prompt(ye2_prompt, file_path=filepath)
                    ye2_final_count = int(r1)
                except:
                    error = f"Got a non-integer output from the model for 耶: {r1}\n"
            er3_count = char_count(content, "耳")
            er3_final_count = 0
            if er3_count > 0:
                try:
                    r2 = cszjj.send_prompt(prompt_template.format(given_char="耳"),
                                                                      file_path=filepath)
                    er3_final_count = int(r2)
                except:
                    error += f"Got a non-integer output from the model for 耳: {r2}\n"
            ye3_count = char_count(content, "也")
            ye3_final_count = 0
            if ye3_count > 0:
                try:
                    r3 = cszjj.send_prompt(prompt_template.format(given_char="也"),
                                                                      file_path=filepath)
                    ye3_final_count = int(r3)
                except:
                    error = f"Got a non-integer output from the model for 也: {r3}\n"
            return {
                "title_zh": title_zh,
                "taisho_no": entry["taisho_no"],
                "length": len(content),
                "rushiwowen": "如是我聞" in content,
                "wenrushi": "聞如是" in content,
                "wowenrushi": "我聞如是" in content,
                "rushiwen": "如是聞" in content,
                "not_in_shanzai": check_shanzai(content),
                "ye2_count": ye2_count,
                "er3_count": er3_count,
                "ye3_count": ye3_count,
                "ye2_final_count": ye2_final_count,
                "er3_final_count": er3_final_count,
                "ye3_final_count": ye3_final_count,
                "error": error,
            }
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return {}


def check_shanzai(content):
    """Checks how many times the final particle 哉 is used outside of 善哉善哉

    Return:
        int: The number of times that 哉 is used outside of 善哉善哉
    """
    count_shanzai = 0
    start_index = 0
    substring = "善哉善哉"
    while True:
        found_index = content.find(substring, start_index)
        if found_index == -1:
            break
        else:
            count_shanzai += 1
            start_index = found_index + len(substring)

    count_zai = char_count(content, "哉")
    return count_zai - 2 * count_shanzai


def char_count(content, char_to_find):
    """Find the number of occurence of character in a string content

    Return:
        int: The number of occurences
    """
    count = 0
    for char in content:
        if char == char_to_find:
            count += 1
    return count


def strip_boiler_plate(content):
    """Strings out boilerplate in text to get an accurate character count
    """
    lines = content.splitlines()
    stripped = ""
    for i, line in enumerate(lines):
        if (not line.startswith("【經文資訊】") and 
                not line.startswith("【版本記錄】") and
                not line.startswith("【編輯說明") and
                not line.startswith("【原始資料】") and
                not line.startswith("【其他事項】") and
                not line.startswith("本網站係採用") and
                not line.startswith("Copyright")):
            stripped += line
    return stripped
 

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
           entry["length"],
           entry["rushiwowen"],
           entry["wenrushi"],
           entry["wowenrushi"],
           entry["rushiwen"],
           entry["not_in_shanzai"],
           entry["ye2_count"],
           entry["er3_count"],
           entry["ye3_count"],
           entry["ye2_final_count"],
           entry["er3_final_count"],
           entry["ye3_final_count"],
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
        description="Searches texts for Buddhist terminology and language useage"
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
               "length",
               "rushiwowen",
               "wenrushi",
               "wowenrushi",
               "rushiwen",
               "not_in_shanzai",
               "ye2_count",
               "er3_count",
               "ye3_count",
               "ye2_final_count",
               "er3_final_count",
               "ye3_final_count",
               "error",
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
