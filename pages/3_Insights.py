"""Insights — Execution stats, token usage, resource graph analytics, and run history."""

import pandas as pd
import streamlit as st

from streamlit_app.helpers import (
    detect_profile,
    list_runs,
    load_json,
    render_sidebar,
    run_path,
)

st.set_page_config(page_title="Insights", page_icon="📊", layout="wide")

run_dir = render_sidebar()

st.title("Insights")

tab_exec, tab_tokens, tab_history = st.tabs(
    ["⚙️ Execution & Resource Graph", "🔢 Token Usage", "🕐 Run History"]
)

# ── Execution & Resource Graph tab ────────────────────────────────────────
with tab_exec:
    if not run_dir:
        st.info("Run an assessment from the sidebar to get started.")
    else:
        meta = load_json(run_dir / "run_metadata.json")
        if not meta:
            st.info(
                "No run_metadata.json found for this run. "
                "Re-run the assessment to generate execution statistics."
            )
        else:
            # ── Timing KPIs ───────────────────────────────────────────
            st.subheader("Execution Timing")
            exe = meta["execution"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Duration", f"{exe['total_seconds']:.1f}s")
            c2.metric("Phase 1 (Discovery)", f"{exe['phase1_seconds']:.1f}s")
            c3.metric("Phase 2 (Analysis)", f"{exe['phase2_seconds']:.1f}s")
            c4.metric("Started", exe["started_at"][:19].replace("T", " "))

            # ── Configuration used ────────────────────────────────────
            st.divider()
            st.subheader("Configuration")
            cfg = meta.get("config", {})
            sub = meta.get("subscription") or {}
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("**Azure Context**")
                if sub:
                    st.caption(
                        f"Subscription: **{sub.get('subscription_name', '—')}** "
                        f"(`{sub.get('subscription_id', '—')}`) — {sub.get('state', '—')}"
                    )
                st.caption(f"Profile: **{meta.get('profile', '—')}**")
            with col_r:
                st.markdown("**Parameters**")
                params = {
                    "PAGE_SIZE": cfg.get("page_size", "—"),
                }
                if cfg.get("ai_enabled"):
                    params.update({
                        "Model": cfg.get("openai_deployment", "—"),
                        "Brief max tokens": cfg.get("brief_max_tokens", "—"),
                        "Doc max tokens": cfg.get("doc_max_tokens", "—"),
                        "Mermaid max tokens": cfg.get("mermaid_max_tokens", "—"),
                    })
                for k, v in params.items():
                    st.caption(f"{k}: **{v}**")

            # ── Resource Graph pagination ─────────────────────────────
            st.divider()
            st.subheader("Resource Graph Queries")
            rg = meta.get("resource_graph", {})
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Queries Executed", rg.get("total_queries", 0))
            c2.metric("Total Rows Fetched", f"{rg.get('total_rows_fetched', 0):,}")
            c3.metric("Total Pages", rg.get("total_pages_fetched", 0))
            c4.metric("Page Size", rg.get("page_size", "—"))

            queries = rg.get("queries", [])
            if queries:
                qdf = pd.DataFrame(queries)
                qdf = qdf.rename(columns={
                    "label": "Query",
                    "rows": "Rows",
                    "page_size": "Page Size",
                    "pages": "Pages",
                    "last_page_fill_pct": "Last Page Fill %",
                })
                st.dataframe(qdf, use_container_width=True, hide_index=True)

                # ── Scaling advisory ──────────────────────────────────
                max_rows = max(q["rows"] for q in queries)
                page_size = rg.get("page_size", 500)
                multi_page = [q for q in queries if q["pages"] > 1]

                st.divider()
                st.subheader("Parameter Guidance")

                if multi_page:
                    st.warning(
                        f"**{len(multi_page)} query(ies) required multiple pages.** "
                        f"The largest query returned **{max_rows:,}** rows across "
                        f"multiple pages at PAGE_SIZE={page_size}. "
                        f"Consider increasing `RESOURCE_GRAPH_PAGE_SIZE` toward "
                        f"**1000** (the Azure hard cap) to reduce round-trips."
                    )
                elif max_rows > page_size * 0.5:
                    st.info(
                        f"The largest query returned **{max_rows:,}** rows "
                        f"({max_rows / page_size * 100:.0f}% of PAGE_SIZE={page_size}). "
                        f"For growing environments, consider raising "
                        f"`RESOURCE_GRAPH_PAGE_SIZE` to avoid hitting multi-page "
                        f"thresholds."
                    )
                else:
                    st.success(
                        f"All queries fit within a single page. "
                        f"Current PAGE_SIZE ({page_size}) is adequate."
                    )

                # Token limit advisory
                tokens = load_json(run_dir / "token_usage.json")
                if tokens:
                    high_usage = [
                        t for t in tokens if t["usage_percent"] > 80
                    ]
                    if high_usage:
                        names = ", ".join(t["label"] for t in high_usage)
                        st.warning(
                            f"**Token limit pressure:** {names} exceeded 80% of "
                            f"the configured max tokens. For larger inventories, "
                            f"increase the corresponding `*_MAX_COMPLETION_TOKENS` "
                            f"in `.env` to avoid truncated output."
                        )

            # ── Resource distribution ─────────────────────────────────
            res_meta = meta.get("resources", {})
            by_region = res_meta.get("by_region", {})
            if by_region:
                st.divider()
                st.subheader("Resource Distribution")
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.metric("Total Resources", res_meta.get("count", 0))
                    st.metric("Regions", len(by_region))
                with c2:
                    rdf = pd.DataFrame(
                        list(by_region.items()), columns=["Region", "Count"]
                    ).sort_values("Count", ascending=False)
                    st.bar_chart(rdf, x="Region", y="Count")

# ── Token Usage tab ───────────────────────────────────────────────────────
with tab_tokens:
    if not run_dir:
        st.info("Run an assessment from the sidebar to get started.")
    else:
        records = load_json(run_dir / "token_usage.json")
        if not records:
            st.info("No token_usage.json found for this run.")
        else:
            cols = st.columns(len(records))
            for col, rec in zip(cols, records):
                col.subheader(rec["label"])
                col.metric("Completion tokens", f"{rec['completion_tokens']:,}")
                col.progress(
                    min(rec["usage_percent"] / 100.0, 1.0),
                    text=f"{rec['usage_percent']}% of {rec['max_tokens']:,} limit",
                )
                col.caption(
                    f"Prompt: {rec['prompt_tokens']:,} · "
                    f"Total: {rec['total_tokens']:,} · "
                    f"Remaining: {rec['remaining']:,}"
                )

            st.divider()
            st.subheader("Summary")

            df = pd.DataFrame(records).rename(columns={
                "label": "Stage",
                "prompt_tokens": "Prompt",
                "completion_tokens": "Completion",
                "total_tokens": "Total",
                "max_tokens": "Limit",
                "usage_percent": "Usage %",
                "remaining": "Remaining",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)

            total_prompt = sum(r["prompt_tokens"] for r in records)
            total_completion = sum(r["completion_tokens"] for r in records)
            total_all = sum(r["total_tokens"] for r in records)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Prompt Tokens", f"{total_prompt:,}")
            c2.metric("Total Completion Tokens", f"{total_completion:,}")
            c3.metric("Total Tokens (all stages)", f"{total_all:,}")

# ── Run History tab ───────────────────────────────────────────────────────
with tab_history:
    runs = list_runs()
    if not runs:
        st.info("No assessment runs found.")
    else:
        rows: list[dict] = []
        for rn in runs:
            rd = run_path(rn)
            files = [f.name for f in rd.iterdir() if f.is_file()]
            summary = load_json(rd / "discovery_summary.json")
            totals = (
                summary.get("totals", [{}])[0]
                if isinstance(summary, dict) and summary.get("totals")
                else {}
            )
            profile = detect_profile(rd) or "—"
            rows.append({
                "Run": rn,
                "Profile": profile,
                "Resources": totals.get("resource_count", "—"),
                "Subscriptions": totals.get("subscription_count", "—"),
                "Regions": totals.get("region_count", "—"),
                "Files": len(files),
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Comparison ────────────────────────────────────────────────
        st.divider()
        st.subheader("Compare Runs")

        if len(runs) < 2:
            st.info("Need at least two runs to compare.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                run_a = st.selectbox("Run A", runs, index=0, key="cmp_a")
            with col2:
                run_b = st.selectbox("Run B", runs, index=min(1, len(runs) - 1), key="cmp_b")

            if run_a == run_b:
                st.warning("Select two different runs to compare.")
            else:
                sum_a = load_json(run_path(run_a) / "discovery_summary.json")
                sum_b = load_json(run_path(run_b) / "discovery_summary.json")

                if not sum_a or not sum_b:
                    st.info("Both runs need a discovery_summary.json for comparison.")
                else:
                    totals_a = (
                        sum_a.get("totals", [{}])[0]
                        if isinstance(sum_a, dict) and sum_a.get("totals")
                        else {}
                    )
                    totals_b = (
                        sum_b.get("totals", [{}])[0]
                        if isinstance(sum_b, dict) and sum_b.get("totals")
                        else {}
                    )

                    metrics = [
                        ("resource_count", "Resources"),
                        ("subscription_count", "Subscriptions"),
                        ("resource_group_count", "Resource Groups"),
                        ("region_count", "Regions"),
                    ]

                    cols = st.columns(len(metrics))
                    for col, (key, label) in zip(cols, metrics):
                        val_a = totals_a.get(key, 0)
                        val_b = totals_b.get(key, 0)
                        delta = val_a - val_b
                        col.metric(
                            label,
                            val_a,
                            delta=delta if delta != 0 else None,
                            help=f"Run A: {val_a}, Run B: {val_b}",
                        )
