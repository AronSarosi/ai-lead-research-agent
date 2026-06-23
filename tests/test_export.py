"""Tests for agent.export: DataFrame shape, columns, and CSV encoding."""

from __future__ import annotations

from agent.export import COLUMNS, dataframe_to_csv_bytes, results_to_dataframe


def test_dataframe_columns_match_spec(sample_lead_result):
    df = results_to_dataframe([sample_lead_result])
    assert list(df.columns) == COLUMNS


def test_dataframe_one_row_per_result(sample_lead_result, failed_lead_result):
    df = results_to_dataframe([sample_lead_result, failed_lead_result])
    assert df.shape == (2, len(COLUMNS))


def test_empty_results_gives_empty_frame_with_columns():
    df = results_to_dataframe([])
    assert df.empty
    assert list(df.columns) == COLUMNS


def test_list_fields_are_joined_with_pipe(sample_lead_result):
    df = results_to_dataframe([sample_lead_result])
    row = df.iloc[0]
    assert row["Signals"] == "raised funding | hired a CMO"
    assert row["Pain points"] == "Manual reporting | Slow onboarding"


def test_scalar_fields_map_through(sample_lead_result):
    row = results_to_dataframe([sample_lead_result]).iloc[0]
    assert row["Company"] == "Acme Ltd"
    assert row["Website"] == "acme.example"
    assert row["Fit"] == 82
    assert row["Contact"] == "Jane Doe"
    assert row["Confidence"] == "found"
    assert row["Subject"] == "Quick idea for Acme"


def test_error_lands_in_notes_column(failed_lead_result, sample_lead_result):
    df = results_to_dataframe([sample_lead_result, failed_lead_result])
    assert df.iloc[0]["Notes"] == ""
    assert df.iloc[1]["Notes"] == "boom"


def test_csv_bytes_roundtrip(sample_lead_result):
    df = results_to_dataframe([sample_lead_result])
    data = dataframe_to_csv_bytes(df)
    assert isinstance(data, bytes)
    text = data.decode("utf-8")
    assert "Acme Ltd" in text
    # Header line present.
    assert text.splitlines()[0].startswith("Company,")
