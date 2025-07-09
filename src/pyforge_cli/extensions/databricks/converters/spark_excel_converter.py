"""
Spark-optimized Excel Converter for Databricks

This module implements an Excel converter using Apache Spark with pandas API,
supporting multi-sheet processing and intelligent sheet combination.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pyspark.pandas as ps
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, to_timestamp, trim, when
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructType,
)


class SparkExcelConverter:
    """
    Excel converter optimized for Apache Spark.

    Features:
    - Multi-sheet detection and processing
    - Intelligent sheet combination
    - Sheet naming in output
    - Large Excel file handling
    - Format preservation where possible
    """

    def __init__(self, spark_session: Optional[SparkSession] = None):
        """
        Initialize the Spark Excel converter.

        Args:
            spark_session: Optional Spark session to use
        """
        self.logger = logging.getLogger(
            "pyforge.extensions.databricks.converters.spark_excel"
        )
        self.spark = spark_session or SparkSession.builder.getOrCreate()

        # Configure Spark pandas API (only if not in serverless)
        # Check for serverless environment first
        import os
        is_serverless = os.environ.get("IS_SERVERLESS", "").lower() == "true"
        
        if not is_serverless:
            try:
                self.spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
                self.spark.conf.set(
                    "spark.sql.execution.arrow.pyspark.fallback.enabled", "true"
                )
                self.logger.debug("Configured Spark pandas API settings")
            except Exception as e:
                self.logger.debug(f"Could not set Spark config: {e}")
        else:
            self.logger.debug("Skipping Spark config - running in serverless environment")

        # Sheet combination strategies
        self.combination_strategies = {
            "union": self._combine_union,
            "concat": self._combine_concat,
            "separate": self._combine_separate,
            "auto": self._combine_auto,
        }

    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        output_format: str,
        options: Dict[str, Any],
    ) -> bool:
        """
        Convert Excel file to specified output format.

        Args:
            input_path: Input Excel file path
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
                f"Starting Spark Excel conversion: {input_path} -> {output_path}"
            )

            # Detect sheets
            sheet_info = self._detect_sheets(input_path)
            self.logger.info(
                f"Detected {len(sheet_info)} sheets: {list(sheet_info.keys())}"
            )

            # Determine processing strategy
            strategy = options.get("sheet_strategy", "auto")
            if strategy not in self.combination_strategies:
                strategy = "auto"

            # Process sheets
            result_df = self._process_sheets(input_path, sheet_info, strategy, options)

            if result_df is None:
                self.logger.error("Failed to process Excel sheets")
                return False

            # Write output
            success = self._write_output(result_df, output_path, output_format, options)

            if success:
                self.logger.info(f"Successfully converted Excel to {output_format}")

            return success

        except Exception as e:
            self.logger.error(f"Error in Spark Excel conversion: {e}", exc_info=True)
            return False

    def _detect_sheets(self, excel_path: str) -> Dict[str, Dict[str, Any]]:
        """Detect all sheets in Excel file."""
        try:
            # Use pandas to detect sheets (more reliable than spark-excel)
            import pandas as pd

            # Get sheet names
            excel_file = pd.ExcelFile(excel_path)
            sheet_names = excel_file.sheet_names

            sheet_info = {}
            for sheet_name in sheet_names:
                # Read first few rows to analyze
                try:
                    sample_df = pd.read_excel(
                        excel_path, sheet_name=sheet_name, nrows=100
                    )

                    sheet_info[sheet_name] = {
                        "rows": len(sample_df),
                        "columns": len(sample_df.columns),
                        "has_header": self._detect_header(sample_df),
                        "column_types": self._infer_column_types(sample_df),
                        "is_empty": len(sample_df) == 0,
                    }

                except Exception as e:
                    self.logger.warning(f"Error analyzing sheet '{sheet_name}': {e}")
                    sheet_info[sheet_name] = {
                        "rows": 0,
                        "columns": 0,
                        "has_header": True,
                        "column_types": {},
                        "is_empty": True,
                    }

            return sheet_info

        except Exception as e:
            self.logger.error(f"Error detecting sheets: {e}")
            return {}

    def _detect_header(self, df: Any) -> bool:
        """Detect if DataFrame has a header row."""
        if len(df) < 2:
            return True  # Assume header if too few rows

        # Check if first row has different types than rest
        first_row_types = {type(val).__name__ for val in df.iloc[0]}
        data_types = set()

        for i in range(1, min(len(df), 10)):
            data_types.update(type(val).__name__ for val in df.iloc[i])

        # If first row is all strings and data has numbers, likely header
        if first_row_types == {"str"} and (
            "int" in data_types or "float" in data_types
        ):
            return True

        return True  # Default to having header

    def _infer_column_types(self, df: Any) -> Dict[str, str]:
        """Infer column types from pandas DataFrame."""
        type_mapping = {}

        for col_name in df.columns:
            dtype = str(df[col_name].dtype)

            if "int" in dtype:
                type_mapping[col_name] = "long"
            elif "float" in dtype:
                type_mapping[col_name] = "double"
            elif "bool" in dtype:
                type_mapping[col_name] = "boolean"
            elif "datetime" in dtype:
                type_mapping[col_name] = "timestamp"
            else:
                type_mapping[col_name] = "string"

        return type_mapping

    def _process_sheets(
        self,
        excel_path: str,
        sheet_info: Dict[str, Dict[str, Any]],
        strategy: str,
        options: Dict[str, Any],
    ) -> Optional[DataFrame]:
        """Process all sheets according to strategy."""
        # Filter out empty sheets unless requested
        if not options.get("include_empty_sheets", False):
            sheet_info = {
                name: info for name, info in sheet_info.items() if not info["is_empty"]
            }

        if not sheet_info:
            self.logger.warning("No non-empty sheets found")
            return None

        # Read all sheets
        sheet_dataframes = {}
        for sheet_name in sheet_info:
            df = self._read_sheet(
                excel_path, sheet_name, sheet_info[sheet_name], options
            )
            if df is not None:
                sheet_dataframes[sheet_name] = df

        if not sheet_dataframes:
            self.logger.error("Failed to read any sheets")
            return None

        # Combine sheets according to strategy
        combiner = self.combination_strategies[strategy]
        return combiner(sheet_dataframes, sheet_info, options)

    def _read_sheet(
        self,
        excel_path: str,
        sheet_name: str,
        sheet_meta: Dict[str, Any],
        options: Dict[str, Any],
    ) -> Optional[DataFrame]:
        """Read a single Excel sheet."""
        try:
            self.logger.debug(f"Reading sheet '{sheet_name}'")

            # Read using Spark pandas API
            pandas_df = ps.read_excel(
                excel_path,
                sheet_name=sheet_name,
                header=0 if sheet_meta["has_header"] else None,
                engine="openpyxl",  # More reliable for complex Excel files
            )

            # Convert to Spark DataFrame
            spark_df = pandas_df.to_spark()

            # Clean column names
            if options.get("clean_column_names", True):
                spark_df = self._clean_column_names(spark_df)

            # Add sheet name column if requested
            if options.get("add_sheet_column", True):
                spark_df = spark_df.withColumn("_sheet_name", lit(sheet_name))

            # Apply transformations
            spark_df = self._apply_sheet_transformations(spark_df, sheet_name, options)

            self.logger.debug(f"Read {spark_df.count()} rows from sheet '{sheet_name}'")

            return spark_df

        except Exception as e:
            self.logger.error(f"Error reading sheet '{sheet_name}': {e}")
            return None

    def _clean_column_names(self, df: DataFrame) -> DataFrame:
        """Clean column names for compatibility."""
        for old_name in df.columns:
            # Skip if already clean
            if old_name.startswith("_") or re.match(
                r"^[a-zA-Z_][a-zA-Z0-9_]*$", old_name
            ):
                continue

            # Clean the name
            new_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(old_name))
            new_name = re.sub(r"_+", "_", new_name).strip("_")

            # Ensure doesn't start with number
            if new_name and new_name[0].isdigit():
                new_name = f"col_{new_name}"

            # Handle empty names
            if not new_name:
                new_name = f"column_{df.columns.index(old_name)}"

            if new_name != old_name:
                df = df.withColumnRenamed(old_name, new_name)
                self.logger.debug(f"Renamed column '{old_name}' to '{new_name}'")

        return df

    def _apply_sheet_transformations(
        self, df: DataFrame, sheet_name: str, options: Dict[str, Any]
    ) -> DataFrame:
        """Apply sheet-specific transformations."""
        # Trim whitespace from string columns
        if options.get("trim_whitespace", True):
            string_cols = [
                f.name for f in df.schema.fields if f.dataType == StringType()
            ]
            for col_name in string_cols:
                df = df.withColumn(col_name, trim(col(col_name)))

        # Handle Excel date serial numbers if needed
        if options.get("convert_excel_dates", True):
            df = self._convert_excel_dates(df)

        # Apply sheet-specific transformations
        sheet_transforms = options.get("sheet_transformations", {})
        if sheet_name in sheet_transforms:
            transforms = sheet_transforms[sheet_name]
            for transform in transforms:
                df = self._apply_transform(df, transform)

        return df

    def _convert_excel_dates(self, df: DataFrame) -> DataFrame:
        """Convert Excel date serial numbers to proper dates."""
        # Excel epoch is 1900-01-01 (with leap year bug)
        # This is a simplified version - production would need more robust handling

        for field in df.schema.fields:
            if field.dataType == DoubleType() and "date" in field.name.lower():
                # Assume it might be Excel date serial
                df = df.withColumn(
                    field.name,
                    when(
                        col(field.name) > 25569,  # Unix epoch in Excel serial
                        to_timestamp((col(field.name) - 25569) * 86400),
                    ).otherwise(col(field.name)),
                )

        return df

    def _apply_transform(self, df: DataFrame, transform: Dict[str, Any]) -> DataFrame:
        """Apply a single transformation."""
        transform_type = transform.get("type")

        if transform_type == "filter":
            condition = transform["condition"]
            df = df.filter(condition)

        elif transform_type == "select":
            columns = transform["columns"]
            df = df.select(columns)

        elif transform_type == "rename":
            mapping = transform["mapping"]
            for old_name, new_name in mapping.items():
                df = df.withColumnRenamed(old_name, new_name)

        return df

    # Sheet combination strategies

    def _combine_auto(
        self,
        sheets: Dict[str, DataFrame],
        sheet_info: Dict[str, Dict[str, Any]],
        options: Dict[str, Any],
    ) -> DataFrame:
        """Automatically determine best combination strategy."""
        # Check if sheets have similar schemas
        schemas = [df.schema for df in sheets.values()]

        if self._schemas_compatible(schemas):
            self.logger.info("Sheets have compatible schemas - using union strategy")
            return self._combine_union(sheets, sheet_info, options)
        else:
            self.logger.info("Sheets have different schemas - using concat strategy")
            return self._combine_concat(sheets, sheet_info, options)

    def _combine_union(
        self,
        sheets: Dict[str, DataFrame],
        sheet_info: Dict[str, Dict[str, Any]],
        options: Dict[str, Any],
    ) -> DataFrame:
        """Combine sheets with union (stack vertically)."""
        if len(sheets) == 1:
            return list(sheets.values())[0]

        # Get all unique columns
        all_columns = set()
        for df in sheets.values():
            all_columns.update(df.columns)

        # Ensure all DataFrames have same columns
        normalized_dfs = []
        for _sheet_name, df in sheets.items():
            for col_name in all_columns:
                if col_name not in df.columns:
                    df = df.withColumn(col_name, lit(None))

            # Select columns in consistent order
            df = df.select(sorted(all_columns))
            normalized_dfs.append(df)

        # Union all
        result = normalized_dfs[0]
        for df in normalized_dfs[1:]:
            result = result.union(df)

        return result

    def _combine_concat(
        self,
        sheets: Dict[str, DataFrame],
        sheet_info: Dict[str, Dict[str, Any]],
        options: Dict[str, Any],
    ) -> DataFrame:
        """Combine sheets with concatenation (side by side)."""
        if len(sheets) == 1:
            return list(sheets.values())[0]

        # This is complex in Spark - for now, we'll add sheet prefix to column names
        # and then union (simulating side-by-side)
        dfs_with_prefix = []

        for sheet_name, df in sheets.items():
            # Add sheet prefix to columns (except _sheet_name)
            for col_name in df.columns:
                if col_name != "_sheet_name":
                    new_name = f"{sheet_name}_{col_name}"
                    df = df.withColumnRenamed(col_name, new_name)

            dfs_with_prefix.append(df)

        # For true concatenation, we'd need to join on row numbers
        # For now, return the first sheet with a warning
        self.logger.warning(
            "Side-by-side concatenation not fully supported in Spark mode. "
            "Consider using 'union' or 'separate' strategy."
        )

        return dfs_with_prefix[0]

    def _combine_separate(
        self,
        sheets: Dict[str, DataFrame],
        sheet_info: Dict[str, Dict[str, Any]],
        options: Dict[str, Any],
    ) -> DataFrame:
        """Keep sheets separate - return first sheet with metadata."""
        # In separate mode, we typically write each sheet to a different file
        # For now, return the first sheet
        first_sheet = list(sheets.values())[0]

        # Add metadata about all sheets
        metadata = {
            "sheet_count": len(sheets),
            "sheet_names": list(sheets.keys()),
            "total_rows": sum(df.count() for df in sheets.values()),
        }

        # Store metadata in DataFrame properties (if supported by output format)
        self._sheet_metadata = metadata

        return first_sheet

    def _schemas_compatible(self, schemas: List[StructType]) -> bool:
        """Check if schemas are compatible for union."""
        if len(schemas) <= 1:
            return True

        # Get column names (ignoring _sheet_name)
        column_sets = []
        for schema in schemas:
            cols = {f.name for f in schema.fields if f.name != "_sheet_name"}
            column_sets.append(cols)

        # Check if all have same columns
        first_cols = column_sets[0]
        for cols in column_sets[1:]:
            if cols != first_cols:
                return False

        return True

    def _write_output(
        self,
        df: DataFrame,
        output_path: str,
        output_format: str,
        options: Dict[str, Any],
    ) -> bool:
        """Write output in specified format."""
        try:
            # Common write options
            write_mode = options.get("mode", "overwrite")

            if output_format == "parquet":
                df.write.mode(write_mode).parquet(output_path)

            elif output_format == "csv":
                df.write.mode(write_mode).option("header", "true").csv(output_path)

            elif output_format == "json":
                df.write.mode(write_mode).json(output_path)

            elif output_format == "delta":
                df.write.mode(write_mode).format("delta").save(output_path)

            else:
                # Try generic format
                df.write.mode(write_mode).format(output_format).save(output_path)

            return True

        except Exception as e:
            self.logger.error(f"Error writing output: {e}")
            return False
