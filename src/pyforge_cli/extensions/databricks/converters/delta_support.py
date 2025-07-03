"""
Delta Lake Support for Databricks Extension

This module provides Delta Lake format support with advanced features like
schema evolution, time travel, ACID transactions, and optimized writes.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType
from delta import DeltaTable, configure_spark_with_delta_pip


class DeltaLakeSupport:
    """
    Delta Lake format support for PyForge Databricks extension.
    
    Features:
    - ACID transactions
    - Schema evolution
    - Time travel queries
    - Optimized writes and compaction
    - Z-ordering for query optimization
    - Change data capture (CDC)
    """
    
    def __init__(self, spark_session: Optional[SparkSession] = None):
        """
        Initialize Delta Lake support.
        
        Args:
            spark_session: Optional Spark session to use
        """
        self.logger = logging.getLogger("pyforge.extensions.databricks.delta")
        
        # Configure Spark for Delta if needed
        if spark_session:
            self.spark = spark_session
        else:
            builder = SparkSession.builder.appName("PyForge-Delta")
            self.spark = configure_spark_with_delta_pip(builder).getOrCreate()
        
        # Configure Delta optimizations
        self._configure_delta_optimizations()
        
    def _configure_delta_optimizations(self):
        """Configure Delta Lake optimizations."""
        # Enable adaptive query execution
        self.spark.conf.set("spark.sql.adaptive.enabled", "true")
        self.spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
        
        # Delta-specific optimizations
        self.spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
        self.spark.conf.set("spark.databricks.delta.merge.optimizeWrite.enabled", "true")
        self.spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
        self.spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
        
    def write_delta(
        self,
        df: DataFrame,
        path: str,
        options: Dict[str, Any]
    ) -> bool:
        """
        Write DataFrame to Delta format with advanced options.
        
        Args:
            df: DataFrame to write
            path: Output path for Delta table
            options: Write options
            
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info(f"Writing Delta table to {path}")
            
            # Determine write mode
            mode = options.get("mode", "overwrite")
            
            if mode == "merge":
                # Use merge for upsert operations
                return self._merge_delta(df, path, options)
            
            # Standard write modes
            writer = df.write.mode(mode)
            
            # Partitioning
            if "partition_by" in options:
                partition_cols = options["partition_by"]
                if isinstance(partition_cols, str):
                    partition_cols = [partition_cols]
                writer = writer.partitionBy(*partition_cols)
                self.logger.info(f"Partitioning by: {partition_cols}")
            
            # Schema evolution
            if options.get("merge_schema", False) and mode == "append":
                writer = writer.option("mergeSchema", "true")
                self.logger.info("Schema merge enabled")
            
            if options.get("overwrite_schema", False) and mode == "overwrite":
                writer = writer.option("overwriteSchema", "true")
                self.logger.info("Schema overwrite enabled")
            
            # Optimize writes
            if options.get("optimize_write", True):
                writer = writer.option("optimizeWrite", "true")
            
            # Write data
            writer.format("delta").save(path)
            
            # Post-write optimizations
            if options.get("optimize_after_write", False):
                self._optimize_delta_table(path, options)
            
            # Create table if requested
            if "table_name" in options:
                self._create_delta_table(path, options["table_name"], options)
            
            self.logger.info("Delta write completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing Delta table: {e}", exc_info=True)
            return False
    
    def _merge_delta(
        self,
        source_df: DataFrame,
        target_path: str,
        options: Dict[str, Any]
    ) -> bool:
        """Perform merge (upsert) operation on Delta table."""
        try:
            # Check if Delta table exists
            if not DeltaTable.isDeltaTable(self.spark, target_path):
                self.logger.info("Target Delta table doesn't exist, creating new table")
                source_df.write.format("delta").save(target_path)
                return True
            
            # Load target Delta table
            target_table = DeltaTable.forPath(self.spark, target_path)
            
            # Get merge keys
            merge_keys = options.get("merge_keys", [])
            if not merge_keys:
                raise ValueError("merge_keys must be specified for merge operation")
            
            # Build merge condition
            merge_conditions = []
            for key in merge_keys:
                merge_conditions.append(f"source.{key} = target.{key}")
            merge_condition = " AND ".join(merge_conditions)
            
            self.logger.info(f"Merge condition: {merge_condition}")
            
            # Perform merge
            merge_builder = target_table.alias("target").merge(
                source_df.alias("source"),
                merge_condition
            )
            
            # Update existing records
            update_cols = options.get("update_columns")
            if update_cols:
                update_dict = {col: f"source.{col}" for col in update_cols}
            else:
                # Update all columns except merge keys
                update_dict = {
                    col: f"source.{col}" 
                    for col in source_df.columns 
                    if col not in merge_keys
                }
            
            merge_builder = merge_builder.whenMatchedUpdate(set=update_dict)
            
            # Insert new records
            merge_builder = merge_builder.whenNotMatchedInsertAll()
            
            # Execute merge
            merge_builder.execute()
            
            self.logger.info("Delta merge completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in Delta merge: {e}", exc_info=True)
            return False
    
    def read_delta(
        self,
        path: str,
        options: Dict[str, Any]
    ) -> Optional[DataFrame]:
        """
        Read Delta table with time travel and other options.
        
        Args:
            path: Delta table path
            options: Read options
            
        Returns:
            Optional[DataFrame]: DataFrame or None if error
        """
        try:
            self.logger.info(f"Reading Delta table from {path}")
            
            # Check for time travel options
            if "timestamp_as_of" in options:
                timestamp = options["timestamp_as_of"]
                df = self.spark.read.format("delta").option("timestampAsOf", timestamp).load(path)
                self.logger.info(f"Reading Delta table as of timestamp: {timestamp}")
                
            elif "version_as_of" in options:
                version = options["version_as_of"]
                df = self.spark.read.format("delta").option("versionAsOf", version).load(path)
                self.logger.info(f"Reading Delta table version: {version}")
                
            else:
                # Read latest version
                df = self.spark.read.format("delta").load(path)
            
            # Apply filters if specified
            if "filter" in options:
                df = df.filter(options["filter"])
            
            # Select columns if specified
            if "select_columns" in options:
                df = df.select(options["select_columns"])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading Delta table: {e}", exc_info=True)
            return None
    
    def get_table_history(self, path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get Delta table history.
        
        Args:
            path: Delta table path
            limit: Number of history entries to return
            
        Returns:
            List[Dict[str, Any]]: Table history
        """
        try:
            delta_table = DeltaTable.forPath(self.spark, path)
            history_df = delta_table.history(limit)
            
            # Convert to list of dicts
            history = []
            for row in history_df.collect():
                history.append({
                    "version": row.version,
                    "timestamp": row.timestamp,
                    "operation": row.operation,
                    "user": getattr(row, "userName", "unknown"),
                    "metrics": row.operationMetrics
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting table history: {e}")
            return []
    
    def _optimize_delta_table(self, path: str, options: Dict[str, Any]):
        """Optimize Delta table with compaction and Z-ordering."""
        try:
            delta_table = DeltaTable.forPath(self.spark, path)
            
            # Compact small files
            self.logger.info("Running Delta optimization...")
            optimize_builder = delta_table.optimize()
            
            # Z-order by columns if specified
            z_order_cols = options.get("z_order_by", [])
            if z_order_cols:
                if isinstance(z_order_cols, str):
                    z_order_cols = [z_order_cols]
                    
                self.logger.info(f"Z-ordering by columns: {z_order_cols}")
                optimize_builder.executeZOrderBy(z_order_cols)
            else:
                optimize_builder.executeCompaction()
            
            # Vacuum old files if requested
            if options.get("vacuum", False):
                retention_hours = options.get("retention_hours", 168)  # 7 days default
                self.logger.info(f"Vacuuming with retention: {retention_hours} hours")
                delta_table.vacuum(retention_hours)
                
        except Exception as e:
            self.logger.error(f"Error optimizing Delta table: {e}")
    
    def _create_delta_table(self, path: str, table_name: str, options: Dict[str, Any]):
        """Create a Delta table in the metastore."""
        try:
            # Parse table name (could be database.table)
            if "." in table_name:
                database, table = table_name.split(".", 1)
                self.spark.sql(f"USE {database}")
            else:
                table = table_name
            
            # Create table
            create_sql = f"CREATE TABLE IF NOT EXISTS {table} USING DELTA LOCATION '{path}'"
            
            # Add table properties if specified
            if "table_properties" in options:
                props = options["table_properties"]
                prop_string = ", ".join([f"'{k}' = '{v}'" for k, v in props.items()])
                create_sql += f" TBLPROPERTIES ({prop_string})"
            
            self.spark.sql(create_sql)
            self.logger.info(f"Created Delta table: {table_name}")
            
            # Add table comment if specified
            if "comment" in options:
                comment_sql = f"COMMENT ON TABLE {table} IS '{options['comment']}'"
                self.spark.sql(comment_sql)
                
        except Exception as e:
            self.logger.error(f"Error creating Delta table: {e}")
    
    def enable_change_data_feed(self, path: str) -> bool:
        """
        Enable Change Data Feed for a Delta table.
        
        Args:
            path: Delta table path
            
        Returns:
            bool: True if successful
        """
        try:
            delta_table = DeltaTable.forPath(self.spark, path)
            
            # Set table property to enable CDF
            self.spark.sql(f"""
                ALTER TABLE delta.`{path}`
                SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
            """)
            
            self.logger.info(f"Enabled Change Data Feed for {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enabling Change Data Feed: {e}")
            return False
    
    def read_change_data(
        self,
        path: str,
        start_version: Optional[int] = None,
        end_version: Optional[int] = None
    ) -> Optional[DataFrame]:
        """
        Read change data from a Delta table with CDF enabled.
        
        Args:
            path: Delta table path
            start_version: Starting version (inclusive)
            end_version: Ending version (inclusive)
            
        Returns:
            Optional[DataFrame]: Change data or None
        """
        try:
            reader = self.spark.read.format("delta").option("readChangeFeed", "true")
            
            if start_version is not None:
                reader = reader.option("startingVersion", start_version)
                
            if end_version is not None:
                reader = reader.option("endingVersion", end_version)
            
            cdf_df = reader.load(path)
            
            self.logger.info(
                f"Read change data from version {start_version} to {end_version}"
            )
            
            return cdf_df
            
        except Exception as e:
            self.logger.error(f"Error reading change data: {e}")
            return None
    
    def convert_to_delta(
        self,
        source_df: DataFrame,
        target_path: str,
        source_format: str,
        options: Dict[str, Any]
    ) -> bool:
        """
        Convert data from other formats to Delta.
        
        Args:
            source_df: Source DataFrame
            target_path: Target Delta path
            source_format: Source format name
            options: Conversion options
            
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info(f"Converting {source_format} to Delta format")
            
            # Add conversion metadata
            conversion_metadata = {
                "source_format": source_format,
                "conversion_timestamp": datetime.now().isoformat(),
                "pyforge_version": "0.5.1"
            }
            
            # Add metadata to table properties
            if "table_properties" not in options:
                options["table_properties"] = {}
            options["table_properties"].update(conversion_metadata)
            
            # Perform conversion
            return self.write_delta(source_df, target_path, options)
            
        except Exception as e:
            self.logger.error(f"Error converting to Delta: {e}")
            return False