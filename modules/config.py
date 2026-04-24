"""Load and validate configuration from the .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cognitive Services token scope used by keyless (Entra ID) authentication.
_COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"


def _get_optional_int(name: str) -> int | None:
    """Return a positive int from an env var, or None if unset."""
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    value = int(raw)
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer. Got: '{raw}'")
    return value


def _build_openai_client(endpoint: str, api_version: str, *, api_key: str | None = None):
    """Create an ``AzureOpenAI`` client with either key or keyless auth."""
    from openai import AzureOpenAI

    if api_key:
        return AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )

    # Keyless auth via DefaultAzureCredential
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    except ImportError as exc:
        raise RuntimeError(
            "Keyless Azure OpenAI authentication requires the 'azure-identity' package.\n"
            "Install it with:  pip install azure-identity\n"
            "Or provide AZURE_OPENAI_API_KEY in the .env file to use key-based auth."
        ) from exc

    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, _COGNITIVE_SCOPE)
    return AzureOpenAI(
        azure_ad_token_provider=token_provider,
        api_version=api_version,
        azure_endpoint=endpoint,
    )


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

    # AI is enabled when the endpoint is set.
    # Auth mode: API key when provided, otherwise keyless via DefaultAzureCredential.
    if endpoint:
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview").strip()
        cfg["openai_endpoint"] = endpoint
        cfg["openai_api_version"] = api_version
        cfg["openai_deployment"] = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini").strip()

        if api_key:
            cfg["openai_auth_mode"] = "key"
            cfg["openai_client"] = _build_openai_client(endpoint, api_version, api_key=api_key)
        else:
            cfg["openai_auth_mode"] = "identity"
            cfg["openai_client"] = _build_openai_client(endpoint, api_version)

        # Token limits — all .env-driven with sensible defaults.
        cfg["brief_max_tokens"] = _get_optional_int("AZURE_OPENAI_BRIEF_MAX_COMPLETION_TOKENS") or 2000
        cfg["doc_max_tokens"] = _get_optional_int("AZURE_OPENAI_DOC_MAX_COMPLETION_TOKENS") or 25000
        cfg["mermaid_max_tokens"] = _get_optional_int("AZURE_OPENAI_MERMAID_MAX_COMPLETION_TOKENS") or 8000
        cfg["max_input_tokens"] = _get_optional_int("AZURE_OPENAI_MAX_INPUT_TOKENS") or 272000

    cfg["prompt_profile"] = os.environ.get("PROMPT_PROFILE", "architecture").strip()

    # Resource Graph page size (default 500, max 1000 enforced by Azure).
    cfg["page_size"] = _get_optional_int("RESOURCE_GRAPH_PAGE_SIZE") or 500

    return cfg
