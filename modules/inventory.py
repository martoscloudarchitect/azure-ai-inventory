"""Query Azure Resource Graph and persist the results."""

import json
from pathlib import Path

from modules.az_cli import run, extract_json_payload

QUERY = (
    "Resources"
    " | project name, type, location, resourceGroup,"
    " subscriptionId, tags, sku, kind,"
    " provisioningState = properties.provisioningState"
    " | order by type asc"
)
PAGE_SIZE = "500"


def fetch(output_file: Path) -> list[dict]:
    """Run the Resource Graph query, save JSON, and return the resource list."""
    print("Collecting Azure inventory through Resource Graph...")
    raw_output = run([
        "graph", "query",
        "-q", QUERY,
        "--first", PAGE_SIZE,
        "--output", "json",
        "--only-show-errors",
    ])

    inventory_text = extract_json_payload(raw_output)
    output_file.write_text(inventory_text, encoding="utf-8")

    inventory_result = json.loads(inventory_text)
    return inventory_result.get("data", [])


def print_stats(resources: list[dict]) -> None:
    """Print resource count and per-region breakdown."""
    print(f"Found {len(resources)} resources")

    region_counts: dict[str, int] = {}
    for r in resources:
        region = (r.get("location") or "unknown").lower()
        region_counts[region] = region_counts.get(region, 0) + 1

    print("Resources per region:")
    for region, count in sorted(region_counts.items(), key=lambda x: -x[1]):
        print(f"  - {region}: {count}")
