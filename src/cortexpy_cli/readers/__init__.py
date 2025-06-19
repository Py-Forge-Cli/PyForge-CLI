"""
Database file readers for various formats.
"""

from .mdb_reader import (
    MDBTableDiscovery,
    TableInfo,
    MDBConnectionInfo,
    discover_mdb_tables,
    get_mdb_summary,
)

from .dbf_reader import (
    DBFTableDiscovery,
    DBFFieldInfo,
    DBFTableInfo,
    discover_dbf_table,
    get_dbf_summary,
    validate_dbf_file,
)

__all__ = [
    # MDB reader
    'MDBTableDiscovery',
    'TableInfo',
    'MDBConnectionInfo',
    'discover_mdb_tables',
    'get_mdb_summary',
    
    # DBF reader
    'DBFTableDiscovery',
    'DBFFieldInfo',
    'DBFTableInfo',
    'discover_dbf_table',
    'get_dbf_summary',
    'validate_dbf_file',
]