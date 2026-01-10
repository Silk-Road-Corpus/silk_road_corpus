# Content Analysis

## Python Script

To run the content analysis script with an all-in-one prompt:

```shell
nohup python3 scripts/content.py  2>&1 &
```

The results are saved in the file `data/content.csv`.

However, the results of this prompt were not very good. 

To run the content analysis script with multiple prompts, one for
each parameter in the rubric, run:

```shell
nohup python3 scripts/content_new_prompt.py  2>&1 &
```

The results are saved in the file `data/content_new.csv`.

Load the file into the GCS bucket:

```shell
gcloud storage cp data/content_new.csv gs://${CSZJJ_BUCKET_NAME}/content.csv
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
-- Content - Correct prediction of top level genre
FROM cszjj.content AS CO
|> INNER JOIN cszjj.chusanzangjiji AS CZ ON CO.czsjj_title_zh = CZ.title_zh
|> WHERE CO.top_level_genre = CZ.top_level_genre
|> AGGREGATE COUNT (CO.taisho_no) AS count_correct
```

```sql
-- Content - Incorrect prediction of top level genre
FROM cszjj.content AS CO
|> INNER JOIN cszjj.chusanzangjiji AS CZ ON CO.czsjj_title_zh = CZ.title_zh
|> WHERE CO.top_level_genre != CZ.top_level_genre
|> AGGREGATE COUNT (CO.taisho_no) AS count_incorrect
```