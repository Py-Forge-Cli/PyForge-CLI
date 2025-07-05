"""
PySpark-based CSV to Parquet converter with Databricks environment detection.
Extends the standard CSV converter with PySpark capabilities for improved performance.
"""

import logging
import time
from pathlib import Path
from typing import Any

from rich.console import Console

from .csv_converter import CSVConverter


class PySparkCSVConverter(CSVConverter):
    """
    CSV to Parquet converter using PySpark in Databricks environments.
    Falls back to pandas-based conversion in non-Databricks environments.
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.console = Console()
        self.databricks_env = None
        self.is_databricks = False
        self.pyspark_available = self._check_pyspark_available()
        self.detect_environment()

    def _check_pyspark_available(self) -> bool:
        """Check if PySpark is available."""
        try:
            import pyspark  # noqa: F401

            return True
        except ImportError:
            self.logger.debug("PySpark not available")
            return False

    def detect_environment(self) -> None:
        """Detect if running in Databricks environment."""
        try:
            from pyforge_cli.databricks.environment import detect_databricks_environment

            self.databricks_env = detect_databricks_environment()

            # Fix: Should check if it's Databricks first, not just serverless
            self.is_databricks = self.databricks_env.is_databricks

            # Enhanced logging for troubleshooting
            self.logger.info("Environment detection results:")
            self.logger.info(f"  - Databricks environment: {self.is_databricks}")
            self.logger.info(
                f"  - Serverless environment: {self.databricks_env.is_serverless()}"
            )
            self.logger.info(f"  - Runtime version: {self.databricks_env.version}")

            # Log key environment variables for debugging
            import os

            key_vars = [
                "IS_SERVERLESS",
                "SPARK_CONNECT_MODE_ENABLED",
                "DB_INSTANCE_TYPE",
                "DATABRICKS_RUNTIME_VERSION",
                "POD_NAME",
            ]
            for var in key_vars:
                value = os.environ.get(var, "Not set")
                self.logger.debug(f"  - {var}: {value}")

            if self.is_databricks:
                if self.databricks_env.is_serverless():
                    self.logger.info(
                        "✓ Databricks serverless environment detected - will use PySpark"
                    )
                else:
                    self.logger.info(
                        "✓ Databricks cluster environment detected - will use PySpark"
                    )
            else:
                self.logger.info(
                    "⚠️  Not in Databricks environment - will use pandas unless --force-pyspark"
                )

        except ImportError:
            self.logger.debug("Databricks environment detection not available")
            self.is_databricks = False

    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """
        Convert CSV file to Parquet format with environment awareness and file size optimization.

        Args:
            input_path: Path to CSV file
            output_path: Path for output Parquet file
            **options: Conversion options (compression, force, etc.)

        Returns:
            True if conversion successful
        """
        time.time()

        try:
            # Validate input
            if not self.validate_input(input_path):
                self.logger.error(f"Invalid CSV file: {input_path}")
                return False

            # Get file size for progress tracking and decision making
            self.stats["file_size"] = input_path.stat().st_size
            file_size_mb = self.stats["file_size"] / (1024 * 1024)

            # Decision logic for using PySpark:
            # 1. Always use PySpark in Databricks environment
            # 2. Use PySpark for files >500MB (even locally)
            # 3. Use PySpark if force_pyspark is explicitly set
            use_pyspark = (
                self.is_databricks
                or file_size_mb > 500  # New: Auto-use PySpark for large files
                or (self.pyspark_available and options.get("force_pyspark", False))
            )

            if use_pyspark:
                # Show environment detection results to user
                if self.is_databricks:
                    if self.databricks_env.is_serverless():
                        self.console.print(
                            "[green]🚀 Databricks Serverless detected - using PySpark distributed processing[/green]"
                        )
                    else:
                        self.console.print(
                            "[green]🚀 Databricks Cluster detected - using PySpark distributed processing[/green]"
                        )
                elif file_size_mb > 500:
                    self.console.print(
                        f"[green]📊 Large file detected ({file_size_mb:.1f}MB > 500MB) - using native Spark for optimal performance[/green]"
                    )
                else:
                    self.console.print(
                        "[yellow]🔧 Local PySpark mode (--force-pyspark enabled)[/yellow]"
                    )

                # For large files, use native Spark session if in Databricks
                if file_size_mb > 500 and self.is_databricks:
                    return self._convert_with_native_spark(
                        input_path, output_path, **options
                    )
                else:
                    return self._convert_with_pyspark(
                        input_path, output_path, **options
                    )
            else:
                # Fall back to pandas-based conversion
                if options.get("verbose"):
                    self.console.print(
                        f"[yellow]📊 Using pandas for CSV conversion ({file_size_mb:.1f}MB file)[/yellow]"
                    )
                    if self.pyspark_available:
                        self.console.print(
                            "[dim]💡 Tip: Files >500MB automatically use Spark, or use --force-pyspark for any size[/dim]"
                        )
                return super().convert(input_path, output_path, **options)

        except Exception as e:
            self.logger.error(f"CSV conversion failed: {e}")
            if options.get("verbose"):
                self.console.print(f"[red]Error: {e}[/red]")
            return False

    def _convert_with_native_spark(
        self, input_path: Path, output_path: Path, **options: Any
    ) -> bool:
        """
        Convert using native Databricks Spark session (optimized for large files).

        Args:
            input_path: Path to CSV file
            output_path: Path for output Parquet file
            **options: Conversion options

        Returns:
            True if conversion successful
        """
        try:
            start_time = time.time()
            self.logger.info("Using native Databricks Spark for CSV conversion")

            file_size_mb = self.stats["file_size"] / (1024 * 1024)
            if options.get("verbose"):
                self.console.print(
                    f"[yellow]Using native Spark session for {file_size_mb:.1f}MB file[/yellow]"
                )

            # Get the existing Databricks Spark session (avoid creating new connections)
            from pyspark.sql import SparkSession

            # Use the active Spark session in Databricks
            spark = SparkSession.getActiveSession()
            if spark is None:
                spark = SparkSession.builder.getOrCreate()

            if options.get("verbose"):
                self.console.print("[dim]Using existing Databricks Spark session[/dim]")

            # Read CSV with optimized settings for large files
            if options.get("verbose"):
                self.console.print("[dim]Reading CSV file with Spark...[/dim]")

            df = (
                spark.read.format("csv")
                .option("header", "true")
                .option("inferSchema", "false")
                .option("delimiter", ",")
                .option("quote", '"')
                .option("escape", '"')
                .option("mode", "PERMISSIVE")
                .option("nullValue", "")
                .option("emptyValue", "")
                .option("multiline", "true")
                .option("ignoreLeadingWhiteSpace", "true")
                .option("ignoreTrailingWhiteSpace", "true")
                .load(str(input_path.absolute()))
            )

            # Show progress for large files
            if options.get("verbose"):
                self.console.print(
                    "[dim]Converting all columns to string type...[/dim]"
                )

            # Convert all columns to strings for consistency
            from pyspark.sql.functions import col
            from pyspark.sql.types import StringType

            for column_name in df.columns:
                df = df.withColumn(column_name, col(column_name).cast(StringType()))

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write as Parquet with optimal settings
            if options.get("verbose"):
                self.console.print("[dim]Writing Parquet file...[/dim]")

            compression = options.get("compression", "snappy")
            df.write.mode("overwrite").option("compression", compression).parquet(
                str(output_path.absolute())
            )

            # Record statistics
            if options.get("verbose"):
                self.console.print("[dim]Collecting statistics...[/dim]")

            self.stats["rows_processed"] = df.count()
            self.stats["columns_detected"] = len(df.columns)
            self.stats["conversion_time"] = time.time() - start_time

            # Record that we used native Spark
            self.stats["engine_used"] = "Native Databricks Spark"

            if options.get("verbose"):
                self._print_native_spark_conversion_summary()

            self.logger.info(f"✓ Native Spark CSV conversion completed: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Native Spark conversion failed: {e}")
            if options.get("verbose"):
                self.console.print(f"[red]Native Spark error: {e}[/red]")
            # Try fallback to standard PySpark conversion
            self.logger.info("Falling back to standard PySpark conversion")
            if options.get("verbose"):
                self.console.print(
                    "[yellow]Falling back to standard PySpark conversion[/yellow]"
                )
            return self._convert_with_pyspark(input_path, output_path, **options)

    def _convert_with_pyspark(
        self, input_path: Path, output_path: Path, **options: Any
    ) -> bool:
        """
        Convert using PySpark.

        Args:
            input_path: Path to CSV file
            output_path: Path for output Parquet file
            **options: Conversion options

        Returns:
            True if conversion successful
        """
        try:
            # Import PySpark here to avoid dependency issues
            from pyspark.sql import SparkSession

            start_time = time.time()
            self.logger.info("Using PySpark for CSV conversion")
            if options.get("verbose"):
                self.console.print(
                    "[yellow]Using PySpark for CSV conversion (fast mode - skipping detection)[/yellow]"
                )

            # Skip encoding/dialect detection for PySpark - use sensible defaults for speed
            # Spark can handle most CSV files with these defaults
            encoding = "utf-8"
            dialect_params = {
                "delimiter": ",",  # Standard CSV delimiter
                "has_header": True,  # Most CSV files have headers
                "quotechar": '"',  # Standard quote character
            }

            # Record defaults used
            self.stats["encoding_detected"] = encoding
            self.stats["delimiter_detected"] = dialect_params["delimiter"]
            self.stats["has_header"] = dialect_params["has_header"]

            if options.get("verbose"):
                self.console.print(
                    f"[dim]Using defaults: encoding={encoding}, delimiter='{dialect_params['delimiter']}', headers={dialect_params['has_header']}[/dim]"
                )
                self.console.print(
                    "[dim]Note: PySpark can auto-detect most issues during reading[/dim]"
                )

            # Get active Spark session or create a new one
            if self.is_databricks:
                # In Databricks, get the active session
                spark = SparkSession.builder.getOrCreate()
            else:
                # Locally, create a new session
                spark = (
                    SparkSession.builder.appName("PyForge-CSV-Converter")
                    .config("spark.sql.execution.arrow.pyspark.enabled", "true")
                    .config("spark.driver.memory", "2g")
                    .getOrCreate()
                )

            # Read CSV with robust options - let Spark handle edge cases
            df = (
                spark.read.format("csv")
                .option("header", dialect_params["has_header"])
                .option("delimiter", dialect_params["delimiter"])
                .option("quote", dialect_params["quotechar"])
                .option("escape", '"')
                .option("mode", "PERMISSIVE")
                .option("inferSchema", "false")
                .option("nullValue", "")
                .option("emptyValue", "")
                .option("multiline", "true")
                .option("ignoreLeadingWhiteSpace", "true")
                .option("ignoreTrailingWhiteSpace", "true")
                .load(str(input_path.absolute()))
            )

            # Convert all columns to strings
            from pyspark.sql.functions import col
            from pyspark.sql.types import StringType

            for column_name in df.columns:
                df = df.withColumn(column_name, col(column_name).cast(StringType()))

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write as Parquet
            compression = options.get("compression", "snappy")
            df.write.mode("overwrite").option("compression", compression).parquet(
                str(output_path.absolute())
            )

            # Record statistics
            self.stats["rows_processed"] = df.count()
            self.stats["columns_detected"] = len(df.columns)
            self.stats["conversion_time"] = time.time() - start_time

            if options.get("verbose"):
                self._print_pyspark_conversion_summary()

            self.logger.info(f"✓ PySpark CSV conversion completed: {output_path}")
            return True

        except ImportError as e:
            self.logger.warning(f"PySpark import error: {e}, falling back to pandas")
            if options.get("verbose"):
                self.console.print(
                    "[yellow]PySpark not available, falling back to pandas[/yellow]"
                )
            return super().convert(input_path, output_path, **options)

        except Exception as e:
            self.logger.error(f"PySpark conversion failed: {e}")
            if options.get("verbose"):
                self.console.print(f"[red]PySpark error: {e}[/red]")
            # Try fallback to pandas
            self.logger.info("Falling back to pandas conversion")
            if options.get("verbose"):
                self.console.print("[yellow]Falling back to pandas conversion[/yellow]")
            return super().convert(input_path, output_path, **options)

    def _print_native_spark_conversion_summary(self):
        """Print summary for native Spark conversion."""
        from rich.table import Table

        table = Table(title="Native Spark CSV Conversion Summary")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        file_size_mb = self.stats["file_size"] / (1024 * 1024)

        table.add_row(
            "File Size", f"{self.stats['file_size']:,} bytes ({file_size_mb:.1f} MB)"
        )
        table.add_row("Rows Processed", f"{self.stats['rows_processed']:,}")
        table.add_row("Columns Detected", str(self.stats["columns_detected"]))
        table.add_row("Conversion Time", f"{self.stats['conversion_time']:.2f} seconds")
        table.add_row("Engine", "Native Databricks Spark")
        table.add_row("Environment", f"Databricks {self.databricks_env.version}")
        table.add_row("Optimization", "Large file processing enabled")

        # Calculate processing rate
        if self.stats["conversion_time"] > 0:
            mb_per_second = file_size_mb / self.stats["conversion_time"]
            rows_per_second = (
                self.stats["rows_processed"] / self.stats["conversion_time"]
            )
            table.add_row(
                "Processing Rate",
                f"{mb_per_second:.1f} MB/s, {rows_per_second:,.0f} rows/s",
            )

        self.console.print(table)

    def _print_pyspark_conversion_summary(self):
        """Print summary for PySpark conversion."""
        from rich.table import Table

        table = Table(title="PySpark CSV Conversion Summary")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("File Size", f"{self.stats['file_size']:,} bytes")
        table.add_row("Encoding Detected", self.stats["encoding_detected"])
        table.add_row("Delimiter Detected", repr(self.stats["delimiter_detected"]))
        table.add_row("Has Headers", str(self.stats["has_header"]))
        table.add_row("Rows Processed", f"{self.stats['rows_processed']:,}")
        table.add_row("Columns Detected", str(self.stats["columns_detected"]))
        table.add_row("Conversion Time", f"{self.stats['conversion_time']:.2f} seconds")
        table.add_row("Engine", "PySpark")

        if self.is_databricks:
            table.add_row(
                "Environment", f"Databricks Serverless {self.databricks_env.version}"
            )
        else:
            table.add_row("Environment", "Local PySpark")

        self.console.print(table)
