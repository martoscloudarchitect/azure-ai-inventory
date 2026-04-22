"""Report & Diagram — AI-generated Markdown report + Mermaid diagram."""

import re

import streamlit as st
import streamlit.components.v1 as components

from streamlit_app.helpers import (
    extract_mermaid_block,
    list_report_files,
    load_markdown,
)

run_dir = st.session_state.get("_run_dir")

st.title("Report & Diagram")

if not run_dir:
    st.info("Select a previous assessment or run a new one from the sidebar to get started.")
    st.stop()

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

# ── Render Markdown + Mermaid ─────────────────────────────────────────────
mermaid_code = extract_mermaid_block(md_content)

if mermaid_code:
    md_text = re.sub(r"```mermaid\s*\n.*?```", "", md_content, flags=re.DOTALL)
    st.markdown(md_text)

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
    st.markdown(md_content)

# ── Download ──────────────────────────────────────────────────────────────
st.divider()
st.download_button(
    "⬇ Download report (.md)",
    data=md_content,
    file_name=report_file.name,
    mime="text/markdown",
)
