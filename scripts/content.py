"""This script analyzes text content and saves the results in a CSV file.
"""

import argparse
import cszjj
import os
import sys


file_index_path = "data/canonical_summaries.csv"
default_outfile = "data/content.csv"
default_model = "gemini-2.5-flash"
prompt_template = """
You are a Buddhist scholar specializing in early Chinese Buddhist texts.

Evaluate the content of the following text using the following rubric
and return the results in JSON format.

1. Top level genre: is the given text a sūtra, jātaka, commentary,
   Vinaya, or history? Do not assume that the genre is a sūtra just because
   the title includes the Chinese character 經 jīng.
   Possible values: 'sutra', 'jataka', 'commentary', 'vinaya', or
   'history'.
2. Taishō genre: what is the Taishō genre classification of the text?
   The Taishō genres and their corresponding English equivalents are:
   Āgama 阿含, Jātaka and Avadāna 本緣, Prajñāpāramitā 般若, Lotus 法華,
   Huayan 華嚴, Ratnakūṭa 寶積, Nirvāṇa 涅槃, Mahāsaṃnipāta 大集,
   Collected Sūtras 經集, Esoteric 密教, Vinaya 律藏,
   Sūtra Explanation 釋經論, Abhidharma 毘曇, Madhyamaka 中觀,
   Yogācāra 瑜伽, Śastra 論, Sūtra Commentary 經疏, and Vinaya 律.
   Possible values: 'Āgama', 'Jātaka and Avadāna', 'Prajñāpāramitā',
   'Lotus', 'Huayan', 'Ratnakūṭa', 'Nirvāṇa', 'Mahāsaṃnipāta',
   'Collected Sūtras', 'Esoteric', 'Vinaya', 'Śastra',
   'Abhidharma', 'Madhyamaka', 'Yogācāra', 'Śastra',
   'Sūtra Commentary', 'Vinaya', or 'Śāstra Commentary'.
3. Is Mahāyāna? Possible values: True or False.
4. Parable or miracle tale: A parable is an expedient means for explaining
   a teaching of the Buddha. A miracle tale is a story of being saved through
   belief in a divine power, especially by Avalokiteśvara, Amitābha, or the
   recitation of a dhāraṇī. OOr does the text consist of one or more
   biographies, possibly in the form of a hagiography?
   Possible values: 'parable', 'miracle_tale', 'biographies', or
   'none'.
5. Commentary type: A sūtra commentary explains the meanings of the terms
   used in the sūtra and the background context. Abhidharma relates to
   mainstream (non-Mahāyāna) Buddhism. A treatise, also known as a Śastra,
   covers a subject area and may refer to multiple texts. Possible values:
   'sūtra commentary', 'Abhidharma', 'treatise', or 'none'.
6. Is a dialog: Is the text mostly in the form of a dialog? Possible values:
   True or False. 
7. Speaker: The value of this parameter is the identity of the speaker
   empty if there is no speaker. Give the name of the speaker in English with
   IAST Sanskrit transliteration, if needed, e.g., Śākyamuni.
8. Contains a dhāraṇī: Does the text contain a dhāraṇī? Possible values: True or False.
9. Philosophical argumentation: Does the text contain philosophical argumentation?
   Possible values: True or False.
10. Contains rhetoric: Does the text contain rhetoric? Possible values: True or False.
11. Karmic retribution: Does the text contain a story of karmic retribution or
    karmic causes and conditions? Possible values: True or False.
12. Historical people: List the historical people mentioned in the text.
    Give the names in English with IAST Sanskrit transliteration, if needed.
13. Deities: List the deities mentioned in the text, including bodhisattvas and
    Buddhas other than Śākyamuni.
    Give the names in English with IAST Sanskrit transliteration, if needed.
14. Places: List the historical places mentioned in the text.
    Give the place names in English with IAST Sanskrit transliteration, if needed.
15. Text references: If the text is a commentary, list the names in Chinese and
    English of any texts referred to.
    Give the titles in English with IAST Sanskrit transliteration, if needed.

Put any comments explaining the decisions in the notes field.

Return the result in the following JSON format. For the string types use only
the enumerations given, not an explanation.
Put the explanation in the notes field.
{"top_level_genre": string,
"taisho_genre": string,
"is_mahayana": Boolean,
"parable_or_miracle_tale": string,
"commentary_type": string,
"is_dialog": Boolean,
"speaker": string,
"contains_dharani": Boolean,
"philosophical_argumentation": Boolean,
"contains_rhetoric": Boolean,
"karmic_retribution": Boolean,
"historical_people": array,
"deities": array,
"places": array,
"text_references": array,
"notes": string}.
"""

schema = {
    "type": "object",
        "properties": {
            "top_level_genre": {
                "type": "string",
                "enum": ["sutra", "jataka", "commentary", "vinaya", "history"],
            },
            "taisho_genre": {
                "type": "string",
                "enum": ["Āgama", "Jātaka and Avadāna", "Prajñāpāramitā",
                         "Lotus", "Huayan", "Ratnakūṭa", "Nirvāṇa", "Mahāsaṃnipāta",
                         "Collected Sūtras", "Esoteric", "Vinaya", "Śastra",
                         "Abhidharma", "Madhyamaka", "Yogācāra", "Śastra",
                         "Sūtra Commentary", "Vinaya", "Śāstra Commentary"],
            },
            "is_mahayana": {
                "type": "boolean",
            },
            "parable_or_miracle_tale": {
                "type": "string",
                "enum": ["parable", "miracle_tale", "biographies", "none"],
            },
            "commentary_type": {
                "type": "string",
                "enum": ["sūtra commentary", "Abhidharma", "treatise", "none"],
            },
            "is_dialog": {
                "type": "boolean",
            },
            "speaker": {
                "type": "string",
            },
            "contains_dharani": {
                "type": "boolean",
            },
            "philosophical_argumentation": {
                "type": "boolean",
            },
            "contains_rhetoric": {
                "type": "boolean",
            },
            "karmic_retribution": {
                "type": "boolean",
            },
            "historical_people": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "deities": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "places": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "text_references": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "notes": {
                "type": "string",
            },
        }
}

DEFAULT_CONTENT = {
    "top_level_genre": "",
    "taisho_genre": "",
    "is_mahayana": "",
    "parable_or_miracle_tale": "",
    "commentary_type": "",
    "is_dialog": "",
    "speaker": "",
    "contains_dharani": "",
    "philosophical_argumentation": "",
    "contains_rhetoric": "",
    "karmic_retribution": "",
    "historical_people": [],
    "deities": [],
    "places": [],
    "text_references": [],
    "notes": "",
}


def analyze_content(nti, entry, model):
    """Analyze content of the given text.
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
    # Initialize with default content values for the success case.
    result.update(DEFAULT_CONTENT)

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
            # Populate result with data from content_data, using defaults from DEFAULT_CONTENT
            for key, default_value in DEFAULT_CONTENT.items():
                result[key] = response.get(key, default_value)

        except FileNotFoundError:
            result["error"] = f"The file '{filepath}' was not found."
        except Exception as e:
            result["error"] = f"An error occurred: {e}"

    if result["error"]:
        print(f"Error for entry {title_zh}: {result['error']}")
        # For errors, null out the fields.
        for key in DEFAULT_CONTENT:
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
           entry["top_level_genre"],
           entry["taisho_genre"],
           entry["is_mahayana"],
           entry["parable_or_miracle_tale"],
           entry["commentary_type"],
           entry["is_dialog"],
           entry["speaker"],
           entry["contains_dharani"],
           entry["philosophical_argumentation"],
           entry["contains_rhetoric"],
           entry["karmic_retribution"],
           entry["historical_people"],
           entry["deities"],
           entry["places"],
           entry["text_references"],
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
    parser.add_argument(
        '-m', '--model',
        type=str,
        required=False,
        help='AI Mmodel to use'
    )
    parser.add_argument(
        '-o', '--outfile',
        type=str,
        required=False,
        help='Name of file to write output to'
    )
    args = parser.parse_args()
    model = default_model
    if args.model:
        model = args.model
    output_filename = default_outfile
    if args.outfile:
        output_filename = args.outfile
    if args.title:
        print(f"Processing args, title: {args.title}, fascicle: {args.fascicle}, "
              f"start_title: {args.restart_at}")
        entries = cszjj.find_entry(file_index_path, args.title, args.fascicle, None)
        for entry in entries:
            result = analyze_content(nti, entry, model)
            append_result(output_filename, result)
        sys.exit()

    if not args.restart_at:
        headers = ["CSZJJ",
                   "Taisho No.",
                   "top_level_genre",
                   "taisho_genre",
                   "is_mahayana",
                   "parable_or_miracle_tale",
                   "commentary_type",
                   "is_dialog",
                   "speaker",
                   "contains_dharani",
                   "philosophical_argumentation",
                   "contains_rhetoric",
                   "karmic_retribution",
                   "historical_people",
                   "deities",
                   "places",
                   "text_references",
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
        result = analyze_content(nti, entry, model)
        append_result(output_filename, result)
        
    print(f"Results written to {output_filename}")
