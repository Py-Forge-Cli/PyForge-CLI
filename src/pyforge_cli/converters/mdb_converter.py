"""
MDB (Microsoft Access) to Parquet converter with string-only output.
Implements the complete conversion pipeline for Phase 1.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from ..detectors.database_detector import DatabaseType, detect_database_file
from ..readers.mdb_reader import MDBTableDiscovery
from .string_database_converter import StringDatabaseConverter


class MDBConverter(StringDatabaseConverter):
    """
    Converts Microsoft Access (MDB/ACCDB) files to Parquet with string-only output.
    Implements Phase 1 requirements with 6-stage progress tracking.
    """

    def __init__(self):
        super().__init__()
        self.discovery: Optional[MDBTableDiscovery] = None
        self.password: Optional[str] = None

        # Set supported formats for registry compatibility
        self.supported_inputs = {".mdb", ".accdb"}
        self.supported_outputs = {".parquet"}

    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats"""
        return [".mdb", ".accdb"]

    def _connect_to_database(self, input_path: Path) -> MDBTableDiscovery:
        """Connect to MDB database and return discovery object"""
        # Detect and validate file
        db_info = detect_database_file(input_path)

        if db_info.file_type not in [DatabaseType.MDB, DatabaseType.ACCDB]:
            raise ValueError(f"File is not an MDB/ACCDB file: {input_path}")

        if db_info.error_message:
            raise ValueError(f"File validation failed: {db_info.error_message}")

        # Store database info
        self.database_info = db_info

        # Create discovery object
        discovery = MDBTableDiscovery()

        # Connect with optional password
        try:
            success = discovery.connect(input_path, self.password)
            if not success:
                raise ConnectionError("Failed to connect to MDB file")
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise ConnectionError(f"Cannot connect to MDB file: {e}") from e

        self.discovery = discovery
        return discovery

    def _list_tables(self, connection: MDBTableDiscovery) -> List[str]:
        """List all user tables in the database"""
        try:
            tables = connection.list_tables(include_system=False)
            self.logger.info(f"Found {len(tables)} user tables: {tables}")
            return tables
        except Exception as e:
            self.logger.error(f"Error listing tables: {e}")
            return []

    def _read_table(
        self, connection: MDBTableDiscovery, table_name: str
    ) -> pd.DataFrame:
        """Read table data as DataFrame"""
        try:
            df = connection.read_table(table_name)
            self.logger.debug(f"Read {len(df)} records from table {table_name}")
            return df
        except Exception as e:
            self.logger.error(f"Error reading table {table_name}: {e}")
            raise

    def _get_table_info(
        self, connection: MDBTableDiscovery, table_name: str
    ) -> Dict[str, Any]:
        """Get metadata about a table"""
        try:
            table_info = connection.get_table_info(table_name)
            return {
                "name": table_info.name,
                "record_count": table_info.record_count,
                "column_count": table_info.column_count,
                "estimated_size": table_info.estimated_size,
                "columns": [
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "size": col.get("size", 0),
                        "nullable": col.get("nullable", True),
                    }
                    for col in table_info.columns
                ],
                "has_primary_key": table_info.has_primary_key,
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

    def _close_connection(self, connection: MDBTableDiscovery) -> None:
        """Close database connection"""
        try:
            connection.close()
        except Exception as e:
            self.logger.warning(f"Error closing MDB connection: {e}")

    def validate_input(self, input_path: Path) -> bool:
        """Validate MDB input file"""
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
        Convert MDB file with 6-stage progress tracking.

        Stages:
        1. Analyzing the file
        2. Listing all tables
        3. Found number-of-tables
        4. Extracting summary
        5. Show all tables with total records
        6. Extract each table to destination path with progress
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
            # Stage 1: Analyzing the file
            console.print(
                "[ANALYZE] [bold blue]Stage 1:[/bold blue] Analyzing the file..."
            )

            # Extract password from options
            self.password = options.get("password")

            # Validate and detect file
            db_info = detect_database_file(input_path)
            if db_info.error_message:
                console.print(f"[FAIL] [red]Error:[/red] {db_info.error_message}")
                return False

            console.print(f"[OK] File format: {db_info.version}")
            console.print(
                f"[OK] File size: {db_info.estimated_size / 1024 / 1024:.1f} MB"
            )
            console.print(
                f"[OK] Password protected: {'Yes' if db_info.is_password_protected else 'No'}"
            )

            # Stage 2: Listing all tables
            console.print(
                "\n[CLIPBOARD] [bold blue]Stage 2:[/bold blue] Listing all tables..."
            )

            connection = self._connect_to_database(input_path)

            try:
                tables = self._list_tables(connection)

                if not tables:
                    console.print(
                        "[WARN] [yellow]Warning:[/yellow] No user tables found in database"
                    )
                    return True

                # Stage 3: Found number of tables
                console.print(f"[OK] Found {len(tables)} user tables")

                # Stage 4: Extracting summary
                console.print(
                    "\n[CHART] [bold blue]Stage 3:[/bold blue] Extracting summary..."
                )

                # Get table info for all tables
                table_infos = []
                total_records = 0
                total_size = 0

                for table_name in tables:
                    info = self._get_table_info(connection, table_name)
                    table_infos.append(info)
                    total_records += info["record_count"]
                    total_size += info["estimated_size"]

                # Stage 5: Show table overview
                console.print(
                    "\n[GRAPH] [bold blue]Stage 4:[/bold blue] Table Overview:"
                )

                # Create summary table (without estimated size)
                summary_table = Table(title="Database Tables Summary")
                summary_table.add_column("Table Name", style="cyan")
                summary_table.add_column("Records", justify="right", style="green")
                summary_table.add_column("Columns", justify="right", style="blue")

                for info in table_infos:
                    summary_table.add_row(
                        info["name"],
                        f"{info['record_count']:,}",
                        str(info["column_count"]),
                    )

                # Add totals row
                summary_table.add_row(
                    "[bold]TOTAL[/bold]", f"[bold]{total_records:,}[/bold]", "-"
                )

                console.print(summary_table)

                # Stage 6: Convert tables
                console.print(
                    "\n[CONVERT] [bold blue]Stage 5:[/bold blue] Converting tables to Parquet..."
                )

                # Create output directory
                output_path.mkdir(parents=True, exist_ok=True)

                # Convert each table with progress
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:

                    overall_task = progress.add_task(
                        f"Converting {len(tables)} tables...", total=len(tables)
                    )

                    converted_files = []

                    for i, table_name in enumerate(tables):
                        # Update progress
                        progress.update(
                            overall_task,
                            description=f"[{i+1}/{len(tables)}] {table_name}",
                            completed=i,
                        )

                        try:
                            # Read table data
                            df = self._read_table(connection, table_name)

                            if df.empty:
                                console.print(
                                    f"[WARN] Table {table_name} is empty, skipping..."
                                )
                                continue

                            # Convert to strings
                            string_df = self.string_converter.convert_dataframe(df)

                            # Save as Parquet
                            output_file = output_path / f"{table_name}.parquet"
                            self._save_parquet(string_df, output_file, **options)

                            # Track statistics
                            self.conversion_stats.append(self.string_converter.stats)

                            # Record successful conversion
                            record_count = len(string_df)
                            converted_files.append(
                                {
                                    "table": table_name,
                                    "records": record_count,
                                    "file": output_file,
                                    "size_mb": output_file.stat().st_size / 1024 / 1024,
                                }
                            )

                            console.print(
                                f"[OK] {table_name}: {record_count:,} records → {output_file.name}"
                            )

                            # Memory cleanup for large datasets
                            del df
                            del string_df
                            import gc

                            gc.collect()

                        except Exception as e:
                            console.print(f"[FAIL] Failed to convert {table_name}: {e}")
                            continue

                    # Complete progress
                    progress.update(overall_task, completed=len(tables))

                # Stage 6: Final summary and Excel report generation
                if converted_files:
                    console.print(
                        "\n[DOCUMENT] [bold blue]Stage 6:[/bold blue] Conversion Summary:"
                    )

                    total_converted_records = sum(f["records"] for f in converted_files)
                    total_output_size = sum(f["size_mb"] for f in converted_files)

                    console.print(
                        "[OK] [green]Conversion completed successfully![/green]"
                    )
                    console.print(f"• Files created: {len(converted_files)}")
                    console.print(f"• Records converted: {total_converted_records:,}")
                    console.print(f"• Output size: {total_output_size:.1f} MB")
                    console.print(f"• Output directory: {output_path}")

                    # List output files
                    console.print("\nOutput files:")
                    for file_info in converted_files:
                        console.print(
                            f"  • {file_info['file'].name} ({file_info['records']:,} records)"
                        )

                    # Generate Excel report
                    console.print(
                        "\n[CHART] [bold blue]Generating Excel Report...[/bold blue]"
                    )
                    try:
                        excel_path = self._generate_excel_report(
                            input_path,
                            output_path,
                            table_infos,
                            converted_files,
                            connection,
                        )
                        console.print(f"[OK] Excel report created: {excel_path.name}")
                    except Exception as e:
                        console.print(
                            f"[WARN] [yellow]Warning: Could not generate Excel report: {e}[/yellow]"
                        )
                else:
                    console.print(
                        "[WARN] [yellow]No tables were successfully converted[/yellow]"
                    )

                return len(converted_files) > 0

            finally:
                self._close_connection(connection)

        except Exception as e:
            console.print(f"[FAIL] [red]Conversion failed:[/red] {e}")
            self.logger.error(f"MDB conversion failed: {e}")
            return False

    def _generate_excel_report(
        self,
        input_path: Path,
        output_path: Path,
        table_infos: List[Dict[str, Any]],
        converted_files: List[Dict[str, Any]],
        connection: Any,
    ) -> Path:
        """
        Generate Excel report with summary and sample data from each table.

        Returns:
            Path to the generated Excel file
        """
        from datetime import datetime

        import pandas as pd

        # Create Excel file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"{input_path.stem}_conversion_report_{timestamp}.xlsx"
        excel_path = output_path / excel_filename

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            # 1. Summary Sheet
            summary_data = {
                "Property": [
                    "Source File",
                    "Conversion Date",
                    "Total Tables",
                    "Total Records",
                    "Output Directory",
                    "Conversion Status",
                ],
                "Value": [
                    str(input_path),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    len(converted_files),
                    sum(f["records"] for f in converted_files),
                    str(output_path),
                    "Completed Successfully",
                ],
            }

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            # Table details in summary
            table_summary_data = {
                "Table Name": [f["table"] for f in converted_files],
                "Records": [f["records"] for f in converted_files],
                "Output File": [f["file"].name for f in converted_files],
                "Size (MB)": [f["size_mb"] for f in converted_files],
            }

            table_summary_df = pd.DataFrame(table_summary_data)
            # Add table summary starting from row 10
            table_summary_df.to_excel(
                writer, sheet_name="Summary", startrow=9, index=False
            )

            # 2. Sample data from each table (first 10 records)
            for table_name in [f["table"] for f in converted_files]:
                try:
                    # Read the full table data
                    df = self._read_table(connection, table_name)

                    # Take first 10 records for sample
                    sample_df = df.head(10)

                    # Convert to strings (same as our conversion process)
                    string_sample = self.string_converter.convert_dataframe(sample_df)

                    # Write to Excel sheet (sheet name max 31 chars)
                    sheet_name = table_name[:31] if len(table_name) > 31 else table_name
                    string_sample.to_excel(writer, sheet_name=sheet_name, index=False)

                except Exception as e:
                    self.logger.warning(
                        f"Could not create sample sheet for {table_name}: {e}"
                    )

                    # Create error sheet
                    error_df = pd.DataFrame(
                        {"Error": [f"Could not read sample data: {e}"]}
                    )
                    sheet_name = (
                        f"{table_name[:25]}_ERROR"
                        if len(table_name) > 25
                        else f"{table_name}_ERROR"
                    )
                    error_df.to_excel(writer, sheet_name=sheet_name, index=False)

        return excel_path

    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """Standard convert method - delegates to progress version"""
        return self.convert_with_progress(input_path, output_path, **options)

    def get_metadata(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from MDB/ACCDB file.

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
                "file_format": "Microsoft Access Database",
                "file_extension": input_path.suffix,
                "modified_date": pd.Timestamp.fromtimestamp(
                    file_stats.st_mtime
                ).isoformat(),
                "created_date": pd.Timestamp.fromtimestamp(
                    file_stats.st_ctime
                ).isoformat(),
            }

            # Detect database type and version
            db_info = detect_database_file(input_path)

            if db_info.file_type not in [DatabaseType.MDB, DatabaseType.ACCDB]:
                return metadata  # Return basic metadata only

            metadata["database_type"] = db_info.file_type.value.upper()
            metadata["database_version"] = db_info.version or "Unknown"
            metadata["is_encrypted"] = getattr(db_info, "is_encrypted", False)

            # Try to get table information without full connection
            try:
                discovery = MDBTableDiscovery()

                # Attempt connection
                connection_success = discovery.connect(input_path, password=None)

                if connection_success:
                    # List tables
                    table_names = discovery.list_tables(include_system=False)

                    if table_names:
                        metadata["table_count"] = len(table_names)
                        metadata["table_names"] = table_names

                        # Get table details
                        table_info = {}
                        total_rows = 0
                        total_columns = 0

                        for table_name in table_names:
                            try:
                                info = discovery.get_table_info(table_name)
                                row_count = info.row_count
                                columns = info.columns if info.columns else []
                                table_info[table_name] = {
                                    "row_count": row_count,
                                    "column_count": len(columns),
                                    "columns": [col.name for col in columns],
                                }
                                total_rows += row_count
                                total_columns += len(columns)
                            except Exception as e:
                                # Still count failed tables but with 0 rows
                                table_info[table_name] = {
                                    "error": str(e),
                                    "row_count": 0,
                                    "column_count": 0,
                                }

                        metadata["table_details"] = table_info
                        metadata["total_rows"] = total_rows
                        metadata["total_columns"] = total_columns
                    else:
                        metadata["table_count"] = 0
                        metadata["error"] = "No tables found"

                    # Close connection
                    discovery.close()
                else:
                    metadata["error"] = "Connection failed"
                    if getattr(db_info, "is_encrypted", False):
                        metadata["error"] = "Database is password protected"

            except Exception as e:
                # If we can't connect, just include basic metadata
                metadata["error"] = f"Could not read database structure: {str(e)}"

            return metadata

        except Exception as e:
            logging.error(f"Failed to extract MDB metadata: {e}")
            return None
