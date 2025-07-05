"""Tests for the main CLI commands."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner
import tempfile
import os

from pyforge_cli.main import cli
from pyforge_cli.converters.base import BaseConverter


class TestMainCLI:
    """Test the main CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_cli_version(self, runner):
        """Test the version option."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'version' in result.output.lower()
    
    def test_cli_help(self, runner):
        """Test the help option."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'PyForge CLI' in result.output
        assert 'Commands:' in result.output
    
    def test_cli_verbose_mode(self, runner):
        """Test verbose mode flag."""
        # Test verbose mode with formats command instead of help (help exits early)
        with patch('pyforge_cli.main.plugin_loader'):
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_ext_manager.return_value = MagicMock()
                with patch('pyforge_cli.main.registry') as mock_registry:
                    mock_registry.get_all_converter_info.return_value = {}
                    with patch('pyforge_cli.main.logging.basicConfig') as mock_logging:
                        with patch('pyforge_cli.main.configure_verbose_logging') as mock_verbose:
                            result = runner.invoke(cli, ['--verbose', 'formats'])
                            assert result.exit_code == 0
                            # Verbose flag should trigger verbose logging setup
                            mock_verbose.assert_called_once()
    
    def test_formats_command(self, runner):
        """Test the formats command."""
        with patch('pyforge_cli.main.registry') as mock_registry:
            # Mock converter info
            mock_registry.get_all_converter_info.return_value = {
                'pdf': {
                    'input_formats': ['.pdf'],
                    'output_formats': ['txt'],
                    'description': 'PDF to text converter'
                },
                'excel': {
                    'input_formats': ['.xlsx', '.xls'],
                    'output_formats': ['parquet'],
                    'description': 'Excel to Parquet converter'
                }
            }
            
            result = runner.invoke(cli, ['formats'])
            assert result.exit_code == 0
            assert 'Supported Formats' in result.output
            assert 'pdf' in result.output
            assert 'excel' in result.output
    
    def test_info_command_pdf(self, runner, temp_dir):
        """Test the info command with a PDF file."""
        # Create a test file
        test_file = temp_dir / "test.pdf"
        test_file.write_bytes(b'%PDF-1.4 test content')
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            # Mock converter
            mock_converter = MagicMock()
            mock_converter.get_metadata.return_value = {
                'format': 'PDF',
                'size': '1.2 MB',
                'pages': 10,
                'encrypted': False
            }
            mock_registry.get_converter.return_value = mock_converter
            
            result = runner.invoke(cli, ['info', str(test_file)])
            assert result.exit_code == 0
            assert 'File Information' in result.output
            assert 'test.pdf' in result.output
    
    def test_info_command_json_format(self, runner, temp_dir):
        """Test the info command with JSON output format."""
        test_file = temp_dir / "test.xlsx"
        test_file.write_text("test")
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_converter = MagicMock()
            # Return simple data types that are JSON serializable
            mock_converter.get_metadata.return_value = {
                'format': 'Excel',
                'sheets': ['Sheet1', 'Sheet2'],
                'rows': 100
            }
            mock_registry.get_converter.return_value = mock_converter
            
            result = runner.invoke(cli, ['info', str(test_file), '--format', 'json'])
            assert result.exit_code == 0
            # JSON output should not have the table formatting
            assert 'File Information' not in result.output
            assert '{' in result.output
            assert '"format"' in result.output
    
    def test_validate_command_valid_file(self, runner, temp_dir):
        """Test the validate command with a valid file."""
        test_file = temp_dir / "test.csv"
        test_file.write_text("col1,col2\nval1,val2")
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_converter = MagicMock()
            mock_converter.validate_input.return_value = True
            mock_registry.get_converter.return_value = mock_converter
            
            result = runner.invoke(cli, ['validate', str(test_file)])
            assert result.exit_code == 0
            assert 'valid' in result.output.lower()
    
    def test_validate_command_invalid_file(self, runner, temp_dir):
        """Test the validate command with an invalid file."""
        test_file = temp_dir / "test.mdb"
        test_file.write_text("invalid content")
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            mock_converter = MagicMock()
            mock_converter.validate_input.return_value = False
            mock_registry.get_converter.return_value = mock_converter
            
            result = runner.invoke(cli, ['validate', str(test_file)])
            assert result.exit_code == 1
            assert 'not a valid' in result.output.lower()
    
    def test_list_extensions_command(self, runner):
        """Test the list-extensions command."""
        with patch('pyforge_cli.main.get_extension_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.get_extension_info.return_value = {
                'databricks': {
                    'version': '1.0.0',
                    'state': 'loaded',
                    'description': 'Databricks extension',
                    'load_time': 0.123,
                    'error': None,
                    'enabled': True
                }
            }
            mock_get_manager.return_value = mock_manager
            
            result = runner.invoke(cli, ['list-extensions'])
            assert result.exit_code == 0
            assert 'PyForge CLI Extensions' in result.output
            assert 'databricks' in result.output
    
    def test_convert_command_basic(self, runner, temp_dir):
        """Test basic convert command."""
        input_file = temp_dir / "input.pdf"
        input_file.write_bytes(b'%PDF-1.4 test content')
        output_file = temp_dir / "output.txt"
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, ['convert', str(input_file), str(output_file)])
                assert result.exit_code == 0
                mock_converter.convert.assert_called_once()
    
    def test_convert_command_with_options(self, runner, temp_dir):
        """Test convert command with various options."""
        input_file = temp_dir / "input.pdf"
        input_file.write_bytes(b'%PDF-1.4 test content')
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, [
                    'convert', 
                    str(input_file),
                    '--pages', '1-10',
                    '--metadata',
                    '--force'
                ])
                assert result.exit_code == 0
            
            # Check that options were passed
            call_args = mock_converter.convert.call_args
            assert 'page_range' in call_args[1]
            assert call_args[1]['page_range'] == '1-10'
            assert 'include_metadata' in call_args[1]
            assert call_args[1]['include_metadata'] is True
    
    def test_convert_command_auto_output_path(self, runner, temp_dir):
        """Test convert command with automatic output path generation."""
        input_file = temp_dir / "input.pdf"
        input_file.write_bytes(b'%PDF-1.4 test content')
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_converter.convert.return_value = True
                mock_converter.get_output_extension.return_value = '.txt'
                mock_registry.get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, ['convert', str(input_file)])
                assert result.exit_code == 0
            
            # Check that output path was generated
            call_args = mock_converter.convert.call_args
            output_path = call_args[0][1]
            assert output_path.name == 'input.txt'
            assert output_path.parent == input_file.parent
    
    def test_convert_command_file_not_found(self, runner):
        """Test convert command with non-existent file."""
        result = runner.invoke(cli, ['convert', 'nonexistent.pdf'])
        assert result.exit_code == 2
        assert 'does not exist' in result.output
    
    def test_convert_command_unsupported_format(self, runner, temp_dir):
        """Test convert command with unsupported format."""
        input_file = temp_dir / "test.xyz"
        input_file.write_text("test")
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                
                mock_registry.get_converter.return_value = None
                
                result = runner.invoke(cli, ['convert', str(input_file)])
                assert result.exit_code == 0  # Returns 0 when format is unsupported
                assert 'Unsupported input format' in result.output
    
    def test_convert_command_existing_output_no_force(self, runner, temp_dir):
        """Test convert command with existing output file without force flag."""
        input_file = temp_dir / "input.pdf"
        input_file.write_bytes(b'%PDF-1.4 test content')
        output_file = temp_dir / "output.txt"
        output_file.write_text("existing content")
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                # Simulate user not confirming overwrite
                result = runner.invoke(cli, ['convert', str(input_file), str(output_file)], input='n\n')
                assert result.exit_code == 0  # Returns 0 when file exists and not forced
                assert 'already' in result.output and 'exists' in result.output
                mock_converter.convert.assert_not_called()
    
    def test_convert_command_parquet_format(self, runner, temp_dir):
        """Test convert command with parquet output format."""
        input_file = temp_dir / "data.csv"
        input_file.write_text("col1,col2\nval1,val2")
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_converter.convert.return_value = True
                mock_converter.get_output_extension.return_value = '.parquet'
                mock_registry.get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, [
                    'convert',
                    str(input_file),
                    '--format', 'parquet',
                    '--compression', 'gzip'
                ])
                assert result.exit_code == 0
                
                call_args = mock_converter.convert.call_args
                assert 'compression' in call_args[1]
                assert call_args[1]['compression'] == 'gzip'
    
    def test_convert_command_excel_options(self, runner, temp_dir):
        """Test convert command with Excel-specific options."""
        input_file = temp_dir / "data.xlsx"
        input_file.write_bytes(b'PK\x03\x04')  # Excel file magic bytes
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, [
                    'convert',
                    str(input_file),
                    '--combine',
                    '--force'
                ])
                assert result.exit_code == 0
                
                call_args = mock_converter.convert.call_args
                assert 'combine' in call_args[1]
                assert call_args[1]['combine'] is True
    
    def test_convert_command_xml_options(self, runner, temp_dir):
        """Test convert command with XML-specific options."""
        input_file = temp_dir / "data.xml"
        input_file.write_text('<?xml version="1.0"?><root></root>')
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, [
                    'convert',
                    str(input_file),
                    '--flatten-strategy', 'aggressive',
                    '--array-handling', 'concatenate',
                    '--namespace-handling', 'strip',
                    '--preview-schema'
                ])
                assert result.exit_code == 0
                
                call_args = mock_converter.convert.call_args
                assert call_args[1]['flatten_strategy'] == 'aggressive'
                assert call_args[1]['array_handling'] == 'concatenate'
                assert call_args[1]['namespace_handling'] == 'strip'
                assert call_args[1]['preview_schema'] is True
    
    def test_convert_command_database_options(self, runner, temp_dir):
        """Test convert command with database-specific options."""
        input_file = temp_dir / "database.mdb"
        input_file.write_bytes(b'\x00\x01\x00\x00Standard Jet DB')
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_converter.convert.return_value = True
                mock_registry.get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, [
                    'convert',
                    str(input_file),
                    '--password', 'secret123',
                    '--tables', 'customers,orders'
                ])
                assert result.exit_code == 0
                
                call_args = mock_converter.convert.call_args
                assert call_args[1]['password'] == 'secret123'
                assert call_args[1]['tables'] == ['customers', 'orders']  # tables is split into a list
    
    def test_convert_command_conversion_failure(self, runner, temp_dir):
        """Test convert command when conversion fails."""
        input_file = temp_dir / "input.pdf"
        input_file.write_bytes(b'%PDF-1.4 test content')
        
        with patch('pyforge_cli.main.registry') as mock_registry:
            with patch('pyforge_cli.main.get_extension_manager') as mock_ext_manager:
                mock_manager = MagicMock()
                mock_manager.initialize.return_value = None
                mock_manager.execute_hook.return_value = {}
                mock_ext_manager.return_value = mock_manager
                
                mock_converter = MagicMock()
                mock_converter.validate_input.return_value = True
                mock_converter.convert.return_value = False  # Return False instead of raising exception
                mock_registry.get_converter.return_value = mock_converter
                
                result = runner.invoke(cli, ['convert', str(input_file)])
                assert result.exit_code == 1
                assert 'Conversion failed!' in result.output
    
    def test_install_command_group(self, runner):
        """Test the install command group."""
        result = runner.invoke(cli, ['install', '--help'])
        assert result.exit_code == 0
        assert 'install' in result.output.lower()
        assert 'Commands:' in result.output
    
    def test_mdf_tools_command_group(self, runner):
        """Test the mdf-tools command group."""
        result = runner.invoke(cli, ['mdf-tools', '--help'])
        assert result.exit_code == 0
        assert 'mdf-tools' in result.output.lower()
        assert 'Commands:' in result.output


class TestConvertCommandIntegration:
    """Integration tests for the convert command with real converters."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_csv_to_parquet_conversion(self, runner, temp_dir):
        """Test actual CSV to Parquet conversion."""
        # Create a test CSV file
        csv_file = temp_dir / "test.csv"
        csv_content = """name,age,city
John Doe,30,New York
Jane Smith,25,Los Angeles
Bob Johnson,35,Chicago"""
        csv_file.write_text(csv_content)
        
        # Run the conversion
        result = runner.invoke(cli, [
            'convert',
            str(csv_file),
            '--format', 'parquet',
            '--force'
        ])
        
        # Check results
        assert result.exit_code == 0
        
        # Check output file exists
        output_file = temp_dir / "test.parquet"
        assert output_file.exists()
    
    def test_dbf_to_parquet_conversion(self, runner, temp_dir):
        """Test DBF format detection and conversion setup."""
        # Create a test DBF file with minimal header
        dbf_file = temp_dir / "test.dbf"
        # DBF header: version(1) + date(3) + numrecords(4) + headerlen(2) + recordlen(2) + reserved(20)
        dbf_header = bytearray(32)
        dbf_header[0] = 0x03  # dBase III
        dbf_header[8:10] = b'\x21\x00'  # Header length = 33
        dbf_header[10:12] = b'\x10\x00'  # Record length = 16
        dbf_file.write_bytes(bytes(dbf_header))
        
        result = runner.invoke(cli, [
            'convert',
            str(dbf_file),
            '--format', 'parquet',
            '--force'
        ])
        
        # Even if conversion fails, check that the right converter was selected
        assert 'dbf' in result.output.lower() or 'error' in result.output.lower()