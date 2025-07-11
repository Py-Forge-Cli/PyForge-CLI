"""
Database file format detection for MDB/DBF files.
Identifies file types by magic bytes and metadata analysis.
"""

import struct
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple, Union


class DatabaseType(Enum):
    """Supported database file types"""

    MDB = "mdb"
    ACCDB = "accdb"
    DBF = "dbf"
    UNKNOWN = "unknown"


@dataclass
class DatabaseInfo:
    """Database file information"""

    file_type: DatabaseType
    version: Optional[str] = None
    is_password_protected: bool = False
    estimated_size: int = 0
    estimated_tables: int = 0
    encoding: Optional[str] = None
    creation_date: Optional[str] = None
    error_message: Optional[str] = None


class DatabaseFileDetector:
    """Detects and analyzes database file formats"""

    # Magic bytes for different database formats
    MDB_SIGNATURES = {
        b"\x00\x01\x00\x00": "Access 97 (Jet 3.5)",
        b"\x01\x00\x00\x00": "Access 2000/2002/2003 (Jet 4.0)",
        b"\x02\x00\x00\x00": "Access 2007/2010/2013 (ACE)",
        b"\x03\x00\x00\x00": "Access 2016+ (ACE)",
    }

    DBF_SIGNATURES = {
        0x02: "FoxBASE",
        0x03: "FoxBASE+/dBASE III PLUS, no memo",
        0x04: "dBASE IV w/o memo",
        0x05: "dBASE V w/o memo",
        0x30: "Visual FoxPro",
        0x31: "Visual FoxPro, autoincrement",
        0x32: "Visual FoxPro with field type Varchar",
        0x43: "dBASE IV SQL table files, no memo",
        0x63: "dBASE IV SQL system files, no memo",
        0x83: "FoxBASE+/dBASE III PLUS, with memo",
        0x8B: "dBASE IV with memo",
        0x8E: "dBASE IV with SQL table",
        0xCB: "dBASE IV SQL table files, with memo",
        0xF5: "FoxPro 2.x (or earlier) with memo",
        0xFB: "FoxPro without memo",
    }

    def __init__(self):
        self.detected_files: Dict[str, DatabaseInfo] = {}

    def detect_file(self, file_path: Union[str, Path]) -> DatabaseInfo:
        """
        Detect database file type and extract metadata.

        Args:
            file_path: Path to database file

        Returns:
            DatabaseInfo object with file details
        """
        file_path = Path(file_path)

        # Check if file exists
        if not file_path.exists():
            return DatabaseInfo(
                file_type=DatabaseType.UNKNOWN,
                error_message=f"File not found: {file_path}",
            )

        # Get file extension
        extension = file_path.suffix.lower()

        try:
            # Route to appropriate detector based on extension
            if extension in [".mdb", ".accdb"]:
                return self._detect_access_file(file_path)
            elif extension == ".dbf":
                return self._detect_dbf_file(file_path)
            else:
                # Try to detect by content
                with open(file_path, "rb") as f:
                    header = f.read(32)

                # Check for MDB signature
                if self._is_access_signature(header):
                    return self._detect_access_file(file_path)
                # Check for DBF signature
                elif len(header) > 0 and header[0] in self.DBF_SIGNATURES:
                    return self._detect_dbf_file(file_path)
                else:
                    return DatabaseInfo(
                        file_type=DatabaseType.UNKNOWN,
                        error_message=f"Unknown database format: {file_path}",
                    )

        except Exception as e:
            return DatabaseInfo(
                file_type=DatabaseType.UNKNOWN,
                error_message=f"Error detecting file: {str(e)}",
            )

    def _detect_access_file(self, file_path: Path) -> DatabaseInfo:
        """Detect and analyze Access database file"""
        try:
            with open(file_path, "rb") as f:
                # Read header
                header = f.read(32)

                # Check magic bytes
                if len(header) < 4:
                    return DatabaseInfo(
                        file_type=DatabaseType.UNKNOWN,
                        error_message="File too small to be valid Access database",
                    )

                magic = header[:4]

                # Determine file type
                if file_path.suffix.lower() == ".accdb":
                    file_type = DatabaseType.ACCDB
                    version = "Access 2007+"
                else:
                    file_type = DatabaseType.MDB
                    version = self.MDB_SIGNATURES.get(magic, "Unknown Access version")

                # Check for password protection (simple heuristic)
                is_password_protected = self._check_access_password(f)

                # Get file size
                f.seek(0, 2)  # Seek to end
                file_size = f.tell()

                # Estimate tables (rough heuristic)
                estimated_tables = self._estimate_access_tables(f)

                return DatabaseInfo(
                    file_type=file_type,
                    version=version,
                    is_password_protected=is_password_protected,
                    estimated_size=file_size,
                    estimated_tables=estimated_tables,
                    encoding=(
                        "UTF-8" if file_type == DatabaseType.ACCDB else "Windows-1252"
                    ),
                )

        except Exception as e:
            return DatabaseInfo(
                file_type=(
                    DatabaseType.MDB
                    if file_path.suffix.lower() == ".mdb"
                    else DatabaseType.ACCDB
                ),
                error_message=f"Error analyzing Access file: {str(e)}",
            )

    def _detect_dbf_file(self, file_path: Path) -> DatabaseInfo:
        """Detect and analyze DBF database file"""
        try:
            with open(file_path, "rb") as f:
                # Read DBF header
                header = f.read(32)

                if len(header) < 32:
                    return DatabaseInfo(
                        file_type=DatabaseType.UNKNOWN,
                        error_message="File too small to be valid DBF file",
                    )

                # Parse DBF header
                version_byte = header[0]
                version = self.DBF_SIGNATURES.get(
                    version_byte, f"Unknown DBF version (0x{version_byte:02X})"
                )

                # Extract basic information
                last_update = struct.unpack("<3B", header[1:4])  # YY, MM, DD
                struct.unpack("<L", header[4:8])[0]
                header_length = struct.unpack("<H", header[8:10])[0]
                struct.unpack("<H", header[10:12])[0]

                # Calculate file size
                f.seek(0, 2)
                file_size = f.tell()

                # Estimate encoding
                encoding = self._estimate_dbf_encoding(f, header_length)

                # Format creation date
                creation_date = None
                if last_update[0] > 0:  # Valid date
                    year = (
                        1900 + last_update[0]
                        if last_update[0] < 80
                        else 2000 + last_update[0]
                    )
                    creation_date = (
                        f"{year:04d}-{last_update[1]:02d}-{last_update[2]:02d}"
                    )

                return DatabaseInfo(
                    file_type=DatabaseType.DBF,
                    version=version,
                    is_password_protected=False,  # DBF files don't have password protection
                    estimated_size=file_size,
                    estimated_tables=1,  # DBF files contain one table
                    encoding=encoding,
                    creation_date=creation_date,
                )

        except Exception as e:
            return DatabaseInfo(
                file_type=DatabaseType.DBF,
                error_message=f"Error analyzing DBF file: {str(e)}",
            )

    def _is_access_signature(self, header: bytes) -> bool:
        """Check if header contains Access database signature"""
        if len(header) < 4:
            return False

        magic = header[:4]
        return magic in self.MDB_SIGNATURES

    def _check_access_password(self, f) -> bool:
        """
        Check if Access database is password protected.
        This is a simple heuristic and may not be 100% accurate.
        """
        try:
            # Move to password flag location (approximate)
            f.seek(66)
            password_flag = f.read(1)

            # Check for password marker
            if password_flag and password_flag[0] == 0x02:
                return True

            # Alternative check - look for encrypted header patterns
            f.seek(16)
            header_section = f.read(16)

            # If header contains mostly zeros or encrypted patterns
            if header_section.count(b"\x00") > 12:
                return False

            # Look for encryption markers
            encryption_markers = [b"\x86\xfb", b"\x68\x08", b"\x01\x00"]
            for marker in encryption_markers:
                if marker in header_section:
                    return True

            return False

        except Exception:
            return False

    def _estimate_access_tables(self, f) -> int:
        """
        Estimate number of tables in Access database.
        This is a rough heuristic based on common patterns.
        """
        try:
            # Look for table name patterns in the file
            f.seek(0)
            content = f.read(8192)  # Read first 8KB

            # Count occurrences of common table markers
            table_markers = [
                b"MSysObjects",
                b"MSysQueries",
                b"MSysRelationships",
                b"TABLE",
                b"QUERY",
            ]

            table_count = 0
            for marker in table_markers:
                if marker in content:
                    table_count += content.count(marker)

            # Rough estimate (subtract system tables)
            estimated = max(1, table_count // 3)
            return min(estimated, 50)  # Cap at reasonable number

        except Exception:
            return 1  # Default estimate

    def _estimate_dbf_encoding(self, f, header_length: int) -> str:
        """Estimate character encoding for DBF file"""
        try:
            # Read some data to analyze
            f.seek(header_length)
            sample_data = f.read(1024)

            # Try to detect encoding
            import chardet

            detected = chardet.detect(sample_data)

            if detected and detected["confidence"] > 0.7:
                return detected["encoding"]

            # Fallback to common DBF encodings
            if any(b > 127 for b in sample_data[:100]):  # Non-ASCII characters
                return "cp850"  # Common European encoding
            else:
                return "ascii"

        except Exception:
            return "cp850"  # Default fallback

    def validate_file_access(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Validate that file can be opened and read.

        Args:
            file_path: Path to database file

        Returns:
            Tuple of (is_valid, error_message)
        """
        file_path = Path(file_path)

        try:
            # Check file exists
            if not file_path.exists():
                return False, f"File does not exist: {file_path}"

            # Check file is not empty
            if file_path.stat().st_size == 0:
                return False, "File is empty"

            # Check file is readable
            with open(file_path, "rb") as f:
                f.read(1)

            # Check file type is supported
            info = self.detect_file(file_path)
            if info.file_type == DatabaseType.UNKNOWN:
                return False, info.error_message or "Unknown file format"

            return True, "File is valid and supported"

        except PermissionError:
            return False, "Permission denied - cannot read file"
        except Exception as e:
            return False, f"Error validating file: {str(e)}"

    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions"""
        return [".mdb", ".accdb", ".dbf"]

    def format_file_info(self, info: DatabaseInfo) -> str:
        """Format DatabaseInfo for display"""
        if info.error_message:
            return f"❌ Error: {info.error_message}"

        lines = [
            f"📁 File Type: {info.file_type.value.upper()}",
            f"🔧 Version: {info.version or 'Unknown'}",
            f"🔒 Password Protected: {'Yes' if info.is_password_protected else 'No'}",
            f"📊 Estimated Size: {info.estimated_size:,} bytes",
            f"📋 Estimated Tables: {info.estimated_tables}",
            f"🔤 Encoding: {info.encoding or 'Unknown'}",
        ]

        if info.creation_date:
            lines.append(f"📅 Creation Date: {info.creation_date}")

        return "\n".join(lines)


# Convenience functions for common use cases
def detect_database_file(file_path: Union[str, Path]) -> DatabaseInfo:
    """Convenience function to detect a single database file"""
    detector = DatabaseFileDetector()
    return detector.detect_file(file_path)


def is_supported_database(file_path: Union[str, Path]) -> bool:
    """Check if file is a supported database format"""
    info = detect_database_file(file_path)
    return info.file_type != DatabaseType.UNKNOWN and info.error_message is None


def get_database_type(file_path: Union[str, Path]) -> DatabaseType:
    """Get database type for file"""
    info = detect_database_file(file_path)
    return info.file_type
