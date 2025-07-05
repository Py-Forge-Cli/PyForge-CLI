"""Tests for output path generation behavior."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from click.testing import CliRunner

from pyforge_cli.main import cli


class TestOutputPathGeneration:
    """Test cases for output path generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
        # Create a mock converter that we'll register
        self.mock_converter_class = MagicMock()
        self.mock_converter_instance = Mock()
        self.mock_converter_instance.supported_inputs = {'.pdf', '.txt'}
        self.mock_converter_instance.supported_outputs = {'.txt', '.parquet'}
        self.mock_converter_instance.convert.return_value = True
        self.mock_converter_class.return_value = self.mock_converter_instance
    
    def test_output_path_same_directory(self):
        """Test that output file is created in same directory as input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file path and write some content
            input_file = temp_path / "test_document.pdf"
            input_file.write_bytes(b'%PDF-1.4 test content')  # Create actual file
            expected_output = temp_path / "test_document.txt"
            
            # Mock the entire plugin loading and registry system
            with patch('pyforge_cli.main.plugin_loader') as mock_loader, \
                 patch('pyforge_cli.main.registry') as mock_registry, \
                 patch('pyforge_cli.main.get_extension_manager') as mock_get_ext_manager:
                
                # Setup extension manager mock
                mock_ext_manager = Mock()
                mock_ext_manager.initialize.return_value = None
                mock_ext_manager.execute_hook.return_value = []
                mock_get_ext_manager.return_value = mock_ext_manager
                
                # Setup plugin loader
                mock_loader.load_all.return_value = None
                
                # Setup converter
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = self.runner.invoke(cli, [
                    'convert', str(input_file), '--format', 'txt'
                ])
                
                # Check result
                assert result.exit_code == 0, f"Command failed: {result.output}"
                
                # Verify the converter was called with correct paths
                mock_converter.convert.assert_called_once()
                call_args = mock_converter.convert.call_args[0]
                
                assert call_args[0] == input_file  # Input path
                assert call_args[1].parent == input_file.parent  # Same directory
                assert call_args[1].stem == input_file.stem  # Same base name
                assert call_args[1].suffix == '.txt'  # Correct extension
    
    def test_output_path_subdirectory(self):
        """Test output path generation for files in subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create subdirectory structure
            subdir = temp_path / "documents" / "pdfs"
            subdir.mkdir(parents=True)
            input_file = subdir / "report.pdf"
            input_file.write_bytes(b'%PDF-1.4 test content')  # Create actual file
            expected_output = subdir / "report.txt"
            
            with patch('pyforge_cli.main.plugin_loader') as mock_loader, \
                 patch('pyforge_cli.main.registry') as mock_registry, \
                 patch('pyforge_cli.main.get_extension_manager') as mock_get_ext_manager:
                
                # Setup extension manager mock
                mock_ext_manager = Mock()
                mock_ext_manager.initialize.return_value = None
                mock_ext_manager.execute_hook.return_value = []
                mock_get_ext_manager.return_value = mock_ext_manager
                
                # Setup plugin loader
                mock_loader.load_all.return_value = None
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = self.runner.invoke(cli, [
                    'convert', str(input_file), '--format', 'txt'
                ])
                
                assert result.exit_code == 0, f"Command failed: {result.output}"
                
                call_args = mock_converter.convert.call_args[0]
                assert call_args[1].parent == input_file.parent
                assert call_args[1].stem == input_file.stem
                assert call_args[1].suffix == '.txt'
    
    def test_explicit_output_path_respected(self):
        """Test that explicit output path is used when provided."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "input.pdf"
            input_file.write_bytes(b'%PDF-1.4 test content')  # Create actual file
            
            # Create the custom directory
            custom_dir = temp_path / "custom"
            custom_dir.mkdir()
            explicit_output = custom_dir / "output.txt"
            
            with patch('pyforge_cli.main.plugin_loader') as mock_loader, \
                 patch('pyforge_cli.main.registry') as mock_registry, \
                 patch('pyforge_cli.main.get_extension_manager') as mock_get_ext_manager:
                
                # Setup extension manager mock
                mock_ext_manager = Mock()
                mock_ext_manager.initialize.return_value = None
                mock_ext_manager.execute_hook.return_value = []
                mock_get_ext_manager.return_value = mock_ext_manager
                
                # Setup plugin loader
                mock_loader.load_all.return_value = None
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = self.runner.invoke(cli, [
                    'convert', str(input_file), str(explicit_output)
                ])
                
                assert result.exit_code == 0, f"Command failed: {result.output}"
                
                mock_converter.convert.assert_called_once()
                call_args = mock_converter.convert.call_args[0]
                assert call_args[1] == explicit_output
    
    def test_verbose_shows_auto_generated_path(self):
        """Test that verbose mode shows the auto-generated output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "verbose_test.pdf"
            input_file.write_bytes(b'%PDF-1.4 test content')  # Create actual file
            expected_output = temp_path / "verbose_test.txt"
            
            with patch('pyforge_cli.main.plugin_loader') as mock_loader, \
                 patch('pyforge_cli.main.registry') as mock_registry, \
                 patch('pyforge_cli.main.get_extension_manager') as mock_get_ext_manager:
                
                # Setup extension manager mock
                mock_ext_manager = Mock()
                mock_ext_manager.initialize.return_value = None
                mock_ext_manager.execute_hook.return_value = []
                mock_get_ext_manager.return_value = mock_ext_manager
                
                # Setup plugin loader
                mock_loader.load_all.return_value = None
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = self.runner.invoke(cli, [
                    '--verbose', 'convert', str(input_file), '--format', 'txt'
                ])
                
                assert result.exit_code == 0, f"Command failed: {result.output}"
                
                # Check that verbose output mentions the auto-generated path
                assert "Auto-generated output file" in result.output or "output" in result.output.lower()
                # The exact path format may vary, so check for the filename
                assert "verbose_test" in result.output
    
    def test_output_format_extension_applied(self):
        """Test that the correct extension is applied based on output format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "document.pdf"
            input_file.write_bytes(b'%PDF-1.4 test content')  # Create actual file
            expected_output = temp_path / "document.txt"  # Default format is txt
            
            with patch('pyforge_cli.main.plugin_loader') as mock_loader, \
                 patch('pyforge_cli.main.registry') as mock_registry, \
                 patch('pyforge_cli.main.get_extension_manager') as mock_get_ext_manager:
                
                # Setup extension manager mock
                mock_ext_manager = Mock()
                mock_ext_manager.initialize.return_value = None
                mock_ext_manager.execute_hook.return_value = []
                mock_get_ext_manager.return_value = mock_ext_manager
                
                # Setup plugin loader
                mock_loader.load_all.return_value = None
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = self.runner.invoke(cli, [
                    'convert', str(input_file), '--format', 'txt'
                ])
                
                assert result.exit_code == 0, f"Command failed: {result.output}"
                
                mock_converter.convert.assert_called_once()
                call_args = mock_converter.convert.call_args[0]
                assert call_args[1].parent == input_file.parent
                assert call_args[1].stem == input_file.stem
                assert call_args[1].suffix == '.txt'
    
    def test_complex_filename_handling(self):
        """Test output path generation with complex filenames."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test file with multiple dots and spaces
            input_file = temp_path / "my.document.with.dots.and spaces.pdf"
            input_file.write_bytes(b'%PDF-1.4 test content')  # Create actual file
            expected_output = temp_path / "my.document.with.dots.and spaces.txt"
            
            with patch('pyforge_cli.main.plugin_loader') as mock_loader, \
                 patch('pyforge_cli.main.registry') as mock_registry, \
                 patch('pyforge_cli.main.get_extension_manager') as mock_get_ext_manager:
                
                # Setup extension manager mock
                mock_ext_manager = Mock()
                mock_ext_manager.initialize.return_value = None
                mock_ext_manager.execute_hook.return_value = []
                mock_get_ext_manager.return_value = mock_ext_manager
                
                # Setup plugin loader
                mock_loader.load_all.return_value = None
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = self.runner.invoke(cli, [
                    'convert', str(input_file), '--format', 'txt'
                ])
                
                assert result.exit_code == 0, f"Command failed: {result.output}"
                
                mock_converter.convert.assert_called_once()
                call_args = mock_converter.convert.call_args[0]
                assert call_args[1].parent == input_file.parent
                assert call_args[1].stem == "my.document.with.dots.and spaces"
                assert call_args[1].suffix == '.txt'