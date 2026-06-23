"""Tests for agent.search: hits_to_context and the search() degrade path.

No live Tavily calls: search() is exercised only on its no-key short-circuit,
and hits_to_context is pure.
"""

from __future__ import annotations

from agent.config import Settings
from agent.search import SearchHit, hits_to_context, search


def _hit(i: int, content: str = "some content") -> SearchHit:
    return SearchHit(title=f"Title {i}", url=f"https://example.com/{i}", content=content)


def test_hits_to_context_empty():
    assert hits_to_context([]) == "(no web results found)"


def test_hits_to_context_includes_title_and_url():
    out = hits_to_context([_hit(1)])
    assert "Title 1" in out
    assert "https://example.com/1" in out


def test_hits_to_context_respects_limit():
    hits = [_hit(i) for i in range(10)]
    out = hits_to_context(hits, limit=3)
    # One block per included hit; blocks start with "- ".
    assert out.count("- Title") == 3
    assert "Title 0" in out
    assert "Title 3" not in out


def test_hits_to_context_truncates_long_snippets():
    long_content = "x" * 1000
    out = hits_to_context([_hit(1, content=long_content)])
    # Snippet is capped at 500 chars.
    assert "x" * 500 in out
    assert "x" * 501 not in out


def test_hits_to_context_flattens_newlines():
    out = hits_to_context([_hit(1, content="line one\nline two")])
    assert "line one line two" in out


def test_search_returns_empty_without_key():
    settings = Settings(tavily_api_key="")
    assert search("anything", settings=settings) == []
