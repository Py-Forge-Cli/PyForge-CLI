"""
Unit tests for database converters (MDB and DBF).
"""

import tempfile
from pathlib import Path

from pyforge_cli.converters.dbf_converter import DBFConverter
from pyforge_cli.converters.mdb_converter import MDBConverter


class TestMDBConverter:
    """Test cases for MDBConverter class"""

    def test_instantiation(self):
        """Test MDB converter instantiation"""
        converter = MDBConverter()
        assert converter is not None
        assert hasattr(converter, "string_converter")
        assert hasattr(converter, "discovery")

    def test_supported_formats(self):
        """Test supported file formats"""
        converter = MDBConverter()
        formats = converter.get_supported_formats()

        assert ".mdb" in formats
        assert ".accdb" in formats
        assert len(formats) == 2

    def test_input_validation(self):
        """Test input file validation"""
        converter = MDBConverter()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Valid extension, non-existent file
            mdb_file = temp_path / "test.mdb"
            is_valid = converter.validate_input(mdb_file)
            assert not is_valid  # File doesn't exist

            # Invalid extension
            txt_file = temp_path / "test.txt"
            txt_file.write_text("Not an MDB file")
            is_valid = converter.validate_input(txt_file)
            assert not is_valid  # Wrong extension

            # Valid MDB file (basic)
            mdb_file.write_bytes(b"\x01\x00\x00\x00" + b"Test MDB" + b"\x00" * 100)
            is_valid = converter.validate_input(mdb_file)
            assert is_valid  # Valid extension and file exists

    def test_conversion_error_handling(self):
        """Test conversion error handling"""
        converter = MDBConverter()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / "output"

            # Try to convert non-existent file
            missing_file = temp_path / "missing.mdb"
            result = converter.convert(missing_file, output_path)
            assert not result

    def test_string_conversion_integration(self):
        """Test string conversion integration"""
        converter = MDBConverter()
        string_converter = converter.string_converter

        # Test basic conversions
        assert string_converter.convert_value(123) == "123"
        assert string_converter.convert_value(True) == "true"
        assert string_converter.convert_value(None) == ""

    def test_conversion_reporting(self):
        """Test conversion reporting"""
        converter = MDBConverter()

        # Initial report should show no conversions
        report = converter.get_conversion_report()
        assert report["status"] == "no_conversions"


class TestDBFConverter:
    """Test cases for DBFConverter class"""

    def test_instantiation(self):
        """Test DBF converter instantiation"""
        converter = DBFConverter()
        assert converter is not None
        assert hasattr(converter, "string_converter")
        assert hasattr(converter, "discovery")

    def test_supported_formats(self):
        """Test supported file formats"""
        converter = DBFConverter()
        formats = converter.get_supported_formats()

        assert ".dbf" in formats
        assert len(formats) == 1

    def test_input_validation(self):
        """Test input file validation"""
        converter = DBFConverter()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Valid extension, non-existent file
            dbf_file = temp_path / "test.dbf"
            is_valid = converter.validate_input(dbf_file)
            assert not is_valid  # File doesn't exist

            # Invalid extension
            txt_file = temp_path / "test.txt"
            txt_file.write_text("Not a DBF file")
            is_valid = converter.validate_input(txt_file)
            assert not is_valid  # Wrong extension

            # Valid DBF file (basic)
            dbf_file.write_bytes(b"\x03" + b"\x00" * 31 + b"Test DBF" + b"\x00" * 100)
            is_valid = converter.validate_input(dbf_file)
            assert is_valid  # Valid extension and file exists

    def test_conversion_error_handling(self):
        """Test conversion error handling"""
        converter = DBFConverter()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / "output"

            # Try to convert non-existent file
            missing_file = temp_path / "missing.dbf"
            result = converter.convert(missing_file, output_path)
            assert not result

    def test_string_conversion_integration(self):
        """Test string conversion integration"""
        converter = DBFConverter()
        string_converter = converter.string_converter

        # Test basic conversions
        assert string_converter.convert_value(123) == "123"
        assert string_converter.convert_value(True) == "true"
        assert string_converter.convert_value(None) == ""

    def test_conversion_reporting(self):
        """Test conversion reporting"""
        converter = DBFConverter()

        # Initial report should show no conversions
        report = converter.get_conversion_report()
        assert report["status"] == "no_conversions"


class TestConverterIntegration:
    """Test integration between converters and other components"""

    def test_file_detection_integration(self):
        """Test integration with file detection"""
        from pyforge_cli.detectors import DatabaseType, detect_database_file

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test MDB file
            mdb_file = temp_path / "test.mdb"
            mdb_file.write_bytes(b"\x01\x00\x00\x00" + b"Test MDB" + b"\x00" * 100)

            info = detect_database_file(mdb_file)
            assert info.file_type == DatabaseType.MDB

            mdb_converter = MDBConverter()
            is_valid = mdb_converter.validate_input(mdb_file)
            assert is_valid

            # Test DBF file
            dbf_file = temp_path / "test.dbf"
            dbf_file.write_bytes(b"\x03" + b"\x00" * 31 + b"Test DBF" + b"\x00" * 100)

            info = detect_database_file(dbf_file)
            assert info.file_type == DatabaseType.DBF

            dbf_converter = DBFConverter()
            is_valid = dbf_converter.validate_input(dbf_file)
            assert is_valid

    def test_converter_factory_pattern(self):
        """Test that converters can be selected by file type"""
        from pyforge_cli.detectors import DatabaseType, get_database_type

        def get_converter_for_file(file_path):
            """Factory function to get appropriate converter"""
            db_type = get_database_type(file_path)

            if db_type in [DatabaseType.MDB, DatabaseType.ACCDB]:
                return MDBConverter()
            elif db_type == DatabaseType.DBF:
                return DBFConverter()
            else:
                return None

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # MDB file
            mdb_file = temp_path / "test.mdb"
            mdb_file.write_bytes(b"\x01\x00\x00\x00" + b"\x00" * 100)

            converter = get_converter_for_file(mdb_file)
            assert isinstance(converter, MDBConverter)

            # DBF file
            dbf_file = temp_path / "test.dbf"
            dbf_file.write_bytes(b"\x03" + b"\x00" * 100)

            converter = get_converter_for_file(dbf_file)
            assert isinstance(converter, DBFConverter)

            # Unknown file
            txt_file = temp_path / "test.txt"
            txt_file.write_text("Unknown")

            converter = get_converter_for_file(txt_file)
            assert converter is None
