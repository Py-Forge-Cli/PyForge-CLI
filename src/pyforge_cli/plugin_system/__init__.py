"""
PyForge Plugin System

This module provides the plugin discovery and loading infrastructure for PyForge CLI.
It uses Python's entry points mechanism to enable extensions without modifying core code.
"""

from .discovery import PluginDiscovery, plugin_discovery
from .exceptions import PluginError, PluginLoadError, PluginInitializationError
from .registry import ExtensionRegistry, extension_registry, PluginState, PluginInfo
from .lifecycle import ExtensionLifecycleManager, lifecycle_manager
from .hooks import ExtensionHooksManager, hooks_manager, HookType, HookResult

__all__ = [
    "PluginDiscovery",
    "plugin_discovery",
    "PluginError",
    "PluginLoadError", 
    "PluginInitializationError",
    "ExtensionRegistry",
    "extension_registry",
    "PluginState",
    "PluginInfo",
    "ExtensionLifecycleManager",
    "lifecycle_manager",
    "ExtensionHooksManager",
    "hooks_manager",
    "HookType",
    "HookResult"
]