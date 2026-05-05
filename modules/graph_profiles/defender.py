"""Defender profile graph adapter (stub).

Emphasizes security misconfigurations, control gaps, and CSPM requirements.
"""

from modules.graph_profiles.base import (
    ProfileGraphAdapter,
    NodeStyleConfig,
    EdgeStyleConfig,
    FilterConfig,
)


class DefenderGraphAdapter(ProfileGraphAdapter):
    """Graph adapter for Defender profile visualization.
    
    TODO: Implement CSPM finding visualization and control gap clustering.
    Currently uses default behavior.
    """
    
    @property
    def profile_name(self) -> str:
        return "defender"
    
    @property
    def profile_label(self) -> str:
        return "Defender for Cloud"
    
    @property
    def relationship_types(self) -> list[str]:
        return [
            "parent_child",
            "misconfiguration_clusters",
            "cspm_requirements",
            "control_gaps",
        ]
    
    @property
    def node_style(self) -> NodeStyleConfig:
        return NodeStyleConfig(
            color_dimension="defender_severity",  # Critical, High, Medium, Low
            color_palette="cspm_severity",
            size_dimension="cspm_finding_count",
            size_scale=2.0,
        )
    
    @property
    def edge_style(self) -> EdgeStyleConfig:
        return EdgeStyleConfig(
            color_field="control_relationship",
            color_map={
                "critical": "#D13438",  # Red
                "high": "#FF8C00",      # Orange
                "medium": "#FFB900",    # Amber
                "default": "#888888",
            },
            show_labels=True,
            label_field="control_relationship",
        )
    
    @property
    def default_filters(self) -> list[FilterConfig]:
        return [
            FilterConfig(
                field="has_findings",
                values=[True],
                include=True,
            ),
        ]
    
    @property
    def layout_algorithm(self) -> str:
        return "spring"  # Force-directed to group control-gap clusters
    
    @property
    def help_text(self) -> str:
        return (
            "Defender for Cloud assessment. "
            "Red (Critical) = immediate action needed; Orange (High) = priority; "
            "Yellow (Medium) = schedule; Green (Low) = backlog. "
            "Edges show related control gaps. "
            "Node size = finding count (larger = more findings). "
            "Clusters = coordinated remediation needed. "
            "[Implementation pending: CSPM requirement mapping, control relationship inference]"
        )
    
    @property
    def annotations(self) -> list[str] | None:
        return [
            "Critical control gaps (remediate immediately)",
            "Related misconfiguration clusters",
            "CSPM policy violations by control family",
            "Blast radius of control gaps",
        ]
