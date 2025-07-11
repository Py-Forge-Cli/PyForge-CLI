"""Multi-backend MDB reader with UCanAccess, subprocess, and pyodbc support."""

import logging
from typing import List, Optional

import pandas as pd

from ..backends.pyodbc_backend import PyODBCBackend
from ..backends.ucanaccess_backend import UCanAccessBackend
from ..backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend


class DualBackendMDBReader:
    """MDB reader with UCanAccess primary and pyodbc fallback support."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.backend = None
        self.backend_name = None
        self._connection_info = {}

    def connect(self, db_path: str, password: str = None) -> bool:
        """Connect to Access database using best available backend.

        Connection strategy:
        1. Try UCanAccess first (cross-platform, handles space-named tables)
        2. Try UCanAccess subprocess if JPype fails (Databricks Serverless compatible)
        3. Fallback to pyodbc if all else fails (Windows only, high performance)

        Args:
            db_path: Path to Access database file
            password: Optional password for protected databases

        Returns:
            True if connection successful with any backend, False otherwise

        Raises:
            RuntimeError: If no backends are available or all connections fail
        """
        self.logger.info(f"Connecting to Access database: {db_path}")

        # Store connection attempts for detailed error reporting
        connection_attempts = []

        # Try UCanAccess first (cross-platform solution)
        ucanaccess = UCanAccessBackend()
        if ucanaccess.is_available():
            self.logger.info("Attempting UCanAccess connection...")

            try:
                if ucanaccess.connect(db_path, password):
                    self.backend = ucanaccess
                    self.backend_name = "UCanAccess"
                    self._connection_info = ucanaccess.get_connection_info()

                    self.logger.info("✓ Connected using UCanAccess (cross-platform)")
                    return True
                else:
                    connection_attempts.append(("UCanAccess", "Connection failed"))
                    self.logger.warning(
                        "UCanAccess connection failed, trying fallback..."
                    )

            except Exception as e:
                connection_attempts.append(("UCanAccess", f"Exception: {e}"))
                self.logger.warning(f"UCanAccess connection exception: {e}")

                # Check if it's a JPype error
                if "org.jpype.jar" in str(e) or "JPype" in str(e):
                    self.logger.info(
                        "JPype error detected, will try subprocess backend"
                    )
        else:
            connection_attempts.append(("UCanAccess", "Backend not available"))
            self.logger.info("UCanAccess not available, trying fallback...")

        # Try UCanAccess subprocess backend (for Databricks Serverless)
        ucanaccess_subprocess = UCanAccessSubprocessBackend()
        if ucanaccess_subprocess.is_available():
            self.logger.info(
                "Attempting UCanAccess subprocess connection (Databricks Serverless compatible)..."
            )

            try:
                if ucanaccess_subprocess.connect(db_path, password):
                    self.backend = ucanaccess_subprocess
                    self.backend_name = "UCanAccess-Subprocess"
                    self._connection_info = ucanaccess_subprocess.get_connection_info()

                    self.logger.info(
                        "✓ Connected using UCanAccess subprocess (Databricks Serverless compatible)"
                    )
                    return True
                else:
                    connection_attempts.append(
                        ("UCanAccess-Subprocess", "Connection failed")
                    )
                    self.logger.warning(
                        "UCanAccess subprocess connection failed, trying next fallback..."
                    )

            except Exception as e:
                connection_attempts.append(("UCanAccess-Subprocess", f"Exception: {e}"))
                self.logger.warning(f"UCanAccess subprocess connection exception: {e}")
        else:
            connection_attempts.append(
                ("UCanAccess-Subprocess", "Backend not available")
            )
            self.logger.info(
                "UCanAccess subprocess not available, trying next fallback..."
            )

        # Fallback to pyodbc (Windows-native solution)
        pyodbc_backend = PyODBCBackend()
        if pyodbc_backend.is_available():
            self.logger.info("Attempting pyodbc connection...")

            try:
                if pyodbc_backend.connect(db_path, password):
                    self.backend = pyodbc_backend
                    self.backend_name = "pyodbc"
                    self._connection_info = pyodbc_backend.get_connection_info()

                    self.logger.info("✓ Connected using pyodbc (Windows native)")
                    return True
                else:
                    connection_attempts.append(("pyodbc", "Connection failed"))
                    self.logger.error("pyodbc connection also failed")

            except Exception as e:
                connection_attempts.append(("pyodbc", f"Exception: {e}"))
                self.logger.error(f"pyodbc connection exception: {e}")
        else:
            connection_attempts.append(("pyodbc", "Backend not available"))
            self.logger.info("pyodbc not available")

        # No backends were able to connect
        self._raise_connection_error(connection_attempts, db_path)

    def _raise_connection_error(self, attempts: List[tuple], db_path: str):
        """Raise comprehensive connection error with helpful suggestions.

        Args:
            attempts: List of (backend_name, error_message) tuples
            db_path: Path to database file that failed to connect
        """
        error_msg = f"Failed to connect to Access database: {db_path}\n\n"

        # List all attempts
        error_msg += "Connection attempts:\n"
        for backend, error in attempts:
            error_msg += f"  • {backend}: {error}\n"

        # Provide helpful suggestions
        error_msg += "\nSuggestions:\n"

        # Check if any backends were available
        available_backends = [
            name for name, error in attempts if "not available" not in error
        ]
        if not available_backends:
            error_msg += "  • No database backends are available!\n"

            # Check if we're in Databricks Serverless
            import os

            if (
                os.environ.get("IS_SERVERLESS", "").upper() == "TRUE"
                or os.environ.get("SPARK_CONNECT_MODE_ENABLED") == "1"
            ):
                error_msg += "  • Environment: Databricks Serverless detected\n"
                error_msg += "  • The subprocess backend should be available but may have issues with Java detection\n"
                error_msg += "  • Check notebook logs for detailed error messages\n"
            else:
                error_msg += "  • For cross-platform support: Install Java and run 'pip install jaydebeapi jpype1'\n"
                error_msg += (
                    "  • For Windows: Install pyodbc with 'pip install pyodbc'\n"
                )
        else:
            error_msg += "  • Check if the database file exists and is not corrupted\n"
            error_msg += "  • Verify the database is not password-protected (or provide correct password)\n"
            error_msg += (
                "  • Ensure the database is not currently open in Microsoft Access\n"
            )

            if any("UCanAccess" in name for name, _ in attempts):
                error_msg += "  • For UCanAccess issues: Ensure Java 8+ is installed\n"

                # Check for JPype errors
                jpype_errors = [
                    error for name, error in attempts if "jpype" in error.lower()
                ]
                if jpype_errors:
                    error_msg += "  • For JPype errors in Databricks Serverless: The subprocess backend should work\n"

            if any("UCanAccess-Subprocess" in name for name, _ in attempts):
                error_msg += "  • For subprocess issues: Check Java installation and file permissions\n"

            if any("pyodbc" in name for name, _ in attempts):
                error_msg += (
                    "  • For pyodbc issues: Install Microsoft Access Database Engine\n"
                )

        raise RuntimeError(error_msg)

    def list_tables(self) -> List[str]:
        """List all readable tables using the active backend.

        Returns:
            List of table names, excluding system tables

        Raises:
            RuntimeError: If not connected to database
        """
        if not self.backend:
            raise RuntimeError("Not connected to database")

        try:
            tables = self.backend.list_tables()
            self.logger.info(f"Found {len(tables)} tables using {self.backend_name}")

            # Log tables for debugging (helpful for space-named table verification)
            if tables:
                self.logger.debug(f"Available tables: {tables}")

                # Count tables with spaces (these were previously failing)
                space_tables = [t for t in tables if " " in t]
                if space_tables:
                    self.logger.info(
                        f"Found {len(space_tables)} tables with spaces in names: {space_tables}"
                    )

            return tables

        except Exception as e:
            self.logger.error(f"Error listing tables with {self.backend_name}: {e}")
            raise

    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read table data using the active backend.

        Args:
            table_name: Name of table to read

        Returns:
            DataFrame containing table data

        Raises:
            RuntimeError: If not connected to database
            Exception: If table cannot be read
        """
        if not self.backend:
            raise RuntimeError("Not connected to database")

        try:
            df = self.backend.read_table(table_name)

            self.logger.debug(
                f"Read {len(df)} records, {len(df.columns)} columns "
                f"from '{table_name}' using {self.backend_name}"
            )

            return df

        except Exception as e:
            self.logger.error(
                f"Error reading table '{table_name}' with {self.backend_name}: {e}"
            )
            raise

    def get_active_backend(self) -> Optional[str]:
        """Get name of the currently active backend.

        Returns:
            Backend name ('UCanAccess' or 'pyodbc') or None if not connected
        """
        return self.backend_name

    def get_connection_info(self) -> dict:
        """Get comprehensive connection information.

        Returns:
            Dictionary with connection details
        """
        base_info = {
            "connected": self.backend is not None,
            "active_backend": self.backend_name,
        }

        if self._connection_info:
            base_info.update(self._connection_info)

        return base_info

    def close(self):
        """Close database connection and cleanup resources."""
        if self.backend:
            try:
                self.backend.close()
                self.logger.debug(f"Closed {self.backend_name} connection")
            except Exception as e:
                self.logger.warning(
                    f"Error closing {self.backend_name} connection: {e}"
                )
            finally:
                self.backend = None
                self.backend_name = None
                self._connection_info = {}

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.close()

    def __del__(self):
        """Destructor with automatic cleanup."""
        try:
            self.close()
        except Exception:
            pass  # Ignore cleanup errors during destruction
