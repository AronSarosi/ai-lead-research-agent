"""Shared test fixtures and helpers.

The whole suite is offline: no live OpenAI, Azure, or Tavily calls. Anything
that would hit the network is either mocked or driven down a no-network code
path (e.g. a manual company list).
"""

from __future__ import annotations

import pytest

from agent.schemas import (
    Company,
    Contact,
    Draft,
    LeadResult,
    Research,
)


@pytest.fixture
def sample_lead_result() -> LeadResult:
    """A fully populated LeadResult for export / table tests."""
    return LeadResult(
        company=Company(name="Acme Ltd", domain="acme.example", reason="fits the ICP"),
        research=Research(
            what_they_do="Builds widgets.",
            signals=["raised funding", "hired a CMO"],
            fit_score=82,
            fit_reason="Strong match.",
        ),
        pain_points=["Manual reporting", "Slow onboarding"],
        contact=Contact(
            name="Jane Doe",
            title="Head of Marketing",
            source="https://acme.example/team",
            confidence="found",
        ),
        draft=Draft(subject="Quick idea for Acme", message="Hi Jane, ..."),
        error=None,
    )


@pytest.fixture
def failed_lead_result() -> LeadResult:
    """A LeadResult that represents a failed company run."""
    return LeadResult(
        company=Company(name="Broken Co"),
        research=Research(what_they_do="(research failed)"),
        pain_points=[],
        contact=Contact(),
        draft=Draft(subject="", message=""),
        error="boom",
    )
