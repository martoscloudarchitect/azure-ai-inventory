"""Assemble the final Markdown report from AI-generated content."""

import re
from pathlib import Path


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

    content = f"""{documentation}

---

## Architecture Diagram

{normalized}
"""
    output_file.write_text(content, encoding="utf-8")
    print(f"Documentation saved to: {output_file}")
