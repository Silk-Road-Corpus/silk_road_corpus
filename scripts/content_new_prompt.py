"""This script analyzes text content with the prompt split up.

The results for content analysis with a single prompt were not
that good. This script splits the prompt into multiple, smaller
prompts to improve the results.
"""

import argparse
import cszjj
import os
import sys


file_index_path = "data/canonical_summaries.csv"
default_outfile = "data/content_new.csv"
default_model = "gemini-2.5-flash"
prompt_system = """
You are a Buddhist scholar specializing in early Chinese Buddhist texts.

Answer the following question with respect to the content of the attached
text and return the results in JSON format, choosing the values from the given
set only. Write any freeform strings in English, using
IAST Sanskrit transliteration, if needed, e.g., Śākyamuni.

Put any comments explaining the decisions in the notes field in English.
Do not insert newlines or add markdown.

Question:
"""

prompt_top_genre = """
Is the given text a sūtra, jātaka, commentary, Vinaya, or history? Do not
assume that the genre is a sūtra just because the title includes the
Chinese character 經 jīng. Possible values: 'sutra', 'jataka', 'commentary',
'vinaya', or 'history'.

JSON schema:
{"top_level_genre": string, "notes": string}
"""

prompt_taisho_genre = """
What is the Taishō genre classification of the text?
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

JSON schema:
{"taisho_genre": string, "notes": string}

"""

prompt_is_mahayana = """
Is Mahāyāna? Possible values: True or False.

JSON schema:
{"is_mahayana": Boolean, "notes": string}
"""

prompt_parable = """
Does the content contain a parable, miracle story, or biography?
A parable is an expedient means for explaining a teaching of the Buddha.
A miracle tale is a story of being saved through belief in a divine power,
especially by Avalokiteśvara, Amitābha, or the recitation of a dhāraṇī.
Or does the text consist of one or more biographies, possibly in the form
of a hagiography?

Possible values: 'parable', 'miracle_tale', 'biographies', or 'none'.

JSON schema:
{"parable_or_miracle_tale": string, "notes": string}
"""

prompt_commentary_type = """
If the text is a commentary, what type is it?
A sūtra commentary explains the meanings of the terms
used in the sūtra and the background context. Abhidharma relates to
mainstream (non-Mahāyāna) Buddhism. A treatise, also known as a Śastra,
covers a subject area and may refer to multiple texts.

Possible values: 'sūtra commentary', 'Abhidharma', 'treatise', or 'none'.

JSON schema:
{"commentary_type": Boolean, "notes": string}
"""

prompt_dialog = """
Is the text mostly in the form of a dialog?

Possible values: True or False.

JSON schema:
{"is_dialog": Boolean, "notes": string}
"""

prompt_speaker = """
What is the identity of the main speaker in the text? Leave emty if 
there is no speaker.

JSON schema:
{"speaker": string, "notes": string}
"""

prompt_dharani = """
Does the text contain a dhāraṇī?

Possible values: True or False.

JSON schema:
{"contains_dharani": Boolean "notes": string}
"""

prompt_argumentation = """
Does the text contain philosophical argumentation?

Possible values: True or False.

JSON schema:
{"philosophical_argumentation": Boolean "notes": string}
"""

prompt_rhetoric = """
Does the text contain rhetoric?

Possible values: True or False.

JSON schema:
{"contains_rhetoric": Boolean "notes": string}
"""

prompt_retribution = """
Does the text contain karmic retribution?

Possible values: True or False.

JSON schema:
{"karmic_retribution": Boolean "notes": string}
"""

prompt_people = """
List the historical people mentioned in the text.

Possible values: array.

JSON schema:
{"historical_people": array "notes": string}
"""

prompt_deities = """
List the deities mentioned in the text, including bodhisattvas and
Buddhas other than Śākyamuni.

Possible values: array.

JSON schema:
{"deities": array "notes": string}
"""

prompt_places = """
List the historical places mentioned in the text.

Possible values: array.

JSON schema:
{"places": array "notes": string}
"""

prompt_references = """
If the text is a commentary, list the names of any texts referred to.

Possible values: array.

JSON schema:
{"text_references": array "notes": string}
"""

schema_top_genre = {
    "type": "object",
        "properties": {
            "top_level_genre": {
                "type": "string",
                "enum": ["sutra", "jataka", "commentary", "vinaya", "history"],
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_taisho_genre = {
    "type": "object",
        "properties": {
            "taisho_genre": {
                "type": "string",
                "enum": ["Āgama", "Jātaka and Avadāna", "Prajñāpāramitā",
                         "Lotus", "Huayan", "Ratnakūṭa", "Nirvāṇa", "Mahāsaṃnipāta",
                         "Collected Sūtras", "Esoteric", "Vinaya", "Śastra",
                         "Abhidharma", "Madhyamaka", "Yogācāra", "Śastra",
                         "Sūtra Commentary", "Vinaya", "Śāstra Commentary"],
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_is_mahayana = {
    "type": "object",
        "properties": {
            "is_mahayana": {
                "type": "boolean",
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_parable = {
    "type": "object",
        "properties": {
            "parable_or_miracle_tale": {
                "type": "string",
                "enum": ["parable", "miracle_tale", "biographies", "none"],
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_commentary_type = {
    "type": "object",
        "properties": {
            "commentary_type": {
                "type": "string",
                "enum": ["sūtra commentary", "Abhidharma", "treatise", "none"],
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_is_dialog = {
    "type": "object",
        "properties": {
            "is_dialog": {
                "type": "boolean",
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_speaker = {
    "type": "object",
        "properties": {
            "speaker": {
                "type": "string",
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_contains_dharani = {
    "type": "object",
        "properties": {
            "contains_dharani": {
                "type": "boolean",
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_argumentation = {
    "type": "object",
        "properties": {
            "philosophical_argumentation": {
                "type": "boolean",
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_rhetoric = {
    "type": "object",
        "properties": {
            "contains_rhetoric": {
                "type": "boolean",
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_karmic_retribution = {
    "type": "object",
        "properties": {
            "karmic_retribution": {
                "type": "boolean",
            },
            "notes": {
                "type": "string",
            },
        }
}

schema_people = {
    "type": "object",
        "properties": {
            "historical_people": {
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

schema_deities = {
    "type": "object",
        "properties": {
            "deities": {
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

schema_places = {
    "type": "object",
        "properties": {
            "places": {
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

schema_references = {
    "type": "object",
        "properties": {
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

    if "filepath" not in entry:
        result["error"] = "filepath not given"
        return result
    fname = entry["filepath"]
    filepath = fname
    if fname.startswith("$nti"):
        filepath = nti + fname[4:]
    notes = []
    errors = []

    try:
        p1 = prompt_system + prompt_top_genre
        r1 = cszjj.send_prompt_file_and_schema(p1,
                                               file_path=filepath,
                                               response_schema=schema_top_genre)
        result["top_level_genre"] = r1.get("top_level_genre", "")
        if r1.get("notes"):
            notes.append("top_level_genre: " + r1.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing top_level_genre: {e}.")

    try:
        p2 = prompt_system + prompt_taisho_genre
        r2 = cszjj.send_prompt_file_and_schema(p2,
                                               file_path=filepath,
                                               response_schema=schema_taisho_genre)
        result["taisho_genre"] = r2.get("taisho_genre", "")
        if r2.get("notes"):
            notes.append("taisho_genre: " + r2.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing taisho_genre: {e}.")

    try:
        p3 = prompt_system + prompt_is_mahayana
        r3 = cszjj.send_prompt_file_and_schema(p3,
                                               file_path=filepath,
                                               response_schema=schema_is_mahayana)
        result["is_mahayana"] = r3.get("is_mahayana", "")
        if r3.get("notes"):
            notes.append("is_mahayana: " + r3.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing is_mahayana: {e}.")

    try:
        p4 = prompt_system + prompt_parable
        r4 = cszjj.send_prompt_file_and_schema(p4,
                                               file_path=filepath,
                                               response_schema=schema_parable)
        result["parable_or_miracle_tale"] = r4.get("parable_or_miracle_tale", "")
        if r4.get("notes"):
            notes.append("parable_or_miracle_tale: " + r4.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing parable_or_miracle_tale: {e}.")

    try:
        p5 = prompt_system + prompt_commentary_type
        r5 = cszjj.send_prompt_file_and_schema(p5,
                                               file_path=filepath,
                                               response_schema=schema_commentary_type)
        result["commentary_type"] = r5.get("commentary_type", "")
        if r4.get("notes"):
            notes.append("commentary_type: " + r4.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing commentary_type: {e}.")

    try:
        p6 = prompt_system + prompt_dialog
        r6 = cszjj.send_prompt_file_and_schema(p6,
                                               file_path=filepath,
                                               response_schema=schema_is_dialog)
        result["is_dialog"] = r6.get("is_dialog", "")
        if r6.get("notes"):
            notes.append("is_dialog: " + r6.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing is_dialog: {e}.")

    try:
        p7 = prompt_system + prompt_speaker
        r7 = cszjj.send_prompt_file_and_schema(p7,
                                               file_path=filepath,
                                               response_schema=schema_speaker)
        result["speaker"] = r7.get("speaker", "")
        if r7.get("notes"):
            notes.append("speaker: " + r7.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing speaker: {e}.")

    try:
        p8 = prompt_system + prompt_dharani
        r8 = cszjj.send_prompt_file_and_schema(p8,
                                               file_path=filepath,
                                               response_schema=schema_contains_dharani)
        result["contains_dharani"] = r8.get("contains_dharani", "")
        if r8.get("notes"):
            notes.append("contains_dharani: " + r8.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing contains_dharani: {e}.")

    try:
        p9 = prompt_system + prompt_argumentation
        r9 = cszjj.send_prompt_file_and_schema(p9,
                                               file_path=filepath,
                                               response_schema=schema_argumentation)
        result["philosophical_argumentation"] = r9.get("philosophical_argumentation", "")
        if r9.get("notes"):
            notes.append("philosophical_argumentation: " + r9.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing philosophical_argumentation: {e}.")

    try:
        p10 = prompt_system + prompt_rhetoric
        r10 = cszjj.send_prompt_file_and_schema(p10,
                                                file_path=filepath,
                                                response_schema=schema_rhetoric)
        result["contains_rhetoric"] = r10.get("contains_rhetoric", "")
        if r10.get("notes"):
            notes.append("contains_rhetoric: " + r10.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing contains_rhetoric: {e}.")

    try:
        p11 = prompt_system + prompt_retribution
        r11 = cszjj.send_prompt_file_and_schema(p11,
                                                file_path=filepath,
                                                response_schema=schema_karmic_retribution)
        result["karmic_retribution"] = r11.get("karmic_retribution", "")
        if r11.get("notes"):
            notes.append("karmic_retribution: " + r11.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing karmic_retribution: {e}.")

    try:
        p12 = prompt_system + prompt_people
        r12 = cszjj.send_prompt_file_and_schema(p12,
                                                file_path=filepath,
                                                response_schema=schema_people)
        people = r12.get("historical_people", [])
        result["historical_people"] = ", ".join(people)
        if r12.get("notes"):
            notes.append("historical_people: " + r12.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing historical_people: {e}.")

    try:
        p13 = prompt_system + prompt_deities
        r13 = cszjj.send_prompt_file_and_schema(p13,
                                                file_path=filepath,
                                                response_schema=schema_deities)
        deities = r13.get("deities", [])
        result["deities"] = ", ".join(deities)
        if r13.get("notes"):
            notes.append("deities: " + r13.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing deities: {e}.")

    try:
        p14 = prompt_system + prompt_places
        r14 = cszjj.send_prompt_file_and_schema(p14,
                                                file_path=filepath,
                                                response_schema=schema_places)
        places = r14.get("places", [])
        result["places"] = ", ".join(places)
        if r14.get("notes"):
            notes.append("places: " + r14.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing places: {e}.")

    try:
        p15 = prompt_system + prompt_references
        r15 = cszjj.send_prompt_file_and_schema(p15,
                                                file_path=filepath,
                                                response_schema=schema_references)
        text_references = r15.get("text_references", [])
        result["text_references"] = ", ".join(text_references)
        if r15.get("notes"):
            notes.append("text_references: " + r15.get("notes"))
    except Exception as e:
        errors.append(f"An error occurred processing text_references: {e}.")

    result["notes"] = ", ".join(notes)
    if errors:
        print(f"Error for entry {title_zh}: {', '.join(errors)}")
        result['error'] = ", ".join(errors)
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
