# Troubleshooting — AzurePrism AI Inventory Architect

← [Back to README](../README.md)

---

## Contents

1. [Authentication Errors](#authentication-errors)
2. [Setup & Installation Errors](#setup--installation-errors)
3. [Execution Errors](#execution-errors)
4. [Output Issues](#output-issues)
5. [Performance Issues](#performance-issues)
6. [Frequently Asked Questions](#frequently-asked-questions)

---

## Authentication Errors

| Symptom | Cause | Fix |
|---|---|---|
| `401 Unauthorized` from Azure OpenAI | Invalid API key, or identity missing RBAC role | **Key auth**: verify `AZURE_OPENAI_API_KEY` in `.env` matches Portal → resource → Keys and Endpoint. **Keyless auth**: ensure your identity has **Cognitive Services OpenAI User** role on the OpenAI resource (Portal → resource → Access control (IAM)). |
| `BadRequest: Please provide a custom subdomain for token authentication` | Keyless auth used with a regional endpoint | Switch `AZURE_OPENAI_ENDPOINT` to a custom-subdomain URL: `https://<resource-name>.openai.azure.com/`. Regional endpoints (`https://swedencentral.api.cognitive.microsoft.com/`) only support API key auth. |
| `404 Not Found` from Azure OpenAI | Deployment name mismatch | Verify `AZURE_OPENAI_DEPLOYMENT` in `.env` exactly matches the deployment name in Azure AI Studio → Deployments. |
| `az login` opens browser but fails | Cached credentials expired or MFA required | Run `az account clear` then `az login --tenant <your-tenant-id>` again. |
| `No resources found` / empty inventory | Insufficient RBAC or wrong tenant ID | Confirm `AZURE_TENANT_ID` is correct. Verify your identity has at least **Reader** on the target subscriptions. Run `az account list` to see what subscriptions are accessible. |
| `openai.APIConnectionError: Connection error` | DNS cannot resolve endpoint hostname | Verify `AZURE_OPENAI_ENDPOINT` in `.env` is correct. Check Portal → resource → Overview for the exact endpoint. |

---

## Setup & Installation Errors

| Symptom | Cause | Fix |
|---|---|---|
| `ERROR: The term 'az' is not recognized` | Azure CLI not installed or not in PATH | Install Azure CLI and restart your terminal. See [Getting Started — Prerequisites](./GETTING_STARTED.md#prerequisites). |
| `resource-graph extension not found` | Extension missing | `az extension add --name resource-graph` |
| `ModuleNotFoundError: No module named 'openai'` | Dependencies not installed | Activate virtual environment first (`.venv\Scripts\Activate.ps1`), then `pip install -r requirements.txt`. |
| Virtual environment not activating on Windows | Execution policy restriction | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in PowerShell before activating. |
| `python --version` shows Python 2.x | Wrong Python on PATH | Use `python3` instead of `python`, or ensure Python 3.11 is first on PATH. |
| `pip install` fails with SSL errors | Corporate proxy / certificate | Set `REQUESTS_CA_BUNDLE` or use `pip install --trusted-host pypi.org -r requirements.txt`. |

---

## Execution Errors

| Symptom | Cause | Fix |
|---|---|---|
| `429 Too Many Requests` | Rate limit (TPM) exceeded | Wait 1–2 minutes and retry. For persistent issues, increase TPM quota in Azure AI Studio → Deployments → your deployment → Edit. |
| Supplementary query skipped with warning | Missing RBAC for that Resource Graph table | Grant the required role (e.g. **Security Reader** for `SecurityResources`, **Policy Reader** for `PolicyResources`) or safely ignore — the run continues without that data. |
| `ValueError: Estimated input tokens ... exceed limit` | Estimated prompt size is above configured guardrail (example: `343072 > 272000`) | Confirm `AZURE_OPENAI_MAX_INPUT_TOKENS` in `.env` matches your model context window. If still failing: narrow scope (subscription/RG), reduce payload size, or tune sampling thresholds in `modules/constants.py` for smaller-context models. |
| Script hangs at `Signing in to Azure tenant...` | Interactive browser login required | Complete the login in the browser window that opened. If no browser opens, try `az login --use-device-code`. |
| `KeyError: 'inventory'` in inventory processing | Unexpected response format from Resource Graph | Check `az` version: `az --version`. Update if outdated: `az upgrade`. |

---

## Output Issues

| Symptom | Cause | Fix |
|---|---|---|
| Report appears truncated | `DOC_MAX_COMPLETION_TOKENS` too low or reduced from default | Check `AZURE_OPENAI_DOC_MAX_COMPLETION_TOKENS` in `.env`. The default is `25000`. If you reduced it, restore it or try a higher value. |
| Mermaid diagram does not render in VS Code | Malformed Mermaid syntax from LLM | Install the **Markdown Preview Mermaid** extension (`bierner.markdown-mermaid`). If diagram is still broken, re-run — LLM output is non-deterministic. |
| Mermaid diagram renders in VS Code but not in Streamlit | Mermaid.js CDN blocked | Ensure `mermaid.min.js` CDN (`cdn.jsdelivr.net`) is accessible from your network. |
| `data_export/` folder is empty | Run failed before writing output | Check console output for errors. Common causes: RBAC, endpoint misconfiguration, network issues. |
| `inventory.csv` has no data | Inventory collection failed or no resources found | Verify Azure CLI login, tenant ID, and subscription access. Run `az graph query -q "Resources | limit 5"` manually to confirm connectivity. |
| `run_metadata.json` missing | Older run (pre-Phase 3 optimization) | Not a bug — older runs did not generate this file. Streamlit handles missing files gracefully. |

---

## Performance Issues

| Symptom | Cause | Fix |
|---|---|---|
| Inventory collection is slow (>2 min) | Large tenant with many pages of resources | Normal behaviour — pagination fetches all pages sequentially. Reduce `RESOURCE_GRAPH_PAGE_SIZE` to `100–200` to reduce per-page processing time, at the cost of more API calls. |
| Report generation is slow (>60 sec) | Large completion token budget + long model response | Reduce `AZURE_OPENAI_DOC_MAX_COMPLETION_TOKENS`. Reports with 3,000–5,000 tokens are generally sufficient for most environments. |
| Streamlit dashboard is slow to load | Large `inventory.json` in browser | Normal for >500 resources. The dashboard loads all data into memory. Filtering is handled client-side. |
| Multiple 429 errors in a session | Shared Azure OpenAI deployment with low TPM quota | Request TPM quota increase in Azure AI Studio, or stagger runs with 30–60 second delays between profiles. |

---

## Frequently Asked Questions

**Can I use a different AI model (e.g. GPT-4o, GPT-4 Turbo)?**

Yes. Set `AZURE_OPENAI_DEPLOYMENT` in `.env` to any model deployment in your Azure OpenAI resource. Larger models produce higher-quality reports but cost more per token. The token budget logic (`MAX_INPUT_TOKENS=272000`) should be adjusted if your model has a different context window.

**Can I customize the report prompts?**

Yes. All prompts are in `agent_use_cases.txt`. Edit the `DOC_SYSTEM` and `DOC_USER` sections for any profile. See [Architecture — Prompt Profiles](./ARCHITECTURE.md#prompt-profiles) for the structure.

**Can I add a new profile (e.g. FinOps, BCDR2)?**

Yes. See [Architecture — Adding a Custom Profile](./ARCHITECTURE.md#adding-a-custom-profile). You need to add entries in `agent_use_cases.txt`, create a KQL module in `modules/kql/`, and register it in `modules/kql/__init__.py`.

**Can I schedule runs automatically?**

The CLI supports non-interactive mode (`--profile security`), which can be scheduled via:
- **Windows Task Scheduler**
- **GitHub Actions** (see [Testing — CI/CD](./TESTING.md#continuous-integration))
- **Azure Logic Apps** (trigger on a timer, run CLI via Azure Container Instance)

**Can I run against multiple subscriptions?**

Yes — the tool queries all subscriptions your identity can access. To scope to specific subscriptions, modify the base KQL query in `modules/kql/base.py` to add a `| where subscriptionId in (...)` filter, or use `az account set` to target a specific subscription before running.

**Is the data sent to Microsoft / OpenAI stored?**

Your Azure inventory JSON is sent to your Azure OpenAI resource (your own deployment, in your own tenant). Standard Azure OpenAI data handling policies apply — by default, prompt data is not used for model training. Review your Azure OpenAI resource's data privacy settings and your organization's policies before processing sensitive workload data.

**Can I use this with Azure Government or sovereign clouds?**

Possibly, with endpoint adjustments. Azure Government endpoints differ from commercial (`*.azure.us` vs `*.azure.com`). The KQL queries and OpenAI calls use standard Azure CLI and SDK — both support sovereign cloud authentication via `az cloud set`.

**The Streamlit dashboard shows no runs. What's wrong?**

The dashboard reads from the `data_export/` folder relative to where `streamlit run app.py` is launched. Ensure you run the command from the project root directory and that at least one run folder exists in `data_export/`.

---

→ [Getting Started](./GETTING_STARTED.md) | [Architecture](./ARCHITECTURE.md) | [Testing](./TESTING.md) | [Capacity & Scaling](./CAPACITY_AND_SCALING.md)
