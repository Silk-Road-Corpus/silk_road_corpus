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

### Language Analysis

Language analysis is found in [Linguistic Analysis](linguistic_analysis.md).

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
-- Terminology usage lookup
FROM cszjj.terminology_usage
|> WHERE term = '佛'
```

```sql
-- Teminology evolution: number of terms used grouped by who used them and who introduced them
FROM cszjj.terminology_usage AS TU
|> INNER JOIN cszjj.terminology_analysis AS TA ON TU.term = TA.term
|> WHERE TU.document_frequency > 1 AND TA.valid_terminology AND TU.attribution IS NOT NULL
|> AGGREGATE COUNT(DISTINCT TU.term) AS num_terms GROUP BY TU.attribution, TU.term_introduced_by
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
FROM cszjj.terminology_usage AS TU
|> INNER JOIN cszjj.terminology_analysis AS TA ON TU.term = TA.term
|> WHERE TU.document_frequency > 1 AND TA.valid_terminology AND TU.attribution IS NOT NULL
|> SELECT DISTINCT TU.term, TU.term_introduced_by
|> AGGREGATE COUNT(*) GROUP BY term_introduced_by
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

```sql
-- Most widely used terms introduced by a particular translator
FROM cszjj.terminology_usage
|> WHERE term_introduced_by = 'Lokakṣema'
|> SELECT DISTINCT term, document_frequency
|> ORDER BY document_frequency DESC
```

### Terminology Validation

Load the CSV file into the GCS bucket:

```shell
gcloud storage cp data/terminology_validation.csv gs://${CSZJJ_BUCKET_NAME}/terminology_validation.csv
```

Load the terminology usage file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.terminology_validation \
    gs://${CSZJJ_BUCKET_NAME}/terminology_validation.csv \
    data/terminology_validation_schema.json
```

SQL queries:

```sql
-- Terminology validation sample size
FROM cszjj.terminology_validation
|> SELECT valid
|> AGGREGATE COUNT(*) GROUP BY valid
```

```sql
-- Terminology validation
FROM cszjj.terminology_validation
|> WHERE validated IS NOT NULL
|> SELECT valid
|> AGGREGATE COUNT(*) GROUP BY valid
```

```sql
-- Terminology validation by document frequency
FROM cszjj.terminology_validation
|> WHERE validated IS NOT NULL
|> SELECT valid, document_frequency
|> AGGREGATE COUNT(*) AS count GROUP BY valid, document_frequency
|> ORDER BY document_frequency DESC
```

```sql
-- Terminology false positive rate
SELECT * FROM
(SELECT document_frequency, valid FROM cszjj.terminology_validation WHERE validated IS NOT NULL)
PIVOT (
  COUNT(valid) AS count_valid
  FOR valid in (TRUE, FALSE)
)
|> EXTEND ROUND(count_valid_false / count_valid_true, 2) AS false_positive_rate
```

```sql
-- Terminology - use of transliteration
FROM cszjj.terminology_validation
|> WHERE valid = TRUE
|> SELECT term_introduced_by, semantic_or_transiteration
|> AGGREGATE COUNT(*) GROUP BY term_introduced_by, semantic_or_transiteration
|> ORDER BY term_introduced_by```

Run terminology analysis

```shell
python3 scripts/terminology_analysis.py
```

### Terminology Analysis

Load the CSV file into the GCS bucket:

```shell
gcloud storage cp data/terminology_analysis.csv gs://${CSZJJ_BUCKET_NAME}/terminology_analysis.csv
```

Load the terminology usage file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.terminology_analysis \
    gs://${CSZJJ_BUCKET_NAME}/terminology_analysis.csv \
    data/terminology_analysis_schema.json
```

SQL queries:

```sql
-- Valid and invalid terminology
FROM cszjj.terminology_analysis
|> AGGREGATE COUNT(*) GROUP BY valid_terminology
```

```sql
-- Correlation on terminology validation
FROM cszjj.terminology_analysis AS TA
|> INNER JOIN cszjj.terminology_validation AS TV ON TA.term = TV.term
|> AGGREGATE COUNT(*) GROUP BY TA.valid_terminology, TV.valid
```

```sql
-- Count of Distinct Terms by Translation Type
FROM cszjj.terminology_analysis
|> WHERE valid_terminology 
|> AGGREGATE COUNT(*) AS `Count of Distinct Terms` GROUP BY translation_type
|> ORDER BY `Count of Distinct Terms` DESC
```

```sql
-- Translation Analysis - types with percental
SELECT
  translation_type,
  `Count of Distinct Terms`,
  ROUND((`Count of Distinct Terms` * 100.0 / SUM(`Count of Distinct Terms`) OVER ()), 1) AS `Percentage of Total`
FROM
  (
    SELECT
      translation_type,
      COUNT(*) AS `Count of Distinct Terms`
    FROM
      cszjj.terminology_analysis
    WHERE
      valid_terminology = TRUE
    GROUP BY translation_type
  )
ORDER BY `Count of Distinct Terms` DESC;
```

```sql
-- Terminology Analysis - Semantic translations
FROM cszjj.terminology_usage AS TU
INNER JOIN cszjj.terminology_analysis AS TA ON TU.term = TA.term
|> WHERE TA.valid_terminology and TA.translation_type = 'Semantic'
|> SELECT DISTINCT TA.term, TA.english_equivalent, TA.term_introduced_by, TU.document_frequency
|> ORDER BY document_frequency DESC
```

```sql
-- Count of Distinct Terms by Translation Type, pivot by translator
SELECT * FROM
  (SELECT
    term,
    translation_type,
    term_introduced_by,
  FROM cszjj.terminology_analysis
  WHERE valid_terminology)
PIVOT (
  COUNT(DISTINCT term) AS count_terms
  FOR term_introduced_by IN ('An Shigao', 'Lokakṣema', 'Dharmarakṣa', 'Kumārajīva')
)
ORDER BY `count_terms_Kumārajīva` DESC
```

```sql
-- Most widely used terms introduced by a particular translator of a particular translation type
FROM cszjj.terminology_usage AS TU
JOIN cszjj.terminology_analysis as TA ON TU.term = TA.term
|> WHERE TU.term_introduced_by = 'Zhi Qian' AND TA.translation_type = 'Buddhist idiom'
|> SELECT DISTINCT TU.term, TU.document_frequency
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

To analyze the language of all the texts in the collection, for example,
for the presence of 如是我聞 and variants, first clone the NTI Reader
project and then set the NTI environment variable:

```shell
sudo apt-get install git
git clone https://github.com/alexamies/buddhist-dictionary.git
export NTI=$PWD/buddhist-dictionary/corpus/taisho
```

To run the terminology extraction from the corpus:

```shell
python3 scripts/terminology.py
```

For a single entry use the `--title` flag. The results are saved in the file
data/terminology.csv.

To run the script that compiles the terminology usage from the previous step and associates
each term used with the translator that introduced the term:

```shell
python3 scripts/terminology_usage.py
```

The output will be saved to data/terminology_usage.csv.

To run the script that analyzes the validity and type terminology:

```shell
python3 scripts/terminology_usage.py
```

The output will be saved to data/terminology_analysis.csv.

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