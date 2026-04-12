"""
Azure infrastructure inventory via Resource Graph.
Python version of AI_Inventory.ps1 — inventory + AI documentation.
Raphael Andrade - TFTEC Cloud
"""

from datetime import datetime
from pathlib import Path

from modules import az_cli, config, export_csv, inventory
from modules import ai_client, export_markdown, prompt_loader
from modules.token_tracker import TokenTracker


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    cfg = config.load(project_dir)

    az_cli.check_cli_installed()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = project_dir / "data_export" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory_file = output_dir / "inventory.json"
    csv_file = output_dir / "inventory.csv"

    execution_start = datetime.now()
    print(f"Saving output files to: {output_dir}")
    print(f"Execution started at: {execution_start:%Y-%m-%d %H:%M:%S}")

    az_cli.login(cfg["tenant_id"])

    resources = inventory.fetch(inventory_file)
    print(f"Inventory saved to: {inventory_file}")
    inventory.print_stats(resources)

    export_csv.export(resources, csv_file)

    # AI features — only run when Azure OpenAI credentials are configured.
    if "openai_endpoint" in cfg:
        use_cases_file = project_dir / "agent_use_cases.txt"
        available = prompt_loader.list_profiles(use_cases_file)
        default_profile = cfg["prompt_profile"]

        # Interactive profile selection menu.
        print("\n--- AI Documentation Profile ---")
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
            profile = default_profile
        elif choice.isdigit() and 1 <= int(choice) <= len(available):
            profile = available[int(choice) - 1]
        else:
            print(f"Invalid selection '{choice}' — using default '{default_profile}'.")
            profile = default_profile

        prompts = prompt_loader.load(use_cases_file, profile)
        print(f"Using prompt profile: {profile}")

        inventory_json = inventory_file.read_text(encoding="utf-8")
        tracker = TokenTracker()

        # Generate documentation.
        print("Generating technical documentation with AI...")
        doc_result = ai_client.complete(
            endpoint=cfg["openai_endpoint"],
            api_key=cfg["openai_api_key"],
            deployment=cfg["openai_deployment"],
            system_prompt=prompts["doc_system"],
            user_prompt=prompt_loader.render(prompts["doc_user"], inventory_json),
            max_tokens=cfg["doc_max_tokens"],
            temperature=0.3,
        )
        tracker.report("Documentation", doc_result["usage"], cfg["doc_max_tokens"])

        # Generate Mermaid diagram.
        print("Generating Mermaid diagram...")
        mermaid_result = ai_client.complete(
            endpoint=cfg["openai_endpoint"],
            api_key=cfg["openai_api_key"],
            deployment=cfg["openai_deployment"],
            system_prompt=prompts["mermaid_system"],
            user_prompt=prompt_loader.render(prompts["mermaid_user"], inventory_json),
            max_tokens=cfg["mermaid_max_tokens"],
            temperature=0.1,
        )
        tracker.report("Mermaid", mermaid_result["usage"], cfg["mermaid_max_tokens"])

        # Save Markdown report and token usage.
        md_file = output_dir / f"{profile}.md"
        export_markdown.save(doc_result["content"], mermaid_result["content"], md_file)
        tracker.save(output_dir)
    else:
        print("Azure OpenAI not configured — skipping AI documentation.")

    elapsed = (datetime.now() - execution_start).total_seconds()
    print(f"Execution ended at: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Total execution time (seconds): {elapsed:.2f}")


if __name__ == "__main__":
    main()
