"""This script extracts writing style from Taisho texts and saves the result.
"""

import argparse
import cszjj
import os
import sys


file_index_path = "data/canonical_summaries.csv"
output_filename = "data/style.csv"
prompt_template = """
You are a Buddhist scholar specializing in early Chinese Buddhist texts.

Evaluate the translation style of the following text, given that it was
translated to Chinese from an Indic language, probably Sanskrit. Separate 
the style of source text from translation style. Use the following rubric:

1. Is the text written in verse, prose, or a mixture? Options: 'verse',
    'prose', or 'mixed'.
2. If verse or mixed, how many syllables per line or sentence? Return:
   an integer number.
3. Is the text written in vernacular form or literary Chinese? Options:
    'vernacular', 'literary'.
4. Is the translation literal or fluent? Options: 'literal', 'fluent'.
5. Does the translation use ornate language or plain language? Options:
    'ornate', 'plain'.
6. Does the translation use terse versus verbose wording? Options: 'terse',
    'verbose'.
7. Are idioms used? Return a Boolean value.
8. Is the tone factual or spiritual? For example, is a factual term
    like 'concentration' 定 or a spiritual term like samādhi 三昧 used for
    meditation? Options: 'factual', 'spiritual'.
9. Were Buddhist teachings interpreted according to indigenous Chinese
    philosophical concepts? Return: a Boolean value.
10. Does the text include interpolations? Return: a Boolean value.
11. Is there any interlinear commentary? Return: a Boolean value.
12. Are there signs of oral transmission? Return: a Boolean value.
13. Are abbreviations used? Return: a Boolean value.
14. Does the text use implicit or explicit sentence subjects? Options:
    'implicit', 'explicit'.
15. Is the adverb 諸 zhū used to indicate plural form? For example, in
    'Buddhas' 諸佛? Return: a Boolean value.
16. How is tense indicated? Is it left unspecified or explicitly indicated?
    Options: 'unspecified', 'explicit'.

Return the result in the following JSON format. For the string types use only
the enumerations given, for example, 'verse' or 'prose', not an explanation.
Put the explanation in the notes field.
{"verse_or_prose": string,
"syllables_per_line": integer,
"vernacular_or_literary": string,
"literal_or_fluent": string,
"ornate_or_plain_language": string,
"terse_or_verbose": string,
"idioms_used": Boolean,
"factual_or_spiritual": string,
"indiginous_chinese": Boolean,
"interpolations": Boolean,
"interlinear_commentary": Boolean,
"oral_transmission": Boolean,
"explicit_sentence_subject": string,
"plural_zhu": Boolean,
"tense": string,
"abbreviations": Boolean,
"notes": string}.
"""

schema = {
    "type": "object",
        "properties": {
            "verse_or_prose": {
                "type": "string",
            },
            "syllables_per_line": {
                "type": "integer",
            },
            "vernacular_or_literary": {
                "type": "string",
            },
            "literal_or_fluent": {
                "type": "string",
            },
            "ornate_or_plain_language": {
                "type": "string",
            },
            "terse_or_verbose": {
                "type": "string",
            },
            "idioms_used": {
                "type": "boolean",
            },
            "factual_or_spiritual": {
                "type": "string",
            },
            "indigenous_chinese": {
                "type": "boolean",
            },
            "interpolations": {
                "type": "boolean",
            },
            "interlinear_commentary": {
                "type": "boolean",
            },
            "oral_transmission": {
                "type": "boolean",
            },
            "explicit_sentence_subject": {
                "type": "string",
            },
            "plural_zhu": {
                "type": "boolean",
            },
            "tense": {
                "type": "string",
            },
            "abbreviations": {
                "type": "boolean",
            },
            "notes": {
                "type": "string",
            },
        }
}

DEFAULT_STYLE = {
    "verse_or_prose": "",
    "syllables_per_line": 0,
    "vernacular_or_literary": "",
    "literal_or_fluent": "",
    "ornate_or_plain_language": "",
    "terse_or_verbose": "",
    "idioms_used": False,
    "factual_or_spiritual": "",
    "indigenous_chinese": False,
    "interpolations": False,
    "interlinear_commentary": False,
    "oral_transmission": False,
    "explicit_sentence_subject": "",
    "plural_zhu": False,
    "tense": "",
    "abbreviations": False,
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
           entry["verse_or_prose"],
           entry["syllables_per_line"],
           entry["vernacular_or_literary"],
           entry["literal_or_fluent"],
           entry["ornate_or_plain_language"],
           entry["terse_or_verbose"],
           entry["idioms_used"],
           entry["factual_or_spiritual"],
           entry["indigenous_chinese"],
           entry["interpolations"],
           entry["interlinear_commentary"],
           entry["oral_transmission"],
           entry["explicit_sentence_subject"],
           entry["plural_zhu"],
           entry["tense"],
           entry["abbreviations"],
           False,
           False,
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
                   "verse_or_prose",
                   "syllables_per_line",
                   "vernacular_or_literary",
                   "literal_or_fluent",
                   "ornate_or_plain_language",
                   "terse_or_verbose",
                   "idioms_used",
                   "factual_or_spiritual",
                   "indigenous_chinese",
                   "interpolations",
                   "interlinear_commentary",
                   "oral_transmission",
                   "explicit_sentence_subject",
                   "plural_zhu",
                   "tense",
                   "abbreviations",
                   "do_not_use1",
                   "do_not_use2",
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
