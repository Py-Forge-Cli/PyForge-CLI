"""Unit tests for the extension hooks system."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from pyforge_cli.plugin_system.hooks import (
    ExtensionHooksManager, hooks_manager, HookType, HookResult
)
from pyforge_cli.plugin_system.registry import extension_registry, PluginState
from pyforge_cli.extensions.base import BaseExtension


class MockExtensionWithHooks(BaseExtension):
    """Mock extension with hook implementations for testing."""
    
    def __init__(self, name="test"):
        super().__init__()
        self.name = name
        self.version = "1.0.0"
        self.description = f"Test extension {name}"
        self.hook_calls = []
    
    def is_available(self) -> bool:
        return True
    
    def initialize(self) -> bool:
        return True
    
    def hook_pre_conversion(self, data):
        self.hook_calls.append(('pre_conversion', data))
        # Modify options to test parameter passing
        if 'options' in data:
            data['options']['test_pre_hook'] = True
        return data
    
    def hook_post_conversion(self, data):
        self.hook_calls.append(('post_conversion', data))
        return data
    
    def hook_parameter_enhancement(self, data):
        self.hook_calls.append(('parameter_enhancement', data))
        if 'options' in data:
            data['options']['enhanced'] = True
        return data
    
    def hook_error_handling(self, data):
        self.hook_calls.append(('error_handling', data))
        # Simulate error recovery
        return {'handled': True, 'recovery_success': True}
    
    def hook_converter_selection(self, data):
        self.hook_calls.append(('converter_selection', data))
        return {'selected_converter': 'enhanced_converter'}


class FailingMockExtension(BaseExtension):
    """Mock extension that fails in hooks."""
    
    def __init__(self):
        super().__init__()
        self.name = "failing"
        self.version = "1.0.0"
        self.description = "Failing test extension"
    
    def is_available(self) -> bool:
        return True
    
    def initialize(self) -> bool:
        return True
    
    def hook_pre_conversion(self, data):
        raise RuntimeError("Hook failed")
    
    def hook_post_conversion(self, data):
        return HookResult(success=False, message="Post hook failed", stop_processing=True)


class TestHookResult:
    """Test cases for HookResult class."""
    
    def test_default_init(self):
        """Test default HookResult initialization."""
        result = HookResult()
        assert result.success is True
        assert result.data is None
        assert result.message == ""
        assert result.stop_processing is False
    
    def test_custom_init(self):
        """Test custom HookResult initialization."""
        data = {'test': 'value'}
        result = HookResult(
            success=False,
            data=data,
            message="Test message",
            stop_processing=True
        )
        assert result.success is False
        assert result.data == data
        assert result.message == "Test message"
        assert result.stop_processing is True


class TestExtensionHooksManager:
    """Test cases for ExtensionHooksManager class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.manager = ExtensionHooksManager()
        extension_registry.clear()
    
    def teardown_method(self):
        """Cleanup test environment."""
        extension_registry.clear()
    
    def test_init(self):
        """Test hooks manager initialization."""
        manager = ExtensionHooksManager()
        assert manager._hook_cache == {}
        assert manager._last_cache_update == 0
    
    def test_no_hooks_registered(self):
        """Test behavior when no hooks are registered."""
        input_file = Path("test.txt")
        output_file = Path("output.txt")
        options = {"test": True}
        
        result = self.manager.execute_pre_conversion_hooks(input_file, output_file, options)
        
        assert result.success is True
        # When no hooks are registered, the original data is returned unchanged
        assert result.data == options
    
    def test_pre_conversion_hooks(self):
        """Test pre-conversion hooks execution."""
        # Register mock extension
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        
        input_file = Path("test.txt")
        output_file = Path("output.txt")
        options = {"existing": True}
        
        result = self.manager.execute_pre_conversion_hooks(input_file, output_file, options)
        
        assert result.success is True
        assert 'test_pre_hook' in result.data
        assert result.data['test_pre_hook'] is True
        assert ext.hook_calls[0][0] == 'pre_conversion'
    
    def test_post_conversion_hooks(self):
        """Test post-conversion hooks execution."""
        # Register mock extension
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        
        input_file = Path("test.txt")
        output_file = Path("output.txt")
        metadata = {"pages": 5}
        
        result = self.manager.execute_post_conversion_hooks(
            input_file, output_file, True, metadata
        )
        
        assert result.success is True
        assert ext.hook_calls[0][0] == 'post_conversion'
        hook_data = ext.hook_calls[0][1]
        assert hook_data['conversion_result'] is True
        assert hook_data['metadata'] == metadata
    
    def test_parameter_enhancement_hooks(self):
        """Test parameter enhancement hooks execution."""
        # Register mock extension
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        
        input_file = Path("test.txt")
        options = {"original": True}
        
        result = self.manager.execute_parameter_enhancement_hooks(input_file, options)
        
        assert result.success is True
        assert 'enhanced' in result.data
        assert result.data['enhanced'] is True
        assert ext.hook_calls[0][0] == 'parameter_enhancement'
    
    def test_error_handling_hooks(self):
        """Test error handling hooks execution."""
        # Register mock extension
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        
        input_file = Path("test.txt")
        output_file = Path("output.txt")
        error = RuntimeError("Test error")
        context = {"test": "context"}
        
        result = self.manager.execute_error_handling_hooks(
            input_file, output_file, error, context
        )
        
        assert result.success is True
        assert result.data['handled'] is True
        assert result.data['recovery_success'] is True
        assert ext.hook_calls[0][0] == 'error_handling'
    
    def test_converter_selection_hooks(self):
        """Test converter selection hooks execution."""
        # Register mock extension
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        
        input_file = Path("test.txt")
        available_converters = ["pdf", "excel", "xml"]
        
        result = self.manager.execute_converter_selection_hooks(input_file, available_converters)
        
        assert result.success is True
        assert result.data == 'enhanced_converter'
        assert ext.hook_calls[0][0] == 'converter_selection'
    
    def test_multiple_extensions_hooks(self):
        """Test hooks execution with multiple extensions."""
        # Register multiple mock extensions
        ext1 = MockExtensionWithHooks("test1")
        ext2 = MockExtensionWithHooks("test2")
        
        extension_registry.register_extension("test1", ext1)
        extension_registry.register_extension("test2", ext2)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        extension_registry.update_state("test2", PluginState.INITIALIZED)
        
        input_file = Path("test.txt")
        options = {}
        
        result = self.manager.execute_parameter_enhancement_hooks(input_file, options)
        
        assert result.success is True
        assert 'enhanced' in result.data
        
        # Both extensions should have been called
        assert len(ext1.hook_calls) == 1
        assert len(ext2.hook_calls) == 1
    
    def test_hook_failure_handling(self):
        """Test handling of failed hooks."""
        # Register failing extension
        ext = FailingMockExtension()
        extension_registry.register_extension("failing", ext)
        extension_registry.update_state("failing", PluginState.INITIALIZED)
        
        input_file = Path("test.txt")
        output_file = Path("output.txt")
        options = {}
        
        result = self.manager.execute_pre_conversion_hooks(input_file, output_file, options)
        
        # Should still succeed but log the error
        assert result.success is True
        assert "Error" in result.message
    
    def test_hook_result_stop_processing(self):
        """Test stop_processing flag in hook results."""
        # Register failing extension that returns stop_processing=True
        ext = FailingMockExtension()
        extension_registry.register_extension("failing", ext)
        extension_registry.update_state("failing", PluginState.INITIALIZED)
        
        input_file = Path("test.txt")
        output_file = Path("output.txt")
        
        result = self.manager.execute_post_conversion_hooks(
            input_file, output_file, True, {}
        )
        
        # Should fail due to stop_processing=True
        assert result.success is False
        assert "Post hook failed" in result.message
    
    def test_hook_cache_refresh(self):
        """Test that hook cache is refreshed when extensions change."""
        # Initially no hooks
        stats = self.manager.get_hook_statistics()
        assert stats['total'] == 0
        
        # Register extension
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        
        # Cache should refresh and find hooks
        stats = self.manager.get_hook_statistics()
        assert stats['total'] > 0
        assert stats['pre_conversion'] == 1
        assert stats['post_conversion'] == 1
    
    def test_hook_statistics(self):
        """Test hook statistics generation."""
        # Register extension with hooks
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        
        stats = self.manager.get_hook_statistics()
        
        assert 'pre_conversion' in stats
        assert 'post_conversion' in stats
        assert 'parameter_enhancement' in stats
        assert 'error_handling' in stats
        assert 'converter_selection' in stats
        assert 'total' in stats
        assert stats['total'] == 5  # All hook types implemented
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Register extension
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.INITIALIZED)
        
        # Trigger cache population
        self.manager.get_hook_statistics()
        assert len(self.manager._hook_cache) > 0
        
        # Clear cache
        self.manager.clear_cache()
        assert len(self.manager._hook_cache) == 0
        assert self.manager._last_cache_update == 0
    
    def test_disabled_extension_hooks_not_called(self):
        """Test that hooks from disabled extensions are not called."""
        # Register extension but keep it disabled
        ext = MockExtensionWithHooks("test1")
        extension_registry.register_extension("test1", ext)
        extension_registry.update_state("test1", PluginState.LOADED)  # Not INITIALIZED
        
        input_file = Path("test.txt")
        options = {}
        
        result = self.manager.execute_parameter_enhancement_hooks(input_file, options)
        
        # Hook should not be called
        assert len(ext.hook_calls) == 0
        assert result.success is True
    
    def test_global_hooks_manager(self):
        """Test that hooks_manager is a global instance."""
        assert isinstance(hooks_manager, ExtensionHooksManager)
        
        # Import again to verify it's the same instance
        from pyforge_cli.plugin_system.hooks import hooks_manager as hm2
        assert hooks_manager is hm2