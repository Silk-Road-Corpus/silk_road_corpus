"""This script searches texts for Buddhist terminology and language useage.
"""

import argparse
import cszjj
import os
import sys


cszjj_path = "data/chusanzangjiji.csv"
file_index_path = "data/canonical_summaries.csv"
analysis_filename = "data/linguistic_analysis.csv"

schema = {
    "type": "object",
        "properties": {
            "count": {
                "type": "integer"
            }
        }
}
system_prompt = "You are an expert in historical Chinese linguistics."
explanation = """Return only the integer number and no other output. The text
has been punctuated for the convenience of modern readers but the punctuation
is not accurate. Do not include terms in the preface of the text.
"""
final_particle_prompt = """
{system_prompt} How many times does the character {given_char} used as a final particle
at the end of declarative sentences in the given text [text uploaded] {explanation}? 
"""
ye2_prompt = """
{system_prompt} How many times does the character '耶' appear at end of yes or no questions
or as a final particle at the end of declarative sentences in the given text
[text uploaded] {explanation}?
"""
wei_prompt = """
{system_prompt} How many times is the character 謂 wèi used for delegated agency or as a
semi-copula {explanation}? 
"""
bei_prompt = """
{system_prompt} How many passive sentences using the 被 bèi passive construction are there
in this text?  {explanation}
"""
di_prompt = """
{system_prompt} How many times does the character 的 dì in the sense of 'indeed' or
'certainly' occur in this text?  {explanation}
"""
shigu_prompt = """
{system_prompt} How many times does the term 事故 shìgù in the sense of 'accident' or
'disaster' occur in this text?  {explanation}
"""
yiqie_prompt = """
{system_prompt} How many times does the term 一切 yīqiè  in the sense of 'all'
occur in this text?  {explanation}
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
            content = cszjj.strip_boiler_plate(content)
            ye2_count = phrase_count(content, "耶")
            ye2_final_count = 0
            error = ""
            if ye2_count > 0:
                try:
                    prompt = ye2_prompt.format(system_prompt=system_prompt,
                                               explanation=explanation)
                    r1 = cszjj.send_prompt_file_and_schema(prompt,
                                                           file_path=filepath,
                                                           response_schema=schema)
                    ye2_final_count = r1.get("count", 0)
                except:
                    error = f"Got an error from the model for 耶: {r1}\n"
            er3_count = phrase_count(content, "耳")
            er3_final_count = 0
            if er3_count > 0:
                try:
                    prompt = final_particle_prompt.format(system_prompt=system_prompt,
                                               given_char="耳",
                                               explanation=explanation)
                    r2 = cszjj.send_prompt_file_and_schema(prompt,
                                                           file_path=filepath,
                                                           response_schema=schema)
                    er3_final_count = r2.get("count", 0)
                except:
                    error += f"Got an error from the model for 耳: {r2}\n"
            ye3_count = phrase_count(content, "也")
            ye3_final_count = 0
            if ye3_count > 0:
                try:
                    prompt = final_particle_prompt.format(system_prompt=system_prompt,
                                                          given_char="也",
                                                          explanation=explanation)
                    r3 = cszjj.send_prompt_file_and_schema(prompt,
                                                           file_path=filepath,
                                                           response_schema=schema)
                    ye3_final_count = r3.get("count", 0)
                except:
                    error = f"Got an error from the model for 也: {r3}\n"
            wei4_count = phrase_count(content, "謂")
            wei4_grammar_count = 0
            if wei4_count > 0:
                try:
                    prompt = wei_prompt.format(system_prompt=system_prompt,
                                               explanation=explanation)
                    r4 = cszjj.send_prompt_file_and_schema(prompt,
                                                           file_path=filepath,
                                                           response_schema=schema)
                    wei4_grammar_count = r4.get("count", 0)
                except:
                    error = f"Got an error from the model for 謂: {r4}\n"
            bei4_count = phrase_count(content, "被")
            bei4_grammar_count = 0
            if bei4_count > 0:
                try:
                    prompt = bei_prompt.format(system_prompt=system_prompt,
                                               explanation=explanation)
                    r5 = cszjj.send_prompt_file_and_schema(prompt,
                                                           file_path=filepath,
                                                           response_schema=schema)
                    bei4_grammar_count = r5.get("count", 0)
                except:
                    error = f"Got an error from the model for 被: {r5}\n"
            hezhe_count = phrase_count(content, "何者")
            hedengren_count = phrase_count(content, "何等人")
            cun_count = phrase_count(content, "村")
            tian_count = phrase_count(content, "添")
            sixiang_count = phrase_count(content, "思想")
            di_count = phrase_count(content, "的")
            di_sense_count = 0
            if di_count > 0:
                try:
                    prompt = di_prompt.format(system_prompt=system_prompt,
                                               explanation=explanation)
                    r6 = cszjj.send_prompt_file_and_schema(prompt,
                                                           file_path=filepath,
                                                           response_schema=schema)
                    di_sense_count = r6.get("count", 0)
                except:
                    error = f"Got an error from the model for 的: {r6}\n"
            shigu_count = phrase_count(content, "事故")
            shigu_sense_count = 0
            if shigu_count > 0:
                try:
                    prompt = shigu_prompt.format(system_prompt=system_prompt,
                                               explanation=explanation)
                    r7 = cszjj.send_prompt_file_and_schema(prompt,
                                                           file_path=filepath,
                                                           response_schema=schema)
                    shigu_sense_count = r7.get("count", 0)
                except:
                    error = f"Got an error from the model for 事故: {r6}\n"
            yiqie_count = phrase_count(content, "一切")
            yiqie_sense_count = 0
            if yiqie_count > 0:
                try:
                    prompt = yiqie_prompt.format(system_prompt=system_prompt,
                                               explanation=explanation)
                    r8 = cszjj.send_prompt_file_and_schema(prompt,
                                                           file_path=filepath,
                                                           response_schema=schema)
                    yiqie_sense_count = r8.get("count", 0)
                except:
                    error = f"Got an error from the model for 一切: {r6}\n"
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
                "wei4_count": wei4_count,
                "wei4_grammar_count": wei4_grammar_count,
                "bei_count": bei4_count,
                "bei_grammar_count": bei4_grammar_count,
                "hezhe_count": hezhe_count,
                "hedengren_count": hedengren_count,
                "cun_count": cun_count,
                "tian_count": tian_count,
                "sixiang_count": sixiang_count,
                "di_count": di_count,
                "di_sense_count": di_sense_count,
                "shigu_count": shigu_count,
                "shigu_sense_count": shigu_sense_count,
                "yiqie_count": yiqie_count,
                "yiqie_sense_count": yiqie_sense_count,
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

    count_zai = phrase_count(content, "哉")
    return count_zai - 2 * count_shanzai


def phrase_count(content, char_to_find):
    """Find the number of occurence of a phrase in a string content

    Return:
        int: The number of occurences
    """
    count = 0
    for char in content:
        if char == char_to_find:
            count += 1
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
           entry["wei4_count"],
           entry["wei4_grammar_count"],
           entry["bei_count"],
           entry["bei_grammar_count"],
           entry["hezhe_count"],
           entry["hedengren_count"],
           entry["cun_count"],
           entry["tian_count"],
           entry["sixiang_count"],
           entry["di_count"],
           entry["di_sense_count"],
           entry["shigu_count"],
           entry["shigu_sense_count"],
           entry["yiqie_count"],
           entry["yiqie_sense_count"],
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
        description="Searches texts for Buddhist terminology and language useage"
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
        '-r', '--restart',
        type=str,
        required=False,
        help='Restart processing all records at the given CSZJJ title'
    )
    args = parser.parse_args()
    if args.title:
        print(f"Processing {args.title}")
        entries = cszjj.find_entry(file_index_path, args.title, args.fascicle, None)
        for entry in entries:
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
               "wei4_count",
               "wei4_grammar_count",
               "bei_count",
               "bei_grammar_count",
               "hezhe_count",
               "hedengren_count",
               "cun_count",
               "tian_count",
               "sixiang_count",
               "di_count",
               "di_sense_count",
               "shigu_count",
               "shigu_sense_count",
               "yiqie_count",
               "yiqie_sense_count",
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
