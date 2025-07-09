"""
PyForge Databricks API - Main Interface for Notebook Users

This module provides the main API class for using PyForge in Databricks notebooks,
with automatic environment detection and optimized conversion capabilities.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .converter_selector import ConverterSelector, ConverterType
from .converters.delta_support import DeltaLakeSupport
from .converters.spark_csv_converter import SparkCSVConverter
from .converters.spark_excel_converter import SparkExcelConverter
from .converters.spark_xml_converter import SparkXMLConverter
from .converters.streaming_support import StreamingSupport
from .environment import DatabricksEnvironment
from .fallback_manager import FallbackManager
from .volume_operations import VolumeOperations


class PyForgeDatabricks:
    """
    Main API class for PyForge Databricks extension.

    Provides a simple, intuitive interface for data conversion in Databricks
    notebooks with automatic optimization and environment detection.

    Example:
        >>> forge = PyForgeDatabricks()
        >>> forge.convert("data.csv", "output.parquet")
        >>> forge.convert("sales.xlsx", format="delta", partition_by="date")
    """

    def __init__(self, spark_session=None, auto_init: bool = True):
        """
        Initialize PyForge Databricks.

        Args:
            spark_session: Optional Spark session (auto-detected if not provided)
                           In Databricks notebooks, this is usually the global 'spark' variable
            auto_init: Automatically initialize on creation (default: True)
        """
        self.logger = logging.getLogger("pyforge.databricks")

        # Core components
        self.environment = DatabricksEnvironment()
        self.converter_selector = ConverterSelector()
        self.fallback_manager = FallbackManager()
        self.volume_ops = VolumeOperations()

        # Converters
        self.spark = spark_session
        self._converters_initialized = False

        # Conversion statistics
        self.stats = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "total_bytes_processed": 0,
            "start_time": datetime.now(),
        }

        if auto_init:
            self.initialize()

    def initialize(self) -> bool:
        """
        Initialize the PyForge Databricks environment.

        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing PyForge Databricks...")

            # Get environment info
            env_info = self.environment.get_environment_info()

            if env_info["is_databricks"]:
                self.logger.info(
                    f"Running in Databricks {env_info['compute_type']} "
                    f"(Runtime: {env_info['runtime_version']})"
                )
            else:
                self.logger.info("Running in non-Databricks environment")

            # Initialize Spark if needed
            if self.spark is None:
                try:
                    # In Databricks, try to use the existing 'spark' variable first
                    if env_info["is_databricks"]:
                        try:
                            # Try to access the global spark variable
                            import builtins
                            if hasattr(builtins, '__dict__') and 'spark' in builtins.__dict__:
                                self.spark = builtins.__dict__['spark']
                                self.logger.info("Using existing Databricks spark session")
                            else:
                                # Fallback to getting active session
                                from pyspark.sql import SparkSession
                                self.spark = SparkSession.getActiveSession()
                                if self.spark:
                                    self.logger.info("Using active Spark session")
                                else:
                                    self.logger.warning("No active Spark session found")
                        except Exception as e:
                            self.logger.debug(f"Could not access global spark variable: {e}")
                            # Try getActiveSession as fallback
                            from pyspark.sql import SparkSession
                            self.spark = SparkSession.getActiveSession()
                    else:
                        # Non-Databricks environment, create new session
                        from pyspark.sql import SparkSession
                        self.spark = SparkSession.builder.getOrCreate()
                        
                except Exception as spark_error:
                    self.logger.warning(f"Could not initialize Spark session: {spark_error}")
                    # Continue without Spark - native converters can still work

            # Initialize converters (always initialize, even if Spark fails)
            self._initialize_converters()

            self.logger.info("PyForge Databricks initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False

    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        format: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Convert file with automatic format detection and optimization.

        Args:
            input_path: Input file path (local or Volume path)
            output_path: Output path (auto-generated if not provided)
            format: Output format (auto-detected if not provided)
            **kwargs: Additional conversion options

        Returns:
            Dict[str, Any]: Conversion result with metadata

        Example:
            >>> result = forge.convert("data.csv")
            >>> result = forge.convert("data.xlsx", format="parquet", compression="snappy")
            >>> result = forge.convert("/Volumes/main/data/input.csv", partition_by="date")
        """
        start_time = datetime.now()
        self.stats["total_conversions"] += 1

        try:
            # Prepare paths
            input_path = self._prepare_input_path(input_path)
            output_path, output_format = self._prepare_output_path(
                input_path, output_path, format
            )

            self.logger.info(
                f"Converting: {input_path} -> {output_path} (format: {output_format})"
            )

            # Get file info
            file_info = self.get_info(input_path)
            if not file_info["exists"]:
                raise FileNotFoundError(f"Input file not found: {input_path}")

            # Select converter
            options = self._prepare_options(kwargs)
            recommendation = self.converter_selector.select_converter(
                Path(input_path), output_format, options
            )

            self.logger.info(
                f"Selected {recommendation.converter_type.value} converter "
                f"(confidence: {recommendation.confidence:.2f})"
            )

            # Execute conversion with fallback
            result = self.fallback_manager.execute_with_fallback(
                Path(input_path), Path(output_path), recommendation, options
            )

            # Prepare response
            duration = (datetime.now() - start_time).total_seconds()

            if result.success:
                self.stats["successful_conversions"] += 1
                self.stats["total_bytes_processed"] += file_info.get("size", 0)

                return {
                    "success": True,
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "output_format": output_format,
                    "converter_used": result.final_converter.value,
                    "duration_seconds": duration,
                    "file_size_bytes": file_info.get("size", 0),
                    "rows_processed": self._get_row_count(output_path, output_format),
                    "warnings": result.warnings,
                    "environment": {
                        "compute_type": self.environment.get_compute_type(),
                        "runtime_version": self.environment.get_runtime_version(),
                    },
                }
            else:
                self.stats["failed_conversions"] += 1

                return {
                    "success": False,
                    "input_path": str(input_path),
                    "error": "Conversion failed - see logs for details",
                    "attempts": len(result.attempts),
                    "duration_seconds": duration,
                    "fallback_history": [
                        {
                            "converter": attempt.converter_type.value,
                            "reason": attempt.reason.value,
                            "error": attempt.error_message,
                        }
                        for attempt in result.attempts
                    ],
                }

        except Exception as e:
            self.stats["failed_conversions"] += 1
            self.logger.error(f"Conversion error: {e}", exc_info=True)

            return {
                "success": False,
                "input_path": str(input_path),
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }

    def get_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get detailed information about a file.

        Args:
            file_path: File path to inspect

        Returns:
            Dict[str, Any]: File information including format, size, schema

        Example:
            >>> info = forge.get_info("sales_data.xlsx")
            >>> print(f"Format: {info['format']}, Sheets: {info['excel_sheets']}")
        """
        try:
            file_path = Path(file_path)

            # Basic file info
            info = {
                "path": str(file_path),
                "exists": (
                    file_path.exists()
                    if not str(file_path).startswith("/Volumes")
                    else True
                ),
                "format": (
                    file_path.suffix.lower().lstrip(".")
                    if file_path.suffix
                    else "unknown"
                ),
            }

            # Volume check
            if str(file_path).startswith("/Volumes"):
                volume_info = self.volume_ops.parse_volume_path(str(file_path))
                if volume_info:
                    info.update(
                        {
                            "is_volume": True,
                            "catalog": volume_info.catalog,
                            "schema": volume_info.schema,
                            "volume": volume_info.volume,
                        }
                    )

                    # Get file info from volume
                    file_details = self.volume_ops.get_file_info(str(file_path))
                    if file_details:
                        info.update(
                            {
                                "size": file_details.size,
                                "modified": file_details.modified_time.isoformat(),
                            }
                        )
            else:
                # Local file
                if file_path.exists():
                    stat = file_path.stat()
                    info.update(
                        {
                            "is_volume": False,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )

            # Format-specific info
            if info["format"] in ["xlsx", "xls"]:
                excel_info = self._get_excel_info(file_path)
                info.update(excel_info)

            elif info["format"] == "csv":
                csv_info = self._get_csv_info(file_path)
                info.update(csv_info)

            elif info["format"] == "parquet":
                parquet_info = self._get_parquet_info(file_path)
                info.update(parquet_info)

            return info

        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return {"path": str(file_path), "exists": False, "error": str(e)}

    def validate(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a file before conversion.

        Args:
            file_path: File to validate

        Returns:
            Dict[str, Any]: Validation results

        Example:
            >>> validation = forge.validate("data.csv")
            >>> if validation['is_valid']:
            >>>     forge.convert("data.csv")
        """
        try:
            file_path = Path(file_path)

            validation = {
                "path": str(file_path),
                "is_valid": True,
                "issues": [],
                "warnings": [],
            }

            # Check existence
            info = self.get_info(file_path)
            if not info.get("exists", False):
                validation["is_valid"] = False
                validation["issues"].append("File does not exist")
                return validation

            # Check size
            size = info.get("size", 0)
            if size == 0:
                validation["is_valid"] = False
                validation["issues"].append("File is empty")
            elif size > 10 * 1024**3:  # 10GB
                validation["warnings"].append(
                    f"Large file ({size / 1024**3:.1f}GB) - consider streaming"
                )

            # Check format support
            format = info.get("format", "unknown")
            if format == "unknown":
                validation["is_valid"] = False
                validation["issues"].append("Unknown file format")

            # Format-specific validation
            if format == "csv" and "encoding" in info:
                if info["encoding"] not in ["utf-8", "ascii", "latin-1"]:
                    validation["warnings"].append(
                        f"Unusual encoding: {info['encoding']}"
                    )

            return validation

        except Exception as e:
            return {
                "path": str(file_path),
                "is_valid": False,
                "issues": [str(e)],
                "warnings": [],
            }

    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get detailed environment information.

        Returns:
            Dict[str, Any]: Environment details

        Example:
            >>> env = forge.get_environment_info()
            >>> print(f"Compute Type: {env['compute_type']}")
        """
        return self.environment.get_environment_info()

    def batch_convert(
        self,
        file_pattern: str,
        output_dir: Union[str, Path],
        format: str = "parquet",
        parallel: bool = True,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Convert multiple files matching a pattern.

        Args:
            file_pattern: Glob pattern for input files
            output_dir: Output directory
            format: Output format for all files
            parallel: Process files in parallel (default: True)
            **kwargs: Additional conversion options

        Returns:
            List[Dict[str, Any]]: Results for each file

        Example:
            >>> results = forge.batch_convert("*.csv", "/tmp/output", format="parquet")
            >>> print(f"Converted {len(results)} files")
        """
        import glob
        from pathlib import Path

        results = []
        files = glob.glob(file_pattern)

        self.logger.info(f"Found {len(files)} files matching pattern: {file_pattern}")

        for file_path in files:
            input_path = Path(file_path)
            output_path = Path(output_dir) / f"{input_path.stem}.{format}"

            result = self.convert(input_path, output_path, format=format, **kwargs)
            results.append(result)

        # Summary
        successful = sum(1 for r in results if r["success"])
        self.logger.info(
            f"Batch conversion complete: {successful}/{len(results)} successful"
        )

        return results

    def install_sample_datasets(
        self, volume_path: Optional[str] = None, datasets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Install sample datasets for testing and demos.

        Args:
            volume_path: Unity Catalog Volume path (optional)
            datasets: Specific datasets to install (None = all)

        Returns:
            Dict[str, Any]: Installation results

        Example:
            >>> forge.install_sample_datasets("/Volumes/main/default/samples")
        """
        # This would download sample datasets from a repository
        # For now, return a placeholder
        return {
            "success": True,
            "message": "Sample dataset installation not yet implemented",
            "volume_path": volume_path,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get conversion statistics for this session.

        Returns:
            Dict[str, Any]: Session statistics
        """
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()

        return {
            "session_duration_seconds": uptime,
            "total_conversions": self.stats["total_conversions"],
            "successful_conversions": self.stats["successful_conversions"],
            "failed_conversions": self.stats["failed_conversions"],
            "success_rate": (
                self.stats["successful_conversions"] / self.stats["total_conversions"]
                if self.stats["total_conversions"] > 0
                else 0
            ),
            "total_bytes_processed": self.stats["total_bytes_processed"],
            "total_gb_processed": round(
                self.stats["total_bytes_processed"] / (1024**3), 2
            ),
            "environment": self.get_environment_info(),
        }

    # Private helper methods

    def _initialize_converters(self):
        """Initialize converter instances and register with fallback manager."""
        if self._converters_initialized:
            return

        # Initialize converters only if we have a Spark session
        if self.spark:
            try:
                csv_converter = SparkCSVConverter(self.spark)
                excel_converter = SparkExcelConverter(self.spark)
                xml_converter = SparkXMLConverter(self.spark)
                
                # Only initialize Delta support in non-serverless environments
                import os
                is_serverless = os.environ.get("IS_SERVERLESS", "").lower() == "true"
                if not is_serverless:
                    delta_support = DeltaLakeSupport(self.spark)
                else:
                    delta_support = None
                    self.logger.debug("Skipping Delta support initialization in serverless environment")
                    
                streaming_support = StreamingSupport(self.spark)
                
                # Store converter instances
                self._csv_converter = csv_converter
                self._excel_converter = excel_converter
                self._xml_converter = xml_converter
                self._delta_support = delta_support
                self._streaming_support = streaming_support
            except Exception as e:
                self.logger.warning(f"Could not initialize Spark converters: {e}")
                # Set to None so we know they're not available
                self._csv_converter = None
                self._excel_converter = None
                self._xml_converter = None
                self._delta_support = None
                self._streaming_support = None
        else:
            # No Spark session, can't create Spark converters
            self.logger.warning("No Spark session available, Spark converters will not be initialized")
            self._csv_converter = None
            self._excel_converter = None
            self._xml_converter = None
            self._delta_support = None
            self._streaming_support = None

        # Import native converters for fallback
        from ...converters import CSVConverter, XmlConverter
        try:
            from ...converters.excel_converter import ExcelConverter
            excel_available = True
        except ImportError:
            excel_available = False
            self.logger.warning("ExcelConverter not available for native fallback")

        # Note: Spark converter instances are already stored above
        
        # Store native converter instances for fallback
        self._native_csv_converter = CSVConverter()
        self._native_xml_converter = XmlConverter()
        if excel_available:
            self._native_excel_converter = ExcelConverter()
        else:
            self._native_excel_converter = None

        # Register all converter types with fallback manager
        # SPARK converter (distributed processing)
        self.fallback_manager.register_converter(
            ConverterType.SPARK,
            lambda i, o, opts: self._spark_converter_wrapper(i, o, opts),
        )
        
        # PANDAS converter (uses pandas for processing)
        self.fallback_manager.register_converter(
            ConverterType.PANDAS,
            lambda i, o, opts: self._pandas_converter_wrapper(i, o, opts),
        )
        
        # PYARROW converter (uses PyArrow for processing)
        self.fallback_manager.register_converter(
            ConverterType.PYARROW,
            lambda i, o, opts: self._pyarrow_converter_wrapper(i, o, opts),
        )
        
        # NATIVE converter (PyForge's native converters)
        self.fallback_manager.register_converter(
            ConverterType.NATIVE,
            lambda i, o, opts: self._native_converter_wrapper(i, o, opts),
        )

        self._converters_initialized = True

    def _spark_converter_wrapper(
        self, input_path: Path, output_path: Path, options: Dict[str, Any]
    ) -> bool:
        """Wrapper for Spark converters to match fallback manager interface."""
        # Check if Spark converters are available
        if not self.spark:
            self.logger.error("Spark session not available")
            return False
            
        input_format = input_path.suffix.lower().lstrip(".")
        output_format = options.get("output_format", "parquet")

        # Route to appropriate converter
        if input_format == "csv" and self._csv_converter:
            return self._csv_converter.convert(
                input_path, output_path, output_format, options
            )
        elif input_format in ["xlsx", "xls"] and self._excel_converter:
            return self._excel_converter.convert(
                input_path, output_path, output_format, options
            )
        elif input_format == "xml" and self._xml_converter:
            return self._xml_converter.convert(
                input_path, output_path, output_format, options
            )
        else:
            # Generic Spark reader
            return self._generic_spark_convert(
                input_path, output_path, input_format, output_format, options
            )

    def _pandas_converter_wrapper(
        self, input_path: Path, output_path: Path, options: Dict[str, Any]
    ) -> bool:
        """Wrapper for pandas-based converters."""
        input_format = input_path.suffix.lower().lstrip(".")
        output_format = options.get("output_format", "parquet")

        try:
            import pandas as pd

            # Read file with pandas
            if input_format == "csv":
                df = pd.read_csv(input_path)
            elif input_format in ["xlsx", "xls"]:
                df = pd.read_excel(input_path)
            elif input_format == "json":
                df = pd.read_json(input_path)
            elif input_format == "parquet":
                df = pd.read_parquet(input_path)
            else:
                self.logger.warning(f"Pandas doesn't support {input_format} format")
                return False

            # Write output
            if output_format == "parquet":
                df.to_parquet(output_path, index=False)
            elif output_format == "csv":
                df.to_csv(output_path, index=False)
            elif output_format == "json":
                df.to_json(output_path, orient="records")
            else:
                self.logger.warning(f"Pandas doesn't support writing to {output_format} format")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Pandas conversion failed: {e}")
            return False

    def _pyarrow_converter_wrapper(
        self, input_path: Path, output_path: Path, options: Dict[str, Any]
    ) -> bool:
        """Wrapper for PyArrow-based converters."""
        input_format = input_path.suffix.lower().lstrip(".")
        output_format = options.get("output_format", "parquet")

        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
            import pyarrow.csv as pc

            # Read file with PyArrow
            if input_format == "csv":
                table = pc.read_csv(input_path)
            elif input_format == "parquet":
                table = pq.read_table(input_path)
            else:
                self.logger.warning(f"PyArrow doesn't support {input_format} format")
                return False

            # Write output
            if output_format == "parquet":
                pq.write_table(table, output_path)
            elif output_format == "csv":
                pc.write_csv(table, output_path)
            else:
                self.logger.warning(f"PyArrow doesn't support writing to {output_format} format")
                return False

            return True

        except Exception as e:
            self.logger.error(f"PyArrow conversion failed: {e}")
            return False

    def _native_converter_wrapper(
        self, input_path: Path, output_path: Path, options: Dict[str, Any]
    ) -> bool:
        """Wrapper for PyForge's native converters."""
        input_format = input_path.suffix.lower().lstrip(".")
        output_format = options.get("output_format", "parquet")

        try:
            # Route to appropriate native converter
            if input_format == "csv":
                return self._native_csv_converter.convert(input_path, output_path, **options)
            elif input_format in ["xlsx", "xls"]:
                if self._native_excel_converter:
                    return self._native_excel_converter.convert(input_path, output_path, **options)
                else:
                    self.logger.warning(f"No native Excel converter available")
                    return False
            elif input_format == "xml":
                return self._native_xml_converter.convert(input_path, output_path, **options)
            else:
                self.logger.warning(f"No native converter for {input_format} format")
                return False

        except Exception as e:
            self.logger.error(f"Native converter failed: {e}")
            return False

    def _prepare_input_path(self, path: Union[str, Path]) -> Path:
        """Prepare and validate input path."""
        if isinstance(path, str):
            path = Path(path)
        return path

    def _prepare_output_path(
        self,
        input_path: Path,
        output_path: Optional[Union[str, Path]],
        format: Optional[str],
    ) -> tuple[Path, str]:
        """Prepare output path and format."""
        # Auto-detect format
        if format is None:
            if output_path and Path(output_path).suffix:
                format = Path(output_path).suffix.lower().lstrip(".")
            else:
                format = "parquet"  # Default

        # Auto-generate output path
        if output_path is None:
            output_dir = input_path.parent
            output_name = f"{input_path.stem}_converted.{format}"
            output_path = output_dir / output_name
        else:
            output_path = Path(output_path)

            # Add extension if missing
            if not output_path.suffix:
                output_path = output_path.with_suffix(f".{format}")

        return output_path, format

    def _prepare_options(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare conversion options."""
        options = kwargs.copy()

        # Add output format for converter selection
        if "output_format" not in options:
            options["output_format"] = "parquet"

        # Environment-specific defaults
        env_info = self.environment.get_environment_info()
        if env_info["compute_type"] == "serverless":
            options.setdefault("optimize_write", True)
            options.setdefault("adaptive_execution", True)

        return options

    def _get_row_count(self, file_path: Path, format: str) -> Optional[int]:
        """Get row count from output file."""
        try:
            if format == "parquet":
                df = self.spark.read.parquet(str(file_path))
                return df.count()
            elif format == "csv":
                df = self.spark.read.option("header", "true").csv(str(file_path))
                return df.count()
            # Add other formats as needed
        except Exception:
            pass
        return None

    def _get_excel_info(self, file_path: Path) -> Dict[str, Any]:
        """Get Excel-specific file information."""
        try:
            import pandas as pd

            excel_file = pd.ExcelFile(str(file_path))
            return {
                "excel_sheets": excel_file.sheet_names,
                "sheet_count": len(excel_file.sheet_names),
            }
        except Exception:
            return {}

    def _get_csv_info(self, file_path: Path) -> Dict[str, Any]:
        """Get CSV-specific file information."""
        try:
            # Quick sample to detect properties
            with open(file_path, "rb") as f:
                sample = f.read(8192)

            # Detect encoding
            import chardet

            encoding = chardet.detect(sample)["encoding"]

            # Detect delimiter
            sample_text = sample.decode(encoding or "utf-8", errors="ignore")
            delimiter = ","
            if "\t" in sample_text[:1000]:
                delimiter = "\t"
            elif "|" in sample_text[:1000]:
                delimiter = "|"

            return {
                "encoding": encoding,
                "delimiter": delimiter,
                "has_header": True,  # Assume header
            }
        except Exception:
            return {}

    def _get_parquet_info(self, file_path: Path) -> Dict[str, Any]:
        """Get Parquet-specific file information."""
        try:
            df = self.spark.read.parquet(str(file_path))
            return {
                "columns": df.columns,
                "column_count": len(df.columns),
                "schema": df.schema.simpleString(),
            }
        except Exception:
            return {}

    def _generic_spark_convert(
        self,
        input_path: Path,
        output_path: Path,
        input_format: str,
        output_format: str,
        options: Dict[str, Any],
    ) -> bool:
        """Generic Spark-based conversion for supported formats."""
        try:
            # Read
            df = self.spark.read.format(input_format).load(str(input_path))

            # Write
            writer = df.write.mode(options.get("mode", "overwrite"))

            if output_format == "delta":
                if self._delta_support:
                    self._delta_support.write_delta(df, str(output_path), options)
                else:
                    # Fallback to basic delta write without optimizations
                    writer.format("delta").save(str(output_path))
            else:
                writer.format(output_format).save(str(output_path))

            return True
        except Exception as e:
            self.logger.error(f"Generic Spark conversion failed: {e}")
            return False
