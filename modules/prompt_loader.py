"""Parse agent_use_cases.txt and return prompts for the selected profile."""

import re
from pathlib import Path

from modules.constants import REPORT_DISCLAIMER

REQUIRED_SECTIONS = ["DOC_SYSTEM", "DOC_USER", "MERMAID_SYSTEM", "MERMAID_USER"]
DISCOVERY_SECTIONS = ["BRIEF_SYSTEM", "BRIEF_USER"]

# Profile IDs and their display descriptions for the interactive menu.
PROFILE_DESCRIPTIONS: dict[str, str] = {
    "discovery": "Environment Brief (Phase 1 — auto)",
    "architecture": "General architecture review",
    "bcdr": "Business Continuity & Disaster Recovery",
    "security": "Security posture assessment",
    "observability": "Observability & monitoring assessment",
    "governance": "Governance, compliance & tagging audit",
    "networking": "Network topology & connectivity review",
    "defender": "Defender for Cloud Bonus Report",
}


def get_report_disclaimer() -> str:
    """Return the canonical disclaimer to be included in exported reports."""
    return REPORT_DISCLAIMER


def list_profiles(file_path: Path) -> list[str]:
    """Return all profile IDs found in the use-cases file, in order of first appearance."""
    if not file_path.exists():
        return []
    seen: dict[str, None] = {}
    for line in file_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\[USE_CASE:([^:]+):", line.strip())
        if m:
            pid = m.group(1)
            if pid not in seen:
                seen[pid] = None
    return list(seen.keys())


def load(file_path: Path, profile: str) -> dict[str, str]:
    """Return the four prompt sections for the given use-case profile.

    Keys: doc_system, doc_user, mermaid_system, mermaid_user
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Use-cases file not found: {file_path}")

    sections: dict[str, str] = {}
    current_key: str | None = None
    buffer: list[str] = []
    prefix = f"USE_CASE:{profile}:"

    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        header = re.match(r"^\[(.+)]$", stripped)
        if header:
            if current_key is not None:
                sections[current_key] = "\n".join(buffer).strip()
                buffer.clear()

            tag = header.group(1).strip()
            if tag.startswith(prefix):
                current_key = tag[len(prefix):]
            else:
                current_key = None
            continue

        if current_key is not None:
            buffer.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(buffer).strip()

    for name in REQUIRED_SECTIONS:
        if name not in sections or not sections[name]:
            raise ValueError(
                f"Profile '{profile}' is missing required section [{prefix}{name}] "
                f"in {file_path.name}"
            )

    return {
        "doc_system": sections["DOC_SYSTEM"],
        "doc_user": sections["DOC_USER"],
        "mermaid_system": sections["MERMAID_SYSTEM"],
        "mermaid_user": sections["MERMAID_USER"],
    }


def load_discovery(file_path: Path) -> dict[str, str]:
    """Return the discovery prompt sections (BRIEF_SYSTEM, BRIEF_USER).

    Keys: brief_system, brief_user
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Use-cases file not found: {file_path}")

    sections: dict[str, str] = {}
    current_key: str | None = None
    buffer: list[str] = []
    prefix = "USE_CASE:discovery:"

    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        header = re.match(r"^\[(.+)]$", stripped)
        if header:
            if current_key is not None:
                sections[current_key] = "\n".join(buffer).strip()
                buffer.clear()

            tag = header.group(1).strip()
            if tag.startswith(prefix):
                current_key = tag[len(prefix):]
            else:
                current_key = None
            continue

        if current_key is not None:
            buffer.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(buffer).strip()

    for name in DISCOVERY_SECTIONS:
        if name not in sections or not sections[name]:
            raise ValueError(
                f"Discovery profile is missing required section [{prefix}{name}] "
                f"in {file_path.name}"
            )

    return {
        "brief_system": sections["BRIEF_SYSTEM"],
        "brief_user": sections["BRIEF_USER"],
    }


def render(template: str, inventory_json: str, sampling_context_json: str = "{}") -> str:
    """Replace placeholders with runtime JSON payloads.

    Supported placeholders:
      - {{inventory}}: full or sampled inventory payload
      - {{sampling_context}}: JSON metadata about Phase 2 sampling scope
    """
    return (
        template
        .replace("{{inventory}}", inventory_json)
        .replace("{{sampling_context}}", sampling_context_json)
    )


def render_summary(template: str, summary_json: str) -> str:
    """Replace {{summary}} placeholder with discovery summary JSON."""
    return template.replace("{{summary}}", summary_json)
