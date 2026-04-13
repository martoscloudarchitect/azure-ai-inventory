"""Parse agent_use_cases.txt and return prompts for the selected profile."""

import re
from pathlib import Path

REQUIRED_SECTIONS = ["DOC_SYSTEM", "DOC_USER", "MERMAID_SYSTEM", "MERMAID_USER"]

# Profile IDs and their display descriptions for the interactive menu.
PROFILE_DESCRIPTIONS: dict[str, str] = {
    "architecture": "General architecture review",
    "bcdr": "Business Continuity & Disaster Recovery",
    "security": "Security posture assessment",
    "cost": "Cost optimization & right-sizing",
    "governance": "Governance, compliance & tagging audit",
    "networking": "Network topology & connectivity review",
}


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


def render(template: str, inventory_json: str) -> str:
    """Replace {{inventory}} placeholder with actual inventory JSON."""
    return template.replace("{{inventory}}", inventory_json)
