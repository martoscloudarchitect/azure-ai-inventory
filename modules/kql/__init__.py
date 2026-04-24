"""KQL query registry — selects queries based on the active use-case profile."""

import importlib

from modules.kql import base, discovery

# Maps profile names to their module paths.
_PROFILE_MODULES: dict[str, str] = {
    "architecture": "modules.kql.architecture",
    "bcdr": "modules.kql.bcdr",
    "security": "modules.kql.security",
    "observability": "modules.kql.observability",
    "governance": "modules.kql.governance",
    "networking": "modules.kql.networking",
    "defender": "modules.kql.defender",
}


def get_base_query() -> str:
    """Return the base Resource Graph query shared by all profiles."""
    return base.QUERY


def get_discovery_queries() -> list[dict]:
    """Return the lightweight summary queries used by Phase 1 discovery."""
    return discovery.SUMMARY_QUERIES


def get_supplementary_queries(profile: str) -> list[dict]:
    """Return supplementary KQL queries for the given use-case profile.

    Each entry is a dict with keys: key, table, query.
    Returns an empty list for unknown profiles or profiles with no extras.
    """
    mod_path = _PROFILE_MODULES.get(profile)
    if not mod_path:
        return []
    mod = importlib.import_module(mod_path)
    return getattr(mod, "SUPPLEMENTARY_QUERIES", [])
