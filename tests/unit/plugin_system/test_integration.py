"""Integration tests for plugin system with PyForge CLI."""

import pytest
from unittest.mock import patch, Mock

from pyforge_cli.plugin_system import plugin_discovery, PluginDiscovery
from pyforge_cli.extensions.base import BaseExtension


def test_plugin_discovery_singleton():
    """Test that plugin_discovery is a singleton instance."""
    assert isinstance(plugin_discovery, PluginDiscovery)
    
    # Should be the same instance
    from pyforge_cli.plugin_system import plugin_discovery as pd2
    assert plugin_discovery is pd2


def test_empty_discovery():
    """Test discovery when no plugins are installed."""
    discovery = PluginDiscovery()
    
    # Mock to return empty entry points
    with patch('pyforge_cli.plugin_system.discovery.metadata.entry_points') as mock_ep:
        mock_ep.return_value = []
        
        extensions = discovery.discover_extensions()
        converters = discovery.discover_converters()
        
        assert extensions == {}
        assert converters == {}


def test_base_extension_abstract():
    """Test that BaseExtension cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseExtension()


class SampleExtension(BaseExtension):
    """Sample extension for testing."""
    
    def __init__(self):
        super().__init__()
        self.initialized = False
    
    def is_available(self):
        return True
    
    def initialize(self):
        self.initialized = True
        return True


def test_extension_initialization_flow():
    """Test the complete extension initialization flow."""
    discovery = PluginDiscovery()
    
    # Manually add an extension
    ext = SampleExtension()
    discovery._extensions = {'sample': ext}
    
    # Initialize extensions
    results = discovery.initialize_extensions()
    
    assert results['sample'] is True
    assert ext.initialized is True


def test_extension_info():
    """Test extension info retrieval."""
    ext = SampleExtension()
    info = ext.get_info()
    
    assert info['name'] == 'sample'
    assert info['version'] == '1.0.0'
    assert info['available'] is True
    assert 'description' in info