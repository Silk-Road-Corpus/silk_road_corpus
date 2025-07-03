"""This script searches the Kaiyuan Lu for alternative titles.
"""

import base64
import csv
import requests
import json
import os
import cszjj

# Edit the variable `restart_at` to restart the program if it is interupted.
restart_at = "德女問經"
prompt_template = """
Is the title {title} a synonym for any other tiles listed in the given text (Kaiyuan Lu)?
Return only the alternative titles in Chinese in the form ["Title 1", "Title 2", …].
Do not return any other output."
"""
kaiyuanlu_path = "taisho/t2154.txt"
cszjj_path = "data/chusanzangjiji.csv"
taisho_path = "data/taisho.csv"


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


def send_prompt(prompt: str, file_path: str = None) -> str:
    """
    Sends a text prompt and a text file to the Gemini 2.5 Flash model.

    Args:
        prompt (str): The text prompt to send to the model.
        file_path (str, optional): The path to the file to send. Defaults to None.

    Returns:
        str: The generated text from the Gemini model, or an error message if the request fails.
    """
    api_key = os.environ.get("API_KEY", "")

    if not api_key:
        return "Warning: API_KEY environment variable not set."

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    parts = [{"text": prompt}]

    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    try:
        mime_type = "text/plain"

        with open(file_path, "rb") as f:
            file_data = f.read()
            base64_file = base64.b64encode(file_data).decode("utf-8")

            # Add the file data to the parts list
            parts.append({
                "inlineData": {
                    "mimeType": mime_type,
                    "data": base64_file
                }
        })
    except Exception as e:
        return f"Error processing file {file_path}: {e}"

    # Construct the chat history for the payload
    chat_history = [
        {"role": "user", "parts": parts}
    ]

    # Define the payload for the POST request
    payload = {
        "contents": chat_history
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
            return generated_text
        else:
            return f"Error: Unexpected response structure or no content generated. Response: {result}"

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err} - Response: {response.text}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Connection error occurred: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"Timeout error occurred: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"An error occurred: {req_err}"
    except json.JSONDecodeError as json_err:
        return f"JSON decoding error: {json_err} - Response text: {response.text}"


def write_headers_to_csv(filename, header):
    """
    Writes data to a CSV file.

    Args:
        filename (str): The name of the CSV file to write to.
        data (list of lists): The data to write. Each inner list represents a row.
        header (list, optional): A list of strings for the header row. Defaults to None.
    """
    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header)
    except IOError as e:
        print(f"Error writing header to file {filename}: {e}")


def append_to_csv(filename, data):
    """
    Append data to a CSV file.

    Args:
        filename (str): The name of the CSV file to write to.
        data (list of lists): The data to append. Each inner list represents a row.
    """
    try:
        with open(filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(data)
    except IOError as e:
        print(f"Error appending to file {filename}: {e}")


if __name__ == "__main__":
    entries = cszjj.parse_cszjj_file(cszjj_path)
    taisho_entries = parse_taisho_file(taisho_path)
    num_taisho = len(taisho_entries)
    print(f"Taisho file opened with {num_taisho} entries.")
    if len(restart_at) == 0:
        write_headers_to_csv("data/alt_titles.csv", ["CSZJJ", "Alt Title"])
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
            resp = send_prompt(prompt, file_path=kaiyuanlu_path)
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
                        append_to_csv("data/alt_titles.csv", alt_titles)
