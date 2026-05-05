# Profile-Aware Network Graph Framework — Architectural Analysis

**Question:** Should the new network graph page dynamically adapt based on which profile (security, architecture, bcdr, governance, networking, defender, observability) is being analyzed?

**Answer:** ✅ **YES — ABSOLUTELY. This is critical.**

This transforms the feature from a generic "nice visualization" into a **professional, contextualized framework** that delivers profile-specific insight.

---

## The Current Architecture: Profile-Centric Design

### Your Existing Model

Each of the **7 profiles** is a distinct analytical lens:

| Profile | Focus | Current Output | What Graph Should Emphasize |
|---------|-------|---|---|
| **Architecture** | Service composition, patterns, best practices, IaC | Narrative + Mermaid flowchart | Service dependencies, deployment patterns, regional distribution |
| **Security** | Risk exposure, remediation priorities, RBAC, identity | Narrative + threat vectors | Remediation chains, blast radius, implicit dependencies, at-risk resources |
| **BCDR** | Business continuity, RTO/RPO, HA, failover | Narrative + availability analysis | Redundancy relationships, failover chains, critical path to HA |
| **Governance** | Tagging audit, naming, RBAC, compliance maturity | Narrative + compliance gaps | Tagging hierarchy, RBAC chains, policy-to-resource mappings |
| **Networking** | VNet topology, segmentation, private endpoints, DNS | Narrative + network diagram | VNet → Subnet → NIC → VM hierarchy; NSG rules; private endpoints |
| **Observability** | Monitoring coverage, alerting, diagnostics, Log Analytics | Narrative + coverage map | Monitoring relationships, alerting chains, diagnostic settings |
| **Defender** | Defender for Cloud gaps, CSPM, misconfigurations | Narrative + risk assessment | Security misconfiguration clusters, control gaps, at-risk resources |

### Current Report Page Behavior (2_Report.py)

```python
# Auto-detect which profile was run
reports = list_report_files(run_dir)  # Returns [security.md], [architecture.md], etc.
profile_name = reports[0].stem  # "security", "architecture", etc.
md_content = load_markdown(report_file)  # Loads profile-specific narrative
```

**The report page is already profile-aware.** It adapts the narrative, structure, and insights based on profile.

---

## The Opportunity: Extend Profile-Awareness to Network Graph

### Without Profile Adaptation (Current Assessment Proposal)

```
Network Graph Page (Generic)
├── Load inventory CSV
├── Build generic parent-child hierarchy
├── Apply generic filters (service_category, resource_group, state)
├── Render same layout for all profiles
└── Result: Same visual for security analyst as for network engineer
```

**Problem:** A **security analyst** analyzing `security.md` wants to see remediation chains and risk clusters. A **network engineer** analyzing `networking.md` wants to see VNet segmentation. Same graph ≠ same insight.

### With Profile Adaptation (Recommended)

```
Network Graph Page (Profile-Aware)
├── Detect active profile from run_dir
├── Load profile-specific graph configuration:
│   ├── Relationship types to emphasize
│   ├── Node color scheme (risk, category, compliance state)
│   ├── Edge filtering rules
│   ├── Default filter selections
│   ├── Layout algorithm suggestions
│   └── Interpretation guidance (help text, annotations)
├── Build and render profile-adapted graph
└── Result: Tailored visualization that amplifies profile insights
```

---

## Profile-Specific Graph Configurations (Proposed)

### **1. Architecture Profile**
**Goal:** Show service composition, deployment patterns, multi-region spread

**Graph Adaptation:**
```python
{
    "profile": "architecture",
    "relationship_types": [
        "parent_child",        # Cognitive Services → Projects
        "service_composition", # Container Registry → Repositories
        "regional_distribution" # Nodes positioned by location
    ],
    "node_colors": {
        "dimension": "service_category",  # Color by compute, storage, network, etc.
        "palette": "colorblind_safe_category"
    },
    "node_size": "sku_tier",  # Larger nodes = higher SKU (more resources)
    "edge_labels": ["composition", "deployment"],
    "default_filters": {
        "provisioning_state": ["Succeeded"]  # Hide failed/updating
    },
    "layout": "hierarchical",  # Emphasizes levels
    "help_text": "Resource groups and service composition. Size indicates SKU tier.",
    "highlights": ["service_category", "iac_hint"]  # Color bicep/ARM resources differently
}
```

**What the analyst sees:**
- Bicep/ARM resources highlighted (IaC adoption)
- Services grouped by category (Compute, Storage, Network clusters)
- Size shows deployment scale (S0 vs S1 vs S2)
- Quick assessment: "Is this service-oriented or monolithic?" "Multi-region or single?"

---

### **2. Security Profile**
**Goal:** Identify remediation chains, at-risk resources, blast radius

**Graph Adaptation:**
```python
{
    "profile": "security",
    "relationship_types": [
        "parent_child",
        "implicit_dependencies",  # What fails if this resource fails?
        "remediation_chains"       # What remediations unblock others?
    ],
    "node_colors": {
        "dimension": "remediation_priority",  # P1 (red), P2 (orange), P3 (yellow)
        "palette": "risk_based"
    },
    "node_size": "blast_radius_estimate",  # Larger = affects more resources if compromised
    "edge_labels": ["blast_radius", "remediation_blocker"],
    "edge_colors": {
        "depends_on": "red",          # High-risk dependency
        "remediation_blocker": "orange"  # Blocks other fixes
    },
    "default_filters": {
        "has_remediation": [True]  # Only show resources with findings
    },
    "layout": "force_directed",  # Groups at-risk clusters
    "help_text": "P1 (red) = Critical risks. Larger nodes = higher impact if compromised. Red edges = blast radius.",
    "highlights": ["remediation_priority", "has_encryption", "has_rbac"]
}
```

**What the analyst sees:**
- P1 remediations are spatially clustered (force-directed layout)
- Red nodes with large blast radius jump out immediately
- Orange edges show "fix this first, it unblocks others"
- Implicit dependencies revealed (e.g., Keyvault outage cascades to 5 App Services)

---

### **3. Networking Profile**
**Goal:** Show VNet topology, segmentation, private endpoints, NSG relationships

**Graph Adaptation:**
```python
{
    "profile": "networking",
    "relationship_types": [
        "network_hierarchy",    # VNet → Subnet → NIC → VM
        "segmentation_rules",   # NSG connections
        "private_endpoints",    # PEP relationships
        "regional_peering"      # Cross-region connections
    ],
    "node_colors": {
        "dimension": "resource_type",  # Distinct colors for VNet, Subnet, NIC, VM, etc.
        "palette": "network_topology"
    },
    "node_size": "ip_utilization",  # Subnets sized by used IPs
    "edge_labels": ["nsg_rule", "peering", "private_endpoint"],
    "edge_colors": {
        "allows": "green",
        "denies": "red",
        "peering": "blue"
    },
    "default_filters": {
        "resource_type": ["VNet", "Subnet", "NIC", "NetworkSecurityGroup"]
    },
    "layout": "hierarchical",  # Emphasizes layers: VNet → Subnet → VM
    "help_text": "Network topology. Green edges = allowed; red edges = denied. Grouped by VNet.",
    "annotations": "Highlight un-segmented subnets, missing NSGs"
}
```

**What the analyst sees:**
- VNet/Subnet structure immediately clear
- NSG rules visualized as edge colors (green = allow, red = deny)
- Over-permissive segmentation jumps out
- Private endpoint dependencies and peering relationships explicit

---

### **4. BCDR Profile**
**Goal:** Show redundancy, failover chains, critical path to availability

**Graph Adaptation:**
```python
{
    "profile": "bcdr",
    "relationship_types": [
        "redundancy_pairs",     # Primary ↔ Secondary
        "failover_chains",      # Orchestration relationships
        "rto_rpo_dependencies"  # What affects RTO/RPO?
    ],
    "node_colors": {
        "dimension": "availability_state",  # Replicated, single-instance, unreplicated
        "palette": "redundancy"
    },
    "node_size": "rto_minutes",  # Larger = longer RTO if fails
    "edge_labels": ["failover", "replication", "orchestration"],
    "edge_colors": {
        "replication": "green",     # Active
        "failover": "orange",       # Standby
        "depends_on": "red"         # Blocking
    },
    "default_filters": {
        "has_redundancy": [True, False]  # Show both replicated and single-instance (highlight gaps)
    },
    "layout": "force_directed",  # Groups replicated pairs
    "help_text": "Red nodes = single-instance (RTO risk). Green edges = active replication. Orange = failover chains.",
    "annotations": "Highlight resources violating RTO/RPO targets"
}
```

**What the analyst sees:**
- Single points of failure (red nodes) immediately visible
- Failover chains (orange edges) show dependency sequences
- Redundancy gaps by region and service category
- Critical path to full HA restoration explicit

---

### **5. Governance Profile**
**Goal:** Show tagging hierarchy, RBAC chains, compliance state

**Graph Adaptation:**
```python
{
    "profile": "governance",
    "relationship_types": [
        "rbac_hierarchy",       # Role assignments
        "tagging_inheritance",  # Tag propagation
        "compliance_lineage"    # Who owns what?
    ],
    "node_colors": {
        "dimension": "tagging_compliance",  # Compliant, missing-tags, miscategorized
        "palette": "compliance_state"
    },
    "node_size": "untagged_child_count",  # Larger = more tagging debt
    "edge_labels": ["rbac_role", "tag_inheritance", "owner"],
    "edge_colors": {
        "owner": "blue",
        "contributor": "green",
        "reader": "gray"
    },
    "default_filters": {
        "tagging_state": ["compliant", "non_compliant"]  # Highlight gaps
    },
    "layout": "hierarchical",  # Emphasizes ownership hierarchy
    "help_text": "Nodes without tags = no color. RBAC relationships shown as edges labeled with role.",
    "annotations": "Highlight untagged resources and orphaned ownership"
}
```

**What the analyst sees:**
- Untagged resources visually prominent (no color)
- RBAC hierarchy and role assignments explicit
- Tagging debt concentrated in specific resource groups
- Orphaned or over-permissioned resources flagged

---

### **6. Observability Profile**
**Goal:** Show monitoring coverage, alerting chains, diagnostic relationships

**Graph Adaptation:**
```python
{
    "profile": "observability",
    "relationship_types": [
        "monitoring_coverage",  # What's monitored?
        "alerting_chains",      # Alert dependencies
        "diagnostic_flow"       # Logs → Analytics → Dashboards
    ],
    "node_colors": {
        "dimension": "monitoring_coverage",  # Monitored, partial, unmonitored
        "palette": "coverage_state"
    },
    "node_size": "log_volume_gb_per_day",  # Larger = higher volume
    "edge_labels": ["alert_rule", "diagnostic_setting", "log_destination"],
    "edge_colors": {
        "logs": "blue",
        "metrics": "green",
        "traces": "orange"
    },
    "default_filters": {
        "monitoring_state": ["monitored", "unmonitored"]  # Show gaps
    },
    "layout": "force_directed",  # Groups monitoring domains
    "help_text": "Gray nodes = unmonitored. Blue/green/orange edges = logs/metrics/traces. Size = log volume.",
    "annotations": "Highlight high-volume resources without alerts, monitoring blind spots"
}
```

**What the analyst sees:**
- Unmonitored resources (gray) jump out
- High-volume resources easily identifiable (larger nodes)
- Alerting chains and escalation paths explicit
- Diagnostic gaps by resource type

---

### **7. Defender Profile**
**Goal:** Show security misconfigurations, control gaps, at-risk clusters

**Graph Adaptation:**
```python
{
    "profile": "defender",
    "relationship_types": [
        "misconfiguration_clusters",  # Related control gaps
        "cspm_requirements",          # Policy → Resource mappings
        "control_gaps"                # Missing controls
    ],
    "node_colors": {
        "dimension": "defender_severity",  # Critical, High, Medium, Low, Passed
        "palette": "cspm_severity"
    },
    "node_size": "cspm_finding_count",  # Larger = more findings
    "edge_labels": ["related_control", "requirement", "policy"],
    "edge_colors": {
        "critical": "red",
        "high": "orange",
        "medium": "yellow",
        "passed": "green"
    },
    "default_filters": {
        "severity": ["Critical", "High", "Medium"]  # Filter by risk threshold
    },
    "layout": "force_directed",  # Groups control-gap clusters
    "help_text": "Red nodes = Critical Defender findings. Edges show related control gaps. Size = finding count.",
    "annotations": "Highlight critical clusters and policy violations"
}
```

**What the analyst sees:**
- Critical findings (red) spatially clustered
- Related control gaps connected (e.g., "missing encryption" + "missing audit logging")
- CSPM policy requirements mapped to resources
- Remediation sequencing (fix critical clusters first)

---

## Implementation Architecture: Profile-Aware Adapter Pattern

### Directory Structure

```
modules/
├── network_graph.py          # Core graph building (unchanged)
├── graph_profiles/           # NEW: Profile-specific adapters
│   ├── __init__.py
│   ├── base.py               # Abstract ProfileAdapter
│   ├── architecture.py       # ArchitectureGraphAdapter
│   ├── security.py           # SecurityGraphAdapter
│   ├── bcdr.py               # BCDRGraphAdapter
│   ├── governance.py         # GovernanceGraphAdapter
│   ├── networking.py         # NetworkingGraphAdapter
│   ├── observability.py      # ObservabilityGraphAdapter
│   └── defender.py           # DefenderGraphAdapter
│
pages/
└── 4_Network.py              # Profile-aware Streamlit page (updated)
```

### Code Pattern

```python
# modules/graph_profiles/base.py
class ProfileGraphAdapter:
    """Base class for profile-specific graph configurations."""
    
    profile_name: str
    relationship_types: list[str]
    node_color_dimension: str
    node_color_palette: str
    node_size_dimension: str
    edge_labels: list[str]
    default_filters: dict
    layout_algorithm: str
    help_text: str
    
    def adapt_graph(self, graph: nx.DiGraph, inventory_df: pd.DataFrame) -> nx.DiGraph:
        """Apply profile-specific node/edge attributes and filtering."""
        raise NotImplementedError


# modules/graph_profiles/security.py
class SecurityGraphAdapter(ProfileGraphAdapter):
    profile_name = "security"
    relationship_types = ["parent_child", "implicit_dependencies", "remediation_chains"]
    node_color_dimension = "remediation_priority"  # P1, P2, P3
    node_color_palette = "risk_based"
    node_size_dimension = "blast_radius_estimate"
    default_filters = {"has_remediation": [True]}
    layout_algorithm = "force_directed"
    
    def adapt_graph(self, graph: nx.DiGraph, inventory_df: pd.DataFrame) -> nx.DiGraph:
        # Color nodes by P1/P2/P3
        # Size by blast radius
        # Edge colors: red (blast), orange (blocker)
        # Highlight at-risk clusters
        return graph


# pages/4_Network.py
def render_network_page():
    run_dir = st.session_state.get("_run_dir")
    profile = detect_profile(run_dir)  # Same logic as Report page
    
    # Load profile adapter
    adapter = load_profile_adapter(profile)
    
    # Build and render adapted graph
    inventory_df = load_inventory_csv(run_dir)
    graph = build_base_graph(inventory_df)
    adapted_graph = adapter.adapt_graph(graph, inventory_df)
    
    # Render with profile-specific filters and help text
    st.info(adapter.help_text)
    pyvis_html = generate_pyvis(adapted_graph, layout=adapter.layout_algorithm)
    st.components.v1.html(pyvis_html, height=700)
```

---

## Implementation Impact: Minimal Change to Scope

### Effort Adjustment

| Phase | Original | With Profile Awareness | Delta |
|-------|----------|------------------------|-------|
| **MVP (basic hierarchy)** | 3.5 days | +1.5 days (profile adapters) | **5 days total** |
| **Enhanced (all views)** | 10 days | +3 days (profile-specific relationship rules) | **13 days total** |
| **Production hardening** | 3–5 days | (unchanged) | (no change) |

**Why small delta?**
- Core graph building logic (parent-child extraction) is unchanged
- Profile adapters are configuration-driven, not custom code per profile
- 7 profiles × ~50 lines of config each = ~350 lines of config code (reusable pattern)

---

## Value Multiplier: Why Profile-Awareness Changes Everything

### Without Profile Adaptation

Generic hierarchy view:
- ✅ Shows parent-child relationships
- ✅ Improves topology understanding
- ⚠️ Delivers same insight to all 7 user personas
- ❌ Misses profile-specific patterns (security clusters, network hierarchy, BCDR chains)

**ROI:** Moderate — nice to have, but not transformative.

### With Profile Adaptation

Each profile gets tailored visualization:
- **Security analyst:** Sees remediation chains + blast radius clusters → P1 prioritization clarity
- **Network engineer:** Sees VNet hierarchy + NSG rules → segmentation assessment
- **BCDR planner:** Sees redundancy pairs + failover chains → HA strategy validation
- **Governance officer:** Sees tagging gaps + RBAC hierarchy → compliance tracking
- **Architect:** Sees service composition + IaC adoption → architecture patterns
- **Ops engineer:** Sees monitoring gaps + alerting chains → observability strategy
- **Defender manager:** Sees control-gap clusters + severity zones → remediation sequencing

**ROI:** High — Transforms from a generic visualization into a **professional, context-aware tool** that amplifies insights for each persona.

---

## Recommendations: Revised Proposal

### ✅ **DO (Revised Plan)**

**Phase 1 MVP (5 days, not 3.5):**
1. Core graph builder (parent-child extraction) — unchanged
2. **Base profile adapter pattern** (abstract class + 1–2 example implementations)
3. Streamlit page with profile detection
4. Implement 2–3 high-value adapters (e.g., **Architecture**, **Security**, **Networking**)
5. Others as templates (copy-paste ready for future)

**Reasoning:**
- You get profile-aware framework from day 1
- Others inherit the pattern
- Minimal effort ($5 vs $3.5 = +1.5 days) for 10x value gain
- Framework is extensible for future profiles (AI-powered hardening, cost optimization, etc.)

### 📋 **Revised Success Criteria**

- [ ] Base `ProfileGraphAdapter` abstract class implemented
- [ ] 3 adapters fully implemented: Architecture, Security, Networking
- [ ] 4 adapters stubbed (boilerplate ready): BCDR, Governance, Observability, Defender
- [ ] Profile detection integrated into Streamlit page (mirrors Report page logic)
- [ ] Tests validate adapter configuration per profile
- [ ] Documentation includes adapter pattern + per-profile visualization guide

---

## Summary: Profile-Aware Changes the Game

| Aspect | Generic Graph | Profile-Aware Framework |
|--------|---|---|
| **Complexity** | Simple hierarchy | Tailored to context |
| **User value** | Moderate (nice to have) | High (context-specific insights) |
| **Implementation cost** | 3.5 days | 5 days |
| **Future extensibility** | Hard (baked-in logic) | Easy (new adapters) |
| **Professional polish** | Good | Excellent |
| **Alignment with AzurePrism values** | Partial (generic analysis) | Full (profile-centric) |

**Bottom line:** The 1.5-day investment in profile adapters transforms this from a "nice visualization" into a **first-class feature** that aligns with AzurePrism's core strength: **profile-driven, AI-powered analysis tailored to user intent.**

---

**Recommended next step:** Should we update the implementation plan to include the profile adapter framework in MVP, or keep it as Phase 2 enhancement?
