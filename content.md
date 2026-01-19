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
 
## SQL Statements

```sql
-- Content - Total records
FROM cszjj.content AS CO
|> AGGREGATE COUNT (CO.taisho_no) AS count_total
```

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

```sql
-- Content - Correct prediction of Taisho genre
FROM cszjj.content AS CO
|> INNER JOIN cszjj.chusanzangjiji AS CZ ON CO.czsjj_title_zh = CZ.title_zh
|> WHERE CO.taisho_genre = CZ.taisho_classification
|> AGGREGATE COUNT (CO.taisho_no) AS count_correct
```

```sql
-- Content - Incorrect prediction of Taisho genre
FROM cszjj.content AS CO
|> INNER JOIN cszjj.chusanzangjiji AS CZ ON CO.czsjj_title_zh = CZ.title_zh
|> WHERE CO.taisho_genre != CZ.taisho_classification
|> AGGREGATE COUNT (CO.taisho_no) AS count_correct
```

```sql
-- Content - Number of errors
FROM cszjj.content
|> WHERE error IS NOT NULL
|> AGGREGATE COUNT (czsjj_title_zh) AS count_total
```

```sql
-- Content - Topic analysis of sutras
FROM cszjj.content
|> WHERE top_level_genre = 'sutra'
|> EXTEND CASE parable_or_miracle_tale
  WHEN 'parable' THEN 'parable'
  WHEN 'miracle_tale' THEN 'miracle_tale'
  WHEN 'biographies' THEN 'biographies'
  ELSE 'other'
  END AS topic
|> AGGREGATE COUNT (czsjj_title_zh) AS count_topic GROUP BY topic
```

```sql
-- Content - Topic analysis other
FROM cszjj.content
|> EXTEND CASE parable_or_miracle_tale
  WHEN 'parable' THEN 'parable'
  WHEN 'miracle_tale' THEN 'miracle_tale'
  WHEN 'biographies' THEN 'biographies'
  ELSE 'other'
  END AS topic
|> WHERE top_level_genre = 'sutra' AND topic = 'other'
```

```sql
-- Content - Topic analysis of commentaries
FROM cszjj.content
|> WHERE top_level_genre = 'commentary'
|> AGGREGATE COUNT (czsjj_title_zh) AS count_commentary_type GROUP BY commentary_type
```

```sql
-- Content - Topic analysis other that contains philosophical argumentation
FROM cszjj.content
|> EXTEND CASE parable_or_miracle_tale
  WHEN 'parable' THEN 'parable'
  WHEN 'miracle_tale' THEN 'miracle_tale'
  WHEN 'biographies' THEN 'biographies'
  ELSE 'other'
  END AS topic
|> WHERE top_level_genre = 'sutra' AND topic = 'other'
|> AGGREGATE COUNT (czsjj_title_zh) AS count_phil_arg GROUP BY philosophical_argumentation
```

```sql
-- Content - Rhetoric
FROM cszjj.content
|> AGGREGATE COUNT (czsjj_title_zh) AS count_rhetoric GROUP BY contains_rhetoric 
```

```sql
-- Content - Rhetoric Examples
FROM cszjj.content
|> WHERE contains_rhetoric
|> LIMIT 200
```
