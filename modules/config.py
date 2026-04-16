"""Load and validate configuration from the .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv


def _get_optional_int(name: str) -> int | None:
    """Return a positive int from an env var, or None if unset."""
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    value = int(raw)
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer. Got: '{raw}'")
    return value


def load(project_dir: Path) -> dict:
    """Return a validated config dict from the .env file."""
    env_file = project_dir / ".env"
    if not env_file.exists():
        raise FileNotFoundError(f"The .env file was not found at: {env_file}")
    load_dotenv(env_file)

    tenant_id = os.environ.get("AZURE_TENANT_ID", "").strip()
    if not tenant_id:
        raise RuntimeError("Set AZURE_TENANT_ID in the .env file before running the script.")

    cfg: dict = {"tenant_id": tenant_id}

    # Azure OpenAI settings (optional — AI features are skipped when absent).
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip()

    if endpoint and api_key:
        cfg["openai_endpoint"] = endpoint
        cfg["openai_api_key"] = api_key
        cfg["openai_deployment"] = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini").strip()

        # Token limits — all .env-driven with sensible defaults.
        cfg["brief_max_tokens"] = _get_optional_int("AZURE_OPENAI_BRIEF_MAX_COMPLETION_TOKENS") or 2000
        cfg["doc_max_tokens"] = _get_optional_int("AZURE_OPENAI_DOC_MAX_COMPLETION_TOKENS") or 25000
        cfg["mermaid_max_tokens"] = _get_optional_int("AZURE_OPENAI_MERMAID_MAX_COMPLETION_TOKENS") or 8000

    cfg["prompt_profile"] = os.environ.get("PROMPT_PROFILE", "architecture").strip()

    # Resource Graph page size (default 500, max 1000 enforced by Azure).
    cfg["page_size"] = _get_optional_int("RESOURCE_GRAPH_PAGE_SIZE") or 500

    return cfg
