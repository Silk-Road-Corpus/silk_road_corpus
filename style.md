# Translation Style Analysis

## Python Script

To run the style analysis:

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

```sql
-- Style - syllables per line
FROM cszjj.style
|> WHERE syllables_per_line != 0
|> AGGREGATE COUNT(*) AS Count GROUP BY syllables_per_line
|> ORDER BY Count DESC
```

```sql
-- Style - examples of four-syllables per line
FROM cszjj.style AS S
|> INNER JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.syllables_per_line = 5
|> SELECT S.czsjj_title_zh, S.taisho_no, C.attribution_analysis
```

```sql
-- Style - group by vernacular or literary
FROM cszjj.style
|> AGGREGATE COUNT(*) AS Count GROUP BY vernacular_or_literary
```

```sql
-- Style - vernacular enumerate
FROM cszjj.style AS S
|> INNER JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.vernacular_or_literary = 'vernacular'
|> SELECT S.czsjj_title_zh, S.taisho_no, C.attribution_analysis
```

```sql
-- Style - group by literal or fluent
FROM cszjj.style
|> AGGREGATE COUNT(*) AS Count GROUP BY literal_or_fluent
```

```sql
-- Style - fluent enumerate
FROM cszjj.style AS S
|> INNER JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.literal_or_fluent = 'fluent'
|> SELECT S.czsjj_title_zh, S.taisho_no, C.attribution_analysis, S.notes
```
