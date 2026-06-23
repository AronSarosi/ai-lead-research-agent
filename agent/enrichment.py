"""Contact enrichment - clean stub for a future paid API.

v1 finds contacts only from free web search + LLM inference (see graph.py's
contact node, `_node_contact`). That gives you a likely name/role, not a
verified email.

When you want real, verified contacts later (Apollo, Hunter, Clearbit, etc.),
implement `enrich_contact` below. The contact node already calls it first and
falls back to inference when it returns None, so this is the only seam to touch.

Deliberately out of scope for v1 - this returns None today.
"""

from __future__ import annotations

from typing import Optional

from .schemas import Company, Contact


def enrich_contact(company: Company, role_hint: str = "") -> Optional[Contact]:
    """Look up a verified decision-maker for a company via a paid enrichment API.

    Args:
        company:   the company we want a contact for.
        role_hint: the target role, e.g. 'Head of Marketing'.

    Returns:
        A Contact with confidence='found' (ideally including a real email once
        you extend the Contact schema), or None if not implemented / no match.

    TODO (later): call your enrichment provider here. Read its key from
    config.Settings (add e.g. APOLLO_API_KEY), map the response onto Contact,
    and set confidence='found'.
    """
    return None
