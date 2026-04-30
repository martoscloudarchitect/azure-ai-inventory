"""Assemble the final Markdown report from AI-generated content."""

import re
from pathlib import Path

from modules.constants import REPORT_DISCLAIMER


def _ensure_mermaid_fence(block: str) -> str:
    """Ensure the Mermaid block has opening and closing code fences.
    
    Fallback wrapper for cases where the LLM returns bare diagram code without
    the ```mermaid and ``` markers. This prevents silent diagram failures.
    """
    block = block.strip()
    
    # Check if already has opening fence
    if block.startswith("```mermaid"):
        return block
    
    # If block starts with a diagram type (flowchart, graph, stateDiagram, etc.),
    # wrap it in fences
    if re.match(r"^(flowchart|graph|stateDiagram|sequenceDiagram|classDiagram|erDiagram)", block):
        return f"```mermaid\n{block}\n```"
    
    return block


def _normalize_line_breaks_in_labels(block: str) -> str:
    """Convert \\n inside label strings to <br> for cross-platform portability.
    
    Mermaid supports both \\n and <br> but <br> is more portable across 
    different renderers and viewers outside the Streamlit app context.
    """
    # Replace \n with <br> inside double-quoted labels: ["...text\nmore..."]
    def replace_in_label(match):
        label = match.group(1)
        label = label.replace("\\n", "<br>")
        return f'["{label}"]'
    
    block = re.sub(r'\["(.*?)"\]', replace_in_label, block, flags=re.DOTALL)
    return block


def _normalize_mermaid(block: str) -> str:
    """Fix common LLM-generated Mermaid syntax issues for portability and compatibility.
    
    This function:
    1. Ensures the block has ```mermaid opening and closing fences (fallback wrapper)
    2. Converts \\n in labels to <br> for cross-platform portability
    3. Quotes node and subgraph labels for VS Code Preview compatibility
    """
    # Step 1: Ensure code fences are present (fallback for LLM omission)
    block = _ensure_mermaid_fence(block)
    
    # Step 2: Normalize line breaks inside labels for portability
    block = _normalize_line_breaks_in_labels(block)
    
    # Step 3: Original label quoting logic for VS Code
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


def _sampling_notice(sampling_info: dict | None) -> str:
    """Return a deterministic sampling notice block for Phase 2 reports."""
    if not sampling_info or not sampling_info.get("sampled"):
        return ""

    original = sampling_info.get("original_count", "unknown")
    sampled = sampling_info.get("sampled_count", "unknown")
    reduction = sampling_info.get("reduction_percentage", "unknown")
    ceiling = sampling_info.get("max_input_tokens", "unknown")
    target = sampling_info.get("target_percentage")
    target_text = "unknown"
    if isinstance(target, (int, float)):
        target_text = f"{target * 100:.0f}%"

    return (
        "## Sampling & Confidence Notice\n\n"
        "This is a **Phase 2 deep-dive assessment generated from a sampled inventory** "
        f"to remain within the configured input token ceiling (**{ceiling}** tokens).\n\n"
        f"- Original resources discovered: **{original}**\n"
        f"- Resources analyzed in this report: **{sampled}**\n"
        f"- Reduction applied: **{reduction}%** (target keep-rate: **{target_text}**)\n"
        "- Critical resource types are preserved by design, but findings and recommendations "
        "should be treated as **directional, not exhaustive** for non-critical resources.\n"
    )


def _build_confidence_score_box(sampling_info: dict | None) -> str:
    """Return a compact confidence box and uplift conditions for report top."""
    sampled = bool(sampling_info and sampling_info.get("sampled"))
    reduction = 0.0
    if sampling_info:
        reduction = float(sampling_info.get("reduction_percentage", 0) or 0)

    # Conservative POC-scoped heuristic.
    score = 0.62
    reason = "POC baseline with full discovered inventory scope for this run."

    if sampled:
        if reduction >= 40:
            score = 0.46
            reason = "POC assessment with aggressive sampling; findings are directional."
        elif reduction >= 20:
            score = 0.52
            reason = "POC assessment with moderate sampling; non-critical coverage is partial."
        else:
            score = 0.57
            reason = "POC assessment with light sampling; coverage is good but not exhaustive."

    score = max(0.0, min(0.95, score))
    score_pct = score * 100

    return (
        "## Confidence Score\n\n"
        f"> **Score:** {score_pct:.1f}%\n"
        f"> **Summary:** {reason}\n\n"
        "### Conditions to Increase Confidence\n"
        "- Validate top findings with live Azure-native controls (Policy/Defender/Monitor) and evidence links.\n"
        "- Ensure complete RBAC visibility across all target subscriptions and critical resource groups.\n"
        "- Reduce or eliminate sampling for high-impact scopes and re-run profile-specific assessments.\n"
        "- Corroborate recommendations across repeated runs and change windows to confirm consistency.\n"
    )


def save(
    documentation: str,
    diagram: str,
    output_file: Path,
    sampling_info: dict | None = None,
) -> None:
    """Combine documentation and Mermaid diagram into a single Markdown file."""
    normalized = _normalize_mermaid(diagram)

    # Ensure the disclaimer is present even if the model omitted it.
    if "Proof of Concept" not in documentation:
        documentation = REPORT_DISCLAIMER + "\n" + documentation

    notice = _sampling_notice(sampling_info)
    confidence_box = _build_confidence_score_box(sampling_info)

    # Ensure confidence section exists once at top of report body.
    if "## Confidence Score" not in documentation:
        documentation = f"{confidence_box}\n\n{documentation}"

    if notice:
        documentation = f"{documentation}\n\n---\n\n{notice}"

    content = f"""{documentation}

---

## Architecture Diagram

{normalized}
"""
    output_file.write_text(content, encoding="utf-8")
    print(f"Documentation saved to: {output_file}")
