# silk_road_corpus
Corpus documents and data

# Update the index

1. Update the server by copying bibliography.csv and bib_parts.csv to silk_road_go/data.
2. Update the clients by copying bibliography.csv to silk_road_app/assets.
3. Update the authors dropdown in the client app.
4. Copy the new files to bib_file_parts
5. Upload the new PDF files to the GCS bucket.
6. Update the Agent Builder index.

## OCR with Google Vision API

### Setup

Create a virtual env

```shell
python3 -m venv env
```

Activate it

```shell
source env/bin/activate
```

Deactivate it

```shell
deactivate
```

Install the Google Vision API and Cloud Storage client libraries

```shell
pip install --upgrade google-cloud-vision
pip install --upgrade google-cloud-storage
```

Run the OCR program

```shell
python3 python/ocr.py
```

Assemble the output from the OCR program

```shell
python3 python/extract_from_json.py
```