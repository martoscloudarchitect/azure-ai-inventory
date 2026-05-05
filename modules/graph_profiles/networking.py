"""Networking profile graph adapter.

Emphasizes VNet topology, segmentation, private endpoints, and NSG relationships.
"""

from modules.graph_profiles.base import (
    ProfileGraphAdapter,
    NodeStyleConfig,
    EdgeStyleConfig,
    FilterConfig,
)


class NetworkingGraphAdapter(ProfileGraphAdapter):
    """Graph adapter for Networking profile visualization."""
    
    @property
    def profile_name(self) -> str:
        return "networking"
    
    @property
    def profile_label(self) -> str:
        return "Network Topology"
    
    @property
    def relationship_types(self) -> list[str]:
        return [
            "network_hierarchy",
            "segmentation_rules",
            "private_endpoints",
            "regional_peering",
        ]
    
    @property
    def node_style(self) -> NodeStyleConfig:
        return NodeStyleConfig(
            color_dimension="resource_type",  # VNet, Subnet, NIC, VM, NSG
            color_palette="network_topology",
            size_dimension="ip_utilization",
            size_scale=1.5,
        )
    
    @property
    def edge_style(self) -> EdgeStyleConfig:
        return EdgeStyleConfig(
            color_field="nsg_action",
            color_map={
                "allow": "#107C10",    # Green (allowed)
                "deny": "#D13438",     # Red (denied)
                "peering": "#0078D4",  # Blue (peering)
                "default": "#888888",  # Gray
            },
            show_labels=True,
            label_field="nsg_action",
        )
    
    @property
    def default_filters(self) -> list[FilterConfig]:
        return [
            FilterConfig(
                field="resource_type",
                values=[
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/virtualNetworks/subnets",
                    "Microsoft.Network/networkInterfaces",
                    "Microsoft.Network/networkSecurityGroups",
                    "Microsoft.Network/publicIPAddresses",
                    "Microsoft.Compute/virtualMachines",
                ],
                include=True,
            ),
        ]
    
    @property
    def layout_algorithm(self) -> str:
        return "hierarchical"  # VNet → Subnet → NIC → VM hierarchy
    
    @property
    def help_text(self) -> str:
        return (
            "Network topology. "
            "Nodes show VNet/Subnet/NIC/VM structure; colored by resource type. "
            "Green edges = allowed traffic; Red edges = denied/NSG rules. "
            "Blue edges = VNet peering. "
            "Node size = IP utilization (subnets) or NICs (VMs). "
            "Reveals segmentation gaps and over-permissive rules."
        )
    
    @property
    def annotations(self) -> list[str] | None:
        return [
            "Under-segmented subnets (all traffic allowed)",
            "Missing NSG rules (unprotected subnets)",
            "Private endpoint deployment patterns",
            "Cross-region peering topology",
        ]
