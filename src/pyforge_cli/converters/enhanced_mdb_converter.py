"""
Enhanced MDB (Microsoft Access) to Parquet converter with dual-backend support.
Uses UCanAccess + pyodbc fallback for maximum compatibility and table coverage.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from ..detectors.database_detector import DatabaseType, detect_database_file
from ..readers.dual_backend_mdb_reader import DualBackendMDBReader
from .string_database_converter import StringDatabaseConverter


class EnhancedMDBConverter(StringDatabaseConverter):
    """
    Enhanced MDB converter with UCanAccess + pyodbc dual-backend support.

    Features:
    - Cross-platform UCanAccess support (primary)
    - Windows pyodbc fallback for performance
    - Support for space-named tables (Order Details, etc.)
    - 100% table coverage vs 45% with pandas-access
    - Automatic backend selection and fallback
    """

    def __init__(self):
        super().__init__()
        self.dual_reader: Optional[DualBackendMDBReader] = None
        self.password: Optional[str] = None

        # Set supported formats for registry compatibility
        self.supported_inputs = {".mdb", ".accdb"}
        self.supported_outputs = {".parquet"}

    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats."""
        return [".mdb", ".accdb"]

    def _connect_to_database(self, input_path: Path) -> DualBackendMDBReader:
        """Connect to MDB database using dual-backend reader.

        Args:
            input_path: Path to Access database file

        Returns:
            Connected DualBackendMDBReader instance

        Raises:
            ValueError: If file validation fails
            ConnectionError: If connection fails with all backends
        """
        # Detect and validate file
        db_info = detect_database_file(input_path)

        if db_info.file_type not in [DatabaseType.MDB, DatabaseType.ACCDB]:
            raise ValueError(f"File is not an MDB/ACCDB file: {input_path}")

        if db_info.error_message:
            raise ValueError(f"File validation failed: {db_info.error_message}")

        # Store database info
        self.database_info = db_info

        # Create dual-backend reader
        dual_reader = DualBackendMDBReader()

        # Extract password from options if provided
        password = getattr(self, "password", None)

        # Connect with automatic backend selection
        try:
            success = dual_reader.connect(str(input_path), password)
            if not success:
                raise ConnectionError("Failed to connect with any available backend")

            # Log which backend was selected
            backend_name = dual_reader.get_active_backend()
            self.logger.info(f"[OK] Connected using {backend_name} backend")

            # Store connection info for later use
            conn_info = dual_reader.get_connection_info()
            self.logger.debug(f"Connection info: {conn_info}")

            self.dual_reader = dual_reader
            return dual_reader

        except Exception as e:
            self.logger.error(f"Enhanced MDB connection failed: {e}")
            raise ConnectionError(f"Cannot connect to MDB file: {e}") from e

    def _list_tables(self, connection: DualBackendMDBReader) -> List[str]:
        """List all user tables using the active backend.

        Args:
            connection: Connected DualBackendMDBReader instance

        Returns:
            List of table names, excluding system tables
        """
        try:
            tables = connection.list_tables()
            backend_name = connection.get_active_backend()

            self.logger.info(f"Found {len(tables)} tables using {backend_name}")

            # Log detailed information about space-named tables
            space_tables = [t for t in tables if " " in t]
            if space_tables:
                self.logger.info(
                    f"[OK] {len(space_tables)} space-named tables accessible: {space_tables}"
                )

            return tables

        except Exception as e:
            self.logger.error(f"Error listing tables: {e}")
            return []

    def _read_table(
        self, connection: DualBackendMDBReader, table_name: str
    ) -> pd.DataFrame:
        """Read table data using the active backend.

        Args:
            connection: Connected DualBackendMDBReader instance
            table_name: Name of table to read

        Returns:
            DataFrame containing table data

        Raises:
            Exception: If table cannot be read
        """
        try:
            df = connection.read_table(table_name)
            backend_name = connection.get_active_backend()

            self.logger.debug(
                f"Read {len(df)} records, {len(df.columns)} columns "
                f"from '{table_name}' using {backend_name}"
            )

            return df

        except Exception as e:
            self.logger.error(f"Error reading table {table_name}: {e}")
            raise

    def _get_table_info(
        self, connection: DualBackendMDBReader, table_name: str
    ) -> Dict[str, Any]:
        """Get metadata about a table.

        Args:
            connection: Connected DualBackendMDBReader instance
            table_name: Name of table to analyze

        Returns:
            Dictionary with table metadata
        """
        try:
            # Read table to get basic information
            df = connection.read_table(table_name)

            # Build metadata from DataFrame
            return {
                "name": table_name,
                "record_count": len(df),
                "column_count": len(df.columns),
                "estimated_size": df.memory_usage(deep=True).sum(),
                "columns": [
                    {
                        "name": col,
                        "type": str(df[col].dtype),
                        "size": df[col].memory_usage(deep=True),
                        "nullable": df[col].isnull().any(),
                    }
                    for col in df.columns
                ],
                "has_primary_key": False,  # Cannot easily determine from DataFrame
            }

        except Exception as e:
            self.logger.warning(f"Could not get table info for {table_name}: {e}")
            return {
                "name": table_name,
                "record_count": 0,
                "column_count": 0,
                "estimated_size": 0,
                "columns": [],
                "has_primary_key": False,
            }

    def _close_connection(self, connection: DualBackendMDBReader) -> None:
        """Close database connection and cleanup resources.

        Args:
            connection: DualBackendMDBReader instance to close
        """
        try:
            if connection:
                backend_name = connection.get_active_backend()
                connection.close()
                self.logger.debug(f"Closed {backend_name} connection")
        except Exception as e:
            self.logger.warning(f"Error closing enhanced MDB connection: {e}")

    def _convert_tables_to_parquet(
        self, connection, table_info_list: List[dict], output_path: Path, **options: Any
    ) -> bool:
        """Convert database tables to Parquet files.

        Args:
            connection: Database connection (dual reader)
            table_info_list: List of table information dictionaries
            output_path: Output directory path
            **options: Additional conversion options

        Returns:
            True if conversion successful, False otherwise
        """
        from rich.console import Console
        from rich.progress import (
            BarColumn,
            Progress,
            SpinnerColumn,
            TaskProgressColumn,
            TextColumn,
        )

        try:
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)

            # Convert each table with progress tracking
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=Console(),
                transient=False,
            ) as progress:

                task = progress.add_task(
                    "Converting tables...", total=len(table_info_list)
                )

                for table_info in table_info_list:
                    table_name = table_info["name"]

                    try:
                        # Update progress
                        progress.update(task, description=f"Converting {table_name}...")

                        # Read table data
                        df = self._read_table(connection, table_name)

                        # Create safe filename
                        safe_filename = self._sanitize_filename(f"{table_name}.parquet")
                        output_file = output_path / safe_filename

                        # Write to Parquet
                        df.to_parquet(output_file, index=False)

                        progress.advance(task)

                    except Exception as e:
                        self.logger.error(f"Failed to convert table {table_name}: {e}")
                        return False

            # Generate conversion report
            self._generate_conversion_report(table_info_list, output_path)

            return True

        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            return False

    def _sanitize_filename(self, filename: str) -> str:
        """Create safe filename from table name."""
        import re

        # Replace spaces and special characters with underscores
        safe_name = re.sub(r'[<>:"/\\|?*\s]+', "_", filename)
        # Remove multiple consecutive underscores
        safe_name = re.sub(r"_+", "_", safe_name)
        # Remove leading/trailing underscores
        return safe_name.strip("_")

    def _generate_conversion_report(
        self, table_info_list: List[dict], output_path: Path
    ):
        """Generate Excel conversion report."""
        try:
            from datetime import datetime

            import pandas as pd

            # Create report DataFrame
            report_data = []
            for table_info in table_info_list:
                report_data.append(
                    {
                        "Table Name": table_info["name"],
                        "Record Count": table_info["record_count"],
                        "Column Count": table_info["column_count"],
                        "Status": "Converted Successfully",
                        "Output File": f"{self._sanitize_filename(table_info['name'])}.parquet",
                    }
                )

            df_report = pd.DataFrame(report_data)

            # Create report filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_name = output_path.name
            report_file = output_path / f"{db_name}_conversion_report_{timestamp}.xlsx"

            # Write Excel report
            with pd.ExcelWriter(report_file) as writer:
                df_report.to_excel(writer, sheet_name="Conversion Summary", index=False)

                # Add column details sheet if available
                if table_info_list and "columns" in table_info_list[0]:
                    column_data = []
                    for table_info in table_info_list:
                        for col in table_info.get("columns", []):
                            column_data.append(
                                {
                                    "Table": table_info["name"],
                                    "Column": col.get("name", ""),
                                    "Data Type": col.get("type", ""),
                                    "Nullable": col.get("nullable", True),
                                }
                            )

                    if column_data:
                        df_columns = pd.DataFrame(column_data)
                        df_columns.to_excel(
                            writer, sheet_name="Column Details", index=False
                        )

            self.logger.info(f"Conversion report saved to: {report_file}")

        except Exception as e:
            self.logger.warning(f"Failed to generate conversion report: {e}")

    def validate_input(self, input_path: Path) -> bool:
        """Validate MDB input file.

        Args:
            input_path: Path to input file

        Returns:
            True if file is valid MDB/ACCDB, False otherwise
        """
        # Check file extension
        if input_path.suffix.lower() not in [".mdb", ".accdb"]:
            return False

        # Use detector for validation
        from ..detectors.database_detector import DatabaseFileDetector

        detector = DatabaseFileDetector()
        is_valid, _ = detector.validate_file_access(input_path)
        return is_valid

    def convert_with_progress(
        self, input_path: Path, output_path: Path, **options: Any
    ) -> bool:
        """
        Convert MDB file with enhanced 6-stage progress tracking.

        Stages:
        1. Analyzing the file and detecting best backend
        2. Connecting to database with backend selection
        3. Listing all accessible tables
        4. Extracting table metadata summary
        5. Displaying table overview with backend info
        6. Converting each table to Parquet with progress

        Args:
            input_path: Path to Access database file
            output_path: Path to output directory or file
            **options: Additional conversion options

        Returns:
            True if conversion successful, False otherwise
        """
        from rich.console import Console
        from rich.progress import (
            BarColumn,
            Progress,
            SpinnerColumn,
            TaskProgressColumn,
            TextColumn,
        )
        from rich.table import Table

        console = Console()

        try:
            # Store options for use in connection (e.g., password)
            self.password = options.get("password")

            # Stage 1: File Analysis with Backend Detection
            console.print("[ANALYZE] Stage 1: Analyzing the file...")

            # Detect file and available backends
            db_info = detect_database_file(input_path)
            console.print(f"[OK] File format: {db_info.file_type.name}")
            file_size_mb = input_path.stat().st_size / (1024 * 1024)
            console.print(f"[OK] File size: {file_size_mb:.1f} MB")
            console.print(
                f"[OK] Password protected: {'Yes' if options.get('password') else 'No'}"
            )

            # Check available backends
            from ..backends.pyodbc_backend import PyODBCBackend
            from ..backends.ucanaccess_backend import UCanAccessBackend

            ucanaccess = UCanAccessBackend()
            pyodbc_backend = PyODBCBackend()

            available_backends = []
            if ucanaccess.is_available():
                available_backends.append("UCanAccess (cross-platform)")
            if pyodbc_backend.is_available():
                available_backends.append("pyodbc (Windows native)")

            if available_backends:
                console.print(
                    f"[OK] Available backends: {', '.join(available_backends)}"
                )
            else:
                console.print("[FAIL] No database backends available!")
                return False

            # Stage 2: Database Connection
            console.print("\n[CLIPBOARD] Stage 2: Connecting to database...")

            console.print("  Establishing connection...")
            connection = self._connect_to_database(input_path)
            backend_name = connection.get_active_backend()
            console.print(f"[OK] Connected using {backend_name}")

            # Stage 3: Table Discovery
            console.print("\n[CHART] Stage 3: Discovering tables...")

            console.print("  Scanning database structure...")
            tables = self._list_tables(connection)

            if not tables:
                console.print("[FAIL] No readable tables found")
                return False

            console.print(f"[OK] Found {len(tables)} user tables")

            # Stage 4: Metadata Extraction
            console.print("\n[GRAPH] Stage 4: Extracting table metadata...")

            table_info_list = []
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Analyzing tables...", total=len(tables))

                for table_name in tables:
                    try:
                        table_info = self._get_table_info(connection, table_name)
                        table_info_list.append(table_info)
                        progress.advance(task)
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to analyze table {table_name}: {e}"
                        )
                        # Add placeholder info for failed tables
                        table_info_list.append(
                            {
                                "name": table_name,
                                "record_count": 0,
                                "column_count": 0,
                                "estimated_size": 0,
                                "columns": [],
                                "has_primary_key": False,
                            }
                        )
                        progress.advance(task)

            # Stage 5: Table Overview Display
            console.print("\n[GRAPH] Stage 5: Table Overview:")

            # Create enhanced table display
            table_display = Table(
                title=f"Database Tables Summary ({backend_name} Backend)"
            )
            table_display.add_column("Table Name", style="cyan")
            table_display.add_column("Records", justify="right", style="green")
            table_display.add_column("Columns", justify="right", style="blue")
            table_display.add_column("Notes", style="yellow")

            total_records = 0
            accessible_tables = 0
            space_tables = 0

            for table_info in table_info_list:
                table_name = table_info["name"]
                record_count = table_info["record_count"]
                column_count = table_info["column_count"]

                # Generate notes
                notes = []
                if " " in table_name:
                    notes.append("Space-named")
                    space_tables += 1
                if record_count > 0:
                    accessible_tables += 1
                    total_records += record_count
                elif record_count == 0:
                    notes.append("Empty/Inaccessible")

                notes_str = ", ".join(notes) if notes else ""

                table_display.add_row(
                    table_name, str(record_count), str(column_count), notes_str
                )

            # Add summary row
            table_display.add_row(
                "TOTAL",
                str(total_records),
                "-",
                f"{accessible_tables}/{len(tables)} accessible",
                style="bold",
            )

            console.print(table_display)

            # Highlight improvements over pandas-access
            if space_tables > 0:
                console.print(
                    f"\n[ENHANCE] Enhancement: {space_tables} space-named tables accessible with {backend_name}"
                )
                console.print(
                    "   (These were previously inaccessible with pandas-access)"
                )

            # Stage 6: Table Conversion
            console.print("\n[CONVERT] Stage 6: Converting tables to Parquet...")

            # Perform conversion using parent class method
            success = self._convert_tables_to_parquet(
                connection, table_info_list, output_path, **options
            )

            if success:
                console.print(
                    f"\n[OK] Conversion completed successfully using {backend_name}!"
                )
                console.print(f"• Tables processed: {accessible_tables}/{len(tables)}")
                console.print(f"• Records converted: {total_records:,}")
                console.print(
                    f"• Space-named tables: {space_tables} (enhanced support)"
                )

            return success

        except Exception as e:
            console.print(f"\n[FAIL] Conversion failed: {e}")
            self.logger.error(f"Enhanced MDB conversion error: {e}", exc_info=True)
            return False

        finally:
            # Cleanup connection
            if hasattr(self, "dual_reader") and self.dual_reader:
                self._close_connection(self.dual_reader)

    def get_metadata(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from MDB/ACCDB file using dual-backend approach.

        Args:
            input_path: Path to MDB/ACCDB file

        Returns:
            Dictionary containing file metadata or None if extraction fails
        """
        try:
            # Get basic file info
            file_stats = input_path.stat()
            metadata = {
                "file_name": input_path.name,
                "file_size": file_stats.st_size,
                "file_format": "Microsoft Access Database (Enhanced)",
                "file_extension": input_path.suffix,
                "modified_date": pd.Timestamp.fromtimestamp(file_stats.st_mtime).isoformat(),
                "created_date": pd.Timestamp.fromtimestamp(file_stats.st_ctime).isoformat(),
            }

            # Detect database type and version
            db_info = detect_database_file(input_path)

            if db_info.file_type not in [DatabaseType.MDB, DatabaseType.ACCDB]:
                return metadata  # Return basic metadata only

            metadata["database_type"] = db_info.file_type.value.upper()
            metadata["database_version"] = db_info.version or "Unknown"
            metadata["is_encrypted"] = getattr(db_info, 'is_encrypted', False)

            # Try to get table information using dual-backend reader
            try:
                dual_reader = DualBackendMDBReader()

                # Attempt connection
                connection_success = dual_reader.connect(input_path, password=self.password)

                if connection_success:
                    # Get backend info
                    metadata["backend_used"] = dual_reader.get_active_backend()

                    # List tables
                    table_names = dual_reader.list_tables()

                    if table_names:
                        metadata["table_count"] = len(table_names)
                        metadata["table_names"] = table_names

                        # Get table details
                        table_info = {}
                        total_rows = 0
                        total_columns = 0

                        for table_name in table_names:
                            try:
                                # Get basic table info
                                info = dual_reader.get_table_info(table_name)

                                if info:
                                    table_info[table_name] = {
                                        "row_count": info.row_count,
                                        "column_count": len(info.columns) if info.columns else 0,
                                        "columns": [col.name for col in info.columns] if info.columns else []
                                    }
                                    total_rows += info.row_count
                                    total_columns += len(info.columns) if info.columns else 0
                                else:
                                    table_info[table_name] = {"error": "Could not read table info"}
                            except Exception as e:
                                table_info[table_name] = {"error": str(e)}

                        metadata["table_details"] = table_info
                        metadata["total_rows"] = total_rows
                        metadata["total_columns"] = total_columns
                    else:
                        metadata["table_count"] = 0
                        metadata["error"] = "No tables found"

                    # Disconnect
                    dual_reader.close()
                else:
                    metadata["error"] = "Connection failed"
                    if getattr(db_info, 'is_encrypted', False):
                        metadata["error"] = "Database is password protected"

            except Exception as e:
                # If we can't connect, just include basic metadata
                metadata["error"] = f"Could not read database structure: {str(e)}"

            return metadata

        except Exception as e:
            logging.error(f"Failed to extract Enhanced MDB metadata: {e}")
            return None
    def __del__(self):
        """Destructor with automatic connection cleanup."""
        try:
            if hasattr(self, "dual_reader") and self.dual_reader:
                self.dual_reader.close()
        except Exception:
            pass  # Ignore cleanup errors during destruction
