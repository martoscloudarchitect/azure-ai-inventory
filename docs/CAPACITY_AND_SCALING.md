# Capacity, Scaling & Cost Guide — AzurePrism AI Inventory Architect

← [Back to README](../README.md)

> **Disclaimer — Proof of Concept · Not for Production Decisions**
>
> Cost estimates are illustrative approximations based on Azure OpenAI public pricing (gpt-5.4-mini, April 2026) and typical resource inventory sizes. Actual costs vary by model, deployment region, TPM quota, and negotiated enterprise agreements. Infrastructure cost ranges are indicative only. This guide is intended to inform planning and prioritization — not to replace formal cost modeling.

---

## For the Decision Maker

**The bottom line in three sentences:**

AzurePrism turns a multi-day manual Azure governance exercise into a **60-second, repeatable, AI-generated report**. At current Azure OpenAI pricing, a complete 7-profile analysis of a 200-resource Azure environment costs approximately **$0.14 in API calls** — less than the cost of one minute of a cloud architect's time. The tool's value is not in the API cost. It is in the hours it eliminates, the consistency it enforces, and the governance posture it makes continuously visible.

---

## Contents

1. [Environment Tiers & Capabilities](#environment-tiers--capabilities)
2. [API Call Cost Estimates](#api-call-cost-estimates)
3. [Infrastructure Cost Context](#infrastructure-cost-context)
4. [Total Cost of Ownership (Scenarios)](#total-cost-of-ownership-scenarios)
5. [Known Limitations](#known-limitations)
6. [Future Enhancements Roadmap](#future-enhancements-roadmap)
7. [Recommendation Matrix](#recommendation-matrix)
8. [Glossary](#glossary)

---

## Environment Tiers & Capabilities

This tool has been validated at the following environment scales using the token optimization pipeline (Phases 1–3). Estimates assume gpt-5.4-mini with average prompt + completion token usage per profile.

| Tier | Resource Count | Subscriptions | Regions | Sampling Applied | Supported? |
|---|---|---|---|---|---|
| **Micro** | 0–50 | 1 | 1–2 | None | ✅ Full support |
| **Small** | 50–100 | 1–3 | 1–3 | None | ✅ Full support |
| **Medium** | 100–300 | 3–10 | 2–5 | 20% reduction | ✅ Full support |
| **Large** | 300–500 | 10–20 | 3–8 | 40% reduction | ✅ Full support |
| **Very Large** | 500–1,000 | 20–50 | 5–10 | 40–60% reduction | ✅ Supported with sampling |
| **Hyper-Scale** | 1,000–5,000 | 50–200 | Global | Requires chunking | ⚠️ Partial — see [roadmap](#future-enhancements-roadmap) |
| **Enterprise-Wide** | 5,000+ | 200+ | Global | Not yet supported | ❌ Out of scope (current version) |

### What "Sampling Applied" Means

For inventories above 100 resources, the system applies **intelligent sampling** — keeping 100% of critical infrastructure (VMs, databases, Key Vaults, networking) and a priority-ranked subset of remaining resources. The AI report reflects the sampled set but is representative of the environment's structure. See [Architecture — Token Management](./ARCHITECTURE.md#token-management--optimization) for details.

---

## API Call Cost Estimates

### Pricing Basis

Estimates use **Azure OpenAI gpt-5.4-mini** public pricing (April 2026):
- Input tokens: **$0.150 / 1M tokens** ($0.00000015 per token)
- Output tokens: **$0.600 / 1M tokens** ($0.00000060 per token)

> Check current pricing at [azure.microsoft.com/pricing/details/cognitive-services/openai-service](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/)

### Cost Per Execution Phase

| Stage | Input Tokens | Output Tokens | Cost per Run |
|---|---|---|---|
| Phase 1 — Environment Brief | ~820 | ~650 | **~$0.001** |
| Phase 2 — Narrative Report (per profile) | ~1,850 | ~3,200 | **~$0.002** |
| Phase 2 — Mermaid Diagram (per profile) | ~1,850 | ~1,100 | **~$0.001** |
| **Single Profile Run (total)** | ~4,520 | ~4,950 | **~$0.004** |
| **All 7 Profiles (full analysis)** | ~26,540 | ~31,450 | **~$0.023** |

### Cost by Environment Size (Single Profile)

| Tier | Resources | Approx. Input Tokens | Approx. Output Tokens | Estimated API Cost |
|---|---|---|---|---|
| Micro | 0–50 | ~4,500 | ~4,950 | **~$0.004** |
| Small | 50–100 | ~7,000 | ~5,500 | **~$0.005** |
| Medium | 100–300 | ~13,500 | ~6,000 | **~$0.006** |
| Large | 300–500 | ~25,000 | ~8,000 | **~$0.009** |
| Very Large | 500–1,000 | ~42,000 | ~12,000 | **~$0.013** |
| Hyper-Scale | 1,000–5,000 | ~80,000+ | ~20,000+ | **~$0.024+** |

### Cost for Full 7-Profile Analysis

| Tier | Resources | API Cost (All 7 Profiles) | Cost per Profile |
|---|---|---|---|
| Micro | 0–50 | **~$0.03** | ~$0.004 |
| Small | 50–100 | **~$0.04** | ~$0.006 |
| Medium | 100–300 | **~$0.05** | ~$0.007 |
| Large | 300–500 | **~$0.07** | ~$0.010 |
| Very Large | 500–1,000 | **~$0.10** | ~$0.014 |

> **Practical takeaway**: Even monthly full analysis of a Large environment costs **less than $1/year in API calls**. The cost driver is not the tool — it is the analyst time it replaces.

---

## Infrastructure Cost Context

The following costs are illustrative of what you are **analyzing**, not what you are spending to run the tool. They provide context for the ROI conversation.

### Typical Azure Infrastructure Cost Ranges

| Environment | Resources | Monthly Azure Spend | Annual Azure Spend |
|---|---|---|---|
| Micro (startup/lab) | 0–50 | $500–$5,000 | $6K–$60K |
| Small (SMB) | 50–100 | $5,000–$25,000 | $60K–$300K |
| Medium (growing company) | 100–300 | $25,000–$150,000 | $300K–$1.8M |
| Large (enterprise division) | 300–500 | $150,000–$500,000 | $1.8M–$6M |
| Very Large (global enterprise) | 500–1,000 | $500,000–$2,000,000 | $6M–$24M |

### Cost Avoidance ROI

Even conservative governance improvement estimates justify the tool many times over:

| Environment | Annual Azure Spend | Governance Waste % (industry avg.) | Avoidable Waste | Tool Cost/Year | ROI Multiple |
|---|---|---|---|---|---|
| Medium | $500K | 15–20% | $75K–$100K | < $1 | **>75,000×** |
| Large | $3M | 15–20% | $450K–$600K | < $5 | **>100,000×** |
| Very Large | $15M | 15–20% | $2.25M–$3M | < $20 | **>150,000×** |

> Source: Gartner estimates organizations waste 20–35% of cloud spend due to governance gaps. The figures above use a conservative 15–20% range.

---

## Total Cost of Ownership (Scenarios)

### Scenario A: Quarterly Governance Review (Medium — 200 resources)

| Item | Cost |
|---|---|
| 4 full analyses/year × $0.05 | **$0.20/year API costs** |
| Azure OpenAI resource (shared) | **~$0/month** (existing deployment) |
| Analyst time to review reports | 2 hrs × 4 = **8 hrs/year** |
| Analyst time saved vs. manual | 40 hrs/year saved |
| **Net annual benefit** | **32 hrs saved + ~$0.20 total tool cost** |

### Scenario B: Monthly Security Reviews (Large — 500 resources)

| Item | Cost |
|---|---|
| 12 security profile runs/year × $0.009 | **$0.11/year API costs** |
| 12 governance profile runs/year × $0.009 | **$0.11/year API costs** |
| 4 full analyses/year × $0.07 | **$0.28/year API costs** |
| **Total tool cost** | **< $0.50/year** |
| Analyst time saved vs. manual | 120+ hrs/year |

### Scenario C: Weekly Monitoring (Very Large — 800 resources, enterprise)

| Item | Cost |
|---|---|
| 52 focused profile runs/year × $0.013 | **$0.68/year API costs** |
| 12 full analyses/year × $0.10 | **$1.20/year API costs** |
| **Total tool cost** | **< $2.00/year** |
| Compliance incidents avoided | $50K–$500K/incident × risk reduction |
| Analyst time saved vs. manual | 500+ hrs/year |

---

## Known Limitations

### Current Ceiling: ~800 Resources per Profile Run

The tool reliably handles up to **~800 resources** within the 272K token budget with 40% sampling applied. Beyond this threshold, sampling keeps all critical resources but may drop a significant portion of secondary resources, potentially reducing report depth.

### Token Budget (272K Hard Ceiling)

Azure OpenAI enforces a maximum input token limit per call. The current version handles this through intelligent sampling, but does not support chunked/batched inventory submission for very large environments.

### Workarounds for Large Environments (Today)

| Approach | Description | Limitation |
|---|---|---|
| **Profile targeting** | Run one profile per subscription group rather than all resources | Manual effort |
| **Resource Group filtering** | Modify base KQL query to filter to specific RGs | Requires KQL knowledge |
| **Subscription scoping** | Use `AZURE_SUBSCRIPTION_IDS` (future) to run per-subscription | Not yet implemented |
| **Critical-only mode** | Reduce `RESOURCE_GRAPH_PAGE_SIZE` to limit inventory | Loses non-critical context |

### Other Known Limitations

| Limitation | Impact | Severity |
|---|---|---|
| No retry logic on 429 responses | Rate limit hits require manual re-run | Medium |
| Single-tenant scope per run | Multi-tenant requires multiple executions | Medium |
| RBAC partial visibility | Resources without Reader access are silently excluded | Medium |
| Non-deterministic LLM output | Report content varies slightly between runs | Low |
| No subscription filtering via `.env` | All accessible subscriptions are always queried | Low |
| Mermaid diagram quality depends on model | Complex diagrams may have minor syntax errors | Low |

---

## Future Enhancements Roadmap

The following enhancements are proposed for consideration based on organizational maturity and scale needs. These are not committed development items — they represent the natural evolution path for production adoption.

### Near-Term (1–4 weeks effort)

| Enhancement | Effort | Value | Target Tier |
|---|---|---|---|
| **Subscription filtering** (`AZURE_SUBSCRIPTION_IDS` in `.env`) | 1 week | High | All |
| **Retry logic with exponential back-off** (handles 429, transient failures) | 3 days | High | All |
| **Structured logging** (replace `print()` with Python `logging`) | 3 days | Medium | Large+ |
| **Cost calculator** (estimate $ for detected resources by SKU) | 1 week | High | Medium+ |

### Medium-Term (1–2 months effort)

| Enhancement | Effort | Value | Target Tier |
|---|---|---|---|
| **Inventory chunking** (batch large inventories into multiple AI calls) | 2 weeks | **Critical** | Hyper-Scale |
| **Streaming API support** (reduce perceived latency for large reports) | 1 week | Medium | Large+ |
| **Change tracking / drift detection** (compare runs over time) | 2 weeks | High | All |
| **Multi-subscription Hub Report** (aggregate brief across tenants) | 2 weeks | High | Enterprise |

### Long-Term (Quarterly+ initiatives)

| Enhancement | Effort | Value | Target Tier |
|---|---|---|---|
| **Power BI / Fabric connector** (pipe CSV output for dashboards) | 1 month | High | Enterprise |
| **Azure DevOps / GitHub Actions integration** (scheduled runs, PR checks) | 2 weeks | Medium | Large+ |
| **Custom sampling threshold controls** (per-organization priority tuning) | 1 week | Medium | Large+ |
| **AI-assisted remediation suggestions** (not just findings, but action plans) | 2 months | Very High | All |
| **Defender for Cloud deep integration** (pull CSPM scores, alert history) | 3 weeks | High | Enterprise |

### Hyper-Scale Strategy (1,000+ Resources)

For environments with thousands of resources, the recommended evolution path is:

1. **Phase 4 — Chunked Inventory** (2 weeks): Split inventory into topic-specific batches (compute, networking, security, data) and generate per-batch reports that are then synthesized.
2. **Phase 5 — Subscription Hub** (2 weeks): Run Phase 1 discovery per subscription, aggregate summaries into a tenant-level brief, then drill into subscriptions of interest.
3. **Phase 6 — Continuous Mode** (1 month): Scheduled execution, change detection, and alert-on-drift capability via Azure Logic Apps or GitHub Actions.

---

## Recommendation Matrix

Use this table to identify the right approach for your organization:

| Organization Type | Resources | Recommended Approach | Run Frequency | Est. Annual API Cost | Primary ROI |
|---|---|---|---|---|---|
| **Startup / Lab** | 0–50 | Streamlit dashboard, all profiles | Quarterly | < $0.50 | Learning + baseline |
| **Growing SMB** | 50–200 | Streamlit + CLI for automation | Monthly | < $1.00 | Governance hygiene |
| **Enterprise Division** | 200–500 | CLI + scheduled runs + security focus | Monthly/bi-weekly | < $2.00 | Compliance + cost avoidance |
| **Large Enterprise** | 500–1,000 | CLI automation + all profiles | Weekly (per profile) | < $5.00 | Risk reduction + audit readiness |
| **Global Enterprise** | 1,000+ | Wait for Phase 4–6 roadmap | TBD | TBD | Transformational governance |

---

## Glossary

| Term | Definition |
|---|---|
| **Token** | Unit of text processed by the LLM. ~4 characters per token (English). 272K token limit = ~1MB of JSON. |
| **Sampling** | Intelligent resource filtering to stay within token budget. Critical resources are always preserved. |
| **Critical Resources** | 11 resource types never dropped during sampling: VMs, SQL DBs, PostgreSQL/MySQL, App Services, Key Vaults, VNets, NSGs, Load Balancers, Traffic Managers, Public IPs, App Insights. |
| **Profile** | Domain-specific analysis lens. Each profile runs specialized KQL queries and uses a tailored LLM prompt. |
| **Phase 1** | Environment Discovery — lightweight aggregate queries to produce an Environment Brief before full inventory. |
| **Phase 2** | Detailed Analysis — full inventory collection + AI report + Mermaid diagram for the selected profile. |
| **TPM** | Tokens Per Minute — Azure OpenAI rate limit. Can be increased via quota request in Azure AI Studio. |
| **CSPM** | Cloud Security Posture Management — Defender for Cloud's continuous assessment of security configuration. |
| **KQL** | Kusto Query Language — Azure Resource Graph's query language, also used by Log Analytics and Defender. |

---

→ [Getting Started](./GETTING_STARTED.md) | [Architecture](./ARCHITECTURE.md) | [Testing](./TESTING.md) | [Troubleshooting](./TROUBLESHOOTING.md)
