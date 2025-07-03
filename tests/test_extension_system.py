"""Unit tests for the PyForge CLI extension system."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import logging

from pyforge_cli.extensions.base import BaseExtension
from pyforge_cli.extensions.discovery import ExtensionDiscovery
from pyforge_cli.extensions.loader import ExtensionLoader, ExtensionLoadError
from pyforge_cli.extensions.registry import ExtensionRegistry, ExtensionState, ExtensionMetadata
from pyforge_cli.extensions.manager import ExtensionManager


class MockExtension(BaseExtension):
    """Mock extension for testing."""
    
    def __init__(self):
        super().__init__()
        self.initialized = False
        self.cleaned_up = False
    
    @classmethod
    def is_available(cls) -> bool:
        return True
    
    def initialize(self) -> bool:
        self.initialized = True
        return True
    
    def cleanup(self) -> None:
        self.cleaned_up = True


class FailingExtension(BaseExtension):
    """Mock extension that fails to initialize."""
    
    @classmethod
    def is_available(cls) -> bool:
        return True
    
    def initialize(self) -> bool:
        raise Exception("Initialization failed")


class UnavailableExtension(BaseExtension):
    """Mock extension that is not available."""
    
    @classmethod
    def is_available(cls) -> bool:
        return False
    
    def initialize(self) -> bool:
        return True


class TestExtensionDiscovery:
    """Test the extension discovery mechanism."""
    
    def test_discover_extensions_no_entry_points(self):
        """Test discovery when no entry points exist."""
        discovery = ExtensionDiscovery()
        
        with patch('pyforge_cli.extensions.discovery.entry_points', return_value={}):
            extensions = discovery.discover_extensions()
            assert extensions == {}
    
    def test_discover_extensions_with_entry_points(self):
        """Test discovery with valid entry points."""
        discovery = ExtensionDiscovery()
        
        # Mock entry point
        mock_ep = Mock()
        mock_ep.name = 'test_extension'
        mock_ep.value = 'test_module:TestExtension'
        
        if sys.version_info >= (3, 10):
            with patch('pyforge_cli.extensions.discovery.entry_points', return_value=[mock_ep]):
                extensions = discovery.discover_extensions()
                assert 'test_extension' in extensions
                assert extensions['test_extension'] == 'test_module:TestExtension'
        else:
            mock_eps = {discovery.ENTRY_POINT_GROUP: [mock_ep]}
            with patch('pyforge_cli.extensions.discovery.entry_points', return_value=mock_eps):
                extensions = discovery.discover_extensions()
                assert 'test_extension' in extensions
                assert extensions['test_extension'] == 'test_module:TestExtension'
    
    def test_load_extension_class_valid(self):
        """Test loading a valid extension class."""
        discovery = ExtensionDiscovery()
        
        # Mock the import
        mock_module = Mock()
        mock_module.TestExtension = MockExtension
        
        with patch('importlib.import_module', return_value=mock_module):
            ext_class = discovery.load_extension_class('test', 'test_module:TestExtension')
            assert ext_class == MockExtension
    
    def test_load_extension_class_invalid_format(self):
        """Test loading with invalid entry point format."""
        discovery = ExtensionDiscovery()
        
        ext_class = discovery.load_extension_class('test', 'invalid_format')
        assert ext_class is None
        assert 'test' in discovery._discovered_extensions
        _, error = discovery._discovered_extensions['test']
        assert isinstance(error, ValueError)
    
    def test_load_extension_class_import_error(self):
        """Test loading when module import fails."""
        discovery = ExtensionDiscovery()
        
        with patch('importlib.import_module', side_effect=ImportError("Module not found")):
            ext_class = discovery.load_extension_class('test', 'missing_module:Extension')
            assert ext_class is None
    
    def test_load_extension_class_not_base_extension(self):
        """Test loading a class that doesn't inherit from BaseExtension."""
        discovery = ExtensionDiscovery()
        
        # Mock module with non-extension class
        mock_module = Mock()
        mock_module.NotAnExtension = object
        
        with patch('importlib.import_module', return_value=mock_module):
            ext_class = discovery.load_extension_class('test', 'test_module:NotAnExtension')
            assert ext_class is None


class TestExtensionLoader:
    """Test the extension loader."""
    
    def test_load_all_extensions_empty(self):
        """Test loading when no extensions are discovered."""
        discovery = Mock()
        discovery.discover_extensions.return_value = {}
        
        loader = ExtensionLoader(discovery)
        loaded = loader.load_all_extensions()
        assert loaded == {}
    
    def test_load_all_extensions_success(self):
        """Test successfully loading extensions."""
        discovery = Mock()
        discovery.discover_extensions.return_value = {'mock': 'module:MockExtension'}
        discovery.load_extension_class.return_value = MockExtension
        
        loader = ExtensionLoader(discovery)
        loaded = loader.load_all_extensions()
        
        assert 'mock' in loaded
        assert isinstance(loaded['mock'], MockExtension)
        assert loaded['mock'].initialized
    
    def test_load_single_extension_unavailable(self):
        """Test loading an unavailable extension."""
        discovery = Mock()
        discovery.load_extension_class.return_value = UnavailableExtension
        
        loader = ExtensionLoader(discovery)
        ext = loader._load_single_extension('unavail', 'module:UnavailableExtension', 30.0)
        
        assert ext is None
        assert 'unavail' in loader._failed_extensions
    
    def test_load_single_extension_timeout(self):
        """Test extension initialization timeout."""
        # Create a slow extension
        class SlowExtension(BaseExtension):
            @classmethod
            def is_available(cls):
                return True
            
            def initialize(self):
                import time
                time.sleep(2)  # Sleep for 2 seconds
                return True
        
        discovery = Mock()
        discovery.load_extension_class.return_value = SlowExtension
        
        loader = ExtensionLoader(discovery)
        ext = loader._load_single_extension('slow', 'module:SlowExtension', 0.1)  # 100ms timeout
        
        assert ext is None
        assert 'slow' in loader._failed_extensions
    
    def test_reload_extension(self):
        """Test reloading an extension."""
        discovery = Mock()
        discovery.discover_extensions.return_value = {'mock': 'module:MockExtension'}
        discovery.load_extension_class.return_value = MockExtension
        
        loader = ExtensionLoader(discovery)
        
        # First load
        loaded = loader.load_all_extensions()
        first_instance = loaded['mock']
        
        # Reload
        success = loader.reload_extension('mock')
        assert success
        
        # Check it's a new instance
        reloaded = loader.get_extension('mock')
        assert reloaded is not first_instance
        assert isinstance(reloaded, MockExtension)


class TestExtensionRegistry:
    """Test the extension registry."""
    
    def test_register_discovered(self):
        """Test registering a discovered extension."""
        registry = ExtensionRegistry()
        registry.register_discovered('test', 'module:TestExtension')
        
        metadata = registry.get_metadata('test')
        assert metadata is not None
        assert metadata.name == 'test'
        assert metadata.entry_point == 'module:TestExtension'
        assert metadata.state == ExtensionState.DISCOVERED
    
    def test_register_loaded(self):
        """Test registering a loaded extension."""
        registry = ExtensionRegistry()
        extension = MockExtension()
        
        registry.register_loaded('test', extension, 1.5, version='1.0.0')
        
        metadata = registry.get_metadata('test')
        assert metadata.state == ExtensionState.LOADED
        assert metadata.instance == extension
        assert metadata.load_time == 1.5
        assert metadata.version == '1.0.0'
        assert registry.is_enabled('test')
    
    def test_register_failed(self):
        """Test registering a failed extension."""
        registry = ExtensionRegistry()
        error = Exception("Load failed")
        
        registry.register_failed('test', error)
        
        metadata = registry.get_metadata('test')
        assert metadata.state == ExtensionState.FAILED
        assert metadata.error == error
    
    def test_enable_disable_extension(self):
        """Test enabling and disabling extensions."""
        registry = ExtensionRegistry()
        extension = MockExtension()
        
        registry.register_loaded('test', extension, 1.0)
        assert registry.is_enabled('test')
        
        # Disable
        success = registry.disable_extension('test')
        assert success
        assert not registry.is_enabled('test')
        assert registry.get_extension('test') is None
        
        # Re-enable
        success = registry.enable_extension('test')
        assert success
        assert registry.is_enabled('test')
        assert registry.get_extension('test') == extension
    
    def test_get_extensions_by_state(self):
        """Test filtering extensions by state."""
        registry = ExtensionRegistry()
        
        registry.register_discovered('discovered', 'module:Extension')
        registry.register_loaded('loaded', MockExtension(), 1.0)
        registry.register_failed('failed', Exception())
        
        discovered = registry.get_extensions_by_state(ExtensionState.DISCOVERED)
        loaded = registry.get_extensions_by_state(ExtensionState.LOADED)
        failed = registry.get_extensions_by_state(ExtensionState.FAILED)
        
        assert 'discovered' in discovered
        assert 'loaded' in loaded
        assert 'failed' in failed
    
    def test_unregister_extension(self):
        """Test unregistering an extension."""
        registry = ExtensionRegistry()
        extension = MockExtension()
        
        registry.register_loaded('test', extension, 1.0)
        assert registry.get_extension('test') is not None
        
        success = registry.unregister('test')
        assert success
        assert registry.get_extension('test') is None
        assert extension.cleaned_up  # Cleanup was called
    
    def test_clear_registry(self):
        """Test clearing all extensions."""
        registry = ExtensionRegistry()
        ext1 = MockExtension()
        ext2 = MockExtension()
        
        registry.register_loaded('ext1', ext1, 1.0)
        registry.register_loaded('ext2', ext2, 1.0)
        
        registry.clear()
        
        assert registry.get_all_metadata() == {}
        assert ext1.cleaned_up
        assert ext2.cleaned_up


class TestExtensionManager:
    """Test the extension manager."""
    
    def test_initialize_no_extensions(self):
        """Test initialization with no extensions."""
        manager = ExtensionManager()
        
        with patch.object(manager.discovery, 'discover_extensions', return_value={}):
            manager.initialize()
            assert manager._initialized
            assert manager.get_all_extensions() == []
    
    def test_initialize_with_extensions(self):
        """Test initialization with extensions."""
        manager = ExtensionManager()
        
        mock_extension = MockExtension()
        
        with patch.object(manager.discovery, 'discover_extensions', return_value={'mock': 'module:Mock'}):
            with patch.object(manager.loader, 'load_all_extensions', return_value={'mock': mock_extension}):
                with patch.object(manager.loader, 'get_loading_stats', return_value={'mock': 1.0}):
                    manager.initialize()
                    
                    assert manager._initialized
                    extensions = manager.get_all_extensions()
                    assert len(extensions) == 1
                    assert extensions[0] == mock_extension
    
    def test_execute_hook(self):
        """Test executing hooks on extensions."""
        manager = ExtensionManager()
        
        # Create extension with hook
        class HookedExtension(MockExtension):
            def hook_test(self, value):
                return value * 2
        
        ext = HookedExtension()
        manager.registry.register_loaded('hooked', ext, 1.0)
        
        results = manager.execute_hook('hook_test', value=5)
        assert 'HookedExtension' in results
        assert results['HookedExtension'] == 10
    
    def test_execute_hook_with_error(self):
        """Test hook execution with errors."""
        manager = ExtensionManager()
        
        # Create extension with failing hook
        class FailingHookExtension(MockExtension):
            def hook_test(self):
                raise ValueError("Hook failed")
        
        ext = FailingHookExtension()
        manager.registry.register_loaded('failing', ext, 1.0)
        
        results = manager.execute_hook('hook_test')
        assert 'FailingHookExtension' in results
        assert 'error' in results['FailingHookExtension']
    
    def test_reload_extension(self):
        """Test reloading an extension through manager."""
        manager = ExtensionManager()
        
        mock_extension = MockExtension()
        manager.registry.register_loaded('mock', mock_extension, 1.0)
        
        with patch.object(manager.loader, 'reload_extension', return_value=True):
            with patch.object(manager.loader, 'get_extension', return_value=MockExtension()):
                with patch.object(manager.loader, 'get_loading_stats', return_value={'mock': 1.5}):
                    success = manager.reload_extension('mock')
                    assert success
    
    def test_get_extension_info(self):
        """Test getting extension information."""
        manager = ExtensionManager()
        
        ext = MockExtension()
        manager.registry.register_loaded('test', ext, 1.2, version='1.0.0', description='Test extension')
        
        info = manager.get_extension_info()
        assert 'test' in info
        assert info['test']['state'] == 'loaded'
        assert info['test']['version'] == '1.0.0'
        assert info['test']['load_time'] == 1.2
        assert info['test']['description'] == 'Test extension'
        assert info['test']['enabled'] is True
    
    def test_shutdown(self):
        """Test manager shutdown."""
        manager = ExtensionManager()
        
        # Add extension with shutdown hook
        class ShutdownExtension(MockExtension):
            def hook_shutdown(self):
                self.shutdown_called = True
        
        ext = ShutdownExtension()
        manager.registry.register_loaded('shutdown', ext, 1.0)
        
        manager.shutdown()
        
        assert not manager._initialized
        assert ext.cleaned_up  # Registry cleanup was called
        assert manager.registry.get_all_metadata() == {}


class TestExtensionLogging:
    """Test extension logging configuration."""
    
    def test_setup_extension_logging(self):
        """Test basic logging setup."""
        from pyforge_cli.extensions.logging import setup_extension_logging, EXTENSION_LOGGER_NAME
        
        logger = setup_extension_logging()
        assert logger.name == EXTENSION_LOGGER_NAME
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_get_extension_logger(self):
        """Test getting component-specific loggers."""
        from pyforge_cli.extensions.logging import get_extension_logger
        
        base_logger = get_extension_logger()
        discovery_logger = get_extension_logger('discovery')
        
        assert base_logger.name == 'pyforge_cli.extensions'
        assert discovery_logger.name == 'pyforge_cli.extensions.discovery'
    
    def test_logger_adapter(self):
        """Test the logger adapter."""
        from pyforge_cli.extensions.logging import ExtensionLoggerAdapter, get_extension_logger
        
        base_logger = get_extension_logger()
        adapter = ExtensionLoggerAdapter(base_logger, 'test_extension')
        
        msg, kwargs = adapter.process("Test message", {})
        assert msg == "[test_extension] Test message"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])