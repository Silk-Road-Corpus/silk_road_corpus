"""This module searches the Kaiyuan Lu for alternative titles.
"""

import requests
import json
import os
import base64

prompt_template = """
Is the title {title} a synonym for any other tiles listed in the given text (Kaiyuan Lu)?
Return only the alternative titles in Chinese in the form ["Title 1", "Title 2", …].
Do not return any other output."
"""

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

if __name__ == "__main__":
    prompt = prompt_template.format(title="施色力經")
    file_path = "taisho/t2154.txt"
    print(f"\nSending prompt with text file: '{prompt}' and file '{file_path}' to Gemini ...")
    response_with_text_file = send_prompt(prompt, file_path=file_path)
    print("\n--- Gemini Model Response (With Text File) ---")
    print(response_with_text_file)
