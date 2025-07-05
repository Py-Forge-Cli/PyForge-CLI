"""
Unit tests for database readers (MDB and DBF).
"""

import tempfile
from pathlib import Path

import pytest

from pyforge_cli.readers.dbf_reader import DBFTableDiscovery
from pyforge_cli.readers.mdb_reader import MDBTableDiscovery


class TestMDBTableDiscovery:
    """Test cases for MDBTableDiscovery class"""

    def test_instantiation(self):
        """Test MDB discovery instantiation"""
        discovery = MDBTableDiscovery()
        assert discovery is not None
        assert hasattr(discovery, "system_tables")
        assert hasattr(discovery, "connection_info")

    def test_system_table_detection(self):
        """Test system table detection"""
        discovery = MDBTableDiscovery()

        # System tables
        assert discovery._is_system_table("MSysObjects")
        assert discovery._is_system_table("MSysQueries")
        assert discovery._is_system_table("MSysAccessObjects")

        # User tables
        assert not discovery._is_system_table("Customers")
        assert not discovery._is_system_table("Orders")
        assert not discovery._is_system_table("Products")

    def test_context_manager(self):
        """Test context manager functionality"""
        with MDBTableDiscovery() as discovery:
            assert discovery is not None

    def test_connection_error_handling(self):
        """Test connection error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing_file = temp_path / "missing.mdb"

            discovery = MDBTableDiscovery()

            with pytest.raises(FileNotFoundError):
                discovery.connect(missing_file)


class TestDBFTableDiscovery:
    """Test cases for DBFTableDiscovery class"""

    def test_instantiation(self):
        """Test DBF discovery instantiation"""
        discovery = DBFTableDiscovery()
        assert discovery is not None
        assert hasattr(discovery, "version_map")
        assert hasattr(discovery, "field_types")

    def test_version_mapping(self):
        """Test DBF version mapping"""
        discovery = DBFTableDiscovery()

        assert discovery.version_map[0x03] == "FoxBASE+/dBASE III PLUS, no memo"
        assert discovery.version_map[0x8B] == "dBASE IV with memo"
        assert discovery.version_map[0xFB] == "FoxPro without memo"

    def test_field_type_mapping(self):
        """Test DBF field type mapping"""
        discovery = DBFTableDiscovery()

        assert discovery.field_types["C"] == "Character"
        assert discovery.field_types["N"] == "Numeric"
        assert discovery.field_types["D"] == "Date"
        assert discovery.field_types["L"] == "Logical"
        assert discovery.field_types["M"] == "Memo"

    def test_context_manager(self):
        """Test context manager functionality"""
        with DBFTableDiscovery() as discovery:
            assert discovery is not None

    def test_connection_error_handling(self):
        """Test connection error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Missing file
            missing_file = temp_path / "missing.dbf"
            discovery = DBFTableDiscovery()

            with pytest.raises(FileNotFoundError):
                discovery.connect(missing_file)

            # Wrong extension
            wrong_file = temp_path / "test.txt"
            wrong_file.write_text("Not a DBF file")

            with pytest.raises(ValueError):
                discovery.connect(wrong_file)


class TestConvenienceFunctions:
    """Test convenience functions for readers"""

    def test_mdb_convenience_functions(self):
        """Test MDB convenience functions"""
        from pyforge_cli.readers import discover_mdb_tables, get_mdb_summary

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing_file = temp_path / "missing.mdb"

            # These should handle errors gracefully
            with pytest.raises((FileNotFoundError, ConnectionError)):
                discover_mdb_tables(missing_file)

            with pytest.raises((FileNotFoundError, ConnectionError)):
                get_mdb_summary(missing_file)

    def test_dbf_convenience_functions(self):
        """Test DBF convenience functions"""
        from pyforge_cli.readers import (
            discover_dbf_table,
            get_dbf_summary,
            validate_dbf_file,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing_file = temp_path / "missing.dbf"

            # These should handle errors gracefully
            with pytest.raises((FileNotFoundError, ConnectionError)):
                discover_dbf_table(missing_file)

            with pytest.raises((FileNotFoundError, ConnectionError)):
                get_dbf_summary(missing_file)

            with pytest.raises((FileNotFoundError, ConnectionError)):
                validate_dbf_file(missing_file)
