"""Abstract base class for profile-specific graph adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import networkx as nx
import pandas as pd


@dataclass
class FilterConfig:
    """Filter configuration for graph nodes."""
    
    field: str
    values: list
    include: bool = True


@dataclass
class NodeStyleConfig:
    """Node styling configuration."""
    
    color_dimension: str  # Field to use for node color
    color_palette: str    # Color scheme name
    size_dimension: str   # Field to use for node size
    size_scale: float = 1.0  # Scaling factor


@dataclass
class EdgeStyleConfig:
    """Edge styling configuration."""
    
    color_field: str | None = None
    color_map: dict | None = None
    show_labels: bool = False
    label_field: str | None = None


class ProfileGraphAdapter(ABC):
    """Abstract base class for profile-specific graph visualization adapters.
    
    Each profile (architecture, security, networking, bcdr, governance, 
    observability, defender) provides tailored graph configurations that
    emphasize profile-specific relationships, node properties, and visual cues.
    
    Subclasses should override properties to customize graph appearance and
    filtering for their profile.
    """
    
    # ─── Profile identity ────────────────────────────────────────────────
    
    @property
    @abstractmethod
    def profile_name(self) -> str:
        """Unique identifier for this profile (e.g., 'security')."""
        pass
    
    @property
    @abstractmethod
    def profile_label(self) -> str:
        """Human-readable profile label (e.g., 'Security Posture')."""
        pass
    
    # ─── Graph configuration ─────────────────────────────────────────────
    
    @property
    @abstractmethod
    def relationship_types(self) -> list[str]:
        """Relationship types to emphasize (e.g., ['parent_child', 'remediation_chains'])."""
        pass
    
    @property
    @abstractmethod
    def node_style(self) -> NodeStyleConfig:
        """Node styling configuration (colors, sizes)."""
        pass
    
    @property
    @abstractmethod
    def edge_style(self) -> EdgeStyleConfig:
        """Edge styling configuration."""
        pass
    
    @property
    @abstractmethod
    def default_filters(self) -> list[FilterConfig]:
        """Default filters to apply when loading graph."""
        pass
    
    @property
    @abstractmethod
    def layout_algorithm(self) -> str:
        """Preferred layout algorithm: 'spring' (force-directed) or 'hierarchical'."""
        pass
    
    # ─── Help text and annotations ───────────────────────────────────────
    
    @property
    @abstractmethod
    def help_text(self) -> str:
        """User-facing help text explaining the visualization."""
        pass
    
    @property
    def annotations(self) -> list[str] | None:
        """Optional list of annotations to highlight in the graph."""
        return None
    
    # ─── Adaptation methods ──────────────────────────────────────────────
    
    def adapt_graph(
        self,
        graph: nx.DiGraph,
        inventory_df: pd.DataFrame,
        active_filters: dict | None = None,
    ) -> nx.DiGraph:
        """Apply profile-specific adaptations to the graph.
        
        Args:
            graph: Base NetworkX directed graph
            inventory_df: Inventory DataFrame
            active_filters: User-selected filter overrides
        
        Returns:
            Adapted graph with profile-specific node/edge attributes
        """
        # Apply node styling
        self._apply_node_styling(graph, inventory_df)
        
        # Apply edge styling
        self._apply_edge_styling(graph, inventory_df)
        
        # Apply default filters
        self._apply_filters(graph, active_filters or {})
        
        return graph
    
    def _apply_node_styling(
        self,
        graph: nx.DiGraph,
        inventory_df: pd.DataFrame,
    ) -> None:
        """Apply node color and size based on profile configuration."""
        node_style = self.node_style
        
        # Create lookup map from inventory_df
        inventory_map = inventory_df.set_index("id").to_dict("index")
        
        # Color palette mappings (to be extended as needed)
        color_map = self._get_color_map(node_style.color_palette)
        
        for node_id in graph.nodes():
            if node_id not in inventory_map:
                continue
            
            resource = inventory_map[node_id]
            
            # Color by dimension
            color_value = resource.get(node_style.color_dimension, "unknown")
            color = color_map.get(color_value, "#808080")
            
            # Size by dimension
            size_value = resource.get(node_style.size_dimension, 1)
            if isinstance(size_value, str):
                size_value = 1  # Default if not numeric
            size = max(10, min(50, size_value * node_style.size_scale))
            
            # Apply attributes
            graph.nodes[node_id]["color"] = color
            graph.nodes[node_id]["size"] = size
            graph.nodes[node_id]["title"] = self._build_node_title(resource)
    
    def _apply_edge_styling(
        self,
        graph: nx.DiGraph,
        inventory_df: pd.DataFrame,
    ) -> None:
        """Apply edge colors and labels based on profile configuration."""
        edge_style = self.edge_style
        
        if not edge_style.color_field or not edge_style.color_map:
            # No custom edge styling
            for u, v in graph.edges():
                graph.edges[u, v]["color"] = "#888888"
            return
        
        # Apply custom edge colors if available
        for u, v in graph.edges():
            graph.edges[u, v]["color"] = "#888888"  # Default
            if edge_style.show_labels and edge_style.label_field:
                graph.edges[u, v]["label"] = ""
            color_map = self.edge_style.color_map if self.edge_style.color_map else {}
        
            # Get color palette for mapping
            color_palette = self._get_color_map(edge_style.color_field) if edge_style.color_field else {}
        
            # Apply edge styling
            for u, v in graph.edges():
                edge_data = graph.edges[u, v]
            
                # Get edge type/relationship from edge data
                edge_type = edge_data.get("type", "parent_child")
            
                # Apply color based on color map or edge type
                if color_map and edge_type in color_map:
                    graph.edges[u, v]["color"] = color_map[edge_type]
                elif edge_type in color_palette:
                    graph.edges[u, v]["color"] = color_palette[edge_type]
                else:
                    # Default colors for common edge types
                    default_colors = {
                        "parent_child": "#888888",
                        "service_composition": "#4A90E2",
                        "implicit_dependencies": "#7ED321",
                        "remediation_chains": "#D0021B",
                        "network_hierarchy": "#4A90E2",
                        "segmentation_rules": "#50E3C2",
                        "private_endpoints": "#B8E986",
                        "regional_peering": "#FF6B6B",
                    }
                    graph.edges[u, v]["color"] = default_colors.get(edge_type, "#888888")
            
                # Apply edge width based on type
                edge_widths = {
                    "parent_child": 1,
                    "service_composition": 2,
                    "implicit_dependencies": 2,
                    "remediation_chains": 3,
                    "network_hierarchy": 2,
                    "segmentation_rules": 2,
                    "private_endpoints": 2,
                    "regional_peering": 2,
                }
                graph.edges[u, v]["width"] = edge_widths.get(edge_type, 1)
            
                # Apply labels if configured
                if edge_style.show_labels:
                    label = edge_data.get("label", edge_type)
                    graph.edges[u, v]["label"] = label
    def _apply_filters(
        self,
        graph: nx.DiGraph,
        active_filters: dict,
    ) -> None:
        """Apply filters to graph (remove nodes matching filter criteria).
        
        Currently, filters are applied at data load time, not at graph render.
        This is a placeholder for future enhancement if dynamic filtering
        is needed at render time.
        """
        # Filters are typically applied during graph construction
        # This method is here for future extensibility
        pass
    
    def _get_color_map(self, palette: str) -> dict[str, str]:
        """Get color mapping for a given palette name."""
        palettes = {
            # Service categories
            "service_category": {
                "microsoft.compute": "#0078D4",         # Blue
                "microsoft.storage": "#50E6FF",         # Cyan
                "microsoft.network": "#107C10",         # Green
                "microsoft.database": "#DA3B01",        # Red
                "microsoft.cognitiveservices": "#8764B8",  # Purple
                "microsoft.insights": "#FFB900",        # Amber
                "microsoft.keyvault": "#C50F1F",        # Dark Red
                "microsoft.containerregistry": "#6B69D6",  # Indigo
            },
            # Risk-based (security)
            "risk_based": {
                "P1": "#D13438",         # Critical red
                "P2": "#FF8C00",         # High orange
                "P3": "#FFB900",         # Medium amber
                "P4": "#107C10",         # Low green
                "P5": "#8764B8",         # Info purple
            },
            # Compliance state (governance)
            "compliance_state": {
                "compliant": "#107C10",      # Green
                "non_compliant": "#D13438", # Red
                "partial": "#FF8C00",       # Orange
                "unknown": "#808080",       # Gray
            },
            # Monitoring coverage
            "coverage_state": {
                "monitored": "#107C10",     # Green
                "partial": "#FF8C00",       # Orange
                "unmonitored": "#D13438",   # Red
                "unknown": "#808080",       # Gray
            },
            # CSPM severity (defender)
            "cspm_severity": {
                "Critical": "#D13438",      # Red
                "High": "#FF8C00",          # Orange
                "Medium": "#FFB900",        # Amber
                "Low": "#107C10",           # Green
                "Passed": "#50E6FF",        # Cyan
            },
            # Redundancy state (BCDR)
            "redundancy": {
                "replicated": "#107C10",    # Green (redundant)
                "single_instance": "#D13438",  # Red (at risk)
                "unreplicated": "#FF8C00",  # Orange (warning)
                "unknown": "#808080",       # Gray
            },
            # Network resource type
            "network_topology": {
                "VNet": "#0078D4",          # Blue
                "Subnet": "#107C10",        # Green
                "NIC": "#FF8C00",           # Orange
                "NSG": "#D13438",           # Red
                "VM": "#8764B8",            # Purple
                "Peering": "#50E6FF",       # Cyan
            },
        }
        return palettes.get(palette, {})
    
    def _build_node_title(self, resource: dict) -> str:
        """Build tooltip text for a node."""
        name = resource.get("name", "Unknown")
        res_type = resource.get("type", "Unknown")
        location = resource.get("location", "Unknown")
        state = resource.get("provisioning_state", "Unknown")
        
        return f"{name}\n{res_type}\nLocation: {location}\nState: {state}"


# Default no-op adapter for profiles not yet implemented
class DefaultGraphAdapter(ProfileGraphAdapter):
    """Default adapter for profiles without custom implementation."""
    
    def __init__(self, profile_name: str):
        self._profile_name = profile_name
    
    @property
    def profile_name(self) -> str:
        return self._profile_name
    
    @property
    def profile_label(self) -> str:
        return self._profile_name.replace("_", " ").title()
    
    @property
    def relationship_types(self) -> list[str]:
        return ["parent_child"]
    
    @property
    def node_style(self) -> NodeStyleConfig:
        return NodeStyleConfig(
            color_dimension="service_category",
            color_palette="service_category",
            size_dimension="sku_name",
            size_scale=1.0,
        )
    
    @property
    def edge_style(self) -> EdgeStyleConfig:
        return EdgeStyleConfig()
    
    @property
    def default_filters(self) -> list[FilterConfig]:
        return [
            FilterConfig(field="provisioning_state", values=["Succeeded"]),
        ]
    
    @property
    def layout_algorithm(self) -> str:
        return "spring"
    
    @property
    def help_text(self) -> str:
        return f"Resource hierarchy graph for {self.profile_label} profile."
