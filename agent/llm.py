"""Chat-model factory, Tavily client, and optional Langfuse tracing.

One place to build the LLM so the provider switch (OpenAI vs Azure) lives in a
single spot. Everything else in the codebase just asks for `get_llm()`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, List, Optional

from .config import Settings, load_settings


def get_llm(
    settings: Optional[Settings] = None,
    temperature: Optional[float] = None,
    model: Optional[str] = None,
):
    """Return a LangChain chat model for the configured provider.

    OpenAI by default. Set LLM_PROVIDER=azure in .env to use Azure OpenAI - the
    rest of the code is provider-agnostic because both return a BaseChatModel.

    `model` overrides the model (OpenAI) or the deployment (Azure) - used to run
    the draft step on a stronger model than the structured steps.
    """
    settings = settings or load_settings()
    temp = settings.temperature if temperature is None else temperature

    if settings.provider == "azure":
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            azure_endpoint=settings.azure_endpoint,
            azure_deployment=model or settings.azure_deployment,
            api_version=settings.azure_api_version,
            api_key=settings.azure_api_key,
            temperature=temp,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model or settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=temp,
    )


def get_draft_llm(settings: Optional[Settings] = None):
    """The model for writing outreach drafts - stronger, and a touch warmer.

    Uses OPENAI_DRAFT_MODEL (or AZURE_OPENAI_DRAFT_DEPLOYMENT), falling back to
    the standard model if no separate one is configured.
    """
    settings = settings or load_settings()
    if settings.provider == "azure":
        draft_model = settings.azure_draft_deployment or settings.azure_deployment
    else:
        draft_model = settings.openai_draft_model or settings.openai_model
    return get_llm(settings, temperature=settings.draft_temperature, model=draft_model)


@lru_cache(maxsize=1)
def get_tavily_client(api_key: str):
    """Return a cached Tavily client. Cached on the key so tests can vary it."""
    from tavily import TavilyClient

    return TavilyClient(api_key=api_key)


def get_callbacks(settings: Optional[Settings] = None) -> List[Any]:
    """Return LangChain callbacks. Includes Langfuse only if its keys are set."""
    settings = settings or load_settings()
    if not settings.langfuse_enabled:
        return []
    try:
        from langfuse.callback import CallbackHandler

        return [
            CallbackHandler(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )
        ]
    except Exception:
        # Tracing is best-effort. Never let it break a run.
        return []
