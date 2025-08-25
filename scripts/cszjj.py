"""This module provides utilities for working with Chu San Zan Ji Ji data.
"""

import base64
import csv
import json
import os
import requests


def find_entry(file_path, title_zh):
    """
    Finds the Taisho file index and file path from the summaries file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionary entries each with a title, Taisho number,
              and file name.
    """
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvfile) # Skip header row
            i = 0
            matches = []
            for row in csvreader:
                if len(row) > 1:
                    i = i + 1
                    if row[1] == title_zh:
                        matches.append({
                            "title_zh": row[1],
                            "taisho_no": row[2],
                            "filepath": row[3],
                        })
            if not matches:
                print(f"{i} rows scanned but the entry {title_zh} was not found.")
            return matches
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
        raise
    return []


def index_cszjj_file(file_path):
    """
    Parses the CSZJJ CSV file and returns its content as a dictionnary of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionnary of dictionaries,indexed by Chinese title
    """
    catalog = {}
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvfile) # Skip header row
            i = 0
            for row in csvreader:
                if len(row) > 2:
                    title_zh = row[1]
                    entry = {
                        "id": row[0],
                        "title_zh": title_zh,
                        "fascicle": int(row[2]),
                        "taisho_title_zh": row[19],
                        "attribution_analysis": row[39],
                    }
                    catalog[title_zh] = entry
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
    return catalog


def parse_cszjj_file(file_path):
    """
    Parses the CSZJJ CSV file and returns its content as a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row.
    """
    data = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvfile) # Skip header row
            i = 0
            for row in csvreader:
                if len(row) > 2:
                    entry = {
                        "id": row[0],
                        "title_zh": row[1],
                        "fascicle": int(row[2]),
                        "taisho_title_zh": row[19],
                    }
                    data.append(entry)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
    return data


def parse_file_index(file_path, restart_at=None):
    """
    Parses the Taisho file index from the summaries file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary entry represents a Taisho
        text number and file name.
    """
    data = []
    restarted = False
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvfile) # Skip header row
            i = 0
            for row in csvreader:
                if restart_at and (restart_at == row[1]):
                    restarted = True
                if restart_at and (restart_at != row[1]) and not restarted:
                    continue
                if len(row) > 1:
                    entry = {
                        "title_zh": row[1],
                        "taisho_no": row[2],
                        "filepath": row[3],
                    }
                    data.append(entry)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
        raise
    return data

def parse_file_index(file_path, restart_at=None):
    """
    Parses the Taisho file index from the summaries file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary entry represents a Taisho
        text number and file name.
    """
    data = []
    restarted = False
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvfile) # Skip header row
            i = 0
            for row in csvreader:
                if restart_at and (restart_at == row[1]):
                    restarted = True
                if restart_at and (restart_at != row[1]) and not restarted:
                    continue
                if len(row) > 1:
                    entry = {
                        "title_zh": row[1],
                        "taisho_no": row[2],
                        "filepath": row[3],
                    }
                    data.append(entry)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise
    except Exception as e:
        print(f"An error occurred while parsing the CSV file: {e}")
        raise
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
    api_key = os.environ.get("GEMINI_API_KEY", "")

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
        return f"HTTP error occurred: {http_err} - Response: {response.text}, code: {response.status_code}"
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
