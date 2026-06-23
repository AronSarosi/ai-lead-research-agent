"""Pydantic models for the agent's structured data.

These do double duty: they validate the LLM's structured output and they give
every node a clear, typed contract. Keep them small and flat - this is a v1.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# --- Inputs -----------------------------------------------------------------


class ICP(BaseModel):
    """An Ideal Client Profile: who we're looking for and what we're pitching."""

    industry: str = Field(description="Target industry, e.g. 'B2B SaaS' or 'recruitment agencies'.")
    company_size: str = Field(default="", description="Rough size, e.g. '10-50 employees'.")
    location: str = Field(default="", description="Geography, e.g. 'London, UK'.")
    keywords: str = Field(default="", description="Extra signals to match on, comma separated.")
    offer: str = Field(description="The offer being pitched, in one or two sentences.")
    num_companies: int = Field(default=5, ge=1, le=20, description="How many companies to research.")
    # Optional manual list of company names to skip discovery for known targets.
    manual_companies: List[str] = Field(default_factory=list)


class Profile(BaseModel):
    """Aron's details, injected into the draft so it sounds like him, not generic AI."""

    name: str
    one_line_offer: str = ""
    demo_links: List[str] = Field(default_factory=list)
    tone_notes: str = ""
    credibility: str = ""
    sign_off: str = ""


# --- Per-company results ----------------------------------------------------


class Company(BaseModel):
    """A candidate company surfaced during discovery."""

    name: str
    domain: str = Field(default="", description="Best-guess website domain.")
    reason: str = Field(default="", description="One line on why it matches the ICP.")


class CompanyList(BaseModel):
    """Wrapper so the LLM can return a list via structured output."""

    companies: List[Company] = Field(default_factory=list)


class Research(BaseModel):
    """What we learned about a company."""

    what_they_do: str = Field(description="One or two plain sentences on the business.")
    signals: List[str] = Field(default_factory=list, description="Recent, specific signals (news, hires, launches).")
    fit_score: int = Field(default=0, ge=0, le=100, description="0-100 fit against the ICP.")
    fit_reason: str = Field(default="", description="Short justification for the fit score.")


class PainPoints(BaseModel):
    """A couple of hypothesised pain points the offer could solve."""

    pain_points: List[str] = Field(default_factory=list)


class Contact(BaseModel):
    """A likely decision-maker. A hypothesis unless confidence is 'found'."""

    name: str = Field(default="", description="Person's name, or empty if only a role is known.")
    title: str = Field(default="", description="Job title or target role, e.g. 'Head of Marketing'.")
    source: str = Field(default="", description="URL the contact was inferred from, if any.")
    confidence: str = Field(default="guess", description="'found', 'likely', or 'guess'.")


class Draft(BaseModel):
    """The personalised cold-outreach draft. Always reviewed by a human before use."""

    subject: str = Field(description="A short, specific subject line. No clickbait.")
    message: str = Field(description="The outreach body. Short, personal, ties a specific detail to the offer.")


class LeadResult(BaseModel):
    """Everything we produced for a single company - one row in the results table."""

    company: Company
    research: Research
    pain_points: List[str] = Field(default_factory=list)
    contact: Contact
    draft: Draft
    error: Optional[str] = None
