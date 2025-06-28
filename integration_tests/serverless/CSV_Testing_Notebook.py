# Databricks notebook source
# DBTITLE 1,CSV Testing Notebook - PyForge CLI Serverless Detection
# MAGIC %md
# MAGIC # CSV Testing Notebook for PyForge CLI
# MAGIC 
# MAGIC This notebook focuses specifically on testing CSV file conversions to verify:
# MAGIC - Databricks Serverless V1 environment detection
# MAGIC - Native Spark session usage for distributed processing
# MAGIC - File size detection (>500MB uses optimized processing)
# MAGIC - PySpark vs pandas converter selection

# COMMAND ----------

# DBTITLE 1,Configuration
# PyForge version and wheel path
PYFORGE_VERSION = "0.5.5.dev13"
PYFORGE_WHEEL_PATH = "/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/usa-sdandey@deloitte.com/pyforge_cli-0.5.5.dev13-py3-none-any.whl"

# Test data paths
DEFAULT_VOLUME_PATH = "/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox"
SAMPLE_DATASETS_PATH = f"{DEFAULT_VOLUME_PATH}/sample-datasets"
OUTPUT_PATH = f"{DEFAULT_VOLUME_PATH}/sample-datasets/converted/csv"

print(f"🔧 CSV Testing Configuration:")
print(f"   PyForge Version: {PYFORGE_VERSION}")
print(f"   Output Path: {OUTPUT_PATH}")

# COMMAND ----------

# DBTITLE 1,Install PyForge CLI
print(f"📦 Installing PyForge CLI {PYFORGE_VERSION}...")
%pip install {PYFORGE_WHEEL_PATH} --no-cache-dir --quiet
print("✅ Installation complete!")

# COMMAND ----------

# DBTITLE 1,Restart Python Environment
print("🔄 Restarting Python environment...")
dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Verify Installation and Environment
import subprocess
import os
from datetime import datetime

# Re-initialize configuration after restart
PYFORGE_VERSION = "0.5.5.dev13"
DEFAULT_VOLUME_PATH = "/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox"
SAMPLE_DATASETS_PATH = f"{DEFAULT_VOLUME_PATH}/sample-datasets"
OUTPUT_PATH = f"{DEFAULT_VOLUME_PATH}/sample-datasets/converted/csv"

print(f"🔍 Verifying PyForge CLI installation...")
print(f"   Version: {PYFORGE_VERSION}")
print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Test import
try:
    import pyforge_cli
    print(f"✅ PyForge CLI imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")

# Check environment variables for serverless detection
print(f"\n🌐 Key Environment Variables:")
env_vars = ['IS_SERVERLESS', 'SPARK_CONNECT_MODE_ENABLED', 'DB_INSTANCE_TYPE', 
           'DATABRICKS_RUNTIME_VERSION', 'POD_NAME']
for var in env_vars:
    value = os.environ.get(var, 'Not set')
    print(f"   {var}: {value}")

# COMMAND ----------

# DBTITLE 1,Verify Test Data Files
import os

# Create output directory
os.makedirs(OUTPUT_PATH, exist_ok=True)

print("📂 Verifying available CSV test files...")

# Define test files with their expected locations
test_files = {
    'small': f"{SAMPLE_DATASETS_PATH}/csv/small/credit-fraud.csv",
    'medium_1': f"{SAMPLE_DATASETS_PATH}/csv/medium/nyc-taxi.csv", 
    'medium_2': f"{SAMPLE_DATASETS_PATH}/csv/medium/paysim-financial.csv"
}

# Check file sizes and availability
for file_type, file_path in test_files.items():
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) / (1024*1024)
        print(f"✅ {file_type}: {file_path} ({file_size:.1f} MB)")
    else:
        print(f"❌ {file_type}: {file_path} (NOT FOUND)")

print(f"\n📁 Output directory: {OUTPUT_PATH}")

# COMMAND ----------

# DBTITLE 1,Test 1: Credit Fraud CSV (Small Dataset)
print("🧪 Test 1: Credit Fraud CSV - Small dataset serverless detection")
print("=" * 80)

input_file = f"{SAMPLE_DATASETS_PATH}/csv/small/credit-fraud.csv"
output_file = f"{OUTPUT_PATH}/credit-fraud"

# Show file info
if os.path.exists(input_file):
    file_size = os.path.getsize(input_file) / (1024*1024)
    print(f"📂 Input: {input_file} ({file_size:.1f} MB)")
    print(f"📁 Output: {output_file}.parquet")
else:
    print(f"❌ File not found: {input_file}")

cmd = f"pyforge convert '{input_file}' '{output_file}' --format parquet --verbose"
print(f"\n🔧 Command: {cmd}")
print("\n" + "=" * 40 + " OUTPUT " + "=" * 40)

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

if result.returncode == 0:
    print("\n✅ Test 1 PASSED - Credit Fraud conversion successful")
else:
    print("\n❌ Test 1 FAILED - Credit Fraud conversion failed")

# COMMAND ----------

# DBTITLE 1,Test 2: NYC Taxi CSV (Medium Dataset - Expected >500MB)
print("🧪 Test 2: NYC Taxi CSV - Large dataset with native Spark optimization")
print("=" * 80)

input_file = f"{SAMPLE_DATASETS_PATH}/csv/medium/nyc-taxi.csv"
output_file = f"{OUTPUT_PATH}/nyc-taxi"

# Show file info
if os.path.exists(input_file):
    file_size = os.path.getsize(input_file) / (1024*1024)
    print(f"📂 Input: {input_file} ({file_size:.1f} MB)")
    print(f"📁 Output: {output_file}.parquet")
    if file_size > 500:
        print(f"🚀 Expected behavior: Should trigger native Spark optimization for large files")
else:
    print(f"❌ File not found: {input_file}")

cmd = f"pyforge convert '{input_file}' '{output_file}' --format parquet --verbose"
print(f"\n🔧 Command: {cmd}")
print("\n" + "=" * 40 + " OUTPUT " + "=" * 40)

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

if result.returncode == 0:
    print("\n✅ Test 2 PASSED - NYC Taxi conversion successful")
else:
    print("\n❌ Test 2 FAILED - NYC Taxi conversion failed")

# COMMAND ----------

# DBTITLE 1,Test 3: PaySim Financial CSV (Medium Dataset)
print("🧪 Test 3: PaySim Financial CSV - Financial transaction data")
print("=" * 80)

input_file = f"{SAMPLE_DATASETS_PATH}/csv/medium/paysim-financial.csv"
output_file = f"{OUTPUT_PATH}/paysim-financial"

# Show file info
if os.path.exists(input_file):
    file_size = os.path.getsize(input_file) / (1024*1024)
    print(f"📂 Input: {input_file} ({file_size:.1f} MB)")
    print(f"📁 Output: {output_file}.parquet")
    if file_size > 500:
        print(f"🚀 Expected behavior: Should trigger native Spark optimization for large files")
    else:
        print(f"📊 Expected behavior: Should use standard PySpark processing")
else:
    print(f"❌ File not found: {input_file}")

cmd = f"pyforge convert '{input_file}' '{output_file}' --format parquet --verbose"
print(f"\n🔧 Command: {cmd}")
print("\n" + "=" * 40 + " OUTPUT " + "=" * 40)

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

if result.returncode == 0:
    print("\n✅ Test 3 PASSED - PaySim Financial conversion successful")
else:
    print("\n❌ Test 3 FAILED - PaySim Financial conversion failed")

# COMMAND ----------

# DBTITLE 1,Test 4: Force PySpark Mode on Small File
print("🧪 Test 4: Force PySpark mode on Credit Fraud dataset")
print("=" * 80)

input_file = f"{SAMPLE_DATASETS_PATH}/csv/small/credit-fraud.csv"
output_file = f"{OUTPUT_PATH}/credit-fraud-forced-pyspark"

print(f"📂 Input: {input_file}")
print(f"📁 Output: {output_file}.parquet")
print(f"🔧 Testing: --force-pyspark flag to explicitly use PySpark")

cmd = f"pyforge convert '{input_file}' '{output_file}' --format parquet --force-pyspark --verbose"
print(f"\n🔧 Command: {cmd}")
print("\n" + "=" * 40 + " OUTPUT " + "=" * 40)

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

if result.returncode == 0:
    print("\n✅ Test 4 PASSED - Force PySpark mode successful")
else:
    print("\n❌ Test 4 FAILED - Force PySpark mode failed")

# COMMAND ----------

# DBTITLE 1,Test 5: Verify Output Files with Spark
print("🧪 Test 5: Verify converted Parquet files can be read with Spark")
print("=" * 80)

try:
    # Test reading the converted files
    output_files = [
        f"{OUTPUT_PATH}/credit-fraud.parquet",
        f"{OUTPUT_PATH}/nyc-taxi.parquet", 
        f"{OUTPUT_PATH}/paysim-financial.parquet",
        f"{OUTPUT_PATH}/credit-fraud-forced-pyspark.parquet"
    ]
    
    total_files = 0
    successful_reads = 0
    
    for output_file in output_files:
        total_files += 1
        try:
            if os.path.exists(output_file):
                df = spark.read.parquet(output_file)
                row_count = df.count()
                col_count = len(df.columns)
                file_size = os.path.getsize(output_file) / (1024*1024)
                print(f"✅ {os.path.basename(output_file)}: {row_count:,} rows, {col_count} columns, {file_size:.1f} MB")
                successful_reads += 1
            else:
                print(f"⚠️  {os.path.basename(output_file)}: File not found (conversion may have failed)")
        except Exception as e:
            print(f"❌ {os.path.basename(output_file)}: Error reading - {e}")
    
    print(f"\n📊 Summary: {successful_reads}/{total_files} files successfully verified")
    
    if successful_reads == total_files:
        print("✅ Test 5 PASSED - All files readable with Spark")
    else:
        print("⚠️  Test 5 PARTIAL - Some files had issues")
    
except Exception as e:
    print(f"❌ Test 5 FAILED: {e}")

# COMMAND ----------

# DBTITLE 1,Test Summary and Environment Info
print("📊 CSV Testing Summary - Real Dataset Testing")
print("=" * 80)

# Show what we tested
print("Tests Completed:")
print("1. ✅ Credit Fraud CSV (Small) - Environment detection testing")
print("2. ✅ NYC Taxi CSV (Large) - Native Spark optimization testing (>500MB)")
print("3. ✅ PaySim Financial CSV (Medium) - PySpark processing testing")
print("4. ✅ Force PySpark mode - Explicit PySpark flag testing")
print("5. ✅ Parquet verification - Spark read validation")

# Environment summary
print(f"\nEnvironment Information:")
print(f"   PyForge Version: {PYFORGE_VERSION}")
print(f"   Databricks Serverless: {os.environ.get('IS_SERVERLESS', 'Unknown')}")
print(f"   Spark Connect Mode: {os.environ.get('SPARK_CONNECT_MODE_ENABLED', 'Unknown')}")
print(f"   Instance Type: {os.environ.get('DB_INSTANCE_TYPE', 'Unknown')}")
print(f"   Runtime Version: {os.environ.get('DATABRICKS_RUNTIME_VERSION', 'Unknown')}")

# File locations tested
print(f"\nTest Data Sources:")
print(f"   Credit Fraud: /sample-datasets/csv/small/credit-fraud.csv")
print(f"   NYC Taxi: /sample-datasets/csv/medium/nyc-taxi.csv") 
print(f"   PaySim Financial: /sample-datasets/csv/medium/paysim-financial.csv")

print(f"\nOutput Location:")
print(f"   {OUTPUT_PATH}/")

# Show expected behavior
print(f"\nExpected Behavior:")
print("- Should see: '🚀 Databricks Serverless detected - using PySpark distributed processing'")
print("- Large files (>500MB): Should trigger native Spark optimization") 
print("- Should use existing Databricks Spark session")
print("- All files should convert successfully to Parquet format")
print("- Processing rates should be displayed for large files (MB/s, rows/s)")

print(f"\n🎉 Real Dataset CSV Testing Complete!")

# COMMAND ----------

# DBTITLE 1,Cleanup (Optional)
# Uncomment to clean up converted files
# import shutil
# 
# print("🧹 Cleaning up converted Parquet files...")
# try:
#     output_files = [
#         f"{OUTPUT_PATH}/credit-fraud.parquet",
#         f"{OUTPUT_PATH}/nyc-taxi.parquet",
#         f"{OUTPUT_PATH}/paysim-financial.parquet", 
#         f"{OUTPUT_PATH}/credit-fraud-forced-pyspark.parquet"
#     ]
#     
#     cleaned_count = 0
#     for output_file in output_files:
#         if os.path.exists(output_file):
#             if os.path.isfile(output_file):
#                 os.remove(output_file)
#             else:
#                 shutil.rmtree(output_file)  # In case it's a directory
#             cleaned_count += 1
#             print(f"✅ Removed: {os.path.basename(output_file)}")
#     
#     print(f"✅ Cleaned up {cleaned_count} converted files")
#     
# except Exception as e:
#     print(f"⚠️ Cleanup error (non-critical): {e}")
# 
# print("ℹ️  Note: Original CSV source files in /sample-datasets/ are preserved")