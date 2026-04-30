"""Overview — Discovery KPIs, charts, and AI-generated environment brief."""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from streamlit_app.helpers import (
    load_json,
    load_markdown,
    get_inventory_size,
    display_disclaimer,
    display_scaling_warning,
    display_sampling_statistics,
    get_latest_run_per_profile,
    extract_initiatives,
    PROFILE_COLORS,
)


# ── Prioritization chart builder ──────────────────────────────────────────
_COST_SIZE: dict[str, int] = {"Low": 26, "Medium": 40, "High": 58}
_COMPLEXITY_LABEL: dict[float, str] = {1.5: "Low", 5.0: "Medium", 8.5: "High"}
_ZONES = [
    (0.0,  3.5, "Tactical Quick Wins",          "rgba(255,253,231,0.65)", "#E65100"),
    (3.5,  7.0, "Strategic Priorities",          "rgba(227,242,253,0.65)", "#1565C0"),
    (7.0, 10.0, "Transformational Initiatives",  "rgba(243,229,245,0.65)", "#6A1B9A"),
]


def _build_prioritization_chart(initiatives: list[dict]) -> go.Figure:
    y_max = max(i["uplift"] for i in initiatives) + 3
    fig = go.Figure()

    # ── Zone background rectangles
    for x0, x1, label, fill, text_color in _ZONES:
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=0, y1=y_max,
            fillcolor=fill, line=dict(width=0), layer="below",
        )
        fig.add_annotation(
            x=(x0 + x1) / 2, y=y_max * 0.97,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=11, color=text_color),
            xanchor="center", yanchor="top",
        )

    # ── Zone boundary lines
    for x in (3.5, 7.0):
        fig.add_shape(
            type="line", x0=x, x1=x, y0=0, y1=y_max,
            line=dict(color="rgba(150,150,150,0.45)", width=1, dash="dot"),
        )

    # ── One scatter trace per profile (drives the legend)
    for profile in sorted({i["profile"] for i in initiatives}):
        color = PROFILE_COLORS.get(profile, "#888888")
        subset = [i for i in initiatives if i["profile"] == profile]
        fig.add_trace(go.Scatter(
            x=[i["complexity"] for i in subset],
            y=[i["uplift"] for i in subset],
            mode="markers+text",
            marker=dict(
                size=[_COST_SIZE[i["cost_label"]] for i in subset],
                color=color,
                opacity=0.85,
                line=dict(width=1.5, color="white"),
                sizemode="diameter",
            ),
            text=[i["priority"] for i in subset],
            textposition="middle center",
            textfont=dict(color="white", size=11, family="Arial Black"),
            name=profile.capitalize(),
            customdata=[
                (
                    i["remediation"],
                    i["cost_label"],
                    _COMPLEXITY_LABEL[i["complexity"]],
                    i.get("source_run", ""),
                )
                for i in subset
            ],
            hovertemplate=(
                f"<b>%{{text}}</b> · {profile.capitalize()}<br>"
                "%{customdata[0]}<br>"
                "Uplift: +%{y:.0f}% │ Complexity: %{customdata[2]} │ Cost: %{customdata[1]}<br>"
                "<i>Source: %{customdata[3]}</i><extra></extra>"
            ),
        ))

    fig.update_layout(
        xaxis=dict(
            title=dict(text="Technical Complexity", font=dict(color="#222222")),
            range=[0, 10],
            tickvals=[1.75, 5.25, 8.5],
            ticktext=["Low", "Medium", "High"],
            tickfont=dict(color="#222222"),
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text="Potential Benefits Impact (Uplift %)", font=dict(color="#222222")),
            range=[0, y_max],
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)",
            tickfont=dict(color="#222222"),
            zeroline=False,
        ),
        legend=dict(
            title=dict(text="<b>Profile</b>", font=dict(color="#222222")),
            orientation="v",
            yanchor="top", y=1.0,
            xanchor="left", x=1.01,
            bgcolor="#ffffff",
            bordercolor="#cccccc",
            borderwidth=1,
            font=dict(color="#222222"),
        ),
        font=dict(color="#222222", family="Arial"),
        margin=dict(l=60, r=160, t=40, b=60),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=520,
    )
    return fig

run_dir = st.session_state.get("_run_dir")

# ── Header ───────────────────────────────────────────────────────────────
st.title("AzurePrism — Overview")
st.caption("One beam in, full spectrum out.")

if not run_dir:
    st.info("Select a previous assessment or run a new one from the sidebar to get started.")
    st.stop()

# ── Disclaimer ────────────────────────────────────────────────────────────
display_disclaimer()

# ── Cross-Profile Initiative Prioritization ─────────────────────────────
st.header("Initiative Prioritization")

st.markdown(
    """
Every assessment profile — Security, Governance, BCDR, Observability, and others — produces a ranked
list of improvement initiatives. This chart brings all of them onto a single canvas so leadership and
budget owners can compare and sequence investments across the entire Azure environment at a glance,
rather than reviewing each technical report in isolation.

**How to read the chart**

| Dimension | What it measures | Business question it answers |
|---|---|---|
| **Vertical position (Y-axis)** | Potential benefit impact — how much the initiative improves the overall environment score | *"What do we gain?"* |
| **Horizontal position (X-axis)** | Technical complexity — how difficult the initiative is to implement | *"How hard is it?"* |
| **Bubble size** | Estimated implementation cost — small = low spend, large = significant investment | *"What does it cost?"* |
| **Bubble color** | Source profile — which workstream the initiative belongs to | *"Who owns it?"* |

**How to use it in a conversation**

- Bubbles in the **bottom-left** (high benefit, low complexity, small size) are your quick wins —
  propose these first to demonstrate fast, low-risk progress.
- Bubbles in the **top-right** (high benefit, high complexity, large size) are transformational bets —
  these belong in a multi-quarter roadmap with executive sponsorship.
- **Clusters of bubbles from different profiles** at the same position signal cross-team dependencies:
  Security, Networking, and Governance may all be asking for private endpoints at the same time —
  one coordinated initiative instead of three separate budget asks.
- Run additional profiles to populate missing workstreams and sharpen the picture before a budget
  review or architecture board presentation.
"""
)

st.caption(
    "Each bubble is a P1–P8 remediation initiative from the **latest run** of each profile. "
    "Position = benefit impact vs. technical complexity. "
    "Bubble size = estimated implementation cost (small = low, large = high)."
)

_latest_runs = get_latest_run_per_profile()
if not _latest_runs:
    st.info("No profile assessments found. Run at least one profile to see the chart.")
else:
    _all_initiatives: list[dict] = []
    for _profile, (_folder_name, _path) in _latest_runs.items():
        for _item in extract_initiatives(_path, _profile):
            _item["source_run"] = _folder_name
            _all_initiatives.append(_item)

    if not _all_initiatives:
        st.info("No uplift tables found in any profile report.")
    else:
        _available = sorted({i["profile"] for i in _all_initiatives})
        _selected = st.multiselect(
            "Filter profiles",
            options=_available,
            default=_available,
            format_func=str.capitalize,
            label_visibility="collapsed",
        )
        _filtered = [i for i in _all_initiatives if i["profile"] in _selected]
        if _filtered:
            st.plotly_chart(_build_prioritization_chart(_filtered), use_container_width=True)
            st.caption(
                "**Bubble size legend:** ● Small = Low Cost   ● Medium = Medium Cost   ● Large = High Cost"
            )
            with st.expander("Data sources — latest run used per profile"):
                for _profile, (_folder_name, _) in sorted(_latest_runs.items()):
                    if _profile in _selected:
                        _count = len([i for i in _all_initiatives if i["profile"] == _profile])
                        st.caption(
                            f"**{_profile.capitalize()}** → `{_folder_name}` ({_count} initiatives)"
                        )
        else:
            st.info("Select at least one profile to display the chart.")

st.divider()

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

# ── Scaling warning and sampling statistics ────────────────────────────────
inventory_count = get_inventory_size(run_dir)
display_scaling_warning(inventory_count)
display_sampling_statistics(run_dir)

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
st.divider()
st.header("AI-Generated Environment Brief")

brief = load_markdown(run_dir / "discovery.md")
if brief:
    st.markdown(brief)
else:
    st.info("No discovery.md found for this run.")
