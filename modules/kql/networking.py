"""Supplementary queries for the networking use case."""

SUPPLEMENTARY_QUERIES: list[dict] = [
    {
        "key": "virtual_networks",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/virtualnetworks'"
            " | project name, resourceGroup, location,"
            " addressSpace = properties.addressSpace,"
            " subnets = properties.subnets,"
            " peerings = properties.virtualNetworkPeerings"
        ),
    },
    {
        "key": "private_endpoints",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/privateendpoints'"
            " | project name, resourceGroup, location,"
            " targetResource = properties.privateLinkServiceConnections"
        ),
    },
    {
        "key": "private_dns_zones",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/privatednszones'"
            " | project name, resourceGroup, location"
        ),
    },
    {
        "key": "nsg_rules",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/networksecuritygroups'"
            " | project name, resourceGroup, location,"
            " rules = properties.securityRules"
        ),
    },
    {
        "key": "route_tables",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/routetables'"
            " | project name, resourceGroup, location,"
            " routes = properties.routes"
        ),
    },
]
