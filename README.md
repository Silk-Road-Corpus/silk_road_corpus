# silk_road_corpus
Corpus documents and data

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