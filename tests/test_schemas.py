"""Tests for the Pydantic schemas: defaults, bounds, and the enrichment stub."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agent.enrichment import enrich_contact
from agent.schemas import Company, Contact, ICP, Research


def test_icp_defaults():
    icp = ICP(industry="saas", offer="an offer")
    assert icp.num_companies == 5
    assert icp.manual_companies == []
    assert icp.company_size == ""


def test_icp_num_companies_bounds():
    with pytest.raises(ValidationError):
        ICP(industry="x", offer="y", num_companies=0)
    with pytest.raises(ValidationError):
        ICP(industry="x", offer="y", num_companies=21)


def test_research_fit_score_bounds():
    with pytest.raises(ValidationError):
        Research(what_they_do="x", fit_score=101)
    assert Research(what_they_do="x", fit_score=100).fit_score == 100


def test_contact_defaults_to_guess():
    c = Contact()
    assert c.confidence == "guess"
    assert c.name == ""


def test_enrich_contact_stub_returns_none():
    # Intentional extension seam: returns None in v1.
    assert enrich_contact(Company(name="Acme")) is None
    assert enrich_contact(Company(name="Acme"), role_hint="Head of Marketing") is None
