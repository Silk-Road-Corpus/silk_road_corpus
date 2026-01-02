# Content Analysis

## Python Script

To run the content analysis script with an all-in-one prompt:

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


To run the content analysis script with multiple prompts, one for
each parameter:

```shell
nohup python3 scripts/content_new_prompt.py  2>&1 &
```

The results are saved in the file `data/content_new.csv`.

Load the file into the GCS bucket:

```shell
gcloud storage cp data/content_new.csv gs://${CSZJJ_BUCKET_NAME}/content_new.csv
```

Load the content analysis into BigQuery:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.content_new \
    gs://${CSZJJ_BUCKET_NAME}/content_new.csv \
    data/content_schema.json
```
 

SQL Statements

```sql
-- Content - Invalid records
FROM cszjj.content
|> WHERE top_level_genre NOT IN ('sutra', 'commentary', 'vinaya', 'jataka', 'history')
|> SELECT czsjj_title_zh, taisho_no, top_level_genre
```