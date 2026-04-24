"""Base inventory query shared by all use-case profiles."""

QUERY = (
    "Resources"
    " | project id, name, type, location, resourceGroup,"
    " subscriptionId, tags, sku, kind, identity,"
    " provisioningState = properties.provisioningState,"
    " properties"
    " | order by type asc"
)
