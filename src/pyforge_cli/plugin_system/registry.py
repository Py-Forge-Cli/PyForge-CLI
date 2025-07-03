"""
Extension registry for tracking and managing loaded plugins.

This module provides a thread-safe registry for managing plugin states,
metadata, and enabling/disabling functionality.
"""

import threading
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..extensions.base import BaseExtension
from .exceptions import PluginError

logger = logging.getLogger(__name__)


class PluginState(Enum):
    """Possible states for a plugin."""
    DISCOVERED = "discovered"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class PluginInfo:
    """Information about a registered plugin."""
    name: str
    state: PluginState
    extension: Optional[BaseExtension] = None
    error_message: Optional[str] = None
    loaded_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class ExtensionRegistry:
    """
    Thread-safe registry for managing PyForge extensions.
    
    This registry tracks plugin states, provides metadata access,
    and supports enabling/disabling plugins at runtime.
    """
    
    def __init__(self):
        """Initialize the extension registry."""
        self._plugins: Dict[str, PluginInfo] = {}
        self._lock = threading.RLock()
        self._disabled_plugins: set = set()
        self.logger = logging.getLogger(__name__)
    
    def register_discovered(self, name: str) -> None:
        """
        Register a newly discovered plugin.
        
        Args:
            name: Plugin name
        """
        with self._lock:
            if name not in self._plugins:
                self._plugins[name] = PluginInfo(
                    name=name,
                    state=PluginState.DISCOVERED,
                    enabled=name not in self._disabled_plugins
                )
                self.logger.debug(f"Registered discovered plugin: {name}")
    
    def update_state(self, name: str, state: PluginState, 
                    error_message: Optional[str] = None) -> None:
        """
        Update the state of a plugin.
        
        Args:
            name: Plugin name
            state: New plugin state
            error_message: Optional error message for failed states
        """
        with self._lock:
            if name not in self._plugins:
                self.register_discovered(name)
            
            plugin_info = self._plugins[name]
            plugin_info.state = state
            
            if error_message:
                plugin_info.error_message = error_message
            
            if state == PluginState.LOADED:
                plugin_info.loaded_at = datetime.now()
            
            self.logger.info(f"Plugin {name} state changed to: {state.value}")
    
    def register_extension(self, name: str, extension: BaseExtension) -> None:
        """
        Register a loaded extension instance.
        
        Args:
            name: Plugin name
            extension: Extension instance
        """
        with self._lock:
            if name not in self._plugins:
                self.register_discovered(name)
            
            plugin_info = self._plugins[name]
            plugin_info.extension = extension
            plugin_info.metadata = {
                'version': extension.version,
                'description': extension.description,
                'class': extension.__class__.__name__
            }
            
            self.update_state(name, PluginState.LOADED)
    
    def get_plugin_info(self, name: str) -> Optional[PluginInfo]:
        """
        Get information about a specific plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            PluginInfo or None if not found
        """
        with self._lock:
            return self._plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, PluginInfo]:
        """
        Get information about all registered plugins.
        
        Returns:
            Dictionary of plugin name to PluginInfo
        """
        with self._lock:
            return self._plugins.copy()
    
    def get_enabled_extensions(self) -> Dict[str, BaseExtension]:
        """
        Get all enabled and successfully loaded extensions.
        
        Returns:
            Dictionary of plugin name to extension instance
        """
        with self._lock:
            return {
                name: info.extension
                for name, info in self._plugins.items()
                if info.enabled and info.extension is not None
                and info.state in (PluginState.LOADED, PluginState.INITIALIZED)
            }
    
    def enable_plugin(self, name: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was enabled, False if not found
        """
        with self._lock:
            if name in self._plugins:
                self._plugins[name].enabled = True
                self._disabled_plugins.discard(name)
                self.logger.info(f"Plugin {name} enabled")
                return True
            return False
    
    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was disabled, False if not found
        """
        with self._lock:
            if name in self._plugins:
                self._plugins[name].enabled = False
                self._disabled_plugins.add(name)
                self.logger.info(f"Plugin {name} disabled")
                return True
            return False
    
    def is_plugin_enabled(self, name: str) -> bool:
        """
        Check if a plugin is enabled.
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin is enabled, False otherwise
        """
        with self._lock:
            plugin = self._plugins.get(name)
            return plugin.enabled if plugin else False
    
    def get_failed_plugins(self) -> Dict[str, str]:
        """
        Get all plugins that failed to load or initialize.
        
        Returns:
            Dictionary of plugin name to error message
        """
        with self._lock:
            return {
                name: info.error_message or "Unknown error"
                for name, info in self._plugins.items()
                if info.state == PluginState.FAILED
            }
    
    def get_plugin_stats(self) -> Dict[str, int]:
        """
        Get statistics about registered plugins.
        
        Returns:
            Dictionary with counts by state
        """
        with self._lock:
            stats = {state.value: 0 for state in PluginState}
            for plugin in self._plugins.values():
                stats[plugin.state.value] += 1
            
            stats['total'] = len(self._plugins)
            stats['enabled'] = sum(1 for p in self._plugins.values() if p.enabled)
            stats['disabled'] = sum(1 for p in self._plugins.values() if not p.enabled)
            
            return stats
    
    def clear(self) -> None:
        """Clear all registered plugins (mainly for testing)."""
        with self._lock:
            self._plugins.clear()
            self._disabled_plugins.clear()


# Global registry instance
extension_registry = ExtensionRegistry()