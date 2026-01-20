# Bibliographic Database

The main file for the bibliographic database is
[data/bibliography.csv](data/bibliography.csv). It was compiled manually and
exported from a Google Sheet. It can also be loaded into the BigQuery 
dataset and joined with other tables.

The file [data/cszjj_citations.csv](data/cszjj_citations.csv) joins the 
Chu San Zang Ji Ji catalog with the bibliographic database. It was compiled
manually and exported from a Google Sheet.

## Setup

Load the bibliography file into the GCS bucket:

```shell
gcloud storage cp data/bibliography.csv gs://${CSZJJ_BUCKET_NAME}/bibliography.csv
```

Load the bibliography file into BigQuery:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.bibliography \
    gs://${CSZJJ_BUCKET_NAME}/bibliography.csv \
    data/bibliography_schema.json
```

Load the cszjj_citations file into the GCS bucket:

```shell
gcloud storage cp data/cszjj_citations.csv gs://${CSZJJ_BUCKET_NAME}/cszjj_citations.csv
```

Load the cszjj_citations file into BigQuery:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.cszjj_citations \
    gs://${CSZJJ_BUCKET_NAME}/cszjj_citations.csv \
    data/cszjj_citations_schema.json
```

## SQL queries

```sql
-- Corpus - Fascicles
FROM cszjj.canonical_summaries
|> AGGREGATE COUNT(*)
```

```sql
-- How many anoymous entries are Chinese native compositions? Join with citations table.
FROM `cszjj.cszjj_citations`
|> SELECT cszjj_title_zh, bib_id
|> AGGREGATE STRING_AGG(bib_id, ', ') AS bib_ids
   GROUP BY cszjj_title_zh
|> AS CI
|> RIGHT JOIN cszjj.chusanzangjiji AS CZ ON CZ.title_zh = CI.cszjj_title_zh
|> WHERE CZ.secondary_lit_classification IS NOT NULL
   AND CZ.modern_ref IS NOT NULL
|> SELECT
  CZ.title_en,
  CZ.modern_title,
  CZ.modern_ref,
  '(',
  CI.bib_ids,
  ')'
```