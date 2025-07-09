# Databricks notebook source
# MAGIC %md
# MAGIC # Debug Converter Registration Issue
# MAGIC This notebook debugs why converters are showing as "not available" in PyForgeDatabricks

# COMMAND ----------

# Install PyForge from Unity Catalog Volume
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/usa-sdandey@deloitte.com/pyforge_cli-1.0.9.dev53-py3-none-any.whl --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

# Restart Python kernel
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Import and Initialize PyForgeDatabricks

# COMMAND ----------

import json
import logging
from pyforge_cli.extensions.databricks import PyForgeDatabricks
from pyforge_cli.extensions.databricks.converter_selector import ConverterType
from pathlib import Path

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pyforge")

# COMMAND ----------

# Initialize PyForgeDatabricks
print("Initializing PyForgeDatabricks...")
forge = PyForgeDatabricks()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Check Converter Registration

# COMMAND ----------

# Check what converters are registered
print("=== Converter Registration Status ===")
print(f"Converters initialized: {forge._converters_initialized}")
print(f"\nRegistered converter types in fallback manager:")
for converter_type, converter_func in forge.fallback_manager._converter_registry.items():
    print(f"  - {converter_type.value}: {converter_func}")

# COMMAND ----------

# Check converter availability
print("\n=== Converter Availability ===")
from pyforge_cli.extensions.databricks.converter_selector import ConverterType

for converter_type in [ConverterType.SPARK, ConverterType.PANDAS, ConverterType.PYARROW, ConverterType.NATIVE]:
    is_available = forge.fallback_manager._is_converter_available(converter_type)
    print(f"{converter_type.value}: {'✓ Available' if is_available else '✗ Not Available'}")
    
    # Check why it might not be available
    if not is_available:
        if converter_type not in forge.fallback_manager._converter_registry:
            print(f"  → Not registered in fallback manager")
        else:
            print(f"  → Registered but dependencies missing")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Test Converter Selection

# COMMAND ----------

# Test converter selection for CSV -> Parquet
test_file = Path("/tmp/test.csv")
output_format = "parquet"
options = {}

print("=== Testing Converter Selection ===")
try:
    recommendation = forge.converter_selector.select_converter(
        test_file, output_format, options
    )
    print(f"Recommended converter: {recommendation.converter_type.value}")
    print(f"Confidence: {recommendation.confidence:.2f}")
    print(f"Reasons: {recommendation.reasons}")
    print(f"Fallback options: {[c.value for c in recommendation.fallback_options]}")
except Exception as e:
    print(f"Error in converter selection: {e}")
    import traceback
    traceback.print_exc()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Test Fallback Chain

# COMMAND ----------

# Build a fallback chain manually
from pyforge_cli.extensions.databricks.converter_selector import ConverterRecommendation

print("=== Testing Fallback Chain ===")

# Create a mock recommendation
mock_recommendation = ConverterRecommendation(
    converter_type=ConverterType.SPARK,
    confidence=0.8,
    reasons=["Test recommendation"],
    estimated_performance="fast",
    memory_requirement="low",
    fallback_options=[ConverterType.PANDAS, ConverterType.NATIVE]
)

# Test building fallback chain
fallback_chain = forge.fallback_manager._build_fallback_chain(mock_recommendation)
print(f"Fallback chain: {[c.value for c in fallback_chain]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Check Spark Session

# COMMAND ----------

# Check if Spark session is available
print("=== Spark Session Check ===")
print(f"Spark session: {forge.spark}")
if forge.spark:
    print(f"Spark version: {forge.spark.version}")
    print(f"App name: {forge.spark.sparkContext.appName}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Test Simple Conversion

# COMMAND ----------

# Create a simple test CSV file
import pandas as pd

test_data = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'value': [10.5, 20.3, 30.7]
})

test_csv_path = "/tmp/test_converter.csv"
test_data.to_csv(test_csv_path, index=False)
print(f"Created test CSV: {test_csv_path}")

# COMMAND ----------

# Try to convert the test file
output_path = "/tmp/test_converter.parquet"

print("\n=== Testing Conversion ===")
result = forge.convert(test_csv_path, output_path)
print(f"Conversion result: {json.dumps(result, indent=2)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Check Native Converters

# COMMAND ----------

# Check if native converters are available
print("=== Native Converter Check ===")
try:
    from pyforge_cli.converters import CSVConverter, XmlConverter
    print("✓ Native CSV converter imported successfully")
    print("✓ Native XML converter imported successfully")
    
    # Check Excel converter
    try:
        from pyforge_cli.converters.excel_converter import ExcelConverter
        print("✓ Native Excel converter imported successfully")
    except ImportError as e:
        print(f"✗ Excel converter import failed: {e}")
        
except ImportError as e:
    print(f"✗ Native converter import failed: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Manual Converter Test

# COMMAND ----------

# Try to use converters directly
print("=== Direct Converter Test ===")

# Test Spark CSV converter
if hasattr(forge, '_csv_converter'):
    print("✓ Spark CSV converter is available")
    print(f"  Type: {type(forge._csv_converter)}")
else:
    print("✗ Spark CSV converter not found")

# Test native converters
if hasattr(forge, '_native_csv_converter'):
    print("✓ Native CSV converter is available")
    print(f"  Type: {type(forge._native_csv_converter)}")
else:
    print("✗ Native CSV converter not found")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC This notebook helps identify the root cause of converter registration issues in PyForgeDatabricks.