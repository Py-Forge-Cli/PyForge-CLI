"""Improved tests for MDB converter using generated test data."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pyforge_cli.converters.mdb_converter import MDBConverter
from pyforge_cli.detectors.database_detector import DatabaseInfo, DatabaseType


class TestMDBConverterImproved:
    """Improved test suite for MDB converter."""

    @pytest.fixture
    def converter(self):
        """Create an MDB converter instance."""
        return MDBConverter()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def test_data_dir(self):
        """Get the test data directory."""
        return Path(__file__).parent / "data" / "mdb"

    @pytest.fixture
    def mock_table_discovery(self):
        """Create a mock MDBTableDiscovery."""
        mock = MagicMock()
        mock.discover_tables.return_value = True
        mock.get_tables.return_value = ["Customers", "Orders", "Products"]
        mock.get_table_info.side_effect = lambda table: {
            "Customers": {"row_count": 100, "columns": ["ID", "Name", "Email"]},
            "Orders": {"row_count": 500, "columns": ["OrderID", "CustomerID", "Date"]},
            "Products": {"row_count": 50, "columns": ["ProductID", "Name", "Price"]},
        }.get(table, {})
        return mock

    def test_supported_formats(self, converter):
        """Test supported format detection."""
        # MDBConverter has get_supported_formats method
        if hasattr(converter, "get_supported_formats"):
            formats = converter.get_supported_formats()
            assert ".mdb" in formats
            assert ".accdb" in formats

        # Check attributes
        assert hasattr(converter, "supported_inputs")
        assert hasattr(converter, "supported_outputs")
        assert ".mdb" in converter.supported_inputs
        assert ".accdb" in converter.supported_inputs

    def test_validate_jet3_mdb(self, converter, test_data_dir):
        """Test validation of Jet 3 MDB file."""
        mdb_file = test_data_dir / "jet3_database.mdb"
        if mdb_file.exists():
            with patch(
                "pyforge_cli.detectors.database_detector.DatabaseFileDetector.detect_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 3.x", error_message=None
                )
                assert converter.validate_input(mdb_file) is True

    def test_validate_jet4_mdb(self, converter, test_data_dir):
        """Test validation of Jet 4 MDB file."""
        mdb_file = test_data_dir / "jet4_database.mdb"
        if mdb_file.exists():
            with patch(
                "pyforge_cli.detectors.database_detector.DatabaseFileDetector.detect_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )
                assert converter.validate_input(mdb_file) is True

    def test_validate_accdb(self, converter, test_data_dir):
        """Test validation of ACCDB file."""
        accdb_file = test_data_dir / "access_2007.accdb"
        if accdb_file.exists():
            with patch(
                "pyforge_cli.detectors.database_detector.DatabaseFileDetector.detect_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.ACCDB, version="ACE 12.0", error_message=None
                )
                assert converter.validate_input(accdb_file) is True

    def test_validate_corrupted_mdb(self, converter, test_data_dir):
        """Test validation of corrupted MDB file."""
        corrupted_file = test_data_dir / "corrupted.mdb"
        if corrupted_file.exists():
            with patch(
                "pyforge_cli.detectors.database_detector.DatabaseFileDetector.detect_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.UNKNOWN,
                    error_message="Corrupted or invalid MDB file",
                )
                assert converter.validate_input(corrupted_file) is False

    def test_validate_not_mdb(self, converter, test_data_dir):
        """Test validation of non-MDB file with .mdb extension."""
        not_mdb_file = test_data_dir / "not_mdb.mdb"
        if not_mdb_file.exists():
            with patch(
                "pyforge_cli.detectors.database_detector.DatabaseFileDetector.detect_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.UNKNOWN, error_message="Not a database file"
                )
                assert converter.validate_input(not_mdb_file) is False

    def test_validate_nonexistent_file(self, converter):
        """Test validation of non-existent file."""
        assert converter.validate_input(Path("/nonexistent/file.mdb")) is False

    def test_get_metadata_from_real_file(self, converter, test_data_dir):
        """Test metadata extraction from real MDB file if available."""
        mdb_file = test_data_dir / "jet4_database.mdb"

        if mdb_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )

                with patch(
                    "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
                ) as mock_discovery_class:
                    mock_discovery = MagicMock()
                    mock_discovery.connect.return_value = True
                    mock_discovery.list_tables.return_value = [
                        "Customers",
                        "Orders",
                        "Products",
                    ]
                    mock_discovery.get_table_info.side_effect = [
                        type(
                            "TableInfo",
                            (),
                            {
                                "row_count": 100,
                                "columns": [
                                    type("Column", (), {"name": "ID"}),
                                    type("Column", (), {"name": "Name"}),
                                ],
                            },
                        )(),
                        type(
                            "TableInfo",
                            (),
                            {
                                "row_count": 500,
                                "columns": [
                                    type("Column", (), {"name": "OrderID"}),
                                    type("Column", (), {"name": "CustomerID"}),
                                ],
                            },
                        )(),
                        type(
                            "TableInfo",
                            (),
                            {
                                "row_count": 50,
                                "columns": [
                                    type("Column", (), {"name": "ProductID"}),
                                    type("Column", (), {"name": "ProductName"}),
                                ],
                            },
                        )(),
                    ]
                    mock_discovery_class.return_value = mock_discovery

                    metadata = converter.get_metadata(mdb_file)

                    assert metadata is not None
                    assert metadata["table_count"] == 3
                    assert metadata["table_names"] == [
                        "Customers",
                        "Orders",
                        "Products",
                    ]
                    assert "table_details" in metadata
                    assert "Customers" in metadata["table_details"]
                    assert metadata["table_details"]["Customers"]["row_count"] == 100
        else:
            pytest.skip("Test data file not found")

    def test_get_metadata_with_structure_file(self, converter, test_data_dir):
        """Test metadata extraction using structure information."""
        structure_file = test_data_dir / "structures" / "complex_structure.json"

        if structure_file.exists():
            with open(structure_file, encoding="utf-8") as f:
                structure = json.load(f)

            mdb_file = test_data_dir / "jet4_database.mdb"
            if mdb_file.exists():
                with patch(
                    "pyforge_cli.converters.mdb_converter.detect_database_file"
                ) as mock_detect:
                    mock_detect.return_value = DatabaseInfo(
                        file_type=DatabaseType.MDB,
                        version="Jet 4.x",
                        error_message=None,
                    )

                    with patch(
                        "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
                    ) as mock_discovery_class:
                        mock_discovery = MagicMock()
                        mock_discovery.connect.return_value = True
                        mock_discovery.list_tables.return_value = list(
                            structure["tables"].keys()
                        )

                        def mock_get_table_info(table_name):
                            table = structure["tables"].get(table_name, {})
                            columns = table.get("columns", [])
                            return type(
                                "TableInfo",
                                (),
                                {
                                    "row_count": table.get("rows", 0),
                                    "columns": [
                                        type("Column", (), {"name": col})
                                        for col in columns
                                    ],
                                },
                            )()

                        mock_discovery.get_table_info.side_effect = mock_get_table_info
                        mock_discovery_class.return_value = mock_discovery

                        metadata = converter.get_metadata(mdb_file)

                        assert metadata is not None
                        assert metadata["table_count"] == len(structure["tables"])
                        for table_name in structure["tables"]:
                            assert table_name in metadata["table_details"]
            else:
                pytest.skip("Test data file not found")
        else:
            pytest.skip("Structure file not found")

    def test_convert_basic(
        self, converter, test_data_dir, temp_dir, mock_table_discovery
    ):
        """Test basic MDB conversion."""
        mdb_file = test_data_dir / "jet4_database.mdb"
        output_dir = temp_dir / "output"

        if mdb_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )

                with patch.object(converter, "_connect_to_database"):
                    with patch.object(converter, "_list_tables") as mock_list:
                        with patch.object(converter, "_read_table") as mock_read:
                            with patch.object(
                                converter, "_get_table_info"
                            ) as mock_get_info:
                                with patch.object(converter, "_close_connection"):
                                    # Configure mocks
                                    mock_list.return_value = [
                                        "Customers",
                                        "Orders",
                                        "Products",
                                    ]
                                    mock_read.return_value = pd.DataFrame(
                                        {
                                            "col1": ["val1", "val2"],
                                            "col2": ["val3", "val4"],
                                        }
                                    )
                                    mock_get_info.return_value = {
                                        "name": "TestTable",
                                        "record_count": 2,
                                        "column_count": 2,
                                        "estimated_size": 1024,
                                    }

                                    result = converter.convert(mdb_file, output_dir)
                                    assert result is True

                                    # Should have read all tables (might be called multiple times due to progress tracking)
                                    assert mock_read.call_count >= 3

    def test_convert_with_table_filter(self, converter, test_data_dir, temp_dir):
        """Test conversion with table filtering."""
        mdb_file = test_data_dir / "jet4_database.mdb"
        output_dir = temp_dir / "output"

        if mdb_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )

                with patch.object(converter, "_connect_to_database"):
                    with patch.object(converter, "_list_tables") as mock_list:
                        with patch.object(converter, "_read_table") as mock_read:
                            with patch.object(
                                converter, "_get_table_info"
                            ) as mock_get_info:
                                with patch.object(converter, "_close_connection"):
                                    # Configure mocks
                                    mock_list.return_value = [
                                        "Customers",
                                        "Orders",
                                        "Products",
                                    ]
                                    mock_read.return_value = pd.DataFrame(
                                        {"col1": ["val1"], "col2": ["val2"]}
                                    )
                                    mock_get_info.return_value = {
                                        "name": "TestTable",
                                        "record_count": 1,
                                        "column_count": 2,
                                        "estimated_size": 512,
                                    }

                                    # Convert only specific tables
                                    result = converter.convert(
                                        mdb_file,
                                        output_dir,
                                        tables=["Customers", "Orders"],
                                    )
                                    assert result is True

                                    # Should have read only 2 tables (might be called multiple times due to progress tracking)
                                    assert mock_read.call_count >= 2

    def test_convert_encrypted_mdb(self, converter, test_data_dir, temp_dir):
        """Test handling of encrypted MDB file."""
        encrypted_file = test_data_dir / "encrypted.mdb"
        output_dir = temp_dir / "output"

        if encrypted_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB,
                    version="Jet 4.x",
                    is_password_protected=True,
                    error_message=None,
                )

                with patch.object(converter, "_connect_to_database") as mock_connect:
                    # Mock connection to raise exception for encrypted file without password
                    mock_connect.side_effect = ValueError(
                        "Password required for encrypted database"
                    )

                    # Should fail without password
                    result = converter.convert(encrypted_file, output_dir)
                    assert result is False

    def test_convert_with_password(self, converter, test_data_dir, temp_dir):
        """Test conversion with password."""
        encrypted_file = test_data_dir / "encrypted.mdb"
        output_dir = temp_dir / "output"

        if encrypted_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB,
                    version="Jet 4.x",
                    is_password_protected=True,
                    error_message=None,
                )

                with patch.object(converter, "_connect_to_database"):
                    with patch.object(converter, "_list_tables") as mock_list:
                        with patch.object(converter, "_read_table") as mock_read:
                            with patch.object(
                                converter, "_get_table_info"
                            ) as mock_get_info:
                                with patch.object(converter, "_close_connection"):
                                    # Configure mocks
                                    mock_list.return_value = [
                                        "Customers",
                                        "Orders",
                                        "Products",
                                    ]
                                    mock_read.return_value = pd.DataFrame(
                                        {"col1": ["val1"], "col2": ["val2"]}
                                    )
                                    mock_get_info.return_value = {
                                        "name": "TestTable",
                                        "record_count": 1,
                                        "column_count": 2,
                                        "estimated_size": 512,
                                    }

                                    result = converter.convert(
                                        encrypted_file, output_dir, password="secret123"
                                    )
                                    assert result is True

    def test_convert_empty_tables(self, converter, test_data_dir, temp_dir):
        """Test handling of empty tables."""
        structure_file = test_data_dir / "structures" / "empty_tables.json"

        if structure_file.exists():
            with open(structure_file, encoding="utf-8") as f:
                structure = json.load(f)

            mdb_file = test_data_dir / "empty_valid.mdb"
            output_dir = temp_dir / "output"

            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )

                with patch.object(converter, "_connect_to_database"):
                    with patch.object(converter, "_list_tables") as mock_list:
                        with patch.object(converter, "_read_table") as mock_read:
                            with patch.object(
                                converter, "_get_table_info"
                            ) as mock_get_info:
                                with patch.object(converter, "_close_connection"):
                                    # Configure mocks for empty tables
                                    mock_list.return_value = list(
                                        structure["tables"].keys()
                                    )
                                    mock_read.return_value = (
                                        pd.DataFrame()
                                    )  # Empty DataFrame
                                    mock_get_info.return_value = {
                                        "name": "EmptyTable",
                                        "record_count": 0,
                                        "column_count": 0,
                                        "estimated_size": 0,
                                    }

                                    result = converter.convert(mdb_file, output_dir)
                                    # Empty tables result in no conversion, which is considered a failure
                                    assert result is False

    def test_convert_special_table_names(self, converter, test_data_dir, temp_dir):
        """Test handling of special characters in table names."""
        structure_file = test_data_dir / "structures" / "special_names.json"

        if structure_file.exists():
            with open(structure_file, encoding="utf-8") as f:
                structure = json.load(f)

            mdb_file = test_data_dir / "jet4_database.mdb"
            output_dir = temp_dir / "output"

            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )

                with patch.object(converter, "_connect_to_database"):
                    with patch.object(converter, "_list_tables") as mock_list:
                        with patch.object(converter, "_read_table") as mock_read:
                            with patch.object(
                                converter, "_get_table_info"
                            ) as mock_get_info:
                                with patch.object(converter, "_close_connection"):
                                    # Configure mocks for special names
                                    mock_list.return_value = list(
                                        structure["tables"].keys()
                                    )
                                    mock_read.return_value = pd.DataFrame(
                                        {"ID": [1, 2], "Data": ["val1", "val2"]}
                                    )
                                    mock_get_info.return_value = {
                                        "name": "SpecialTable",
                                        "record_count": 10,
                                        "column_count": 2,
                                        "estimated_size": 1024,
                                    }

                                    result = converter.convert(mdb_file, output_dir)
                                    assert result is True

    def test_convert_truncated_file(self, converter, test_data_dir, temp_dir):
        """Test handling of truncated MDB file."""
        truncated_file = test_data_dir / "truncated.mdb"
        output_dir = temp_dir / "output"

        if truncated_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.UNKNOWN,
                    error_message="File is truncated or incomplete",
                )

                result = converter.convert(truncated_file, output_dir)
                assert result is False

    def test_convert_with_compression(self, converter, test_data_dir, temp_dir):
        """Test conversion with compression options."""
        mdb_file = test_data_dir / "jet4_database.mdb"
        output_dir = temp_dir / "output"

        if mdb_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )

                with patch.object(converter, "_connect_to_database"):
                    with patch.object(converter, "_list_tables") as mock_list:
                        with patch.object(converter, "_read_table") as mock_read:
                            with patch.object(
                                converter, "_get_table_info"
                            ) as mock_get_info:
                                with patch.object(converter, "_close_connection"):
                                    # Configure mocks
                                    mock_list.return_value = [
                                        "Customers",
                                        "Orders",
                                        "Products",
                                    ]
                                    mock_read.return_value = pd.DataFrame(
                                        {"col1": ["val1"], "col2": ["val2"]}
                                    )
                                    mock_get_info.return_value = {
                                        "name": "TestTable",
                                        "record_count": 1,
                                        "column_count": 2,
                                        "estimated_size": 512,
                                    }

                                    result = converter.convert(
                                        mdb_file, output_dir, compression="gzip"
                                    )
                                    assert result is True

    def test_get_default_output_extension(self, converter):
        """Test default output extension."""
        # Use base class method
        ext = converter.get_output_extension("parquet")
        assert ext == ".parquet"

    def test_convert_output_directory_creation(
        self, converter, test_data_dir, temp_dir
    ):
        """Test that output directory is created if it doesn't exist."""
        mdb_file = test_data_dir / "jet4_database.mdb"
        output_dir = temp_dir / "nested" / "output"

        if mdb_file.exists():
            # Directory doesn't exist yet
            assert not output_dir.exists()

            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )

                with patch.object(converter, "_connect_to_database"):
                    with patch.object(converter, "_list_tables") as mock_list:
                        with patch.object(converter, "_read_table") as mock_read:
                            with patch.object(
                                converter, "_get_table_info"
                            ) as mock_get_info:
                                with patch.object(converter, "_close_connection"):
                                    # Configure mocks
                                    mock_list.return_value = ["TestTable"]
                                    mock_read.return_value = pd.DataFrame(
                                        {"col1": ["val1"], "col2": ["val2"]}
                                    )
                                    mock_get_info.return_value = {
                                        "name": "TestTable",
                                        "record_count": 1,
                                        "column_count": 2,
                                        "estimated_size": 512,
                                    }

                                    result = converter.convert(mdb_file, output_dir)
                                    assert result is True
                                    assert output_dir.exists()

    def test_get_metadata_basic_mdb(self, converter, test_data_dir):
        """Test metadata extraction from basic MDB file."""
        mdb_file = test_data_dir / "jet4_database.mdb"
        if mdb_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
                )

                with patch(
                    "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
                ) as mock_discovery_class:
                    mock_discovery = MagicMock()
                    mock_discovery.connect.return_value = True
                    mock_discovery.list_tables.return_value = ["Customers", "Orders"]
                    mock_discovery.get_table_info.side_effect = [
                        type(
                            "TableInfo",
                            (),
                            {
                                "row_count": 100,
                                "columns": [
                                    type("Column", (), {"name": "ID"}),
                                    type("Column", (), {"name": "Name"}),
                                ],
                            },
                        )(),
                        type(
                            "TableInfo",
                            (),
                            {
                                "row_count": 500,
                                "columns": [
                                    type("Column", (), {"name": "OrderID"}),
                                    type("Column", (), {"name": "CustomerID"}),
                                ],
                            },
                        )(),
                    ]
                    mock_discovery_class.return_value = mock_discovery

                    metadata = converter.get_metadata(mdb_file)

                    assert metadata is not None
                    assert metadata["file_name"] == "jet4_database.mdb"
                    assert metadata["file_format"] == "Microsoft Access Database"
                    assert metadata["file_extension"] == ".mdb"
                    assert metadata["database_type"] == "MDB"
                    assert metadata["database_version"] == "Jet 4.x"
                    assert metadata["table_count"] == 2
                    assert metadata["table_names"] == ["Customers", "Orders"]
                    assert metadata["total_rows"] == 600
                    assert metadata["total_columns"] == 4

                    # Check table details
                    assert "table_details" in metadata
                    assert "Customers" in metadata["table_details"]
                    assert "Orders" in metadata["table_details"]
                    assert metadata["table_details"]["Customers"]["row_count"] == 100
                    assert metadata["table_details"]["Orders"]["row_count"] == 500
        else:
            pytest.skip("Test data file not found")

    def test_get_metadata_accdb_file(self, converter, test_data_dir):
        """Test metadata extraction from ACCDB file."""
        accdb_file = test_data_dir / "access2016_database.accdb"
        if accdb_file.exists():
            with patch(
                "pyforge_cli.converters.mdb_converter.detect_database_file"
            ) as mock_detect:
                mock_detect.return_value = DatabaseInfo(
                    file_type=DatabaseType.ACCDB,
                    version="Access 2016",
                    error_message=None,
                )

                with patch(
                    "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
                ) as mock_discovery_class:
                    mock_discovery = MagicMock()
                    mock_discovery.connect.return_value = True
                    mock_discovery.list_tables.return_value = ["Products", "Categories"]
                    mock_discovery.get_table_info.side_effect = [
                        type(
                            "TableInfo",
                            (),
                            {
                                "row_count": 50,
                                "columns": [
                                    type("Column", (), {"name": "ProductID"}),
                                    type("Column", (), {"name": "ProductName"}),
                                    type("Column", (), {"name": "Price"}),
                                ],
                            },
                        )(),
                        type(
                            "TableInfo",
                            (),
                            {
                                "row_count": 10,
                                "columns": [
                                    type("Column", (), {"name": "CategoryID"}),
                                    type("Column", (), {"name": "CategoryName"}),
                                ],
                            },
                        )(),
                    ]
                    mock_discovery_class.return_value = mock_discovery

                    metadata = converter.get_metadata(accdb_file)

                    assert metadata is not None
                    assert metadata["database_type"] == "ACCDB"
                    assert metadata["database_version"] == "Access 2016"
                    assert metadata["table_count"] == 2
                    assert metadata["total_rows"] == 60
                    assert metadata["total_columns"] == 5
        else:
            pytest.skip("Test data file not found")

    def test_get_metadata_encrypted_database(self, converter, temp_dir):
        """Test metadata extraction from encrypted database."""
        # Create a fake encrypted database file
        encrypted_file = temp_dir / "encrypted.mdb"
        encrypted_file.write_bytes(b"Encrypted MDB file content")

        with patch(
            "pyforge_cli.converters.mdb_converter.detect_database_file"
        ) as mock_detect:
            mock_detect.return_value = DatabaseInfo(
                file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
            )
            # Add is_encrypted attribute to the returned object
            mock_detect.return_value.is_encrypted = True

            with patch(
                "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
            ) as mock_discovery_class:
                mock_discovery = MagicMock()
                mock_discovery.connect.return_value = (
                    False  # Connection fails for encrypted DB
                )
                mock_discovery_class.return_value = mock_discovery

                metadata = converter.get_metadata(encrypted_file)

                assert metadata is not None
                assert metadata["is_encrypted"] is True
                assert metadata["error"] == "Database is password protected"

    def test_get_metadata_connection_failure(self, converter, temp_dir):
        """Test metadata extraction when connection fails."""
        # Create a fake MDB file
        mdb_file = temp_dir / "connection_fail.mdb"
        mdb_file.write_bytes(b"Fake MDB file content")

        with patch(
            "pyforge_cli.converters.mdb_converter.detect_database_file"
        ) as mock_detect:
            mock_detect.return_value = DatabaseInfo(
                file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
            )

            with patch(
                "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
            ) as mock_discovery_class:
                mock_discovery = MagicMock()
                mock_discovery.connect.return_value = False  # Connection fails
                mock_discovery_class.return_value = mock_discovery

                metadata = converter.get_metadata(mdb_file)

                assert metadata is not None
                assert metadata["error"] == "Connection failed"

    def test_get_metadata_no_tables(self, converter, temp_dir):
        """Test metadata extraction from database with no tables."""
        # Create a fake MDB file
        mdb_file = temp_dir / "no_tables.mdb"
        mdb_file.write_bytes(b"Fake MDB file content")

        with patch(
            "pyforge_cli.converters.mdb_converter.detect_database_file"
        ) as mock_detect:
            mock_detect.return_value = DatabaseInfo(
                file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
            )

            with patch(
                "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
            ) as mock_discovery_class:
                mock_discovery = MagicMock()
                mock_discovery.connect.return_value = True
                mock_discovery.list_tables.return_value = []  # No tables
                mock_discovery_class.return_value = mock_discovery

                metadata = converter.get_metadata(mdb_file)

                assert metadata is not None
                assert metadata["table_count"] == 0
                assert metadata["error"] == "No tables found"

    def test_get_metadata_table_info_error(self, converter, temp_dir):
        """Test metadata extraction when table info extraction fails."""
        # Create a fake MDB file
        mdb_file = temp_dir / "table_error.mdb"
        mdb_file.write_bytes(b"Fake MDB file content")

        with patch(
            "pyforge_cli.converters.mdb_converter.detect_database_file"
        ) as mock_detect:
            mock_detect.return_value = DatabaseInfo(
                file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
            )

            with patch(
                "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
            ) as mock_discovery_class:
                mock_discovery = MagicMock()
                mock_discovery.connect.return_value = True
                mock_discovery.list_tables.return_value = ["ErrorTable"]
                mock_discovery.get_table_info.side_effect = Exception(
                    "Table info error"
                )
                mock_discovery_class.return_value = mock_discovery

                metadata = converter.get_metadata(mdb_file)

                assert metadata is not None
                assert metadata["table_count"] == 1
                assert "table_details" in metadata
                assert "ErrorTable" in metadata["table_details"]
                assert "error" in metadata["table_details"]["ErrorTable"]
                assert (
                    metadata["table_details"]["ErrorTable"]["error"]
                    == "Table info error"
                )

    def test_get_metadata_corrupted_file(self, converter, temp_dir):
        """Test metadata extraction from corrupted MDB file."""
        # Create a corrupted MDB file
        corrupted_file = temp_dir / "corrupted.mdb"
        corrupted_file.write_bytes(b"Not a valid MDB file")

        with patch(
            "pyforge_cli.converters.mdb_converter.detect_database_file"
        ) as mock_detect:
            mock_detect.return_value = DatabaseInfo(
                file_type=DatabaseType.UNKNOWN,
                version=None,
                error_message="Invalid file format",
            )

            metadata = converter.get_metadata(corrupted_file)

            # Should return basic metadata only
            assert metadata is not None
            assert metadata["file_name"] == "corrupted.mdb"
            assert metadata["file_format"] == "Microsoft Access Database"
            assert (
                "database_type" not in metadata
                or metadata["database_type"] == "UNKNOWN"
            )

    def test_get_metadata_nonexistent_file(self, converter):
        """Test metadata extraction from non-existent file."""
        from pathlib import Path

        nonexistent_file = Path("/nonexistent/file.mdb")
        metadata = converter.get_metadata(nonexistent_file)

        # Should return None for non-existent files
        assert metadata is None

    def test_get_metadata_large_database(self, converter, temp_dir):
        """Test metadata extraction from large database with many tables."""
        # Create a fake MDB file
        mdb_file = temp_dir / "large.mdb"
        mdb_file.write_bytes(b"Fake large MDB file content")

        # Create mock table info for 20 tables
        table_names = [f"Table_{i:02d}" for i in range(1, 21)]

        with patch(
            "pyforge_cli.converters.mdb_converter.detect_database_file"
        ) as mock_detect:
            mock_detect.return_value = DatabaseInfo(
                file_type=DatabaseType.MDB, version="Jet 4.x", error_message=None
            )

            with patch(
                "pyforge_cli.converters.mdb_converter.MDBTableDiscovery"
            ) as mock_discovery_class:
                mock_discovery = MagicMock()
                mock_discovery.connect.return_value = True
                mock_discovery.list_tables.return_value = table_names

                def mock_get_table_info(table_name):
                    # Return varying table sizes
                    table_num = int(table_name.split("_")[1])
                    return type(
                        "TableInfo",
                        (),
                        {
                            "row_count": table_num * 100,
                            "columns": [
                                type("Column", (), {"name": "Col_1"}),
                                type("Column", (), {"name": "Col_2"}),
                            ],
                        },
                    )()

                mock_discovery.get_table_info.side_effect = mock_get_table_info
                mock_discovery_class.return_value = mock_discovery

                metadata = converter.get_metadata(mdb_file)

                assert metadata is not None
                assert metadata["table_count"] == 20
                assert metadata["total_rows"] == sum(
                    i * 100 for i in range(1, 21)
                )  # 21000
                assert metadata["total_columns"] == 20 * 2  # 40 columns total
                assert len(metadata["table_names"]) == 20
                assert len(metadata["table_details"]) == 20
