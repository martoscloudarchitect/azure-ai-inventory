"""Assemble the final Markdown report from AI-generated content."""

import re
from pathlib import Path

_DISCLAIMER = """\
> **Disclaimer — Proof of Concept · Not for Production Decisions**
>
> This report was generated automatically by **AI Inventory Architect**, an \
open-source scaffold project in **proof-of-concept (POC) stage**. The analysis \
relies on AI-generated interpretations of Azure Resource Graph data and is \
subject to inherent limitations including hard-coded defaults, token limits, \
model reasoning constraints, and incomplete resource visibility.
>
> **This output does not constitute professional advice and must not be used as \
the sole basis for architectural, security, compliance, or financial decisions.** \
No commercial warranty, liability, or accountability is implied.
>
> The value of this tool lies in demonstrating how automated inventory \
collection, structured normalization, and AI-powered analysis can accelerate \
cloud governance workflows. Organizations are encouraged to evaluate this \
scaffold with their internal engineering teams or with a trusted Microsoft \
partner to build a responsible, production-grade solution tailored to their \
Azure environment and its specific requirements.
"""


def _normalize_mermaid(block: str) -> str:
    """Quote Mermaid node and subgraph labels for VS Code Preview compatibility."""
    # Subgraph labels: subgraph ID[label] → subgraph ID["label"]
    block = re.sub(
        r'(?m)^(\s*subgraph\s+[A-Za-z0-9_]+)\[(.+?)]\s*$',
        lambda m: '{}["{}"]'.format(m.group(1), m.group(2).replace('"', '&quot;')),
        block,
    )
    # Node labels: ID[label] → ID["label"]
    block = re.sub(
        r'(?m)^(\s*[A-Za-z0-9_]+)\[(.+?)]\s*$',
        lambda m: '{}["{}"]'.format(m.group(1), m.group(2).replace('"', '&quot;')),
        block,
    )
    return block


def save(documentation: str, diagram: str, output_file: Path) -> None:
    """Combine documentation and Mermaid diagram into a single Markdown file."""
    normalized = _normalize_mermaid(diagram)

    # Ensure the disclaimer is present even if the model omitted it.
    if "Proof of Concept" not in documentation:
        documentation = _DISCLAIMER + "\n" + documentation

    content = f"""{documentation}

---

## Architecture Diagram

{normalized}
"""
    output_file.write_text(content, encoding="utf-8")
    print(f"Documentation saved to: {output_file}")
