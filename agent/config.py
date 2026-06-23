"""Configuration: load .env and profile.yaml, expose typed settings.

Everything that varies between environments (keys, model, provider) comes from
.env. Everything that personalises the drafts comes from profile.yaml. Keeping
those two apart means you can edit your voice without touching secrets.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

from .schemas import Profile

# Project root = the folder that contains this package.
ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT / "profile.yaml"
SAMPLE_ICP_PATH = ROOT / "sample_icp.yaml"

# Load .env once, on import. Safe to call repeatedly.
load_dotenv(ROOT / ".env")


@dataclass
class Settings:
    """Runtime settings derived from the environment."""

    provider: str = "openai"  # 'openai' or 'azure'
    openai_api_key: str = ""
    # Cheap, fast model for the structured research steps.
    openai_model: str = "gpt-4o-mini"
    # Stronger model just for writing the outreach draft (the bit that must not
    # sound generic). Falls back to openai_model if left blank.
    openai_draft_model: str = "gpt-4o"

    azure_api_key: str = ""
    azure_endpoint: str = ""
    azure_deployment: str = ""
    # Optional separate Azure deployment for the draft step (falls back to the main one).
    azure_draft_deployment: str = ""
    azure_api_version: str = "2024-08-01-preview"

    tavily_api_key: str = ""

    # Langfuse tracing is opt-in: only active when both keys are present.
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # Structured steps run cool for consistency; the draft runs a little warmer.
    temperature: float = 0.4
    draft_temperature: float = 0.6

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)

    @property
    def search_enabled(self) -> bool:
        return bool(self.tavily_api_key)

    def validate(self) -> list[str]:
        """Return a list of human-readable problems, empty if good to go."""
        problems: list[str] = []
        if self.provider == "openai" and not self.openai_api_key:
            problems.append("OPENAI_API_KEY is not set (.env).")
        if self.provider == "azure" and not (self.azure_api_key and self.azure_endpoint and self.azure_deployment):
            problems.append("Azure provider selected but AZURE_OPENAI_* vars are incomplete (.env).")
        if not self.tavily_api_key:
            problems.append("TAVILY_API_KEY is not set (.env) - web research will be skipped.")
        return problems


def load_settings() -> Settings:
    """Build Settings from environment variables."""
    return Settings(
        provider=os.getenv("LLM_PROVIDER", "openai").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_draft_model=os.getenv("OPENAI_DRAFT_MODEL", "gpt-4o"),
        azure_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", ""),
        azure_draft_deployment=os.getenv("AZURE_OPENAI_DRAFT_DEPLOYMENT", ""),
        azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        langfuse_host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.4")),
        draft_temperature=float(os.getenv("LLM_DRAFT_TEMPERATURE", "0.6")),
    )


def load_profile(path: Optional[Path] = None) -> Profile:
    """Load profile.yaml into a Profile model. Falls back to a minimal default."""
    path = path or PROFILE_PATH
    if not path.exists():
        return Profile(name="Me")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Profile(**data)


def load_sample_icp() -> dict:
    """Load sample_icp.yaml as a plain dict for pre-filling the UI form."""
    if not SAMPLE_ICP_PATH.exists():
        return {}
    return yaml.safe_load(SAMPLE_ICP_PATH.read_text(encoding="utf-8")) or {}
