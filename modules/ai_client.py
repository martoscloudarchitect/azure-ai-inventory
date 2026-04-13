"""Send chat completion requests to Azure OpenAI."""

import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_VERSION = "2024-12-01-preview"


def complete(
    endpoint: str,
    api_key: str,
    deployment: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float = 0.3,
) -> dict:
    """Call Azure OpenAI and return content + usage dict.

    Returns:
        {
            "content": str,
            "usage": {
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int,
            }
        }
    """
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"

    body = json.dumps({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
    }).encode("utf-8")

    req = Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "api-key": api_key,
    })

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(
            f"Azure OpenAI request failed: {e.code} - {error_body}"
        ) from e

    usage = data.get("usage", {})
    return {
        "content": data["choices"][0]["message"]["content"],
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
    }
