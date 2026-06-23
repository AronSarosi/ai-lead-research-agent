"""The LangGraph agent.

Two parts:

1. `discover_companies` - one LLM + search step that turns an ICP into a list of
   candidate companies. Skipped when the user supplies a manual company list.

2. A compiled per-company `StateGraph`:
       research -> pain_points -> contact -> draft
   We invoke it once per company so a failure on one company never sinks the run.

LLM calls use structured output (Pydantic) so every node returns clean, typed
data instead of free text we'd have to parse.
"""

from __future__ import annotations

from typing import List, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from .config import Settings, load_settings
from .enrichment import enrich_contact
from .llm import get_callbacks, get_draft_llm, get_llm
from .schemas import (
    Company,
    CompanyList,
    Contact,
    Draft,
    ICP,
    LeadResult,
    PainPoints,
    Profile,
    Research,
)
from .search import hits_to_context, search


# --- Discovery --------------------------------------------------------------


def discover_companies(icp: ICP, settings: Optional[Settings] = None) -> List[Company]:
    """Turn an ICP into a list of candidate companies.

    If the ICP carries a manual company list, we use that verbatim. Otherwise we
    search the web for matches and ask the LLM to name real companies that fit.
    """
    settings = settings or load_settings()

    if icp.manual_companies:
        return [Company(name=n.strip()) for n in icp.manual_companies if n.strip()]

    query = " ".join(
        part
        for part in [
            icp.industry,
            icp.company_size,
            icp.location,
            icp.keywords,
            "companies",
        ]
        if part
    )
    context = hits_to_context(search(query, max_results=8, settings=settings))

    llm = get_llm(settings).with_structured_output(CompanyList)
    prompt = (
        "You are a B2B prospecting researcher. Using the Ideal Client Profile and the "
        "web search results, list real companies that plausibly match. Prefer specific, "
        "named organisations over generic categories. Avoid huge household-name enterprises "
        "unless they clearly fit a small-business offer.\n\n"
        f"Ideal Client Profile:\n"
        f"- Industry: {icp.industry}\n"
        f"- Company size: {icp.company_size}\n"
        f"- Location: {icp.location}\n"
        f"- Keywords: {icp.keywords}\n"
        f"- Offer being pitched: {icp.offer}\n\n"
        f"Web search results:\n{context}\n\n"
        f"Return up to {icp.num_companies} companies. For each: name, best-guess website "
        "domain, and one line on why it matches."
    )
    result: CompanyList = llm.invoke(prompt, config={"callbacks": get_callbacks(settings)})
    companies = result.companies[: icp.num_companies]
    return companies


# --- Per-company pipeline state ---------------------------------------------


class LeadState(TypedDict, total=False):
    # Inputs (set before invoke)
    icp: ICP
    profile: Profile
    company: Company
    settings: Settings
    # Produced by nodes
    research: Research
    pain_points: List[str]
    contact: Contact
    draft: Draft


# --- Nodes ------------------------------------------------------------------


def _node_research(state: LeadState) -> LeadState:
    icp, company, settings = state["icp"], state["company"], state["settings"]
    query = f"{company.name} {company.domain} company overview recent news"
    context = hits_to_context(search(query, max_results=6, settings=settings))

    llm = get_llm(settings).with_structured_output(Research)
    prompt = (
        "Research this company for a cold-outreach campaign. Be concrete and avoid filler.\n\n"
        f"Company: {company.name} ({company.domain})\n"
        f"Why it was shortlisted: {company.reason}\n\n"
        f"Offer being pitched to them: {icp.offer}\n\n"
        f"Web results:\n{context}\n\n"
        "Summarise what they do in one or two plain sentences. List recent, specific signals "
        "(news, hires, launches, funding) - only ones supported by the results, never invented. "
        "Then score fit 0-100 against the offer and justify it in one line."
    )
    state["research"] = llm.invoke(prompt, config={"callbacks": get_callbacks(settings)})
    return state


def _node_pain_points(state: LeadState) -> LeadState:
    icp, company, settings, research = (
        state["icp"],
        state["company"],
        state["settings"],
        state["research"],
    )
    llm = get_llm(settings).with_structured_output(PainPoints)
    prompt = (
        "Given what we know about this company and the offer, hypothesise the two most likely "
        "pain points the offer could solve. Be specific to this company - tie each to a detail "
        "from the research. These are hypotheses, so keep them plausible, not certain.\n\n"
        f"Company: {company.name}\n"
        f"What they do: {research.what_they_do}\n"
        f"Signals: {', '.join(research.signals) or 'none found'}\n"
        f"Offer: {icp.offer}\n"
    )
    result: PainPoints = llm.invoke(prompt, config={"callbacks": get_callbacks(settings)})
    state["pain_points"] = result.pain_points[:2]
    return state


def _node_contact(state: LeadState) -> LeadState:
    company, settings, icp = state["company"], state["settings"], state["icp"]

    # Seam for a future paid enrichment API. Returns None in v1.
    enriched = enrich_contact(company)
    if enriched is not None:
        state["contact"] = enriched
        return state

    query = f"{company.name} {icp.keywords} founder OR CEO OR head of marketing OR decision maker"
    hits = search(query, max_results=6, settings=settings)
    context = hits_to_context(hits)

    llm = get_llm(settings).with_structured_output(Contact)
    prompt = (
        "Identify the most likely decision-maker to approach at this company for the offer below. "
        "If the web results name a real person in a relevant senior role, use them and set "
        "confidence to 'found' (include the source URL) or 'likely'. If not, infer the most "
        "relevant target ROLE (e.g. 'Head of Marketing'), leave the name blank, and set "
        "confidence to 'guess'. Never invent a specific person's name.\n\n"
        f"Company: {company.name}\n"
        f"Offer: {icp.offer}\n\n"
        f"Web results:\n{context}\n"
    )
    state["contact"] = llm.invoke(prompt, config={"callbacks": get_callbacks(settings)})
    return state


def _node_draft(state: LeadState) -> LeadState:
    icp, company, settings, profile = (
        state["icp"],
        state["company"],
        state["settings"],
        state["profile"],
    )
    research, pain_points, contact = state["research"], state["pain_points"], state["contact"]

    greeting = contact.name or (f"the {contact.title}" if contact.title else "there")
    demos = "\n".join(f"- {d}" for d in profile.demo_links) or "(none)"

    # The draft is the bit that must sound like Aron, not generic AI - use the
    # stronger draft model here while the research steps stay on the cheap one.
    llm = get_draft_llm(settings).with_structured_output(Draft)
    prompt = (
        "Write a short, personalised cold-outreach message. It must open with something "
        "specific and true about THIS company (from the research), then connect it to the offer "
        "via one of the pain points. It is a first-touch message, not a hard sell.\n\n"
        "Voice and rules (follow exactly):\n"
        f"- Write as {profile.name}. First person.\n"
        f"- One-line offer: {profile.one_line_offer}\n"
        f"- Tone notes: {profile.tone_notes}\n"
        f"- Credibility you may reference lightly if it helps: {profile.credibility}\n"
        f"- You may include at most one relevant link from:\n{demos}\n"
        "- British English. Short sentences. No em-dashes. No buzzwords. Never say 'built with AI'.\n"
        "- 90-130 words. End with a soft, low-friction ask (a quick call or reply), not pushy.\n"
        f"- Sign off as: {profile.sign_off or profile.name}\n\n"
        f"Recipient: {greeting} at {company.name}\n"
        f"What they do: {research.what_they_do}\n"
        f"Signals: {', '.join(research.signals) or 'none found'}\n"
        f"Pain points to draw on: {'; '.join(pain_points) or 'none'}\n"
        f"The offer: {icp.offer}\n\n"
        "Return a specific subject line and the message body."
    )
    state["draft"] = llm.invoke(prompt, config={"callbacks": get_callbacks(settings)})
    return state


# --- Graph assembly ---------------------------------------------------------


def build_graph():
    """Compile the per-company pipeline: research -> pain_points -> contact -> draft."""
    g = StateGraph(LeadState)
    g.add_node("research", _node_research)
    g.add_node("pain_points", _node_pain_points)
    g.add_node("contact", _node_contact)
    g.add_node("draft", _node_draft)

    g.add_edge(START, "research")
    g.add_edge("research", "pain_points")
    g.add_edge("pain_points", "contact")
    g.add_edge("contact", "draft")
    g.add_edge("draft", END)
    return g.compile()


def research_company(
    company: Company,
    icp: ICP,
    profile: Profile,
    settings: Optional[Settings] = None,
    graph=None,
) -> LeadResult:
    """Run the full pipeline for one company and return a LeadResult.

    Catches errors per company so one bad run never breaks the whole batch.
    """
    settings = settings or load_settings()
    graph = graph or build_graph()
    try:
        final: LeadState = graph.invoke(
            {"icp": icp, "profile": profile, "company": company, "settings": settings}
        )
        return LeadResult(
            company=company,
            research=final["research"],
            pain_points=final.get("pain_points", []),
            contact=final["contact"],
            draft=final["draft"],
        )
    except Exception as exc:  # noqa: BLE001 - surfaced to the UI, not swallowed
        return LeadResult(
            company=company,
            research=Research(what_they_do="(research failed)"),
            pain_points=[],
            contact=Contact(),
            draft=Draft(subject="", message=""),
            error=str(exc),
        )
