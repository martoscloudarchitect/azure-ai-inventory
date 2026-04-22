"""Lightweight summary queries for the Phase 1 environment discovery."""

# Each query returns a small, fixed-size result set regardless of tenant size.
# The "key" is used to store results in the summary dict sent to the LLM.

SUMMARY_QUERIES: list[dict] = [
    {
        "key": "totals",
        "query": (
            "Resources"
            " | summarize"
            "     resource_count = count(),"
            "     resource_group_count = dcount(resourceGroup),"
            "     subscription_count = dcount(subscriptionId),"
            "     region_count = dcount(location)"
        ),
    },
    {
        "key": "by_type",
        "query": (
            "Resources"
            " | summarize count_ = count() by type"
            " | order by count_ desc"
            " | take 30"
        ),
    },
    {
        "key": "by_region",
        "query": (
            "Resources"
            " | summarize count_ = count() by location"
            " | order by count_ desc"
        ),
    },
    {
        "key": "by_resource_group",
        "query": (
            "Resources"
            " | summarize count_ = count() by resourceGroup, subscriptionId"
            " | order by count_ desc"
            " | take 50"
        ),
    },
    {
        "key": "by_subscription",
        "query": (
            "Resources"
            " | summarize"
            "     count_ = count(),"
            "     rg_count = dcount(resourceGroup)"
            " by subscriptionId"
            " | order by count_ desc"
        ),
    },
    {
        "key": "by_sku",
        "query": (
            "Resources"
            " | where isnotempty(sku)"
            " | summarize count_ = count() by type, sku_name = tostring(sku.name)"
            " | order by count_ desc"
            " | take 30"
        ),
    },
    {
        "key": "by_provisioning_state",
        "query": (
            "Resources"
            " | summarize count_ = count()"
            "     by provisioningState = tostring(properties.provisioningState)"
        ),
    },
]
