"""Supplementary queries for the security use case."""

SUPPLEMENTARY_QUERIES: list[dict] = [
    {
        "key": "security_assessments",
        "table": "SecurityResources",
        "query": (
            "SecurityResources"
            " | where type =~ 'microsoft.security/assessments'"
            " | where properties.status.code =~ 'Unhealthy'"
            " | project name, resourceGroup,"
            " severity = properties.metadata.severity,"
            " description = properties.displayName,"
            " resourceId = properties.resourceDetails.Id"
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
        "key": "public_ips",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/publicipaddresses'"
            " | project name, resourceGroup, location,"
            " ipAddress = properties.ipAddress,"
            " associatedTo = properties.ipConfiguration.id"
        ),
    },
    {
        "key": "key_vaults",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.keyvault/vaults'"
            " | project name, resourceGroup, location,"
            " enableSoftDelete = properties.enableSoftDelete,"
            " enablePurgeProtection = properties.enablePurgeProtection,"
            " networkAcls = properties.networkAcls"
        ),
    },
]
