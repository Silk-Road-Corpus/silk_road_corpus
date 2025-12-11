# Instructions for Code Assist Agents

## Python Scripts

Python Scripts are in the `scripts` directory. They run in a virtual environment.
The libraries used by the Python scripts are in the requirements.txt file.
Many of the scripts use the Gemini REST API. The file `scripts/cszjj.py` provides
common functions.

If a script is generated, it should be saved to this directory.

## Vega Diagrams

Diagrams use the Vega visualization framework. The files are saved in the `drawings`
directory. If a figure is generated it should be saved in this directory. Prefer to
use the regular Vega syntax, not Vega-Lite.

## SQL Queries

SQL queries are in the markdown files. They use tabled loaded from the CSV files in
the `data` directory. The schemas for the tables are also stored in this directory.
They are the files endining with.json. Prefer to use pipe syntax.