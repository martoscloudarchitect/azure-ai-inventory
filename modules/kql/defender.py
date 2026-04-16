"""Supplementary queries for the Defender for Cloud use case.

Covers foundational, high-risk, and most-exploitable misconfigurations
aligned with Microsoft Defender for Cloud / CSPM best practices.
"""

SUPPLEMENTARY_QUERIES: list[dict] = [
    # ── Storage Security ─────────────────────────────────────────────────
    {
        "key": "storage_public_access",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.storage/storageaccounts'"
            " | extend allowBlobPublicAccess = properties.allowBlobPublicAccess"
            " | where allowBlobPublicAccess == true"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    {
        "key": "storage_no_secure_transfer",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.storage/storageaccounts'"
            " | where properties.supportsHttpsTrafficOnly == false"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    {
        "key": "storage_no_encryption",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.storage/storageaccounts'"
            " | where properties.encryption.services.blob.enabled == false"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    # ── Network Exposure & Attack Surface ────────────────────────────────
    {
        "key": "vms_with_public_ip",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.compute/virtualmachines'"
            " | extend publicIp = properties.networkProfile.networkInterfaces[0]"
            ".properties.ipConfigurations[0].properties.publicIPAddress.id"
            " | where isnotempty(publicIp)"
            " | project name, resourceGroup, subscriptionId, publicIp"
        ),
    },
    {
        "key": "nsg_allow_any_inbound",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/networksecuritygroups'"
            " | mv-expand rules = properties.securityRules"
            " | where rules.properties.access == 'Allow'"
            " | where rules.properties.sourceAddressPrefix in ('*', '0.0.0.0/0')"
            " | project nsg = name, rule = rules.name,"
            " direction = rules.properties.direction"
        ),
    },
    {
        "key": "subnets_without_nsg",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.network/virtualnetworks/subnets'"
            " | extend nsg = properties.networkSecurityGroup.id"
            " | where isempty(nsg)"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    # ── Compute & VM Security ────────────────────────────────────────────
    {
        "key": "vms_no_disk_encryption",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.compute/virtualmachines'"
            " | extend encryption = properties.storageProfile.osDisk.encryptionSettings"
            " | where isempty(encryption)"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    {
        "key": "vms_no_endpoint_protection",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.compute/virtualmachines'"
            " | extend av = properties.extended.instanceView.vmAgent.extensionHandlers"
            " | where isempty(av)"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    # ── Key Vault Security ───────────────────────────────────────────────
    {
        "key": "keyvault_public_access",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.keyvault/vaults'"
            " | extend publicNetworkAccess = properties.networkAcls.defaultAction"
            " | where publicNetworkAccess == 'Allow'"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    {
        "key": "keyvault_no_soft_delete",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.keyvault/vaults'"
            " | extend softDelete = properties.enableSoftDelete,"
            " purgeProtection = properties.enablePurgeProtection"
            " | where softDelete == false or purgeProtection == false"
            " | project name, softDelete, purgeProtection"
        ),
    },
    # ── SQL & Database Security ──────────────────────────────────────────
    {
        "key": "sql_no_tls",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.sql/servers'"
            " | extend minimalTlsVersion = properties.minimalTlsVersion"
            " | where minimalTlsVersion == 'None' or isempty(minimalTlsVersion)"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    {
        "key": "sql_no_tde",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.sql/servers/databases'"
            " | extend tde = properties.encryptionProtector"
            " | where isempty(tde)"
            " | project name, resourceGroup, subscriptionId"
        ),
    },
    # ── Defender for Cloud / CSPM Coverage ───────────────────────────────
    {
        "key": "defender_free_tier",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.security/pricings'"
            " | where properties.pricingTier == 'Free'"
            " | project subscriptionId, resourceType = name,"
            " tier = properties.pricingTier"
        ),
    },
    {
        "key": "defender_no_servers",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.security/pricings'"
            " | where name == 'VirtualMachines'"
            " | where properties.pricingTier == 'Free'"
            " | project subscriptionId"
        ),
    },
    # ── Identity & Access ────────────────────────────────────────────────
    {
        "key": "subscriptions_no_rbac",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.authorization/roleassignments'"
            " | summarize count() by subscriptionId"
            " | where count_ == 0"
        ),
    },
    {
        "key": "wildcard_permissions",
        "table": "Resources",
        "query": (
            "Resources"
            " | where type =~ 'microsoft.authorization/roledefinitions'"
            " | mv-expand perms = properties.permissions"
            " | where perms.actions contains '*'"
            " | project name, roleName = properties.roleName"
        ),
    },
]
