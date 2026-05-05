"""Observability profile graph adapter (stub).

Emphasizes monitoring coverage, alerting chains, and diagnostic relationships.
"""

from modules.graph_profiles.base import (
    ProfileGraphAdapter,
    NodeStyleConfig,
    EdgeStyleConfig,
    FilterConfig,
)


class ObservabilityGraphAdapter(ProfileGraphAdapter):
    """Graph adapter for Observability profile visualization.
    
    TODO: Implement monitoring coverage and alerting chain visualization.
    Currently uses default behavior.
    """
    
    @property
    def profile_name(self) -> str:
        return "observability"
    
    @property
    def profile_label(self) -> str:
        return "Monitoring & Observability"
    
    @property
    def relationship_types(self) -> list[str]:
        return [
            "parent_child",
            "monitoring_coverage",
            "alerting_chains",
            "diagnostic_flow",
        ]
    
    @property
    def node_style(self) -> NodeStyleConfig:
        return NodeStyleConfig(
            color_dimension="monitoring_coverage",  # monitored, partial, unmonitored
            color_palette="coverage_state",
            size_dimension="log_volume_gb_per_day",
            size_scale=1.5,
        )
    
    @property
    def edge_style(self) -> EdgeStyleConfig:
        return EdgeStyleConfig(
            color_field="signal_type",
            color_map={
                "logs": "#0078D4",    # Blue
                "metrics": "#107C10", # Green
                "traces": "#FF8C00",  # Orange
                "default": "#888888",
            },
            show_labels=True,
            label_field="signal_type",
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
        return "spring"  # Force-directed to group monitoring domains
    
    @property
    def help_text(self) -> str:
        return (
            "Observability topology. "
            "Green nodes = monitored; Orange = partial coverage; Red = unmonitored. "
            "Blue edges = logs; Green = metrics; Orange = traces. "
            "Node size = log volume (larger = higher ingestion). "
            "[Implementation pending: alert rule visualization, diagnostic flow mapping]"
        )
    
    @property
    def annotations(self) -> list[str] | None:
        return [
            "Unmonitored resources (monitoring blind spots)",
            "High-volume resources without alerting",
            "Missing diagnostic settings",
            "Alert rule coverage gaps",
        ]
