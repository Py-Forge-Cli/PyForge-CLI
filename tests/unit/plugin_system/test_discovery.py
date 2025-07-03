"""Unit tests for plugin discovery system."""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import TimeoutError

from pyforge_cli.plugin_system.discovery import PluginDiscovery
from pyforge_cli.plugin_system.exceptions import PluginLoadError
from pyforge_cli.extensions.base import BaseExtension


class MockExtension(BaseExtension):
    """Mock extension for testing."""
    
    def is_available(self) -> bool:
        return True
    
    def initialize(self) -> bool:
        return True


class FailingExtension(BaseExtension):
    """Extension that fails to initialize."""
    
    def is_available(self) -> bool:
        return True
    
    def initialize(self) -> bool:
        raise Exception("Initialization failed")


class UnavailableExtension(BaseExtension):
    """Extension that is not available."""
    
    def is_available(self) -> bool:
        return False
    
    def initialize(self) -> bool:
        return True


class SlowExtension(BaseExtension):
    """Extension that takes too long to initialize."""
    
    def is_available(self) -> bool:
        return True
    
    def initialize(self) -> bool:
        import time
        time.sleep(10)  # Longer than timeout
        return True


class TestPluginDiscovery:
    """Test cases for PluginDiscovery class."""
    
    def test_init(self):
        """Test PluginDiscovery initialization."""
        discovery = PluginDiscovery()
        assert discovery._extensions == {}
        assert discovery._converters == {}
        assert discovery._failed_plugins == {}
    
    @patch('pyforge_cli.plugin_system.discovery.metadata.entry_points')
    def test_discover_extensions_python310(self, mock_entry_points):
        """Test extension discovery on Python 3.10+."""
        # Mock entry point
        mock_ep = Mock()
        mock_ep.name = 'test_extension'
        mock_ep.load.return_value = MockExtension
        
        # Mock entry_points to return our mock
        mock_entry_points.return_value = [mock_ep]
        
        discovery = PluginDiscovery()
        with patch.object(sys, 'version_info', (3, 10, 0)):
            extensions = discovery.discover_extensions()
        
        assert 'test_extension' in extensions
        assert isinstance(extensions['test_extension'], MockExtension)
        mock_entry_points.assert_called_once_with(group='pyforge.extensions')
    
    @patch('pyforge_cli.plugin_system.discovery.metadata.entry_points')
    def test_discover_extensions_python39(self, mock_entry_points):
        """Test extension discovery on Python 3.9."""
        # Mock entry point
        mock_ep = Mock()
        mock_ep.name = 'test_extension'
        mock_ep.load.return_value = MockExtension
        
        # Mock entry_points with select method
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps
        
        discovery = PluginDiscovery()
        with patch.object(sys, 'version_info', (3, 9, 0)):
            extensions = discovery.discover_extensions()
        
        assert 'test_extension' in extensions
        assert isinstance(extensions['test_extension'], MockExtension)
        mock_eps.select.assert_called_once_with(group='pyforge.extensions')
    
    @patch('pyforge_cli.plugin_system.discovery.metadata.entry_points')
    def test_discover_extensions_load_error(self, mock_entry_points):
        """Test handling of extension load errors."""
        # Mock entry point that fails to load
        mock_ep = Mock()
        mock_ep.name = 'failing_extension'
        mock_ep.load.side_effect = ImportError("Module not found")
        
        mock_entry_points.return_value = [mock_ep]
        
        discovery = PluginDiscovery()
        extensions = discovery.discover_extensions()
        
        assert 'failing_extension' not in extensions
        assert 'failing_extension' in discovery._failed_plugins
    
    @patch('pyforge_cli.plugin_system.discovery.metadata.entry_points')
    def test_discover_converters(self, mock_entry_points):
        """Test converter discovery."""
        # Mock converter entry point
        mock_converter = Mock()
        mock_ep = Mock()
        mock_ep.name = 'test_converter'
        mock_ep.load.return_value = mock_converter
        
        mock_entry_points.return_value = [mock_ep]
        
        discovery = PluginDiscovery()
        converters = discovery.discover_converters()
        
        assert 'test_converter' in converters
        assert converters['test_converter'] == mock_converter
    
    def test_initialize_extensions_success(self):
        """Test successful extension initialization."""
        discovery = PluginDiscovery()
        discovery._extensions = {
            'mock': MockExtension()
        }
        
        results = discovery.initialize_extensions()
        assert results['mock'] is True
    
    def test_initialize_extensions_unavailable(self):
        """Test initialization of unavailable extension."""
        discovery = PluginDiscovery()
        discovery._extensions = {
            'unavailable': UnavailableExtension()
        }
        
        results = discovery.initialize_extensions()
        assert results['unavailable'] is False
    
    def test_initialize_extensions_failure(self):
        """Test handling of extension initialization failure."""
        discovery = PluginDiscovery()
        discovery._extensions = {
            'failing': FailingExtension()
        }
        
        results = discovery.initialize_extensions()
        assert results['failing'] is False
    
    def test_initialize_extensions_timeout(self):
        """Test handling of extension initialization timeout."""
        discovery = PluginDiscovery()
        discovery._extensions = {
            'slow': SlowExtension()
        }
        
        # Temporarily reduce timeout for faster testing
        original_timeout = discovery.INIT_TIMEOUT
        discovery.INIT_TIMEOUT = 0.1
        
        try:
            results = discovery.initialize_extensions()
            assert results['slow'] is False
        finally:
            discovery.INIT_TIMEOUT = original_timeout
    
    def test_get_failed_plugins(self):
        """Test getting failed plugins information."""
        discovery = PluginDiscovery()
        discovery._failed_plugins = {
            'test1': 'Error 1',
            'test2': 'Error 2'
        }
        
        failed = discovery.get_failed_plugins()
        assert failed == discovery._failed_plugins
        assert failed is not discovery._failed_plugins  # Should be a copy
    
    @patch('pyforge_cli.plugin_system.discovery.metadata.entry_points')
    def test_caching(self, mock_entry_points):
        """Test that discovery results are cached."""
        mock_ep = Mock()
        mock_ep.name = 'test_extension'
        mock_ep.load.return_value = MockExtension
        
        mock_entry_points.return_value = [mock_ep]
        
        discovery = PluginDiscovery()
        
        # First call
        extensions1 = discovery.discover_extensions()
        # Second call should return cached results
        extensions2 = discovery.discover_extensions()
        
        assert extensions1 is extensions2
        # entry_points should only be called once due to caching
        mock_entry_points.assert_called_once()


class TestBaseExtension:
    """Test cases for BaseExtension class."""
    
    def test_base_extension_interface(self):
        """Test that BaseExtension defines the required interface."""
        # Ensure abstract methods are defined
        assert hasattr(BaseExtension, 'is_available')
        assert hasattr(BaseExtension, 'initialize')
        assert hasattr(BaseExtension, 'get_commands')
        assert hasattr(BaseExtension, 'get_converters')
        assert hasattr(BaseExtension, 'enhance_convert_command')
        assert hasattr(BaseExtension, 'post_conversion_hook')
    
    def test_extension_metadata(self):
        """Test extension metadata handling."""
        ext = MockExtension()
        assert ext.name == 'mock'
        assert ext.version == '1.0.0'
        
        info = ext.get_info()
        assert info['name'] == 'mock'
        assert info['version'] == '1.0.0'
        assert info['available'] is True
    
    def test_default_methods(self):
        """Test default implementations of optional methods."""
        ext = MockExtension()
        
        # Default implementations should return empty results
        assert ext.get_commands() == []
        assert ext.get_converters() == {}
        
        # Pass-through methods
        ctx = Mock()
        kwargs = {'test': 'value'}
        assert ext.enhance_convert_command(ctx, **kwargs) == kwargs
        
        result = {'success': True}
        assert ext.post_conversion_hook(result) == result