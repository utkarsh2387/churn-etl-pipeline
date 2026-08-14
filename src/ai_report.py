"""
Optional AI reporting stage.

Sends run statistics to Claude and gets back a short, plain-English
data quality summary — useful for a non-technical stakeholder update
or a portfolio screenshot. Fails gracefully if no API key is set,
so the pipeline still runs end-to-end without it.
"""

import os
import anthropic


def generate_qa_summary(stats: dict) -> str:
    """
    Generate a 3-bullet plain-English QA summary of the ETL run.

    Args:
        stats: dict of run statistics, e.g.
            {"total_rows": 7032, "anomalies": 211, "duplicates_removed": 4}

    Returns:
        Summary text, or a fallback message if no API key is configured.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            "[AI REPORT SKIPPED] No ANTHROPIC_API_KEY set — "
            "add one to .env to enable AI-generated QA summaries."
        )

    client = anthropic.Anthropic(api_key=api_key)

    prompt = (
        "Summarize this ETL pipeline run's data quality in exactly 3 short bullet "
        "points, written for a non-technical stakeholder. Be concrete and use the "
        f"numbers given. Stats: {stats}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


if __name__ == "__main__":
    example_stats = {"total_rows": 7032, "anomalies": 211, "duplicates_removed": 4}
    print(generate_qa_summary(example_stats))
