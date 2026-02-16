"""This script analyzes Taisho texts for vernacular elements of style and saves the
results.
"""

import argparse
import cszjj
import os
import sys


file_index_path = "data/canonical_summaries.csv"
output_filename = "data/style_vernacular.csv"
prompt_template = """
You are a Buddhist scholar specializing in early Chinese Buddhist texts.

Evaluate the translation style of the following text for vernacular
elements:

1. Does the text use the prefix 阿 ā, not as part of a transliteration?
   Return a Boolean value.
2. Does the text use the prefix 老 lǎo? Return a Boolean value.
3. Does the text use the suffix 兒 ér? Return a Boolean value.
4. Does the text use reduplicated nouns? Return a Boolean value.
5. Does the text use the second-person pronoun ‘he / she’ 渠 qú?
   Return a Boolean value.
6. Does the text use the personal pronoun 他 tā?
   Return a Boolean value.
7. Does the text use the personal pronoun 伊 yī?
   Return a Boolean value.

Return the result in the following JSON format.
Put the explanation in the notes field. Do not use newlines in the notes.
{"prefix_a": Boolean,
"prefix_lao": Boolean,
"suffix_er": Boolean,
"reduplicated_nouns": Boolean,
"pronoun_qu": Boolean,
"personal_pronoun_ta": Boolean,
"personal_pronoun_yi": Boolean,
"notes": string}.
"""


schema = {
    "type": "object",
        "properties": {
            "prefix_a": {
                "type": "boolean",
            },
            "prefix_lao": {
                "type": "boolean",
            },
            "suffix_er": {
                "type": "boolean",
            },
            "reduplicated_nouns": {
                "type": "boolean",
            },
            "pronoun_qu": {
                "type": "boolean",
            },
            "personal_pronoun_ta": {
                "type": "boolean",
            },
            "personal_pronoun_yi": {
                "type": "boolean",
            },
            "notes": {
                "type": "string",
            },
        }
}

DEFAULT_STYLE = {
    "prefix_a": False,
    "prefix_lao": False,
    "suffix_er": False,
    "reduplicated_nouns": False,
    "pronoun_qu": False,
    "personal_pronoun_ta": False,
    "personal_pronoun_yi": False,
    "notes": "",
}


def analyze_style(nti, entry):
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
            response = cszjj.send_prompt_file_and_schema(prompt_template,
                                                         file_path=filepath,
                                                         response_schema=schema)
            # Populate result with data from style_data, using defaults from DEFAULT_STYLE
            for key, default_value in DEFAULT_STYLE.items():
                result[key] = response.get(key, default_value)

        except FileNotFoundError:
            result["error"] = f"The file '{filepath}' was not found."
        except Exception as e:
            result["error"] = f"An error occurred: {e}"

    if result["error"]:
        print(f"Error for entry {title_zh}: {result['error']}")
        # For errors, null out the style fields.
        for key in DEFAULT_STYLE:
            result[key] = None

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
    row = [title_zh,
           entry["taisho_no"],
           entry["prefix_a"],
           entry["prefix_lao"],
           entry["suffix_er"],
           entry["reduplicated_nouns"],
           entry["pronoun_qu"],
           entry["personal_pronoun_ta"],
           entry["personal_pronoun_yi"],
           entry["notes"],
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
                   "Taisho No.",
                   "prefix_a",
                   "prefix_lao",
                   "suffix_er",
                   "reduplicated_nouns",
                   "pronoun_qu",
                   "personal_pronoun_ta",
                   "personal_pronoun_yi",
                   "notes",
                   "error",
                   ]
        print(f"Starting at the beginning\n")
        cszjj.write_headers_to_csv(output_filename, headers)
    else:
        print(f"Starting at {args.restart_at}\n")
    entries = cszjj.parse_file_index(file_index_path, args.restart_at)
    num = len(entries)
    for entry in entries:
        result = analyze_style(nti, entry)
        append_result(output_filename, result)
        
    print(f"Results written to {output_filename}")
