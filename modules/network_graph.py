"""Network graph builder and visualization utilities.

Constructs NetworkX graphs from inventory data and renders them using Pyvis
with profile-specific adaptations.
"""

from typing import Optional

import networkx as nx
import pandas as pd
from pyvis.network import Network

from modules.graph_profiles.base import ProfileGraphAdapter


def build_base_graph(
    inventory_df: pd.DataFrame,
    include_failed: bool = False,
) -> nx.DiGraph:
    """Build base directed graph from inventory.
    
    Creates nodes for each resource and edges for parent-child relationships.
    Uses multiple detection methods to find relationships since is_child_resource
    may not be populated by all export methods.
    
    Args:
        inventory_df: Inventory DataFrame with columns: id, name, type, etc.
        include_failed: If False, exclude resources with provisioning_state != Succeeded
    
    Returns:
        NetworkX directed graph
    """
    graph = nx.DiGraph()
    
    # Filter to succeeded resources if requested
    df = inventory_df.copy()
    if not include_failed:
        df = df[df.get("provisioning_state", "Succeeded") == "Succeeded"]
    
    # Add nodes (one per resource)
    for _, resource in df.iterrows():
        resource_id = resource.get("id", "unknown")
        resource_name = resource.get("name", "unknown")
        
        graph.add_node(
            resource_id,
            label=resource_name,
            name=resource_name,
            type=resource.get("type", "unknown"),
            service_category=resource.get("service_category", "unknown"),
        )
    
    # Add edges (parent-child relationships) using multiple detection methods
    # Method 1: Use explicit is_child_resource flag
    for _, resource in df.iterrows():
        if resource.get("is_child_resource", False):
            resource_id = resource.get("id", "")
            parent_id = _extract_parent_id(resource_id)
            
            if parent_id and parent_id in graph.nodes():
                graph.add_edge(parent_id, resource_id, type="parent_child")
    
    # Method 2: Detect from resource name (e.g., "vault/secret" or "vault/secret/version")
    for _, resource in df.iterrows():
        resource_id = resource.get("id", "")
        resource_name = resource.get("name", "")
        
        if "/" in resource_name:
            # Try to find parent by name
            parent_name = resource_name.split("/")[0]
            for node_id in graph.nodes():
                node_data = graph.nodes[node_id]
                if node_data.get("name") == parent_name and node_id != resource_id:
                    # Found potential parent by name matching
                    if (node_id, resource_id) not in graph.edges():
                        graph.add_edge(node_id, resource_id, type="parent_child")
                    break
    
    # Method 3: Detect from resource ID path
    for _, resource in df.iterrows():
        resource_id = resource.get("id", "")
        parent_id = _extract_parent_id(resource_id)
        
        if parent_id and parent_id in graph.nodes() and parent_id != resource_id:
            # Verify we haven't already added this edge
            if (parent_id, resource_id) not in graph.edges():
                graph.add_edge(parent_id, resource_id, type="parent_child")
    
    return graph


def apply_profile_adaptation(
    graph: nx.DiGraph,
    inventory_df: pd.DataFrame,
    adapter: ProfileGraphAdapter,
) -> nx.DiGraph:
    """Apply profile-specific adaptations to graph.
    
    Args:
        graph: Base NetworkX graph
        inventory_df: Inventory DataFrame
        adapter: ProfileGraphAdapter instance
    
    Returns:
        Adapted graph with profile-specific attributes
    """
    return adapter.adapt_graph(graph, inventory_df)


def render_pyvis_html(
    graph: nx.DiGraph,
    layout_algorithm: str = "spring",
    height: int = 700,
    physics_enabled: bool = True,
) -> str:
    """Render NetworkX graph as Pyvis HTML.
    
    Args:
        graph: NetworkX graph (should have color/size attributes on nodes)
        layout_algorithm: 'spring' (force-directed) or 'hierarchical'
        height: Height of the visualization in pixels
        physics_enabled: Enable physics simulation
    
    Returns:
        HTML string for embedding in Streamlit
    """
    net = Network(
        directed=True,
        height=f"{height}px",
    )
    
    # Add nodes with styling
    for node_id in graph.nodes():
        node_data = graph.nodes[node_id]
        label = node_data.get("label", node_id)
        color = node_data.get("color", "#808080")
        size = node_data.get("size", 25)
        title = node_data.get("title", label)
        
        net.add_node(
            node_id,
            label=label,
            title=title,
            color=color,
            size=size,
            font={"size": 14},
        )
    
    # Add edges with styling - with width and labels for relationship visibility
    for source, target in graph.edges():
        edge_data = graph.edges[source, target]
        color = edge_data.get("color", "#888888")
        label = edge_data.get("label", "")
        width = edge_data.get("width", 1)
        
        # Scale width for visibility (Pyvis uses pixels)
        scaled_width = max(1, width * 2)  # 1→2px, 2→4px, 3→6px
        
        net.add_edge(
            source,
            target,
            color=color,
            label=label,
            arrows="to",
            width=scaled_width,
            font={"size": 12, "strokeWidth": 2, "color": "#000000"},
        )
    
    # Configure physics and layout
    if layout_algorithm == "spring" and physics_enabled:
        net.show_buttons(filter_=["physics"])
    else:
        # Disable physics for hierarchical layout
        net.show_buttons(filter_=["physics"])
    
    # Generate HTML using temporary file approach
    import tempfile
    import os
    
    # Create temporary HTML file
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, "network.html")
    
    try:
        # Use write_html directly instead of show
        net.write_html(tmp_path, notebook=False)
        
        # Read the generated HTML file
        with open(tmp_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    finally:
        # Clean up temporary files and directory
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if os.path.exists(tmp_dir):
                os.rmdir(tmp_dir)
        except OSError:
            pass  # Ignore cleanup errors


def filter_graph_by_properties(
    graph: nx.DiGraph,
    inventory_df: pd.DataFrame,
    filters: dict[str, list],
) -> nx.DiGraph:
    """Filter graph nodes based on properties.
    
    Args:
        graph: NetworkX graph
        inventory_df: Inventory DataFrame
        filters: Dict of {property: [values]} to include
    
    Returns:
        Filtered graph (nodes/edges matching filter criteria)
    """
    if not filters:
        return graph
    
    # Create lookup map
    inventory_map = inventory_df.set_index("id").to_dict("index")
    
    # Identify nodes to keep
    nodes_to_keep = set(graph.nodes())
    
    for node_id in graph.nodes():
        if node_id not in inventory_map:
            nodes_to_keep.discard(node_id)
            continue
        
        resource = inventory_map[node_id]
        
        # Check if node matches all filter criteria
        for field, allowed_values in filters.items():
            node_value = resource.get(field)
            if node_value not in allowed_values:
                nodes_to_keep.discard(node_id)
                break
    
    # Create subgraph with kept nodes
    return graph.subgraph(nodes_to_keep).copy()


def get_graph_statistics(graph: nx.DiGraph) -> dict:
    """Get graph statistics.
    
    Args:
        graph: NetworkX graph
    
    Returns:
        Dictionary with statistics
    """
    return {
        "node_count": len(graph.nodes()),
        "edge_count": len(graph.edges()),
        "density": nx.density(graph),
        "connected_components": nx.number_weakly_connected_components(graph),
    }


def apply_resource_group_coloring(
    graph: nx.DiGraph,
    inventory_df: pd.DataFrame,
) -> tuple[nx.DiGraph, dict[str, str]]:
    """Apply deterministic node coloring by resource group.

    Useful for quickly spotting cross-resource-group dependencies in topology views.

    Args:
        graph: Input graph (already adapted/styled)
        inventory_df: Inventory DataFrame with id and resource_group columns

    Returns:
        (colored_graph, resource_group_color_map)
    """
    colored_graph = graph.copy()

    if "id" not in inventory_df.columns or "resource_group" not in inventory_df.columns:
        return colored_graph, {}

    # High-contrast palette for group segmentation.
    palette = [
        "#0078D4",
        "#107C10",
        "#D83B01",
        "#5C2D91",
        "#038387",
        "#E81123",
        "#FFB900",
        "#8764B8",
        "#00B7C3",
        "#CA5010",
        "#498205",
        "#005A9E",
    ]

    inventory_map = inventory_df.set_index("id").to_dict("index")

    groups = set()
    for node_id in colored_graph.nodes():
        resource = inventory_map.get(node_id, {})
        group_name = str(resource.get("resource_group") or "unknown")
        groups.add(group_name)

    sorted_groups = sorted(groups)
    group_color_map = {
        group_name: palette[index % len(palette)]
        for index, group_name in enumerate(sorted_groups)
    }

    for node_id in colored_graph.nodes():
        resource = inventory_map.get(node_id, {})
        group_name = str(resource.get("resource_group") or "unknown")
        color = group_color_map.get(group_name, "#808080")
        colored_graph.nodes[node_id]["color"] = color

        existing_title = colored_graph.nodes[node_id].get("title", colored_graph.nodes[node_id].get("label", node_id))
        if "Resource Group:" not in str(existing_title):
            colored_graph.nodes[node_id]["title"] = f"{existing_title}<br/>Resource Group: {group_name}"

    return colored_graph, group_color_map


def _extract_parent_id(resource_id: str) -> Optional[str]:
    """Extract parent resource ID from a child resource ID.
    
    Azure resource IDs are hierarchical:
    /subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{type}/{name}
    
    Parent-child pattern:
    Parent: /subscriptions/.../providers/Microsoft.KeyVault/vaults/my-vault
    Child:  /subscriptions/.../providers/Microsoft.KeyVault/vaults/my-vault/secrets/my-secret
    
    Args:
        resource_id: Full Azure resource ID
    
    Returns:
        Parent resource ID, or None if this is a top-level resource
    """
    if not resource_id or "/" not in resource_id:
        return None
    
    # Remove trailing slash if present
    resource_id = resource_id.rstrip("/")
    
    # Split by '/' and find the position of 'providers'
    parts = resource_id.split("/")
    
    try:
        provider_idx = parts.index("providers")
    except ValueError:
        # Not a provider-based resource
        return None
    
    # After 'providers', we have: provider/resourceType/name[/childType/childName...]
    remaining = parts[provider_idx + 1:]
    
    # Alternating pattern: provider, type, name, type, name...
    # 3 components: provider, type, name (top-level)
    # 5 components: provider, type, name, childtype, childname (1 level deep)
    
    if len(remaining) <= 3:
        # Top-level resource
        return None
    
    # Remove the last two elements (child type and child name)
    parent_parts = parts[:-2]
    parent_id = "/".join(parent_parts)
    
    return parent_id if parent_id else None
