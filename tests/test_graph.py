"""Tests for agent.graph.discover_companies.

The manual-company path takes no network. The discovery path is exercised with
the LLM and search both mocked, so still no live API calls.
"""

from __future__ import annotations

from agent.config import Settings
from agent.schemas import Company, CompanyList, ICP


def test_manual_companies_skip_discovery(monkeypatch):
    import agent.graph as graph

    # If discovery tried to search or call the LLM, these would blow up.
    def _boom(*args, **kwargs):
        raise AssertionError("manual path must not touch the network or LLM")

    monkeypatch.setattr(graph, "search", _boom)
    monkeypatch.setattr(graph, "get_llm", _boom)

    icp = ICP(
        industry="recruitment",
        offer="I help agencies",
        manual_companies=["Alpha Ltd", "  Beta Co ", ""],
    )
    companies = graph.discover_companies(icp, settings=Settings())

    names = [c.name for c in companies]
    assert names == ["Alpha Ltd", "Beta Co"]  # trimmed, blanks dropped
    assert all(isinstance(c, Company) for c in companies)


def test_discovery_path_uses_llm_and_caps_count(monkeypatch):
    import agent.graph as graph

    # Search returns nothing (mocked) - no network.
    monkeypatch.setattr(graph, "search", lambda *a, **k: [])

    returned = CompanyList(
        companies=[Company(name=f"Co {i}") for i in range(5)]
    )

    class _FakeLLM:
        def with_structured_output(self, _schema):
            return self

        def invoke(self, _prompt, config=None):
            return returned

    monkeypatch.setattr(graph, "get_llm", lambda settings: _FakeLLM())
    monkeypatch.setattr(graph, "get_callbacks", lambda settings: [])

    icp = ICP(industry="saas", offer="thing", num_companies=3)
    companies = graph.discover_companies(icp, settings=Settings())

    # Capped at num_companies.
    assert len(companies) == 3
    assert companies[0].name == "Co 0"
