# AzurePrism — AI Inventory Architect

> **Disclaimer — Proof of Concept · Not for Production Decisions**
>
> AI Inventory Architect is an open-source scaffold project in **POC stage**. All AI-generated reports rely on automated interpretations of Azure Resource Graph data and are subject to inherent limitations. **This tool and its outputs do not constitute professional advice and must not be used as the sole basis for architectural, security, compliance, or financial decisions.** No commercial warranty or liability is implied by the authors or contributors.
>
> The value of this project lies in demonstrating how automated inventory collection, structured normalization, and AI-powered analysis can accelerate cloud governance workflows. Organizations are encouraged to evaluate this scaffold with their internal engineering teams or a trusted Microsoft partner.

![AzurePrism Overview Dashboard](Images/PageOverview.jpeg)

---

## Why This Project Matters

Most organizations treat Azure governance as a cost center — a compliance checkbox that generates spreadsheets nobody reads. **This project exists to close that gap.**

In under 60 seconds, your team can run a single command and receive an AI-generated security posture assessment, architecture review, or BCDR analysis — complete with a Mermaid diagram — derived directly from your live Azure inventory. The deliverable is no longer the pain. **The insight is the product.**

| You already have | This project adds |
|---|---|
| Azure Resource Graph | Automated extraction, flattened CSV, derived analytics columns |
| Azure Policy and tags | IaC detection, service categorization, child-resource flagging |
| Azure OpenAI deployment | Domain-specific prompts that turn raw inventory into governance reports |
| VS Code and CLI skills | A modular Python codebase your team can read, extend, and own |

> *"By 2026, organizations that implement continuous cloud governance automation will reduce cloud-related security incidents by 45% and unplanned spend overruns by 30%."* — Gartner, 2025

---

## Quick Start

```bash
# 1. Clone and set up
git clone <repository-url> && cd <project-directory>
python -m venv .venv && .venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt

# 2. Configure — create a .env file in the project root with the following contents:
```

```ini
AZURE_TENANT_ID=<your-tenant-id>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-5.4-mini
```

Note: For input/output/total token accounting and per-execution totals, see Section 6 comments in `.env` and the generated `data_export/<timestamp>_<profile>/token_usage.json` file.

```bash
# 3. Run
streamlit run app.py          # Dashboard (recommended)
python AI_Inventory_Architect.py          # CLI interactive
python AI_Inventory_Architect.py --profile security   # CLI non-interactive
```

→ Detailed setup: [docs/GETTING_STARTED.md](./docs/GETTING_STARTED.md)

---

## What You Get

| Mode | Command | Output |
|---|---|---|
| **Inventory only** (no OpenAI) | `python AI_Inventory_Architect.py` with only `AZURE_TENANT_ID` set | `inventory.json`, `inventory.csv` |
| **Full analysis** | `streamlit run app.py` or CLI with OpenAI vars set | Environment Brief + deep-dive report + Mermaid diagram per profile |
| **Automation / CI** | `python AI_Inventory_Architect.py --profile security` | Same as full analysis, no prompts |

### Streamlit Dashboard Pages

| Page | Content |
|---|---|
| **Overview** | KPI cards, resource distribution charts, AI environment brief |
| **Inventory** | Interactive filterable table, CSV download |
| **Report & Diagram** | AI narrative + Mermaid diagram (auto-detected profile) |
| **Insights** | Token usage gauges, run history comparison |

---

## Built-In Analysis Profiles

| # | Profile | Focus |
|---|---|---|
| — | `discovery` | Auto Phase 1 — Environment Brief, runs before profile selection |
| 1 | `architecture` | Architecture review, patterns, risks, best practices |
| 2 | `bcdr` | Business continuity, disaster recovery, HA, RTO/RPO gaps |
| 3 | `security` | Security posture, exposure, identity, network controls |
| 4 | `observability` | Monitoring coverage, diagnostics, alerting, Log Analytics |
| 5 | `governance` | Tagging audit, naming conventions, RBAC, compliance maturity |
| 6 | `networking` | VNet topology, segmentation, private endpoints, DNS |
| 7 | `defender` | Defender for Cloud misconfigurations, CSPM coverage |

All profiles are defined in `agent_use_cases.txt`. A template block at the bottom provides a skeleton for custom profiles.

---

## Validated Scaling

The token optimization pipeline (Phases 1–3) has been validated at multiple environment scales:

| Environment | Resources | Token Reduction | Report Quality |
|---|---|---|---|
| Micro | 0–50 | None needed | Full inventory analyzed |
| Small | 50–100 | None needed | Full inventory analyzed |
| Medium | 100–300 | ~20% | All critical resources preserved |
| Large | 300–500 | ~40% | All critical resources preserved |
| Very Large | 500–1,000 | ~40–60% | Critical resources always kept |

→ Sizing guide, cost estimates, and roadmap: [docs/CAPACITY_AND_SCALING.md](./docs/CAPACITY_AND_SCALING.md)

---

## Documentation

| Guide | Contents |
|---|---|
| [docs/GETTING_STARTED.md](./docs/GETTING_STARTED.md) | Prerequisites, installation, `.env` configuration, first run, IDE setup |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Pipeline, project structure, data schemas, profiles, KQL library, token management |
| [docs/TESTING.md](./docs/TESTING.md) | Test suite (52 tests), validation results, CI/CD integration |
| [docs/CAPACITY_AND_SCALING.md](./docs/CAPACITY_AND_SCALING.md) | Environment tiers, API cost estimates, infrastructure context, ROI, roadmap |
| [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | Auth errors, setup issues, execution errors, FAQ |
| [modules/kql/KQL_Tech_Spec.md](./modules/kql/KQL_Tech_Spec.md) | KQL framework deep-dive, profile routing, per-query intent |

---

## Baseline Versions

| Component | Version |
|---|---|
| Python | 3.11.0 |
| Azure CLI | 2.81.0 |
| Resource Graph extension | 2.1.0 |
| openai SDK | 2.32.0 |
| streamlit | 1.56.0 |
| pandas | 3.0.2 |

> Newer versions are generally compatible. If issues arise, align with the versions above.
