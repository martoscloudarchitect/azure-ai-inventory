"""Profile-specific graph adapters for network visualization.

Each profile (architecture, security, networking, etc.) provides a tailored
graph configuration that emphasizes profile-specific relationships, node
properties, and visual cues.
"""

from modules.graph_profiles.base import ProfileGraphAdapter
from modules.graph_profiles.architecture import ArchitectureGraphAdapter
from modules.graph_profiles.security import SecurityGraphAdapter
from modules.graph_profiles.networking import NetworkingGraphAdapter
from modules.graph_profiles.bcdr import BCDRGraphAdapter
from modules.graph_profiles.governance import GovernanceGraphAdapter
from modules.graph_profiles.observability import ObservabilityGraphAdapter
from modules.graph_profiles.defender import DefenderGraphAdapter

__all__ = [
    "ProfileGraphAdapter",
    "ArchitectureGraphAdapter",
    "SecurityGraphAdapter",
    "NetworkingGraphAdapter",
    "BCDRGraphAdapter",
    "GovernanceGraphAdapter",
    "ObservabilityGraphAdapter",
    "DefenderGraphAdapter",
    "get_adapter_for_profile",
]


def get_adapter_for_profile(profile_name: str) -> ProfileGraphAdapter:
    """Load the appropriate adapter for a given profile.
    
    Args:
        profile_name: One of 'architecture', 'security', 'networking', 'bcdr',
                     'governance', 'observability', 'defender'
    
    Returns:
        Instantiated ProfileGraphAdapter subclass
    
    Raises:
        ValueError: If profile_name is not recognized
    """
    adapters = {
        "architecture": ArchitectureGraphAdapter(),
        "security": SecurityGraphAdapter(),
        "networking": NetworkingGraphAdapter(),
        "bcdr": BCDRGraphAdapter(),
        "governance": GovernanceGraphAdapter(),
        "observability": ObservabilityGraphAdapter(),
        "defender": DefenderGraphAdapter(),
    }
    
    if profile_name not in adapters:
        raise ValueError(
            f"Unknown profile: {profile_name}. "
            f"Must be one of: {list(adapters.keys())}"
        )
    
    return adapters[profile_name]
