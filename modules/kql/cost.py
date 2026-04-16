"""Supplementary queries for the cost optimization use case."""

SUPPLEMENTARY_QUERIES: list[dict] = [
    {
        "key": "advisor_cost",
        "table": "AdvisorResources",
        "query": (
            "AdvisorResources"
            " | where properties.category =~ 'Cost'"
            " | project name, resourceGroup,"
            " impact = properties.impact,"
            " recommendation = properties.shortDescription.solution"
        ),
    },
    {
        "key": "orphaned_disks",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.compute/disks'"
            " | where properties.diskState =~ 'Unattached'"
            " | project name, resourceGroup, location, sku,"
            " diskSizeGB = properties.diskSizeGB"
        ),
    },
    {
        "key": "app_service_plans",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.web/serverfarms'"
            " | project name, resourceGroup, location, sku,"
            " workerCount = properties.numberOfWorkers,"
            " zoneRedundant = properties.zoneRedundant"
        ),
    },
]
