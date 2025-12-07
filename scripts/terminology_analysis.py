"""Analyze the terminology collected from Taisho entries.
"""

import argparse
import csv
import cszjj


term_dict_input = "data/terminology_list.csv"
term_dict_output = "data/terminology_analysis.csv"
prompt_template = """
For the term '{term}', give whether the term is valid Buddhist terminology,
Hanyu pinyin for the Chinese, the type of translation, English equivalent,
Sanskrit equivalent, and any notes. The
translation type may be one of the following values: 'Semantic', 'Mixed',
'Transliteration', 'New meaning', 'Buddhist idiom', 'Buddhist saying',
'Generic phrase', or 'Partial term' (if not valid Buddhist terminology). 
The 'Mixed' value indicates that the term is a mixture of transliteration
and semantic translation, for example,'Buddhaland' 佛土, which combines the
transliteration 'Buddha' 佛 with the semantic translation 'land' 土. An
example of semantic translation is 'Dharma King' 法王. A 'New meaning' is
a translation based on a newly invented senses of a Chinese word, for
example, śūnyatā 空. Buddhist idioms are the Buddhist equivalent of
traditional four-character Chinese idioms 成語, for example,
'a deluge of heavenly flowers' 天華亂墜. A 'Buddhist saying' is a concise
form of a proverb. 'Generic phrase' and 'Partial term' apply only if the
phrase is not valid Buddhist terminology. The Sanskrit equivalent should be
provided in International Alphabet of Sanskrit Transliteration (IAST). 
Return the result in the
following JSON format: {"valid_terminology": Boolean, "hanyu_pinyin": string,
"translation_type": string, "english_equivalent": string,
"sanskrit_equivalent": string, "notes": string}. 
"""


def parse_term_dict_file(file_path):
    """
    Parses the terminology dictionary CSV file and returns its content as a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary is a row in the file.
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
                        "term": row[0],
                        "introduced_by": row[1],
                    }
                    data.append(entry)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
        raise
    return data


def analyze_terminology(entry):
    """Analyze terminology with AI model.

    Returns:
        dictionary: a dictionary with an analysis
    """
    if "term" not in entry:
        print(f"term not in entry {entry}")
        return {}
    term = entry["term"]
    introduced_by = None
    if "introduced_by" in entry:
        introduced_by = entry["introduced_by"]
    prompt = prompt_template.replace("{term}", term)
    schema = {
        "type": "object",
            "properties": {
                "valid_terminology": {
                    "type": "boolean",
                },
                "hanyu_pinyin": {
                    "type": "string",
                },
                "translation_type": {
                    "type": "string",
                },
                "english_equivalent": {
                    "type": "string",
                },
                "sanskrit_equivalent": {
                    "type": "string",
                },
                "notes": {
                    "type": "string",
                },
            }
        }
    try:
        result = cszjj.send_prompt_with_schema(prompt)
        valid_terminology = False
        if "valid_terminology" in result:
            valid_terminology = result["valid_terminology"]
        hanyu_pinyin = ""
        if "hanyu_pinyin" in result:
            hanyu_pinyin = result["hanyu_pinyin"]
        translation_type = ""
        if "translation_type" in result:
            translation_type = result["translation_type"]
        english_equivalent = ""
        if "english_equivalent" in result:
            english_equivalent = result["english_equivalent"]
        sanskrit_equivalent = ""
        if "sanskrit_equivalent" in result:
            sanskrit_equivalent = result["sanskrit_equivalent"]
        notes = ""
        if "notes" in result:
            notes = result["notes"]
        return {
            "term": term,
            "term_introduced_by": introduced_by,
            "valid_terminology": valid_terminology,
            "hanyu_pinyin": hanyu_pinyin,
            "translation_type": translation_type,
            "english_equivalent": english_equivalent,
            "sanskrit_equivalent": sanskrit_equivalent,
            "notes": notes,
            "error": "",
        }
    except Exception as e:
        error = f"Got a error from the model: {e}"
        return {
            "term": term,
            "term_introduced_by": introduced_by,
            "valid_terminology": False,
            "hanyu_pinyin": "",
            "translation_type": "",
            "english_equivalent": "",
            "sanskrit_equivalent": "",
            "notes": "",
            "error": error,
        }
    return {}


def write_result_to_csv(filename, data):
    """
    Writes a single result to the given CSV file.

    Args:
        filename (str): The name of the CSV file to write to.
        data (dictionary of fields): The data to write. Each inner list represents a row.
    """
    try:
        with open(filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            r = [data["term"],
                 data["term_introduced_by"],
                 data["valid_terminology"],
                 data["hanyu_pinyin"],
                 data["translation_type"],
                 data["english_equivalent"],
                 data["sanskrit_equivalent"],
                 data["notes"],
                 data["error"],
                 ""]
            csv_writer.writerow(r)
    except IOError as e:
        print(f"Error writing data to file {filename}: {e}")


def write_header_to_csv(filename):
    """
    Writes the header to the given CSV file.

    Args:
        filename (str): The name of the CSV file to write to.
        header (list, optional): A list of strings for the header row. Defaults to None.
    """
    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            header = [
                "term",
                "term_introduced_by",
                "valid_terminology",
                "hanyu_pinyin",
                "translation_type",
                "english_equivalent",
                "sanskrit_equivalent",
                "notes",
                "error",
                "validation"]
            csv_writer.writerow(header)
    except IOError as e:
        print(f"Error writing header to file {filename}: {e}")


if __name__ == "__main__":
    print("Analyzing terminology")

    # Process command line arguments
    parser = argparse.ArgumentParser(
        description="Analyze Buddhist terminology collected from Taisho texts"
    )
    parser.add_argument(
        '-r', '--restart_at',
        type=str,
        required=False,
        help='Begin processing starting at the given term'
    )
    parser.add_argument(
        '-t', '--term',
        type=str,
        required=False,
        help='Process only the given term'
    )
    args = parser.parse_args()
    start_found = False
    if not args.restart_at and not args.term:
        # Start at the beginning
        write_header_to_csv(term_dict_output)
    entries = parse_term_dict_file(term_dict_input)
    print(f"Found {len(entries)} entries")
    for entry in entries:
        term = entry["term"]
        if args.restart_at and (not start_found) and (args.restart_at != term):
            continue
        if args.restart_at and (args.restart_at == term):
            start_found = True
        if args.term and (args.term != term):
          continue
        result = analyze_terminology(entry)
        write_result_to_csv(term_dict_output, result)
        if args.term and (args.term == term):
          break
    print("Done")
