"""Shared helpers for the Streamlit dashboard."""

import json
import re
import subprocess
import sys
from pathlib import Path

import streamlit as st

_PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_EXPORT_DIR = _PROJECT_DIR / "data_export"
_SCRIPT = _PROJECT_DIR / "AI_Inventory_Architect.py"
_USE_CASES_FILE = _PROJECT_DIR / "agent_use_cases.txt"

# Import the canonical profile list from the same source the CLI uses.
sys.path.insert(0, str(_PROJECT_DIR))
from modules.prompt_loader import list_profiles as _list_profiles_from_file  # noqa: E402


def _get_profiles() -> list[str]:
    """Return available deep-dive profiles from agent_use_cases.txt."""
    try:
        profiles = _list_profiles_from_file(_USE_CASES_FILE)
        # Exclude discovery — it runs automatically in Phase 1.
        return [p for p in profiles if p != "discovery"]
    except (FileNotFoundError, OSError, ValueError):
        return ["architecture", "bcdr", "security", "observability", "governance", "networking", "defender"]


# ── Data helpers ─────────────────────────────────────────────────────────


def list_runs() -> list[str]:
    """Return timestamped run folder names, newest first."""
    if not DATA_EXPORT_DIR.is_dir():
        return []
    return sorted(
        [d.name for d in DATA_EXPORT_DIR.iterdir() if d.is_dir()],
        reverse=True,
    )


def run_path(run_name: str) -> Path:
    """Return the absolute path for a run folder."""
    return DATA_EXPORT_DIR / run_name


def load_json(filepath: Path) -> dict | list | None:
    """Load a JSON file, returning None on failure."""
    if not filepath.is_file():
        return None
    return json.loads(filepath.read_text(encoding="utf-8"))


def load_markdown(filepath: Path) -> str | None:
    """Load a Markdown file, returning None on failure."""
    if not filepath.is_file():
        return None
    return filepath.read_text(encoding="utf-8")


def extract_mermaid_block(md_text: str) -> str | None:
    """Extract the first ```mermaid ... ``` fenced block from Markdown."""
    match = re.search(r"```mermaid\s*\n(.*?)```", md_text, re.DOTALL)
    if not match:
        return None
    return _sanitize_mermaid(match.group(1).strip())


def _sanitize_mermaid(code: str) -> str:
    """Fix common LLM-generated Mermaid syntax issues.

    1. ``&quot;`` HTML entities inside node/subgraph labels cause doubled
       quotes after the browser decodes them (``[""label""]``).
       Strip them since the text is already wrapped in ``["..."]``.
    2. ``<br/>`` → ``<br>`` for consistency (Mermaid prefers ``<br>``).
    3. Add fallback ``classDef`` lines when classes like ``:::highrisk``
       are referenced but never defined.
    """
    code = code.replace("&quot;", "")
    code = code.replace("<br/>", "<br>")

    # Collect referenced :::className tokens.
    referenced = set(re.findall(r":::(\w+)", code))
    # Collect defined classDef names.
    defined = set(re.findall(r"classDef\s+(\w+)", code))
    missing = referenced - defined

    if missing:
        defs = "\n".join(
            f"  classDef {cls} fill:#f5f5f5,stroke:#999,stroke-width:1px"
            for cls in sorted(missing)
        )
        code = defs + "\n" + code

    return code


def list_report_files(run_dir: Path) -> list[Path]:
    """Return .md report files excluding discovery.md."""
    return sorted(
        f for f in run_dir.glob("*.md")
        if f.name != "discovery.md"
    )


def detect_profile(run_dir: Path) -> str | None:
    """Detect the profile name from the report .md file in a run."""
    reports = list_report_files(run_dir)
    return reports[0].stem if reports else None


# ── Shared sidebar ───────────────────────────────────────────────────────


def render_sidebar(pages: list | None = None) -> Path | None:
    """Render the global sidebar and return the active run directory (or None).

    Parameters
    ----------
    pages : list[st.Page] | None
        Page objects to render as navigation links once an assessment is selected.
    """
    st.sidebar.caption("⚠️ **POC / Experimental** — AzurePrism is a proof-of-concept "
                       "and is not intended for production use.")
    runs = list_runs()

    st.sidebar.header("📂 Previous Assessments")

    if not runs:
        st.sidebar.info("No assessment runs found yet.")
        st.sidebar.divider()
        _render_new_assessment()
        _render_sidebar_footer()
        return None

    if "selected_run" not in st.session_state or st.session_state.selected_run not in runs:
        st.session_state.selected_run = runs[0]

    # Apply deferred selection from a just-completed assessment run.
    if "_pending_run" in st.session_state:
        st.session_state.selected_run = st.session_state.pop("_pending_run")

    st.sidebar.selectbox("Run", runs, key="selected_run", label_visibility="collapsed")

    run_dir = run_path(st.session_state.selected_run)

    # Run metadata caption
    profile = detect_profile(run_dir)
    file_count = len([f for f in run_dir.iterdir() if f.is_file()])
    summary = load_json(run_dir / "discovery_summary.json")
    totals = (
        summary.get("totals", [{}])[0]
        if isinstance(summary, dict) and summary.get("totals")
        else {}
    )
    res = totals.get("resource_count", "—")

    parts = []
    if profile:
        parts.append(f"**Profile:** {profile}")
    parts.append(f"**Resources:** {res}")
    parts.append(f"**Files:** {file_count}")
    st.sidebar.caption(" · ".join(parts))

    # ── Page navigation links (shown only when an assessment is selected) ─
    if pages:
        st.sidebar.divider()
        for page in pages:
            st.sidebar.page_link(page)

    st.sidebar.divider()
    _render_new_assessment()
    _render_sidebar_footer()

    return run_dir


def _render_sidebar_footer() -> None:
    """Contact card at the bottom of the sidebar."""
    st.sidebar.divider()
    st.sidebar.subheader("Contributors")
    st.sidebar.markdown(
        "**Diego Martos**  \n"
        "Sr. Digital Solution Specialist – Azure  \n"
        "SME & C: West U.S. – Americas STU\n\n"
        "**Marcos Augusto Motta dos Santos**  \n"
        "Sr. Digital Solution Engineer  \n"
        "SME & C: West U.S. – Azure"
    )


def _render_new_assessment() -> None:
    """New Assessment controls in the sidebar."""
    st.sidebar.header("▶ New Assessment")
    profile = st.sidebar.selectbox("Profile", _get_profiles(), key="sb_new_profile")

    if st.sidebar.button("Run Assessment", type="primary", use_container_width=True):
        _execute_assessment(profile)


def _execute_assessment(profile: str) -> None:
    """Run AI_Inventory_Architect.py and stream output in the sidebar."""
    cmd = [sys.executable, str(_SCRIPT), "--profile", profile]
    with st.sidebar:
        with st.status(f"Running **{profile}**…", expanded=True) as status:
            log_area = st.empty()
            lines: list[str] = []
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(_SCRIPT.parent),
            )
            for line in proc.stdout:  # type: ignore[union-attr]
                lines.append(line.rstrip())
                log_area.code("\n".join(lines[-15:]), language="text")
            proc.wait()
            if proc.returncode == 0:
                status.update(label="✓ Completed", state="complete")
                new_runs = list_runs()
                if new_runs:
                    st.session_state._pending_run = new_runs[0]
                st.rerun()
            else:
                status.update(label=f"✗ Failed (exit {proc.returncode})", state="error")
