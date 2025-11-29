# Linguistic Analysis

Setup the environment and run the Python script that extracts linguistic data from
the corpus:

```shell
cd ..
git clone https://github.com/alexamies/buddhist-dictionary.git
export NTI=$PWD/buddhist-dictionary/corpus/taisho
cd silk_road_corpus
python3 scripts/language_analysis.py
```

The results will be written to data/linguistic_analysis.csv. This can also take a long
time to run. If you need to restart it use the `--restart` flag. If you need to run
it for a single entry use the `--title` flag.

Load the CSV file into the bucket:

```shell
gcloud storage cp data/linguistic_analysis.csv gs://${CSZJJ_BUCKET_NAME}/linguistic_analysis.csv
```

Load the language analysis file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.linguistic_analysis \
    gs://${CSZJJ_BUCKET_NAME}/linguistic_analysis.csv \
    data/linguistic_analysis_schema.json
```

SQL queries:

```sql
-- Number of texts analyzed
FROM cszjj.linguistic_analysis
|> AGGREGATE COUNT(*)
```

```sql
-- What at the centuries were the texts produced in?
FROM cszjj.chusanzangjiji
|> WHERE century IS NOT NULL
|> SELECT
     id,
     title_zh,
     modern_ref,
     attribution_analysis,
     century
```

```sql
-- Histogram of the centuries were the texts produced in
FROM cszjj.chusanzangjiji
|> WHERE century IS NOT NULL
|> AGGREGATE COUNT(*) as count_century GROUP BY century
|> ORDER BY CENTURY
```

```sql
-- Aggreate results from indivual fascicles into results for each title, join with century from CSZJJ
WITH Frequencies
AS (
  SELECT
    CASE
      WHEN INSTR(t.taisho_no, '(') > 0 THEN TRIM(SUBSTR(t.taisho_no, 1, INSTR(t.taisho_no, '(') - 1))
      ELSE t.taisho_no
    END AS base_taisho_no,
    SUM(t.length) AS total_length,
    SAFE_DIVIDE(SUM(t.not_in_shanzai), SUM(t.length))*10000 AS not_in_shanzai_frequency10000,
    SAFE_DIVIDE(SUM(t.ye2_final_count), SUM(t.length))*10000 AS ye2_frequency10000,
    SAFE_DIVIDE(SUM(t.er3_final_count), SUM(t.length))*10000 AS er3_frequency10000,
    SAFE_DIVIDE(SUM(t.ye3_final_count), SUM(t.length))*10000 AS ye3_frequency10000,
    SAFE_DIVIDE(SUM(t.wei4_grammar_count), SUM(t.length))*10000 AS wei4_frequency10000,
    SAFE_DIVIDE(SUM(t.bei_grammar_count), SUM(t.length))*10000 AS bei_frequency10000,
    SAFE_DIVIDE(SUM(t.hezhe_count), SUM(t.length))*10000 AS hezhe_frequency10000,
    SAFE_DIVIDE(SUM(t.hedengren_count), SUM(t.length))*10000 AS hedengren_frequency10000,
    SAFE_DIVIDE(SUM(t.cun_count), SUM(t.length))*10000 AS cun_frequency10000,
    SAFE_DIVIDE(SUM(t.tian_count), SUM(t.length))*10000 AS tian_frequency10000,
    SAFE_DIVIDE(SUM(t.sixiang_count), SUM(t.length))*10000 AS sixiang_frequency10000,
    SAFE_DIVIDE(SUM(t.di_sense_count), SUM(t.length))*10000 AS di_frequency10000,
    SAFE_DIVIDE(SUM(t.shigu_sense_count), SUM(t.length))*10000 AS shigu_frequency10000,
    SAFE_DIVIDE(SUM(t.yiqie_sense_count), SUM(t.length))*10000 AS yiqie_frequency10000,
  FROM
    cszjj.linguistic_analysis AS t
  GROUP BY base_taisho_no
)
SELECT
  f.base_taisho_no AS taisho_no,
  f.total_length,
  f.not_in_shanzai_frequency10000,
  f.ye2_frequency10000,
  f.er3_frequency10000,
  f.ye3_frequency10000,
  f.wei4_frequency10000,
  f.bei_frequency10000,
  f.hezhe_frequency10000,
  f.hedengren_frequency10000,
  f.cun_frequency10000,
  f.tian_frequency10000,
  f.sixiang_frequency10000,
  f.di_frequency10000,
  f.shigu_frequency10000,
  f.yiqie_frequency10000,
  c.century
FROM Frequencies AS f
INNER JOIN cszjj.chusanzangjiji AS c
  ON f.base_taisho_no = c.modern_ref
WHERE c.century IS NOT NULL
```

Older queries:

```sql
-- Number of anonymous texts analyzed
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE C.fascicle = 3 OR C.fascicle = 4
|> AGGREGATE COUNT(*)
```

```sql
-- Median length in characters of anonymous texts
FROM cszjj.chusanzangjiji AS C
|> INNER JOIN cszjj.language_analysis AS LA
  ON C.title_zh = LA.czsjj_title_zh
|> WHERE C.fascicle = 3 OR C.fascicle = 4
|> SELECT PERCENTILE_CONT(LA.length, 0.5) OVER () AS media_length
|> LIMIT 1
```

```sql
-- Number of anonymous texts analyzed by ru shi wo wen
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE (C.fascicle = 3 OR C.fascicle = 4)
|> AGGREGATE COUNT(*) AS num_texts GROUP BY LA.rushiwowen, LA.wenrushi
```

```sql
-- List of anonymous texts analyzed by ru shi wo wen
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE (C.fascicle = 3 OR C.fascicle = 4)
|> SELECT LA.taisho_no, LA.rushiwowen, LA.wenrushi
```

```sql
-- Counts of anonymous texts with We Ru Shi by section
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE (C.fascicle = 3 OR C.fascicle = 4)
   AND LA.wenrushi
|> SELECT C.title_zh, LA.taisho_no, C.modern_title, C.fascicle, C.section
|> AGGREGATE COUNT(*) num_texts GROUP BY fascicle, section
|> ORDER BY fascicle, section
```

```sql
-- Number of anonymous texts with Wen Ru Shi and no final particles
FROM cszjj.language_analysis AS LA
|> JOIN cszjj.chusanzangjiji AS C
   ON LA.czsjj_title_zh = C.title_zh
|> WHERE (C.fascicle = 3 OR C.fascicle = 4)
   AND LA.wenrushi
   and not_in_shanzai = 0
   AND ye2_final_count = 0
   AND er3_final_count = 0
   AND ye3_final_count = 0
|> AGGREGATE COUNT(*) AS num_texts
```
