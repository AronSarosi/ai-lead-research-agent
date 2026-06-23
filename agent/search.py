"""Thin Tavily search wrappers.

We keep these tiny and defensive: if no key is set, or a call fails, we return
an empty result rather than raising. The agent then degrades gracefully (the
LLM still drafts from the ICP, just with less specific detail).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .config import Settings, load_settings
from .llm import get_tavily_client


@dataclass
class SearchHit:
    title: str
    url: str
    content: str


def search(query: str, max_results: int = 5, settings: Optional[Settings] = None) -> List[SearchHit]:
    """Run a Tavily search and return a list of hits. Empty list on any failure."""
    settings = settings or load_settings()
    if not settings.search_enabled:
        return []
    try:
        client = get_tavily_client(settings.tavily_api_key)
        resp = client.search(query=query, max_results=max_results, search_depth="basic")
    except Exception:
        return []

    hits: List[SearchHit] = []
    for item in resp.get("results", []):
        hits.append(
            SearchHit(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", ""),
            )
        )
    return hits


def hits_to_context(hits: List[SearchHit], limit: int = 5) -> str:
    """Flatten search hits into a compact text block for an LLM prompt."""
    if not hits:
        return "(no web results found)"
    blocks = []
    for h in hits[:limit]:
        snippet = h.content.strip().replace("\n", " ")
        blocks.append(f"- {h.title} ({h.url})\n  {snippet[:500]}")
    return "\n".join(blocks)
