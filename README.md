# Churn ETL Pipeline (AI-Enabled)

Automated ETL pipeline that preprocesses the Telco Customer Churn dataset,
using an unsupervised ML model to detect anomalous records and an LLM to
generate a plain-English data quality summary on every run.

## What makes this "AI-enabled"

- **Anomaly detection (ML):** an Isolation Forest is fit on the numeric
  feature space during the Transform stage and flags statistically
  anomalous customer records, replacing hardcoded threshold rules.
- **AI QA reporting (LLM):** run statistics are sent to the Claude API,
  which returns a 3-bullet, non-technical summary of data quality for
  that run.

## Architecture

```
Extract (CSV) -> Transform (clean + encode + Isolation Forest) -> Load (SQLite)
                                                                        |
                                                                        v
                                                        AI QA summary (Claude API)
```

Orchestrated with [Prefect](https://www.prefect.io/); containerized with
Docker; scheduled via GitHub Actions (free tier, no cloud infra required).

## Project structure

```
churn-etl-pipeline/
├── data/raw/              # place telco_churn.csv here
├── src/
│   ├── extract.py         # reads raw CSV
│   ├── transform.py       # cleans data, runs Isolation Forest anomaly detection
│   ├── ai_report.py       # Claude-generated QA summary
│   └── load.py            # writes to SQLite warehouse
├── flows/
│   └── pipeline_flow.py   # Prefect flow tying it all together
├── .github/workflows/
│   └── run_pipeline.yml   # scheduled daily run via GitHub Actions
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Setup

1. **Get the dataset.** Download the
   [Telco Customer Churn dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
   and place it at `data/raw/telco_churn.csv`.

2. **Install dependencies.**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure your API key (optional, enables AI QA report).**
   ```bash
   cp .env.example .env
   # edit .env and add your ANTHROPIC_API_KEY
   ```
   The pipeline runs end-to-end without a key — the AI report step just
   prints a note that it was skipped.

## Run locally

```bash
python flows/pipeline_flow.py
```

You'll see console output for each stage (rows loaded, anomalies flagged,
rows written) followed by the AI-generated QA summary.

## Run with Docker

```bash
docker build -t churn-etl .
docker run --env-file .env -v $(pwd)/data:/app/data churn-etl
```

Or with Compose:
```bash
docker compose up --build
```

## Schedule it (free, no cloud bill)

The included GitHub Actions workflow (`.github/workflows/run_pipeline.yml`)
runs the pipeline daily on GitHub's free runners.

1. Push this repo to GitHub.
2. Go to **Settings → Secrets and variables → Actions** and add
   `ANTHROPIC_API_KEY` as a repository secret.
3. The pipeline runs automatically on the schedule, or trigger it manually
   from the **Actions** tab (`workflow_dispatch`).
4. Each run uploads the resulting SQLite warehouse as a downloadable
   workflow artifact.

## Output

- `data/churn_warehouse.db` — SQLite database containing the
  `customers_clean` table: cleaned, encoded customer records with an
  added `anomaly_flag` column (`normal` / `anomaly`).
- Console/CI logs — row counts, duplicates removed, anomalies flagged,
  and the AI-generated QA summary.

## Extending this

- Swap SQLite for Postgres/BigQuery/Snowflake by changing the connection
  string in `src/load.py` — the rest of the pipeline is unchanged.
- Tune the `contamination` parameter in `detect_anomalies()`
  (`src/transform.py`) to match the expected anomaly rate in your data.
- Feed `anomaly_flag == "anomaly"` records into a separate review table
  or alerting step for a fuller data-quality workflow.
