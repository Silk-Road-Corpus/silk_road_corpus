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
17. Is 為 wèi used as a cupola (wei_for_cupola)? Return: a Boolean value.
18. Is 謂 wèi used as a cupola (wei_call_cupola)? Return: a Boolean value.

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
"wei_for_cupola": Boolean,
"wei_call_cupola": Boolean,
"notes": string}.
"""

def analyze_style(nti, entry):
    """Analysze style of the given text.

    Returns:
        dictionary: a dictionary following the rubric in the prompt.
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
            "style": {},
            "error": "filepath not given",
        }
    fname = entry["filepath"]
    filepath = fname
    if fname.startswith("$nti"):
        filepath = nti + fname[4:]
    # print(f"Analyzing style for entry {title_zh}, {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            error = ""
            content = file.read()
            try:
                result = cszjj.send_prompt(prompt_template, file_path=filepath)
                if isinstance(result, str):
                    error += result
                    result = {}
            except Exception as e:
                error += f"Got a error from the model: {e}"
            verse_or_prose = ""
            syllables_per_line = 0
            vernacular_or_literary = ""
            literal_or_fluent = ""
            ornate_or_plain_language = ""
            terse_or_verbose = ""
            idioms_used = False
            factual_or_spiritual = ""
            indigenous_chinese = False
            interpolations = False
            interlinear_commentary = False
            oral_transmission = False
            explicit_sentence_subject = ""
            plural_zhu = False
            tense = ""
            abbreviations = False
            wei_for_cupola = False
            wei_call_cupola = False
            notes = ""
            if "verse_or_prose" in result:
                verse_or_prose = result["verse_or_prose"]
            if "syllables_per_line" in result:
                syllables_per_line = result["syllables_per_line"]
            if "vernacular_or_literary" in result:
                vernacular_or_literary = result["vernacular_or_literary"]
            if "literal_or_fluent" in result:
                literal_or_fluent = result["literal_or_fluent"] 
            if "ornate_or_plain_language" in result:
                ornate_or_plain_language = result["ornate_or_plain_language"]
            if "terse_or_verbose" in result:
                terse_or_verbose = result["terse_or_verbose"]
            if "idioms_used" in result:
                idioms_used = result["idioms_used"]
            if "factual_or_spiritual" in result:
                factual_or_spiritual = result["factual_or_spiritual"]
            if "indigenous_chinese" in result:
                indigenous_chinese = result["indigenous_chinese"]
            if "interpolations" in result:
                interpolations = result["interpolations"]
            if "interlinear_commentary" in result:
                interlinear_commentary = result["interlinear_commentary"]
            if "oral_transmission" in result:
                oral_transmission = result["oral_transmission"]
            if "explicit_sentence_subject" in result:
                explicit_sentence_subject = result["explicit_sentence_subject"]
            if "plural_zhu" in result:
                plural_zhu = result["plural_zhu"]
            if "tense" in result:
                tense = result["tense"]
            if "abbreviations" in result:
                abbreviations = result["abbreviations"]
            if "wei_for_cupola" in result:
                wei_for_cupola = result["wei_for_cupola"]
            if "wei_call_cupola" in result:
                wei_call_cupola = result["wei_call_cupola"]
            if "notes" in result:
                notes = result["notes"]
            else:
                print(f"No notes found for entry {title_zh}: {result}")
            return {
                "title_zh": title_zh,
                "taisho_no": entry["taisho_no"],
                "verse_or_prose": verse_or_prose,
                "syllables_per_line": syllables_per_line,
                "vernacular_or_literary": vernacular_or_literary,
                "literal_or_fluent": literal_or_fluent,
                "ornate_or_plain_language": ornate_or_plain_language,
                "terse_or_verbose": terse_or_verbose,
                "idioms_used": idioms_used,
                "factual_or_spiritual": factual_or_spiritual,
                "indigenous_chinese": indigenous_chinese,
                "interpolations": interpolations,
                "interlinear_commentary": interlinear_commentary,
                "oral_transmission": oral_transmission,
                "explicit_sentence_subject": explicit_sentence_subject,
                "plural_zhu": plural_zhu,
                "tense": tense,
                "abbreviations": abbreviations,
                "wei_for_cupola": wei_for_cupola,
                "wei_call_cupola": wei_call_cupola,
                "notes": notes,
                "error": error,
            }
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return {
            "title_zh": title_zh,
            "taisho_no": entry["taisho_no"],
            "verse_or_prose": None,
            "syllables_per_line": None,
            "vernacular_or_literary": None,
            "literal_or_fluent": None,
            "ornate_or_plain_language": None,
            "terse_or_verbose": None,
            "idioms_used": None,
            "factual_or_spiritual": None,
            "indigenous_chinese": None,
            "interpolations": None,
            "interlinear_commentary": None,
            "oral_transmission": None,
            "explicit_sentence_subject": None,
            "plural_zhu": None,
            "tense": None,
            "abbreviations": None,
            "wei_for_cupola": None,
            "wei_call_cupola": None,
            "notes": None,
            "error": f"The file '{filepath}' was not found.",
        }
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return {
            "title_zh": title_zh,
            "taisho_no": entry["taisho_no"],
            "verse_or_prose": None,
            "syllables_per_line": None,
            "vernacular_or_literary": None,
            "literal_or_fluent": None,
            "ornate_or_plain_language": None,
            "terse_or_verbose": None,
            "idioms_used": None,
            "factual_or_spiritual": None,
            "indigenous_chinese": None,
            "interpolations": None,
            "interlinear_commentary": None,
            "oral_transmission": None,
            "explicit_sentence_subject": None,
            "plural_zhu": None,
            "tense": None,
            "abbreviations": None,
            "wei_for_cupola": None,
            "wei_call_cupola": None,
            "notes": None,
            "error": f"An error occurred while reading the file: {e}",
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
           entry["wei_for_cupola"],
           entry["wei_call_cupola"],
           entry["notes"],
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
                   "wei_for_cupola",
                   "wei_call_cupola",
                   "notes",
                   "error",
                   "notes",
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
