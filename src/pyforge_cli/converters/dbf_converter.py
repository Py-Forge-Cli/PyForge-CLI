"""
DBF (dBase) to Parquet converter with string-only output.
Implements the complete conversion pipeline for Phase 1.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from ..detectors.database_detector import DatabaseType, detect_database_file
from ..readers.dbf_reader import DBFTableDiscovery
from .string_database_converter import StringDatabaseConverter


class DBFConverter(StringDatabaseConverter):
    """
    Converts dBase (DBF) files to Parquet with string-only output.
    Implements Phase 1 requirements with 6-stage progress tracking.
    """

    def __init__(self):
        super().__init__()
        self.discovery: Optional[DBFTableDiscovery] = None

        # Set supported formats for registry compatibility
        self.supported_inputs = {".dbf"}
        self.supported_outputs = {".parquet"}

    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats"""
        return [".dbf"]

    def _connect_to_database(self, input_path: Path) -> DBFTableDiscovery:
        """Connect to DBF database and return discovery object"""
        # Detect and validate file
        db_info = detect_database_file(input_path)

        if db_info.file_type != DatabaseType.DBF:
            raise ValueError(f"File is not a DBF file: {input_path}")

        if db_info.error_message:
            raise ValueError(f"File validation failed: {db_info.error_message}")

        # Store database info
        self.database_info = db_info

        # Create discovery object
        discovery = DBFTableDiscovery()

        # Connect to DBF file
        try:
            success = discovery.connect(input_path)
            if not success:
                raise ConnectionError("Failed to connect to DBF file")
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise ConnectionError(f"Cannot connect to DBF file: {e}") from e

        self.discovery = discovery
        return discovery

    def _list_tables(self, connection: DBFTableDiscovery) -> List[str]:
        """List all tables in the database (DBF has only one table)"""
        try:
            tables = connection.list_tables()
            self.logger.info(
                f"DBF file contains table: {tables[0] if tables else 'None'}"
            )
            return tables
        except Exception as e:
            self.logger.error(f"Error listing tables: {e}")
            return []

    def _read_table(
        self, connection: DBFTableDiscovery, table_name: str
    ) -> pd.DataFrame:
        """Read table data as DataFrame"""
        try:
            df = connection.read_table()  # DBF has only one table
            self.logger.debug(f"Read {len(df)} records from DBF file")
            return df
        except Exception as e:
            self.logger.error(f"Error reading DBF data: {e}")
            raise

    def _get_table_info(
        self, connection: DBFTableDiscovery, table_name: str
    ) -> Dict[str, Any]:
        """Get metadata about the table"""
        try:
            table_info = connection.get_table_info()
            return {
                "name": table_info.name,
                "record_count": table_info.record_count,
                "column_count": table_info.field_count,
                "estimated_size": table_info.estimated_size,
                "columns": [
                    {
                        "name": field.name,
                        "type": field.type,
                        "size": field.length,
                        "decimal_places": field.decimal_places,
                        "position": field.position,
                    }
                    for field in table_info.fields
                ],
                "has_memo": table_info.has_memo,
                "version": table_info.version,
                "encoding": table_info.encoding,
                "last_update": (
                    table_info.last_update.isoformat()
                    if table_info.last_update
                    else None
                ),
            }
        except Exception as e:
            self.logger.warning(f"Could not get table info: {e}")
            return {
                "name": table_name,
                "record_count": 0,
                "column_count": 0,
                "estimated_size": 0,
                "columns": [],
                "has_memo": False,
                "version": "Unknown",
                "encoding": "Unknown",
            }

    def _close_connection(self, connection: DBFTableDiscovery) -> None:
        """Close database connection"""
        try:
            connection.close()
        except Exception as e:
            self.logger.warning(f"Error closing DBF connection: {e}")

    def validate_input(self, input_path: Path) -> bool:
        """Validate DBF input file"""
        # Check file extension
        if input_path.suffix.lower() != ".dbf":
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
        Convert DBF file with 6-stage progress tracking.

        Stages:
        1. Analyzing the file
        2. Listing table (DBF has one table)
        3. Found 1 table
        4. Extracting summary
        5. Show table details with records
        6. Extract table to destination path
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

            # Validate and detect file
            db_info = detect_database_file(input_path)
            if db_info.error_message:
                console.print(f"[FAIL] [red]Error:[/red] {db_info.error_message}")
                return False

            console.print(f"[OK] File format: {db_info.version}")
            console.print(
                f"[OK] File size: {db_info.estimated_size / 1024 / 1024:.1f} MB"
            )
            console.print(f"[OK] Encoding: {db_info.encoding}")
            if db_info.creation_date:
                console.print(f"[OK] Last update: {db_info.creation_date}")

            # Stage 2: Listing table
            console.print(
                "\n[CLIPBOARD] [bold blue]Stage 2:[/bold blue] Listing table..."
            )

            connection = self._connect_to_database(input_path)

            try:
                tables = self._list_tables(connection)

                if not tables:
                    console.print("[FAIL] [red]Error:[/red] No table found in DBF file")
                    return False

                table_name = tables[0]

                # Stage 3: Found table
                console.print(f"[OK] Found 1 table: {table_name}")

                # Stage 4: Extracting summary
                console.print(
                    "\n[CHART] [bold blue]Stage 3:[/bold blue] Extracting summary..."
                )

                # Get table info
                table_info = self._get_table_info(connection, table_name)

                # Stage 5: Show table overview
                console.print(
                    "\n[GRAPH] [bold blue]Stage 4:[/bold blue] Table Overview:"
                )

                # Create detailed info display
                info_table = Table(title=f"DBF File Details: {table_name}")
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="green")

                info_table.add_row("Table Name", table_info["name"])
                info_table.add_row("Records", f"{table_info['record_count']:,}")
                info_table.add_row("Fields", str(table_info["column_count"]))
                info_table.add_row("Version", table_info["version"])
                info_table.add_row("Encoding", table_info["encoding"])

                if table_info.get("last_update"):
                    info_table.add_row("Last Update", table_info["last_update"])

                if table_info.get("has_memo"):
                    info_table.add_row(
                        "Has Memo Fields", "Yes" if table_info["has_memo"] else "No"
                    )

                console.print(info_table)

                # Show field details
                if table_info["columns"]:
                    fields_table = Table(title="Field Definitions")
                    fields_table.add_column("Field Name", style="cyan")
                    fields_table.add_column("Type", style="blue")
                    fields_table.add_column("Length", justify="right", style="green")
                    fields_table.add_column("Decimals", justify="right", style="yellow")

                    for col in table_info["columns"]:
                        fields_table.add_row(
                            col["name"],
                            col["type"],
                            str(col["size"]),
                            str(col.get("decimal_places", 0)),
                        )

                    console.print(fields_table)

                # Stage 6: Convert table
                console.print(
                    "\n[CONVERT] [bold blue]Stage 5:[/bold blue] Converting to Parquet..."
                )

                # Create output directory
                output_path.mkdir(parents=True, exist_ok=True)

                # Convert the table
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:

                    convert_task = progress.add_task(
                        f"Converting {table_name}...", total=100
                    )

                    try:
                        # Read table data
                        progress.update(
                            convert_task,
                            description="Reading DBF data...",
                            completed=20,
                        )
                        df = self._read_table(connection, table_name)

                        if df.empty:
                            console.print(
                                "[WARN] [yellow]Warning:[/yellow] DBF file contains no data"
                            )
                            return True

                        # Convert to strings
                        progress.update(
                            convert_task,
                            description="Converting to strings...",
                            completed=50,
                        )
                        string_df = self.string_converter.convert_dataframe(df)

                        # Save as Parquet
                        progress.update(
                            convert_task,
                            description="Saving Parquet file...",
                            completed=80,
                        )
                        output_file = output_path / f"{table_name}.parquet"
                        self._save_parquet(string_df, output_file, **options)

                        # Track statistics
                        self.conversion_stats.append(self.string_converter.stats)

                        progress.update(
                            convert_task,
                            description="Conversion complete!",
                            completed=100,
                        )

                        # Final summary
                        console.print(
                            "\n[DOCUMENT] [bold blue]Stage 6:[/bold blue] Conversion Summary:"
                        )

                        output_size_mb = output_file.stat().st_size / 1024 / 1024
                        compression_ratio = (
                            (table_info["estimated_size"] / output_file.stat().st_size)
                            if output_file.stat().st_size > 0
                            else 0
                        )

                        console.print(
                            "[OK] [green]Conversion completed successfully![/green]"
                        )
                        console.print(f"• Records converted: {len(string_df):,}")
                        console.print(f"• Output file: {output_file.name}")
                        console.print(f"• Output size: {output_size_mb:.1f} MB")
                        console.print(f"• Compression ratio: {compression_ratio:.1f}x")
                        console.print(f"• Output directory: {output_path}")

                        # Show conversion statistics
                        conversion_summary = (
                            self.string_converter.get_conversion_summary()
                        )
                        if conversion_summary["conversions_by_type"]:
                            console.print("\nData type conversions:")
                            for data_type, count in conversion_summary[
                                "conversions_by_type"
                            ].items():
                                console.print(f"  • {data_type}: {count:,} values")

                        if conversion_summary["warnings"] > 0:
                            console.print(
                                f"[WARN] [yellow]Warnings:[/yellow] {conversion_summary['warnings']} conversion warnings"
                            )

                        if conversion_summary["errors"] > 0:
                            console.print(
                                f"[FAIL] [red]Errors:[/red] {conversion_summary['errors']} conversion errors"
                            )

                        return True

                    except Exception as e:
                        console.print(f"[FAIL] Failed to convert DBF file: {e}")
                        return False

            finally:
                self._close_connection(connection)

        except Exception as e:
            console.print(f"[FAIL] [red]Conversion failed:[/red] {e}")
            self.logger.error(f"DBF conversion failed: {e}")
            return False

    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """Standard convert method - delegates to progress version"""
        return self.convert_with_progress(input_path, output_path, **options)

    def get_metadata(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from DBF file.

        Args:
            input_path: Path to DBF file

        Returns:
            Dictionary containing file metadata or None if extraction fails
        """
        try:
            # Get basic file info
            file_stats = input_path.stat()
            metadata = {
                "file_name": input_path.name,
                "file_size": file_stats.st_size,
                "file_format": "dBase Database File",
                "file_extension": input_path.suffix,
                "modified_date": pd.Timestamp.fromtimestamp(file_stats.st_mtime).isoformat(),
                "created_date": pd.Timestamp.fromtimestamp(file_stats.st_ctime).isoformat(),
            }

            # Detect database type and version
            db_info = detect_database_file(input_path)

            if db_info.file_type != DatabaseType.DBF:
                return metadata  # Return basic metadata only

            metadata["database_type"] = db_info.file_type.value
            metadata["database_version"] = db_info.version or "Unknown"

            # Try to get table information
            try:
                discovery = DBFTableDiscovery()

                # Read DBF header and structure
                if discovery.connect(input_path):
                    # Get table info
                    table_info = discovery.get_table_info()

                    if table_info:
                        metadata["record_count"] = table_info.record_count
                        metadata["field_count"] = len(table_info.fields) if table_info.fields else 0
                        metadata["record_length"] = getattr(table_info, 'record_length', 0)
                        metadata["header_length"] = getattr(table_info, 'header_length', 0)
                        metadata["last_update"] = getattr(table_info, 'last_update', None)

                        # Field information
                        if table_info.fields:
                            field_info = []
                            for field in table_info.fields:
                                field_info.append({
                                    "name": field.name,
                                    "type": field.type,
                                    "length": field.length,
                                    "decimal_places": getattr(field, 'decimal_places', 0)
                                })
                            metadata["fields"] = field_info

                        # Calculate approximate data size
                        if hasattr(table_info, 'record_length') and table_info.record_count:
                            metadata["estimated_data_size"] = table_info.record_length * table_info.record_count
                    else:
                        metadata["error"] = "Could not read DBF table structure"

                    discovery.disconnect()
                else:
                    metadata["error"] = "Could not connect to DBF file"

            except Exception as e:
                # If we can't read structure, just include basic metadata
                metadata["error"] = f"Could not read DBF structure: {str(e)}"

            return metadata

        except Exception as e:
            logging.error(f"Failed to extract DBF metadata: {e}")
            return None
