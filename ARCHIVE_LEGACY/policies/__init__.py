from .policy_engine import PolicyEngine
from .registry.policy_registry import PolicyRegistry
from .rules.global_policies import arka_global_policy

# Create a global registry instance
registry = PolicyRegistry()

# Register all default policies here
registry.register("arka_global_policy", arka_global_policy)

# Create a global policy engine instance
policy_engine = PolicyEngine()

# Inject the registry into the engine
policy_engine.registry = registry

# Export for external use
__all__ = ["policy_engine", "registry"]
