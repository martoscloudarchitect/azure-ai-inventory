"""Supplementary queries for the observability and monitoring use case."""

SUPPLEMENTARY_QUERIES: list[dict] = [
    {
        "key": "diagnostic_settings",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type !in~ ("
            "'microsoft.managedidentity/userassignedidentities',"
            "'microsoft.insights/actiongroups',"
            "'microsoft.insights/activitylogalerts'"
            ")"
            " | extend hasDiag = isnotnull(properties.diagnosticSettings)"
            " | summarize total = count(), withDiag = countif(hasDiag)"
            " by type"
            " | extend withoutDiag = total - withDiag"
            " | order by withoutDiag desc"
        ),
    },
    {
        "key": "log_analytics_workspaces",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.operationalinsights/workspaces'"
            " | project name, resourceGroup, location,"
            " sku = properties.sku.name,"
            " retentionDays = properties.retentionInDays"
        ),
    },
    {
        "key": "app_insights",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.insights/components'"
            " | project name, resourceGroup, location,"
            " kind = kind,"
            " ingestionMode = properties.IngestionMode,"
            " retentionDays = properties.RetentionInDays"
        ),
    },
    {
        "key": "alert_rules",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type in~ ("
            "'microsoft.insights/metricalerts',"
            "'microsoft.insights/scheduledqueryrules',"
            "'microsoft.insights/activitylogalerts'"
            ")"
            " | project name, resourceGroup, type,"
            " enabled = properties.enabled,"
            " severity = properties.severity"
        ),
    },
    {
        "key": "action_groups",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.insights/actiongroups'"
            " | project name, resourceGroup,"
            " enabled = properties.enabled,"
            " emailReceivers = array_length(properties.emailReceivers),"
            " smsReceivers = array_length(properties.smsReceivers),"
            " webhookReceivers = array_length(properties.webhookReceivers)"
        ),
    },
    {
        "key": "network_watchers",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/networkwatchers'"
            " | project name, resourceGroup, location,"
            " provisioningState = properties.provisioningState"
        ),
    },
    {
        "key": "vm_extensions",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.compute/virtualmachines/extensions'"
            " | where name in~ ("
            "'AzureMonitorLinuxAgent','AzureMonitorWindowsAgent',"
            "'MicrosoftMonitoringAgent','OmsAgentForLinux'"
            ")"
            " | project name, resourceGroup,"
            " vmName = tostring(split(id, '/')[8]),"
            " publisher = properties.publisher,"
            " agentType = properties.type"
        ),
    },
]
