"""Static KQL query reference page."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from modules.kql import get_base_query, get_discovery_queries, get_supplementary_queries


PROFILE_SEQUENCE = [
    "base",
    "discovery",
    "architecture",
    "bcdr",
    "security",
    "observability",
    "governance",
    "networking",
    "defender",
]

PROFILE_LABELS = {
    "base": "Base Inventory",
    "discovery": "Discovery",
    "architecture": "Architecture",
    "bcdr": "BCDR",
    "security": "Security",
    "observability": "Observability",
    "governance": "Governance",
    "networking": "Networking",
    "defender": "Defender",
}


@dataclass
class QuerySpec:
    sequence: int
    profile: str
    key: str
    table: str
    query: str


def _normalize_query(query: str) -> str:
    return query.strip()


def _format_kql_for_display(query: str) -> str:
    """Pretty-format compact KQL into readable multi-line clauses."""
    compact = " ".join(query.split())
    segments = [segment.strip() for segment in compact.split("|") if segment.strip()]

    formatted_lines: list[str] = []
    for index, segment in enumerate(segments):
        if index == 0:
            formatted_lines.append(segment)
            continue

        lower_segment = segment.lower()
        if lower_segment.startswith("project "):
            formatted_lines.append("| project")
            project_items = [item.strip() for item in segment[8:].split(",") if item.strip()]
            for item in project_items:
                formatted_lines.append(f"    {item},")
            if project_items:
                formatted_lines[-1] = formatted_lines[-1].rstrip(",")
            continue

        if lower_segment.startswith("summarize "):
            formatted_lines.append("| summarize")
            summary_body = segment[10:]
            if " by " in summary_body.lower():
                split_at = summary_body.lower().rfind(" by ")
                aggregate_part = summary_body[:split_at].strip()
                by_part = summary_body[split_at + 4:].strip()

                aggregates = [item.strip() for item in aggregate_part.split(",") if item.strip()]
                for item in aggregates:
                    formatted_lines.append(f"    {item},")
                if aggregates:
                    formatted_lines[-1] = formatted_lines[-1].rstrip(",")

                formatted_lines.append(f"    by {by_part}")
            else:
                aggregates = [item.strip() for item in summary_body.split(",") if item.strip()]
                for item in aggregates:
                    formatted_lines.append(f"    {item},")
                if aggregates:
                    formatted_lines[-1] = formatted_lines[-1].rstrip(",")
            continue

        if lower_segment.startswith("extend "):
            formatted_lines.append("| extend")
            extend_items = [item.strip() for item in segment[7:].split(",") if item.strip()]
            for item in extend_items:
                formatted_lines.append(f"    {item},")
            if extend_items:
                formatted_lines[-1] = formatted_lines[-1].rstrip(",")
            continue

        formatted_lines.append(f"| {segment}")

    return "\n".join(formatted_lines)


def _humanize_key(key: str) -> str:
    return key.replace("_", " ").title()


def _build_catalog() -> list[QuerySpec]:
    catalog: list[QuerySpec] = []
    seq = 1

    catalog.append(
        QuerySpec(
            sequence=seq,
            profile="base",
            key="base_inventory",
            table="Resources",
            query=_normalize_query(get_base_query()),
        )
    )
    seq += 1

    for item in get_discovery_queries():
        catalog.append(
            QuerySpec(
                sequence=seq,
                profile="discovery",
                key=item.get("key", "unknown"),
                table="Resources",
                query=_normalize_query(item.get("query", "")),
            )
        )
        seq += 1

    for profile in PROFILE_SEQUENCE:
        if profile in ("base", "discovery"):
            continue
        for item in get_supplementary_queries(profile):
            catalog.append(
                QuerySpec(
                    sequence=seq,
                    profile=profile,
                    key=item.get("key", "unknown"),
                    table=item.get("table", "Resources"),
                    query=_normalize_query(item.get("query", "")),
                )
            )
            seq += 1

    return catalog


def _derive_description(spec: QuerySpec) -> str:
    if spec.profile == "base":
        return (
            "This baseline query extracts tenant-wide resource metadata and core properties. "
            "It provides the common inventory foundation used by every profile before deeper checks run."
        )

    if spec.profile == "discovery":
        return (
            "This discovery query summarizes footprint shape for fast triage. "
            "It is designed to quickly characterize size, spread, and dominant patterns before deep collection."
        )

    return (
        f"This {PROFILE_LABELS.get(spec.profile, spec.profile)} query focuses on {_humanize_key(spec.key).lower()} evidence "
        "to enrich profile-specific analysis beyond the baseline inventory."
    )


def _derive_value(spec: QuerySpec) -> str:
    if spec.profile in ("base", "discovery"):
        return (
            "Operational value: supports fast scoping, profile selection, and prioritization by grounding assessments "
            "in consistent, comparable data points."
        )

    return (
        "Operational value: provides concrete, profile-targeted signals that can drive recommendations, "
        "risk prioritization, and evidence-based report narratives."
    )


def _derive_limitations(_spec: QuerySpec) -> str:
    return (
        "Scale limitations: In medium footprints, nested properties and high-cardinality fields may increase response size and review effort. "
        "In large footprints, full-table scans and broad projections can increase query latency and payload volume; use scope filters, "
        "projection trimming, and partitioned collection by subscription or region where needed."
    )


def _render_query_card(spec: QuerySpec, use_formatted: bool) -> None:
    st.markdown(f"### {spec.sequence}. {PROFILE_LABELS.get(spec.profile, spec.profile)} - {_humanize_key(spec.key)}")

    info_cols = st.columns([1, 1, 2])
    info_cols[0].markdown(f"**Profile**: {PROFILE_LABELS.get(spec.profile, spec.profile)}")
    info_cols[1].markdown(f"**Table**: {spec.table}")
    info_cols[2].markdown(f"**Key**: {spec.key}")

    st.markdown("**What this query does**")
    st.write(_derive_description(spec))

    st.markdown("**Value**")
    st.write(_derive_value(spec))

    st.markdown("**Limitations for medium and large Azure footprints**")
    st.write(_derive_limitations(spec))

    st.markdown("**KQL syntax**")
    if use_formatted:
        st.code(_format_kql_for_display(spec.query), language="sql")
    else:
        st.code(spec.query, language="sql")
    st.divider()


st.title("Query_Specs")
st.caption("Static KQL reference in execution sequence for all profiles.")

query_catalog = _build_catalog()

profile_options = ["all"] + [p for p in PROFILE_SEQUENCE]
selected_profile = st.selectbox(
    "Filter by profile",
    options=profile_options,
    format_func=lambda p: "All" if p == "all" else PROFILE_LABELS.get(p, p.title()),
)

format_kql_output = st.toggle(
    "Display formatted KQL (multi-line grouped clauses)",
    value=True,
    help="Breaks one-line KQL into readable rows by pipeline and clause.",
)

with st.expander("View summary", expanded=True):
    total_queries = len(query_catalog)
    profile_count = len({item.profile for item in query_catalog})
    st.markdown(f"**Total queries in sequence:** {total_queries}")
    st.markdown(f"**Profiles represented:** {profile_count}")

if selected_profile == "all":
    filtered = query_catalog
else:
    filtered = [item for item in query_catalog if item.profile == selected_profile]

st.markdown(f"### Showing {len(filtered)} query entries")

for query_item in filtered:
    with st.container(border=True):
        _render_query_card(query_item, format_kql_output)
