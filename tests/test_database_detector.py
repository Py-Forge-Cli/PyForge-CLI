"""
Unit tests for database file detection functionality.
"""

import tempfile
from pathlib import Path
import struct
import pytest

from pyforge_cli.detectors.database_detector import (
    DatabaseFileDetector, 
    DatabaseType, 
    detect_database_file,
    is_supported_database,
    get_database_type
)


class TestDatabaseFileDetector:
    """Test cases for DatabaseFileDetector class"""
    
    def test_instantiation(self):
        """Test detector instantiation"""
        detector = DatabaseFileDetector()
        assert detector is not None
        assert hasattr(detector, 'detected_files')
    
    def test_supported_extensions(self):
        """Test supported file extensions"""
        detector = DatabaseFileDetector()
        extensions = detector.get_supported_extensions()
        assert '.mdb' in extensions
        assert '.accdb' in extensions
        assert '.dbf' in extensions
    
    def test_mdb_detection(self):
        """Test MDB file detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mdb_file = temp_path / "test.mdb"
            
            # Create mock MDB file
            with open(mdb_file, 'wb') as f:
                f.write(b'\x01\x00\x00\x00')  # Jet 4.0 signature
                f.write(b'Standard Jet DB')
                f.write(b'\x00' * 1000)
            
            detector = DatabaseFileDetector()
            info = detector.detect_file(mdb_file)
            
            assert info.file_type == DatabaseType.MDB
            assert info.version is not None
            assert info.estimated_size > 0
    
    def test_dbf_detection(self):
        """Test DBF file detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            dbf_file = temp_path / "test.dbf"
            
            # Create mock DBF file
            with open(dbf_file, 'wb') as f:
                f.write(struct.pack('<B', 0x03))  # dBASE III signature
                f.write(struct.pack('<3B', 24, 6, 19))  # Date
                f.write(struct.pack('<L', 100))  # Record count
                f.write(struct.pack('<H', 65))  # Header length
                f.write(struct.pack('<H', 50))  # Record length
                f.write(b'\x00' * 1000)
            
            detector = DatabaseFileDetector()
            info = detector.detect_file(dbf_file)
            
            assert info.file_type == DatabaseType.DBF
            assert info.version is not None
            assert info.estimated_size > 0
    
    def test_unknown_file_detection(self):
        """Test unknown file detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            unknown_file = temp_path / "test.txt"
            unknown_file.write_text("This is not a database file")
            
            detector = DatabaseFileDetector()
            info = detector.detect_file(unknown_file)
            
            assert info.file_type == DatabaseType.UNKNOWN
            assert info.error_message is not None
    
    def test_missing_file_detection(self):
        """Test missing file detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing_file = temp_path / "missing.mdb"
            
            detector = DatabaseFileDetector()
            info = detector.detect_file(missing_file)
            
            assert info.file_type == DatabaseType.UNKNOWN
            assert "not found" in info.error_message
    
    def test_file_validation(self):
        """Test file validation functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Valid MDB file
            mdb_file = temp_path / "test.mdb"
            with open(mdb_file, 'wb') as f:
                f.write(b'\x01\x00\x00\x00')
                f.write(b'Test MDB Content')
                f.write(b'\x00' * 100)
            
            detector = DatabaseFileDetector()
            is_valid, message = detector.validate_file_access(mdb_file)
            assert is_valid
            assert "valid" in message
            
            # Missing file
            missing_file = temp_path / "missing.mdb"
            is_valid, message = detector.validate_file_access(missing_file)
            assert not is_valid
            assert "does not exist" in message
    
    def test_format_file_info(self):
        """Test file info formatting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mdb_file = temp_path / "test.mdb"
            
            # Create mock MDB file
            with open(mdb_file, 'wb') as f:
                f.write(b'\x01\x00\x00\x00')
                f.write(b'Test content')
                f.write(b'\x00' * 100)
            
            detector = DatabaseFileDetector()
            info = detector.detect_file(mdb_file)
            formatted = detector.format_file_info(info)
            
            assert "File Type" in formatted
            assert "MDB" in formatted
            assert "Version" in formatted
            assert "Size" in formatted


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_detect_database_file(self):
        """Test detect_database_file convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mdb_file = temp_path / "test.mdb"
            
            with open(mdb_file, 'wb') as f:
                f.write(b'\x01\x00\x00\x00')
                f.write(b'\x00' * 100)
            
            info = detect_database_file(mdb_file)
            assert info.file_type == DatabaseType.MDB
    
    def test_is_supported_database(self):
        """Test is_supported_database convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Supported file
            mdb_file = temp_path / "test.mdb"
            with open(mdb_file, 'wb') as f:
                f.write(b'\x01\x00\x00\x00')
                f.write(b'\x00' * 100)
            
            assert is_supported_database(mdb_file)
            
            # Unsupported file
            txt_file = temp_path / "test.txt"
            txt_file.write_text("Not a database")
            
            assert not is_supported_database(txt_file)
    
    def test_get_database_type(self):
        """Test get_database_type convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # MDB file
            mdb_file = temp_path / "test.mdb"
            with open(mdb_file, 'wb') as f:
                f.write(b'\x01\x00\x00\x00')
                f.write(b'\x00' * 100)
            
            assert get_database_type(mdb_file) == DatabaseType.MDB
            
            # DBF file
            dbf_file = temp_path / "test.dbf"
            with open(dbf_file, 'wb') as f:
                f.write(struct.pack('<B', 0x03))
                f.write(b'\x00' * 100)
            
            assert get_database_type(dbf_file) == DatabaseType.DBF