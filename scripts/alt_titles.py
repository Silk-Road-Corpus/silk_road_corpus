"""This script searches the Kaiyuan Lu for alternative titles.
"""

import csv
import cszjj
import json

# Edit the variable `restart_at` to restart the program if it is interupted.
restart_at = "德女問經"
prompt_template = """
Is the title {title} a synonym for any other tiles listed in the given text (Kaiyuan Lu)?
Return only the alternative titles in Chinese in the form ["Title 1", "Title 2", …].
Do not return any other output.
"""
kaiyuanlu_path = "taisho/t2154.txt"
cszjj_path = "data/chusanzangjiji.csv"
taisho_path = "data/taisho.csv"
alt_titles_path = "data/alt_titles.csv"

def parse_taisho_file(file_path):
    """
    Parses the Taisho CSV file and returns its content as a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A dictionary of lists, where each dictionary entry represents a Taisho entry
        and the keys are the Taisho titles.
    """
    data = {}
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvfile) # Skip header row
            i = 0
            for row in csvreader:
                if len(row) > 1:
                    title_zh = row[1]
                    data[title_zh] = row
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
    return data


if __name__ == "__main__":
    entries = cszjj.parse_cszjj_file(cszjj_path)
    taisho_entries = parse_taisho_file(taisho_path)
    num_taisho = len(taisho_entries)
    print(f"Taisho file opened with {num_taisho} entries.")
    if len(restart_at) == 0:
        cszjj.write_headers_to_csv(alt_titles_path, ["CSZJJ", "Alt Title"])
    for entry in entries:
        title_zh = entry["title_zh"]
        if len(restart_at) > 0 and restart_at != title_zh:
            continue
        if len(restart_at) > 0 and restart_at == title_zh:
            print(f"restarting with {restart_at}")
            restart_at = ""
        fascicle = entry["fascicle"]
        if fascicle == 3 or fascicle == 4:
            taisho_title_zh = entry["taisho_title_zh"]
            if title_zh == taisho_title_zh:
                print(f"title_zh {title_zh} exactly matches the Taisho title. Skipping.")
                continue
            if len(title_zh) > 2 and title_zh[:2] == "佛說":
                print(f"title_zh {title_zh} varies only by 佛說 from the Taisho title. Skipping.")
                continue
            prompt = prompt_template.format(title=title_zh)
            print(f"\nSending prompt with text file: '{prompt}' and file '{kaiyuanlu_path}' to Gemini ...")
            resp = cszjj.send_prompt(prompt, file_path=kaiyuanlu_path)
            print("\n--- Gemini Response ---")
            print(resp)
            try:
                parsed_data = json.loads(resp)
            except:
                print(f"Error parsing alt titles")
                continue
            if parsed_data:
                for t in parsed_data:
                    if t in taisho_entries:
                        print(f"Found {t} in the Taisho")
                        entry = [title_zh, t]
                        alt_titles = []
                        alt_titles.append(entry)
                        cszjj.append_to_csv(alt_titles_path, alt_titles)
