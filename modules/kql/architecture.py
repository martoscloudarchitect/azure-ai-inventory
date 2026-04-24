"""Supplementary queries for the architecture use case."""

SUPPLEMENTARY_QUERIES: list[dict] = [
    {
        "key": "resource_containers",
        "table": "ResourceContainers",
        "query": (
            "ResourceContainers"
            " | where type =~ 'microsoft.resources/subscriptions/resourcegroups'"
            " | project name, location, tags, properties"
        ),
    },
]
