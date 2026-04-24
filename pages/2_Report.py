"""Report & Diagram — AI-generated Markdown report + Mermaid diagram."""

import re

import streamlit as st
import streamlit.components.v1 as components

from streamlit_app.helpers import (
    extract_mermaid_block,
    list_report_files,
    load_markdown,
    get_inventory_size,
    display_disclaimer,
    display_scaling_warning,
    load_json,
)

run_dir = st.session_state.get("_run_dir")

st.title("Report & Diagram")

if not run_dir:
    st.info("Select a previous assessment or run a new one from the sidebar to get started.")
    st.stop()

# ── Disclaimer ────────────────────────────────────────────────────────────
display_disclaimer()

# ── Scaling warning ───────────────────────────────────────────────────────
inventory_count = get_inventory_size(run_dir)
display_scaling_warning(inventory_count)

# ── Token usage (if available) ────────────────────────────────────────────
metadata = load_json(run_dir / "run_metadata.json")
if isinstance(metadata, dict) and "token_usage" in metadata:
    tokens = metadata["token_usage"]
    if isinstance(tokens, dict):
        cols = st.columns(len(tokens))
        for i, (key, val) in enumerate(tokens.items()):
            if isinstance(val, dict):
                cols[i].metric(key.replace("_", " ").title(), f"{val.get('total_tokens', '—')} tokens")

st.divider()

# ── Auto-detect report ────────────────────────────────────────────────────
reports = list_report_files(run_dir)
if not reports:
    st.info("No report files found for this run.")
    st.stop()

report_file = reports[0]
profile_name = report_file.stem

md_content = load_markdown(report_file)
if not md_content:
    st.error(f"Could not read {report_file.name}.")
    st.stop()

st.subheader(f"{profile_name.replace('_', ' ').title()} Report")


def _extract_assessment_score_data(report_markdown: str) -> tuple[float | None, list[dict]]:
    """Parse assessment score and remediation uplift rows from markdown.

    Expected signals (prompt-enforced):
    - Current Assessment Score: <number>%
    - Table under 'Prioritized Remediation Value Uplift' with '+<number>' uplifts.
    """
    score_match = re.search(
        r"Current Assessment Score:\*\*\s*([0-9]+(?:\.[0-9]+)?)%",
        report_markdown,
        flags=re.IGNORECASE,
    )
    current_score = float(score_match.group(1)) if score_match else None

    uplift_rows: list[dict] = []
    for line in report_markdown.splitlines():
        if not line.strip().startswith("|"):
            continue
        if "Priority" in line and "Estimated Uplift" in line:
            continue
        if "---" in line:
            continue

        table_cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(table_cols) < 3:
            continue

        priority = table_cols[0]
        remediation = table_cols[1]
        uplift_text = table_cols[2]

        if not re.match(r"^P\d+$", priority, flags=re.IGNORECASE):
            continue

        uplift_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", uplift_text)
        if not uplift_match:
            continue

        uplift_rows.append({
            "priority": priority.upper(),
            "remediation": remediation,
            "uplift": float(uplift_match.group(1)),
        })

    return current_score, uplift_rows


def _render_assessment_score_chart(current_score: float, uplift_rows: list[dict]) -> None:
    """Render assessment score pie chart and remediation contribution table."""
    if current_score < 0 or current_score > 100:
        return

    # Build pie slices: baseline score + each uplift (capped) + remaining gap.
    slices: list[dict] = []
    slices.append({"segment": "Current Score", "value": current_score})

    running = current_score
    contribution_rows: list[dict] = []
    for row in uplift_rows:
        if running >= 100:
            break
        raw_uplift = max(0.0, row["uplift"])
        effective_uplift = min(raw_uplift, 100 - running)
        running += effective_uplift
        slices.append({"segment": f"{row['priority']} uplift", "value": effective_uplift})

        contribution_rows.append({
            "Priority": row["priority"],
            "Remediation": row["remediation"],
            "Estimated Uplift (%)": round(raw_uplift, 2),
            "Effective Contribution (%)": round(effective_uplift, 2),
        })

    remaining_gap = max(0.0, 100 - running)
    if remaining_gap > 0:
        slices.append({"segment": "Remaining Gap", "value": remaining_gap})

    st.divider()
    st.subheader("Assessment Score Visualization")
    st.caption(
        "This chart reflects the profile/use-case assessment posture score and remediation uplift contribution. "
        "It is distinct from the LLM Confidence Score."
    )

    st.vega_lite_chart(
        {
            "data": {"values": slices},
            "mark": {"type": "arc", "innerRadius": 70},
            "encoding": {
                "theta": {"field": "value", "type": "quantitative"},
                "color": {"field": "segment", "type": "nominal"},
                "tooltip": [
                    {"field": "segment", "type": "nominal"},
                    {"field": "value", "type": "quantitative", "format": ".2f"},
                ],
            },
            "width": 460,
            "height": 320,
            "title": "Assessment Score Toward 100%",
        },
        use_container_width=True,
    )

    c1, c2 = st.columns(2)
    c1.metric("Current Score", f"{current_score:.1f}%")
    c2.metric("Projected Score (Capped)", f"{running:.1f}%")

    # Explicit percentage view for each pie segment.
    pct_rows = [
        {
            "Segment": s["segment"],
            "Percentage (%)": round(float(s["value"]), 2),
        }
        for s in slices
    ]
    st.dataframe(pct_rows, use_container_width=True, hide_index=True)

    if contribution_rows:
        st.dataframe(contribution_rows, use_container_width=True, hide_index=True)


def _split_after_executive_summary(report_markdown: str) -> tuple[str, str, str]:
    """Split markdown into (before summary, summary block, after summary)."""
    heading_match = re.search(
        r"(?im)^\s*(#{1,2})\s*Executive Summary\s*$",
        report_markdown,
    )
    if not heading_match:
        return report_markdown, "", ""

    start = heading_match.start()
    summary_start = heading_match.start()
    summary_end_search = re.search(
        r"(?im)^\s*#{1,2}\s+.+$",
        report_markdown[heading_match.end():],
    )

    if summary_end_search:
        summary_end = heading_match.end() + summary_end_search.start()
        return (
            report_markdown[:start],
            report_markdown[summary_start:summary_end],
            report_markdown[summary_end:],
        )

    return report_markdown[:start], report_markdown[summary_start:], ""


def _strip_duplicate_disclaimer(report_markdown: str) -> str:
    """Remove leading disclaimer blocks from report markdown for UI rendering.

    The page already displays the canonical disclaimer banner at the top, so we
    hide duplicated disclaimer text that may come from the generated report.
    """
    # Blockquote-form disclaimer (canonical markdown style).
    report_markdown = re.sub(
        r"(?s)^\s*> \*\*Disclaimer — Proof of Concept · Not for Production Decisions\*\*.*?(?=\n## |\n# |\Z)",
        "",
        report_markdown,
        count=1,
    )

    # Plain-text disclaimer heading (some model outputs).
    report_markdown = re.sub(
        r"(?s)^\s*Disclaimer — Proof of Concept · Not for Production Decisions.*?(?=\n## |\n# |\Z)",
        "",
        report_markdown,
        count=1,
    )

    return report_markdown.lstrip()


md_content = _strip_duplicate_disclaimer(md_content)

# ── Render Markdown + Mermaid ─────────────────────────────────────────────
mermaid_code = extract_mermaid_block(md_content)

if mermaid_code:
    md_text = re.sub(r"```mermaid\s*\n.*?```", "", md_content, flags=re.DOTALL)

    # Place Assessment Score visualization right after Executive Summary.
    assessment_score, assessment_uplifts = _extract_assessment_score_data(md_text)
    before_summary, summary_block, after_summary = _split_after_executive_summary(md_text)

    if before_summary.strip():
        st.markdown(before_summary)

    if summary_block.strip():
        st.markdown(summary_block)
        if assessment_score is not None:
            _render_assessment_score_chart(assessment_score, assessment_uplifts)
        if after_summary.strip():
            st.markdown(after_summary)
    else:
        st.markdown(md_text)
        if assessment_score is not None:
            _render_assessment_score_chart(assessment_score, assessment_uplifts)

    st.divider()
    st.subheader("Architecture Diagram")

    mermaid_html = f"""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
        <script>mermaid.initialize({{startOnLoad: true, theme: 'neutral'}});</script>
        <style>
            body {{ margin: 0; padding: 16px; background: white; }}
            .mermaid {{ text-align: center; }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{mermaid_code}
        </div>
    </body>
    </html>
    """
    components.html(mermaid_html, height=600, scrolling=True)
else:
    assessment_score, assessment_uplifts = _extract_assessment_score_data(md_content)
    before_summary, summary_block, after_summary = _split_after_executive_summary(md_content)

    if summary_block.strip():
        if before_summary.strip():
            st.markdown(before_summary)
        st.markdown(summary_block)
        if assessment_score is not None:
            _render_assessment_score_chart(assessment_score, assessment_uplifts)
        if after_summary.strip():
            st.markdown(after_summary)
    else:
        st.markdown(md_content)
        if assessment_score is not None:
            _render_assessment_score_chart(assessment_score, assessment_uplifts)

# ── Download ──────────────────────────────────────────────────────────────
st.divider()
st.download_button(
    "⬇ Download report (.md)",
    data=md_content,
    file_name=report_file.name,
    mime="text/markdown",
)
