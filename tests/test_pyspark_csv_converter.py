"""
Tests for the PySpark CSV converter.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyforge_cli.converters import get_csv_converter
from pyforge_cli.converters.csv_converter import CSVConverter
from pyforge_cli.converters.pyspark_csv_converter import PySparkCSVConverter

# Skip all tests if PySpark is not available
pyspark_available = False
try:
    import pyspark  # noqa: F401

    pyspark_available = True
except ImportError:
    pass

# Mark all tests in this module as databricks tests and skip if pyspark not available
pytestmark = [
    pytest.mark.databricks,
    pytest.mark.skipif(not pyspark_available, reason="PySpark not available"),
]


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

    @patch(
        "pyforge_cli.converters.pyspark_csv_converter.PySparkCSVConverter._convert_with_pyspark"
    )
    def test_convert_uses_pyspark_when_forced(self, mock_convert_with_pyspark):
        """Test that convert uses PySpark when forced."""
        mock_convert_with_pyspark.return_value = True

        converter = PySparkCSVConverter()
        input_path = Path("tests/data/csv/sample.csv")
        output_path = Path("tests/data/csv/sample.parquet")

        # Mock validate_input to return True
        with patch.object(converter, "validate_input", return_value=True):
            # Mock Path.stat to avoid file not found error
            with patch.object(Path, "stat", return_value=MagicMock(st_size=1000)):
                result = converter.convert(input_path, output_path, force_pyspark=True)

                # Check that _convert_with_pyspark was called
                mock_convert_with_pyspark.assert_called_once_with(
                    input_path, output_path, force_pyspark=True
                )
                assert result is True

    def test_convert_falls_back_to_pandas_when_pyspark_fails(self):
        """Test that convert falls back to pandas when PySpark fails."""
        converter = PySparkCSVConverter()
        input_path = Path("tests/data/csv/sample.csv")
        output_path = Path("tests/data/csv/sample.parquet")

        # Create a mock that simulates SparkSession creation failure
        mock_spark_module = MagicMock()
        mock_spark_module.sql.SparkSession.builder.getOrCreate.side_effect = Exception(
            "PySpark error"
        )

        # Mock the parent class convert method to track calls
        with patch.object(
            CSVConverter, "convert", return_value=True
        ) as mock_pandas_convert:
            # Patch sys.modules to inject our mock
            with patch.dict(
                "sys.modules",
                {"pyspark": mock_spark_module, "pyspark.sql": mock_spark_module.sql},
            ):
                # Mock validate_input to return True
                with patch.object(converter, "validate_input", return_value=True):
                    # Mock Path.stat to avoid file not found error
                    with patch.object(
                        Path, "stat", return_value=MagicMock(st_size=1000)
                    ):
                        # Call convert with force_pyspark=True
                        result = converter.convert(
                            input_path, output_path, force_pyspark=True
                        )

                        # Check that pandas convert was called as fallback
                        mock_pandas_convert.assert_called_once_with(
                            input_path, output_path, force_pyspark=True
                        )
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

    @patch("pyforge_cli.converters.PySparkCSVConverter")
    def test_get_csv_converter_handles_pyspark_converter_error(
        self, mock_pyspark_converter
    ):
        """Test that get_csv_converter handles PySpark converter error."""
        from pyforge_cli.converters.csv_converter import CSVConverter

        # Mock PySparkCSVConverter to raise an exception
        mock_pyspark_converter.side_effect = Exception("PySpark error")

        # Should fall back to standard converter
        converter = get_csv_converter(detect_environment=True, force_pyspark=True)
        assert isinstance(converter, CSVConverter)
        assert not isinstance(converter, PySparkCSVConverter)

    def test_get_csv_converter_returns_pyspark_converter_in_databricks(self):
        """Test that get_csv_converter returns PySpark converter in Databricks."""
        # Create a mock PySparkCSVConverter instance
        mock_instance = MagicMock(spec=PySparkCSVConverter)
        mock_instance.is_databricks = True
        mock_instance.pyspark_available = True

        # Patch the PySparkCSVConverter class to return our mock
        with patch(
            "pyforge_cli.converters.PySparkCSVConverter", return_value=mock_instance
        ):
            converter = get_csv_converter(detect_environment=True)
            assert converter == mock_instance
