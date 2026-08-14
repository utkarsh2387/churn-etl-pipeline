"""
Transform stage of the churn ETL pipeline.

Cleans the raw dataset and applies an unsupervised ML model
(Isolation Forest) to automatically flag anomalous customer records
for review, instead of relying on hardcoded threshold rules.
"""

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: fix types, drop unparseable/duplicate rows."""
    df = df.copy()

    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        before = len(df)
        df = df.dropna(subset=["TotalCharges"])
        dropped = before - len(df)
        if dropped:
            print(f"[TRANSFORM] Dropped {dropped} rows with unparseable TotalCharges")

    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    if dropped:
        print(f"[TRANSFORM] Dropped {dropped} duplicate rows")

    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Label-encode categorical columns so the anomaly model can consume them."""
    df = df.copy()
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        if col == "customerID":
            continue
        df[col] = LabelEncoder().fit_transform(df[col].astype(str))
    return df


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.03) -> pd.DataFrame:
    """
    AI step: fits an Isolation Forest on the numeric feature space and
    flags statistically anomalous customer records.

    Args:
        df: encoded DataFrame (numeric columns only will be used).
        contamination: expected proportion of anomalies (tune per dataset).

    Returns:
        DataFrame with an added 'anomaly_flag' column ('normal' / 'anomaly').
    """
    df = df.copy()
    numeric_df = df.select_dtypes(include="number")

    model = IsolationForest(contamination=contamination, random_state=42)
    predictions = model.fit_predict(numeric_df)

    df["anomaly_flag"] = pd.Series(predictions, index=df.index).map(
        {1: "normal", -1: "anomaly"}
    )

    n_flagged = (df["anomaly_flag"] == "anomaly").sum()
    print(f"[TRANSFORM] Flagged {n_flagged} anomalous records via Isolation Forest "
          f"({n_flagged / len(df):.1%} of dataset)")

    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Full transform pipeline: clean -> encode -> detect anomalies."""
    df = clean(df)
    encoded = encode_categoricals(df)
    result = detect_anomalies(encoded)
    return result


if __name__ == "__main__":
    from extract import extract

    raw = extract()
    transformed = transform(raw)
    print(transformed[["anomaly_flag"]].value_counts())
