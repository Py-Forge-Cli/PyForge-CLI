"""Integration tests for PyForge CLI extension system with Databricks extension."""

import pytest
import tempfile
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, Mock
import json
import sys

from pyforge_cli.main import cli
from pyforge_cli.extensions import get_extension_manager
from pyforge_cli.extensions.databricks import DatabricksExtension


class TestExtensionIntegration:
    """Integration tests for the extension system."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_list_extensions_command(self, runner):
        """Test the list-extensions command."""
        # Mock entry points to return Databricks extension
        mock_ep = Mock()
        mock_ep.name = 'databricks'
        mock_ep.value = 'pyforge_cli.extensions.databricks:DatabricksExtension'
        
        if sys.version_info >= (3, 10):
            mock_entry_points = [mock_ep]
        else:
            mock_entry_points = {'pyforge_cli.extensions': [mock_ep]}
        
        with patch('pyforge_cli.extensions.discovery.entry_points', return_value=mock_entry_points):
            # Mock the extension to be available
            with patch.object(DatabricksExtension, 'is_available', return_value=True):
                result = runner.invoke(cli, ['list-extensions'])
                
                assert result.exit_code == 0
                assert 'databricks' in result.output
                assert 'Loaded' in result.output or 'Failed' in result.output
    
    def test_extension_hooks_in_convert(self, runner, temp_dir):
        """Test that extension hooks are called during conversion."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        # Track hook calls
        hook_calls = {'pre': False, 'post': False}
        
        class TestExtension(DatabricksExtension):
            def hook_pre_conversion(self, **kwargs):
                hook_calls['pre'] = True
                return {'status': 'pre-hook-executed'}
            
            def hook_post_conversion(self, **kwargs):
                hook_calls['post'] = True
                return {'status': 'post-hook-executed'}
        
        # Mock the extension manager to use our test extension
        manager = get_extension_manager()
        test_ext = TestExtension()
        test_ext.initialize()
        
        with patch.object(manager, 'get_all_extensions', return_value=[test_ext]):
            # We need a converter for .txt files
            with patch('pyforge_cli.plugins.registry.get_converter') as mock_get_converter:
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, ['convert', str(test_file), '--format', 'txt'])
                
                # Verify hooks were called
                assert hook_calls['pre']
                assert hook_calls['post']
    
    def test_extension_lifecycle(self):
        """Test the complete extension lifecycle."""
        from pyforge_cli.extensions.manager import ExtensionManager
        from pyforge_cli.extensions.databricks import DatabricksExtension
        
        manager = ExtensionManager()
        
        # Mock discovery to find Databricks extension
        with patch.object(manager.discovery, 'discover_extensions', 
                         return_value={'databricks': 'pyforge_cli.extensions.databricks:DatabricksExtension'}):
            with patch.object(manager.discovery, 'load_extension_class', return_value=DatabricksExtension):
                with patch.object(DatabricksExtension, 'is_available', return_value=True):
                    # Initialize
                    manager.initialize()
                    
                    # Check extension is loaded
                    extensions = manager.get_all_extensions()
                    assert len(extensions) > 0
                    assert any(isinstance(ext, DatabricksExtension) for ext in extensions)
                    
                    # Get extension info
                    info = manager.get_extension_info()
                    assert 'databricks' in info
                    assert info['databricks']['state'] == 'loaded'
                    
                    # Test disabling
                    success = manager.disable_extension('databricks')
                    assert success
                    
                    # Test re-enabling
                    success = manager.enable_extension('databricks')
                    assert success
                    
                    # Shutdown
                    manager.shutdown()
                    assert not manager._initialized
    
    def test_databricks_extension_commands(self, runner):
        """Test that Databricks extension adds its commands."""
        # The Databricks extension doesn't add CLI commands in the current implementation,
        # but we can test that it loads successfully
        with patch.object(DatabricksExtension, 'is_available', return_value=True):
            result = runner.invoke(cli, ['--help'])
            assert result.exit_code == 0
            # The main help should still work with extensions loaded
            assert 'PyForge CLI' in result.output
    
    def test_extension_error_handling(self):
        """Test error handling in extension system."""
        from pyforge_cli.extensions.manager import ExtensionManager
        
        manager = ExtensionManager()
        
        # Create a failing extension
        class FailingExtension:
            @classmethod
            def is_available(cls):
                return True
            
            def __init__(self):
                raise Exception("Constructor failed")
        
        # Mock discovery to find the failing extension
        with patch.object(manager.discovery, 'discover_extensions', 
                         return_value={'failing': 'test:FailingExtension'}):
            with patch.object(manager.discovery, 'load_extension_class', return_value=FailingExtension):
                # Initialize should not crash
                manager.initialize()
                
                # Check that the extension is marked as failed
                info = manager.get_extension_info()
                assert 'failing' in info
                assert info['failing']['state'] == 'failed'
                assert info['failing']['error'] is not None
    
    def test_verbose_logging(self, runner, temp_dir):
        """Test that verbose mode enables extension logging."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        with patch('pyforge_cli.plugins.registry.get_converter') as mock_get_converter:
            mock_converter = Mock()
            mock_converter.convert.return_value = True
            mock_get_converter.return_value = mock_converter
            
            # Run with verbose flag
            result = runner.invoke(cli, ['--verbose', 'convert', str(test_file)])
            
            # In verbose mode, we should see extension-related output if any extensions are loaded
            # The exact output depends on what extensions are discovered
            assert result.exit_code == 0
    
    def test_extension_hooks_error_recovery(self, runner, temp_dir):
        """Test that conversion continues even if extension hooks fail."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        class FailingHookExtension(DatabricksExtension):
            def hook_pre_conversion(self, **kwargs):
                raise Exception("Pre-hook failed")
            
            def hook_post_conversion(self, **kwargs):
                raise Exception("Post-hook failed")
        
        # Mock the extension manager
        manager = get_extension_manager()
        failing_ext = FailingHookExtension()
        failing_ext.initialize()
        
        with patch.object(manager, 'get_all_extensions', return_value=[failing_ext]):
            with patch('pyforge_cli.plugins.registry.get_converter') as mock_get_converter:
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_get_converter.return_value = mock_converter
                
                # Conversion should still succeed despite hook failures
                result = runner.invoke(cli, ['convert', str(test_file), '--format', 'txt'])
                
                # The conversion should succeed
                assert mock_converter.convert.called
    
    def test_multiple_extensions(self):
        """Test loading multiple extensions simultaneously."""
        from pyforge_cli.extensions.manager import ExtensionManager
        from pyforge_cli.extensions.base import BaseExtension
        
        # Create two test extensions
        class Extension1(BaseExtension):
            @classmethod
            def is_available(cls):
                return True
            
            def initialize(self):
                return True
        
        class Extension2(BaseExtension):
            @classmethod
            def is_available(cls):
                return True
            
            def initialize(self):
                return True
        
        manager = ExtensionManager()
        
        # Mock discovery to find both extensions
        with patch.object(manager.discovery, 'discover_extensions', 
                         return_value={'ext1': 'test:Extension1', 'ext2': 'test:Extension2'}):
            with patch.object(manager.discovery, 'load_extension_class') as mock_load:
                # Return different classes for different calls
                mock_load.side_effect = [Extension1, Extension2]
                
                manager.initialize()
                
                # Both should be loaded
                extensions = manager.get_all_extensions()
                assert len(extensions) == 2
                
                info = manager.get_extension_info()
                assert 'ext1' in info
                assert 'ext2' in info
                assert info['ext1']['state'] == 'loaded'
                assert info['ext2']['state'] == 'loaded'


class TestDatabricksExtensionIntegration:
    """Integration tests specific to the Databricks extension."""
    
    def test_databricks_extension_initialization(self):
        """Test that Databricks extension initializes correctly."""
        ext = DatabricksExtension()
        
        # In non-Databricks environment, it should still initialize
        success = ext.initialize()
        assert success
        
        # Check version
        assert hasattr(ext, '__version__')
        assert ext.__version__ is not None
    
    def test_databricks_extension_in_registry(self):
        """Test that Databricks extension can be registered and retrieved."""
        from pyforge_cli.extensions.registry import ExtensionRegistry
        
        registry = ExtensionRegistry()
        ext = DatabricksExtension()
        ext.initialize()
        
        registry.register_loaded('databricks', ext, 1.0)
        
        # Retrieve it
        retrieved = registry.get_extension('databricks')
        assert retrieved == ext
        assert registry.is_enabled('databricks')
    
    def test_databricks_extension_hooks(self):
        """Test Databricks extension hook methods."""
        ext = DatabricksExtension()
        ext.initialize()
        
        # Test pre-conversion hook
        result = ext.hook_pre_conversion(
            input_file=Path("test.csv"),
            output_file=Path("test.parquet"),
            converter=None,
            options={}
        )
        # In non-Databricks environment, hooks should return early
        assert result is not None
        
        # Test post-conversion hook
        result = ext.hook_post_conversion(
            input_file=Path("test.csv"),
            output_file=Path("test.parquet"),
            converter=None,
            options={},
            success=True
        )
        assert result is not None
    
    def test_databricks_extension_enhance_convert_command(self):
        """Test that Databricks extension can enhance the convert command."""
        ext = DatabricksExtension()
        ext.initialize()
        
        # The enhance_convert_command should return None (no CLI enhancements currently)
        result = ext.enhance_convert_command()
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])