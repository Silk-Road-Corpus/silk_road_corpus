# Silk Road Corpus

This repository contains data for the Silk Road Corpus app and
Chu San Zang Ji Ji data.

## Exploratory Data Analysis

To explore the data in this repository, you can use the included Colab notebook:

[![Explore the Chu San Zang Ji Ji](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Silk-Road-Corpus/silk_road_corpus/blob/main/cszjj.ipynb)

or this one on anonymous records in the Chu San Zang Ji Ji:

[![Anonymous Records in the Chu San Zang Ji Ji](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Silk-Road-Corpus/silk_road_corpus/blob/main/eda.ipynb)

## Basic Setup

Clone this repo:

```shell
sudo apt-get install git
git clone https://github.com/Silk-Road-Corpus/silk_road_corpus.git
```

Install [gcloud](https://docs.cloud.google.com/sdk/docs/install#linux).

Change to the project directory:

```shell
cd silk_road_corpus
```

## Loading the Chu San Zang Ji Ji Data into BigQuery

### Import Data

Create a GCS bucket:

```shell
gcloud storage buckets --project=${PROJECT_ID} create gs://${CSZJJ_BUCKET_NAME} --location=US --public-access-prevention
```

Load the CSV files into the bucket:

```shell
gcloud storage cp data/chusanzangjiji.csv gs://${CSZJJ_BUCKET_NAME}/chusanzangjiji.csv
gcloud storage cp data/cszjj_sections.csv gs://${CSZJJ_BUCKET_NAME}/cszjj_sections.csv
```

Create a BiqQuery dataset:

```shell
bq --project_id=${PROJECT_ID} mk $DATASETID
```

### Catalog

Load the catalog into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.chusanzangjiji \
    gs://${CSZJJ_BUCKET_NAME}/chusanzangjiji.csv \
    data/chusanzangjiji_schema.json
```

## Query the Chu San Zang Ji Ji Catalog

SQL queries use
[Pipe syntax](https://cloud.google.com/bigquery/docs/pipe-syntax-guide).

```sql
-- How many titles are there in the CXZJJ?
FROM cszjj.chusanzangjiji
|> AGGREGATE COUNT(*) AS `Number of Titles in the CSZJJ`
```

```sql
-- How many titles in the CXZJJ can be related to currently existing texts?
FROM cszjj.chusanzangjiji
|> WHERE modern_ref IS NOT NULL
|> AGGREGATE COUNT(*) AS `Number of Related Existing Texts`
```

```sql
-- How many titles in the CXZJJ can be related to Taisho texts? Also, sum of fascicles.
SELECT
  COUNT(*) AS count_titles,
  SUM(taisho_num_fascicles) AS taisho_fascicles,
FROM cszjj.chusanzangjiji
WHERE REGEXP_CONTAINS(modern_ref, r'T \d+')
```

```sql
-- Count of entries and fascicles that can be related to a text in the modern canon, break down by attribution_analysis
SELECT
  attribution_analysis,
  COUNT(*) AS count_titles,
  SUM(taisho_num_fascicles) AS taisho_fascicles
FROM cszjj.chusanzangjiji
WHERE modern_ref IS NOT NULL
GROUP BY attribution_analysis
|> WHERE count_titles >= 5
```

```sql
-- Count of entries and fascicles that can be related to a text in the modern canon break, down by cszjj_attribution
SELECT
  cszjj_attribution,
  COUNT(*) AS count_titles,
  COUNT(*) AS count_lost,
  SUM(taisho_num_fascicles) AS taisho_fascicles
FROM cszjj.chusanzangjiji
WHERE modern_ref IS NOT NULL
GROUP BY cszjj_attribution
|> WHERE count_titles >= 5
```

```sql
-- Count of entries and fascicles, down by cszjj_attribution
SELECT
  cszjj_attribution,
  COUNT(*) AS count_titles,
  SUM(num_fascicles) AS total_fascicles
FROM cszjj.chusanzangjiji
GROUP BY cszjj_attribution
|> WHERE count_titles >= 5
```

```sql
-- What at the centuries were the texts produced in?
FROM cszjj.chusanzangjiji
|> WHERE century IS NOT NULL
|> SELECT
     id,
     title_zh,
     modern_ref,
     attribution_analysis,
     century
|> ORDER BY century
```

```sql
-- Histogram of the centuries were the texts produced in
FROM cszjj.chusanzangjiji
|> WHERE century IS NOT NULL
|> AGGREGATE COUNT(*) as count_century GROUP BY century
|> ORDER BY century
```

```sql
-- Summary of CSZJJ titles with key variables
FROM cszjj.chusanzangjiji
|> WHERE modern_ref IS NOT NULL
   AND (STARTS_WITH(modern_ref, "T ") OR STARTS_WITH(modern_ref, "X "))
|> SELECT
  id,
  title_zh,
  title_en,
  modern_ref,
  attribution_analysis,
  COALESCE(indic_manuscript,pali_parallel) AS indic_parallel,
  source_type
```

```sql
-- How many anonymous texts?
FROM cszjj.chusanzangjiji
|> WHERE fascicle = 3 or fascicle = 4
|> AGGREGATE COUNT(*)
```

```sql
-- Count of catalog entries by CSZJJ section
FROM cszjj.chusanzangjiji
|> AGGREGATE COUNT(*) GROUP BY fascicle, section
```

```sql
-- Lost texts by section
FROM cszjj.chusanzangjiji
|> WHERE cszjj_not_seen IS NOT NULL
|> AGGREGATE COUNT(*) GROUP BY fascicle, section;
```

```sql
-- Count of catalog entries where Sengyou mentions that the text is an extract, grouped by CSZJJ section
FROM cszjj.chusanzangjiji
|> WHERE cszjj_production = "extract"
|> AGGREGATE COUNT(*) GROUP BY fascicle, section;
```

```sql
-- Sengyou mentions that the text is an extract and we have the text in a modern canon.
FROM cszjj.chusanzangjiji
|> WHERE cszjj_production = "extract" AND modern_ref IS NOT NULL
|> SELECT modern_ref, modern_title
```


```sql
-- How many anoymous entries can be related to a text in the modern canon?
FROM cszjj.chusanzangjiji
|> WHERE modern_ref IS NOT NULL
   AND (fascicle = 3 OR fascicle = 4)
|> SELECT id, title_zh, modern_ref, modern_title
|> AGGREGATE COUNT(*)
```


```sql
-- How many Taisho titles are exactly the same as the titles in CSZJJ?
FROM cszjj.chusanzangjiji
|> WHERE modern_title = title_zh
   AND (fascicle = 3 OR fascicle = 4)
|> SELECT modern_ref, modern_title
|> AGGREGATE COUNT(*)
```

```sql
-- How many Taisho titles have 佛說 prepended compared with CSZJJ?
FROM cszjj.chusanzangjiji
|> WHERE STARTS_WITH(modern_title, "佛說") AND NOT STARTS_WITH(title_zh, "佛說")
   AND (fascicle = 3 OR fascicle = 4)
|> SELECT id, title_zh, modern_ref, modern_title
|> AGGREGATE COUNT(*)
```

```sql
-- Total anonymous texts, grouped by number of fascicles
FROM cszjj.chusanzangjiji
|> WHERE fascicle = 3 or fascicle = 4
|> AGGREGATE COUNT(*) num_texts GROUP BY num_fascicles
|> ORDER BY num_fascicles DESC
```

```sql
-- Total anonymous texts, grouped by genre
FROM cszjj.chusanzangjiji
|> WHERE (fascicle = 3 OR fascicle = 4)
   AND taisho_classification IS NOT NULL
|> AGGREGATE COUNT(*) AS `Number of Texts` GROUP BY taisho_classification AS `Taisho Classification`
|> ORDER BY `Number of Texts` DESC
|> WHERE `Number of Texts` > 5```

```sql
-- How many anonymous entries can be related to a text in a larger collection?
FROM cszjj.chusanzangjiji
|> WHERE (fascicle = 3 OR fascicle = 4)
   AND modern_ref LIKE '%)'
|> SELECT id, title_zh, modern_ref, modern_title
|> AGGREGATE COUNT(*)
```

```sql
-- How many anonymous entries can be related to a text in a larger collection (for visualization)?
FROM cszjj.chusanzangjiji
|> WHERE (fascicle = 3 OR fascicle = 4)
   AND modern_ref LIKE '%)'
|> EXTEND SUBSTR(modern_ref, 1, INSTR(modern_ref, '(') - 1) AS collection_ref
|> SELECT id, title_zh, modern_ref, collection_ref AS `Taisho No`
|> AGGREGATE COUNT(*) AS `Number in Collection` GROUP BY `Taisho No`
|> WHERE `Number in Collection` > 1
|> ORDER BY `Number in Collection` DESC
```

```sql
-- How many anoymous entries are Chinese native compositions?
FROM cszjj.chusanzangjiji
|> WHERE secondary_lit_classification IS NOT NULL
   AND (fascicle = 3 OR fascicle = 4)
|> SELECT id, title_zh, modern_ref, modern_title, secondary_lit_classification
```

### Terminology Usage ad Analysis

Terminology usage and analysis is found in [Terminology](terminology.md).

### Linguistic Analysis

Linguistic analysis is found in [Linguistic Analysis](linguistic_analysis.md).

### Style Analysis

Translation style analysis is found in [Style Analysis](style.md).

## Running the Python Scripts

Setup a virtual env:

```shell
python3 -m venv venv
```

Activate it

```shell
source venv/bin/activate
```

Install dependencies

```shell
pip install -r requirements.txt
```

To deactivate the virtual env:

```shell
deactivate
```

Enable the Gemini API in the Google Cloud Console. Generate an API in the
Console and set it as an environment variable:

```shell
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

Put the GCP project ID in the environment:

```shell
GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID_HERE"
```

the alternative titles iterates over all the anonymous texts to find
alternative titles and attempt to match them to Taisho entries.
To run script:

```shell
python3 scripts/alt_titles.py
```

This script takes a long time to run. Edit the variable `restart_at` to
restart the program if it is interupted.

The NTI project has the corpus texts. Clone the repo and set an NTI
environment variable:

```shell
git clone https://github.com/alexamies/buddhist-dictionary.git
export NTI=$PWD/buddhist-dictionary/corpus/taisho
```

For all Python scripts a single entry use the `--title` flag.

To compute word embedding examples, in the virtual env install the Vertex client API:

```shell
pip install --upgrade google-genai
```

Authenticate with 

```shell
gcloud auth application-default login
```
Run the code:

```shell
python3 scripts/embedding.py
```

## Updating the Flutter app

To update the Silk Road Corpus app after changing the bibliography:

1. Update the server by copying bibliography.csv and bib_parts.csv to silk_road_go/data.
2. Update the clients by copying bibliography.csv to silk_road_app/assets.
3. Update the authors dropdown in the client app.
4. Copy the new files to bib_file_parts
5. Upload the new PDF files to the GCS bucket.
6. Update the Agent Builder index.

## Drawings

### Graphviz
Network diagrams use [Graphviz](https://graphviz.org/). Images can be generated
from DOT files with the [DOT CLI](https://graphviz.org/doc/info/command.html).
For example,

```shell
dot -Tpng drawings/terminology_processing.dot > images/terminology_processing.png
```

and 

```shell
dot -Tpng drawings/big_picture.dot > images/big_picture.png
```

### Vega Diagrams

Histograms and related charts use [Vega](https://vega.github.io/vega/).
JSON Vega files can be used to generate images using the Vega VSC plugin.