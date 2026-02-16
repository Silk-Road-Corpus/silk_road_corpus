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

The counts of Chinese characters used for translation of Indic grammatical
constucts are computed by the script:

## Vernacular elements

Run the script for the identification of vernacular elements:

```shell
nohup python3 scripts/style_vernacular.py &
```

The results will be written to data/style_vernacular.csv:

```shell
gcloud compute scp --zone "$ZONE" linguistic-analysis:~/silk_road_corpus/data/style_vernacular.csv style_vernacular.csv
```

Load the CSV file into the bucket:

```shell
gcloud storage cp data/style_vernacular.csv gs://${CSZJJ_BUCKET_NAME}/style_vernacular.csv
```

Load the vernacular analysis file into into BQ:

```shell
bq --project_id=${PROJECT_ID} load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    ${PROJECT_ID}:${DATASETID}.style_vernacular \
    gs://${CSZJJ_BUCKET_NAME}/style_vernacular.csv \
    data/style_vernacular_schema.json
```

## Indic source analysis
```shell
python3 scripts/style_indic.py
```

## Mutual information
The mutual information is computed by the script:

```shell
python3 scripts/style_mutual_info.py
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
-- Style - vernacular by translator
FROM cszjj.style AS S
|> INNER JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.vernacular_or_literary = 'vernacular'
|> SELECT S.czsjj_title_zh, S.taisho_no, C.attribution_analysis, S.notes
|> AGGREGATE COUNT(taisho_no) AS num_fascicles GROUP BY attribution_analysis
|> ORDER BY num_fascicles DESC
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

```sql
-- Style - group by ornate or plain
FROM cszjj.style
|> AGGREGATE COUNT(*) AS Count GROUP BY ornate_or_plain_language
```

```sql
-- Style - Ornate examples
FROM cszjj.style
|> WHERE ornate_or_plain_language = 'ornate'
```

```sql
-- Style - group by terse or verbose
FROM cszjj.style
|> AGGREGATE COUNT(*) AS Count GROUP BY terse_or_verbose
```

```sql
-- Style - Terse examples
FROM cszjj.style
|> WHERE terse_or_verbose = "terse"
```

```sql
-- Style - filter by translator
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE C.attribution_analysis = "Dharmarakṣa"
|> SELECT
     S.czsjj_title_zh,
     S.taisho_no,
     S.vernacular_or_literary,
     S.literal_or_fluent,
     S.ornate_or_plain_language,
     S.terse_or_verbose,
     S.idioms_used,
     S.factual_or_spiritual,
     S.indigenous_chinese,
     S.interpolations,
     S.interlinear_commentary,
     S.oral_transmission,
     S.explicit_sentence_subject,
     S.plural_zhu,
     S.tense,
     S.abbreviations,
     S.notes
```

```sql
-- Style - group by indigenous Chinese
FROM cszjj.style
|> AGGREGATE COUNT(*) AS Count GROUP BY indigenous_chinese
```

```sql
-- Style - which texts use indigenous Chinese concepts to explain Buddhist teachings
FROM cszjj.style
|> WHERE indigenous_chinese
```

```sql
-- Style - contains indigenous Chinese concepts, Chinese native compositions
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.indigenous_chinese
   AND C.top_level_genre = "sutra"
   AND C.secondary_lit_classification IS NOT NULL
|> SELECT DISTINCT
     C.title_en,
     C.modern_title,
     C.modern_ref
```

```sql
-- Style - group by interpolations
FROM cszjj.style
|> AGGREGATE COUNT(*) AS Count GROUP BY interpolations
```

```sql
-- Style - containing interpolations
FROM cszjj.style
|> WHERE interpolations
```

```sql
-- Style - containing interpolations
FROM cszjj.style
|> WHERE interpolations
```

```sql
-- Style - containing interpolations, group by translator
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.interpolations AND C.top_level_genre = "sutra"
|> AGGREGATE COUNT (DISTINCT C.title_zh) AS count_inter GROUP BY C.attribution_analysis
|> ORDER BY count_inter DESC
```

```sql
-- Style - containing interpolations with useful note
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.interpolations
   AND C.top_level_genre = "sutra"
   AND S.notes LIKE "%interpolations%"
|> SELECT S.czsjj_title_zh, S.taisho_no, S.notes
```

```sql
-- Style - contains interpolations, Chinese native compositions
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.interpolations
   AND C.top_level_genre = "sutra"
   AND C.secondary_lit_classification IS NOT NULL
|> SELECT DISTINCT
     C.title_zh,
     C.title_en,
     C.modern_title,
     C.modern_ref,
     C.attribution_analysis
```

```sql
-- Style - containing interlinear commentary
FROM cszjj.style
|> WHERE interlinear_commentary
```

```sql
-- Style - containing interlinear commentary, group by translator
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.interlinear_commentary AND C.top_level_genre = "sutra"
|> AGGREGATE COUNT (DISTINCT C.title_zh) AS count_inter GROUP BY C.attribution_analysis
|> ORDER BY count_inter DESC
```

```sql
-- Style - contains interlinear commentary, anonymously produced
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.interlinear_commentary
   AND C.top_level_genre = "sutra"
   AND C.attribution_analysis IS NULL
```

```sql
-- Style - contains interlinear commentary, Chinese native compositions
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.interlinear_commentary
   AND C.top_level_genre = "sutra"
   AND C.secondary_lit_classification IS NOT NULL
```

```sql
-- Style - uses explicit sentence subject
FROM cszjj.style
|> AGGREGATE COUNT(*) GROUP BY explicit_sentence_subject
```

```sql
-- Style - explicit sentence subject notes
FROM cszjj.style
|> WHERE notes LIKE "%explicit%"
|> SELECT czsjj_title_zh, taisho_no, explicit_sentence_subject, notes
```

```sql
-- Style - not using 諸 zhū to indicate plural
FROM cszjj.style
|> WHERE NOT plural_zhu
```

```sql
-- Style - Plural zhu, Chinese native compositions
FROM cszjj.style AS S
|> INNER JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE NOT S.plural_zhu
   AND C.modern_ref IS NOT NULL
   AND C.secondary_lit_classification IS NOT NULL
|> SELECT DISTINCT
     C.title_en,
     C.modern_title,
     C.modern_ref
```

```sql
-- Style - tense
FROM cszjj.style
|> AGGREGATE COUNT(*) GROUP BY tense
```

```sql
-- Style - tense, notes
FROM cszjj.style
|> WHERE tense = "explicit"
   AND notes LIKE "%tense%"
|> SELECT czsjj_title_zh, taisho_no, notes
```

```sql
-- Style - tense by translator
FROM cszjj.style AS S
|> JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE S.tense = "explicit"
|> AGGREGATE COUNT(DISTINCT C.title_zh) AS count_titles GROUP BY C.attribution_analysis
|> ORDER BY count_titles DESC
```

```sql
-- Style - Tense, Chinese native compositions
FROM cszjj.style AS S
|> INNER JOIN cszjj.chusanzangjiji AS C ON S.czsjj_title_zh = C.title_zh
|> WHERE NOT S.tense = "explicit"
   AND C.modern_ref IS NOT NULL
   AND C.secondary_lit_classification IS NOT NULL
|> SELECT DISTINCT
     C.title_en,
     C.modern_title,
     C.modern_ref
```
