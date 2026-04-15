"""Supplementary queries for the BCDR (Business Continuity / Disaster Recovery) use case."""

SUPPLEMENTARY_QUERIES: list[dict] = [
    {
        "key": "recovery_vaults",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.recoveryservices/vaults'"
            " | project name, type, location, resourceGroup, sku, properties"
        ),
    },
    {
        "key": "backup_items",
        "table": "RecoveryServicesResources",
        "query": (
            "RecoveryServicesResources"
            " | where type =~ 'microsoft.recoveryservices/vaults/backupfabrics"
            "/protectioncontainers/protecteditems'"
            " | project name, type, location, resourceGroup, properties"
        ),
    },
    {
        "key": "sql_failover_groups",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.sql/servers/failovergroups'"
            " | project name, resourceGroup, location, properties"
        ),
    },
    {
        "key": "storage_replication",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.storage/storageaccounts'"
            " | project name, resourceGroup, sku, location,"
            " accessTier = properties.accessTier,"
            " secondaryLocation = properties.secondaryLocation"
        ),
    },
    {
        "key": "vm_availability",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.compute/virtualmachines'"
            " | project name, resourceGroup, location, zones,"
            " availabilitySet = properties.availabilitySet,"
            " vmSize = properties.hardwareProfile.vmSize"
        ),
    },
]
