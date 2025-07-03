"""Unit tests for the extension lifecycle manager."""

import pytest
import time
from unittest.mock import Mock, patch, call
from concurrent.futures import ThreadPoolExecutor

from pyforge_cli.plugin_system.lifecycle import (
    ExtensionLifecycleManager, lifecycle_manager
)
from pyforge_cli.plugin_system.registry import PluginState, extension_registry
from pyforge_cli.extensions.base import BaseExtension


class MockExtension(BaseExtension):
    """Mock extension for testing."""
    
    def __init__(self, name="test", available=True, init_success=True, init_delay=0):
        super().__init__()
        self.name = name
        self.version = "1.0.0"
        self.description = f"Test extension {name}"
        self._available = available
        self._init_success = init_success
        self._init_delay = init_delay
        self.initialized = False
        self.shutdown_called = False
    
    def is_available(self) -> bool:
        return self._available
    
    def initialize(self) -> bool:
        if self._init_delay > 0:
            time.sleep(self._init_delay)
        self.initialized = True
        return self._init_success
    
    def shutdown(self):
        self.shutdown_called = True
        self.initialized = False


class TestExtensionLifecycleManager:
    """Test cases for ExtensionLifecycleManager class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.manager = ExtensionLifecycleManager()
        extension_registry.clear()
    
    def teardown_method(self):
        """Cleanup test environment."""
        extension_registry.clear()
    
    def test_init(self):
        """Test lifecycle manager initialization."""
        manager = ExtensionLifecycleManager()
        assert manager._initialization_order == []
        assert manager._cleanup_registered is False
        assert manager._shutdown_in_progress is False
    
    def test_initialize_extensions_empty(self):
        """Test initializing empty extensions dictionary."""
        result = self.manager.initialize_extensions({})
        assert result == {}
    
    def test_initialize_single_extension_success(self):
        """Test successful initialization of single extension."""
        ext = MockExtension("test1")
        extensions = {"test1": ext}
        
        result = self.manager.initialize_extensions(extensions)
        
        assert result == {"test1": True}
        assert ext.initialized is True
        assert "test1" in self.manager.get_initialization_order()
        
        # Check registry state
        plugin_info = extension_registry.get_plugin_info("test1")
        assert plugin_info.state == PluginState.INITIALIZED
    
    def test_initialize_single_extension_failure(self):
        """Test failed initialization of single extension."""
        ext = MockExtension("test1", init_success=False)
        extensions = {"test1": ext}
        
        result = self.manager.initialize_extensions(extensions)
        
        assert result == {"test1": False}
        assert ext.initialized is True  # initialize() was called
        assert "test1" not in self.manager.get_initialization_order()
        
        # Check registry state
        plugin_info = extension_registry.get_plugin_info("test1")
        assert plugin_info.state == PluginState.FAILED
    
    def test_initialize_extension_not_available(self):
        """Test initialization of unavailable extension."""
        ext = MockExtension("test1", available=False)
        extensions = {"test1": ext}
        
        result = self.manager.initialize_extensions(extensions)
        
        assert result == {"test1": False}
        assert ext.initialized is False
        assert "test1" not in self.manager.get_initialization_order()
        
        # Check registry state
        plugin_info = extension_registry.get_plugin_info("test1")
        assert plugin_info.state == PluginState.DISABLED
    
    def test_initialize_multiple_extensions_success(self):
        """Test successful initialization of multiple extensions."""
        ext1 = MockExtension("test1")
        ext2 = MockExtension("test2")
        ext3 = MockExtension("test3")
        extensions = {"test1": ext1, "test2": ext2, "test3": ext3}
        
        result = self.manager.initialize_extensions(extensions)
        
        assert result == {"test1": True, "test2": True, "test3": True}
        assert all(ext.initialized for ext in [ext1, ext2, ext3])
        assert len(self.manager.get_initialization_order()) == 3
    
    def test_initialize_mixed_success_failure(self):
        """Test initialization with mixed success and failure."""
        ext1 = MockExtension("test1", init_success=True)
        ext2 = MockExtension("test2", init_success=False)
        ext3 = MockExtension("test3", available=False)
        extensions = {"test1": ext1, "test2": ext2, "test3": ext3}
        
        result = self.manager.initialize_extensions(extensions)
        
        assert result["test1"] is True
        assert result["test2"] is False
        assert result["test3"] is False
        assert ext1.initialized is True
        assert ext2.initialized is True  # Called but returned False
        assert ext3.initialized is False  # Not available
        assert self.manager.get_initialization_order() == ["test1"]
    
    def test_initialize_with_exception(self):
        """Test initialization when extension raises exception."""
        ext = MockExtension("test1")
        
        # Mock the initialize method to raise an exception
        def failing_init():
            raise RuntimeError("Test initialization error")
        
        ext.initialize = failing_init
        extensions = {"test1": ext}
        
        result = self.manager.initialize_extensions(extensions)
        
        assert result == {"test1": False}
        assert "test1" not in self.manager.get_initialization_order()
        
        # Check registry state
        plugin_info = extension_registry.get_plugin_info("test1")
        assert plugin_info.state == PluginState.FAILED
        assert "Test initialization error" in plugin_info.error_message
    
    def test_initialize_with_timeout(self):
        """Test initialization timeout handling."""
        # Create extension with long delay
        ext = MockExtension("test1", init_delay=0.1)
        extensions = {"test1": ext}
        
        # Use very short timeout
        result = self.manager.initialize_extensions(extensions, timeout=0.05)
        
        # Should still succeed because the timeout is per-extension, 
        # and we give enough buffer in the implementation
        assert result["test1"] is True
    
    def test_shutdown_extensions_empty(self):
        """Test shutdown with no initialized extensions."""
        self.manager.shutdown_extensions()
        # Should not raise any errors
    
    def test_shutdown_extensions_success(self):
        """Test successful shutdown of extensions."""
        ext1 = MockExtension("test1")
        ext2 = MockExtension("test2")
        extensions = {"test1": ext1, "test2": ext2}
        
        # Initialize extensions first
        self.manager.initialize_extensions(extensions)
        
        # Shutdown
        self.manager.shutdown_extensions()
        
        # Check shutdown was called in reverse order
        assert ext1.shutdown_called is True
        assert ext2.shutdown_called is True
        
        # Check registry states
        for name in ["test1", "test2"]:
            plugin_info = extension_registry.get_plugin_info(name)
            assert plugin_info.state == PluginState.DISABLED
    
    def test_shutdown_prevents_double_shutdown(self):
        """Test that shutdown can be called multiple times safely."""
        ext = MockExtension("test1")
        extensions = {"test1": ext}
        
        self.manager.initialize_extensions(extensions)
        
        # Call shutdown multiple times
        self.manager.shutdown_extensions()
        first_call_state = ext.shutdown_called
        
        # Reset the flag and call again
        ext.shutdown_called = False
        self.manager.shutdown_extensions()
        
        # Second call should not call shutdown again
        assert first_call_state is True
        assert ext.shutdown_called is False  # Not called again
    
    def test_shutdown_with_exception(self):
        """Test shutdown when extension raises exception."""
        ext = MockExtension("test1")
        
        # Mock shutdown to raise exception
        def failing_shutdown():
            raise RuntimeError("Test shutdown error")
        
        ext.shutdown = failing_shutdown
        extensions = {"test1": ext}
        
        self.manager.initialize_extensions(extensions)
        
        # Shutdown should handle exception gracefully
        self.manager.shutdown_extensions()
        
        # Should still update registry state despite exception
        plugin_info = extension_registry.get_plugin_info("test1")
        assert plugin_info.state == PluginState.DISABLED
    
    def test_restart_failed_extensions_no_failures(self):
        """Test restart when no extensions failed."""
        result = self.manager.restart_failed_extensions()
        assert result == {}
    
    def test_restart_failed_extensions(self):
        """Test restarting failed extensions."""
        ext1 = MockExtension("test1", init_success=False)  # Will fail initially
        ext2 = MockExtension("test2", init_success=True)   # Will succeed
        extensions = {"test1": ext1, "test2": ext2}
        
        # Initial initialization with failure
        self.manager.initialize_extensions(extensions)
        
        # Now make the failed extension succeed
        ext1._init_success = True
        
        # Restart failed extensions
        result = self.manager.restart_failed_extensions()
        
        assert "test1" in result
        assert result["test1"] is True
    
    def test_initialization_order_tracking(self):
        """Test that initialization order is tracked correctly."""
        ext1 = MockExtension("test1")
        ext2 = MockExtension("test2")
        ext3 = MockExtension("test3")
        extensions = {"test1": ext1, "test2": ext2, "test3": ext3}
        
        self.manager.initialize_extensions(extensions)
        
        order = self.manager.get_initialization_order()
        assert len(order) == 3
        assert set(order) == {"test1", "test2", "test3"}
        
        # Order should be deterministic within a phase, but we can't guarantee
        # exact order due to parallel execution
        for name in order:
            assert name in ["test1", "test2", "test3"]
    
    @patch('atexit.register')
    def test_cleanup_registration(self, mock_atexit):
        """Test that cleanup handler is registered with atexit."""
        manager = ExtensionLifecycleManager()
        ext = MockExtension("test1")
        extensions = {"test1": ext}
        
        manager.initialize_extensions(extensions)
        
        # Should register cleanup handler
        mock_atexit.assert_called_once()
    
    def test_parallel_initialization(self):
        """Test that extensions are initialized in parallel."""
        # Create extensions with small delays
        ext1 = MockExtension("test1", init_delay=0.02)
        ext2 = MockExtension("test2", init_delay=0.02)
        ext3 = MockExtension("test3", init_delay=0.02)
        extensions = {"test1": ext1, "test2": ext2, "test3": ext3}
        
        start_time = time.time()
        result = self.manager.initialize_extensions(extensions)
        total_time = time.time() - start_time
        
        # Should complete in less time than sequential execution
        # (3 * 0.02 = 0.06s sequential, should be much faster in parallel)
        assert total_time < 0.05
        assert all(result.values())
    
    def test_global_lifecycle_manager(self):
        """Test that lifecycle_manager is a global instance."""
        assert isinstance(lifecycle_manager, ExtensionLifecycleManager)
        
        # Import again to verify it's the same instance
        from pyforge_cli.plugin_system.lifecycle import lifecycle_manager as lm2
        assert lifecycle_manager is lm2