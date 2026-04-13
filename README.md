# AI Inventory Architect

Azure infrastructure inventory and AI-powered documentation tool. Queries Azure Resource Graph, exports structured JSON and CSV reports, and optionally generates architecture documentation and Mermaid diagrams using Azure OpenAI — all driven by configurable prompt profiles.

---

## Why This Project Matters

### The Governance Gap

Most organizations treat Azure IT Governance as a cost center — a compliance checkbox that generates spreadsheets nobody reads, passed between teams who dread the exercise. The result is predictable: outdated inventories, blind spots in security posture, architecture drift that compounds silently until an incident forces a fire drill.

**This project exists to close that gap.**

AI Inventory Architect is not just a script. It is a working scaffold that demonstrates how infrastructure governance can shift from **reactive burden** to **proactive capability** — where every execution produces a living, queryable, AI-enriched picture of what you actually have running in Azure.

### What Industry Leaders Are Saying

> *"By 2026, organizations that implement continuous cloud governance automation will reduce cloud-related security incidents by 45% and unplanned spend overruns by 30%."*
> — Gartner, Predicts 2025: Cloud Infrastructure and Platform Services

> *"The biggest risk in cloud governance isn't non-compliance — it's the six-month-old spreadsheet everyone trusts but nobody maintains."*
> — Microsoft Well-Architected Framework, Operational Excellence pillar

> *"Cloud governance must evolve from periodic audits to continuous, automated visibility. Organizations that fail to do so will face compounding technical debt and rising security exposure."*
> — Forrester Research, The State of Cloud Governance, 2025

> *"Companies with mature IT asset management practices achieve 30% lower total cost of ownership and 50% faster incident resolution."*
> — ITIL 4: Create, Deliver and Support (Axelos/PeopleCert)

These are not aspirational quotes. They describe the exact trajectory this project puts your team on.

### Normalization and Standardization: The Compound Effect

When every team, subscription, and environment is inventoried through the same KQL query, exported in the same CSV schema, and documented through the same AI prompt profiles, something powerful happens:

- **Consistent taxonomy** — Service categories, IaC detection, and SKU naming follow a single convention. No more "is it `Standard_D2s_v3` or `D2s v3`?" debates across teams.
- **Comparable baselines** — Tuesday's architecture review and Friday's security assessment share the same resource snapshot. Decisions are grounded in the same truth.
- **Repeatable audits** — Auditors, architects, and finance leads receive reports generated from the same pipeline. The format is known, the columns are documented, the method is transparent.
- **Institutional memory** — Every execution is timestamped and versioned in `data_export/`. The organization builds a chronological record of its Azure footprint without anyone manually maintaining it.

Standardization is not bureaucracy. It is the foundation that makes velocity possible. You cannot move fast on a surface you cannot see.

### Building a Stronger Foundation on Current Architecture

This project does not replace your existing Azure governance tools — it **amplifies** them. It sits on top of what you already have:

| You already have | This project adds |
|---|---|
| Azure Resource Graph | Automated extraction, flattened CSV, derived columns for analytics |
| Azure Policy and tags | IaC detection parsed from tags, service categorization, child-resource flagging |
| Azure OpenAI deployment | Targeted prompts that turn raw inventory into architecture narratives, BCDR assessments, security reviews |
| VS Code and CLI skills | A modular Python codebase your team can read, extend, and own |

The six built-in prompt profiles (architecture, BCDR, security, cost, governance, networking) are **starting positions, not finish lines**. They demonstrate a pattern: take a structured dataset, apply a domain-specific prompt, produce a deliverable that used to take days of manual effort. Your team should build on this scaffold — add profiles for Application Insights telemetry, Defender for Cloud findings, or FinOps chargebacks. The pattern is the product.

### From Cost Center to Catalyst

Here is the transformation this project enables:

**Before** — Governance is synonymous with restriction. The governance team is the group that says "no," produces 80-page compliance decks, and is invited to meetings only when something goes wrong. Engineers avoid them. Leadership tolerates them. Nobody is excited.

**After** — The same team runs `python AI_Inventory_Architect.py`, selects the `security` profile, and in under 60 seconds (for my small scale environment as a benchmark) delivers an AI-generated security posture assessment with a Mermaid diagram that a CISO can present in a board meeting. They switch to `cost`, and within a minute they have a cost optimization narrative with actionable recommendations derived from real SKU data. They switch to `architecture`, and an architecture review document materializes — complete with resource relationships and provisioning state analysis.

The deliverable is no longer the pain. **The insight is the product.**

When governance teams can produce high-quality, visually compelling, data-driven deliverables in minutes instead of weeks, something shifts:

- **Engineers want to collaborate** because the output is useful, not punitive.
- **Leadership funds the initiative** because the ROI is visible and immediate.
- **The team itself is energized** because they are building, creating, and shipping — not copy-pasting between portals and spreadsheets.

This is the inflection point where governance stops being a cost line and starts being a competitive advantage. The organization that masters its cloud inventory — and can articulate what it has, why it has it, and what to do about it — moves faster, spends smarter, and sleeps better.

### Master the Concepts, Then Build

This project is deliberately designed as a **learning scaffold**. Every module is small enough to read in five minutes. Every pattern (KQL extraction → structured export → AI enrichment → deliverable) is explicit and traceable. The team should:

1. **Understand the pipeline** — Follow a single execution from `config.load()` to the final `.md` file. Know what each module does and why.
2. **Customize the prompts** — Modify `agent_use_cases.txt` to match your organization's language, compliance frameworks, and reporting standards.
3. **Extend the modules** — Add pagination, subscription filtering, retry logic, structured logging. The "Known Limitations" section below is your roadmap.
4. **Integrate into workflows** — Schedule executions, pipe CSV into Power BI, feed `.md` files into SharePoint or Confluence, trigger alerts on inventory drift.
5. **Own the tool** — This is not a vendor product. It is your code, your prompts, your pipeline. The team that owns its governance tooling owns its governance posture.

The goal is not to run this script forever. The goal is to internalize the pattern — **automated collection, structured normalization, AI-powered analysis, actionable deliverable** — and apply it to every governance challenge that crosses your desk.

---

## Project Scope

| Capability | Description |
|---|---|
| **Inventory collection** | Query Azure Resource Graph for all resources across subscriptions with enriched metadata (tags, SKU, kind, provisioning state). |
| **CSV export** | Flat CSV with derived columns: service category, child resource detection, IaC hints from tags. |
| **AI documentation** | Send inventory to Azure OpenAI to generate a Markdown narrative (architecture review, security assessment, BCDR, cost, governance, or networking). |
| **Mermaid diagrams** | AI-generated flowchart diagrams normalized for VS Code Preview. |
| **Token tracking** | Per-call token usage reporting and JSON audit file. |
| **Prompt profiles** | Six built-in use cases selectable via `.env`, plus a template for custom profiles. |

## Project Structure

```
AI_Inventory_Architect.py           # Main entry point (orchestration only)
agent_use_cases.txt                 # Prompt definitions with multiple use-case profiles
modules/
  __init__.py
  az_cli.py                         # Azure CLI wrapper: run, login, extract JSON
  config.py                         # Load and validate .env configuration
  inventory.py                      # Resource Graph query, save JSON, print stats
  export_csv.py                     # CSV export with derived columns
  prompt_loader.py                  # Parse agent_use_cases.txt for selected profile
  ai_client.py                      # Azure OpenAI HTTP calls (stdlib only)
  export_markdown.py                # Assemble .md with normalized Mermaid diagram
  token_tracker.py                  # Token usage reporting and JSON audit
data_export/
  <YYYY-MM-DD_HHMMSS>/             # One folder per execution
    inventory.json                  # Raw Resource Graph output
    inventory.csv                   # Flat CSV with derived columns
    {profile}.md                    # AI-generated report + Mermaid (named after selected profile)
    token_usage.json                # Token consumption audit (when AI enabled)
requirements.txt                    # Python dependencies
.env                                # Environment variables (not committed)
prompt-requirements.txt             # Legacy prompt file (PS1 script only)
```

## Baseline Environment Versions

| Component | Version |
|---|---|
| Python | 3.11.0 |
| Azure CLI (`azure-cli`) | 2.81.0 |
| Resource Graph extension (`resource-graph`) | 2.1.0 |
| python-dotenv | 1.0.1 |

> Newer versions should be compatible. If you encounter issues, align with the versions above.

## Prerequisites

### Azure CLI

Install the Azure CLI for your OS:

- **Windows (winget)**: `winget install -e --id Microsoft.AzureCLI`
- **Windows (MSI)**: <https://learn.microsoft.com/cli/azure/install-azure-cli-windows>
- **macOS**: `brew install azure-cli`
- **Linux (Ubuntu/Debian)**: `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`

Verify: `az --version`

### Azure Resource Graph extension

```bash
# Check if installed
az extension list --query "[?name=='resource-graph']" --output table

# Install if missing
az extension add --name resource-graph
```

## Python Environment Setup

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
#    Windows PowerShell:  .venv\Scripts\Activate.ps1
#    Windows cmd:         .venv\Scripts\activate.bat
#    Linux / macOS:       source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Recommended IDE

This project is developed and tested with **[Visual Studio Code](https://code.visualstudio.com/)**. The extensions below ensure a smooth experience across Python, Markdown/Mermaid previews, Azure connectivity, and version control.

### Required extensions

| Extension | ID | Purpose |
|---|---|---|
| Python | `ms-python.python` | Python language support, IntelliSense, virtual environment detection |
| Pylance | `ms-python.vscode-pylance` | Type checking and fast autocompletion for Python |
| Python Debugger | `ms-python.debugpy` | Breakpoint debugging for Python scripts |
| PowerShell | `ms-vscode.powershell` | Terminal and language support for `.ps1` files |

### Recommended extensions

| Extension | ID | Purpose |
|---|---|---|
| Markdown All in One | `yzhang.markdown-all-in-one` | Markdown editing, TOC, preview shortcuts |
| Markdown Preview Mermaid | `bierner.markdown-mermaid` | Render Mermaid diagrams in Markdown preview |
| markdownlint | `davidanson.vscode-markdownlint` | Lint Markdown files for consistency |
| Rainbow CSV | `mechatroner.rainbow-csv` | Column-highlighted CSV viewing for `inventory.csv` |
| YAML | `redhat.vscode-yaml` | Schema validation for YAML/config files |
| Prettier | `esbenp.prettier-vscode` | Auto-format JSON, Markdown, YAML |
| GitLens | `eamodio.gitlens` | Git blame, history, and diff annotations |
| GitHub Copilot Chat | `github.copilot-chat` | AI coding assistant |

### Azure extensions

| Extension | ID | Purpose |
|---|---|---|
| Azure Resources | `ms-azuretools.vscode-azureresourcegroups` | Browse Azure resources from VS Code |
| Azure CLI Tools | `ms-vscode.azurecli` | Syntax highlighting and IntelliSense for `az` commands |
| Bicep | `ms-azuretools.vscode-bicep` | Useful if reviewing IaC templates referenced in reports |

### Quick install (all at once)

```bash
code --install-extension ms-python.python \
     --install-extension ms-python.vscode-pylance \
     --install-extension ms-python.debugpy \
     --install-extension ms-vscode.powershell \
     --install-extension yzhang.markdown-all-in-one \
     --install-extension bierner.markdown-mermaid \
     --install-extension davidanson.vscode-markdownlint \
     --install-extension mechatroner.rainbow-csv \
     --install-extension redhat.vscode-yaml \
     --install-extension esbenp.prettier-vscode \
     --install-extension eamodio.gitlens \
     --install-extension ms-azuretools.vscode-azureresourcegroups \
     --install-extension ms-vscode.azurecli \
     --install-extension ms-azuretools.vscode-bicep
```

## Configuration

Create a `.env` file in the project root.

### Inventory only (minimum)

```
AZURE_TENANT_ID=<your-azure-tenant-id>
```

### Full mode with AI documentation

```
AZURE_TENANT_ID=<your-azure-tenant-id>

# --- Azure OpenAI ---
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_DOC_MAX_COMPLETION_TOKENS=4000
AZURE_OPENAI_MERMAID_MAX_COMPLETION_TOKENS=4000

# --- Prompt profile (default when pressing Enter at the menu) ---
# Valid values: architecture, bcdr, security, cost, governance, networking
# To add a custom profile, define it in agent_use_cases.txt and use its id here.
PROMPT_PROFILE=architecture
```

## Execution Modes

| `.env` configuration | Behavior | Output files |
|---|---|---|
| Only `AZURE_TENANT_ID` | Inventory collection and CSV export | `inventory.json`, `inventory.csv` |
| All OpenAI vars set | Full run with AI documentation and diagrams | `inventory.json`, `inventory.csv`, `{profile}.md`, `token_usage.json` |

## Prompt Profiles

The `PROMPT_PROFILE` value in `.env` sets the **default** profile. When AI documentation is enabled, the script shows an interactive menu at runtime where you can pick any available profile or press Enter to accept the default.

### Built-in profiles

| # | Profile ID | Focus |
|---|---|---|
| 1 | `architecture` | General architecture review, patterns, risks, best practices |
| 2 | `bcdr` | Business continuity, disaster recovery, HA, RTO/RPO gaps |
| 3 | `security` | Security posture, exposure, identity, network, monitoring |
| 4 | `cost` | FinOps, right-sizing, idle resources, SKU optimization |
| 5 | `governance` | Tagging audit, naming conventions, RBAC, compliance maturity |
| 6 | `networking` | VNet topology, segmentation, private endpoints, DNS |

All profiles are defined in `agent_use_cases.txt`. A template block at the bottom of that file provides a skeleton for creating custom profiles — just add the four required sections and the menu will pick it up automatically.

### Changing the default profile

Edit `.env`:

```
# Switch default to security assessment
PROMPT_PROFILE=security
```

Or simply select a different number at the interactive menu when the script runs.

### Example: interactive menu

```
--- AI Documentation Profile ---
Available profiles:
  1. architecture     General architecture review (default)
  2. bcdr             Business Continuity & Disaster Recovery
  3. security         Security posture assessment
  4. cost             Cost optimization & right-sizing
  5. governance       Governance, compliance & tagging audit
  6. networking       Network topology & connectivity review

Select a profile [1-6] or press Enter for 'architecture': 3
Using prompt profile: security
```

## Running the Script

```bash
python AI_Inventory_Architect.py
```

### Sample output (full mode)

```
Saving output files to: C:\GitHub\Inventory\data_export\2026-04-12_103018
Execution started at: 2026-04-12 10:30:18
Signing in to Azure tenant xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx...
Collecting Azure inventory through Resource Graph...
Found 142 resources
Inventory saved to: ...\data_export\2026-04-12_103018\inventory.json
Resources per region:
  - eastus: 65
  - westeurope: 42
  - brazilsouth: 35
CSV export saved to: ...\data_export\2026-04-12_103018\inventory.csv

--- AI Documentation Profile ---
Available profiles:
  1. architecture     General architecture review (default)
  2. bcdr             Business Continuity & Disaster Recovery
  3. security         Security posture assessment
  4. cost             Cost optimization & right-sizing
  5. governance       Governance, compliance & tagging audit
  6. networking       Network topology & connectivity review

Select a profile [1-6] or press Enter for 'architecture':
Using prompt profile: architecture
Generating technical documentation with AI...
Documentation tokens -> prompt: 1850, completion: 3200 / limit: 4000 (80.0%), remaining: 800
Generating Mermaid diagram...
Mermaid tokens -> prompt: 1850, completion: 1100 / limit: 4000 (27.5%), remaining: 2900
Documentation saved to: ...\data_export\2026-04-12_103018\architecture.md
Token usage saved to: ...\data_export\2026-04-12_103018\token_usage.json
Execution ended at: 2026-04-12 10:31:02
Total execution time (seconds): 44.12
```

### Output files

**inventory.json** — Raw Resource Graph response:

```json
{
  "data": [
    {
      "name": "myVM",
      "type": "microsoft.compute/virtualmachines",
      "location": "eastus",
      "resourceGroup": "rg-prod",
      "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "tags": { "env": "prod", "managed-by": "terraform" },
      "sku": { "name": "Standard_D2s_v3" },
      "kind": "",
      "provisioningState": "Succeeded"
    }
  ]
}
```

**inventory.csv** — Derived columns:

| Column | Source | Description |
|---|---|---|
| `name` | `name` | Resource name |
| `type` | `type` | Full ARM resource type |
| `service_category` | derived from `type` | Provider namespace (e.g. `microsoft.compute`) |
| `service_short_type` | derived from `type` | Leaf type (e.g. `virtualmachines`) |
| `is_child_resource` | derived from `type` | `True` if type has more than two segments |
| `location` | `location` | Azure region |
| `resource_group` | `resourceGroup` | Resource group name |
| `subscription_id` | `subscriptionId` | Subscription GUID |
| `kind` | `kind` | Resource variant (e.g. `StorageV2`, `app,linux`) |
| `sku_name` | `sku.name` | Pricing tier / SKU |
| `provisioning_state` | `properties.provisioningState` | Deployment state |
| `iac_hint` | derived from `tags` | Detected IaC tool (`terraform`, `bicep`, `pulumi`, `arm`) or `unknown` |
| `tags` | `tags` | Flattened key=value pairs separated by `;` |

**{profile}.md** — AI-generated narrative + Mermaid diagram (e.g., `architecture.md`, `security.md`).

**token_usage.json** — Token consumption per AI call for auditing.

## Hard-Coded Parameters

| Parameter | Value | Module | Description |
|---|---|---|---|
| `PAGE_SIZE` | `"500"` | `inventory.py` | Max resources per Resource Graph page |
| `QUERY` (columns) | `name, type, location, resourceGroup, subscriptionId, tags, sku, kind, provisioningState` | `inventory.py` | Columns projected from the Resources table |
| `QUERY` (sort) | `order by type asc` | `inventory.py` | Result set sort order |
| `CSV_COLUMNS` | 13 columns | `export_csv.py` | Column names and order in CSV |
| `IAC_TAG_KEYWORDS` | `terraform, bicep, pulumi, arm, iac` | `export_csv.py` | Tag keywords for IaC detection |
| `API_VERSION` | `2024-12-01-preview` | `ai_client.py` | Azure OpenAI API version |
| `REQUIRED_SECTIONS` | `DOC_SYSTEM, DOC_USER, MERMAID_SYSTEM, MERMAID_USER` | `prompt_loader.py` | Required sections per profile |
| `.env` file name | `.env` | `config.py` | Environment file location |

## Known Limitations and Improvement Suggestions

### Azure Resource Graph caps

| Limit | Current behaviour | Impact |
|---|---|---|
| **`--first 500`** — single page cap | Fetches only the first 500 resources. | Tenants with more than 500 resources will have an **incomplete inventory**. Resource Graph supports up to 1,000 rows per page. |
| **No pagination (`$skipToken`)** | Does not follow `$skipToken` when more rows exist. | Large environments will silently miss resources beyond the first page. |
| **Request throttling** | Resource Graph enforces per-tenant read throttling (15 requests per 5-second window). | Not an issue for a single run, but repeated executions could be throttled. |
| **Cross-subscription visibility** | Queries all subscriptions the identity can access, but RBAC may hide some. | Inventory may be partial without Reader role on all subscriptions. |

### Azure OpenAI caps

| Limit | Current behaviour | Impact |
|---|---|---|
| **Token limits** | Controlled via `DOC_MAX_COMPLETION_TOKENS` and `MERMAID_MAX_COMPLETION_TOKENS`. | Large inventories may produce truncated documentation if limits are too low. |
| **Rate limiting** | No retry logic on `429` responses. | Rapid sequential calls or shared deployments could hit TPM limits. |
| **Model context window** | The full inventory JSON is sent as the user prompt. | Very large inventories may exceed the model's context window. |

### Code improvements for production readiness

1. **Implement pagination** — Follow `$skipToken` across multiple `az graph query` calls to remove the 500-row ceiling.
2. **Make `--first` configurable** — Move page size to `.env` (e.g. `RESOURCE_GRAPH_PAGE_SIZE=1000`).
3. **Add subscription filtering** — Optional `AZURE_SUBSCRIPTION_IDS` in `.env` for `--subscriptions`.
4. **Add retry logic with back-off** — Handle transient failures and `429` responses from both Resource Graph and Azure OpenAI.
5. **Structured logging** — Replace `print()` with Python `logging` for levels, file output, and monitoring integration.
6. **Validate output files** — Re-read JSON after write to confirm it is well-formed and non-empty.
7. **Inventory chunking for AI** — For very large inventories, split into batches before sending to Azure OpenAI to stay within context window limits.
