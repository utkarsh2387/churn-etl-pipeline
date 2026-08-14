"""
Orchestrates the full churn ETL pipeline with Prefect:
Extract -> Transform (AI anomaly detection) -> Load -> AI QA report.

Run locally:
    python flows/pipeline_flow.py

Run with Prefect's UI/logging:
    prefect server start   (in a separate terminal, optional)
    python flows/pipeline_flow.py
"""

import sys
from pathlib import Path

# allow running this file directly (adds src/ to the import path)
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from prefect import flow, task

from extract import extract
from transform import transform
from load import load
from ai_report import generate_qa_summary




@task(retries=2, retry_delay_seconds=10)
def extract_task():
    return extract()


@task
def transform_task(df):
    return transform(df)


@task
def load_task(df):
    load(df)
    return df


@task
def report_task(df):
    stats = {
        "total_rows": len(df),
        "anomalies": int((df["anomaly_flag"] == "anomaly").sum()),
    }
    summary = generate_qa_summary(stats)
    print("\n[AI REPORT]\n" + summary)
    return summary


@flow(name="churn-etl-pipeline", log_prints=True)
def churn_pipeline():
    raw_df = extract_task()
    clean_df = transform_task(raw_df)
    loaded_df = load_task(clean_df)
    report_task(loaded_df)


if __name__ == "__main__":
    churn_pipeline()
