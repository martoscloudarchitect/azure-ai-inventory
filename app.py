"""AI Inventory Architect — Streamlit Dashboard (Router).

Launch with:  streamlit run app.py
"""

import streamlit as st

from streamlit_app.helpers import render_sidebar

st.set_page_config(
    page_title="AzurePrism",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Define pages ──────────────────────────────────────────────────────────
welcome   = st.Page("pages/welcome.py",     title="Welcome",   icon="👋", default=True)
overview  = st.Page("pages/0_Overview.py",  title="Overview",  icon="📊")
inventory = st.Page("pages/1_Inventory.py", title="Inventory", icon="📦")
report    = st.Page("pages/2_Report.py",    title="Report",    icon="📄")
topology  = st.Page("pages/4_Topology.py",  title="Topology",  icon="🔗")
analytics = st.Page("pages/3_Insights.py",  title="Analytics",  icon="📈")
query_specs = st.Page("pages/5_Query_Specs.py", title="Query_Specs", icon="📚")

all_pages = [welcome, overview, inventory, report, topology, analytics, query_specs]

# ── Sidebar: assessment selection, page links, new assessment ─────────────
run_dir = render_sidebar(all_pages)
st.session_state["_run_dir"] = run_dir

# ── Navigation ────────────────────────────────────────────────────────────
if run_dir:
    pg = st.navigation(all_pages, position="hidden")
else:
    pg = st.navigation([welcome], position="hidden")

pg.run()
