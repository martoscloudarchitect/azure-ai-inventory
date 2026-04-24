"""Query Azure Resource Graph and persist the results."""

import json
import math
from pathlib import Path

from modules.az_cli import run, extract_json_payload
from modules import kql


def _run_graph_query(query: str, page_size: int,
                     label: str | None = None) -> tuple[list[dict], dict]:
    """Execute a Resource Graph query with automatic pagination.

    Returns ``(rows, stats)`` where *stats* is a dict with pagination
    metrics: ``rows``, ``page_size``, ``pages``, ``last_page_fill_pct``.
    """

    all_data: list[dict] = []
    skip = 0
    page_num = 0

    while True:
        page_num += 1
        args = [
            "graph", "query",
            "-q", query,
            "--first", str(page_size),
            "--skip", str(skip),
            "--output", "json",
            "--only-show-errors",
        ]
        raw_output = run(args)
        text = extract_json_payload(raw_output)
        result = json.loads(text)
        page = result.get("data", [])
        all_data.extend(page)

        if label:
            print(
                f"    {label} — page {page_num}: "
                f"{len(page)} rows (running total: {len(all_data)})"
            )

        if len(page) < page_size:
            break
        skip += page_size

    stats = _pagination_stats(label or "query", len(all_data), page_size)
    return all_data, stats


def _pagination_stats(label: str, total_rows: int, page_size: int) -> dict:
    """Return a dict of pagination metrics and print a one-line summary."""
    pages = math.ceil(total_rows / page_size) if total_rows else 0
    last_page_fill = (
        round((total_rows % page_size) / page_size * 100, 1)
        if total_rows and total_rows % page_size
        else 100.0 if total_rows else 0.0
    )
    print(
        f"  [{label}] {total_rows} rows | page_size={page_size} | "
        f"pages={pages} | last page fill={last_page_fill}%"
    )
    return {
        "label": label,
        "rows": total_rows,
        "page_size": page_size,
        "pages": pages,
        "last_page_fill_pct": last_page_fill,
    }


def fetch_summary(output_file: Path, page_size: int) -> tuple[dict, list[dict]]:
    """Run lightweight discovery queries and return ``(summary, query_stats)``.

    The summary is small and fixed-size regardless of tenant scale, making it
    safe to send directly to the LLM for the Phase 1 Environment Brief.
    ``query_stats`` is a list of per-query pagination metric dicts.
    """
    print("\n=== Phase 1: Environment Discovery ===")
    print(f"  Resource Graph PAGE_SIZE: {page_size}")
    print("Collecting environment summary from Resource Graph...")

    summary: dict[str, list[dict]] = {}
    query_stats: list[dict] = []
    for sq in kql.get_discovery_queries():
        key = sq["key"]
        try:
            data, stats = _run_graph_query(sq["query"], page_size, label=f"discovery/{key}")
            summary[key] = data
            query_stats.append(stats)
        except RuntimeError as exc:
            print(f"  WARNING: discovery query '{key}' failed ({exc}), skipping.")
            summary[key] = []

    # Print a quick human-readable headline.
    totals = summary.get("totals", [{}])[0] if summary.get("totals") else {}
    res_count = totals.get("resource_count", "?")
    sub_count = totals.get("subscription_count", "?")
    rg_count = totals.get("resource_group_count", "?")
    region_count = totals.get("region_count", "?")
    print(
        f"  Total resources: {res_count} across {sub_count} subscription(s), "
        f"{rg_count} resource group(s), {region_count} region(s)"
    )

    output_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"  Discovery summary saved to: {output_file}")
    return summary, query_stats


def fetch(output_file: Path, profile: str = "architecture",
          page_size: int = 500) -> tuple[dict, list[dict]]:
    """Run base + supplementary queries, save JSON, and return ``(combined, query_stats)``.

    ``combined`` has at least an ``"inventory"`` key containing the base
    resource list.  Profile-specific supplementary data is stored under
    additional keys (e.g. ``"recovery_vaults"``, ``"nsg_rules"``).
    ``query_stats`` is a list of per-query pagination metric dicts.
    """
    print(f"\nCollecting Azure inventory through Resource Graph (page_size={page_size})...")
    base_data, base_stats = _run_graph_query(kql.get_base_query(), page_size, label="base inventory")

    query_stats: list[dict] = [base_stats]
    supplements: dict[str, list[dict]] = {}
    for sq in kql.get_supplementary_queries(profile):
        key = sq["key"]
        try:
            print(f"  Running supplementary query: {key}...")
            data, stats = _run_graph_query(sq["query"], page_size, label=key)
            supplements[key] = data
            query_stats.append(stats)
        except RuntimeError as exc:
            print(f"    -> WARNING: {key} query failed ({exc}), skipping.")
            supplements[key] = []

    combined: dict = {"inventory": base_data, **supplements}
    output_file.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    return combined, query_stats


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
