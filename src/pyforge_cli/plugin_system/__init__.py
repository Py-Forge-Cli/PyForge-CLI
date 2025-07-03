"""
PyForge Plugin System

This module provides the plugin discovery and loading infrastructure for PyForge CLI.
It uses Python's entry points mechanism to enable extensions without modifying core code.
"""

from .discovery import PluginDiscovery, plugin_discovery
from .exceptions import PluginError, PluginLoadError, PluginInitializationError
from .registry import ExtensionRegistry, extension_registry, PluginState, PluginInfo

__all__ = [
    "PluginDiscovery",
    "plugin_discovery",
    "PluginError",
    "PluginLoadError", 
    "PluginInitializationError",
    "ExtensionRegistry",
    "extension_registry",
    "PluginState",
    "PluginInfo"
]