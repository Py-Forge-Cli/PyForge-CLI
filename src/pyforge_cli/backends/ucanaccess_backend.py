"""UCanAccess JDBC backend for cross-platform Access database connectivity."""

import os
import subprocess
import logging
from typing import List, Optional
import pandas as pd

from .base import DatabaseBackend
from .jar_manager import UCanAccessJARManager


class UCanAccessBackend(DatabaseBackend):
    """UCanAccess JDBC backend for cross-platform Access support."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.jar_manager = UCanAccessJARManager()
        self.connection = None
        self.db_path = None
        self._jaydebeapi = None
    
    def is_available(self) -> bool:
        """Check if UCanAccess backend is available.
        
        Checks:
        1. Java runtime availability
        2. JayDeBeApi Python package
        3. UCanAccess JAR (downloads if needed)
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        try:
            # Check Java runtime
            if not self._check_java():
                self.logger.debug("Java runtime not available")
                return False
            
            # Check JayDeBeApi
            if not self._check_jaydebeapi():
                self.logger.debug("JayDeBeApi not available")
                return False
            
            # Check/download UCanAccess JAR
            if not self.jar_manager.ensure_jar_available():
                self.logger.debug("UCanAccess JAR not available")
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"UCanAccess availability check failed: {e}")
            return False
    
    def connect(self, db_path: str, password: str = None) -> bool:
        """Connect to Access database via UCanAccess JDBC.
        
        Args:
            db_path: Path to Access database file
            password: Optional password for protected databases
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Ensure backend is available
            if not self.is_available():
                self.logger.error("UCanAccess backend not available")
                return False
            
            # Import jaydebeapi (should be available after is_available check)
            import jaydebeapi
            self._jaydebeapi = jaydebeapi
            
            self.db_path = os.path.abspath(db_path)
            jar_path = self.jar_manager.get_jar_path()
            
            # Build JDBC connection string
            conn_string = f"jdbc:ucanaccess://{self.db_path}"
            
            # Add performance optimizations
            # Use disk-based mode for better reliability with medium/large databases
            conn_string += ";memory=false"
            
            # Set up connection properties
            connection_props = ["", ""]  # [username, password]
            if password:
                connection_props = [password, ""]
            
            # Establish JDBC connection
            self.connection = jaydebeapi.connect(
                "net.ucanaccess.jdbc.UcanaccessDriver",
                conn_string,
                connection_props,
                jar_path
            )
            
            # Test connection by getting database metadata
            meta = self.connection.jconn.getMetaData()
            meta.getTables(None, None, '%', ['TABLE'])
            
            self.logger.info(f"UCanAccess connected to: {db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"UCanAccess connection failed: {e}")
            self.connection = None
            return False
    
    def list_tables(self) -> List[str]:
        """List all user tables in the database.
        
        Returns:
            List of table names, excluding system tables
            
        Raises:
            RuntimeError: If not connected to database
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        try:
            # Use JDBC metadata to get tables (more reliable than INFORMATION_SCHEMA)
            meta = self.connection.jconn.getMetaData()
            tables_rs = meta.getTables(None, None, '%', ['TABLE'])
            
            tables = []
            while tables_rs.next():
                table_name = tables_rs.getString('TABLE_NAME')
                # Skip system tables
                if not table_name.startswith('MSys') and not table_name.startswith('~'):
                    tables.append(table_name)
            
            self.logger.info(f"UCanAccess found {len(tables)} user tables")
            self.logger.debug(f"Tables: {tables}")
            
            return sorted(tables)
            
        except Exception as e:
            self.logger.error(f"Error listing tables with UCanAccess: {e}")
            return []
    
    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read table data using SQL query.
        
        Args:
            table_name: Name of table to read
            
        Returns:
            DataFrame containing table data
            
        Raises:
            RuntimeError: If not connected to database
            Exception: If table cannot be read
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        try:
            # Use bracket notation for table names with spaces
            # This handles tables like "Order Details", "Employee Privileges"
            query = f"SELECT * FROM [{table_name}]"
            
            # Read data using pandas
            df = pd.read_sql(query, self.connection)
            
            self.logger.debug(f"UCanAccess read {len(df)} records from {table_name}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading table {table_name} with UCanAccess: {e}")
            raise
    
    def close(self):
        """Close database connection and cleanup resources."""
        if self.connection:
            try:
                self.connection.close()
                self.logger.debug("UCanAccess connection closed")
            except Exception as e:
                self.logger.warning(f"Error closing UCanAccess connection: {e}")
            finally:
                self.connection = None
                self.db_path = None
    
    def _check_java(self) -> bool:
        """Check if Java runtime is available.
        
        Returns:
            True if Java is available, False otherwise
        """
        try:
            result = subprocess.run(
                ['java', '-version'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract Java version for logging
                version_line = result.stderr.split('\n')[0] if result.stderr else "Unknown"
                self.logger.debug(f"Java available: {version_line}")
                return True
            else:
                self.logger.debug("Java command failed")
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            self.logger.debug(f"Java check failed: {e}")
            return False
    
    def _check_jaydebeapi(self) -> bool:
        """Check if JayDeBeApi is available.
        
        Returns:
            True if JayDeBeApi can be imported, False otherwise
        """
        try:
            import jaydebeapi
            self.logger.debug("JayDeBeApi available")
            return True
        except ImportError:
            self.logger.debug("JayDeBeApi not available")
            return False
    
    def get_connection_info(self) -> dict:
        """Get information about the current connection.
        
        Returns:
            Dictionary with connection information
        """
        return {
            'backend': 'UCanAccess',
            'connected': self.connection is not None,
            'db_path': self.db_path,
            'jar_info': self.jar_manager.get_jar_info()
        }