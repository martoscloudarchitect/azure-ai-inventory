"""AI Inventory Architect — Streamlit Dashboard (Overview).

Launch with:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from streamlit_app.helpers import load_json, load_markdown, render_sidebar

st.set_page_config(
    page_title="AI Inventory Architect",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

run_dir = render_sidebar()

# ── Header ───────────────────────────────────────────────────────────────
st.title("AI Inventory Architect")
st.caption("Azure infrastructure inventory & AI-powered documentation")

if not run_dir:
    st.info("Run an assessment from the sidebar to get started.")
    st.stop()

# ── Discovery summary ────────────────────────────────────────────────────
summary = load_json(run_dir / "discovery_summary.json")

if not summary:
    st.warning("No discovery summary found for this run.")
    st.stop()

# KPI cards
totals = summary.get("totals", [{}])[0] if summary.get("totals") else {}
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Resources", totals.get("resource_count", "—"))
c2.metric("Subscriptions", totals.get("subscription_count", "—"))
c3.metric("Resource Groups", totals.get("resource_group_count", "—"))
c4.metric("Regions", totals.get("region_count", "—"))

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────
tab_type, tab_region, tab_rg, tab_sku, tab_state = st.tabs(
    ["By Type", "By Region", "By Resource Group", "By SKU", "By Provisioning State"]
)

with tab_type:
    data = summary.get("by_type", [])
    if data:
        df = pd.DataFrame(data).rename(columns={"count_": "Count", "type": "Resource Type"})
        st.bar_chart(df, x="Resource Type", y="Count", horizontal=True)
    else:
        st.info("No type data.")

with tab_region:
    data = summary.get("by_region", [])
    if data:
        df = pd.DataFrame(data).rename(columns={"count_": "Count", "location": "Region"})
        st.bar_chart(df, x="Region", y="Count")
    else:
        st.info("No region data.")

with tab_rg:
    data = summary.get("by_resource_group", [])
    if data:
        df = pd.DataFrame(data).rename(
            columns={"count_": "Count", "resourceGroup": "Resource Group"}
        )
        st.bar_chart(df, x="Resource Group", y="Count")
    else:
        st.info("No resource group data.")

with tab_sku:
    data = summary.get("by_sku", [])
    if data:
        df = pd.DataFrame(data).rename(
            columns={"count_": "Count", "sku_name": "SKU", "type": "Resource Type"}
        )
        df["Label"] = df["SKU"] + " (" + df["Resource Type"].str.split("/").str[-1] + ")"
        st.bar_chart(df, x="Label", y="Count")
    else:
        st.info("No SKU data.")

with tab_state:
    data = summary.get("by_provisioning_state", [])
    if data:
        df = pd.DataFrame(data).rename(
            columns={"count_": "Count", "provisioningState": "State"}
        )
        df["State"] = df["State"].replace("", "(empty)")
        st.bar_chart(df, x="State", y="Count")
    else:
        st.info("No provisioning state data.")

# ── AI-generated brief ────────────────────────────────────────────────────
st.divider()
st.header("AI-Generated Environment Brief")

brief = load_markdown(run_dir / "discovery.md")
if brief:
    st.markdown(brief)
else:
    st.info("No discovery.md found for this run.")
