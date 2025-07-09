# Databricks notebook source
# MAGIC %md
# MAGIC # PyForge CLI MDB/Access File Conversion Testing
# MAGIC 
# MAGIC This notebook tests PyForge CLI v1.0.8.dev8 with various MDB and Access database files in Databricks Serverless environment.
# MAGIC 
# MAGIC ## Test Files:
# MAGIC - `/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/Northwind_2007_VBNet.accdb`
# MAGIC - `/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/access_sakila.mdb`
# MAGIC - `/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/sample_dibi.mdb`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Install PyForge CLI v1.0.8.dev8 from TestPyPI

# COMMAND ----------

# Install specific version from TestPyPI
%pip install -i https://test.pypi.org/simple/ pyforge-cli==1.0.8.dev8 --no-cache-dir --quiet

# COMMAND ----------

# Restart Python to ensure clean import
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Verify Installation

# COMMAND ----------

# Check PyForge version and available converters
%sh
echo "=== PyForge CLI Version ==="
pyforge --version
echo ""
echo "=== Available Commands ==="
pyforge --help
echo ""
echo "=== System Information ==="
python --version
java -version 2>&1 | head -n 1 || echo "Java not available"
echo ""
echo "=== Working Directory ==="
pwd

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Test File 1 - Northwind_2007_VBNet.accdb

# COMMAND ----------

# Test conversion of Northwind ACCDB file to CSV
%sh
echo "=== Converting Northwind_2007_VBNet.accdb to CSV ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/Northwind_2007_VBNet.accdb --format csv --force --verbose

# COMMAND ----------

# Test conversion of Northwind ACCDB file to Parquet
%sh
echo "=== Converting Northwind_2007_VBNet.accdb to Parquet ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/Northwind_2007_VBNet.accdb --format parquet --force --verbose

# COMMAND ----------

# Test conversion of Northwind ACCDB file to JSON
%sh
echo "=== Converting Northwind_2007_VBNet.accdb to JSON ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/Northwind_2007_VBNet.accdb --format json --force --verbose

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Test File 2 - access_sakila.mdb

# COMMAND ----------

# Test conversion of Sakila MDB file to CSV
%sh
echo "=== Converting access_sakila.mdb to CSV ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/access_sakila.mdb --format csv --force --verbose

# COMMAND ----------

# Test conversion of Sakila MDB file to Parquet
%sh
echo "=== Converting access_sakila.mdb to Parquet ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/access_sakila.mdb --format parquet --force --verbose

# COMMAND ----------

# Test conversion of Sakila MDB file to JSON
%sh
echo "=== Converting access_sakila.mdb to JSON ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/access_sakila.mdb --format json --force --verbose

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Test File 3 - sample_dibi.mdb

# COMMAND ----------

# Test conversion of sample_dibi MDB file to CSV
%sh
echo "=== Converting sample_dibi.mdb to CSV ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/sample_dibi.mdb --format csv --force --verbose

# COMMAND ----------

# Test conversion of sample_dibi MDB file to Parquet
%sh
echo "=== Converting sample_dibi.mdb to Parquet ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/sample_dibi.mdb --format parquet --force --verbose

# COMMAND ----------

# Test conversion of sample_dibi MDB file to JSON
%sh
echo "=== Converting sample_dibi.mdb to JSON ==="
pyforge convert /Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/sample_dibi.mdb --format json --force --verbose

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Check Output Files

# COMMAND ----------

# List generated output files
%sh
echo "=== Listing Output Files ==="
ls -la *.csv 2>/dev/null || echo "No CSV files found"
echo ""
ls -la *.parquet 2>/dev/null || echo "No Parquet files found"
echo ""
ls -la *.json 2>/dev/null || echo "No JSON files found"
echo ""
echo "=== Total files in current directory ==="
ls -la | grep -E "\.(csv|parquet|json)$" | wc -l

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Test with Password-Protected Database (if available)

# COMMAND ----------

# Example of testing with password if needed
%sh
echo "=== Testing with password parameter (example) ==="
echo "Command format: pyforge convert <file> --password <password> --format <format>"
echo "Not executed - no password-protected test files available"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8: Error Analysis and Debugging

# COMMAND ----------

# Check PyForge logs and error details
%sh
echo "=== Checking PyForge Configuration ==="
# Check if there are any config files
ls -la ~/.pyforge/ 2>/dev/null || echo "No PyForge config directory found"

echo ""
echo "=== Python Environment ==="
pip show pyforge-cli

echo ""
echo "=== Java/JPype Status ==="
python -c "import jpype; print(f'JPype version: {jpype.__version__}')" 2>&1 || echo "JPype not available"

echo ""
echo "=== Available Python Packages for DB Access ==="
pip list | grep -E "(jaydebeapi|jpype|pyodbc|mdbtools)" || echo "No relevant packages found"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9: Summary Report

# COMMAND ----------

import os
from datetime import datetime

# Generate summary report
print("=" * 80)
print("PyForge CLI MDB/Access Conversion Test Summary")
print("=" * 80)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"PyForge Version: 1.0.8.dev8")
print(f"Environment: Databricks Serverless")
print("\nTest Files:")
print("1. Northwind_2007_VBNet.accdb")
print("2. access_sakila.mdb")
print("3. sample_dibi.mdb")
print("\nFormats Tested: CSV, Parquet, JSON")
print("=" * 80)

# Check for output files
output_extensions = ['.csv', '.parquet', '.json']
found_files = []

for ext in output_extensions:
    files = [f for f in os.listdir('.') if f.endswith(ext)]
    if files:
        found_files.extend(files)
        print(f"\n{ext.upper()} Files Generated: {len(files)}")
        for f in files[:5]:  # Show first 5 files
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")

if not found_files:
    print("\n⚠️  No output files found - conversions may have failed")
else:
    print(f"\n✓ Total files generated: {len(found_files)}")

print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 10: Cleanup (Optional)

# COMMAND ----------

# Uncomment to clean up generated files
# %sh
# echo "=== Cleaning up generated files ==="
# rm -f *.csv *.parquet *.json
# echo "Cleanup completed"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Notes and Observations
# MAGIC 
# MAGIC Record any errors or issues encountered during testing:
# MAGIC 
# MAGIC 1. **Java/JPype Availability**: Check if Java runtime and JPype are available in Serverless
# MAGIC 2. **UCanAccess Backend**: Note any errors related to JDBC/UCanAccess
# MAGIC 3. **File Access**: Verify if Unity Catalog volumes are accessible
# MAGIC 4. **Alternative Backends**: Check if mdbtools or other backends are tried
# MAGIC 5. **Performance**: Note conversion times for each file