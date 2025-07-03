"""
Tests for the PySpark CSV converter.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from pyforge_cli.converters import get_csv_converter
from pyforge_cli.converters.pyspark_csv_converter import PySparkCSVConverter


# Skip all tests if PySpark is not available
pyspark_available = False
try:
    import pyspark
    pyspark_available = True
except ImportError:
    pass

pytestmark = pytest.mark.skipif(not pyspark_available, reason="PySpark not available")


class TestPySparkCSVConverter:
    """Tests for the PySpark CSV converter."""
    
    def test_pyspark_availability_detection(self):
        """Test PySpark availability detection."""
        converter = PySparkCSVConverter()
        assert isinstance(converter.pyspark_available, bool)
        # Should be True since we're only running these tests if PySpark is available
        assert converter.pyspark_available is True
    
    def test_databricks_environment_detection(self):
        """Test Databricks environment detection."""
        converter = PySparkCSVConverter()
        # We're not in Databricks, so this should be False
        assert converter.is_databricks is False
    
    @patch('pyforge_cli.converters.pyspark_csv_converter.PySparkCSVConverter._convert_with_pyspark')
    def test_convert_uses_pyspark_when_forced(self, mock_convert_with_pyspark):
        """Test that convert uses PySpark when forced."""
        mock_convert_with_pyspark.return_value = True
        
        converter = PySparkCSVConverter()
        input_path = Path('tests/data/csv/sample.csv')
        output_path = Path('tests/data/csv/sample.parquet')
        
        # Mock validate_input to return True
        with patch.object(converter, 'validate_input', return_value=True):
            # Mock Path.stat to avoid file not found error
            with patch.object(Path, 'stat', return_value=MagicMock(st_size=1000)):
                result = converter.convert(input_path, output_path, force_pyspark=True)
                
                # Check that _convert_with_pyspark was called
                mock_convert_with_pyspark.assert_called_once_with(input_path, output_path, force_pyspark=True)
                assert result is True
    
    @patch('pyforge_cli.converters.pyspark_csv_converter.PySparkCSVConverter._convert_with_pyspark')
    @patch('pyforge_cli.converters.csv_converter.CSVConverter.convert')
    def test_convert_falls_back_to_pandas_when_pyspark_fails(self, mock_pandas_convert, mock_convert_with_pyspark):
        """Test that convert falls back to pandas when PySpark fails."""
        mock_convert_with_pyspark.side_effect = Exception("PySpark error")
        mock_pandas_convert.return_value = True
        
        converter = PySparkCSVConverter()
        input_path = Path('tests/data/csv/sample.csv')
        output_path = Path('tests/data/csv/sample.parquet')
        
        # Mock validate_input to return True
        with patch.object(converter, 'validate_input', return_value=True):
            # Mock Path.stat to avoid file not found error
            with patch.object(Path, 'stat', return_value=MagicMock(st_size=1000)):
                result = converter.convert(input_path, output_path, force_pyspark=True)
                
                # Check that _convert_with_pyspark was called
                mock_convert_with_pyspark.assert_called_once_with(input_path, output_path, force_pyspark=True)
                # Check that pandas convert was called as fallback
                mock_pandas_convert.assert_called_once()
                assert result is True


class TestCSVConverterFactory:
    """Tests for the CSV converter factory."""
    
    def test_get_csv_converter_returns_standard_converter_when_no_detection(self):
        """Test that get_csv_converter returns standard converter when no detection."""
        from pyforge_cli.converters.csv_converter import CSVConverter
        
        converter = get_csv_converter(detect_environment=False, force_pyspark=False)
        assert isinstance(converter, CSVConverter)
        assert not isinstance(converter, PySparkCSVConverter)
    
    def test_get_csv_converter_returns_pyspark_converter_when_forced(self):
        """Test that get_csv_converter returns PySpark converter when forced."""
        converter = get_csv_converter(detect_environment=True, force_pyspark=True)
        assert isinstance(converter, PySparkCSVConverter)
    
    @patch('pyforge_cli.converters.PySparkCSVConverter')
    def test_get_csv_converter_handles_pyspark_converter_error(self, mock_pyspark_converter):
        """Test that get_csv_converter handles PySpark converter error."""
        from pyforge_cli.converters.csv_converter import CSVConverter
        
        # Mock PySparkCSVConverter to raise an exception
        mock_pyspark_converter.side_effect = Exception("PySpark error")
        
        # Should fall back to standard converter
        converter = get_csv_converter(detect_environment=True, force_pyspark=True)
        assert isinstance(converter, CSVConverter)
        assert not isinstance(converter, PySparkCSVConverter)
    
    @patch('pyforge_cli.converters.pyspark_csv_converter.PySparkCSVConverter.is_databricks', True)
    def test_get_csv_converter_returns_pyspark_converter_in_databricks(self):
        """Test that get_csv_converter returns PySpark converter in Databricks."""
        with patch('pyforge_cli.converters.PySparkCSVConverter') as mock_class:
            # Mock the instance returned by PySparkCSVConverter()
            mock_instance = MagicMock()
            mock_instance.is_databricks = True
            mock_instance.pyspark_available = True
            mock_class.return_value = mock_instance
            
            converter = get_csv_converter(detect_environment=True)
            assert converter == mock_instance
