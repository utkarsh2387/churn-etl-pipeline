"""
Data quality validation stage.

Runs a set of assertions against the pipeline's output and raises a
DataQualityError if any check fails. Wired into the flow so that a
failed check fails the whole run (and the GitHub Actions job) instead
of silently shipping bad data.

Thresholds are intentionally simple and documented — tune them if the
expected shape of the dataset changes.
"""

import pandas as pd


class DataQualityError(Exception):
    """Raised when the pipeline's output fails a quality check."""
    pass


# Expected bounds, based on the known Telco Customer Churn dataset.
# Adjust these if you swap in a different source file.
EXPECTED_ROW_RANGE = (6500, 7100)          # raw dataset is 7,043 rows
MAX_ANOMALY_RATE = 0.10                     # contamination is set to 0.03; alert well above that
REQUIRED_COLUMNS = {"anomaly_flag"}


def validate(df: pd.DataFrame) -> dict:
    """
    Run all data quality checks against the transformed DataFrame.

    Returns:
        dict of check results (for logging).

    Raises:
        DataQualityError: if any check fails.
    """
    checks = {}
    errors = []

    # 1. Row count sanity check
    row_count = len(df)
    checks["row_count"] = row_count
    if not (EXPECTED_ROW_RANGE[0] <= row_count <= EXPECTED_ROW_RANGE[1]):
        errors.append(
            f"Row count {row_count} outside expected range {EXPECTED_ROW_RANGE}"
        )

    # 2. Required columns present
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    checks["missing_columns"] = list(missing_cols)
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    # 3. No fully-null rows (a join or encoding failure often produces these)
    fully_null_rows = int(df.isnull().all(axis=1).sum())
    checks["fully_null_rows"] = fully_null_rows
    if fully_null_rows > 0:
        errors.append(f"{fully_null_rows} fully-null rows found")

    # 4. Anomaly rate within expected bounds
    if "anomaly_flag" in df.columns and row_count > 0:
        anomaly_rate = (df["anomaly_flag"] == "anomaly").sum() / row_count
        checks["anomaly_rate"] = round(anomaly_rate, 4)
        if anomaly_rate > MAX_ANOMALY_RATE:
            errors.append(
                f"Anomaly rate {anomaly_rate:.1%} exceeds max threshold {MAX_ANOMALY_RATE:.0%}"
            )

    # 5. No duplicate rows in final output
    duplicate_rows = int(df.duplicated().sum())
    checks["duplicate_rows"] = duplicate_rows
    if duplicate_rows > 0:
        errors.append(f"{duplicate_rows} duplicate rows found in final output")

    checks["passed"] = len(errors) == 0
    checks["errors"] = errors

    if errors:
        error_summary = "; ".join(errors)
        print(f"[VALIDATE] FAILED — {error_summary}")
        raise DataQualityError(error_summary)

    print(f"[VALIDATE] All checks passed: {checks}")
    return checks


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent))
    from extract import extract
    from transform import transform

    raw = extract()
    transformed = transform(raw)
    validate(transformed)
