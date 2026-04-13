"""Thin wrapper around Azure CLI subprocess calls."""

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


def check_cli_installed() -> None:
    """Raise if Azure CLI is not available."""
    if subprocess.run(["az", "--version"], capture_output=True, shell=True).returncode != 0:
        raise RuntimeError("Azure CLI was not found. Install the az command before running the script.")


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
