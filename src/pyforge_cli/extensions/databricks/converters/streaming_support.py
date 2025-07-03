"""
Streaming Support for Large Files in Databricks

This module provides streaming capabilities for processing ultra-large files
with memory-efficient operations and progress tracking.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable, Union
from pathlib import Path
from datetime import datetime
import threading
import queue

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.functions import col, count, sum as spark_sum, max as spark_max, min as spark_min


class StreamingSupport:
    """
    Streaming support for processing large files.
    
    Features:
    - Memory-efficient processing
    - Progress tracking and reporting
    - Error recovery with checkpointing
    - Micro-batch optimization
    - Real-time statistics
    """
    
    def __init__(self, spark_session: Optional[SparkSession] = None):
        """
        Initialize streaming support.
        
        Args:
            spark_session: Optional Spark session to use
        """
        self.logger = logging.getLogger("pyforge.extensions.databricks.streaming")
        self.spark = spark_session or SparkSession.builder.getOrCreate()
        
        # Configure streaming optimizations
        self._configure_streaming()
        
        # Active streaming queries
        self.active_queries: Dict[str, StreamingQuery] = {}
        
        # Progress tracking
        self.progress_queue = queue.Queue()
        self.progress_thread: Optional[threading.Thread] = None
        
    def _configure_streaming(self):
        """Configure Spark streaming settings."""
        # Set streaming configurations
        self.spark.conf.set("spark.sql.streaming.schemaInference", "true")
        self.spark.conf.set("spark.sql.streaming.stopGracefullyOnShutdown", "true")
        
        # Micro-batch settings
        self.spark.conf.set("spark.sql.streaming.pollingDelay", "10")
        self.spark.conf.set("spark.sql.streaming.noDataMicroBatches.enabled", "false")
        
        # State store settings
        self.spark.conf.set("spark.sql.streaming.stateStore.compression.codec", "lz4")
        
    def process_file_streaming(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        input_format: str,
        output_format: str,
        options: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Process file using streaming for memory efficiency.
        
        Args:
            input_path: Input file path
            output_path: Output path
            input_format: Input format (csv, json, etc.)
            output_format: Output format
            options: Processing options
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if successful
        """
        try:
            input_path = str(input_path)
            output_path = str(output_path)
            query_name = f"stream_{Path(input_path).stem}_{int(time.time())}"
            
            self.logger.info(
                f"Starting streaming processing: {input_path} -> {output_path}"
            )
            
            # Create streaming DataFrame
            stream_df = self._create_stream_reader(
                input_path, input_format, options
            )
            
            if stream_df is None:
                return False
            
            # Apply transformations
            stream_df = self._apply_streaming_transformations(
                stream_df, options
            )
            
            # Start streaming query
            query = self._create_stream_writer(
                stream_df,
                output_path,
                output_format,
                query_name,
                options
            )
            
            if query is None:
                return False
            
            # Store active query
            self.active_queries[query_name] = query
            
            # Start progress tracking if callback provided
            if progress_callback:
                self._start_progress_tracking(query, progress_callback)
            
            # Wait for completion
            success = self._wait_for_completion(query, options)
            
            # Cleanup
            self.active_queries.pop(query_name, None)
            
            if success:
                self.logger.info("Streaming processing completed successfully")
            else:
                self.logger.error("Streaming processing failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error in streaming processing: {e}", exc_info=True)
            return False
    
    def _create_stream_reader(
        self,
        path: str,
        format: str,
        options: Dict[str, Any]
    ) -> Optional[DataFrame]:
        """Create streaming DataFrame reader."""
        try:
            reader = self.spark.readStream.format(format)
            
            # Common options
            if format == "csv":
                reader = reader.option("header", options.get("header", "true"))
                reader = reader.option("inferSchema", options.get("infer_schema", "true"))
                reader = reader.option("maxFilesPerTrigger", options.get("files_per_batch", 1))
                
            elif format == "json":
                reader = reader.option("multiLine", options.get("multiline", "true"))
                reader = reader.option("maxFilesPerTrigger", options.get("files_per_batch", 1))
                
            elif format == "parquet":
                reader = reader.option("maxFilesPerTrigger", options.get("files_per_batch", 1))
            
            # Schema handling
            if "schema" in options:
                reader = reader.schema(options["schema"])
            
            # File-specific options
            if options.get("process_subdirectories", False):
                reader = reader.option("recursiveFileLookup", "true")
            
            # Load stream
            stream_df = reader.load(path)
            
            self.logger.info(f"Created streaming reader for {format} format")
            return stream_df
            
        except Exception as e:
            self.logger.error(f"Error creating stream reader: {e}")
            return None
    
    def _apply_streaming_transformations(
        self,
        df: DataFrame,
        options: Dict[str, Any]
    ) -> DataFrame:
        """Apply transformations suitable for streaming."""
        # Note: Some transformations are not supported in streaming
        # We focus on row-level operations
        
        # Filter if specified
        if "filter" in options:
            df = df.filter(options["filter"])
        
        # Select columns if specified
        if "select_columns" in options:
            df = df.select(options["select_columns"])
        
        # Add processing timestamp
        if options.get("add_timestamp", True):
            from pyspark.sql.functions import current_timestamp
            df = df.withColumn("_processed_at", current_timestamp())
        
        # Watermarking for stateful operations
        if "watermark_column" in options:
            watermark_duration = options.get("watermark_duration", "10 minutes")
            df = df.withWatermark(options["watermark_column"], watermark_duration)
        
        return df
    
    def _create_stream_writer(
        self,
        df: DataFrame,
        path: str,
        format: str,
        query_name: str,
        options: Dict[str, Any]
    ) -> Optional[StreamingQuery]:
        """Create streaming query writer."""
        try:
            # Configure checkpoint location
            checkpoint_path = options.get(
                "checkpoint_location",
                f"{path}_checkpoint_{query_name}"
            )
            
            writer = (
                df.writeStream
                .outputMode(options.get("output_mode", "append"))
                .format(format)
                .option("path", path)
                .option("checkpointLocation", checkpoint_path)
                .queryName(query_name)
            )
            
            # Format-specific options
            if format == "parquet":
                writer = writer.option(
                    "compression",
                    options.get("compression", "snappy")
                )
                
            elif format == "json":
                writer = writer.option(
                    "compression",
                    options.get("compression", "gzip")
                )
            
            # Trigger configuration
            trigger_type = options.get("trigger_type", "processingTime")
            
            if trigger_type == "processingTime":
                interval = options.get("trigger_interval", "10 seconds")
                writer = writer.trigger(processingTime=interval)
                
            elif trigger_type == "once":
                writer = writer.trigger(once=True)
                
            elif trigger_type == "continuous":
                interval = options.get("trigger_interval", "1 second")
                writer = writer.trigger(continuous=interval)
            
            # Partitioning
            if "partition_by" in options:
                writer = writer.partitionBy(options["partition_by"])
            
            # Start query
            query = writer.start()
            
            self.logger.info(
                f"Started streaming query '{query_name}' with checkpoint at {checkpoint_path}"
            )
            
            return query
            
        except Exception as e:
            self.logger.error(f"Error creating stream writer: {e}")
            return None
    
    def _wait_for_completion(
        self,
        query: StreamingQuery,
        options: Dict[str, Any]
    ) -> bool:
        """Wait for streaming query completion."""
        try:
            timeout = options.get("timeout_seconds")
            
            if timeout:
                # Wait with timeout
                start_time = time.time()
                
                while query.isActive and (time.time() - start_time) < timeout:
                    time.sleep(1)
                    
                    # Check for exceptions
                    if query.exception() is not None:
                        raise query.exception()
                
                if query.isActive:
                    self.logger.warning("Query timeout reached, stopping...")
                    query.stop()
                    return False
            else:
                # Wait indefinitely
                query.awaitTermination()
            
            # Check final status
            if query.exception() is not None:
                raise query.exception()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during query execution: {e}")
            if query.isActive:
                query.stop()
            return False
    
    def _start_progress_tracking(
        self,
        query: StreamingQuery,
        callback: Callable
    ):
        """Start progress tracking thread."""
        def track_progress():
            while query.isActive:
                try:
                    progress = query.lastProgress
                    if progress:
                        # Extract progress information
                        progress_info = {
                            "timestamp": datetime.now().isoformat(),
                            "id": progress.get("id"),
                            "runId": progress.get("runId"),
                            "batchId": progress.get("batchId"),
                            "numInputRows": progress.get("numInputRows", 0),
                            "inputRowsPerSecond": progress.get("inputRowsPerSecond", 0),
                            "processedRowsPerSecond": progress.get("processedRowsPerSecond", 0)
                        }
                        
                        # Get source progress
                        sources = progress.get("sources", [])
                        if sources:
                            source = sources[0]
                            progress_info.update({
                                "description": source.get("description"),
                                "startOffset": source.get("startOffset"),
                                "endOffset": source.get("endOffset"),
                                "numInputRows": source.get("numInputRows", 0)
                            })
                        
                        # Call callback
                        callback(progress_info)
                    
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error tracking progress: {e}")
        
        self.progress_thread = threading.Thread(target=track_progress, daemon=True)
        self.progress_thread.start()
    
    def estimate_file_size_for_streaming(
        self,
        file_path: Union[str, Path],
        format: str
    ) -> Dict[str, Any]:
        """
        Estimate if file should use streaming based on size and format.
        
        Args:
            file_path: File path to check
            format: File format
            
        Returns:
            Dict[str, Any]: Streaming recommendation
        """
        try:
            import os
            file_size = os.path.getsize(str(file_path))
            
            # Streaming thresholds by format
            thresholds = {
                "csv": 500 * 1024 * 1024,     # 500MB
                "json": 200 * 1024 * 1024,    # 200MB
                "xml": 100 * 1024 * 1024,     # 100MB
                "parquet": 1024 * 1024 * 1024, # 1GB
                "avro": 500 * 1024 * 1024     # 500MB
            }
            
            threshold = thresholds.get(format, 500 * 1024 * 1024)
            use_streaming = file_size > threshold
            
            return {
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "format": format,
                "threshold_mb": round(threshold / (1024 * 1024), 2),
                "recommend_streaming": use_streaming,
                "reason": (
                    f"File size ({file_size / (1024 * 1024):.1f}MB) "
                    f"{'exceeds' if use_streaming else 'below'} "
                    f"streaming threshold ({threshold / (1024 * 1024):.1f}MB)"
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error estimating file size: {e}")
            return {
                "recommend_streaming": False,
                "reason": "Could not determine file size"
            }
    
    def stop_all_streams(self):
        """Stop all active streaming queries."""
        for query_name, query in self.active_queries.items():
            try:
                if query.isActive:
                    self.logger.info(f"Stopping query: {query_name}")
                    query.stop()
            except Exception as e:
                self.logger.error(f"Error stopping query {query_name}: {e}")
        
        self.active_queries.clear()
    
    def get_stream_statistics(
        self,
        query_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get statistics for an active streaming query.
        
        Args:
            query_name: Name of the query
            
        Returns:
            Optional[Dict[str, Any]]: Query statistics
        """
        query = self.active_queries.get(query_name)
        
        if not query or not query.isActive:
            return None
        
        try:
            progress = query.lastProgress
            status = query.status
            
            return {
                "name": query.name,
                "id": query.id,
                "runId": query.runId,
                "isActive": query.isActive,
                "progress": progress,
                "status": {
                    "message": status["message"],
                    "isDataAvailable": status["isDataAvailable"],
                    "isTriggerActive": status["isTriggerActive"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stream statistics: {e}")
            return None