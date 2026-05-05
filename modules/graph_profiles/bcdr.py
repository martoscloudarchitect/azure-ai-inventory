"""BCDR profile graph adapter (stub).

Emphasizes redundancy, failover chains, RTO/RPO dependencies, and 
business continuity patterns.
"""

from modules.graph_profiles.base import (
    ProfileGraphAdapter,
    NodeStyleConfig,
    EdgeStyleConfig,
    FilterConfig,
)


class BCDRGraphAdapter(ProfileGraphAdapter):
    """Graph adapter for BCDR profile visualization.
    
    TODO: Implement redundancy detection and failover chain visualization.
    Currently uses default behavior.
    """
    
    @property
    def profile_name(self) -> str:
        return "bcdr"
    
    @property
    def profile_label(self) -> str:
        return "Business Continuity & Disaster Recovery"
    
    @property
    def relationship_types(self) -> list[str]:
        return [
            "parent_child",
            "redundancy_pairs",
            "failover_chains",
            "rto_rpo_dependencies",
        ]
    
    @property
    def node_style(self) -> NodeStyleConfig:
        return NodeStyleConfig(
            color_dimension="availability_state",  # replicated, single_instance, etc.
            color_palette="redundancy",
            size_dimension="rto_minutes",
            size_scale=1.5,
        )
    
    @property
    def edge_style(self) -> EdgeStyleConfig:
        return EdgeStyleConfig(
            color_field="relationship_type",
            color_map={
                "replication": "#107C10",  # Green (active replication)
                "failover": "#FF8C00",     # Orange (standby/failover)
                "depends_on": "#D13438",   # Red (blocking)
                "default": "#888888",
            },
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
        return "spring"  # Force-directed to group redundancy pairs
    
    @property
    def help_text(self) -> str:
        return (
            "BCDR topology. "
            "Red nodes = single-instance (RTO risk). "
            "Green nodes = replicated/redundant. "
            "Green edges = active replication; Orange = failover chains. "
            "Node size = RTO impact (larger = longer recovery time). "
            "[Implementation pending: redundancy detection, failover orchestration]"
        )
    
    @property
    def annotations(self) -> list[str] | None:
        return [
            "Single points of failure (red nodes)",
            "RTO/RPO compliance gaps",
            "Failover orchestration dependencies",
            "Cross-region replication patterns",
        ]
