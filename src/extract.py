"""
Extract stage of the churn ETL pipeline.
Reads the raw Telco customer churn CSV from disk.
"""

import pandas as pd
from pathlib import Path


def extract(source_path: str = "data/raw/telco_churn.csv") -> pd.DataFrame:
    """
    Load the raw customer churn dataset.

    Args:
        source_path: path to the raw CSV file.

    Returns:
        Raw pandas DataFrame, unmodified.
    """
    path = Path(source_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Source file not found: {path}. "
            f"Place the Telco Customer Churn CSV at this path before running the pipeline."
        )

    df = pd.read_csv(path)
    print(f"[EXTRACT] Loaded {len(df)} rows, {len(df.columns)} columns from {path}")
    return df


if __name__ == "__main__":
    df = extract()
    print(df.head())
