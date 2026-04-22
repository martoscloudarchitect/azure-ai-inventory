"""Export resource inventory to CSV with derived columns."""

import csv
from pathlib import Path

# Columns written to the CSV in order.
CSV_COLUMNS = [
    "name",
    "type",
    "service_category",
    "service_short_type",
    "is_child_resource",
    "location",
    "resource_group",
    "subscription_id",
    "kind",
    "sku_name",
    "provisioning_state",
    "iac_hint",
    "tags",
]

IAC_TAG_KEYWORDS = ["terraform", "bicep", "pulumi", "arm", "iac"]


def _derive_row(resource: dict) -> dict:
    """Build a flat CSV row from a raw Resource Graph record."""
    rtype = resource.get("type") or ""
    parts = rtype.split("/", 2)  # e.g. microsoft.network / virtualnetworks / subnets
    service_category = parts[0] if parts else ""
    service_short_type = parts[1] if len(parts) > 1 else ""
    is_child = len(parts) > 2

    tags = resource.get("tags") or {}
    tags_flat = "; ".join(f"{k}={v}" for k, v in tags.items()) if isinstance(tags, dict) else str(tags)

    sku = resource.get("sku") or {}
    sku_name = sku.get("name", "") if isinstance(sku, dict) else str(sku)

    # Detect IaC hints from tags.
    iac_hint = "unknown"
    if isinstance(tags, dict):
        combined = " ".join(f"{k} {v}" for k, v in tags.items()).lower()
        for keyword in IAC_TAG_KEYWORDS:
            if keyword in combined:
                iac_hint = keyword
                break

    return {
        "name": resource.get("name", ""),
        "type": rtype,
        "service_category": service_category,
        "service_short_type": service_short_type,
        "is_child_resource": str(is_child),
        "location": resource.get("location", ""),
        "resource_group": resource.get("resourceGroup", ""),
        "subscription_id": resource.get("subscriptionId", ""),
        "kind": resource.get("kind", ""),
        "sku_name": sku_name,
        "provisioning_state": resource.get("provisioningState", ""),
        "iac_hint": iac_hint,
        "tags": tags_flat,
    }


def export(resources: list[dict], output_file: Path) -> None:
    """Write the resource list to a CSV file."""
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for resource in resources:
            writer.writerow(_derive_row(resource))
    print(f"CSV export saved to: {output_file}")
