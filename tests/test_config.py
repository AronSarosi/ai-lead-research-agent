"""Tests for agent.config: Settings.validate(), properties, and load_settings()."""

from __future__ import annotations

from agent.config import Settings, load_settings


# --- validate() branches ----------------------------------------------------


def test_validate_clean_openai():
    s = Settings(provider="openai", openai_api_key="sk-x", tavily_api_key="tv-x")
    assert s.validate() == []


def test_validate_missing_openai_key():
    s = Settings(provider="openai", openai_api_key="", tavily_api_key="tv-x")
    problems = s.validate()
    assert any("OPENAI_API_KEY" in p for p in problems)


def test_validate_missing_tavily_is_a_soft_warning():
    s = Settings(provider="openai", openai_api_key="sk-x", tavily_api_key="")
    problems = s.validate()
    assert any("TAVILY_API_KEY" in p for p in problems)
    # Missing Tavily is non-fatal: the OpenAI key is still fine.
    assert not any("OPENAI_API_KEY" in p for p in problems)


def test_validate_azure_incomplete():
    s = Settings(provider="azure", azure_api_key="k", tavily_api_key="tv-x")
    problems = s.validate()
    assert any("AZURE_OPENAI" in p for p in problems)


def test_validate_azure_complete():
    s = Settings(
        provider="azure",
        azure_api_key="k",
        azure_endpoint="https://x.openai.azure.com",
        azure_deployment="dep",
        tavily_api_key="tv-x",
    )
    assert s.validate() == []


# --- properties -------------------------------------------------------------


def test_search_enabled_property():
    assert Settings(tavily_api_key="tv-x").search_enabled is True
    assert Settings(tavily_api_key="").search_enabled is False


def test_langfuse_enabled_needs_both_keys():
    assert Settings(langfuse_public_key="p", langfuse_secret_key="s").langfuse_enabled is True
    assert Settings(langfuse_public_key="p").langfuse_enabled is False
    assert Settings(langfuse_secret_key="s").langfuse_enabled is False
    assert Settings().langfuse_enabled is False


# --- load_settings() reads the documented env knobs -------------------------


def test_load_settings_defaults(monkeypatch):
    for var in [
        "LLM_PROVIDER",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "OPENAI_DRAFT_MODEL",
        "LLM_TEMPERATURE",
        "LLM_DRAFT_TEMPERATURE",
        "TAVILY_API_KEY",
    ]:
        monkeypatch.delenv(var, raising=False)
    s = load_settings()
    assert s.provider == "openai"
    assert s.openai_model == "gpt-4o-mini"
    assert s.openai_draft_model == "gpt-4o"
    assert s.temperature == 0.4
    assert s.draft_temperature == 0.6


def test_load_settings_reads_draft_temperature(monkeypatch):
    monkeypatch.setenv("LLM_TEMPERATURE", "0.1")
    monkeypatch.setenv("LLM_DRAFT_TEMPERATURE", "0.9")
    s = load_settings()
    assert s.temperature == 0.1
    assert s.draft_temperature == 0.9


def test_load_settings_normalises_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "  AZURE ")
    s = load_settings()
    assert s.provider == "azure"
