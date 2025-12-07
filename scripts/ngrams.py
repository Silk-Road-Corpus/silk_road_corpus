"""This script extracts n-gram counts from the corpus.
"""

import argparse
from collections import Counter
import cszjj
import os
import re
import sys


file_index_path = "data/canonical_summaries.csv"
output_filename = "data/ngram_counts.csv"


def extract_ngrams(text: str) -> Counter:
    """Computes all the n-gram counts in the text string for n=1, 2, 3, 4, 5.

    The text string consists of Chinese characters. Each character is a token
    in an n-gram. Chinese punctuation is stripped from the string before
    processing.

    Args:
        text (str): The input string of Chinese characters.

    Returns:
        Counter: A Counter object with n-grams as keys and their counts as values.
    """
    # Remove Chinese punctuation, whitespace, boilerplate, and non-Chinese characters
    punctuation = "[\u3000-\u303f\uff00-\uffef]"
    cleaned_text = re.sub(punctuation, "", text)
    cleaned_text = re.sub(r"[a-zA-Z0-9]", "", cleaned_text)
    cleaned_text = re.sub(r"[\(\):;\.\[\]\/\*\s]", "", cleaned_text)
    cleaned_text = cszjj.strip_boiler_plate(cleaned_text)

    # Generate n-grams for n=1, 2, and 3
    ngrams = [cleaned_text[i:i+n] for n in range(1, 11) for i in range(len(cleaned_text) - n + 1)]
    return Counter(ngrams)


def ngrams(nti, entry):
    """Extracts the ngram counts from a file.

    Returns:
        dictionary: a dictionary with the ngram counts
    """
    if "title_zh" not in entry:
        raise Exception(f"title_zh not in entry {entry}")

    title_zh = entry["title_zh"]
    taisho_no = entry.get("taisho_no")

    result = {
        "title_zh": title_zh,
        "taisho_no": taisho_no,
        "ngram_counts": {},
    }

    if "filepath" not in entry:
        raise Exception("filepath not given")
    fname = entry["filepath"]
    filepath = fname
    if fname.startswith("$nti"):
        filepath = nti + fname[4:]
    with open(filepath, 'r') as f:
        text = f.read()
        ngram_counts = extract_ngrams(text)
        result["ngram_counts"] = ngram_counts
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
    row = [title_zh, entry["taisho_no"]]
    ngram_counts = entry["ngram_counts"]
    for ngram, count in ngram_counts.items():
        row = [title_zh, entry["taisho_no"], ngram, count]
        cszjj.append_to_csv(filename, [row])
    row.append(str(dict(ngram_counts)))
    print(f"Result appended for {title_zh}")


if __name__ == "__main__":
    nti = os.environ.get("NTI", "")
    if len(nti) == 0:
        sys.exit("NTI not in environment.") 

    # Process command line arguments
    parser = argparse.ArgumentParser(
        description="Extracts Buddhist n-gram counts from the corpus"
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
            result = ngrams(nti, entry)
            append_result(output_filename, result)
        sys.exit()

    if not args.restart_at:
        headers = ["cjzjj_title",
                   "taisho_no",
                   "ngram",
                   "count"]
        print(f"Starting at the beginning\n")
        cszjj.write_headers_to_csv(output_filename, headers)
    else:
        print(f"Starting at {args.restart_at}\n")
    entries = cszjj.parse_file_index(file_index_path, args.restart_at)
    num = len(entries)
    for entry in entries:
        result = ngrams(nti, entry)
        append_result(output_filename, result)
    print(f"Results written to {output_filename}")
