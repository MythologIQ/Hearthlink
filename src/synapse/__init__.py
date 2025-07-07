"""
Synapse - Secure External Gateway & Protocol Boundary

Sole orchestrator and gatekeeper for all inbound/outbound traffic between 
Hearthlink, plugins, external LLMs, APIs, and web resources. Synapse enforces 
protocol boundaries, logs and mediates all traffic, and provides policy-driven 
controls for plugin sandboxing, manifest enforcement, and multi-system onboarding.

All external access, plugin execution, and agent communications flow through 
Synapse and are routed through Core for context/logging.
"""

from .synapse import Synapse
from .plugin_manager import PluginManager
from .sandbox import SandboxManager
from .manifest import PluginManifest, ManifestValidator
from .permissions import PermissionManager
from .benchmark import BenchmarkManager
from .traffic_logger import TrafficLogger

__all__ = [
    'Synapse',
    'PluginManager', 
    'SandboxManager',
    'PluginManifest',
    'ManifestValidator',
    'PermissionManager',
    'BenchmarkManager',
    'TrafficLogger'
] 