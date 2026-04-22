"""Inventory Explorer — interactive CSV table with filters and charts."""

import pandas as pd
import streamlit as st

run_dir = st.session_state.get("_run_dir")

st.title("Inventory Explorer")

if not run_dir:
    st.info("Select a previous assessment or run a new one from the sidebar to get started.")
    st.stop()

csv_file = run_dir / "inventory.csv"
if not csv_file.is_file():
    st.info("No inventory.csv found for this run.")
    st.stop()

df = pd.read_csv(csv_file)

# ── Sidebar filters (below the shared sidebar content) ───────────────────
st.sidebar.divider()
st.sidebar.header("🔍 Filters")

filter_cols = [
    ("service_category", "Service Category"),
    ("location", "Location"),
    ("resource_group", "Resource Group"),
    ("provisioning_state", "Provisioning State"),
    ("iac_hint", "IaC Hint"),
]

active_filters: dict[str, list[str]] = {}
for col, label in filter_cols:
    if col in df.columns:
        options = sorted(df[col].dropna().unique().tolist())
        selected = st.sidebar.multiselect(label, options, default=[])
        if selected:
            active_filters[col] = selected

filtered = df.copy()
for col, values in active_filters.items():
    filtered = filtered[filtered[col].isin(values)]

# ── KPI row ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Resources", len(filtered))
c2.metric(
    "Service Categories",
    filtered["service_category"].nunique() if "service_category" in filtered.columns else "—",
)
c3.metric(
    "Locations",
    filtered["location"].nunique() if "location" in filtered.columns else "—",
)
c4.metric(
    "Resource Groups",
    filtered["resource_group"].nunique() if "resource_group" in filtered.columns else "—",
)

# ── Data table ────────────────────────────────────────────────────────────
st.subheader(f"Resources ({len(filtered)} of {len(df)})")
st.dataframe(filtered, use_container_width=True, hide_index=True)

# ── Charts ────────────────────────────────────────────────────────────────
st.divider()
tab_cat, tab_loc, tab_sku, tab_iac = st.tabs(
    ["By Category", "By Location", "By SKU", "By IaC Hint"]
)

with tab_cat:
    if "service_category" in filtered.columns:
        counts = filtered["service_category"].value_counts().reset_index()
        counts.columns = ["Service Category", "Count"]
        st.bar_chart(counts, x="Service Category", y="Count")

with tab_loc:
    if "location" in filtered.columns:
        counts = filtered["location"].value_counts().reset_index()
        counts.columns = ["Location", "Count"]
        st.bar_chart(counts, x="Location", y="Count")

with tab_sku:
    if "sku_name" in filtered.columns:
        counts = (
            filtered["sku_name"]
            .replace("", "(none)")
            .value_counts()
            .head(20)
            .reset_index()
        )
        counts.columns = ["SKU", "Count"]
        st.bar_chart(counts, x="SKU", y="Count")

with tab_iac:
    if "iac_hint" in filtered.columns:
        counts = filtered["iac_hint"].value_counts().reset_index()
        counts.columns = ["IaC Hint", "Count"]
        st.bar_chart(counts, x="IaC Hint", y="Count")

# ── CSV download ──────────────────────────────────────────────────────────
st.divider()
st.download_button(
    "⬇ Download filtered CSV",
    data=filtered.to_csv(index=False),
    file_name="inventory_filtered.csv",
    mime="text/csv",
)
