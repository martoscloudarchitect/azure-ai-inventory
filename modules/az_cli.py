"""Thin wrapper around Azure CLI subprocess calls."""

import json
import re
import subprocess


def run(args: list[str]) -> str:
    """Execute an Azure CLI command and return its stdout."""
    result = subprocess.run(
        ["az", *args],
        capture_output=True,
        text=True,
        shell=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to execute 'az {' '.join(args)}': {result.stderr.strip()}")
    return result.stdout


# Extensions required for full functionality.
# Each entry: (extension_name, why_needed, is_critical)
_REQUIRED_EXTENSIONS: list[tuple[str, str, bool]] = [
    ("resource-graph", "Required for 'az graph query' — inventory collection will fail without it.", True),
]


def check_cli_installed() -> None:
    """Raise if Azure CLI is not available."""
    if subprocess.run(["az", "--version"], capture_output=True, shell=True).returncode != 0:
        raise RuntimeError(
            "Azure CLI was not found. Install it before running the script.\n"
            "  Windows:  winget install -e --id Microsoft.AzureCLI\n"
            "  macOS:    brew install azure-cli\n"
            "  Linux:    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        )


def check_extensions() -> None:
    """Verify that required Azure CLI extensions are installed.

    Critical extensions raise RuntimeError.  Non-critical ones print a warning.
    """
    result = subprocess.run(
        ["az", "extension", "list", "--output", "json"],
        capture_output=True,
        text=True,
        shell=True,
    )
    if result.returncode != 0:
        print("WARNING: Could not list Azure CLI extensions. Extension checks skipped.")
        return

    try:
        installed = {ext["name"] for ext in json.loads(result.stdout)}
    except (json.JSONDecodeError, KeyError, TypeError):
        print("WARNING: Could not parse Azure CLI extension list. Extension checks skipped.")
        return

    for ext_name, reason, critical in _REQUIRED_EXTENSIONS:
        if ext_name not in installed:
            msg = f"Azure CLI extension '{ext_name}' is not installed. {reason}\n  Install it with: az extension add --name {ext_name}"
            if critical:
                raise RuntimeError(msg)
            print(f"WARNING: {msg}")


def check_account() -> dict | None:
    """Return the active Azure account info, or None if unavailable."""
    result = subprocess.run(
        ["az", "account", "show", "--output", "json", "--only-show-errors"],
        capture_output=True,
        text=True,
        shell=True,
    )
    if result.returncode != 0:
        print(
            "WARNING: No active Azure session detected. "
            "The script will attempt 'az login' next, but if it fails "
            "ensure your credentials and tenant ID are correct."
        )
        return None

    try:
        account = json.loads(result.stdout)
        sub_name = account.get("name", "unknown")
        sub_id = account.get("id", "unknown")
        state = account.get("state", "unknown")
        print(f"Active Azure session: {sub_name} ({sub_id}) — state: {state}")
        if state != "Enabled":
            print(f"WARNING: Subscription state is '{state}'. Queries may fail if the subscription is disabled.")
        return {
            "subscription_name": sub_name,
            "subscription_id": sub_id,
            "state": state,
            "tenant_id": account.get("tenantId", "unknown"),
        }
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def preflight_checks() -> None:
    """Run all prerequisite checks before execution.

    Call this once at startup.  Account info is captured separately
    after login via ``check_account()``.
    """
    check_cli_installed()
    check_extensions()
    check_account()


def extract_json_payload(cli_output: str) -> str:
    """Return the first valid JSON payload found in Azure CLI output."""
    match = re.search(r'^[\[{]', cli_output, re.MULTILINE)
    if not match:
        raise ValueError(f"Azure CLI output does not contain valid JSON:\n{cli_output[:500]}")
    if match.start() > 0:
        prefix = cli_output[: match.start()].strip()
        if prefix:
            print(f"WARNING: Azure CLI returned messages before the JSON payload: {prefix}")
    return cli_output[match.start():]


def login(tenant_id: str) -> None:
    """Sign in to Azure for the given tenant."""
    print(f"Signing in to Azure tenant {tenant_id}...")
    run(["login", "--tenant", tenant_id, "--only-show-errors", "--output", "none"])
