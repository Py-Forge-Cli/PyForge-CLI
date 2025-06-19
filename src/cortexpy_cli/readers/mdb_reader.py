"""
MDB (Microsoft Access) database reader with table discovery.
Supports cross-platform reading with fallback strategies.
"""

import platform
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
import pandas as pd

from ..detectors.database_detector import DatabaseInfo, DatabaseType


@dataclass
class TableInfo:
    """Information about a database table"""
    name: str
    record_count: int
    column_count: int
    estimated_size: int
    columns: List[Dict[str, Any]]
    has_primary_key: bool = False
    is_system_table: bool = False


@dataclass
class MDBConnectionInfo:
    """Information about MDB connection"""
    file_path: Path
    connection_type: str  # 'pandas_access', 'pyodbc', 'mdbtools'
    version: Optional[str] = None
    is_password_protected: bool = False
    encoding: str = 'windows-1252'


class MDBTableDiscovery:
    """
    Discovers and analyzes tables in Microsoft Access databases.
    Uses cross-platform approach with fallback strategies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection_info: Optional[MDBConnectionInfo] = None
        self._connection = None
        
        # System tables to filter out
        self.system_tables = {
            'MSysObjects', 'MSysQueries', 'MSysRelationships', 'MSysAccessObjects',
            'MSysACEs', 'MSysModules', 'MSysNameMap', 'MSysNavPaneGroupCategories',
            'MSysNavPaneGroups', 'MSysNavPaneObjectIDs', 'MSysComplexColumns',
            'MSysComplexTypes', 'MSysAccessStorage'
        }
    
    def connect(self, file_path: Union[str, Path], password: Optional[str] = None) -> bool:
        """
        Connect to MDB file using best available method.
        
        Args:
            file_path: Path to MDB file
            password: Optional password for protected databases
            
        Returns:
            True if connection successful
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"MDB file not found: {file_path}")
        
        self.logger.info(f"Connecting to MDB file: {file_path}")
        
        # Try connection methods in order of preference
        connection_methods = []
        
        # Windows: prefer pyodbc
        if platform.system() == "Windows":
            connection_methods = [
                ('pyodbc', self._connect_pyodbc),
                ('pandas_access', self._connect_pandas_access)
            ]
        else:
            # Unix: pandas_access only
            connection_methods = [
                ('pandas_access', self._connect_pandas_access)
            ]
        
        # Try each connection method
        for method_name, method_func in connection_methods:
            try:
                self.logger.debug(f"Trying connection method: {method_name}")
                success = method_func(file_path, password)
                
                if success:
                    self.connection_info = MDBConnectionInfo(
                        file_path=file_path,
                        connection_type=method_name,
                        is_password_protected=password is not None
                    )
                    self.logger.info(f"✓ Connected using {method_name}")
                    return True
                    
            except Exception as e:
                self.logger.debug(f"Connection method {method_name} failed: {e}")
                continue
        
        raise ConnectionError(f"Failed to connect to MDB file: {file_path}")
    
    def _connect_pyodbc(self, file_path: Path, password: Optional[str] = None) -> bool:
        """Connect using pyodbc (Windows only)"""
        try:
            import pyodbc
            
            # Build connection string
            conn_str = f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={file_path};'
            
            if password:
                conn_str += f'PWD={password};'
            
            self._connection = pyodbc.connect(conn_str)
            return True
            
        except ImportError:
            raise ImportError("pyodbc not available")
        except Exception as e:
            self.logger.debug(f"pyodbc connection failed: {e}")
            return False
    
    def _connect_pandas_access(self, file_path: Path, password: Optional[str] = None) -> bool:
        """Connect using pandas-access (cross-platform)"""
        try:
            import pandas_access as mdb
            
            if password:
                self.logger.warning("pandas-access doesn't support password-protected files")
                return False
            
            # Test connection by listing tables
            tables = mdb.list_tables(str(file_path))
            self._connection = str(file_path)  # Store file path as connection
            return True
            
        except ImportError:
            raise ImportError("pandas-access not available")
        except Exception as e:
            self.logger.debug(f"pandas-access connection failed: {e}")
            return False
    
    def list_tables(self, include_system: bool = False) -> List[str]:
        """
        List all tables in the database.
        
        Args:
            include_system: Whether to include system tables
            
        Returns:
            List of table names
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        if self.connection_info.connection_type == 'pyodbc':
            return self._list_tables_pyodbc(include_system)
        elif self.connection_info.connection_type == 'pandas_access':
            return self._list_tables_pandas_access(include_system)
        else:
            raise NotImplementedError(f"Table listing not implemented for {self.connection_info.connection_type}")
    
    def _list_tables_pyodbc(self, include_system: bool) -> List[str]:
        """List tables using pyodbc"""
        cursor = self._connection.cursor()
        
        # Get all user tables
        tables = []
        for table_info in cursor.tables(tableType='TABLE'):
            table_name = table_info.table_name
            
            # Filter system tables
            if not include_system and self._is_system_table(table_name):
                continue
                
            tables.append(table_name)
        
        return sorted(tables)
    
    def _list_tables_pandas_access(self, include_system: bool) -> List[str]:
        """List tables using pandas-access"""
        import pandas_access as mdb
        
        all_tables = mdb.list_tables(self._connection)
        
        # Filter system tables
        if include_system:
            return sorted(all_tables)
        else:
            user_tables = [t for t in all_tables if not self._is_system_table(t)]
            return sorted(user_tables)
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """
        Get detailed information about a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            TableInfo object with table details
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        if self.connection_info.connection_type == 'pyodbc':
            return self._get_table_info_pyodbc(table_name)
        elif self.connection_info.connection_type == 'pandas_access':
            return self._get_table_info_pandas_access(table_name)
        else:
            raise NotImplementedError(f"Table info not implemented for {self.connection_info.connection_type}")
    
    def _get_table_info_pyodbc(self, table_name: str) -> TableInfo:
        """Get table info using pyodbc"""
        cursor = self._connection.cursor()
        
        # Get column information
        columns = []
        for column in cursor.columns(table=table_name):
            columns.append({
                'name': column.column_name,
                'type': column.type_name,
                'size': column.column_size,
                'nullable': column.nullable == 1,
                'position': column.ordinal_position
            })
        
        # Get record count
        count_query = f"SELECT COUNT(*) FROM [{table_name}]"
        cursor.execute(count_query)
        record_count = cursor.fetchone()[0]
        
        # Check for primary key (simple heuristic)
        has_primary_key = any('ID' in col['name'].upper() for col in columns)
        
        return TableInfo(
            name=table_name,
            record_count=record_count,
            column_count=len(columns),
            estimated_size=record_count * sum(col.get('size', 50) for col in columns),
            columns=columns,
            has_primary_key=has_primary_key,
            is_system_table=self._is_system_table(table_name)
        )
    
    def _get_table_info_pandas_access(self, table_name: str) -> TableInfo:
        """Get table info using pandas-access"""
        import pandas_access as mdb
        
        try:
            # Read table to get info (read just a few rows for efficiency)
            df = mdb.read_table(self._connection, table_name, rows=5)
            
            # For full count, we need to read the entire table (limitation of pandas-access)
            full_df = mdb.read_table(self._connection, table_name)
            record_count = len(full_df)
            
            # Build column information
            columns = []
            for i, (col_name, dtype) in enumerate(df.dtypes.items()):
                columns.append({
                    'name': col_name,
                    'type': str(dtype),
                    'size': 50,  # Estimate
                    'nullable': df[col_name].isnull().any(),
                    'position': i + 1
                })
            
            # Check for primary key (simple heuristic)
            has_primary_key = any('ID' in col['name'].upper() for col in columns)
            
            return TableInfo(
                name=table_name,
                record_count=record_count,
                column_count=len(columns),
                estimated_size=record_count * 50 * len(columns),  # Rough estimate
                columns=columns,
                has_primary_key=has_primary_key,
                is_system_table=self._is_system_table(table_name)
            )
            
        except Exception as e:
            self.logger.error(f"Error getting table info for {table_name}: {e}")
            # Return minimal info on error
            return TableInfo(
                name=table_name,
                record_count=0,
                column_count=0,
                estimated_size=0,
                columns=[],
                is_system_table=self._is_system_table(table_name)
            )
    
    def read_table(self, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Read table data as DataFrame.
        
        Args:
            table_name: Name of the table to read
            limit: Optional limit on number of records
            
        Returns:
            DataFrame with table data
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        if self.connection_info.connection_type == 'pyodbc':
            return self._read_table_pyodbc(table_name, limit)
        elif self.connection_info.connection_type == 'pandas_access':
            return self._read_table_pandas_access(table_name, limit)
        else:
            raise NotImplementedError(f"Table reading not implemented for {self.connection_info.connection_type}")
    
    def _read_table_pyodbc(self, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Read table using pyodbc"""
        query = f"SELECT * FROM [{table_name}]"
        if limit:
            query = f"SELECT TOP {limit} * FROM [{table_name}]"
        
        return pd.read_sql(query, self._connection)
    
    def _read_table_pandas_access(self, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Read table using pandas-access"""
        import pandas_access as mdb
        
        df = mdb.read_table(self._connection, table_name)
        
        if limit and len(df) > limit:
            df = df.head(limit)
        
        return df
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Get comprehensive database summary"""
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        # Get all user tables
        tables = self.list_tables(include_system=False)
        
        # Get info for each table
        table_info_list = []
        total_records = 0
        total_size = 0
        
        for table_name in tables:
            try:
                info = self.get_table_info(table_name)
                table_info_list.append(info)
                total_records += info.record_count
                total_size += info.estimated_size
            except Exception as e:
                self.logger.warning(f"Could not get info for table {table_name}: {e}")
        
        return {
            'file_path': str(self.connection_info.file_path),
            'connection_type': self.connection_info.connection_type,
            'table_count': len(tables),
            'total_records': total_records,
            'estimated_total_size': total_size,
            'tables': [
                {
                    'name': info.name,
                    'records': info.record_count,
                    'columns': info.column_count,
                    'size': info.estimated_size
                }
                for info in table_info_list
            ]
        }
    
    def _is_system_table(self, table_name: str) -> bool:
        """Check if table is a system table"""
        return table_name in self.system_tables or table_name.startswith('MSys')
    
    def close(self):
        """Close database connection"""
        if self._connection and hasattr(self._connection, 'close'):
            try:
                self._connection.close()
            except:
                pass
        self._connection = None
        self.connection_info = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience functions
def discover_mdb_tables(file_path: Union[str, Path], password: Optional[str] = None) -> List[str]:
    """
    Discover tables in MDB file.
    
    Args:
        file_path: Path to MDB file
        password: Optional password
        
    Returns:
        List of table names
    """
    with MDBTableDiscovery() as discovery:
        discovery.connect(file_path, password)
        return discovery.list_tables()


def get_mdb_summary(file_path: Union[str, Path], password: Optional[str] = None) -> Dict[str, Any]:
    """
    Get comprehensive MDB database summary.
    
    Args:
        file_path: Path to MDB file
        password: Optional password
        
    Returns:
        Database summary dictionary
    """
    with MDBTableDiscovery() as discovery:
        discovery.connect(file_path, password)
        return discovery.get_database_summary()