# Corpus of Related Chinese Texts

The files for the corpus are defined by the
[data/canonical_summaries.csv](data/canonical_summaries.csv) file.

gcloud storage cp data/canonical_summaries.csv gs://${CSZJJ_BUCKET_NAME}/canonical_summaries.csv

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.canonical_summaries \
    gs://${CSZJJ_BUCKET_NAME}/canonical_summaries.csv \
    data/canonical_summaries_schema.json
```

SQL queries

```sql
-- Corpus - Fascicles
FROM cszjj.canonical_summaries
|> AGGREGATE COUNT(*)
```

```sql
-- Corpus - Entries
FROM cszjj.canonical_summaries
|> EXTEND REGEXP_REPLACE(taisho_no, r'\s\(\d+\)', '') AS canonical_ref
|> SELECT DISTINCT title_zh, canonical_ref
```
