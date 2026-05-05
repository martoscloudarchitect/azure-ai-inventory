"""Topology Visualization — Profile-aware interactive resource topology."""

import streamlit as st
import streamlit.components.v1 as components
from modules import network_graph

from streamlit_app.helpers import (
    load_inventory_json,
    detect_profile,
    display_disclaimer,
    get_inventory_size,
    display_scaling_warning,
)
from modules.network_graph import (
    build_base_graph,
    apply_profile_adaptation,
    render_pyvis_html,
    filter_graph_by_properties,
    get_graph_statistics,
)
from modules.graph_profiles import get_adapter_for_profile


run_dir = st.session_state.get("_run_dir")

st.title("🔗 Topology")

if not run_dir:
    st.info("Select a previous assessment or run a new one from the sidebar to get started.")
    st.stop()

# ── Disclaimer ────────────────────────────────────────────────────────────
display_disclaimer()

# ── Scaling warning ───────────────────────────────────────────────────────
inventory_count = get_inventory_size(run_dir)
display_scaling_warning(inventory_count)

st.divider()

# ── Detect profile and load adapter ───────────────────────────────────────
profile = detect_profile(run_dir)
if not profile:
    st.error("Could not detect profile from this run.")
    st.stop()

try:
    adapter = get_adapter_for_profile(profile)
except ValueError as e:
    st.error(f"Profile adapter not available: {e}")
    st.stop()

# ── Load inventory ────────────────────────────────────────────────────────
try:
    inventory_df = load_inventory_json(run_dir)
except (FileNotFoundError, ValueError) as e:
    st.error(f"Failed to load inventory: {e}")
    st.stop()

# ── Display profile info and help text ────────────────────────────────────
st.subheader(f"📊 {adapter.profile_label}")
st.markdown(adapter.help_text)

if adapter.annotations:
    with st.expander("💡 What to look for", expanded=False):
        for annotation in adapter.annotations:
            st.markdown(f"- {annotation}")

st.divider()

# ── Build base graph and apply profile adaptation ────────────────────────
with st.spinner("Building topology graph..."):
    graph = build_base_graph(inventory_df, include_failed=False)
    adapted_graph = apply_profile_adaptation(graph, inventory_df, adapter)
    graph_stats = get_graph_statistics(adapted_graph)

# ── Display graph statistics ──────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Resources", graph_stats["node_count"])
col2.metric("Relationships", graph_stats["edge_count"])
col3.metric("Components", graph_stats["connected_components"])

st.divider()

# ── Filtering controls (profile-specific defaults) ────────────────────────
st.subheader("Filters & Options")

filter_cols = st.columns(3)

with filter_cols[0]:
    include_failed = st.checkbox(
        "Include Failed Resources",
        value=False,
        help="Show resources with provisioning_state != Succeeded"
    )

with filter_cols[1]:
    physics_enabled = st.checkbox(
        "Enable Physics Simulation",
        value=(adapter.layout_algorithm == "spring"),
        help="Force-directed layout (slower but reveals clusters)"
    )

with filter_cols[2]:
    color_by_resource_group = st.checkbox(
        "Color by Resource Group",
        value=False,
        help="Overrides profile coloring to highlight resource-group boundaries"
    )

# ── Service category filter ───────────────────────────────────────────────
st.subheader("Service Category Filter")
service_categories = sorted(inventory_df["service_category"].unique())
selected_categories = st.multiselect(
    "Select service categories to show",
    service_categories,
    default=service_categories,
    help="Filter nodes by service (Compute, Storage, Network, etc.)"
)

# ── Resource group filter ─────────────────────────────────────────────────
st.subheader("Resource Group Filter")
resource_groups = sorted(inventory_df["resource_group"].unique())
selected_rgs = st.multiselect(
    "Select resource groups to show",
    resource_groups,
    default=resource_groups,
    help="Filter nodes by resource group"
)

st.divider()

# ── Build filtered graph ──────────────────────────────────────────────────
with st.spinner("Rendering topology visualization..."):
    # Apply user filters
    filter_dict = {
        "service_category": selected_categories,
        "resource_group": selected_rgs,
    }
    
    if not include_failed:
        filter_dict["provisioning_state"] = ["Succeeded"]
    
    filtered_graph = filter_graph_by_properties(adapted_graph, inventory_df, filter_dict)

    resource_group_color_map = {}
    if color_by_resource_group:
        filtered_graph, resource_group_color_map = network_graph.apply_resource_group_coloring(
            filtered_graph,
            inventory_df,
        )
    
    # Render Pyvis HTML
    pyvis_html = render_pyvis_html(
        filtered_graph,
        layout_algorithm=adapter.layout_algorithm,
        height=700,
        physics_enabled=physics_enabled,
    )

# ── Display Pyvis visualization ───────────────────────────────────────────
st.subheader("Topology Visualization")
components.html(pyvis_html, height=750)

st.divider()

# ── Graph exploration helpers ─────────────────────────────────────────────
st.subheader("Graph Details")

with st.expander("Node Size Legend", expanded=False):
    st.markdown(
        f"""
        **Node size represents:** {adapter.node_style.size_dimension}
        
        - Larger nodes = higher {adapter.node_style.size_dimension}
        - Smaller nodes = lower {adapter.node_style.size_dimension}
        """
    )

with st.expander("Node Color Legend", expanded=False):
    if color_by_resource_group:
        st.markdown("**Node color represents:** resource_group")
        if resource_group_color_map:
            st.markdown("Resource-group palette applied:")
            for rg_name, rg_color in sorted(resource_group_color_map.items()):
                st.markdown(f"- {rg_name}: {rg_color}")
        else:
            st.markdown("No resource-group values available for the current filter selection.")
    else:
        st.markdown(
            f"""
            **Node color represents:** {adapter.node_style.color_dimension}

            Each distinct color reflects a different value in the {adapter.node_style.color_dimension} field.
            """
        )

with st.expander("Graph Statistics", expanded=False):
    st.json(graph_stats)

with st.expander("Sample Nodes (first 10)", expanded=False):
    node_list = list(filtered_graph.nodes())[:10]
    for node_id in node_list:
        node_data = filtered_graph.nodes[node_id]
        st.markdown(f"**{node_data.get('label', node_id)}**")
        st.text(f"ID: {node_id[:80]}...")
        st.text(f"Type: {node_data.get('type', 'unknown')}")
