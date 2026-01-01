"""
Author: Antonio Carrascosa Jiménez
Date: January 2026
Project: Dataset Profiling + LLM Interpretation

Description:
Script that consumes a dataset profiling JSON and uses a local LLM
(e.g. Ollama or LM Studio) to generate a concise textual report with
conclusions and recommended actions based on detected statistics and
data quality signals.

execution:
    After compiling the notebook `dataset_profiling.ipynb` to generate the profiling JSON
    run 'python src/llm_insights.py'
"""

import json
import requests

# =========================
# CONFIGURATION
# =========================

REPORT_PATH = "processed_data.json"
OUTPUT_PATH = "dataset_interpretation.txt"

MODEL_URL = MODEL_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1"

TEMPERATURE = 0.2

# =========================
# LOAD PROFILING REPORT
# =========================

with open(REPORT_PATH, "r", encoding="utf-8") as file:
    report = json.load(file)

# =========================
# PROMPT CONSTRUCTION
# =========================

prompt = f"""
You are a senior data analyst interpreting automated dataset profiling reports.

Strict output rules:
- Do not explain basic statistics or data science concepts.
- Do not repeat raw numerical values unless strictly necessary.
- Avoid generic introductions or filler phrases.
- Do not infer information not present in the report.
- Use short, direct, technical sentences.
- Maximum 3 sections.
- Maximum 7 bullet points per section.
- Make sure to add every recommendation from the report.

Dataset context:
- Total rows: {report.get("total_rows")}
- Total columns: {report.get("total_columns")}
- Global missing value percentage: {report.get("dataset_info", {}).get("percent_nan_global")}
- Columns with high missing ratio: {report.get("quality_summary", {}).get("columns_high_nan")}
- Constant columns: {report.get("quality_summary", {}).get("constant_columns")}
- Identifier columns: {report.get("quality_summary", {}).get("identifier_columns")}
- Total Colum data: {report.get("columns", {})}

Column-level information may include:
- Quartiles (25%, 50%, 75%)
- Maximum values
- IQR
- Data quality warnings
- Automatic recommendations

Mandatory output format:

Executive summary:
<1-5 sentences>

Detected risks:
- <concrete risk derived from the report>
- <concrete risk derived from the report>
...

Recommended actions:
- <concrete technical action>
- <concrete technical action>
...


Do not add any text outside this format. 
For every detected risk, provide an exameple from the dataset profiling report adding the column_name field, but do not add data_type or nan metrics if its not necesary.
"""

# =========================
# CALL LOCAL LLM
# =========================

response = requests.post(
    MODEL_URL,
    json={
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
)

response.raise_for_status()

content = response.json()["message"]["content"]

# =========================
# WRITE OUTPUT FILE
# =========================

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    file.write("AUTOMATED DATASET INTERPRETATION\n")
    file.write("=" * 45 + "\n\n")
    file.write(content.strip())
    file.write("\n")

print("\n--- Automated interpretation ---\n")
print(content)
print(f"\nReport saved to: {OUTPUT_PATH}")
