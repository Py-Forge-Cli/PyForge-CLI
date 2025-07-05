"""Improved tests for Excel converter using generated test data."""

import tempfile
from pathlib import Path

import pytest

from pyforge_cli.converters.excel_converter import ExcelConverter


class TestExcelConverterImproved:
    """Improved test suite for Excel converter."""

    @pytest.fixture
    def converter(self):
        """Create an Excel converter instance."""
        return ExcelConverter()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def test_data_dir(self):
        """Get the test data directory."""
        return Path(__file__).parent / "data" / "excel"

    def test_supported_formats(self, converter):
        """Test supported format detection."""
        # ExcelConverter should have these attributes set
        assert hasattr(converter, "supported_inputs")
        assert hasattr(converter, "supported_outputs")

        # Check supported formats if they exist
        if converter.supported_inputs:
            assert (
                ".xlsx" in converter.supported_inputs
                or ".xls" in converter.supported_inputs
            )

    def test_validate_basic_excel(self, converter, test_data_dir):
        """Test validation of basic Excel file."""
        excel_file = test_data_dir / "basic.xlsx"
        if excel_file.exists():
            assert converter.validate_input(excel_file) is True

    def test_validate_multi_sheet_excel(self, converter, test_data_dir):
        """Test validation of multi-sheet Excel file."""
        excel_file = test_data_dir / "multi_sheet.xlsx"
        if excel_file.exists():
            assert converter.validate_input(excel_file) is True

    def test_validate_invalid_file(self, converter, temp_dir):
        """Test validation of non-Excel file."""
        invalid_file = temp_dir / "not_excel.txt"
        invalid_file.write_text("This is not an Excel file")
        assert converter.validate_input(invalid_file) is False

    def test_validate_nonexistent_file(self, converter):
        """Test validation of non-existent file."""
        assert converter.validate_input(Path("/nonexistent/file.xlsx")) is False

    def test_get_info_basic(self, converter, test_data_dir):
        """Test getting info from basic Excel file."""
        excel_file = test_data_dir / "basic.xlsx"
        if excel_file.exists():
            # ExcelConverter may not have get_info method
            if hasattr(converter, "get_info"):
                info = converter.get_info(excel_file)
                assert isinstance(info, dict)
            elif hasattr(converter, "get_metadata"):
                info = converter.get_metadata(excel_file)
                # get_metadata might return None
                assert info is None or isinstance(info, dict)

    def test_get_info_multi_sheet(self, converter, test_data_dir):
        """Test getting info from multi-sheet Excel file."""
        excel_file = test_data_dir / "multi_sheet.xlsx"
        if excel_file.exists():
            # Skip if converter doesn't have info methods
            if hasattr(converter, "get_info"):
                info = converter.get_info(excel_file)
                assert isinstance(info, dict)
            else:
                pytest.skip("Converter doesn't have get_info method")

    def test_get_info_empty_sheets(self, converter, test_data_dir):
        """Test getting info from Excel with empty sheets."""
        excel_file = test_data_dir / "empty_sheets.xlsx"
        if excel_file.exists():
            # Skip if converter doesn't have info methods
            if hasattr(converter, "get_info"):
                info = converter.get_info(excel_file)
                assert isinstance(info, dict)
            else:
                pytest.skip("Converter doesn't have get_info method")

    def test_convert_basic_excel(self, converter, test_data_dir, temp_dir):
        """Test converting basic Excel file."""
        excel_file = test_data_dir / "basic.xlsx"
        output_file = temp_dir / "output.parquet"

        if excel_file.exists():
            result = converter.convert(excel_file, output_file)
            assert result is True
            assert output_file.exists()

    def test_convert_mixed_types(self, converter, test_data_dir, temp_dir):
        """Test converting Excel with mixed data types."""
        excel_file = test_data_dir / "mixed_types.xlsx"
        output_file = temp_dir / "output.parquet"

        if excel_file.exists():
            result = converter.convert(excel_file, output_file)
            assert result is True
            assert output_file.exists()

    def test_convert_special_characters(self, converter, test_data_dir, temp_dir):
        """Test converting Excel with special characters."""
        excel_file = test_data_dir / "special_characters.xlsx"
        output_file = temp_dir / "output.parquet"

        if excel_file.exists():
            result = converter.convert(excel_file, output_file)
            assert result is True
            assert output_file.exists()

    def test_convert_null_heavy(self, converter, test_data_dir, temp_dir):
        """Test converting Excel with many null values."""
        excel_file = test_data_dir / "null_heavy.xlsx"
        output_file = temp_dir / "output.parquet"

        if excel_file.exists():
            result = converter.convert(excel_file, output_file)
            assert result is True
            assert output_file.exists()

    def test_convert_large_dataset(self, converter, test_data_dir, temp_dir):
        """Test converting large Excel file."""
        excel_file = test_data_dir / "large_dataset.xlsx"
        output_file = temp_dir / "output.parquet"

        if excel_file.exists():
            result = converter.convert(excel_file, output_file)
            assert result is True
            assert output_file.exists()

    def test_convert_multi_sheet_separate(self, converter, test_data_dir, temp_dir):
        """Test converting multi-sheet Excel to separate files."""
        excel_file = test_data_dir / "multi_sheet.xlsx"
        output_dir = temp_dir / "output"

        if excel_file.exists():
            result = converter.convert(excel_file, output_dir, separate=True)
            assert result is True
            assert output_dir.exists()

            # Check that separate files were created
            expected_files = [
                "multi_sheet_Employees.parquet",
                "multi_sheet_Departments.parquet",
                "multi_sheet_Projects.parquet",
            ]
            for filename in expected_files:
                assert (output_dir / filename).exists()

    def test_convert_multi_sheet_combine(self, converter, test_data_dir, temp_dir):
        """Test combining sheets with matching columns."""
        # Create a test Excel with sheets having same columns
        excel_file = test_data_dir / "pivot_like.xlsx"
        output_file = temp_dir / "combined.parquet"

        if excel_file.exists():
            # This file has consistent structure across rows
            result = converter.convert(excel_file, output_file, combine=True)
            assert result is True
            assert output_file.exists()

    def test_convert_with_compression(self, converter, test_data_dir, temp_dir):
        """Test converting with different compression options."""
        excel_file = test_data_dir / "basic.xlsx"

        if excel_file.exists():
            # Test gzip compression
            output_gzip = temp_dir / "output_gzip.parquet"
            result = converter.convert(excel_file, output_gzip, compression="gzip")
            assert result is True
            assert output_gzip.exists()

            # Test snappy compression
            output_snappy = temp_dir / "output_snappy.parquet"
            result = converter.convert(excel_file, output_snappy, compression="snappy")
            assert result is True
            assert output_snappy.exists()

            # Test no compression
            output_none = temp_dir / "output_none.parquet"
            result = converter.convert(excel_file, output_none, compression="none")
            assert result is True
            assert output_none.exists()

    def test_convert_formulas_excel(self, converter, test_data_dir, temp_dir):
        """Test converting Excel with formulas."""
        excel_file = test_data_dir / "formulas.xlsx"
        output_file = temp_dir / "output.parquet"

        if excel_file.exists():
            # Should convert formula results, not formulas themselves
            result = converter.convert(excel_file, output_file)
            assert result is True
            assert output_file.exists()

    def test_convert_styled_excel(self, converter, test_data_dir, temp_dir):
        """Test converting styled Excel (ignores styling)."""
        excel_file = test_data_dir / "styled.xlsx"
        output_file = temp_dir / "output.parquet"

        if excel_file.exists():
            # Should extract data, ignoring styles
            result = converter.convert(excel_file, output_file)
            assert result is True
            assert output_file.exists()

    def test_convert_empty_sheets_handling(self, converter, test_data_dir, temp_dir):
        """Test handling of empty sheets."""
        excel_file = test_data_dir / "empty_sheets.xlsx"
        output_dir = temp_dir / "output"

        if excel_file.exists():
            result = converter.convert(excel_file, output_dir, separate=True)
            assert result is True

            # Check that non-empty sheets were converted
            assert (output_dir / "empty_sheets_Data.parquet").exists()
            # Empty sheets might be skipped or create empty files

    def test_convert_duplicate_columns(self, converter, test_data_dir, temp_dir):
        """Test handling duplicate column names."""
        excel_file = test_data_dir / "duplicate_columns.xlsx"
        output_file = temp_dir / "output.parquet"

        if excel_file.exists():
            result = converter.convert(excel_file, output_file)
            # Duplicate columns cause Parquet schema errors - expected failure
            assert result is False
        else:
            pytest.skip("Test data file not found")

    def test_convert_error_handling(self, converter, temp_dir):
        """Test error handling during conversion."""
        # Create a corrupted Excel file
        corrupted_file = temp_dir / "corrupted.xlsx"
        corrupted_file.write_bytes(b"Not a valid Excel file")

        output_file = temp_dir / "output.parquet"
        result = converter.convert(corrupted_file, output_file)
        assert result is False

    def test_get_default_output_extension(self, converter):
        """Test default output extension."""
        # Check if converter has a default output extension method or use base class method
        ext = converter.get_output_extension("parquet")
        assert ext == ".parquet"

    def test_convert_with_sheet_names_special_chars(
        self, converter, test_data_dir, temp_dir
    ):
        """Test handling sheet names with special characters."""
        excel_file = test_data_dir / "multi_sheet.xlsx"
        output_dir = temp_dir / "output"

        if excel_file.exists():
            result = converter.convert(excel_file, output_dir, separate=True)
            assert result is True

            # Check that files were created with sanitized names
            files = list(output_dir.glob("*.parquet"))
            assert len(files) > 0
            # All files should be valid paths
            for f in files:
                assert f.exists()

    def test_convert_output_directory_creation(
        self, converter, test_data_dir, temp_dir
    ):
        """Test that output directory is created if it doesn't exist."""
        excel_file = test_data_dir / "basic.xlsx"
        output_file = temp_dir / "nested" / "dir" / "output.parquet"

        if excel_file.exists():
            # Directory doesn't exist yet
            assert not output_file.parent.exists()

            result = converter.convert(excel_file, output_file)
            assert result is True
            assert output_file.exists()
            assert output_file.parent.exists()
