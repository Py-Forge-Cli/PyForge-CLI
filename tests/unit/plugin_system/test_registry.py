"""Unit tests for the extension registry."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from pyforge_cli.plugin_system.registry import (
    ExtensionRegistry, PluginState, PluginInfo, extension_registry
)
from pyforge_cli.extensions.base import BaseExtension


class MockExtension(BaseExtension):
    """Mock extension for testing."""
    
    def __init__(self):
        super().__init__()
        self.version = "1.0.0"
        self.description = "Test extension"
    
    def is_available(self) -> bool:
        return True
    
    def initialize(self) -> bool:
        return True


class TestExtensionRegistry:
    """Test cases for ExtensionRegistry class."""
    
    def test_init(self):
        """Test registry initialization."""
        registry = ExtensionRegistry()
        assert registry._plugins == {}
        assert registry._disabled_plugins == set()
    
    def test_register_discovered(self):
        """Test registering a discovered plugin."""
        registry = ExtensionRegistry()
        registry.register_discovered("test_plugin")
        
        plugin_info = registry.get_plugin_info("test_plugin")
        assert plugin_info is not None
        assert plugin_info.name == "test_plugin"
        assert plugin_info.state == PluginState.DISCOVERED
        assert plugin_info.enabled is True
    
    def test_update_state(self):
        """Test updating plugin state."""
        registry = ExtensionRegistry()
        registry.register_discovered("test_plugin")
        
        registry.update_state("test_plugin", PluginState.LOADING)
        plugin_info = registry.get_plugin_info("test_plugin")
        assert plugin_info.state == PluginState.LOADING
        
        registry.update_state("test_plugin", PluginState.FAILED, "Test error")
        plugin_info = registry.get_plugin_info("test_plugin")
        assert plugin_info.state == PluginState.FAILED
        assert plugin_info.error_message == "Test error"
    
    def test_register_extension(self):
        """Test registering an extension instance."""
        registry = ExtensionRegistry()
        extension = MockExtension()
        
        registry.register_extension("test_plugin", extension)
        
        plugin_info = registry.get_plugin_info("test_plugin")
        assert plugin_info.extension is extension
        assert plugin_info.state == PluginState.LOADED
        assert plugin_info.loaded_at is not None
        assert plugin_info.metadata['version'] == "1.0.0"
        assert plugin_info.metadata['description'] == "Test extension"
        assert plugin_info.metadata['class'] == "MockExtension"
    
    def test_get_all_plugins(self):
        """Test getting all plugins."""
        registry = ExtensionRegistry()
        registry.register_discovered("plugin1")
        registry.register_discovered("plugin2")
        
        all_plugins = registry.get_all_plugins()
        assert len(all_plugins) == 2
        assert "plugin1" in all_plugins
        assert "plugin2" in all_plugins
    
    def test_get_enabled_extensions(self):
        """Test getting enabled extensions."""
        registry = ExtensionRegistry()
        ext1 = MockExtension()
        ext2 = MockExtension()
        
        registry.register_extension("plugin1", ext1)
        registry.register_extension("plugin2", ext2)
        registry.update_state("plugin1", PluginState.INITIALIZED)
        registry.update_state("plugin2", PluginState.INITIALIZED)
        
        # Disable plugin2
        registry.disable_plugin("plugin2")
        
        enabled = registry.get_enabled_extensions()
        assert len(enabled) == 1
        assert "plugin1" in enabled
        assert enabled["plugin1"] is ext1
    
    def test_enable_disable_plugin(self):
        """Test enabling and disabling plugins."""
        registry = ExtensionRegistry()
        registry.register_discovered("test_plugin")
        
        # Initially enabled
        assert registry.is_plugin_enabled("test_plugin") is True
        
        # Disable
        result = registry.disable_plugin("test_plugin")
        assert result is True
        assert registry.is_plugin_enabled("test_plugin") is False
        assert "test_plugin" in registry._disabled_plugins
        
        # Enable
        result = registry.enable_plugin("test_plugin")
        assert result is True
        assert registry.is_plugin_enabled("test_plugin") is True
        assert "test_plugin" not in registry._disabled_plugins
        
        # Non-existent plugin
        assert registry.enable_plugin("non_existent") is False
        assert registry.disable_plugin("non_existent") is False
    
    def test_get_failed_plugins(self):
        """Test getting failed plugins."""
        registry = ExtensionRegistry()
        
        registry.register_discovered("plugin1")
        registry.update_state("plugin1", PluginState.FAILED, "Error 1")
        
        registry.register_discovered("plugin2")
        registry.update_state("plugin2", PluginState.INITIALIZED)
        
        registry.register_discovered("plugin3")
        registry.update_state("plugin3", PluginState.FAILED, "Error 3")
        
        failed = registry.get_failed_plugins()
        assert len(failed) == 2
        assert failed["plugin1"] == "Error 1"
        assert failed["plugin3"] == "Error 3"
    
    def test_get_plugin_stats(self):
        """Test getting plugin statistics."""
        registry = ExtensionRegistry()
        
        registry.register_discovered("plugin1")
        registry.update_state("plugin1", PluginState.INITIALIZED)
        
        registry.register_discovered("plugin2")
        registry.update_state("plugin2", PluginState.FAILED)
        
        registry.register_discovered("plugin3")
        registry.update_state("plugin3", PluginState.LOADED)
        registry.disable_plugin("plugin3")
        
        stats = registry.get_plugin_stats()
        assert stats['total'] == 3
        assert stats['initialized'] == 1
        assert stats['failed'] == 1
        assert stats['loaded'] == 1
        assert stats['enabled'] == 2
        assert stats['disabled'] == 1
    
    def test_thread_safety(self):
        """Test thread safety of registry operations."""
        import threading
        import time
        
        registry = ExtensionRegistry()
        results = []
        
        def register_plugins():
            for i in range(10):
                registry.register_discovered(f"plugin_{threading.current_thread().name}_{i}")
                time.sleep(0.001)  # Simulate some work
            results.append(True)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_plugins, name=f"thread_{i}")
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(results) == 5
        all_plugins = registry.get_all_plugins()
        assert len(all_plugins) == 50  # 5 threads * 10 plugins each
    
    def test_clear(self):
        """Test clearing the registry."""
        registry = ExtensionRegistry()
        registry.register_discovered("plugin1")
        registry.register_discovered("plugin2")
        registry.disable_plugin("plugin2")
        
        assert len(registry.get_all_plugins()) == 2
        assert len(registry._disabled_plugins) == 1
        
        registry.clear()
        
        assert len(registry.get_all_plugins()) == 0
        assert len(registry._disabled_plugins) == 0
    
    def test_global_registry(self):
        """Test that extension_registry is a global instance."""
        assert isinstance(extension_registry, ExtensionRegistry)
        
        # Import again to verify it's the same instance
        from pyforge_cli.plugin_system.registry import extension_registry as reg2
        assert extension_registry is reg2