"""Canonical constants and configuration shared across modules."""

# ============================================================================
# REPORT DISCLAIMER
# ============================================================================
# Single source of truth for the disclaimer.
# Used in:
#   - Streamlit pages (displayed as banner)
#   - Exported .md files (prepended to output)
# NOT sent to LLM in prompts to save tokens (~750 per call).

REPORT_DISCLAIMER = """
> **Disclaimer — Proof of Concept · Not for Production Decisions**
>
> This report was generated automatically by **AI Inventory Architect**, an open-source scaffold project in **proof-of-concept (POC) stage**. The analysis relies on AI-generated interpretations of Azure Resource Graph data and is subject to inherent limitations including hard-coded defaults, token limits, model reasoning constraints, and incomplete resource visibility.
>
> **This output does not constitute professional advice and must not be used as the sole basis for architectural, security, compliance, or financial decisions.** No commercial warranty, liability, or accountability is implied.
>
> The value of this tool lies in demonstrating how automated inventory collection, structured normalization, and AI-powered analysis can accelerate cloud governance workflows. Organizations are encouraged to evaluate this scaffold with their internal engineering teams or with a trusted Microsoft partner to build a responsible, production-grade solution tailored to their Azure environment and its specific requirements.
"""

# ============================================================================
# RESOURCE TYPE PRIORITIES FOR SAMPLING
# ============================================================================
# Used by inventory_optimizer to determine which resource types to keep
# when sampling large inventories.
# Higher number = keep first when sampling.
# Critical types (>= 80) are never dropped during sampling.

RESOURCE_TYPE_PRIORITIES = {
    # Compute & Application Services (100–110)
    "Microsoft.Compute/virtualMachines": 110,
    "Microsoft.Web/sites": 105,
    "Microsoft.Web/serverFarms": 103,
    "Microsoft.ContainerRegistry/registries": 102,
    "Microsoft.ContainerService/managedClusters": 101,
    
    # Databases & Data Services (95–99)
    "Microsoft.Sql/servers/databases": 99,
    "Microsoft.Sql/servers": 98,
    "Microsoft.DBforPostgreSQL/servers": 97,
    "Microsoft.DBforMySQL/servers": 96,
    "Microsoft.DocumentDB/databaseAccounts": 95,
    "Microsoft.Cache/redis": 94,
    
    # Networking (90–94)
    "Microsoft.Network/virtualNetworks": 94,
    "Microsoft.Network/networkSecurityGroups": 93,
    "Microsoft.Network/loadBalancers": 92,
    "Microsoft.Network/networkInterfaces": 91,
    "Microsoft.Network/publicIPAddresses": 90,
    
    # Storage & Data (85–89)
    "Microsoft.Storage/storageAccounts": 89,
    "Microsoft.Storage/storageAccounts/blobServices": 88,
    "Microsoft.DataFactory/factories": 87,
    "Microsoft.Synapse/workspaces": 86,
    
    # Security & Governance (80–84)
    "Microsoft.KeyVault/vaults": 84,
    "Microsoft.Authorization/locks": 83,
    "Microsoft.Authorization/policyDefinitions": 82,
    
    # Monitoring (75–79)
    "Microsoft.Insights/components": 79,
    "Microsoft.Insights/workbooks": 78,
    "Microsoft.OperationalInsights/workspaces": 77,
    "Microsoft.Insights/scheduledqueryrules": 76,
    
    # Supporting Services (50–74)
    "Microsoft.Automation/automationAccounts": 74,
    "Microsoft.Search/searchServices": 73,
    "Microsoft.ServiceBus/namespaces": 72,
    "Microsoft.EventHub/namespaces": 71,
    "Microsoft.Logic/workflows": 70,
    "Microsoft.RecoveryServices/vaults": 69,
    
    # Low-value/Supporting Resources (1–49)
    "Microsoft.ManagedIdentity/userAssignedIdentities": 10,
    "Microsoft.Insights/diagnosticSettings": 5,
    "Microsoft.Insights/actionGroups": 4,
    "Microsoft.Insights/metricAlerts": 3,
    "Microsoft.Authorization/roleDefinitions": 2,
    
    # Default for unknown types
    "__default__": 30,
}

# ============================================================================
# PROFILE-SPECIFIC RESOURCE FILTERS
# ============================================================================
# Maps profile ID → set of resource type prefixes to prioritize.
# When sampling for a profile, only these types are considered "relevant".
# Types not in the list are lower priority for keeping.

PROFILE_RESOURCE_FILTERS = {
    "architecture": {
        # Keep everything for general architecture review
        "__all__": True,
    },
    
    "security": {
        # Security focus: VMs, storage, networking, key vaults, SQL, NSGs
        "Microsoft.Compute/virtualMachines",
        "Microsoft.Storage/storageAccounts",
        "Microsoft.KeyVault/vaults",
        "Microsoft.Sql/servers",
        "Microsoft.Network/networkSecurityGroups",
        "Microsoft.Network/virtualNetworks",
        "Microsoft.Web/sites",
        "Microsoft.ManagedIdentity",
        "Microsoft.Authorization",
        "Microsoft.ContainerService",
    },
    
    "observability": {
        # Observability focus: VMs, App Services, databases, monitoring
        "Microsoft.Compute/virtualMachines",
        "Microsoft.Web/sites",
        "Microsoft.Sql/servers",
        "Microsoft.DBforPostgreSQL/servers",
        "Microsoft.Insights/components",
        "Microsoft.OperationalInsights/workspaces",
        "Microsoft.Insights/scheduledqueryrules",
        "Microsoft.Cache/redis",
        "Microsoft.ServiceBus/namespaces",
    },
    
    "governance": {
        # Governance needs full view for tagging audit
        "__all__": True,
    },
    
    "networking": {
        # Networking focus: VNets, NSGs, peerings, private endpoints, DNS
        "Microsoft.Network/virtualNetworks",
        "Microsoft.Network/networkSecurityGroups",
        "Microsoft.Network/virtualNetworks/subnets",
        "Microsoft.Network/virtualNetworkPeerings",
        "Microsoft.Network/privateDnsZones",
        "Microsoft.Network/privateEndpoints",
        "Microsoft.Network/loadBalancers",
        "Microsoft.Network/applicationGateways",
        "Microsoft.Network/firewallPolicies",
        "Microsoft.Network/expressRouteCircuits",
    },
    
    "bcdr": {
        # BCDR focus: VMs, databases, storage, recovery, traffic managers
        "Microsoft.Compute/virtualMachines",
        "Microsoft.Sql/servers",
        "Microsoft.DBforPostgreSQL/servers",
        "Microsoft.Storage/storageAccounts",
        "Microsoft.RecoveryServices/vaults",
        "Microsoft.Network/trafficManagerProfiles",
        "Microsoft.Network/loadBalancers",
        "Microsoft.Cache/redis",
    },
    
    "defender": {
        # Defender focus: storage, compute, keyvault, sql, networking
        "Microsoft.Storage/storageAccounts",
        "Microsoft.Compute/virtualMachines",
        "Microsoft.KeyVault/vaults",
        "Microsoft.Sql/servers",
        "Microsoft.Network/networkSecurityGroups",
        "Microsoft.Web/sites",
        "Microsoft.ManagedIdentity",
        "Microsoft.Authorization",
    },
}

# ============================================================================
# TOKEN ESTIMATION CONSTANTS
# ============================================================================
# Empirically determined ratio for converting text size to token count.
# Based on observed data: 120 KB JSON with ~26,963 tokens = ~224 tokens/KB

TOKENS_PER_KB = 224

# Maximum input tokens for Azure OpenAI (default)
DEFAULT_MAX_INPUT_TOKENS = 272000

# Resource count thresholds for sampling
SAMPLING_THRESHOLD_MIN = 100      # Start sampling at 100 resources
SAMPLING_THRESHOLD_MEDIUM = 300   # More aggressive sampling at 300
SAMPLING_THRESHOLD_LARGE = 500    # Strict sampling at 500

# Target percentages for sampling
SAMPLING_TARGET_PCT_SMALL = 0.80    # Keep 80% for 100–300 resources
SAMPLING_TARGET_PCT_MEDIUM = 0.60   # Keep 60% for 300–500 resources
SAMPLING_TARGET_PCT_LARGE = 0.40    # Keep 40% for 500+ resources

# ============================================================================
# CRITICAL RESOURCE TYPES (NEVER DROPPED DURING SAMPLING)
# ============================================================================
# These types are so important that they should always be kept when sampling,
# even if it means exceeding the target sample size slightly.

CRITICAL_RESOURCE_TYPES = {
    "Microsoft.Compute/virtualMachines",
    "Microsoft.Web/sites",
    "Microsoft.Sql/servers/databases",
    "Microsoft.Sql/servers",
    "Microsoft.DBforPostgreSQL/servers",
    "Microsoft.DBforMySQL/servers",
    "Microsoft.DocumentDB/databaseAccounts",
    "Microsoft.Network/virtualNetworks",
    "Microsoft.KeyVault/vaults",
    "Microsoft.ContainerService/managedClusters",
    "Microsoft.Storage/storageAccounts",
}
