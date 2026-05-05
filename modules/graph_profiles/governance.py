"""Governance profile graph adapter (stub).

Emphasizes tagging hierarchy, RBAC chains, and compliance state.
"""

from modules.graph_profiles.base import (
    ProfileGraphAdapter,
    NodeStyleConfig,
    EdgeStyleConfig,
    FilterConfig,
)


class GovernanceGraphAdapter(ProfileGraphAdapter):
    """Graph adapter for Governance profile visualization.
    
    TODO: Implement tagging hierarchy and RBAC chain visualization.
    Currently uses default behavior.
    """
    
    @property
    def profile_name(self) -> str:
        return "governance"
    
    @property
    def profile_label(self) -> str:
        return "Governance & Compliance"
    
    @property
    def relationship_types(self) -> list[str]:
        return [
            "parent_child",
            "rbac_hierarchy",
            "tagging_inheritance",
            "compliance_lineage",
        ]
    
    @property
    def node_style(self) -> NodeStyleConfig:
        return NodeStyleConfig(
            color_dimension="tagging_compliance",  # compliant, non_compliant
            color_palette="compliance_state",
            size_dimension="untagged_child_count",
            size_scale=1.5,
        )
    
    @property
    def edge_style(self) -> EdgeStyleConfig:
        return EdgeStyleConfig(
            color_field="rbac_role",
            color_map={
                "owner": "#0078D4",        # Blue
                "contributor": "#107C10", # Green
                "reader": "#808080",      # Gray
                "default": "#888888",
            },
            show_labels=True,
            label_field="rbac_role",
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
        return "hierarchical"  # Emphasizes ownership hierarchy
    
    @property
    def help_text(self) -> str:
        return (
            "Governance topology. "
            "Green nodes = compliant tagging; Red = non-compliant (missing tags). "
            "Blue edges = ownership; Green = contributor; Gray = reader. "
            "Node size = tagging debt (larger = more untagged children). "
            "[Implementation pending: RBAC chain visualization, tag inheritance]"
        )
    
    @property
    def annotations(self) -> list[str] | None:
        return [
            "Untagged resources (tagging compliance gaps)",
            "RBAC over-provisioning (excess permissions)",
            "Orphaned ownership (resources without clear owner)",
            "Tag inheritance violations",
        ]
