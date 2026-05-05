"""Architecture profile graph adapter.

Emphasizes service composition, deployment patterns, IaC adoption, and 
regional distribution.
"""

from modules.graph_profiles.base import (
    ProfileGraphAdapter,
    NodeStyleConfig,
    EdgeStyleConfig,
    FilterConfig,
)


class ArchitectureGraphAdapter(ProfileGraphAdapter):
    """Graph adapter for Architecture profile visualization."""
    
    @property
    def profile_name(self) -> str:
        return "architecture"
    
    @property
    def profile_label(self) -> str:
        return "Architecture Review"
    
    @property
    def relationship_types(self) -> list[str]:
        return [
            "parent_child",
            "service_composition",
            "regional_distribution",
        ]
    
    @property
    def node_style(self) -> NodeStyleConfig:
        return NodeStyleConfig(
            color_dimension="service_category",
            color_palette="service_category",
            size_dimension="sku_name",
            size_scale=1.5,
        )
    
    @property
    def edge_style(self) -> EdgeStyleConfig:
        return EdgeStyleConfig(
            color_field=None,  # Use default edge color
            show_labels=True,
            label_field="relationship_type",
        )
    
    @property
    def default_filters(self) -> list[FilterConfig]:
        return [
            FilterConfig(
                field="provisioning_state",
                values=["Succeeded"],
                include=True,
            ),
        ]
    
    @property
    def layout_algorithm(self) -> str:
        return "hierarchical"
    
    @property
    def help_text(self) -> str:
        return (
            "Architecture topology. "
            "Nodes colored by service category; size indicates SKU tier. "
            "IaC resources (Bicep/ARM) highlighted. "
            "Shows service composition and multi-region distribution."
        )
    
    @property
    def annotations(self) -> list[str] | None:
        return [
            "IaC adoption (highlight bicep/arm resources)",
            "Service-oriented vs monolithic patterns",
            "Multi-region concentration risks",
        ]
