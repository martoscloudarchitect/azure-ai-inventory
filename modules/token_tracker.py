"""Report and persist token consumption per AI call."""

import json
from pathlib import Path


class TokenTracker:
    """Accumulates token usage records and prints summaries."""

    def __init__(self) -> None:
        self._records: list[dict] = []

    def report(self, label: str, usage: dict, max_tokens: int) -> None:
        """Print a one-line summary and store the record."""
        prompt = usage.get("prompt_tokens", 0)
        completion = usage.get("completion_tokens", 0)
        total = usage.get("total_tokens", 0)
        pct = round((completion / max_tokens) * 100, 2) if max_tokens else 0
        remaining = max(0, max_tokens - completion)

        print(
            f"{label} tokens -> prompt: {prompt}, "
            f"completion: {completion} / limit: {max_tokens} ({pct}%), "
            f"remaining: {remaining}"
        )

        self._records.append({
            "label": label,
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": total,
            "max_tokens": max_tokens,
            "usage_percent": pct,
            "remaining": remaining,
        })

    def save(self, output_dir: Path) -> None:
        """Write all records to token_usage.json in the output directory."""
        if not self._records:
            return
        out_file = output_dir / "token_usage.json"
        out_file.write_text(json.dumps(self._records, indent=2), encoding="utf-8")
        print(f"Token usage saved to: {out_file}")
