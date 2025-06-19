"""
MDB (Microsoft Access) to Parquet converter with string-only output.
Implements the complete conversion pipeline for Phase 1.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from .string_database_converter import StringDatabaseConverter
from ..readers.mdb_reader import MDBTableDiscovery, TableInfo
from ..detectors.database_detector import DatabaseType, detect_database_file


class MDBConverter(StringDatabaseConverter):
    """
    Converts Microsoft Access (MDB/ACCDB) files to Parquet with string-only output.
    Implements Phase 1 requirements with 6-stage progress tracking.
    """
    
    def __init__(self):
        super().__init__()
        self.discovery: Optional[MDBTableDiscovery] = None
        self.password: Optional[str] = None
        
    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats"""
        return ['.mdb', '.accdb']
    
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
            raise ConnectionError(f"Cannot connect to MDB file: {e}")
        
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
    
    def _read_table(self, connection: MDBTableDiscovery, table_name: str) -> pd.DataFrame:
        """Read table data as DataFrame"""
        try:
            df = connection.read_table(table_name)
            self.logger.debug(f"Read {len(df)} records from table {table_name}")
            return df
        except Exception as e:
            self.logger.error(f"Error reading table {table_name}: {e}")
            raise
    
    def _get_table_info(self, connection: MDBTableDiscovery, table_name: str) -> Dict[str, Any]:
        """Get metadata about a table"""
        try:
            table_info = connection.get_table_info(table_name)
            return {
                'name': table_info.name,
                'record_count': table_info.record_count,
                'column_count': table_info.column_count,
                'estimated_size': table_info.estimated_size,
                'columns': [
                    {
                        'name': col['name'],
                        'type': col['type'],
                        'size': col.get('size', 0),
                        'nullable': col.get('nullable', True)
                    }
                    for col in table_info.columns
                ],
                'has_primary_key': table_info.has_primary_key
            }
        except Exception as e:
            self.logger.warning(f"Could not get table info for {table_name}: {e}")
            return {
                'name': table_name,
                'record_count': 0,
                'column_count': 0,
                'estimated_size': 0,
                'columns': [],
                'has_primary_key': False
            }
    
    def _close_connection(self, connection: MDBTableDiscovery) -> None:
        """Close database connection"""
        try:
            connection.close()
        except Exception as e:
            self.logger.warning(f"Error closing MDB connection: {e}")
    
    def validate_input(self, input_path: Path) -> tuple[bool, str]:
        """Validate MDB input file"""
        # Check file extension
        if input_path.suffix.lower() not in ['.mdb', '.accdb']:
            return False, f"File must be .mdb or .accdb, got {input_path.suffix}"
        
        # Use detector for validation
        from ..detectors.database_detector import DatabaseFileDetector
        detector = DatabaseFileDetector()
        return detector.validate_file_access(input_path)
    
    def convert_with_progress(self, input_path: Path, output_path: Path, **options: Any) -> bool:
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
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        from rich.table import Table
        
        console = Console()
        
        try:
            # Stage 1: Analyzing the file
            console.print("🔍 [bold blue]Stage 1:[/bold blue] Analyzing the file...")
            
            # Extract password from options
            self.password = options.get('password')
            
            # Validate and detect file
            db_info = detect_database_file(input_path)
            if db_info.error_message:
                console.print(f"❌ [red]Error:[/red] {db_info.error_message}")
                return False
            
            console.print(f"✓ File format: {db_info.version}")
            console.print(f"✓ File size: {db_info.estimated_size / 1024 / 1024:.1f} MB")
            console.print(f"✓ Password protected: {'Yes' if db_info.is_password_protected else 'No'}")
            
            # Stage 2: Listing all tables
            console.print("\n📋 [bold blue]Stage 2:[/bold blue] Listing all tables...")
            
            connection = self._connect_to_database(input_path)
            
            try:
                tables = self._list_tables(connection)
                
                if not tables:
                    console.print("⚠️ [yellow]Warning:[/yellow] No user tables found in database")
                    return True
                
                # Stage 3: Found number of tables
                console.print(f"✓ Found {len(tables)} user tables")
                
                # Stage 4: Extracting summary
                console.print("\n📊 [bold blue]Stage 3:[/bold blue] Extracting summary...")
                
                # Get table info for all tables
                table_infos = []
                total_records = 0
                total_size = 0
                
                for table_name in tables:
                    info = self._get_table_info(connection, table_name)
                    table_infos.append(info)
                    total_records += info['record_count']
                    total_size += info['estimated_size']
                
                # Stage 5: Show table overview
                console.print(f"\n📈 [bold blue]Stage 4:[/bold blue] Table Overview:")
                
                # Create summary table
                summary_table = Table(title="Database Tables Summary")
                summary_table.add_column("Table Name", style="cyan")
                summary_table.add_column("Records", justify="right", style="green")
                summary_table.add_column("Columns", justify="right", style="blue")
                summary_table.add_column("Est. Size", justify="right", style="yellow")
                
                for info in table_infos:
                    size_mb = info['estimated_size'] / 1024 / 1024
                    summary_table.add_row(
                        info['name'],
                        f"{info['record_count']:,}",
                        str(info['column_count']),
                        f"{size_mb:.1f} MB"
                    )
                
                # Add totals row
                total_size_mb = total_size / 1024 / 1024
                summary_table.add_row(
                    "[bold]TOTAL[/bold]",
                    f"[bold]{total_records:,}[/bold]",
                    "-",
                    f"[bold]{total_size_mb:.1f} MB[/bold]"
                )
                
                console.print(summary_table)
                
                # Stage 6: Convert tables
                console.print(f"\n🔄 [bold blue]Stage 5:[/bold blue] Converting tables to Parquet...")
                
                # Create output directory
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Convert each table with progress
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console
                ) as progress:
                    
                    overall_task = progress.add_task(
                        f"Converting {len(tables)} tables...", 
                        total=len(tables)
                    )
                    
                    converted_files = []
                    
                    for i, table_name in enumerate(tables):
                        # Update progress
                        progress.update(
                            overall_task, 
                            description=f"[{i+1}/{len(tables)}] {table_name}",
                            completed=i
                        )
                        
                        try:
                            # Read table data
                            df = self._read_table(connection, table_name)
                            
                            if df.empty:
                                console.print(f"⚠️ Table {table_name} is empty, skipping...")
                                continue
                            
                            # Convert to strings
                            string_df = self.string_converter.convert_dataframe(df)
                            
                            # Save as Parquet
                            output_file = output_path / f"{table_name}.parquet"
                            self._save_parquet(string_df, output_file, **options)
                            
                            # Track statistics
                            self.conversion_stats.append(self.string_converter.stats)
                            
                            # Record successful conversion
                            converted_files.append({
                                'table': table_name,
                                'records': len(string_df),
                                'file': output_file,
                                'size_mb': output_file.stat().st_size / 1024 / 1024
                            })
                            
                            console.print(f"✓ {table_name}: {len(string_df):,} records → {output_file.name}")
                            
                        except Exception as e:
                            console.print(f"❌ Failed to convert {table_name}: {e}")
                            continue
                    
                    # Complete progress
                    progress.update(overall_task, completed=len(tables))
                
                # Stage 6: Final summary
                if converted_files:
                    console.print(f"\n📑 [bold blue]Stage 6:[/bold blue] Conversion Summary:")
                    
                    total_converted_records = sum(f['records'] for f in converted_files)
                    total_output_size = sum(f['size_mb'] for f in converted_files)
                    
                    console.print(f"✅ [green]Conversion completed successfully![/green]")
                    console.print(f"• Files created: {len(converted_files)}")
                    console.print(f"• Records converted: {total_converted_records:,}")
                    console.print(f"• Output size: {total_output_size:.1f} MB")
                    console.print(f"• Output directory: {output_path}")
                    
                    # List output files
                    console.print("\nOutput files:")
                    for file_info in converted_files:
                        console.print(f"  • {file_info['file'].name} ({file_info['records']:,} records)")
                else:
                    console.print("⚠️ [yellow]No tables were successfully converted[/yellow]")
                
                return len(converted_files) > 0
                
            finally:
                self._close_connection(connection)
                
        except Exception as e:
            console.print(f"❌ [red]Conversion failed:[/red] {e}")
            self.logger.error(f"MDB conversion failed: {e}")
            return False
    
    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """Standard convert method - delegates to progress version"""
        return self.convert_with_progress(input_path, output_path, **options)