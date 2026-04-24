# Testing & Validation — AzurePrism AI Inventory Architect

← [Back to README](../README.md)

---

## Contents

1. [Test Suite Overview](#test-suite-overview)
2. [Running Tests Locally](#running-tests-locally)
3. [Unit Test Coverage](#unit-test-coverage)
4. [End-to-End Validation Results](#end-to-end-validation-results)
5. [Continuous Integration](#continuous-integration)
6. [Known Gaps & Roadmap](#known-gaps--roadmap)

---

## Test Suite Overview

The project ships with **52 tests** across three test files, covering the complete token optimization pipeline implemented in Phases 1–3.

| Test File | Tests | Coverage Area | Status |
|---|---|---|---|
| `tests/test_inventory_optimizer.py` | 35 | Sampling engine, filtering, priorities, estimation | ✅ All passing |
| `tests/test_ai_client.py` | 9 | Token estimation, API safeguards, oversized rejection | ✅ All passing |
| `test_end_to_end.py` | 8 categories | Full pipeline at 50 / 200 / 500 resource scales | ✅ All passing |
| **Total** | **52** | | **100% pass rate** |

---

## Running Tests Locally

### Prerequisites

Activate your virtual environment and ensure dependencies are installed:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_inventory_optimizer.py -v
pytest tests/test_ai_client.py -v

# Run with coverage report
pip install pytest-cov
pytest tests/ --cov=modules --cov-report=term-missing
```

### End-to-End Tests

```bash
# Full end-to-end validation (no Azure credentials needed — uses synthetic data)
python test_end_to_end.py
```

Expected output:

```
RESULTS: 8/8 PASS (100%)
  Token Estimation:    4/4
  Sampling Thresholds: 6/6
  Target Percentages:  7/7
  Critical Preservation: 1/1
  Profile Filtering:   3/3
  Sampling Accuracy:   4/4
  Full Pipeline:       3/3
  Resource Types:      1/1
```

---

## Unit Test Coverage

### test_inventory_optimizer.py (35 tests)

| Group | Tests | What Is Verified |
|---|---|---|
| Token estimation | 4 | Empty, small, 1 KB, 10 KB inputs → accurate to ±0% |
| Sampling thresholds | 4 | `should_sample()` returns False at ≤100, True at >100 |
| Target percentages | 4 | 100%, 80%, 60%, 40% at correct size boundaries |
| Resource priority | 5 | Priority scores assigned correctly per resource type |
| Critical detection | 4 | 11 resource types always identified as critical |
| Profile filtering | 5 | Each profile reorders resources by relevance correctly |
| Sampling | 5 | Sample size within tolerance; critical resources preserved |
| Sampling report | 2 | `sampled` flag is True only when resources were dropped |
| Inventory to JSON | 2 | JSON serialization round-trip is lossless |

### test_ai_client.py (9 tests)

| Group | Tests | What Is Verified |
|---|---|---|
| Token estimation | 3 | `estimate_prompt_tokens()` scales correctly with text size |
| API safeguards | 6 | `complete()` validates token budget before calling API; oversized prompts raise `ValueError`; `None` usage handled gracefully |

---

## End-to-End Validation Results

All 8 test categories were validated on **April 23, 2026** using synthetic inventory data at three scales. No Azure credentials are required.

### Results Summary

| Test | Category | Scale | Result | Key Finding |
|---|---|---|---|---|
| 1 | Token Estimation | — | ✅ 4/4 | 224 tokens/KB ratio accurate to ±0% |
| 2 | Sampling Thresholds | 50 → 1,000 | ✅ 6/6 | Threshold triggers exactly at 101 resources |
| 3 | Target Percentages | All tiers | ✅ 7/7 | 100% / 80% / 60% / 40% all exact at boundaries |
| 4 | Critical Preservation | 500 resources | ✅ 1/1 | 168/168 critical resources preserved (100%) |
| 5 | Profile Filtering | 3 profiles | ✅ 3/3 | Security, Networking, Architecture all filter correctly |
| 6 | Sampling Accuracy | 200 / 400 / 600 | ✅ 4/4 | Achieves targets ±15% (tolerance due to critical resource density) |
| 7 | Full Pipeline | 50 / 200 / 500 | ✅ 3/3 | 20.4% reduction @ 200 resources; 40.6% @ 500 resources |
| 8 | Resource Types | All types | ✅ 1/1 | All 12 tested types have priorities assigned |

### Detailed Pipeline Results

#### Small Environment (50 resources)
- Sampling: Not applied (below threshold)
- Input tokens: ~4,236
- Output tokens: ~4,236
- Reduction: 0%
- Status: ✅ Full inventory analyzed

#### Medium Environment (200 resources)
- Sampling: Applied at 80% target
- Input tokens before: ~16,984
- Input tokens after: ~13,516
- Reduction: **20.4%** (saved ~3,468 tokens)
- Status: ✅ 160 resources analyzed; all critical preserved

#### Large Environment (500 resources)
- Sampling: Applied at 60% target
- Input tokens before: ~42,532
- Input tokens after: ~25,257
- Reduction: **40.6%** (saved ~17,275 tokens)
- Status: ✅ 300 resources analyzed; all critical preserved (168/168)

### Notes on Sampling Accuracy

At Very Large scale (600+ resources), the achieved reduction may be lower than the 40% target (e.g. 56% kept vs. 40% target). This is **by design**: critical resources are always preserved regardless of the target percentage. In environments with high critical resource density, the sampler prioritizes analysis quality over strict target adherence.

---

## Continuous Integration

### GitHub Actions (Template)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest-cov

      - name: Run unit tests
        run: pytest tests/ -v --cov=modules --cov-report=xml

      - name: Run end-to-end validation
        run: python test_end_to_end.py

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

### Pre-Commit Hook (Optional)

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: unit-tests
        name: Unit Tests
        entry: pytest tests/ -q
        language: system
        pass_filenames: false
        always_run: true
```

Install: `pip install pre-commit && pre-commit install`

---

## Known Gaps & Roadmap

### Current Coverage Gaps

| Area | Gap | Priority |
|---|---|---|
| `modules/inventory.py` | No unit tests for Resource Graph pagination | Medium |
| `modules/export_csv.py` | No unit tests for CSV column derivation | Low |
| `modules/prompt_loader.py` | No unit tests for profile parsing | Medium |
| `modules/export_markdown.py` | No unit tests for Mermaid normalization | Low |
| Streamlit pages | No UI tests (Selenium / Playwright) | Low |
| Live Azure integration | No tests with actual Azure credentials | High |

### Recommended Next Tests

1. **Live Azure smoke test** — Run against a sandbox subscription with known resource counts; verify inventory size and sampling report match expected values.
2. **Profile parsing tests** — Verify `prompt_loader.py` correctly parses all 8 profiles from `agent_use_cases.txt`.
3. **CSV derivation tests** — Verify `iac_hint`, `service_category`, `is_child_resource` columns are computed correctly.
4. **Mermaid normalization tests** — Verify the Mermaid diagram output is valid syntax after LLM generation + normalization.

---

→ [Getting Started](./GETTING_STARTED.md) | [Architecture](./ARCHITECTURE.md) | [Capacity & Scaling](./CAPACITY_AND_SCALING.md) | [Troubleshooting](./TROUBLESHOOTING.md)
