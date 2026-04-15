"""Supplementary queries for the governance use case."""

SUPPLEMENTARY_QUERIES: list[dict] = [
    {
        "key": "policy_compliance",
        "table": "PolicyResources",
        "query": (
            "PolicyResources"
            " | where type =~ 'microsoft.policyinsights/policystates'"
            " | where properties.complianceState =~ 'NonCompliant'"
            " | project name, resourceGroup,"
            " policyName = properties.policyDefinitionName,"
            " complianceState = properties.complianceState"
        ),
    },
    {
        "key": "resource_groups",
        "table": "ResourceContainers",
        "query": (
            "ResourceContainers"
            " | where type =~ 'microsoft.resources/subscriptions/resourcegroups'"
            " | project name, location, tags, properties"
        ),
    },
]
