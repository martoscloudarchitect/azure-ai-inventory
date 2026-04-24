"""
Azure infrastructure inventory via Resource Graph.
Python version of AI_Inventory.ps1 — inventory + AI documentation.
Raphael Andrade - TFTEC Cloud
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from modules import az_cli, config, export_csv, inventory
from modules import ai_client, export_markdown, prompt_loader, inventory_optimizer
from modules.token_tracker import TokenTracker


CONFIDENCE_SCORE_INSTRUCTION = """
Mandatory formatting requirement for this report:

Place a compact confidence box at the very top of the report body (immediately after any disclaimer), using this exact structure:

## Confidence Score
> **Score:** <0.00 to 1.00>
> **Summary:** <one short sentence explaining why this score was assigned>
> **Scope Note:** This is the LLM reliability/confidence score only, not the operational assessment score.

Then add a short section titled **Conditions to Increase Confidence** with 3-6 concise bullets describing concrete actions required to raise confidence beyond proof-of-concept reliability.

Scoring guidance:
- Keep score conservative because this is a POC pipeline.
- Decrease confidence when sampling is applied, RBAC visibility is partial, or coverage is incomplete.
- Increase confidence only when coverage is broad, data quality is strong, and findings are validated by multiple independent signals.
- Use the provided sampling_context to justify the score.
""".strip()


ASSESSMENT_SCORE_INSTRUCTION = """
Mandatory assessment scoring requirement for this report (all Phase 2 profiles):

1) Keep your existing Executive Summary section.
2) Immediately after Executive Summary, add this section and structure exactly:

## Assessment Score (0-100%)
> **Current Assessment Score:** <0-100>%
> **Assessment Scope:** <one short sentence about what this score represents for the current profile/use case>
> **Distinction:** This assessment score measures operational posture/maturity; it is NOT the LLM Confidence Score.

### Prioritized Remediation Value Uplift
| Priority | Remediation | Estimated Uplift (%) | Rationale |
|---|---|---:|---|
| P1 | <action> | +<number> | <short reason> |
| P2 | <action> | +<number> | <short reason> |

3) Include between 3 and 8 remediation rows (P1..Pn).
4) Estimated Uplift (%) must be numeric and reflect each remediation's incremental contribution toward 100%.
5) End the section with:
> **Projected Score After Roadmap:** <0-100>%

Scoring guidance:
- Use conservative, evidence-based scoring from the available inventory and supplementary query data.
- If data coverage is partial or sampled, reflect this in the current assessment score and rationale.
""".strip()


def _run_discovery(cfg: dict, use_cases_file: Path, output_dir: Path,
                   tracker: TokenTracker) -> tuple[dict, list[dict]]:
    """Phase 1 — Run lightweight summary queries and generate an Environment Brief.

    Returns ``(summary, query_stats)`` so the caller can persist the stats.
    """
    summary_file = output_dir / "discovery_summary.json"
    summary, query_stats = inventory.fetch_summary(summary_file, cfg["page_size"])
    summary_json = json.dumps(summary, indent=2)

    prompts = prompt_loader.load_discovery(use_cases_file)
    print("Generating Environment Brief with AI...")
    brief_result = ai_client.complete(
        client=cfg["openai_client"],
        deployment=cfg["openai_deployment"],
        system_prompt=prompts["brief_system"],
        user_prompt=prompt_loader.render_summary(prompts["brief_user"], summary_json),
        max_tokens=cfg["brief_max_tokens"],
        temperature=0.3,
        max_input_tokens=cfg["max_input_tokens"],
    )
    tracker.report("Environment Brief", brief_result["usage"], cfg["brief_max_tokens"])

    brief_file = output_dir / "discovery.md"
    brief_file.write_text(brief_result["content"], encoding="utf-8")
    print(f"  Environment Brief saved to: {brief_file}")

    # Display the brief in the console for immediate visibility.
    print("\n" + "=" * 70)
    print(brief_result["content"])
    print("=" * 70 + "\n")

    return summary, query_stats


def _select_profile(use_cases_file: Path, default_profile: str) -> str:
    """Show the interactive profile menu and return the selected profile ID."""
    available = prompt_loader.list_profiles(use_cases_file)
    # Exclude discovery from the menu — it runs automatically in Phase 1.
    available = [p for p in available if p != "discovery"]

    print("\n=== Phase 2: Detailed Analysis ===")
    print("--- AI Documentation Profile ---")
    print("Available profiles:")
    for i, pid in enumerate(available, 1):
        desc = prompt_loader.PROFILE_DESCRIPTIONS.get(pid, "")
        marker = " (default)" if pid == default_profile else ""
        print(f"  {i}. {pid:<16} {desc}{marker}")
    print()

    choice = input(
        f"Select a profile [1-{len(available)}] or press Enter for '{default_profile}': "
    ).strip()

    if choice == "":
        return default_profile
    if choice.isdigit() and 1 <= int(choice) <= len(available):
        return available[int(choice) - 1]
    print(f"Invalid selection '{choice}' — using default '{default_profile}'.")
    return default_profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Azure inventory + AI documentation.")
    parser.add_argument(
        "--profile",
        help="Skip interactive menu and use this profile directly.",
    )
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent
    cfg = config.load(project_dir)

    az_cli.preflight_checks()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # When --profile is provided we know the profile upfront and can include
    # it in the folder name immediately, avoiding a rename after Phase 1.
    if args.profile:
        output_dir = project_dir / "data_export" / f"{timestamp}_{args.profile}"
    else:
        output_dir = project_dir / "data_export" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory_file = output_dir / "inventory.json"
    csv_file = output_dir / "inventory.csv"

    execution_start = datetime.now()
    print(f"Saving output files to: {output_dir}")
    print(f"Execution started at: {execution_start:%Y-%m-%d %H:%M:%S}")

    az_cli.login(cfg["tenant_id"])
    account_info = az_cli.check_account()

    # Build the config snapshot that will be persisted.
    ai_enabled = "openai_endpoint" in cfg
    auth_mode = cfg.get("openai_auth_mode", "none")
    run_config = {
        "page_size": cfg["page_size"],
        "ai_enabled": ai_enabled,
    }
    if ai_enabled:
        run_config.update({
            "openai_deployment": cfg["openai_deployment"],
            "openai_auth_mode": auth_mode,
            "brief_max_tokens": cfg["brief_max_tokens"],
            "doc_max_tokens": cfg["doc_max_tokens"],
            "mermaid_max_tokens": cfg["mermaid_max_tokens"],
        })

    print("\n--- Configuration ---")
    print(f"  RESOURCE_GRAPH_PAGE_SIZE = {cfg['page_size']}")
    if ai_enabled:
        print(f"  AZURE_OPENAI_DEPLOYMENT  = {cfg['openai_deployment']}")
        print(f"  AZURE_OPENAI_AUTH_MODE   = {auth_mode}")
        print(f"  BRIEF_MAX_TOKENS         = {cfg['brief_max_tokens']}")
        print(f"  DOC_MAX_TOKENS           = {cfg['doc_max_tokens']}")
        print(f"  MERMAID_MAX_TOKENS       = {cfg['mermaid_max_tokens']}")
    else:
        print("  Azure OpenAI             = not configured (inventory-only mode)")

    use_cases_file = project_dir / "agent_use_cases.txt"
    tracker = TokenTracker()
    all_query_stats: list[dict] = []

    # ── Phase 1: Environment Discovery (AI-powered brief) ──────────────
    phase1_start = datetime.now()
    if ai_enabled:
        _summary, discovery_stats = _run_discovery(cfg, use_cases_file, output_dir, tracker)
        all_query_stats.extend(discovery_stats)
        if args.profile:
            profile = args.profile
            print("\n=== Phase 2: Detailed Analysis ===")
            print(f"Using profile from --profile flag: {profile}")
        else:
            profile = _select_profile(use_cases_file, cfg["prompt_profile"])
    else:
        profile = args.profile or cfg["prompt_profile"]
    phase1_elapsed = (datetime.now() - phase1_start).total_seconds()

    # Append the profile to the output folder name for easy identification.
    # Skip when --profile was provided (folder already has the suffix).
    if not args.profile:
        final_dir = output_dir.parent / f"{timestamp}_{profile}"
        shutil.move(str(output_dir), str(final_dir))
        output_dir = final_dir
    inventory_file = output_dir / "inventory.json"
    csv_file = output_dir / "inventory.csv"

    # ── Phase 2: Full inventory collection + deep-dive report ──────────
    phase2_start = datetime.now()
    combined, inventory_stats = inventory.fetch(
        inventory_file, profile=profile, page_size=cfg["page_size"]
    )
    all_query_stats.extend(inventory_stats)
    resources = combined["inventory"]
    print(f"Inventory saved to: {inventory_file}")
    inventory.print_stats(resources)

    export_csv.export(resources, csv_file)

    if ai_enabled:
        prompts = prompt_loader.load(use_cases_file, profile)
        print(f"Using prompt profile: {profile}")

        inventory_json = inventory_file.read_text(encoding="utf-8")
        sampling_info = {
            "phase": "phase2",
            "sampled": False,
            "original_count": len(combined["inventory"]),
            "sampled_count": len(combined["inventory"]),
            "resources_dropped": 0,
            "reduction_percentage": 0.0,
            "target_percentage": 1.0,
            "max_input_tokens": cfg["max_input_tokens"],
        }
        
        # Apply inventory sampling to manage token limits.
        opt = inventory_optimizer
        combined_inventory = combined["inventory"]
        should_sample = opt.should_sample(combined_inventory)
        
        if should_sample:
            target_pct = opt.get_target_sample_percentage(len(combined_inventory))
            sampled = opt.sample_inventory(combined_inventory, profile=profile, target_percentage=target_pct)
            report = opt.get_sampling_report(combined_inventory, sampled)
            sampling_info.update(report)
            sampling_info["target_percentage"] = target_pct
            
            print("\nInventory Sampling Report:")
            print(f"  Original resources: {report['original_count']}")
            print(f"  Sampled resources: {report['sampled_count']}")
            print(f"  Reduction: {report['reduction_percentage']:.1f}%")
            print(f"  Critical resources preserved: {[r['type'] for r in sampled if opt.is_critical_resource(r)][:5]}...\n")
            
            # Re-serialize sampled inventory to JSON
            inventory_json = json.dumps(sampled, indent=2)
        else:
            print(f"Inventory size ({len(combined_inventory)}) below sampling threshold — using full inventory.\n")

        sampling_context_json = json.dumps(sampling_info, indent=2)

        # Generate documentation.
        print("Generating technical documentation with AI...")
        doc_result = ai_client.complete(
            client=cfg["openai_client"],
            deployment=cfg["openai_deployment"],
            system_prompt=(
                f"{prompts['doc_system']}\n\n"
                f"{CONFIDENCE_SCORE_INSTRUCTION}\n\n"
                f"{ASSESSMENT_SCORE_INSTRUCTION}"
            ),
            user_prompt=prompt_loader.render(
                prompts["doc_user"],
                inventory_json,
                sampling_context_json,
            ),
            max_tokens=cfg["doc_max_tokens"],
            temperature=0.3,
            max_input_tokens=cfg["max_input_tokens"],
        )
        tracker.report("Documentation", doc_result["usage"], cfg["doc_max_tokens"])

        # Generate Mermaid diagram.
        print("Generating Mermaid diagram...")
        mermaid_result = ai_client.complete(
            client=cfg["openai_client"],
            deployment=cfg["openai_deployment"],
            system_prompt=prompts["mermaid_system"],
            user_prompt=prompt_loader.render(
                prompts["mermaid_user"],
                inventory_json,
                sampling_context_json,
            ),
            max_tokens=cfg["mermaid_max_tokens"],
            temperature=0.1,
            max_input_tokens=cfg["max_input_tokens"],
        )
        tracker.report("Mermaid", mermaid_result["usage"], cfg["mermaid_max_tokens"])

        # Save Markdown report and token usage.
        md_file = output_dir / f"{profile}.md"
        export_markdown.save(
            doc_result["content"],
            mermaid_result["content"],
            md_file,
            sampling_info=sampling_info,
        )
        tracker.save(output_dir)
    else:
        print("Azure OpenAI not configured — skipping AI documentation.")

    phase2_elapsed = (datetime.now() - phase2_start).total_seconds()
    execution_end = datetime.now()
    total_elapsed = (execution_end - execution_start).total_seconds()

    print(f"Execution ended at: {execution_end:%Y-%m-%d %H:%M:%S}")
    print(f"Total execution time (seconds): {total_elapsed:.2f}")

    # ── Persist run metadata ───────────────────────────────────────────
    total_rows = sum(s["rows"] for s in all_query_stats)
    total_pages = sum(s["pages"] for s in all_query_stats)

    region_counts: dict[str, int] = {}
    for r in resources:
        region = (r.get("location") or "unknown").lower()
        region_counts[region] = region_counts.get(region, 0) + 1

    metadata = {
        "execution": {
            "started_at": execution_start.isoformat(),
            "ended_at": execution_end.isoformat(),
            "total_seconds": round(total_elapsed, 2),
            "phase1_seconds": round(phase1_elapsed, 2),
            "phase2_seconds": round(phase2_elapsed, 2),
        },
        "profile": profile,
        "subscription": account_info,
        "config": run_config,
        "resource_graph": {
            "total_queries": len(all_query_stats),
            "total_rows_fetched": total_rows,
            "total_pages_fetched": total_pages,
            "page_size": cfg["page_size"],
            "queries": all_query_stats,
        },
        "resources": {
            "count": len(resources),
            "by_region": region_counts,
        },
    }

    if ai_enabled:
        metadata["sampling"] = sampling_info

    meta_file = output_dir / "run_metadata.json"
    meta_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Run metadata saved to: {meta_file}")


if __name__ == "__main__":
    main()
