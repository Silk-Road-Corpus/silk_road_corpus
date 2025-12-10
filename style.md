# Translation Style Analysis

## Python Scripts

To run the terminology extraction from the corpus:

```shell
nohup python3 scripts/style.py  2>&1 &
```

The results are saved in the file `data/style.csv`.

Copy the style CSV file into the GCS bucket:

```shell
gcloud storage cp data/style.csv gs://${CSZJJ_BUCKET_NAME}/style.csv
```

Load the style file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.style \
    gs://${CSZJJ_BUCKET_NAME}/style.csv \
    data/style_schema.json
```

## SQL Queries

```sql
-- Style - verse or prose?
FROM cszjj.style
|> AGGREGATE COUNT(*) AS Count GROUP BY verse_or_prose
```