"""
Unit tests for enhanced MDB converter with dual-backend support.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pyforge_cli.converters.enhanced_mdb_converter import EnhancedMDBConverter


class TestEnhancedMDBConverter:
    """Test cases for enhanced MDB converter."""

    def test_converter_instantiation(self):
        """Test converter can be instantiated."""
        converter = EnhancedMDBConverter()
        assert converter is not None
        assert ".mdb" in converter.supported_inputs
        assert ".accdb" in converter.supported_inputs
        assert ".parquet" in converter.supported_outputs

    def test_get_supported_formats(self):
        """Test supported formats method."""
        converter = EnhancedMDBConverter()
        formats = converter.get_supported_formats()
        assert ".mdb" in formats
        assert ".accdb" in formats

    @patch("pyforge_cli.converters.enhanced_mdb_converter.detect_database_file")
    @patch("pyforge_cli.converters.enhanced_mdb_converter.DualBackendMDBReader")
    def test_connect_to_database_success(self, mock_reader_class, mock_detect):
        """Test successful database connection."""
        # Mock file detection
        mock_db_info = Mock()
        mock_db_info.file_type.name = "ACCDB"
        mock_db_info.error_message = None
        mock_detect.return_value = mock_db_info

        # Mock reader
        mock_reader = Mock()
        mock_reader.connect.return_value = True
        mock_reader.get_active_backend.return_value = "UCanAccess"
        mock_reader.get_connection_info.return_value = {"backend": "UCanAccess"}
        mock_reader_class.return_value = mock_reader

        # Test connection
        converter = EnhancedMDBConverter()
        with tempfile.NamedTemporaryFile(suffix=".accdb") as tmp_file:
            tmp_path = Path(tmp_file.name)

            result = converter._connect_to_database(tmp_path)

            assert result is not None
            assert converter.dual_reader is not None
            mock_reader.connect.assert_called_once()

    @patch("pyforge_cli.converters.enhanced_mdb_converter.detect_database_file")
    def test_connect_to_database_invalid_file(self, mock_detect):
        """Test connection with invalid file."""
        # Mock invalid file detection
        mock_db_info = Mock()
        mock_db_info.file_type.name = "UNKNOWN"
        mock_db_info.error_message = None
        mock_detect.return_value = mock_db_info

        converter = EnhancedMDBConverter()
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp_file:
            tmp_path = Path(tmp_file.name)

            with pytest.raises(ValueError, match="not an MDB/ACCDB file"):
                converter._connect_to_database(tmp_path)

    def test_list_tables_success(self):
        """Test successful table listing."""
        # Mock dual reader
        mock_reader = Mock()
        mock_reader.list_tables.return_value = ["Customers", "Orders", "Order Details"]
        mock_reader.get_active_backend.return_value = "UCanAccess"

        converter = EnhancedMDBConverter()
        tables = converter._list_tables(mock_reader)

        assert len(tables) == 3
        assert "Customers" in tables
        assert "Order Details" in tables  # Space-named table
        mock_reader.list_tables.assert_called_once()

    def test_list_tables_with_space_names(self):
        """Test table listing with space-named tables."""
        # Mock dual reader with space-named tables
        mock_reader = Mock()
        mock_reader.list_tables.return_value = [
            "Customers",
            "Employee Privileges",
            "Order Details",
            "Purchase Orders",
            "Sales Reports",
        ]
        mock_reader.get_active_backend.return_value = "UCanAccess"

        converter = EnhancedMDBConverter()
        tables = converter._list_tables(mock_reader)

        # Count space-named tables
        space_tables = [t for t in tables if " " in t]
        assert len(space_tables) == 4  # All except 'Customers'
        assert "Employee Privileges" in space_tables
        assert "Order Details" in space_tables
        assert "Purchase Orders" in space_tables
        assert "Sales Reports" in space_tables

    def test_read_table_success(self):
        """Test successful table reading."""
        # Mock DataFrame
        mock_df = pd.DataFrame(
            {"ID": [1, 2, 3], "Name": ["John", "Jane", "Bob"], "Age": [25, 30, 35]}
        )

        # Mock dual reader
        mock_reader = Mock()
        mock_reader.read_table.return_value = mock_df
        mock_reader.get_active_backend.return_value = "UCanAccess"

        converter = EnhancedMDBConverter()
        result_df = converter._read_table(mock_reader, "Customers")

        assert len(result_df) == 3
        assert list(result_df.columns) == ["ID", "Name", "Age"]
        mock_reader.read_table.assert_called_once_with("Customers")

    def test_read_table_with_space_name(self):
        """Test reading table with space in name."""
        # Mock DataFrame for Order Details
        mock_df = pd.DataFrame(
            {"OrderID": [1, 2], "ProductID": [101, 102], "Quantity": [5, 3]}
        )

        # Mock dual reader
        mock_reader = Mock()
        mock_reader.read_table.return_value = mock_df
        mock_reader.get_active_backend.return_value = "UCanAccess"

        converter = EnhancedMDBConverter()
        result_df = converter._read_table(mock_reader, "Order Details")

        assert len(result_df) == 2
        assert "OrderID" in result_df.columns
        mock_reader.read_table.assert_called_once_with("Order Details")

    def test_get_table_info_success(self):
        """Test table metadata extraction."""
        # Mock DataFrame
        mock_df = pd.DataFrame(
            {
                "ID": [1, 2, 3],
                "Name": ["John", "Jane", None],  # Include null value
                "Age": [25, 30, 35],
            }
        )

        # Mock dual reader
        mock_reader = Mock()
        mock_reader.read_table.return_value = mock_df

        converter = EnhancedMDBConverter()
        table_info = converter._get_table_info(mock_reader, "Customers")

        assert table_info["name"] == "Customers"
        assert table_info["record_count"] == 3
        assert table_info["column_count"] == 3
        assert len(table_info["columns"]) == 3

        # Check column info
        name_column = next(
            col for col in table_info["columns"] if col["name"] == "Name"
        )
        assert name_column["nullable"]  # Has null value

    def test_get_table_info_error_handling(self):
        """Test table info extraction with errors."""
        # Mock dual reader that raises exception
        mock_reader = Mock()
        mock_reader.read_table.side_effect = Exception("Table not found")

        converter = EnhancedMDBConverter()
        table_info = converter._get_table_info(mock_reader, "NonExistent")

        # Should return placeholder info on error
        assert table_info["name"] == "NonExistent"
        assert table_info["record_count"] == 0
        assert table_info["column_count"] == 0
        assert table_info["columns"] == []

    def test_close_connection(self):
        """Test connection cleanup."""
        # Mock dual reader
        mock_reader = Mock()
        mock_reader.get_active_backend.return_value = "UCanAccess"

        converter = EnhancedMDBConverter()
        converter._close_connection(mock_reader)

        mock_reader.close.assert_called_once()

    def test_close_connection_with_error(self):
        """Test connection cleanup with error."""
        # Mock dual reader that raises exception on close
        mock_reader = Mock()
        mock_reader.get_active_backend.return_value = "UCanAccess"
        mock_reader.close.side_effect = Exception("Close failed")

        converter = EnhancedMDBConverter()
        # Should not raise exception
        converter._close_connection(mock_reader)

        mock_reader.close.assert_called_once()

    def test_validate_input_valid_mdb(self):
        """Test input validation for valid MDB file."""
        converter = EnhancedMDBConverter()

        with tempfile.NamedTemporaryFile(suffix=".mdb") as tmp_file:
            tmp_path = Path(tmp_file.name)

            # Mock the detector to return valid
            with patch(
                "pyforge_cli.converters.enhanced_mdb_converter.DatabaseFileDetector"
            ) as mock_detector_class:
                mock_detector = Mock()
                mock_detector.validate_file_access.return_value = (True, None)
                mock_detector_class.return_value = mock_detector

                result = converter.validate_input(tmp_path)
                assert result

    def test_validate_input_invalid_extension(self):
        """Test input validation for invalid file extension."""
        converter = EnhancedMDBConverter()

        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp_file:
            tmp_path = Path(tmp_file.name)
            result = converter.validate_input(tmp_path)
            assert not result

    def test_destructor_cleanup(self):
        """Test automatic cleanup in destructor."""
        mock_reader = Mock()

        converter = EnhancedMDBConverter()
        converter.dual_reader = mock_reader

        # Trigger destructor
        del converter

        # Note: In actual test, destructor might not be called immediately
        # This is more of a structural test


class TestEnhancedMDBConverterIntegration:
    """Integration tests for enhanced MDB converter."""

    @patch("pyforge_cli.converters.enhanced_mdb_converter.detect_database_file")
    @patch("pyforge_cli.backends.ucanaccess_backend.UCanAccessBackend")
    @patch("pyforge_cli.backends.pyodbc_backend.PyODBCBackend")
    def test_backend_selection_ucanaccess_preferred(
        self, mock_pyodbc_class, mock_ucanaccess_class, mock_detect
    ):
        """Test that UCanAccess is preferred over pyodbc."""
        # Mock file detection
        mock_db_info = Mock()
        mock_db_info.file_type.name = "ACCDB"
        mock_db_info.error_message = None
        mock_detect.return_value = mock_db_info

        # Mock UCanAccess available and working
        mock_ucanaccess = Mock()
        mock_ucanaccess.is_available.return_value = True
        mock_ucanaccess_class.return_value = mock_ucanaccess

        # Mock pyodbc available but should not be used
        mock_pyodbc = Mock()
        mock_pyodbc.is_available.return_value = True
        mock_pyodbc_class.return_value = mock_pyodbc

        # Mock the dual reader to use UCanAccess
        with patch(
            "pyforge_cli.converters.enhanced_mdb_converter.DualBackendMDBReader"
        ) as mock_reader_class:
            mock_reader = Mock()
            mock_reader.connect.return_value = True
            mock_reader.get_active_backend.return_value = "UCanAccess"
            mock_reader.get_connection_info.return_value = {"backend": "UCanAccess"}
            mock_reader_class.return_value = mock_reader

            converter = EnhancedMDBConverter()
            with tempfile.NamedTemporaryFile(suffix=".accdb") as tmp_file:
                tmp_path = Path(tmp_file.name)

                result = converter._connect_to_database(tmp_path)

                # Should connect successfully with UCanAccess
                assert result is not None
                mock_reader.connect.assert_called_once()

    @patch("pyforge_cli.converters.enhanced_mdb_converter.Console")
    def test_convert_with_progress_structure(self, mock_console_class):
        """Test convert_with_progress method structure."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        converter = EnhancedMDBConverter()

        with tempfile.NamedTemporaryFile(suffix=".accdb") as tmp_file:
            tmp_path = Path(tmp_file.name)
            output_path = Path(tempfile.mkdtemp())

            # Mock all the dependencies
            with patch.object(
                converter, "_connect_to_database"
            ) as mock_connect, patch.object(
                converter, "_list_tables"
            ) as mock_list, patch.object(
                converter, "_get_table_info"
            ) as mock_info, patch.object(
                converter, "_convert_tables_to_parquet"
            ) as mock_convert, patch.object(
                converter, "_close_connection"
            ) as mock_close, patch(
                "pyforge_cli.converters.enhanced_mdb_converter.detect_database_file"
            ) as mock_detect:

                # Setup mocks
                mock_db_info = Mock()
                mock_db_info.file_type.name = "ACCDB"
                mock_db_info.file_size = 1024 * 1024  # 1MB
                mock_detect.return_value = mock_db_info

                mock_reader = Mock()
                mock_reader.get_active_backend.return_value = "UCanAccess"
                mock_connect.return_value = mock_reader

                mock_list.return_value = ["Customers", "Order Details"]
                mock_info.return_value = {
                    "name": "Customers",
                    "record_count": 10,
                    "column_count": 5,
                    "columns": [],
                }
                mock_convert.return_value = True

                # Test the method
                result = converter.convert_with_progress(tmp_path, output_path)

                # Verify stages were called
                assert result
                mock_connect.assert_called_once()
                mock_list.assert_called_once()
                mock_convert.assert_called_once()
                mock_close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
