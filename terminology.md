# Terminology Usage ad Analysis

## Loading data

Load the CSV file into the GCS bucket:

```shell
gcloud storage cp data/terminology_usage.csv gs://${CSZJJ_BUCKET_NAME}/terminology_usage.csv
```

Load the terminology usage file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.terminology_usage \
    gs://${CSZJJ_BUCKET_NAME}/terminology_usage.csv \
    data/terminology_usage_schema.json
```

SQL queries:

```sql
-- Terminology usage lookup
FROM cszjj.terminology_usage
|> WHERE term = '佛'
```

```sql
-- Teminology evolution: number of terms used grouped by who used them and who introduced them
FROM cszjj.terminology_usage AS TU
|> INNER JOIN cszjj.terminology_analysis AS TA ON TU.term = TA.term
|> WHERE TU.document_frequency > 1 AND TA.valid_terminology AND TU.attribution IS NOT NULL
|> AGGREGATE COUNT(DISTINCT TU.term) AS num_terms GROUP BY TU.attribution, TU.term_introduced_by
```

```sql
-- Count of distinct terms that occur in at least two documents
FROM cszjj.terminology_usage
|> WHERE document_frequency > 1
|> SELECT DISTINCT term
|> AGGREGATE COUNT(*)
```

```sql
-- Distinct terms and who introduced them
FROM cszjj.terminology_usage
|> WHERE document_frequency > 1
|> SELECT DISTINCT term, term_introduced_by, document_frequency
|> ORDER BY term_introduced_by
```

```sql
-- Count of distinct terms, grouped by translator
FROM cszjj.terminology_usage AS TU
|> INNER JOIN cszjj.terminology_analysis AS TA ON TU.term = TA.term
|> WHERE TU.document_frequency > 1 AND TA.valid_terminology AND TU.attribution IS NOT NULL
|> SELECT DISTINCT TU.term, TU.term_introduced_by
|> AGGREGATE COUNT(*) GROUP BY term_introduced_by
```

```sql
-- Terminology usage lookup
FROM cszjj.terminology_usage
|> WHERE term = '教病'
```

```sql
-- Most widely used terms
FROM cszjj.terminology_usage
|> SELECT DISTINCT term, term_introduced_by, document_frequency
|> ORDER BY document_frequency DESC
```

```sql
-- Most widely used terms introduced by a particular translator
FROM cszjj.terminology_usage
|> WHERE term_introduced_by = 'Lokakṣema'
|> SELECT DISTINCT term, document_frequency
|> ORDER BY document_frequency DESC
```

## Terminology Validation

Load the CSV file into the GCS bucket:

```shell
gcloud storage cp data/terminology_validation.csv gs://${CSZJJ_BUCKET_NAME}/terminology_validation.csv
```

Load the terminology usage file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.terminology_validation \
    gs://${CSZJJ_BUCKET_NAME}/terminology_validation.csv \
    data/terminology_validation_schema.json
```

SQL queries:

```sql
-- Terminology validation sample size
FROM cszjj.terminology_validation
|> SELECT valid
|> AGGREGATE COUNT(*) GROUP BY valid
```

```sql
-- Terminology validation
FROM cszjj.terminology_validation
|> WHERE validated IS NOT NULL
|> SELECT valid
|> AGGREGATE COUNT(*) GROUP BY valid
```

```sql
-- Terminology validation by document frequency
FROM cszjj.terminology_validation
|> WHERE validated IS NOT NULL
|> SELECT valid, document_frequency
|> AGGREGATE COUNT(*) AS count GROUP BY valid, document_frequency
|> ORDER BY document_frequency DESC
```

```sql
-- Terminology false positive rate
SELECT * FROM
(SELECT document_frequency, valid FROM cszjj.terminology_validation WHERE validated IS NOT NULL)
PIVOT (
  COUNT(valid) AS count_valid
  FOR valid in (TRUE, FALSE)
)
|> EXTEND ROUND(count_valid_false / count_valid_true, 2) AS false_positive_rate
```

```sql
-- Terminology - use of transliteration
FROM cszjj.terminology_validation
|> WHERE valid = TRUE
|> SELECT term_introduced_by, semantic_or_transiteration
|> AGGREGATE COUNT(*) GROUP BY term_introduced_by, semantic_or_transiteration
|> ORDER BY term_introduced_by```

Run terminology analysis

```shell
python3 scripts/terminology_analysis.py
```

### Terminology Analysis

Load the CSV file into the GCS bucket:

```shell
gcloud storage cp data/terminology_analysis.csv gs://${CSZJJ_BUCKET_NAME}/terminology_analysis.csv
```

Load the terminology usage file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.terminology_analysis \
    gs://${CSZJJ_BUCKET_NAME}/terminology_analysis.csv \
    data/terminology_analysis_schema.json
```

SQL queries:

```sql
-- Valid and invalid terminology
FROM cszjj.terminology_analysis
|> AGGREGATE COUNT(*) GROUP BY valid_terminology
```

```sql
-- Correlation on terminology validation
FROM cszjj.terminology_analysis AS TA
|> INNER JOIN cszjj.terminology_validation AS TV ON TA.term = TV.term
|> AGGREGATE COUNT(*) GROUP BY TA.valid_terminology, TV.valid
```

```sql
-- Count of Distinct Terms by Translation Type
FROM cszjj.terminology_analysis
|> WHERE valid_terminology 
|> AGGREGATE COUNT(*) AS `Count of Distinct Terms` GROUP BY translation_type
|> ORDER BY `Count of Distinct Terms` DESC
```

```sql
-- Translation Analysis - types with percental
SELECT
  translation_type,
  `Count of Distinct Terms`,
  ROUND((`Count of Distinct Terms` * 100.0 / SUM(`Count of Distinct Terms`) OVER ()), 1) AS `Percentage of Total`
FROM
  (
    SELECT
      translation_type,
      COUNT(*) AS `Count of Distinct Terms`
    FROM
      cszjj.terminology_analysis
    WHERE
      valid_terminology = TRUE
    GROUP BY translation_type
  )
ORDER BY `Count of Distinct Terms` DESC;
```

```sql
-- Terminology Analysis - Semantic translations
FROM cszjj.terminology_usage AS TU
INNER JOIN cszjj.terminology_analysis AS TA ON TU.term = TA.term
|> WHERE TA.valid_terminology and TA.translation_type = 'Semantic'
|> SELECT DISTINCT TA.term, TA.english_equivalent, TA.term_introduced_by, TU.document_frequency
|> ORDER BY document_frequency DESC
```

```sql
-- Count of Distinct Terms by Translation Type, pivot by translator
SELECT * FROM
  (SELECT
    term,
    translation_type,
    term_introduced_by,
  FROM cszjj.terminology_analysis
  WHERE valid_terminology)
PIVOT (
  COUNT(DISTINCT term) AS count_terms
  FOR term_introduced_by IN ('An Shigao', 'Lokakṣema', 'Dharmarakṣa', 'Kumārajīva')
)
ORDER BY `count_terms_Kumārajīva` DESC
```

```sql
-- Most widely used terms introduced by a particular translator of a particular translation type
FROM cszjj.terminology_usage AS TU
JOIN cszjj.terminology_analysis as TA ON TU.term = TA.term
|> WHERE TU.term_introduced_by = 'Zhi Qian' AND TA.translation_type = 'Buddhist idiom'
|> SELECT DISTINCT TU.term, TU.document_frequency
|> ORDER BY document_frequency DESC
```
## Unique and Extinct Terminology

```sql
-- Terms established by An Shigao only adopted in anonymous texts
WITH Adopted AS (
  SELECT
    DISTINCT term,
  FROM cszjj.terminology_usage
  WHERE document_frequency > 1
    AND attribution IS NOT NULL
    AND attribution != "An Shigao"
)
SELECT
  term,
  term_introduced_by,
  czjj_no,
  czsjj_title_zh,
  taisho_no
FROM cszjj.terminology_usage
WHERE
  document_frequency > 1
  AND term_introduced_by = "An Shigao"
  AND attribution IS NULL
  AND term NOT IN (SELECT term FROM Adopted)
```
