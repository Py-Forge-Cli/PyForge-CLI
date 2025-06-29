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
        self._temp_file_path = None  # Track temporary files for cleanup
    
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
            
            # Handle Databricks Unity Catalog volume paths
            # Java/JDBC cannot directly access volumes - must copy to local storage first
            if db_path.startswith("/Volumes/"):
                self.logger.info(f"Detected Unity Catalog volume path: {db_path}")
                self.logger.info("Java/JDBC cannot access volumes directly - copying to local storage")
                
                # Create local temp file path
                import tempfile
                import shutil
                temp_dir = tempfile.gettempdir()
                file_name = os.path.basename(db_path)
                local_path = os.path.join(temp_dir, f"pyforge_{os.getpid()}_{file_name}")
                
                try:
                    # Copy from volume to local storage using shell command (not dbutils - JVM limitation)
                    copy_cmd = f"cp '{db_path}' '{local_path}'"
                    result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        self.logger.error(f"Failed to copy file from volume: {result.stderr}")
                        raise RuntimeError(f"Cannot copy {db_path} to local storage: {result.stderr}")
                    
                    self.db_path = local_path
                    self._temp_file_path = local_path  # Track for cleanup
                    self.logger.info(f"Successfully copied volume file to local storage: {local_path}")
                    
                except subprocess.TimeoutExpired:
                    self.logger.error(f"Timeout copying file from volume: {db_path}")
                    raise RuntimeError(f"Timeout copying {db_path} to local storage")
                except Exception as e:
                    self.logger.error(f"Error copying file from volume: {e}")
                    raise RuntimeError(f"Cannot access volume file {db_path}: {e}")
            else:
                self.db_path = os.path.abspath(db_path)
                self._temp_file_path = None  # No temp file created
                
            # Verify file exists at final path
            if not os.path.exists(self.db_path):
                self.logger.error(f"Database file not found at: {self.db_path}")
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
                
            # Get all required JAR paths for UCanAccess and dependencies
            jar_paths = self._get_all_jar_paths()
            
            # Build JDBC connection string
            conn_string = f"jdbc:ucanaccess://{self.db_path}"
            self.logger.debug(f"JDBC connection string: {conn_string}")
            
            # Configure for Databricks environment
            # Use memory mode to avoid file system write issues
            conn_string += ";memory=true"
            
            # Set writable temp directory for Databricks
            import tempfile
            temp_dir = tempfile.gettempdir()
            conn_string += f";tempDirPath={temp_dir}"
            
            # Disable features that require write access
            conn_string += ";immediatelyReleaseResources=true"
            conn_string += ";openExclusive=false"
            
            # Set up connection properties
            connection_props = ["", ""]  # [username, password]
            if password:
                connection_props = [password, ""]
            
            # Establish JDBC connection with all JAR dependencies
            self.connection = jaydebeapi.connect(
                "net.ucanaccess.jdbc.UcanaccessDriver",
                conn_string,
                connection_props,
                jar_paths
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
        
        # Clean up temporary file if it exists
        if self._temp_file_path and os.path.exists(self._temp_file_path):
            try:
                os.remove(self._temp_file_path)
                self.logger.debug(f"Cleaned up temporary file: {self._temp_file_path}")
            except Exception as e:
                self.logger.warning(f"Error cleaning up temporary file {self._temp_file_path}: {e}")
            finally:
                self._temp_file_path = None
    
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
    
    def _get_all_jar_paths(self) -> List[str]:
        """Get paths to all required JAR files for UCanAccess.
        
        Returns:
            List of absolute paths to JAR files
        """
        jar_dir = self.jar_manager.bundled_jar_dir
        jar_paths = []
        
        # Required JAR files for UCanAccess 4.0.4
        required_jars = [
            'ucanaccess-4.0.4.jar',
            'commons-lang3-3.8.1.jar', 
            'commons-logging-1.2.jar',
            'hsqldb-2.5.0.jar',
            'jackcess-3.0.1.jar'
        ]
        
        for jar_name in required_jars:
            jar_path = jar_dir / jar_name
            if jar_path.exists():
                jar_paths.append(str(jar_path))
                self.logger.debug(f"Added JAR: {jar_path}")
            else:
                self.logger.warning(f"Required JAR not found: {jar_path}")
        
        if len(jar_paths) != len(required_jars):
            self.logger.warning(f"Missing some required JARs. Expected {len(required_jars)}, found {len(jar_paths)}")
        
        return jar_paths
    
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