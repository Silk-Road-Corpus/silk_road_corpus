# Indic Catalog

The data is contained in the file [data/indic_catalog.csv](data/indic_catalog.csv), which 
was compiled manually. The citation table, which links the catalog entries to the
bibliographic database is provided in file [data/indic_citations.csv](data/indic_citations.csv).

Load the file into the GCS bucket:

```shell
gcloud storage cp data/indic_catalog.csv gs://${CSZJJ_BUCKET_NAME}/indic_catalog.csv
```

Load the content analysis into BigQuery:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.indic_catalog \
    gs://${CSZJJ_BUCKET_NAME}/indic_catalog.csv \
    data/indic_catalog_schema.json
```
 
## SQL Statements

```sql
-- Indic - All data
FROM cszjj.indic_catalog
```

```sql
-- Indic - Gāndhārī entries
FROM cszjj.indic_catalog
|> WHERE languages LIKE "%Gāndhārī%"
```

```sql
-- Indic - Khotanese entries
FROM cszjj.indic_catalog
|> WHERE languages LIKE "%Khotanese%"
```

```sql
-- CSZJJ - Indic manuscripts and languages
FROM cszjj.chusanzangjiji AS CZ
|> INNER JOIN cszjj.indic_catalog AS IC ON CZ.indic_manuscript = IC.corpus_item_id
|> WHERE indic_manuscript IS NOT NULL
   AND CZ.modern_ref IS NOT NULL
|> SELECT
  CZ.id,
  CZ.title_zh,
  CZ.title_en,
  CZ.modern_ref,
  CZ.modern_title,
  CZ.indic_manuscript,
  IC.title,
  IC.languages
```

```sql
-- CSZJJ - Gāndhārī manuscripts
FROM cszjj.chusanzangjiji AS CZ
|> INNER JOIN cszjj.indic_catalog AS IC ON CZ.indic_manuscript = IC.corpus_item_id
|> WHERE indic_manuscript IS NOT NULL
   AND IC.languages LIKE "%Gāndhārī%"
   AND CZ.modern_ref IS NOT NULL
|> SELECT
  CZ.id,
  CZ.title_zh,
  CZ.title_en,
  CZ.modern_ref,
  CZ.modern_title,
  CZ.indic_manuscript,
  IC.title,
  IC.languages
  ```
  