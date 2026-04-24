"""Inventory sampling and filtering for token optimization."""

import json
from datetime import datetime
from typing import Any

from modules.constants import (
    CRITICAL_RESOURCE_TYPES,
    PROFILE_RESOURCE_FILTERS,
    RESOURCE_TYPE_PRIORITIES,
    SAMPLING_TARGET_PCT_LARGE,
    SAMPLING_TARGET_PCT_MEDIUM,
    SAMPLING_TARGET_PCT_SMALL,
    SAMPLING_THRESHOLD_LARGE,
    SAMPLING_THRESHOLD_MEDIUM,
    SAMPLING_THRESHOLD_MIN,
    TOKENS_PER_KB,
)


def estimate_token_count(text: str) -> int:
    """Estimate input token count using empirical ratio (224 tokens/KB).
    
    Conservative estimate based on observed data:
    - 120 KB inventory JSON = ~26,963 tokens (actual)
    - Ratio: 26,963 / 120 ≈ 224.69 tokens/KB
    
    Args:
        text: Text to estimate token count for
        
    Returns:
        Estimated token count (rounded)
    """
    if not text:
        return 0
    size_kb = len(text.encode("utf-8")) / 1024
    return int(size_kb * TOKENS_PER_KB)


def should_sample(inventory: list) -> bool:
    """Return True if inventory size warrants sampling.
    
    Args:
        inventory: List of resource dicts
        
    Returns:
        True if len(inventory) > SAMPLING_THRESHOLD_MIN
    """
    return len(inventory) > SAMPLING_THRESHOLD_MIN


def get_target_sample_percentage(inventory_size: int) -> float:
    """Return the target percentage of resources to keep when sampling.
    
    Sampling becomes more aggressive as inventory grows.
    
    Args:
        inventory_size: Total number of resources in inventory
        
    Returns:
        Target percentage (0.0–1.0) of resources to keep
    """
    if inventory_size <= SAMPLING_THRESHOLD_MIN:
        return 1.0  # Keep all
    if inventory_size <= SAMPLING_THRESHOLD_MEDIUM:
        return SAMPLING_TARGET_PCT_SMALL  # 80%
    if inventory_size <= SAMPLING_THRESHOLD_LARGE:
        return SAMPLING_TARGET_PCT_MEDIUM  # 60%
    return SAMPLING_TARGET_PCT_LARGE  # 40%


def get_resource_priority(resource: dict) -> int:
    """Get sampling priority for a resource.
    
    Higher priority = keep first when sampling.
    
    Args:
        resource: Resource dict (must have 'type' key)
        
    Returns:
        Priority score (int)
    """
    resource_type = resource.get("type", "")
    
    # Check for exact type match first
    if resource_type in RESOURCE_TYPE_PRIORITIES:
        return RESOURCE_TYPE_PRIORITIES[resource_type]
    
    # Check for partial match (e.g., "Microsoft.Compute/*")
    for key, priority in RESOURCE_TYPE_PRIORITIES.items():
        if key != "__default__" and resource_type.startswith(key):
            return priority
    
    # Default priority for unknown types
    return RESOURCE_TYPE_PRIORITIES.get("__default__", 30)


def is_critical_resource(resource: dict) -> bool:
    """Check if resource is critical and should never be dropped.
    
    Args:
        resource: Resource dict (must have 'type' key)
        
    Returns:
        True if resource type is in CRITICAL_RESOURCE_TYPES
    """
    resource_type = resource.get("type", "")
    
    # Exact match
    if resource_type in CRITICAL_RESOURCE_TYPES:
        return True
    
    # Partial match (prefix)
    for critical_type in CRITICAL_RESOURCE_TYPES:
        if resource_type.startswith(critical_type):
            return True
    
    return False


def apply_profile_filter(inventory: list, profile: str) -> list:
    """Filter inventory for profile-specific resource types.
    
    For profile-specific filtering, keep only resources relevant to that profile.
    Non-relevant resources get lower sampling priority.
    
    Args:
        inventory: List of resource dicts
        profile: Profile ID (e.g., 'security', 'networking')
        
    Returns:
        List of resources (typically same size, but reordered by relevance)
    """
    if profile not in PROFILE_RESOURCE_FILTERS:
        # Unknown profile — keep all
        return inventory
    
    filter_set = PROFILE_RESOURCE_FILTERS[profile]
    
    if filter_set == {"__all__"}:
        # This profile needs full inventory
        return inventory
    
    # Separate resources into "high relevance" and "low relevance"
    high_relevance = []
    low_relevance = []
    
    for resource in inventory:
        resource_type = resource.get("type", "")
        
        # Check if this resource type matches the filter
        is_relevant = False
        for filter_type in filter_set:
            if resource_type.startswith(filter_type):
                is_relevant = True
                break
        
        if is_relevant:
            high_relevance.append(resource)
        else:
            low_relevance.append(resource)
    
    # Return high-relevance first, low-relevance second
    # This way, when sampling, high-relevance resources are kept first
    return high_relevance + low_relevance


def sample_inventory(
    inventory: list,
    profile: str = "architecture",
    target_percentage: float | None = None,
) -> list:
    """Sample inventory to reduce token count while preserving critical resources.
    
    Algorithm:
    1. If inventory size <= threshold, return unchanged
    2. Apply profile-specific filtering (reorder by relevance)
    3. Keep all critical resources (exact size may exceed target)
    4. For remaining resources, keep top N by priority + recency
    5. Return sampled inventory (typically 40–80% of original)
    
    Args:
        inventory: List of resource dicts
        profile: Profile ID for filtering (default: 'architecture')
        target_percentage: Target percentage to keep (0.0–1.0).
                          If None, auto-calculated from inventory size.
                          
    Returns:
        Sampled inventory list
    """
    if not inventory:
        return []
    
    # If already small, no need to sample
    if not should_sample(inventory):
        return inventory
    
    # Auto-calculate target if not provided
    if target_percentage is None:
        target_percentage = get_target_sample_percentage(len(inventory))
    
    # Apply profile-specific filtering (doesn't change size, just order)
    filtered = apply_profile_filter(inventory, profile)
    
    # Separate critical and non-critical resources
    critical = []
    non_critical = []
    
    for resource in filtered:
        if is_critical_resource(resource):
            critical.append(resource)
        else:
            non_critical.append(resource)
    
    # Sort non-critical by priority (descending) + recency (most recent first)
    def sort_key(r: dict) -> tuple:
        priority = get_resource_priority(r)
        # Try to extract modification date; default to epoch if missing
        modified = r.get("properties", {}).get("modificationTime") or "1970-01-01"
        try:
            modified_dt = datetime.fromisoformat(modified.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            modified_dt = datetime.min
        return (-priority, -modified_dt.timestamp())  # Descending priority, most recent first
    
    non_critical.sort(key=sort_key)
    
    # Calculate how many non-critical resources to keep
    target_count = int(len(filtered) * target_percentage)
    remaining_budget = max(0, target_count - len(critical))
    
    # Combine critical + sampled non-critical
    sampled = critical + non_critical[:remaining_budget]
    
    return sampled


def estimate_prompt_tokens(system_prompt: str, user_prompt: str) -> int:
    """Estimate total input token count for a prompt pair.
    
    Args:
        system_prompt: System prompt text
        user_prompt: User prompt text (typically contains inventory JSON)
        
    Returns:
        Estimated total input tokens
    """
    total_text = system_prompt + "\n" + user_prompt
    return estimate_token_count(total_text)


def inventory_to_json_string(inventory: list) -> str:
    """Convert inventory list to JSON string.
    
    Args:
        inventory: List of resource dicts
        
    Returns:
        JSON string representation
    """
    return json.dumps({"inventory": inventory}, indent=2)


def get_sampling_report(
    original_inventory: list,
    sampled_inventory: list,
) -> dict:
    """Generate a summary report of sampling operations.
    
    Args:
        original_inventory: Original inventory before sampling
        sampled_inventory: Sampled inventory after sampling
        
    Returns:
        Dict with sampling stats
    """
    original_count = len(original_inventory)
    sampled_count = len(sampled_inventory)
    resources_dropped = original_count - sampled_count
    reduction_pct = round(
        ((original_count - sampled_count) / original_count * 100)
        if original_count > 0
        else 0,
        1,
    )
    
    return {
        "original_count": original_count,
        "sampled_count": sampled_count,
        "resources_dropped": resources_dropped,
        "reduction_percentage": reduction_pct,
        "sampled": resources_dropped > 0,  # True if resources were actually dropped
    }
