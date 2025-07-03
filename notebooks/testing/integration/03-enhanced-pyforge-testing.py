# Databricks notebook source
# DBTITLE 1,Enhanced PyForge CLI Testing Notebook
# MAGIC %md
# MAGIC # Enhanced PyForge CLI Comprehensive Testing Suite
# MAGIC 
# MAGIC This notebook provides comprehensive testing of PyForge CLI with:
# MAGIC - Automated installation and configuration
# MAGIC - Sample dataset management
# MAGIC - Bulk conversion testing with timing
# MAGIC - Comprehensive error handling and reporting
# MAGIC - Performance metrics and summary reports

# COMMAND ----------

# DBTITLE 1,Important: Library Cache Management
# MAGIC %md
# MAGIC ## ⚠️ Library Cache Management in Databricks Serverless
# MAGIC 
# MAGIC **IMPORTANT**: Databricks serverless automatically caches library installations. If you're updating PyForge or experiencing issues with outdated packages:
# MAGIC 
# MAGIC ### Option 1: Reset Environment (Most Reliable)
# MAGIC 1. Click the **Environment** tab in the side panel
# MAGIC 2. Click the arrow next to **Apply**
# MAGIC 3. Select **Reset environment**
# MAGIC 4. Wait for the environment to reset before running the notebook
# MAGIC 
# MAGIC ### Option 2: No Cache Install (Command Line)
# MAGIC The installation commands below use `--no-cache-dir` to ensure fresh installation.
# MAGIC 
# MAGIC ### Option 3: Manual Cache Clear
# MAGIC Uncomment and run the cell below if you need to manually clear caches:

# COMMAND ----------

# DBTITLE 1,Optional: Manual Cache Clear
# # Uncomment these lines if you need to manually clear caches
# # WARNING: This will restart the Python kernel!
# 
# # Option 1: Uninstall existing version first
# # %pip uninstall -y pyforge-cli
# 
# # Option 2: Clear Spark cache (for data caching)
# # spark.catalog.clearCache()
# 
# # Option 3: Restart Python (will disconnect notebook temporarily)
# # dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Configuration Parameters
# =============================================================================
# CONFIGURATION SECTION - Modify these parameters as needed
# =============================================================================

# PyForge version to test (default: latest with enhanced MDB support and PySpark CSV converter)
PYFORGE_VERSION = "0.5.5.dev13"

# PyForge wheel path for installation from volume
PYFORGE_WHEEL_PATH = "/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/usa-sdandey@deloitte.com/pyforge_cli-0.5.5.dev13-py3-none-any.whl"

# Default volume path for sample datasets
DEFAULT_VOLUME_PATH = "/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox"

# Paths configuration
SAMPLE_DATASETS_PATH = f"{DEFAULT_VOLUME_PATH}/sample-datasets"
CONVERTED_OUTPUT_PATH = f"{DEFAULT_VOLUME_PATH}/converted_parquet"

# Test configuration
FORCE_CONVERSION = True  # Use --force flag for all conversions
SKIP_MDF_FILES = True   # Skip MDF files (not supported yet)
SKIP_CSV_FILES = False  # Enable CSV files testing to verify PySpark serverless detection
USE_PYSPARK_FOR_CSV = True  # Use PySpark converter for CSV files when available

print(f"🔧 Configuration:")
print(f"   PyForge Version: {PYFORGE_VERSION}")
print(f"   PyForge Wheel Path: {PYFORGE_WHEEL_PATH}")
print(f"   Sample Datasets: {SAMPLE_DATASETS_PATH}")
print(f"   Output Path: {CONVERTED_OUTPUT_PATH}")
print(f"   Force Conversion: {FORCE_CONVERSION}")
print(f"   Skip MDF Files: {SKIP_MDF_FILES}")
print(f"   Skip CSV Files: {SKIP_CSV_FILES}")
print(f"   Use PySpark for CSV: {USE_PYSPARK_FOR_CSV}")

# COMMAND ----------

# DBTITLE 1,Install and Restart PyForge Package
# =============================================================================
# INSTALLATION SECTION
# =============================================================================

print(f"📦 Installing PyForge CLI version {PYFORGE_VERSION}...")
print(f"   Installing from volume wheel: {PYFORGE_WHEEL_PATH}")
print(f"   Using --no-cache-dir to ensure fresh installation")

# Install PyForge CLI from volume wheel with no cache
%pip install {PYFORGE_WHEEL_PATH} --no-cache-dir --quiet

print(f"✅ PyForge CLI {PYFORGE_VERSION} installed successfully!")
print("🔄 Restarting Python environment...")

# COMMAND ----------

# Restart Python to ensure clean environment
dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Post-Restart Environment Check
# MAGIC %md
# MAGIC ### ⚠️ Important Notes:
# MAGIC - The Python kernel has been restarted to ensure clean package loading
# MAGIC - If you see any import errors below, try the **Reset environment** option from the Environment panel
# MAGIC - Never install PySpark manually - it's pre-installed in serverless compute
# MAGIC - Avoid upgrading core packages like IPython, numpy, or pandas beyond tested versions

# COMMAND ----------

# DBTITLE 1,Re-initialize Configuration Variables
# =============================================================================
# VARIABLE RE-INITIALIZATION AFTER PYTHON RESTART
# =============================================================================

# Re-initialize all configuration variables since Python was restarted
PYFORGE_VERSION = "0.5.5.dev13"
PYFORGE_WHEEL_PATH = "/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/usa-sdandey@deloitte.com/pyforge_cli-0.5.5.dev13-py3-none-any.whl"
DEFAULT_VOLUME_PATH = "/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox"
SAMPLE_DATASETS_PATH = f"{DEFAULT_VOLUME_PATH}/sample-datasets"
CONVERTED_OUTPUT_PATH = f"{DEFAULT_VOLUME_PATH}/converted_parquet"
FORCE_CONVERSION = True
SKIP_MDF_FILES = True
SKIP_CSV_FILES = False  # Enable CSV testing to verify PySpark serverless detection
USE_PYSPARK_FOR_CSV = True

print(f"🔄 Re-initialized configuration variables after Python restart:")
print(f"   PyForge Version: {PYFORGE_VERSION}")
print(f"   PyForge Wheel Path: {PYFORGE_WHEEL_PATH}")
print(f"   Sample Datasets: {SAMPLE_DATASETS_PATH}")
print(f"   Output Path: {CONVERTED_OUTPUT_PATH}")
print(f"   Force Conversion: {FORCE_CONVERSION}")
print(f"   Skip MDF Files: {SKIP_MDF_FILES}")
print(f"   Skip CSV Files: {SKIP_CSV_FILES}")
print(f"   Use PySpark for CSV: {USE_PYSPARK_FOR_CSV}")

# COMMAND ----------

# DBTITLE 1,Verify Installation and Display Help
# =============================================================================
# VERIFICATION SECTION
# =============================================================================

import subprocess
import time
import os
import pandas as pd
from datetime import datetime
import json

print("🔍 Verifying PyForge CLI installation...")

# Check if we're in Databricks environment
try:
    dbutils
    print("✅ Running in Databricks environment")
except NameError:
    print("⚠️  Not running in Databricks environment")

# Verify PyForge installation
try:
    import pyforge_cli
    print(f"✅ PyForge CLI module imported successfully")
    print(f"   Module location: {pyforge_cli.__file__}")
except ImportError as e:
    print(f"❌ Failed to import PyForge CLI: {e}")
    print("   Try resetting the environment from the Environment panel")

# COMMAND ----------

# MAGIC %sh
# MAGIC echo "📋 PyForge CLI Help Information:"
# MAGIC pyforge --help

# COMMAND ----------

# MAGIC %sh
# MAGIC echo "📊 PyForge CLI Version Information:"
# MAGIC pyforge --version

# COMMAND ----------

# DBTITLE 1,Setup Sample Datasets
# =============================================================================
# SAMPLE DATASETS SETUP
# =============================================================================

print(f"📥 Setting up sample datasets at: {SAMPLE_DATASETS_PATH}")

# For testing purposes, we'll use a direct approach instead of the install command
# which may have issues with GitHub releases in the Databricks environment

# Create sample datasets directory structure
import os
os.makedirs(SAMPLE_DATASETS_PATH, exist_ok=True)

# Create subdirectories for different file types
subdirs = ['csv', 'excel', 'xml', 'pdf', 'access', 'dbf']
for subdir in subdirs:
    os.makedirs(f"{SAMPLE_DATASETS_PATH}/{subdir}", exist_ok=True)

print("✅ Sample datasets directory structure created!")
print("📝 Note: Using built-in test files instead of downloading sample datasets")
print("   This avoids GitHub API issues in Databricks serverless environment")

# Create simple test CSV files
import pandas as pd

# Test CSV 1: Simple data
test_data1 = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'age': [25, 30, 35, 28, 32],
    'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
})
test_data1.to_csv(f"{SAMPLE_DATASETS_PATH}/csv/test_simple.csv", index=False)

# Test CSV 2: With special characters
test_data2 = pd.DataFrame({
    'product': ['Item "A"', 'Item, B', 'Item\nC', 'Item;D'],
    'price': [10.99, 15.50, 8.75, 22.00],
    'description': ['Product with "quotes"', 'Product, with comma', 'Product\nwith newline', 'Product;with semicolon']
})
test_data2.to_csv(f"{SAMPLE_DATASETS_PATH}/csv/test_special_chars.csv", index=False)

print(f"✅ Created test CSV files:")
print(f"   - {SAMPLE_DATASETS_PATH}/csv/test_simple.csv")
print(f"   - {SAMPLE_DATASETS_PATH}/csv/test_special_chars.csv")

# COMMAND ----------

# DBTITLE 1,Check PySpark Availability
# =============================================================================
# PYSPARK AVAILABILITY CHECK
# =============================================================================

def check_pyspark_availability():
    """Check if PySpark is available in the environment."""
    try:
        import pyspark
        from pyspark.sql import SparkSession
        print("✅ PySpark is available in this environment")
        print(f"   PySpark Version: {pyspark.__version__}")
        
        # Try to get or create a Spark session
        try:
            spark = SparkSession.builder.getOrCreate()
            print(f"   Spark Session: Active")
            print(f"   Spark Version: {spark.version}")
            
            # Check if it's Spark Connect (which doesn't support sparkContext)
            try:
                master = spark.sparkContext.master
                print(f"   Spark Master: {master}")
            except Exception:
                print(f"   Spark Mode: Spark Connect (Serverless)")
            
            return True
        except Exception as e:
            print(f"   ⚠️  Could not create Spark session: {e}")
            return False
    except ImportError:
        print("❌ PySpark is NOT available in this environment")
        print("   CSV files will be converted using pandas")
        return False

# Check PySpark availability
pyspark_available = check_pyspark_availability()

# Update USE_PYSPARK_FOR_CSV based on availability
if not pyspark_available and USE_PYSPARK_FOR_CSV:
    print("\n⚠️  Note: PySpark not available, CSV conversion will fall back to pandas")
    USE_PYSPARK_FOR_CSV = False

# COMMAND ----------

# DBTITLE 1,Discover and Catalog Sample Files
# =============================================================================
# FILE DISCOVERY AND CATALOGING
# =============================================================================

def discover_sample_files():
    """Discover all sample files and categorize them for testing."""
    print("🔍 Discovering sample files...")
    
    files_catalog = []
    supported_extensions = {
        '.csv': 'CSV',
        '.xlsx': 'Excel', 
        '.xml': 'XML',
        '.pdf': 'PDF',
        '.dbf': 'DBF',
        '.mdb': 'MDB',
        '.accdb': 'ACCDB',
        '.mdf': 'MDF'  # Will be skipped
    }
    
    if os.path.exists(SAMPLE_DATASETS_PATH):
        for root, dirs, files in os.walk(SAMPLE_DATASETS_PATH):
            # Skip already converted files
            if 'converted' in root or 'parquet' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in supported_extensions:
                    # Get relative path for better display
                    rel_path = os.path.relpath(file_path, SAMPLE_DATASETS_PATH)
                    folder_category = rel_path.split(os.sep)[0] if os.sep in rel_path else 'root'
                    
                    file_info = {
                        'file_name': file,
                        'file_type': supported_extensions[file_ext],
                        'extension': file_ext,
                        'category': folder_category,
                        'relative_path': rel_path,
                        'full_path': file_path,
                        'size_mb': round(os.path.getsize(file_path) / (1024*1024), 2),
                        'skip_reason': 'MDF not supported' if file_ext == '.mdf' and SKIP_MDF_FILES else None
                    }
                    files_catalog.append(file_info)
    
    return files_catalog

# Discover files
files_catalog = discover_sample_files()

# Display catalog
df_catalog = pd.DataFrame(files_catalog)
print(f"📊 Found {len(files_catalog)} test files:")
display(df_catalog.groupby(['file_type', 'category']).agg({
    'file_name': 'count',
    'size_mb': 'sum'
}).round(2).rename(columns={'file_name': 'file_count', 'size_mb': 'total_size_mb'}))

print(f"\n📋 Detailed file catalog:")
display(df_catalog)

# COMMAND ----------

# DBTITLE 1,Bulk Conversion Testing with Timing and Error Handling
# =============================================================================
# BULK CONVERSION TESTING SECTION
# =============================================================================

def run_conversion_test(file_info, verbose=False):
    """Run conversion test for a single file with comprehensive error handling."""
    file_path = file_info['full_path']
    file_type = file_info['file_type']
    file_name = file_info['file_name']
    file_ext = file_info['extension']
    
    # Skip if marked for skipping
    if file_info.get('skip_reason'):
        return {
            'file_name': file_name,
            'file_type': file_type,
            'status': 'SKIPPED',
            'duration_seconds': 0,
            'error_message': file_info['skip_reason'],
            'output_path': None,
            'size_mb': file_info['size_mb'],
            'converter_used': 'N/A'
        }
    
    # Skip CSV files if configured
    if SKIP_CSV_FILES and file_ext == '.csv':
        return {
            'file_name': file_name,
            'file_type': file_type,
            'status': 'SKIPPED',
            'duration_seconds': 0,
            'error_message': 'CSV files skipped (SKIP_CSV_FILES=True) - focusing on other formats',
            'output_path': None,
            'size_mb': file_info['size_mb'],
            'converter_used': 'N/A'
        }
    
    # Skip very large files (>1GB) for non-CSV files to avoid hanging
    # CSV files with PySpark can handle large files efficiently
    if file_info['size_mb'] > 1000 and file_ext != '.csv':
        return {
            'file_name': file_name,
            'file_type': file_type,
            'status': 'SKIPPED',
            'duration_seconds': 0,
            'error_message': f'File too large ({file_info["size_mb"]:.1f} MB) - skipped for testing',
            'output_path': None,
            'size_mb': file_info['size_mb'],
            'converter_used': 'N/A'
        }
    
    # Create output path
    relative_path = file_info['relative_path']
    output_dir = os.path.join(CONVERTED_OUTPUT_PATH, os.path.dirname(relative_path))
    output_name = os.path.splitext(file_name)[0]
    
    # Build conversion command
    force_flag = '--force' if FORCE_CONVERSION else ''
    # Add PySpark flag for CSV files if configured
    pyspark_flag = ''
    if USE_PYSPARK_FOR_CSV and file_info['extension'] == '.csv':
        pyspark_flag = '--force-pyspark'
    # Add Excel-specific flags to avoid interactive prompts
    excel_flag = ''
    if file_info['extension'] in ['.xlsx', '.xls']:
        excel_flag = '--separate'  # Keep sheets separate to avoid prompts
    # Build command with verbose flag for debug logging
    verbose_flag = '--verbose' if verbose else ''
    cmd = f"pyforge --verbose convert '{file_path}' '{output_dir}/{output_name}' --format parquet {force_flag} {pyspark_flag} {excel_flag}" if verbose else f"pyforge convert '{file_path}' '{output_dir}/{output_name}' --format parquet {force_flag} {pyspark_flag} {excel_flag}"
    
    print(f"🔄 Converting {file_name} ({file_type})...")
    if verbose:
        print(f"   Command: {cmd}")
    
    try:
        start_time = time.time()
        
        # Set timeout based on file size
        if file_info['size_mb'] > 100:
            timeout = 600  # 10 minutes for large files (100MB+)
        elif file_info['size_mb'] > 10:
            timeout = 300  # 5 minutes for medium files (10MB+)
        else:
            timeout = 120  # 2 minutes for small files
        
        print(f"   Timeout: {timeout}s (file size: {file_info['size_mb']:.1f} MB)")
        
        # Run conversion
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        if result.returncode == 0:
            status = 'SUCCESS'
            error_message = None
            output_path = f"{output_dir}/{output_name}"
            # Check if PySpark was used for CSV files
            converter_used = 'PySpark' if (file_ext == '.csv' and USE_PYSPARK_FOR_CSV and 'PySpark' in result.stdout) else 'Standard'
            print(f"  ✅ Success ({duration}s) - {converter_used} converter")
        else:
            status = 'FAILED'
            error_message = result.stderr.strip() if result.stderr else result.stdout.strip()
            output_path = None
            converter_used = 'Unknown'
            print(f"  ❌ Failed ({duration}s)")
            print(f"     Error: {error_message[:200]}...")
            if len(error_message) > 200:
                print(f"     (Full error saved in results)")
            # Also print stdout if available for more context
            if result.stdout and result.stdout.strip() != error_message:
                print(f"     Output: {result.stdout.strip()[:100]}...")
        
        return {
            'file_name': file_name,
            'file_type': file_type,
            'status': status,
            'duration_seconds': duration,
            'error_message': error_message,
            'output_path': output_path,
            'size_mb': file_info['size_mb'],
            'command': cmd,
            'converter_used': converter_used
        }
        
    except subprocess.TimeoutExpired:
        return {
            'file_name': file_name,
            'file_type': file_type,
            'status': 'TIMEOUT',
            'duration_seconds': 300,
            'error_message': 'Conversion timed out after 5 minutes',
            'output_path': None,
            'size_mb': file_info['size_mb'],
            'command': cmd,
            'converter_used': 'Unknown'
        }
    except Exception as e:
        return {
            'file_name': file_name,
            'file_type': file_type,
            'status': 'ERROR',
            'duration_seconds': 0,
            'error_message': str(e),
            'output_path': None,
            'size_mb': file_info['size_mb'],
            'command': cmd,
            'converter_used': 'Unknown'
        }

def run_bulk_conversion_tests():
    """Run conversion tests for all discovered files."""
    print(f"🚀 Starting bulk conversion tests...")
    print(f"📁 Output directory: {CONVERTED_OUTPUT_PATH}")
    
    # Create output directory
    os.makedirs(CONVERTED_OUTPUT_PATH, exist_ok=True)
    
    test_results = []
    total_start_time = time.time()
    
    for i, file_info in enumerate(files_catalog, 1):
        print(f"\n📝 Test {i}/{len(files_catalog)}: {file_info['file_name']}")
        # Enable verbose mode for debugging
        result = run_conversion_test(file_info, verbose=True)
        test_results.append(result)
    
    total_end_time = time.time()
    total_duration = round(total_end_time - total_start_time, 2)
    
    return test_results, total_duration

# Run the bulk conversion tests
print("🎯 Executing bulk conversion tests...")
test_results, total_test_duration = run_bulk_conversion_tests()

print(f"\n🏁 Bulk conversion testing completed in {total_test_duration} seconds!")

# COMMAND ----------

# DBTITLE 1,Generate Comprehensive Summary Report
# =============================================================================
# SUMMARY REPORT GENERATION
# =============================================================================

def generate_summary_report(test_results, total_duration):
    """Generate comprehensive summary report of conversion tests."""
    
    df_results = pd.DataFrame(test_results)
    
    # Overall statistics
    total_files = len(test_results)
    successful = len(df_results[df_results['status'] == 'SUCCESS'])
    failed = len(df_results[df_results['status'] == 'FAILED'])
    skipped = len(df_results[df_results['status'] == 'SKIPPED'])
    timeout = len(df_results[df_results['status'] == 'TIMEOUT'])
    errors = len(df_results[df_results['status'] == 'ERROR'])
    
    success_rate = round((successful / (total_files - skipped)) * 100, 1) if (total_files - skipped) > 0 else 0
    
    # Performance statistics
    successful_tests = df_results[df_results['status'] == 'SUCCESS']
    avg_duration = round(successful_tests['duration_seconds'].mean(), 2) if len(successful_tests) > 0 else 0
    total_conversion_time = round(df_results['duration_seconds'].sum(), 2)
    total_size_processed = round(successful_tests['size_mb'].sum(), 2)
    
    # Summary dictionary
    summary = {
        'test_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'pyforge_version': PYFORGE_VERSION,
        'total_files_tested': total_files,
        'successful_conversions': successful,
        'failed_conversions': failed,
        'skipped_files': skipped,
        'timeout_files': timeout,
        'error_files': errors,
        'success_rate_percent': success_rate,
        'total_test_duration_seconds': total_duration,
        'total_conversion_time_seconds': total_conversion_time,
        'average_conversion_time_seconds': avg_duration,
        'total_data_processed_mb': total_size_processed,
        'output_directory': CONVERTED_OUTPUT_PATH
    }
    
    return summary, df_results

# Generate summary report
summary_report, df_detailed_results = generate_summary_report(test_results, total_test_duration)

# COMMAND ----------

# DBTITLE 1,Display Summary Report
# =============================================================================
# SUMMARY REPORT DISPLAY
# =============================================================================

def display_summary_report(summary, detailed_results):
    """Display comprehensive summary report."""
    
    print("=" * 80)
    print("🎯 PYFORGE CLI CONVERSION TESTING SUMMARY REPORT")
    print("=" * 80)
    
    print(f"📅 Test Timestamp: {summary['test_timestamp']}")
    print(f"🔧 PyForge Version: {summary['pyforge_version']}")
    print(f"📁 Output Directory: {summary['output_directory']}")
    
    print("\n📊 OVERALL RESULTS:")
    print(f"   Total Files Tested: {summary['total_files_tested']}")
    print(f"   ✅ Successful: {summary['successful_conversions']}")
    print(f"   ❌ Failed: {summary['failed_conversions']}")
    print(f"   ⏭️  Skipped: {summary['skipped_files']}")
    print(f"   ⏰ Timeout: {summary['timeout_files']}")
    print(f"   🚫 Errors: {summary['error_files']}")
    print(f"   🎯 Success Rate: {summary['success_rate_percent']}%")
    
    print("\n⏱️  PERFORMANCE METRICS:")
    print(f"   Total Test Duration: {summary['total_test_duration_seconds']}s")
    print(f"   Total Conversion Time: {summary['total_conversion_time_seconds']}s")
    print(f"   Average Conversion Time: {summary['average_conversion_time_seconds']}s")
    print(f"   Total Data Processed: {summary['total_data_processed_mb']} MB")
    
    print("\n📋 RESULTS BY FILE TYPE:")
    type_summary = detailed_results.groupby('file_type').agg({
        'status': lambda x: (x == 'SUCCESS').sum(),
        'duration_seconds': 'sum',
        'size_mb': 'sum'
    }).round(2)
    type_summary.columns = ['successful_count', 'total_duration', 'total_size_mb']
    display(type_summary)
    
    print("\n📊 DETAILED RESULTS:")
    display(detailed_results[['file_name', 'file_type', 'status', 'duration_seconds', 'size_mb', 'converter_used', 'error_message']])
    
    # Show failed conversions details
    failed_tests = detailed_results[detailed_results['status'].isin(['FAILED', 'ERROR', 'TIMEOUT'])]
    if len(failed_tests) > 0:
        print(f"\n❌ FAILED CONVERSIONS DETAILS ({len(failed_tests)} failures):")
        display(failed_tests[['file_name', 'file_type', 'status', 'error_message']])
    
    print("=" * 80)

# Display the summary report
display_summary_report(summary_report, df_detailed_results)

# COMMAND ----------

# DBTITLE 1,Export Summary Report to JSON
# =============================================================================
# EXPORT SUMMARY REPORT
# =============================================================================

def export_summary_report(summary, detailed_results):
    """Export summary report to JSON file."""
    
    # Prepare export data
    export_data = {
        'summary': summary,
        'detailed_results': detailed_results.to_dict('records')
    }
    
    # Export to JSON file
    export_path = f"{CONVERTED_OUTPUT_PATH}/pyforge_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    
    with open(export_path, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"📄 Summary report exported to: {export_path}")
    return export_path

# Export the report
report_file_path = export_summary_report(summary_report, df_detailed_results)

# COMMAND ----------

# DBTITLE 1,Sample Converted File Validation
# =============================================================================
# CONVERTED FILE VALIDATION
# =============================================================================

def validate_converted_files():
    """Validate a sample of converted files to ensure they're readable."""
    print("🔍 Validating converted Parquet files...")
    
    successful_conversions = df_detailed_results[df_detailed_results['status'] == 'SUCCESS']
    validation_results = []
    
    for _, result in successful_conversions.head(5).iterrows():  # Validate first 5 successful conversions
        output_path = result['output_path']
        file_name = result['file_name']
        
        try:
            # Try to read the parquet file
            df = spark.read.parquet(output_path)
            row_count = df.count()
            col_count = len(df.columns)
            
            validation_results.append({
                'file_name': file_name,
                'status': 'VALID',
                'rows': row_count,
                'columns': col_count,
                'error': None
            })
            
            print(f"  ✅ {file_name}: {row_count} rows, {col_count} columns")
            
        except Exception as e:
            validation_results.append({
                'file_name': file_name,
                'status': 'INVALID',
                'rows': 0,
                'columns': 0,
                'error': str(e)
            })
            print(f"  ❌ {file_name}: Validation failed - {str(e)[:100]}...")
    
    if validation_results:
        print(f"\n📊 Validation Summary:")
        df_validation = pd.DataFrame(validation_results)
        display(df_validation)
    else:
        print("⚠️  No successful conversions to validate.")

# Run validation
validate_converted_files()

# COMMAND ----------

# DBTITLE 1,Final Test Summary and Recommendations
# =============================================================================
# FINAL SUMMARY AND RECOMMENDATIONS
# =============================================================================

print("🎉 ENHANCED PYFORGE CLI TESTING COMPLETED!")
print("=" * 60)

print(f"📊 FINAL STATISTICS:")
print(f"   PyForge Version Tested: {PYFORGE_VERSION}")
print(f"   Files Processed: {summary_report['total_files_tested']}")
print(f"   Success Rate: {summary_report['success_rate_percent']}%")
print(f"   Total Time: {summary_report['total_test_duration_seconds']}s")
print(f"   Data Processed: {summary_report['total_data_processed_mb']} MB")

print(f"\n📁 OUTPUTS:")
print(f"   Converted Files: {CONVERTED_OUTPUT_PATH}")
print(f"   Test Report: {report_file_path}")

print(f"\n💡 RECOMMENDATIONS:")
if summary_report['success_rate_percent'] >= 90:
    print("   ✅ Excellent performance! PyForge CLI is working well.")
elif summary_report['success_rate_percent'] >= 75:
    print("   ⚠️  Good performance with some issues. Review failed conversions.")
else:
    print("   ❌ Performance needs attention. Check failed conversions and error messages.")

if summary_report['failed_conversions'] > 0:
    print(f"   🔍 Review {summary_report['failed_conversions']} failed conversions for improvement opportunities.")

print("\n🎯 Testing completed successfully! Review the detailed results above for insights.")

# COMMAND ----------

# DBTITLE 1,Troubleshooting Guide
# MAGIC %md
# MAGIC ## 🔧 Troubleshooting Common Issues
# MAGIC 
# MAGIC ### 1. Package Not Updating After Changes
# MAGIC - **Solution**: Use Environment panel → Reset environment
# MAGIC - Alternative: Run `%pip install --no-cache-dir pyforge-cli==<version>`
# MAGIC 
# MAGIC ### 2. Import Errors After Installation
# MAGIC - **Solution**: Ensure Python kernel restart completed (`dbutils.library.restartPython()`)
# MAGIC - Check module location: `import pyforge_cli; print(pyforge_cli.__file__)`
# MAGIC 
# MAGIC ### 3. PySpark Converter Not Working
# MAGIC - Verify PySpark availability in the environment check cell
# MAGIC - Check if `--force-pyspark` flag is being applied
# MAGIC - Review conversion output for "Using PySpark" messages
# MAGIC 
# MAGIC ### 4. Old Version Still Being Used
# MAGIC 1. Uninstall old version: `%pip uninstall -y pyforge-cli`
# MAGIC 2. Clear caches: `spark.catalog.clearCache()`
# MAGIC 3. Restart Python: `dbutils.library.restartPython()`
# MAGIC 4. Install new version: `%pip install pyforge-cli==<version> --no-cache-dir`
# MAGIC 
# MAGIC ### 5. Permission Errors
# MAGIC - Verify Unity Catalog permissions for volume paths
# MAGIC - Check workspace permissions for notebook location
# MAGIC 
# MAGIC ### 6. Memory Issues
# MAGIC - Reduce dataset size or process in smaller batches
# MAGIC - Clear Spark cache between large operations: `spark.catalog.clearCache()`

# COMMAND ----------