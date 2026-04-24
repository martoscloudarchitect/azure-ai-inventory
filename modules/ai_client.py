"""Send chat completion requests to Azure OpenAI via the openai SDK."""

from openai import AzureOpenAI


def estimate_prompt_tokens(system_prompt: str, user_prompt: str) -> int:
    """Estimate input token count using empirical ratio (224 tokens/KB).
    
    Conservative estimate based on observed data:
    - 120 KB inventory JSON = ~26,963 tokens (actual)
    - Ratio: 26,963 / 120 ≈ 224.69 tokens/KB
    
    Args:
        system_prompt: System prompt text
        user_prompt: User prompt text (typically contains inventory JSON)
        
    Returns:
        Estimated input token count
    """
    total_text = system_prompt + "\n" + user_prompt
    size_kb = len(total_text.encode("utf-8")) / 1024
    return int(size_kb * 224)


def complete(
    client: AzureOpenAI,
    deployment: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float = 0.3,
    max_input_tokens: int = 272000,
) -> dict:
    """Call Azure OpenAI and return content + usage dict.
    
    Validates that estimated input tokens do not exceed max_input_tokens before
    making the API call. This provides early rejection for oversized prompts.

    Args:
        client: AzureOpenAI client instance
        deployment: Model deployment name
        system_prompt: System prompt text
        user_prompt: User prompt text
        max_tokens: Maximum completion tokens to generate
        temperature: Sampling temperature (0.0–2.0, default 0.3)
        max_input_tokens: Maximum allowed input tokens (default 272000)
        
    Returns:
        {
            "content": str,
            "usage": {
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int,
            }
        }
        
    Raises:
        ValueError: If estimated input tokens exceed max_input_tokens
    """
    # Estimate input tokens before making API call
    est_input = estimate_prompt_tokens(system_prompt, user_prompt)
    input_usage_percent = round((est_input / max_input_tokens) * 100, 2) if max_input_tokens else 0
    if est_input > max_input_tokens:
        raise ValueError(
            f"Input would be ~{est_input} tokens, exceeds limit of {max_input_tokens}. "
            f"Inventory too large for this profile. Consider sampling or exporting CSV."
        )
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )

    usage = response.usage
    return {
        "content": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
            "estimated_input_tokens": est_input,
            "max_input_tokens": max_input_tokens,
            "input_usage_percent": input_usage_percent,
        },
    }
