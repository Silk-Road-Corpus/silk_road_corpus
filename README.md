# Silk Road Corpus

This repository contains data for the Silk Road Corpus app and
Chu San Zang Ji Ji data.

## Exploratory Data Analysis

To explore the data in this repository, you can use the included Colab notebook:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Silk-Road-Corpus/silk_road_corpus/blob/main/eda.ipynb)

## Loading the Chu San Zang Ji Ji Data into BigQuery

### Project setup

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

### Language Analysis

Load the CSV file into the bucket:

```shell
gcloud storage cp data/language_analysis.csv gs://${CSZJJ_BUCKET_NAME}/language_analysis.csv
```

Load the language analysis file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.language_analysis \
    gs://${CSZJJ_BUCKET_NAME}/language_analysis.csv \
    data/language_analysis_schema.json
```

SQL queries:

```sql
-- Number of texts analyzed
FROM cszjj.language_analysis
|> AGGREGATE COUNT(*)
```

```sql
-- Number of anonymous texts analyzed
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE C.fascicle = 3 OR C.fascicle = 4
|> AGGREGATE COUNT(*)
```

```sql
-- Median length in characters of anonymous texts
FROM cszjj.chusanzangjiji AS C
|> INNER JOIN cszjj.language_analysis AS LA
  ON C.title_zh = LA.czsjj_title_zh
|> WHERE C.fascicle = 3 OR C.fascicle = 4
|> SELECT PERCENTILE_CONT(LA.length, 0.5) OVER () AS media_length
|> LIMIT 1
```

```sql
-- Number of anonymous texts analyzed by ru shi wo wen
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE (C.fascicle = 3 OR C.fascicle = 4)
|> AGGREGATE COUNT(*) AS num_texts GROUP BY LA.rushiwowen, LA.wenrushi
```

```sql
-- List of anonymous texts analyzed by ru shi wo wen
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE (C.fascicle = 3 OR C.fascicle = 4)
|> SELECT LA.taisho_no, LA.rushiwowen, LA.wenrushi
```

```sql
-- Counts of anonymous texts with We Ru Shi by section
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE (C.fascicle = 3 OR C.fascicle = 4)
   AND LA.wenrushi
|> SELECT C.title_zh, LA.taisho_no, C.modern_title, C.fascicle, C.section
|> AGGREGATE COUNT(*) num_texts GROUP BY fascicle, section
|> ORDER BY fascicle, section
```

```sql
-- Number of anonymous texts with Wen Ru Shi and no final particles
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE (C.fascicle = 3 OR C.fascicle = 4)
   AND LA.wenrushi
   and not_in_shanzai = 0
   AND ye2_final_count = 0
   AND er3_final_count = 0
   AND ye3_final_count = 0
|> AGGREGATE COUNT(*) AS num_texts
```

```sql
-- Terminology usage lookup
FROM cszjj.terminology_usage
|> WHERE term = '佛'
```

### Terminology Usage

Load the CSV file into the GCS bucket:

```shell
gcloud storage cp data/terminology_usage.csv gs://${CSZJJ_BUCKET_NAME}/terminology_usage.csv
```

Load the terminology usage file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.terminology_usage \
    gs://${CSZJJ_BUCKET_NAME}/terminology_usage.csv \
    data/terminology_usage_schema.json
```

SQL queries:

```sql
-- Number of terms used grouped by who used them and who introduced them
FROM cszjj.terminology_usage
|> WHERE document_frequency > 1
|> AGGREGATE COUNT(DISTINCT term) num_terms GROUP BY attribution, term_introduced_by```
```

```sql
-- Count of distinct terms that occur in at least two documents
FROM cszjj.terminology_usage
|> WHERE document_frequency > 1
|> SELECT DISTINCT term
|> AGGREGATE COUNT(*)
```

```sql
-- Distinct terms and who introduced them
FROM cszjj.terminology_usage
|> WHERE document_frequency > 1
|> SELECT DISTINCT term, term_introduced_by, document_frequency
|> ORDER BY term_introduced_by
```

```sql
-- Count of distinct terms, grouped by translator
FROM cszjj.terminology_usage
|> WHERE document_frequency > 1
|> SELECT DISTINCT term, term_introduced_by
|> AGGREGATE COUNT(*) GROUP BY term_introduced_by
|> ORDER BY term_introduced_by
```

```sql
-- Terminology usage lookup
FROM cszjj.terminology_usage
|> WHERE term = '教病'
```

```sql
-- Most widely used terms
FROM cszjj.terminology_usage
|> SELECT DISTINCT term, term_introduced_by, document_frequency
|> ORDER BY document_frequency DESC
```

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
pip install requests
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

the alternative titles iterates over all the anonymous texts to find
alternative titles and attempt to match them to Taisho entries.
To run script:

```shell
python3 scripts/alt_titles.py
```

This script takes a long time to run. Edit the variable `restart_at` to
restart the program if it is interupted.

To analyze the language of all the texts in the collection, for example,
for the presence of 如是我聞 and variants, first clone the NTI Reader
project and then set the NTI environment variable:

```shell
cd ..
git clone https://github.com/alexamies/buddhist-dictionary.git
export NTI=$PWD/buddhist-dictionary/corpus/taisho
cd silk_road_corpus
python3 scripts/language_analysis.py
```

The results will be written to data/lanaguage_analysis.csv. This can also take a long
time to run. If you need to restart it use the `--restart` flag. If you need to run
it for a single entry use the `--title` flag.

To run the terminology analysis:

```shell
python3 scripts/terminology.py
```

For a single entry use the `--title` flag.

To run the script that extracts the terminology and associates each term used with the
translator that introduced the term:

```shell
python3 scripts/terminology_usage.py
```

## Updating the Flutter app

To update the Silk Road Corpus app after changing the bibliography:

1. Update the server by copying bibliography.csv and bib_parts.csv to silk_road_go/data.
2. Update the clients by copying bibliography.csv to silk_road_app/assets.
3. Update the authors dropdown in the client app.
4. Copy the new files to bib_file_parts
5. Upload the new PDF files to the GCS bucket.
6. Update the Agent Builder index.
