"""
Spark-optimized XML Converter for Databricks

This module implements an XML converter using Apache Spark with advanced features
for handling nested structures, namespaces, and array flattening.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    explode_outer,
    flatten,
    regexp_replace,
    to_json,
    when,
)
from pyspark.sql.types import ArrayType, MapType, StructType


class SparkXMLConverter:
    """
    XML converter optimized for Apache Spark.

    Features:
    - Nested structure flattening
    - Namespace handling
    - Array expansion options
    - XPath-like selection
    - Schema inference and validation
    """

    def __init__(self, spark_session: Optional[SparkSession] = None):
        """
        Initialize the Spark XML converter.

        Args:
            spark_session: Optional Spark session to use
        """
        self.logger = logging.getLogger(
            "pyforge.extensions.databricks.converters.spark_xml"
        )
        self.spark = spark_session or SparkSession.builder.getOrCreate()

        # Ensure spark-xml package is available
        self._ensure_xml_support()

        # Default XML options
        self.default_options = {
            "rowTag": "row",
            "rootTag": "rows",
            "valueTag": "_VALUE",
            "attributePrefix": "_",
            "nullValue": "",
            "dateFormat": "yyyy-MM-dd",
            "timestampFormat": "yyyy-MM-dd'T'HH:mm:ss",
        }

        # Flattening strategies
        self.flattening_strategies = {
            "none": self._no_flattening,
            "simple": self._simple_flattening,
            "full": self._full_flattening,
            "custom": self._custom_flattening,
        }

    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        output_format: str,
        options: Dict[str, Any],
    ) -> bool:
        """
        Convert XML file to specified output format.

        Args:
            input_path: Input XML file path
            output_path: Output file path
            output_format: Target format
            options: Conversion options

        Returns:
            bool: True if successful
        """
        try:
            input_path = str(input_path)
            output_path = str(output_path)

            self.logger.info(
                f"Starting Spark XML conversion: {input_path} -> {output_path}"
            )

            # Read XML
            df = self._read_xml(input_path, options)

            if df is None:
                return False

            # Apply flattening strategy
            flattening = options.get("flattening", "simple")
            if flattening not in self.flattening_strategies:
                flattening = "simple"

            df = self.flattening_strategies[flattening](df, options)

            # Apply transformations
            df = self._apply_transformations(df, options)

            # Write output
            success = self._write_output(df, output_path, output_format, options)

            if success:
                self.logger.info(f"Successfully converted XML to {output_format}")

                # Log schema for debugging
                self.logger.debug(f"Output schema: {df.schema.simpleString()}")
                self.logger.debug(f"Row count: {df.count()}")

            return success

        except Exception as e:
            self.logger.error(f"Error in Spark XML conversion: {e}", exc_info=True)
            return False

    def _ensure_xml_support(self):
        """Ensure spark-xml package is available."""
        try:
            # Try to load XML package
            self.spark._jvm.com.databricks.spark.xml.XmlReader
        except Exception:
            # Try to add package dynamically
            try:
                self.spark.sparkContext.addPyFile(
                    "https://repo1.maven.org/maven2/com/databricks/spark-xml_2.12/0.15.0/spark-xml_2.12-0.15.0.jar"
                )
            except Exception as e:
                self.logger.warning(
                    f"Could not load spark-xml package. "
                    f"XML conversion may fail: {e}"
                )

    def _read_xml(self, path: str, options: Dict[str, Any]) -> Optional[DataFrame]:
        """Read XML file with options."""
        try:
            # Prepare read options
            read_options = self.default_options.copy()

            # Handle specific options
            if "row_tag" in options:
                read_options["rowTag"] = options["row_tag"]
            if "root_tag" in options:
                read_options["rootTag"] = options["root_tag"]
            if "value_tag" in options:
                read_options["valueTag"] = options["value_tag"]
            if "attribute_prefix" in options:
                read_options["attributePrefix"] = options["attribute_prefix"]

            # Schema handling
            if "schema" in options:
                schema = options["schema"]
                if isinstance(schema, str):
                    # Schema provided as JSON string
                    schema = StructType.fromJson(json.loads(schema))
                read_options["schema"] = schema

            # Read XML
            df = self.spark.read.format("xml").options(**read_options).load(path)

            # Handle namespaces if requested
            if options.get("handle_namespaces", True):
                df = self._handle_namespaces(df, options)

            self.logger.debug(f"Read XML with {df.count()} rows")
            self.logger.debug(f"Schema: {df.schema}")

            return df

        except Exception as e:
            self.logger.error(f"Error reading XML: {e}")
            return None

    def _handle_namespaces(self, df: DataFrame, options: Dict[str, Any]) -> DataFrame:
        """Handle XML namespaces."""
        namespace_handling = options.get("namespace_handling", "remove")

        if namespace_handling == "remove":
            # Remove namespace prefixes from column names
            for col_name in df.columns:
                if ":" in col_name:
                    new_name = col_name.split(":")[-1]
                    df = df.withColumnRenamed(col_name, new_name)

        elif namespace_handling == "preserve":
            # Keep namespaces but clean column names
            for col_name in df.columns:
                if ":" in col_name:
                    new_name = col_name.replace(":", "_")
                    df = df.withColumnRenamed(col_name, new_name)

        return df

    def _no_flattening(self, df: DataFrame, options: Dict[str, Any]) -> DataFrame:
        """No flattening - preserve nested structure."""
        return df

    def _simple_flattening(self, df: DataFrame, options: Dict[str, Any]) -> DataFrame:
        """Simple flattening - expand one level of nesting."""
        flattened_df = df

        # Identify nested columns
        nested_cols = self._find_nested_columns(df.schema)

        for col_name, col_type in nested_cols.items():
            if isinstance(col_type, StructType):
                # Expand struct
                flattened_df = self._expand_struct(flattened_df, col_name, options)

            elif isinstance(col_type, ArrayType):
                # Handle array based on options
                array_handling = options.get("array_handling", "first")

                if array_handling == "explode":
                    flattened_df = flattened_df.withColumn(
                        col_name, explode_outer(col(col_name))
                    )
                elif array_handling == "first":
                    flattened_df = flattened_df.withColumn(
                        col_name, when(col(col_name).isNotNull(), col(col_name)[0])
                    )
                elif array_handling == "json":
                    flattened_df = flattened_df.withColumn(
                        col_name, to_json(col(col_name))
                    )

        return flattened_df

    def _full_flattening(self, df: DataFrame, options: Dict[str, Any]) -> DataFrame:
        """Full recursive flattening of all nested structures."""
        max_depth = options.get("max_flattening_depth", 5)
        current_depth = 0

        while current_depth < max_depth:
            nested_cols = self._find_nested_columns(df.schema)

            if not nested_cols:
                break  # No more nested columns

            for col_name, col_type in nested_cols.items():
                if isinstance(col_type, StructType):
                    df = self._expand_struct(df, col_name, options)

                elif isinstance(col_type, ArrayType):
                    # For full flattening, always explode arrays
                    df = df.withColumn(col_name, explode_outer(col(col_name)))

                    # If array contains structs, they'll be flattened in next iteration
                    if isinstance(col_type.elementType, StructType):
                        df = self._expand_struct(df, col_name, options)

            current_depth += 1

        if current_depth >= max_depth:
            self.logger.warning(f"Reached maximum flattening depth ({max_depth})")

        return df

    def _custom_flattening(self, df: DataFrame, options: Dict[str, Any]) -> DataFrame:
        """Custom flattening based on user-provided rules."""
        rules = options.get("flattening_rules", [])

        for rule in rules:
            rule_type = rule.get("type")
            path = rule.get("path")

            if rule_type == "expand":
                df = self._expand_path(df, path, options)

            elif rule_type == "explode":
                df = df.withColumn(path, explode_outer(col(path)))

            elif rule_type == "select":
                # XPath-like selection
                selected_cols = rule.get("columns", [])
                df = df.select(*selected_cols)

            elif rule_type == "flatten_array":
                df = df.withColumn(path, flatten(col(path)))

        return df

    def _find_nested_columns(self, schema: StructType) -> Dict[str, Any]:
        """Find columns with nested structures."""
        nested = {}

        for field in schema.fields:
            if isinstance(field.dataType, (StructType, ArrayType, MapType)):
                nested[field.name] = field.dataType

        return nested

    def _expand_struct(
        self, df: DataFrame, col_name: str, options: Dict[str, Any]
    ) -> DataFrame:
        """Expand a struct column into separate columns."""
        # Get the struct schema
        struct_schema = None
        for field in df.schema.fields:
            if field.name == col_name and isinstance(field.dataType, StructType):
                struct_schema = field.dataType
                break

        if not struct_schema:
            return df

        # Expand struct fields
        expanded_cols = []
        prefix = options.get("struct_prefix", f"{col_name}_")

        for field in struct_schema.fields:
            new_col_name = f"{prefix}{field.name}"
            expanded_cols.append(col(f"{col_name}.{field.name}").alias(new_col_name))

        # Select all original columns except the struct, plus expanded columns
        other_cols = [col(c) for c in df.columns if c != col_name]
        df = df.select(*other_cols, *expanded_cols)

        return df

    def _expand_path(
        self, df: DataFrame, path: str, options: Dict[str, Any]
    ) -> DataFrame:
        """Expand a nested path (e.g., 'parent.child.field')."""
        parts = path.split(".")

        # Build the column expression
        col_expr = col(parts[0])
        for part in parts[1:]:
            col_expr = col_expr.getField(part)

        # Create new column name
        new_col_name = options.get("path_alias", path.replace(".", "_"))

        return df.withColumn(new_col_name, col_expr)

    def _apply_transformations(
        self, df: DataFrame, options: Dict[str, Any]
    ) -> DataFrame:
        """Apply post-flattening transformations."""
        # Clean column names
        if options.get("clean_column_names", True):
            df = self._clean_column_names(df)

        # Remove empty columns
        if options.get("remove_empty_columns", False):
            df = self._remove_empty_columns(df)

        # Convert data types
        if "type_conversions" in options:
            df = self._apply_type_conversions(df, options["type_conversions"])

        # Apply filters
        if "filters" in options:
            for filter_expr in options["filters"]:
                df = df.filter(filter_expr)

        # Select specific columns
        if "select_columns" in options:
            df = df.select(options["select_columns"])

        return df

    def _clean_column_names(self, df: DataFrame) -> DataFrame:
        """Clean column names for compatibility."""
        for old_name in df.columns:
            # Remove special characters
            new_name = regexp_replace(old_name, r"[^a-zA-Z0-9_]", "_")
            new_name = regexp_replace(new_name, r"_+", "_")
            new_name = new_name.strip("_")

            # Ensure doesn't start with number
            if new_name and new_name[0].isdigit():
                new_name = f"col_{new_name}"

            if new_name != old_name:
                df = df.withColumnRenamed(old_name, new_name)

        return df

    def _remove_empty_columns(self, df: DataFrame) -> DataFrame:
        """Remove columns that are all null."""
        # Sample to check for empty columns
        sample_size = min(1000, df.count())
        sample_df = df.limit(sample_size)

        non_empty_cols = []
        for col_name in df.columns:
            non_null_count = sample_df.filter(col(col_name).isNotNull()).count()
            if non_null_count > 0:
                non_empty_cols.append(col_name)
            else:
                self.logger.debug(f"Removing empty column: {col_name}")

        return df.select(non_empty_cols)

    def _apply_type_conversions(
        self, df: DataFrame, conversions: Dict[str, str]
    ) -> DataFrame:
        """Apply type conversions to columns."""
        for col_name, new_type in conversions.items():
            if col_name in df.columns:
                df = df.withColumn(col_name, col(col_name).cast(new_type))

        return df

    def _write_output(
        self,
        df: DataFrame,
        output_path: str,
        output_format: str,
        options: Dict[str, Any],
    ) -> bool:
        """Write output in specified format."""
        try:
            write_mode = options.get("mode", "overwrite")

            if output_format == "parquet":
                writer = df.write.mode(write_mode)

                if "compression" in options:
                    writer = writer.option("compression", options["compression"])

                if "partition_by" in options:
                    writer = writer.partitionBy(options["partition_by"])

                writer.parquet(output_path)

            elif output_format == "json":
                df.write.mode(write_mode).json(output_path)

            elif output_format == "csv":
                df.write.mode(write_mode).option("header", "true").csv(output_path)

            elif output_format == "delta":
                df.write.mode(write_mode).format("delta").save(output_path)

            else:
                # Generic format
                df.write.mode(write_mode).format(output_format).save(output_path)

            return True

        except Exception as e:
            self.logger.error(f"Error writing output: {e}")
            return False
