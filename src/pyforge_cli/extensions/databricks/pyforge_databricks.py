"""
PyForge Databricks API - Main Interface for Notebook Users

This module provides the main API class for using PyForge in Databricks notebooks,
with automatic environment detection and optimized conversion capabilities.
"""

import logging
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime

from .environment import DatabricksEnvironment
from .converter_selector import ConverterSelector, ConverterType
from .fallback_manager import FallbackManager
from .volume_operations import VolumeOperations
from .converters.spark_csv_converter import SparkCSVConverter
from .converters.spark_excel_converter import SparkExcelConverter
from .converters.spark_xml_converter import SparkXMLConverter
from .converters.delta_support import DeltaLakeSupport
from .converters.streaming_support import StreamingSupport


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
            "start_time": datetime.now()
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
                from pyspark.sql import SparkSession
                self.spark = SparkSession.builder.getOrCreate()
            
            # Initialize converters
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
        **kwargs
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
                Path(input_path),
                output_format,
                options
            )
            
            self.logger.info(
                f"Selected {recommendation.converter_type.value} converter "
                f"(confidence: {recommendation.confidence:.2f})"
            )
            
            # Execute conversion with fallback
            result = self.fallback_manager.execute_with_fallback(
                Path(input_path),
                Path(output_path),
                recommendation,
                options
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
                        "runtime_version": self.environment.get_runtime_version()
                    }
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
                            "error": attempt.error_message
                        }
                        for attempt in result.attempts
                    ]
                }
                
        except Exception as e:
            self.stats["failed_conversions"] += 1
            self.logger.error(f"Conversion error: {e}", exc_info=True)
            
            return {
                "success": False,
                "input_path": str(input_path),
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
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
                "exists": file_path.exists() if not str(file_path).startswith("/Volumes") else True,
                "format": file_path.suffix.lower().lstrip(".") if file_path.suffix else "unknown"
            }
            
            # Volume check
            if str(file_path).startswith("/Volumes"):
                volume_info = self.volume_ops.parse_volume_path(str(file_path))
                if volume_info:
                    info.update({
                        "is_volume": True,
                        "catalog": volume_info.catalog,
                        "schema": volume_info.schema,
                        "volume": volume_info.volume
                    })
                    
                    # Get file info from volume
                    file_details = self.volume_ops.get_file_info(str(file_path))
                    if file_details:
                        info.update({
                            "size": file_details.size,
                            "modified": file_details.modified_time.isoformat()
                        })
            else:
                # Local file
                if file_path.exists():
                    stat = file_path.stat()
                    info.update({
                        "is_volume": False,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
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
            return {
                "path": str(file_path),
                "exists": False,
                "error": str(e)
            }
    
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
                "warnings": []
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
                "warnings": []
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
        **kwargs
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
        from pathlib import Path
        import glob
        
        results = []
        files = glob.glob(file_pattern)
        
        self.logger.info(f"Found {len(files)} files matching pattern: {file_pattern}")
        
        for file_path in files:
            input_path = Path(file_path)
            output_path = Path(output_dir) / f"{input_path.stem}.{format}"
            
            result = self.convert(
                input_path,
                output_path,
                format=format,
                **kwargs
            )
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r["success"])
        self.logger.info(
            f"Batch conversion complete: {successful}/{len(results)} successful"
        )
        
        return results
    
    def install_sample_datasets(
        self,
        volume_path: Optional[str] = None,
        datasets: Optional[List[str]] = None
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
            "volume_path": volume_path
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
                if self.stats["total_conversions"] > 0 else 0
            ),
            "total_bytes_processed": self.stats["total_bytes_processed"],
            "total_gb_processed": round(
                self.stats["total_bytes_processed"] / (1024**3), 2
            ),
            "environment": self.get_environment_info()
        }
    
    # Private helper methods
    
    def _initialize_converters(self):
        """Initialize converter instances and register with fallback manager."""
        if self._converters_initialized:
            return
        
        # Initialize converters
        csv_converter = SparkCSVConverter(self.spark)
        excel_converter = SparkExcelConverter(self.spark)
        xml_converter = SparkXMLConverter(self.spark)
        delta_support = DeltaLakeSupport(self.spark)
        streaming_support = StreamingSupport(self.spark)
        
        # Register converters with fallback manager
        # These would be wrapper functions that match the expected signature
        self.fallback_manager.register_converter(
            ConverterType.SPARK,
            lambda i, o, opts: self._spark_converter_wrapper(i, o, opts)
        )
        
        # Store converter instances
        self._csv_converter = csv_converter
        self._excel_converter = excel_converter
        self._xml_converter = xml_converter
        self._delta_support = delta_support
        self._streaming_support = streaming_support
        
        self._converters_initialized = True
    
    def _spark_converter_wrapper(
        self,
        input_path: Path,
        output_path: Path,
        options: Dict[str, Any]
    ) -> bool:
        """Wrapper for Spark converters to match fallback manager interface."""
        input_format = input_path.suffix.lower().lstrip(".")
        output_format = options.get("output_format", "parquet")
        
        # Route to appropriate converter
        if input_format == "csv":
            return self._csv_converter.convert(
                input_path, output_path, output_format, options
            )
        elif input_format in ["xlsx", "xls"]:
            return self._excel_converter.convert(
                input_path, output_path, output_format, options
            )
        elif input_format == "xml":
            return self._xml_converter.convert(
                input_path, output_path, output_format, options
            )
        else:
            # Generic Spark reader
            return self._generic_spark_convert(
                input_path, output_path, input_format, output_format, options
            )
    
    def _prepare_input_path(self, path: Union[str, Path]) -> Path:
        """Prepare and validate input path."""
        if isinstance(path, str):
            path = Path(path)
        return path
    
    def _prepare_output_path(
        self,
        input_path: Path,
        output_path: Optional[Union[str, Path]],
        format: Optional[str]
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
        except:
            pass
        return None
    
    def _get_excel_info(self, file_path: Path) -> Dict[str, Any]:
        """Get Excel-specific file information."""
        try:
            import pandas as pd
            excel_file = pd.ExcelFile(str(file_path))
            return {
                "excel_sheets": excel_file.sheet_names,
                "sheet_count": len(excel_file.sheet_names)
            }
        except:
            return {}
    
    def _get_csv_info(self, file_path: Path) -> Dict[str, Any]:
        """Get CSV-specific file information."""
        try:
            # Quick sample to detect properties
            with open(file_path, 'rb') as f:
                sample = f.read(8192)
            
            # Detect encoding
            import chardet
            encoding = chardet.detect(sample)["encoding"]
            
            # Detect delimiter
            sample_text = sample.decode(encoding or 'utf-8', errors='ignore')
            delimiter = ","
            if "\t" in sample_text[:1000]:
                delimiter = "\t"
            elif "|" in sample_text[:1000]:
                delimiter = "|"
            
            return {
                "encoding": encoding,
                "delimiter": delimiter,
                "has_header": True  # Assume header
            }
        except:
            return {}
    
    def _get_parquet_info(self, file_path: Path) -> Dict[str, Any]:
        """Get Parquet-specific file information."""
        try:
            df = self.spark.read.parquet(str(file_path))
            return {
                "columns": df.columns,
                "column_count": len(df.columns),
                "schema": df.schema.simpleString()
            }
        except:
            return {}
    
    def _generic_spark_convert(
        self,
        input_path: Path,
        output_path: Path,
        input_format: str,
        output_format: str,
        options: Dict[str, Any]
    ) -> bool:
        """Generic Spark-based conversion for supported formats."""
        try:
            # Read
            df = self.spark.read.format(input_format).load(str(input_path))
            
            # Write
            writer = df.write.mode(options.get("mode", "overwrite"))
            
            if output_format == "delta":
                self._delta_support.write_delta(df, str(output_path), options)
            else:
                writer.format(output_format).save(str(output_path))
            
            return True
        except Exception as e:
            self.logger.error(f"Generic Spark conversion failed: {e}")
            return False