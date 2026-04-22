"""Welcome — Landing page for first-time and returning users."""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

_IMAGES_DIR = Path(__file__).resolve().parent.parent / "Images"

st.title("Welcome to AzurePrism")
st.markdown("#### *One beam in, full spectrum out.*")

st.markdown(
    """
    Point **AzurePrism** at your Azure environment and watch a single beam of
    discovery refract into a **full spectrum** of insights — architecture,
    security, BCDR, observability, governance, and networking — each rendered as
    AI-powered documentation, inventory exports, and architecture diagrams,
    all for **less than a penny per assessment** on Azure OpenAI.
    Whether this is your first run or you're revisiting with a new use case,
    simply pick a profile and let the AI do the heavy lifting.
    """
)

_left, _center, _right = st.columns([1, 2, 1])
with _center:
    st.image(str(_IMAGES_DIR / "AzurePrism.png"))

# ── Architecture Flow Diagram ─────────────────────────────────────────────
st.subheader("How It Works")

_MERMAID = """\
flowchart LR
    A["<b>Azure Environment</b><br>Subscriptions &amp; Resources"]
    B["<b>Resource Graph</b><br>KQL Discovery Queries"]
    C["<b>AI Engine</b><br>Azure OpenAI (GPT)"]
    D["<b>Inventory</b><br>CSV &amp; JSON Export"]
    E["<b>AI Report</b><br>Documentation &amp; Diagrams"]
    F["<b>Interactive Dashboard</b><br>Insights &amp; Analytics"]

    A --> B --> C
    C --> D
    C --> E
    D --> F
    E --> F

    classDef azure fill:#0078D4,stroke:#005A9E,color:#fff,stroke-width:2px,rx:12,ry:12
    classDef ai fill:#6B2FA0,stroke:#4B1F70,color:#fff,stroke-width:2px,rx:12,ry:12
    classDef output fill:#107C10,stroke:#0B5E0B,color:#fff,stroke-width:2px,rx:12,ry:12
    classDef dash fill:#D83B01,stroke:#A12D00,color:#fff,stroke-width:2px,rx:12,ry:12

    class A,B azure
    class C ai
    class D,E output
    class F dash
"""

_MERMAID_HTML = f"""
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad: true, theme: 'base',
        themeVariables: {{fontSize: '14px', fontFamily: 'Segoe UI, sans-serif'}}}});</script>
    <style>
        body {{ margin: 0; padding: 24px 16px; background: transparent; }}
        .mermaid {{ text-align: center; }}
    </style>
</head>
<body>
    <div class="mermaid">
{_MERMAID}
    </div>
</body>
</html>
"""

components.html(_MERMAID_HTML, height=260, scrolling=False)

col1, col2, col3, col4 = st.columns(4)
col1.markdown("🔵 **Azure Platform**\nResource Graph queries across all subscriptions")
col2.markdown("🟣 **AI Engine**\nGPT-powered analysis & documentation generation")
col3.markdown("🟢 **Structured Output**\nInventory CSV/JSON + Markdown reports & diagrams")
col4.markdown("🟠 **Dashboard**\nInteractive exploration, cost estimates & run analytics")

st.divider()

st.markdown(
    """
    ### Get Started

    Use the **▶ New Assessment** section in the sidebar to launch your first
    assessment, or select a **Previous Assessment** to review existing results.
    """
)
