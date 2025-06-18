"""Tests for output path generation behavior."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from click.testing import CliRunner

from cortexpy_cli.main import cli


class TestOutputPathGeneration:
    """Test cases for output path generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_output_path_same_directory(self):
        """Test that output file is created in same directory as input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file path
            input_file = temp_path / "test_document.pdf"
            expected_output = temp_path / "test_document.txt"
            
            # Mock the converter and file operations
            with patch('cortexpy_cli.main.registry') as mock_registry, \
                 patch('pathlib.Path.exists') as mock_exists, \
                 patch('cortexpy_cli.main.plugin_loader'):
                
                # Setup mocks
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                mock_exists.return_value = True  # Input file exists
                
                # Mock Path.exists for output file check
                def exists_side_effect(self):
                    return str(self) != str(expected_output)  # Output doesn't exist
                
                with patch.object(Path, 'exists', exists_side_effect):
                    result = self.runner.invoke(cli, [
                        'convert', str(input_file)
                    ])
                
                # Verify the converter was called with correct paths
                mock_converter.convert.assert_called_once()
                call_args = mock_converter.convert.call_args[0]
                
                assert call_args[0] == input_file  # Input path
                assert call_args[1] == expected_output  # Output path
    
    def test_output_path_subdirectory(self):
        """Test output path generation for files in subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create subdirectory structure
            subdir = temp_path / "documents" / "pdfs"
            input_file = subdir / "report.pdf"
            expected_output = subdir / "report.txt"
            
            with patch('cortexpy_cli.main.registry') as mock_registry, \
                 patch('pathlib.Path.exists') as mock_exists, \
                 patch('cortexpy_cli.main.plugin_loader'):
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                mock_exists.return_value = True
                
                def exists_side_effect(self):
                    return str(self) != str(expected_output)
                
                with patch.object(Path, 'exists', exists_side_effect):
                    result = self.runner.invoke(cli, [
                        'convert', str(input_file)
                    ])
                
                call_args = mock_converter.convert.call_args[0]
                assert call_args[1] == expected_output
                assert call_args[1].parent == input_file.parent
    
    def test_explicit_output_path_respected(self):
        """Test that explicit output path is used when provided."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "input.pdf"
            explicit_output = temp_path / "custom" / "output.txt"
            
            with patch('cortexpy_cli.main.registry') as mock_registry, \
                 patch('pathlib.Path.exists') as mock_exists, \
                 patch('cortexpy_cli.main.plugin_loader'):
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                mock_exists.return_value = True
                
                def exists_side_effect(self):
                    return str(self) != str(explicit_output)
                
                with patch.object(Path, 'exists', exists_side_effect):
                    result = self.runner.invoke(cli, [
                        'convert', str(input_file), str(explicit_output)
                    ])
                
                call_args = mock_converter.convert.call_args[0]
                assert call_args[1] == explicit_output
    
    def test_verbose_shows_auto_generated_path(self):
        """Test that verbose mode shows the auto-generated output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "verbose_test.pdf"
            expected_output = temp_path / "verbose_test.txt"
            
            with patch('cortexpy_cli.main.registry') as mock_registry, \
                 patch('pathlib.Path.exists') as mock_exists, \
                 patch('cortexpy_cli.main.plugin_loader'):
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                mock_exists.return_value = True
                
                def exists_side_effect(self):
                    return str(self) != str(expected_output)
                
                with patch.object(Path, 'exists', exists_side_effect):
                    result = self.runner.invoke(cli, [
                        '--verbose', 'convert', str(input_file)
                    ])
                
                # Check that verbose output mentions the auto-generated path
                assert "Auto-generated output file" in result.output
                assert str(expected_output) in result.output
    
    def test_output_format_extension_applied(self):
        """Test that the correct extension is applied based on output format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "document.pdf"
            expected_output = temp_path / "document.txt"  # Default format is txt
            
            with patch('cortexpy_cli.main.registry') as mock_registry, \
                 patch('pathlib.Path.exists') as mock_exists, \
                 patch('cortexpy_cli.main.plugin_loader'):
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                mock_exists.return_value = True
                
                def exists_side_effect(self):
                    return str(self) != str(expected_output)
                
                with patch.object(Path, 'exists', exists_side_effect):
                    result = self.runner.invoke(cli, [
                        'convert', str(input_file), '--format', 'txt'
                    ])
                
                call_args = mock_converter.convert.call_args[0]
                assert call_args[1] == expected_output
                assert call_args[1].suffix == '.txt'
    
    def test_complex_filename_handling(self):
        """Test output path generation with complex filenames."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test file with multiple dots and spaces
            input_file = temp_path / "my.document.with.dots.and spaces.pdf"
            expected_output = temp_path / "my.document.with.dots.and spaces.txt"
            
            with patch('cortexpy_cli.main.registry') as mock_registry, \
                 patch('pathlib.Path.exists') as mock_exists, \
                 patch('cortexpy_cli.main.plugin_loader'):
                
                mock_converter = Mock()
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                mock_exists.return_value = True
                
                def exists_side_effect(self):
                    return str(self) != str(expected_output)
                
                with patch.object(Path, 'exists', exists_side_effect):
                    result = self.runner.invoke(cli, [
                        'convert', str(input_file)
                    ])
                
                call_args = mock_converter.convert.call_args[0]
                assert call_args[1] == expected_output
                assert call_args[1].stem == "my.document.with.dots.and spaces"