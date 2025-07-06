"""pyodbc backend for Windows-native Access database connectivity."""

import logging
import platform
from typing import List

import pandas as pd

from .base import DatabaseBackend


class PyODBCBackend(DatabaseBackend):
    """pyodbc backend for Windows-native Access database support."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.db_path = None
        self._pyodbc = None

    def is_available(self) -> bool:
        """Check if pyodbc backend is available.

        Checks:
        1. Running on Windows platform
        2. pyodbc package availability
        3. Microsoft Access ODBC drivers

        Returns:
            True if all dependencies are available, False otherwise
        """
        try:
            # Only available on Windows
            if platform.system() != "Windows":
                self.logger.debug("pyodbc backend only available on Windows")
                return False

            # Check pyodbc package
            if not self._check_pyodbc():
                self.logger.debug("pyodbc package not available")
                return False

            # Check for Access ODBC drivers
            if not self._check_access_drivers():
                self.logger.debug("Access ODBC drivers not available")
                return False

            return True

        except Exception as e:
            self.logger.debug(f"pyodbc availability check failed: {e}")
            return False

    def connect(self, db_path: str, password: str = None) -> bool:
        """Connect to Access database using pyodbc.

        Args:
            db_path: Path to Access database file
            password: Optional password for protected databases

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Ensure backend is available
            if not self.is_available():
                self.logger.error("pyodbc backend not available")
                return False

            # Import pyodbc (should be available after is_available check)
            import pyodbc

            self._pyodbc = pyodbc

            # Disable connection pooling for better reliability
            pyodbc.pooling = False

            # Build ODBC connection string
            conn_str = (
                f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};"
                f"DBQ={db_path};"
            )

            # Add password if provided
            if password:
                conn_str += f"PWD={password};"

            # Additional connection options for reliability
            conn_str += "ExtendedAnsiSQL=1;"  # Better SQL support

            # Establish ODBC connection
            self.connection = pyodbc.connect(conn_str)
            self.db_path = db_path

            # Test connection with a simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()

            self.logger.info(f"pyodbc connected to: {db_path}")
            return True

        except Exception as e:
            self.logger.error(f"pyodbc connection failed: {e}")
            self.connection = None
            return False

    def list_tables(self) -> List[str]:
        """List all user tables using pyodbc metadata.

        Returns:
            List of table names, excluding system tables

        Raises:
            RuntimeError: If not connected to database
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        try:
            cursor = self.connection.cursor()

            # Get table names from ODBC metadata
            tables = []

            # Use ODBC metadata to get tables
            for table_info in cursor.tables(tableType="TABLE"):
                table_name = table_info.table_name

                # Filter out system tables and temporary objects
                if (
                    not table_name.startswith("MSys")
                    and not table_name.startswith("~")
                    and not table_name.startswith("USys")
                ):
                    tables.append(table_name)

            cursor.close()

            self.logger.info(f"pyodbc found {len(tables)} user tables")
            self.logger.debug(f"Tables: {tables}")

            return sorted(tables)

        except Exception as e:
            self.logger.error(f"Error listing tables with pyodbc: {e}")
            return []

    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read table data using pyodbc.

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

            # Read data using pandas with pyodbc connection
            df = pd.read_sql(query, self.connection)

            self.logger.debug(f"pyodbc read {len(df)} records from {table_name}")
            return df

        except Exception as e:
            self.logger.error(f"Error reading table {table_name} with pyodbc: {e}")
            raise

    def close(self):
        """Close database connection and cleanup resources."""
        if self.connection:
            try:
                self.connection.close()
                self.logger.debug("pyodbc connection closed")
            except Exception as e:
                self.logger.warning(f"Error closing pyodbc connection: {e}")
            finally:
                self.connection = None
                self.db_path = None

    def _check_pyodbc(self) -> bool:
        """Check if pyodbc package is available.

        Returns:
            True if pyodbc can be imported, False otherwise
        """
        try:
            import pyodbc  # noqa: F401

            self.logger.debug("pyodbc package available")
            return True
        except ImportError:
            self.logger.debug("pyodbc package not available")
            return False

    def _check_access_drivers(self) -> bool:
        """Check if Microsoft Access ODBC drivers are available.

        Returns:
            True if Access drivers found, False otherwise
        """
        try:
            import pyodbc

            # Get list of available ODBC drivers
            drivers = pyodbc.drivers()

            # Look for Microsoft Access drivers
            access_drivers = [d for d in drivers if "Microsoft Access Driver" in d]

            if access_drivers:
                self.logger.debug(f"Found Access drivers: {access_drivers}")
                return True
            else:
                self.logger.debug("No Access ODBC drivers found")
                return False

        except Exception as e:
            self.logger.debug(f"Error checking Access drivers: {e}")
            return False

    def get_connection_info(self) -> dict:
        """Get information about the current connection.

        Returns:
            Dictionary with connection information
        """
        info = {
            "backend": "pyodbc",
            "connected": self.connection is not None,
            "db_path": self.db_path,
            "platform": platform.system(),
        }

        # Add driver information if available
        if self._check_pyodbc():
            try:
                import pyodbc

                drivers = [
                    d for d in pyodbc.drivers() if "Microsoft Access Driver" in d
                ]
                info["available_drivers"] = drivers
            except Exception:
                info["available_drivers"] = []

        return info
