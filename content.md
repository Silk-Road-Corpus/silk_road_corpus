# Content Analysis

## Python Script

To run the terminology extraction from the corpus:

```shell
nohup python3 scripts/content.py  2>&1 &
```

The results are saved in the file `data/content.csv`.

Load the file into the GCS bucket:

```shell
gcloud storage cp data/content.csv gs://${CSZJJ_BUCKET_NAME}/content.csv
```

Load the content analysis into BigQuery:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.content \
    gs://${CSZJJ_BUCKET_NAME}/content.csv \
    data/content_schema.json
```

SQL Statements

```sql
-- Content - Invalid records
FROM cszjj.content
|> WHERE top_level_genre NOT IN ('sutra', 'commentary', 'vinaya', 'jataka', 'history')
|> SELECT czsjj_title_zh, taisho_no, top_level_genre
```