"""
Database file readers for various formats.
"""

from .dbf_reader import (
    DBFFieldInfo,
    DBFTableDiscovery,
    DBFTableInfo,
    discover_dbf_table,
    get_dbf_summary,
    validate_dbf_file,
)
from .mdb_reader import (
    MDBConnectionInfo,
    MDBTableDiscovery,
    TableInfo,
    discover_mdb_tables,
    get_mdb_summary,
)

__all__ = [
    # MDB reader
    "MDBTableDiscovery",
    "TableInfo",
    "MDBConnectionInfo",
    "discover_mdb_tables",
    "get_mdb_summary",
    # DBF reader
    "DBFTableDiscovery",
    "DBFFieldInfo",
    "DBFTableInfo",
    "discover_dbf_table",
    "get_dbf_summary",
    "validate_dbf_file",
]
