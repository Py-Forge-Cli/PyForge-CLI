"""
Spark-optimized CSV Converter for Databricks

This module implements a high-performance CSV converter using Apache Spark,
optimized for large files and distributed processing in Databricks environments.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType, TimestampType, DateType
from pyspark.sql.functions import col, when, trim, regexp_replace, to_timestamp, to_date


class SparkCSVConverter:
    """
    CSV converter optimized for Apache Spark.
    
    Provides high-performance CSV reading and writing with support for:
    - Large file processing
    - Schema inference and enforcement
    - Data type optimization
    - Streaming mode for ultra-large files
    - Various output formats
    """
    
    def __init__(self, spark_session: Optional[SparkSession] = None):
        """
        Initialize the Spark CSV converter.
        
        Args:
            spark_session: Optional Spark session to use
        """
        self.logger = logging.getLogger("pyforge.extensions.databricks.converters.spark_csv")
        self.spark = spark_session or SparkSession.builder.getOrCreate()
        
        # Default CSV options
        self.default_read_options = {
            "header": "true",
            "inferSchema": "true",
            "multiLine": "true",
            "escape": '"',
            "quote": '"',
            "sep": ",",
            "encoding": "UTF-8",
            "ignoreLeadingWhiteSpace": "true",
            "ignoreTrailingWhiteSpace": "true",
            "nullValue": "",
            "emptyValue": "",
            "dateFormat": "yyyy-MM-dd",
            "timestampFormat": "yyyy-MM-dd HH:mm:ss"
        }
        
        # Output format handlers
        self.output_handlers = {
            "parquet": self._write_parquet,
            "delta": self._write_delta,
            "json": self._write_json,
            "orc": self._write_orc,
            "avro": self._write_avro,
            "csv": self._write_csv
        }
        
    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        output_format: str,
        options: Dict[str, Any]
    ) -> bool:
        """
        Convert CSV file to specified output format.
        
        Args:
            input_path: Input CSV file path
            output_path: Output file path
            output_format: Target format (parquet, delta, json, etc.)
            options: Conversion options
            
        Returns:
            bool: True if successful
        """
        try:
            input_path = str(input_path)
            output_path = str(output_path)
            
            self.logger.info(f"Starting Spark CSV conversion: {input_path} -> {output_path}")
            
            # Merge options with defaults
            read_options = self._prepare_read_options(options)
            
            # Determine if streaming mode should be used
            use_streaming = options.get("streaming", False) or self._should_use_streaming(input_path, options)
            
            if use_streaming:
                self.logger.info("Using streaming mode for large file")
                success = self._convert_streaming(
                    input_path, output_path, output_format, read_options, options
                )
            else:
                self.logger.info("Using batch mode")
                success = self._convert_batch(
                    input_path, output_path, output_format, read_options, options
                )
            
            if success:
                self.logger.info(f"Successfully converted {input_path} to {output_format}")
            else:
                self.logger.error(f"Failed to convert {input_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error in Spark CSV conversion: {e}", exc_info=True)
            return False
    
    def _convert_batch(
        self,
        input_path: str,
        output_path: str,
        output_format: str,
        read_options: Dict[str, Any],
        options: Dict[str, Any]
    ) -> bool:
        """Batch mode conversion."""
        try:
            # Read CSV
            df = self._read_csv(input_path, read_options)
            
            # Apply transformations
            df = self._apply_transformations(df, options)
            
            # Optimize for output
            df = self._optimize_dataframe(df, output_format, options)
            
            # Write output
            writer = self.output_handlers.get(output_format)
            if not writer:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            writer(df, output_path, options)
            return True
            
        except Exception as e:
            self.logger.error(f"Batch conversion failed: {e}")
            return False
    
    def _convert_streaming(
        self,
        input_path: str,
        output_path: str,
        output_format: str,
        read_options: Dict[str, Any],
        options: Dict[str, Any]
    ) -> bool:
        """Streaming mode conversion for large files."""
        try:
            # Create streaming dataframe
            stream_df = (
                self.spark.readStream
                .format("csv")
                .options(**read_options)
                .load(input_path)
            )
            
            # Apply transformations
            stream_df = self._apply_transformations(stream_df, options)
            
            # Configure output stream
            query = (
                stream_df.writeStream
                .outputMode("append")
                .format(output_format)
                .option("path", output_path)
                .option("checkpointLocation", f"{output_path}_checkpoint")
            )
            
            # Add format-specific options
            if output_format == "parquet":
                query = query.option("compression", options.get("compression", "snappy"))
            
            # Start streaming
            stream_query = query.start()
            
            # Wait for completion
            stream_query.awaitTermination()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Streaming conversion failed: {e}")
            return False
    
    def _read_csv(self, path: str, options: Dict[str, Any]) -> DataFrame:
        """Read CSV file with options."""
        reader = self.spark.read.format("csv")
        
        # Apply all options
        for key, value in options.items():
            reader = reader.option(key, value)
        
        # Load data
        df = reader.load(path)
        
        # Log schema info
        self.logger.debug(f"Read CSV with schema: {df.schema.simpleString()}")
        self.logger.debug(f"Row count: {df.count()}")
        
        return df
    
    def _prepare_read_options(self, user_options: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare CSV read options."""
        options = self.default_read_options.copy()
        
        # Handle specific user options
        if "delimiter" in user_options:
            options["sep"] = user_options["delimiter"]
            
        if "encoding" in user_options:
            options["encoding"] = user_options["encoding"]
            
        if "header" in user_options:
            options["header"] = str(user_options["header"]).lower()
            
        if "infer_schema" in user_options:
            options["inferSchema"] = str(user_options["infer_schema"]).lower()
            
        if "skip_rows" in user_options:
            # Spark doesn't have skip_rows, but we can handle it differently
            options["skipRows"] = user_options["skip_rows"]
            
        # Schema handling
        if "schema" in user_options:
            # User provided schema overrides inference
            options["inferSchema"] = "false"
            
        return options
    
    def _apply_transformations(self, df: DataFrame, options: Dict[str, Any]) -> DataFrame:
        """Apply data transformations."""
        # Clean column names
        if options.get("clean_column_names", True):
            df = self._clean_column_names(df)
        
        # Trim whitespace
        if options.get("trim_whitespace", True):
            df = self._trim_whitespace(df)
        
        # Handle nulls
        if options.get("handle_nulls", True):
            df = self._handle_nulls(df, options)
        
        # Apply custom transformations
        if "transformations" in options:
            df = self._apply_custom_transformations(df, options["transformations"])
        
        # Filter rows if specified
        if "filter" in options:
            df = df.filter(options["filter"])
        
        # Select columns if specified
        if "select_columns" in options:
            df = df.select(options["select_columns"])
        
        return df
    
    def _clean_column_names(self, df: DataFrame) -> DataFrame:
        """Clean column names for compatibility."""
        # Replace special characters with underscores
        for old_name in df.columns:
            new_name = (
                old_name
                .strip()
                .replace(" ", "_")
                .replace("-", "_")
                .replace(".", "_")
                .replace("(", "")
                .replace(")", "")
                .replace("/", "_")
                .replace("\\", "_")
            )
            # Remove consecutive underscores
            new_name = regexp_replace(new_name, "_+", "_").strip("_")
            
            if new_name != old_name:
                df = df.withColumnRenamed(old_name, new_name)
                self.logger.debug(f"Renamed column '{old_name}' to '{new_name}'")
        
        return df
    
    def _trim_whitespace(self, df: DataFrame) -> DataFrame:
        """Trim whitespace from string columns."""
        string_columns = [
            field.name for field in df.schema.fields
            if field.dataType == StringType()
        ]
        
        for col_name in string_columns:
            df = df.withColumn(col_name, trim(col(col_name)))
        
        return df
    
    def _handle_nulls(self, df: DataFrame, options: Dict[str, Any]) -> DataFrame:
        """Handle null values based on options."""
        null_strategy = options.get("null_strategy", "keep")
        
        if null_strategy == "drop":
            # Drop rows with any null
            df = df.dropna()
        elif null_strategy == "fill":
            # Fill nulls with default values
            fill_values = options.get("null_fill_values", {})
            df = df.fillna(fill_values)
        elif isinstance(null_strategy, dict):
            # Column-specific strategies
            for col_name, strategy in null_strategy.items():
                if strategy == "drop":
                    df = df.filter(col(col_name).isNotNull())
                elif isinstance(strategy, (str, int, float)):
                    df = df.fillna({col_name: strategy})
        
        return df
    
    def _apply_custom_transformations(
        self,
        df: DataFrame,
        transformations: List[Dict[str, Any]]
    ) -> DataFrame:
        """Apply custom transformations."""
        for transform in transformations:
            transform_type = transform.get("type")
            
            if transform_type == "cast":
                col_name = transform["column"]
                data_type = transform["data_type"]
                df = df.withColumn(col_name, col(col_name).cast(data_type))
                
            elif transform_type == "rename":
                old_name = transform["old_name"]
                new_name = transform["new_name"]
                df = df.withColumnRenamed(old_name, new_name)
                
            elif transform_type == "derive":
                new_col = transform["new_column"]
                expression = transform["expression"]
                df = df.withColumn(new_col, expression)
                
            elif transform_type == "parse_date":
                col_name = transform["column"]
                date_format = transform.get("format", "yyyy-MM-dd")
                df = df.withColumn(col_name, to_date(col(col_name), date_format))
                
            elif transform_type == "parse_timestamp":
                col_name = transform["column"]
                ts_format = transform.get("format", "yyyy-MM-dd HH:mm:ss")
                df = df.withColumn(col_name, to_timestamp(col(col_name), ts_format))
        
        return df
    
    def _optimize_dataframe(
        self,
        df: DataFrame,
        output_format: str,
        options: Dict[str, Any]
    ) -> DataFrame:
        """Optimize DataFrame for output format."""
        # Repartition if specified
        if "partitions" in options:
            num_partitions = options["partitions"]
            df = df.repartition(num_partitions)
            self.logger.debug(f"Repartitioned to {num_partitions} partitions")
        
        # Coalesce for small outputs
        elif options.get("coalesce", False):
            target_partitions = options.get("target_partitions", 1)
            df = df.coalesce(target_partitions)
            self.logger.debug(f"Coalesced to {target_partitions} partitions")
        
        # Sort if specified
        if "sort_by" in options:
            sort_cols = options["sort_by"]
            if isinstance(sort_cols, str):
                sort_cols = [sort_cols]
            df = df.orderBy(sort_cols)
        
        # Cache if needed for multiple operations
        if options.get("cache", False):
            df = df.cache()
            self.logger.debug("Cached DataFrame")
        
        return df
    
    def _should_use_streaming(self, input_path: str, options: Dict[str, Any]) -> bool:
        """Determine if streaming mode should be used."""
        # Check file size if possible
        try:
            import os
            file_size = os.path.getsize(input_path)
            # Use streaming for files > 1GB
            if file_size > 1024 * 1024 * 1024:
                return True
        except:
            pass
        
        # Check if user specified large file handling
        return options.get("large_file_mode", False)
    
    # Output format writers
    
    def _write_parquet(self, df: DataFrame, path: str, options: Dict[str, Any]) -> None:
        """Write DataFrame as Parquet."""
        writer = df.write.mode(options.get("mode", "overwrite"))
        
        # Compression
        compression = options.get("compression", "snappy")
        writer = writer.option("compression", compression)
        
        # Partitioning
        if "partition_by" in options:
            partition_cols = options["partition_by"]
            if isinstance(partition_cols, str):
                partition_cols = [partition_cols]
            writer = writer.partitionBy(*partition_cols)
        
        writer.parquet(path)
        self.logger.info(f"Wrote Parquet to {path} with compression: {compression}")
    
    def _write_delta(self, df: DataFrame, path: str, options: Dict[str, Any]) -> None:
        """Write DataFrame as Delta table."""
        writer = df.write.mode(options.get("mode", "overwrite"))
        
        # Delta-specific options
        if "overwriteSchema" in options:
            writer = writer.option("overwriteSchema", options["overwriteSchema"])
        
        # Partitioning
        if "partition_by" in options:
            partition_cols = options["partition_by"]
            if isinstance(partition_cols, str):
                partition_cols = [partition_cols]
            writer = writer.partitionBy(*partition_cols)
        
        writer.format("delta").save(path)
        self.logger.info(f"Wrote Delta table to {path}")
    
    def _write_json(self, df: DataFrame, path: str, options: Dict[str, Any]) -> None:
        """Write DataFrame as JSON."""
        writer = df.write.mode(options.get("mode", "overwrite"))
        
        # JSON options
        if "compression" in options:
            writer = writer.option("compression", options["compression"])
        
        writer.json(path)
        self.logger.info(f"Wrote JSON to {path}")
    
    def _write_orc(self, df: DataFrame, path: str, options: Dict[str, Any]) -> None:
        """Write DataFrame as ORC."""
        writer = df.write.mode(options.get("mode", "overwrite"))
        
        # ORC compression
        compression = options.get("compression", "zlib")
        writer = writer.option("compression", compression)
        
        writer.orc(path)
        self.logger.info(f"Wrote ORC to {path} with compression: {compression}")
    
    def _write_avro(self, df: DataFrame, path: str, options: Dict[str, Any]) -> None:
        """Write DataFrame as Avro."""
        writer = df.write.mode(options.get("mode", "overwrite"))
        
        # Avro specific options
        if "compression" in options:
            writer = writer.option("compression", options["compression"])
        
        writer.format("avro").save(path)
        self.logger.info(f"Wrote Avro to {path}")
    
    def _write_csv(self, df: DataFrame, path: str, options: Dict[str, Any]) -> None:
        """Write DataFrame as CSV."""
        writer = df.write.mode(options.get("mode", "overwrite"))
        
        # CSV options
        writer = writer.option("header", options.get("header", "true"))
        writer = writer.option("sep", options.get("delimiter", ","))
        writer = writer.option("quote", options.get("quote", '"'))
        writer = writer.option("escape", options.get("escape", '"'))
        writer = writer.option("encoding", options.get("encoding", "UTF-8"))
        
        # Compression
        if "compression" in options:
            writer = writer.option("compression", options["compression"])
        
        writer.csv(path)
        self.logger.info(f"Wrote CSV to {path}")