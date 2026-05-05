"""Security profile graph adapter.

Emphasizes remediation chains, risk clusters, blast radius, and at-risk resources.
"""

from modules.graph_profiles.base import (
    ProfileGraphAdapter,
    NodeStyleConfig,
    EdgeStyleConfig,
    FilterConfig,
)


class SecurityGraphAdapter(ProfileGraphAdapter):
    """Graph adapter for Security profile visualization."""
    
    @property
    def profile_name(self) -> str:
        return "security"
    
    @property
    def profile_label(self) -> str:
        return "Security Posture"
    
    @property
    def relationship_types(self) -> list[str]:
        return [
            "parent_child",
            "implicit_dependencies",
            "remediation_chains",
        ]
    
    @property
    def node_style(self) -> NodeStyleConfig:
        return NodeStyleConfig(
            color_dimension="remediation_priority",  # P1, P2, P3
            color_palette="risk_based",
            size_dimension="blast_radius_estimate",
            size_scale=2.0,
        )
    
    @property
    def edge_style(self) -> EdgeStyleConfig:
        return EdgeStyleConfig(
            color_field="edge_type",
            color_map={
                "blast_radius": "#D13438",   # Red (critical dependency)
                "remediation_blocker": "#FF8C00",  # Orange (blocker)
                "default": "#888888",  # Gray
            },
            show_labels=True,
            label_field="edge_type",
        )
    
    @property
    def default_filters(self) -> list[FilterConfig]:
        return [
            FilterConfig(
                field="has_remediation",
                values=[True],
                include=True,
            ),
        ]
    
    @property
    def layout_algorithm(self) -> str:
        return "spring"  # Force-directed to group risk clusters
    
    @property
    def help_text(self) -> str:
        return (
            "Security assessment. "
            "Red (P1) = Critical risk; Orange (P2) = High; Yellow (P3) = Medium. "
            "Node size = blast radius (impact if compromised). "
            "Red edges = cascade dependencies; Orange edges = remediation blockers. "
            "Larger clusters = coordinated remediation needed."
        )
    
    @property
    def annotations(self) -> list[str] | None:
        return [
            "Critical risk clustering (P1 remediation dependencies)",
            "Blast radius hotspots (single resources affecting many others)",
            "Remediation blocking chains (fix this first)",
            "Implicit dependency exposure",
        ]
