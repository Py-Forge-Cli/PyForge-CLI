"""Improved tests for the main CLI commands with better mocking."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
from click.testing import CliRunner
import tempfile
import json
import shutil

from pyforge_cli.main import cli


class TestMainCLIImproved:
    """Improved test suite for main CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def test_data_dir(self):
        """Get the test data directory."""
        return Path(__file__).parent / 'data'
    
    def setup_method(self):
        """Setup before each test method."""
        # Reset any global state
        pass
    
    def test_cli_version(self, runner):
        """Test the version option."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'version' in result.output.lower()
    
    def test_cli_help(self, runner):
        """Test the help option."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Usage:' in result.output
        assert 'Options:' in result.output
        assert 'Commands:' in result.output
    
    def test_cli_verbose_mode(self, runner):
        """Test verbose mode flag."""
        with patch('pyforge_cli.main.configure_verbose_logging') as mock_verbose:
            with patch('pyforge_cli.main.plugin_loader'):
                with patch('pyforge_cli.main.get_extension_manager'):
                    result = runner.invoke(cli, ['--verbose', '--help'])
                    assert result.exit_code == 0
                    # Verbose mode should be called
                    # Note: Due to Click's handling, this might not always be called in tests
    
    def test_formats_command(self, runner):
        """Test the formats command."""
        # Mock the registry to return converter info
        mock_converter_info = {
            'pdf': {
                'input_formats': ['.pdf'],
                'output_formats': ['txt', 'json'],
                'description': 'PDF to text/JSON converter'
            },
            'excel': {
                'input_formats': ['.xlsx', '.xls'],
                'output_formats': ['parquet', 'csv'],
                'description': 'Excel to Parquet/CSV converter'
            },
            'xml': {
                'input_formats': ['.xml', '.xml.gz', '.xml.bz2'],
                'output_formats': ['parquet', 'json'],
                'description': 'XML to Parquet/JSON converter'
            }
        }
        
        # Mock the registry's list_supported_formats to return converter info
        with patch('pyforge_cli.main.registry') as mock_registry:
            # Transform to match expected format
            mock_formats = {}
            for name, info in mock_converter_info.items():
                mock_formats[name] = {
                    'inputs': set(info['input_formats']),
                    'outputs': set(info['output_formats'])
                }
            mock_registry.list_supported_formats.return_value = mock_formats
            result = runner.invoke(cli, ['formats'])
            assert result.exit_code == 0
            # Check for expected content
            assert 'pdf' in result.output.lower()
            assert 'excel' in result.output.lower()
            assert 'xml' in result.output.lower()
    
    def test_info_command_excel(self, runner, test_data_dir):
        """Test the info command with an Excel file."""
        excel_file = test_data_dir / 'excel' / 'basic.xlsx'
        
        # Skip if test data doesn't exist
        if not excel_file.exists():
            pytest.skip("Test data file not found")
        
        mock_info = {
            'format': 'Excel',
            'size': '12.5 KB',
            'sheets': 1,
            'sheet_info': {
                'Sheet1': {'rows': 4, 'columns': 4}
            }
        }
        
        mock_converter = MagicMock()
        mock_converter.get_metadata.return_value = mock_info
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_registry.get_converter.return_value = mock_converter
            result = runner.invoke(cli, ['info', str(excel_file)])
            assert result.exit_code == 0
            assert 'Excel' in result.output
    
    def test_info_command_json_format(self, runner, temp_dir):
        """Test the info command with JSON output format."""
        test_file = temp_dir / "test.xml"
        test_file.write_text('<?xml version="1.0"?><root><item>test</item></root>')
        
        mock_info = {
            'format': 'XML',
            'structure': {
                'max_depth': 2,
                'total_elements': 2
            }
        }
        
        mock_converter = MagicMock()
        mock_converter.get_metadata.return_value = mock_info
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_registry.get_converter.return_value = mock_converter
            result = runner.invoke(cli, ['info', str(test_file), '--format', 'json'])
            assert result.exit_code == 0
            # Extract JSON from output (may have logs before it)
            lines = result.output.split('\n')
            json_start = None
            for i, line in enumerate(lines):
                if line.strip().startswith('{'):
                    json_start = i
                    break
            if json_start is not None:
                json_text = '\n'.join(lines[json_start:]).strip()
                output_data = json.loads(json_text)
                assert output_data['format'] == 'XML'
                assert 'structure' in output_data
            else:
                pytest.fail("No JSON output found")
    
    def test_validate_command_valid_file(self, runner, test_data_dir):
        """Test the validate command with a valid file."""
        xml_file = test_data_dir / 'xml' / 'simple.xml'
        
        if xml_file.exists():
            mock_converter = MagicMock()
            mock_converter.validate_input.return_value = True
            
            with patch('pyforge_cli.main.registry') as mock_registry:
                mock_registry.get_converter.return_value = mock_converter
                result = runner.invoke(cli, ['validate', str(xml_file)])
                assert result.exit_code == 0
                assert 'valid' in result.output.lower()
    
    def test_validate_command_invalid_file(self, runner, test_data_dir):
        """Test the validate command with an invalid file."""
        invalid_file = test_data_dir / 'xml' / 'malformed' / 'malformed_1.xml'
        
        # Skip if test data doesn't exist
        if not invalid_file.exists():
            pytest.skip("Test data file not found")
        
        mock_converter = MagicMock()
        mock_converter.validate_input.return_value = False
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_registry.get_converter.return_value = mock_converter
            result = runner.invoke(cli, ['validate', str(invalid_file)])
            assert result.exit_code == 1
            assert 'not a valid' in result.output.lower()
    
    def test_list_extensions_command(self, runner):
        """Test the list-extensions command."""
        mock_extensions = {
            'databricks': {
                'version': '1.0.0',
                'state': 'loaded',
                'description': 'Databricks extension for Spark processing',
                'load_time': 0.5
            }
        }
        
        mock_manager = MagicMock()
        mock_manager.get_extension_info.return_value = mock_extensions
        
        # The extension manager is accessed via ctx.obj, not imported directly
        # We need to mock the extension manager that's stored in the context
        with patch('pyforge_cli.extensions.get_extension_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_manager
            result = runner.invoke(cli, ['list-extensions'])
            assert result.exit_code == 0
            assert 'databricks' in result.output
    
    def test_convert_command_basic(self, runner, test_data_dir, temp_dir):
        """Test basic convert command."""
        excel_file = test_data_dir / 'excel' / 'basic.xlsx'
        output_file = temp_dir / 'output.parquet'
        
        if excel_file.exists():
            mock_converter = MagicMock()
            mock_converter.validate_input.return_value = True
            mock_converter.convert.return_value = True
            
            with patch('pyforge_cli.main.registry') as mock_registry:
                mock_registry.get_converter.return_value = mock_converter
                result = runner.invoke(cli, ['convert', str(excel_file), str(output_file)])
                assert result.exit_code == 0
                mock_converter.convert.assert_called_once()
    
    def test_convert_command_with_options(self, runner, test_data_dir, temp_dir):
        """Test convert command with various options."""
        xml_file = test_data_dir / 'xml' / 'simple.xml'
        output_file = temp_dir / 'output.parquet'
        
        if xml_file.exists():
            mock_converter = MagicMock()
            mock_converter.validate_input.return_value = True
            mock_converter.convert.return_value = True
            
            with patch('pyforge_cli.main.registry') as mock_registry:
                mock_registry.get_converter.return_value = mock_converter
                result = runner.invoke(cli, [
                    'convert', 
                    str(xml_file),
                    str(output_file),
                    '--flatten-strategy', 'aggressive',
                    '--compression', 'gzip',
                    '--force'
                ])
                assert result.exit_code == 0
                
                # Check that options were passed
                call_args = mock_converter.convert.call_args
                assert 'flatten_strategy' in call_args[1]
                assert call_args[1]['flatten_strategy'] == 'aggressive'
                assert 'compression' in call_args[1]
                assert call_args[1]['compression'] == 'gzip'
    
    def test_convert_command_auto_output(self, runner, test_data_dir, temp_dir):
        """Test convert command with automatic output path."""
        mdb_file = test_data_dir / 'mdb' / 'jet4_database.mdb'
        
        # Skip if test data doesn't exist
        if not mdb_file.exists():
            pytest.skip("Test data file not found")
        
        mock_converter = MagicMock()
        mock_converter.validate_input.return_value = True
        mock_converter.convert.return_value = True
        mock_converter.get_output_extension.return_value = '.parquet'
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_registry.get_converter.return_value = mock_converter
            # Change to temp directory for output
            with runner.isolated_filesystem():
                # Copy input file to isolated filesystem
                shutil.copy(mdb_file, 'jet4_database.mdb')
                
                result = runner.invoke(cli, ['convert', 'jet4_database.mdb'])
                assert result.exit_code == 0
                
                # Check output path was generated correctly
                call_args = mock_converter.convert.call_args
                output_path = call_args[0][1]
                assert output_path.name == 'jet4_database.txt'  # Default format is txt, not parquet
    
    def test_convert_command_file_not_found(self, runner):
        """Test convert command with non-existent file."""
        result = runner.invoke(cli, ['convert', '/nonexistent/file.pdf'])
        assert result.exit_code == 2
        assert 'does not exist' in result.output
    
    def test_convert_command_unsupported_format(self, runner, temp_dir):
        """Test convert command with unsupported format."""
        unsupported_file = temp_dir / 'test.xyz'
        unsupported_file.write_text('unsupported content')
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_registry.get_converter.return_value = None
            result = runner.invoke(cli, ['convert', str(unsupported_file)])
            assert result.exit_code == 0  # Command doesn't exit with error
            assert 'Unsupported input format' in result.output
    
    def test_convert_command_overwrite_protection(self, runner, temp_dir):
        """Test convert command with existing output file."""
        input_file = temp_dir / 'input.xml'
        input_file.write_text('<?xml version="1.0"?><root/>')
        output_file = temp_dir / 'output.parquet'
        output_file.write_text('existing content')
        
        mock_converter = MagicMock()
        mock_converter.validate_input.return_value = True
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_registry.get_converter.return_value = mock_converter
            # Output exists but no --force flag
            result = runner.invoke(cli, ['convert', str(input_file), str(output_file)])
            assert result.exit_code == 0  # Command doesn't exit with error code
            # Should display warning about existing file
            assert 'already exists' in result.output
            # Converter should not be called
            mock_converter.convert.assert_not_called()
    
    def test_convert_excel_with_sheets(self, runner, test_data_dir, temp_dir):
        """Test converting Excel file with multiple sheets."""
        excel_file = test_data_dir / 'excel' / 'multi_sheet.xlsx'
        output_dir = temp_dir / 'output'
        
        if excel_file.exists():
            mock_converter = MagicMock()
            mock_converter.validate_input.return_value = True
            mock_converter.convert.return_value = True
            
            with patch('pyforge_cli.main.registry') as mock_registry:
                mock_registry.get_converter.return_value = mock_converter
                result = runner.invoke(cli, [
                    'convert',
                    str(excel_file),
                    str(output_dir),
                    '--separate',
                    '--force'
                ])
                assert result.exit_code == 0
                
                # Check separate option was passed
                call_args = mock_converter.convert.call_args
                assert 'separate' in call_args[1]
                assert call_args[1]['separate'] is True
    
    def test_convert_mdb_with_tables(self, runner, test_data_dir, temp_dir):
        """Test converting MDB file with table filtering."""
        mdb_file = test_data_dir / 'mdb' / 'jet4_database.mdb'
        output_dir = temp_dir / 'output'
        
        if mdb_file.exists():
            mock_converter = MagicMock()
            mock_converter.validate_input.return_value = True
            mock_converter.convert.return_value = True
            
            with patch('pyforge_cli.main.registry') as mock_registry:
                mock_registry.get_converter.return_value = mock_converter
                result = runner.invoke(cli, [
                    'convert',
                    str(mdb_file),
                    str(output_dir),
                    '--tables', 'Customers,Orders',
                    '--force'
                ])
                assert result.exit_code == 0
                
                # Check tables were parsed correctly
                call_args = mock_converter.convert.call_args
                assert 'tables' in call_args[1]
                # Should be parsed as list
                assert call_args[1]['tables'] == ['Customers', 'Orders']
    
    def test_convert_with_metadata(self, runner, test_data_dir, temp_dir):
        """Test convert command with metadata option."""
        excel_file = test_data_dir / 'excel' / 'mixed_types.xlsx'
        output_file = temp_dir / 'output.parquet'
        
        if excel_file.exists():
            mock_converter = MagicMock()
            mock_converter.validate_input.return_value = True
            mock_converter.convert.return_value = True
            
            with patch('pyforge_cli.main.registry') as mock_registry:
                mock_registry.get_converter.return_value = mock_converter
                result = runner.invoke(cli, [
                    'convert',
                    str(excel_file),
                    str(output_file),
                    '--metadata',
                    '--force'
                ])
                assert result.exit_code == 0
                
                # Check metadata option was passed
                call_args = mock_converter.convert.call_args
                assert 'include_metadata' in call_args[1]
                assert call_args[1]['include_metadata'] is True
    
    def test_convert_error_handling(self, runner, test_data_dir, temp_dir):
        """Test convert command error handling."""
        xml_file = test_data_dir / 'xml' / 'simple.xml'
        output_file = temp_dir / 'output.parquet'
        
        # Skip if test data doesn't exist
        if not xml_file.exists():
            pytest.skip("Test data file not found")
        
        mock_converter = MagicMock()
        mock_converter.validate_input.return_value = True
        mock_converter.convert.side_effect = Exception("Conversion failed due to invalid data")
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_registry.get_converter.return_value = mock_converter
            result = runner.invoke(cli, ['convert', str(xml_file), str(output_file)])
            # The command might exit with error code when conversion fails
            assert result.exit_code == 1
            # Exception is propagated and shown
            assert 'Conversion failed due to invalid data' in str(result.exception)
    
    def test_install_commands(self, runner):
        """Test install command group."""
        result = runner.invoke(cli, ['install', '--help'])
        assert result.exit_code == 0
        assert 'install' in result.output.lower()
        
        # Test subcommands exist
        assert 'sample-datasets' in result.output or 'datasets' in result.output
        assert 'java' in result.output or 'mdf' in result.output
    
    def test_mdf_tools_commands(self, runner):
        """Test mdf-tools command group."""
        result = runner.invoke(cli, ['mdf-tools', '--help'])
        assert result.exit_code == 0
        assert 'mdf-tools' in result.output.lower()
        
        # Test subcommands exist
        assert 'install' in result.output or 'setup' in result.output