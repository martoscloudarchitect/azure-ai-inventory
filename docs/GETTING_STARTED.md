# Getting Started — AzurePrism AI Inventory Architect

> **Disclaimer — Proof of Concept · Not for Production Decisions**
>
> AI Inventory Architect is an open-source scaffold project in **proof-of-concept (POC) stage**. All AI-generated reports rely on automated interpretations of Azure Resource Graph data and are subject to inherent limitations. This tool and its outputs do not constitute professional advice and must not be used as the sole basis for architectural, security, compliance, or financial decisions.

← [Back to README](../README.md)

---

## Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Azure Authentication](#azure-authentication)
4. [Configuration (.env)](#configuration)
5. [Your First Run](#your-first-run)
6. [IDE Setup (Optional)](#ide-setup-optional)

---

## Prerequisites

### Azure Permissions

The script runs under the identity signed in via `az login`. Required permissions:

| Scope | Minimum Role | Used For |
|---|---|---|
| Subscriptions to inventory | **Reader** | Resource Graph queries |
| Azure OpenAI resource | **Cognitive Services OpenAI User** (or API key) | AI report generation |

If your identity lacks Reader on a subscription, those resources are silently excluded. Supplementary queries against tables like `SecurityResources` or `PolicyResources` may require additional roles (e.g. Security Reader); failed queries are skipped with a warning.

### Azure CLI

Install for your OS:

| OS | Command |
|---|---|
| Windows (winget) | `winget install -e --id Microsoft.AzureCLI` |
| macOS | `brew install azure-cli` |
| Linux (Ubuntu/Debian) | `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` |

After install, add the Resource Graph extension:

```bash
az extension add --name resource-graph

# Verify
az --version
az extension list --query "[?name=='resource-graph']" --output table
```

### Python

**Python 3.11** is required. Download from [python.org](https://www.python.org/downloads/) or via package manager.

```bash
python --version   # should return 3.11.x
```

### Azure OpenAI Resource

You need an Azure OpenAI deployment with a model that supports large context windows (e.g. `gpt-5.4-mini`). Find your endpoint and key at:

> **Azure Portal** → your OpenAI resource → **Keys and Endpoint**

---

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd enhancement_test_2

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
#    Windows PowerShell:
.venv\Scripts\Activate.ps1
#    Windows cmd:
.venv\Scripts\activate.bat
#    macOS / Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## Azure Authentication

### Resource Graph authentication

Always uses your `az login` session:

```bash
az login --tenant <your-tenant-id>
```

### Azure OpenAI — Option 1: API Key *(simpler)*

| | |
|---|---|
| **How it works** | Static key sent with every request. No extra RBAC required. |
| **Endpoint format** | Regional OR custom-subdomain — both work. |

```ini
# .env
AZURE_OPENAI_ENDPOINT=https://swedencentral.api.cognitive.microsoft.com/
AZURE_OPENAI_API_KEY=your-api-key-here
```

### Azure OpenAI — Option 2: Keyless / Entra ID *(recommended)*

| | |
|---|---|
| **How it works** | Uses `DefaultAzureCredential` (your `az login` session). No key stored on disk. |
| **Endpoint format** | **Must** be a custom-subdomain endpoint. Regional endpoints do **not** support token auth. |

```ini
# .env
AZURE_OPENAI_ENDPOINT=https://my-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=
```

**RBAC required**: Assign **Cognitive Services OpenAI User** to your identity on the OpenAI resource.

> Portal → resource → **Access control (IAM)** → Add role assignment

The tool auto-selects the auth mode at startup:
- `AZURE_OPENAI_API_KEY` non-empty → **API Key**
- `AZURE_OPENAI_API_KEY` empty/missing → **Keyless (Entra ID)**

---

## Configuration

Create a `.env` file in the project root. **Do not commit this file** — it contains your tenant ID and optionally your API key.

### Minimum (.env for inventory collection only)

```ini
AZURE_TENANT_ID=<your-azure-tenant-id>
```

This produces `inventory.json` and `inventory.csv` with no AI calls.

### Full Mode — API Key

```ini
AZURE_TENANT_ID=<your-azure-tenant-id>

AZURE_OPENAI_ENDPOINT=https://swedencentral.api.cognitive.microsoft.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-5.4-mini
```

### Full Mode — Keyless

```ini
AZURE_TENANT_ID=<your-azure-tenant-id>

AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-5.4-mini
```

### Optional Settings (defaults shown)

```ini
# AI token limits per generation stage
AZURE_OPENAI_BRIEF_MAX_COMPLETION_TOKENS=2000
AZURE_OPENAI_DOC_MAX_COMPLETION_TOKENS=25000
AZURE_OPENAI_MERMAID_MAX_COMPLETION_TOKENS=8000

# Input token hard ceiling — last-resort pre-call rejection guard.
# If the sampled inventory prompt exceeds this limit, the API call is rejected with a
# descriptive error rather than failing at the Azure boundary.
#
# IMPORTANT — what this does NOT do:
#   Changing this value alone does NOT make sampling more or less aggressive.
#   Sampling decisions are driven by fixed resource-count thresholds (100 / 300 / 500
#   resources → 80% / 60% / 40% keep-rate) defined in modules/constants.py.
#
# When to change this:
#   • Switching to a smaller context model (e.g. GPT-4o 32K → set ~28000):
#     You must also lower the sampling thresholds in modules/constants.py, or runs
#     on medium/large environments will be rejected.
#   • Switching to a larger context model (e.g. GPT-4o 128K → set ~120000):
#     Raise this ceiling to allow larger inventories through; consider relaxing
#     sampling thresholds to improve report depth at scale.
#   • Default 272000 matches gpt-5.4-mini's validated context window for this project.
AZURE_OPENAI_MAX_INPUT_TOKENS=272000

# Resource Graph page size (Azure max: 1000)
RESOURCE_GRAPH_PAGE_SIZE=500

# Default profile (overridable at runtime menu)
# Valid: architecture, bcdr, security, observability, governance, networking, defender
PROMPT_PROFILE=architecture
```

---

## Your First Run

### Streamlit Dashboard (recommended)

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Use the **sidebar** to start a new assessment, select a run, and navigate pages.

### CLI — Interactive

```bash
python AI_Inventory_Architect.py
```

After Phase 1 shows the Environment Brief, choose a profile from the numbered menu.

### CLI — Non-Interactive (automation / CI)

```bash
python AI_Inventory_Architect.py --profile security
```

Skips the interactive menu. Valid profiles: `architecture`, `bcdr`, `security`, `observability`, `governance`, `networking`, `defender`.

### Expected output structure

Each run creates a timestamped folder:

```
data_export/
  2026-04-23_103018_security/
    discovery_summary.json   # Phase 1 aggregate counts
    discovery.md             # AI environment brief
    inventory.json           # Full resource inventory + profile-specific data
    inventory.csv            # Flat CSV with derived columns
    security.md              # AI-generated report + Mermaid diagram
    token_usage.json         # API token consumption audit
    run_metadata.json        # Sampling stats, timing, profile used
```

---

## IDE Setup (Optional)

### Recommended: Visual Studio Code

#### Required Extensions

| Extension | ID | Purpose |
|---|---|---|
| Python | `ms-python.python` | Python language support, IntelliSense |
| Pylance | `ms-python.vscode-pylance` | Type checking, fast autocompletion |
| Python Debugger | `ms-python.debugpy` | Breakpoint debugging |
| PowerShell | `ms-vscode.powershell` | Terminal and `.ps1` support |

#### Useful Extensions

| Extension | ID | Purpose |
|---|---|---|
| Markdown Preview Mermaid | `bierner.markdown-mermaid` | Render Mermaid diagrams in Markdown preview |
| Rainbow CSV | `mechatroner.rainbow-csv` | Column-highlighted CSV viewing |
| GitLens | `eamodio.gitlens` | Git blame, history, diff |
| Azure Resources | `ms-azuretools.vscode-azureresourcegroups` | Browse Azure resources from VS Code |
| GitHub Copilot Chat | `github.copilot-chat` | AI coding assistant |

#### Quick Install

```bash
code --install-extension ms-python.python \
     --install-extension ms-python.vscode-pylance \
     --install-extension ms-python.debugpy \
     --install-extension ms-vscode.powershell \
     --install-extension bierner.markdown-mermaid \
     --install-extension mechatroner.rainbow-csv \
     --install-extension eamodio.gitlens \
     --install-extension ms-azuretools.vscode-azureresourcegroups
```

---

→ Next: [Architecture & Pipeline](./ARCHITECTURE.md) | [Troubleshooting](./TROUBLESHOOTING.md) | [Capacity & Scaling](./CAPACITY_AND_SCALING.md)
