"""Turn results into a flat table for display and CSV export."""

from __future__ import annotations

from typing import List

import pandas as pd

from .schemas import LeadResult

# Column order used in both the editable table and the CSV.
COLUMNS = [
    "Company",
    "Website",
    "What they do",
    "Signals",
    "Fit",
    "Pain points",
    "Contact",
    "Title",
    "Confidence",
    "Subject",
    "Draft",
    "Source",
    "Notes",
]


def results_to_dataframe(results: List[LeadResult]) -> pd.DataFrame:
    """Flatten LeadResults into a DataFrame with one row per company."""
    rows = []
    for r in results:
        rows.append(
            {
                "Company": r.company.name,
                "Website": r.company.domain,
                "What they do": r.research.what_they_do,
                "Signals": " | ".join(r.research.signals),
                "Fit": r.research.fit_score,
                "Pain points": " | ".join(r.pain_points),
                "Contact": r.contact.name,
                "Title": r.contact.title,
                "Confidence": r.contact.confidence,
                "Subject": r.draft.subject,
                "Draft": r.draft.message,
                "Source": r.contact.source,
                "Notes": r.error or "",
            }
        )
    return pd.DataFrame(rows, columns=COLUMNS)


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Encode a DataFrame as UTF-8 CSV bytes for st.download_button."""
    return df.to_csv(index=False).encode("utf-8")
