# Silk Road Corpus

This repository contains data for the Silk Road Corpus app and
Chu San Zang Ji Ji data.

## Loading the Chu San Zang Ji Ji Data.

Create a GCS bucket:

```shell
gcloud storage buckets --project=${PROJECT_ID} create gs://${CSZJJ_BUCKET_NAME} --location=US --public-access-prevention
```

Load the catalog file into the bucket:

```shell
gcloud storage cp data/chusanzangjiji.csv gs://${CSZJJ_BUCKET_NAME}/chusanzangjiji.csv
gcloud storage cp data/cszjj_sections.csv gs://${CSZJJ_BUCKET_NAME}/cszjj_sections.csv
```

Create a BiqQuery dataset:

```shell
bq --project_id=${PROJECT_ID} mk $DATASETID
```

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

How many anonymous texts?

```sql
FROM cszjj.chusanzangjiji
|> WHERE fascicle = 3 or fascicle = 4
|> AGGREGATE COUNT(*)
```

Count of catalog entries by CSZJJ section:

```sql
FROM cszjj.chusanzangjiji
|> AGGREGATE COUNT(*) GROUP BY fascicle, section
```

Count of catalog entries where Sengyou mentions that the text is an extract,
grouped by CSZJJ section:

```sql
FROM cszjj.chusanzangjiji
|> WHERE cszjj_production = "extract"
|> AGGREGATE COUNT(*) GROUP BY fascicle, section;
```

Sengyou mentions that the text is an extract and we have the text in a modern
canon.

```sql
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

## Updating the Flutter app

To update the Silk Road Corpus app after changing the bibliography:

1. Update the server by copying bibliography.csv and bib_parts.csv to silk_road_go/data.
2. Update the clients by copying bibliography.csv to silk_road_app/assets.
3. Update the authors dropdown in the client app.
4. Copy the new files to bib_file_parts
5. Upload the new PDF files to the GCS bucket.
6. Update the Agent Builder index.
