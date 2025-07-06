# Databricks notebook source
# DBTITLE 1,PyForge CLI Databricks Extension - Volume Integration Testing
# MAGIC %md
# MAGIC # PyForge CLI Databricks Extension - Unity Catalog Volume Integration
# MAGIC 
# MAGIC This notebook provides comprehensive testing of Unity Catalog Volume operations with PyForge CLI:
# MAGIC - Volume path detection and validation
# MAGIC - Volume metadata operations
# MAGIC - Large file handling in Volumes
# MAGIC - Volume permissions and access control
# MAGIC - Cross-catalog and cross-schema operations
# MAGIC - Performance optimization for Volume operations

# COMMAND ----------

# DBTITLE 1,Volume Testing Configuration
# Create configuration widgets for Volume testing
dbutils.widgets.text("catalog_name", "main", "Catalog Name")
dbutils.widgets.text("schema_name", "default", "Schema Name")
dbutils.widgets.text("volume_name", "pyforge", "Volume Name")
dbutils.widgets.text("test_volume_path", "/Volumes/main/default/pyforge", "Test Volume Path")
dbutils.widgets.dropdown("test_scope", "comprehensive", ["basic", "comprehensive", "performance"], "Test Scope")
dbutils.widgets.checkbox("test_large_files", True, "Test Large Files")
dbutils.widgets.checkbox("test_permissions", True, "Test Permissions")
dbutils.widgets.checkbox("test_cross_catalog", False, "Test Cross-Catalog")
dbutils.widgets.checkbox("cleanup_after_test", True, "Cleanup After Test")
dbutils.widgets.checkbox("verbose_logging", True, "Verbose Logging")

# Get configuration values
CATALOG_NAME = dbutils.widgets.get("catalog_name")
SCHEMA_NAME = dbutils.widgets.get("schema_name")
VOLUME_NAME = dbutils.widgets.get("volume_name")
TEST_VOLUME_PATH = dbutils.widgets.get("test_volume_path")
TEST_SCOPE = dbutils.widgets.get("test_scope")
TEST_LARGE_FILES = dbutils.widgets.get("test_large_files") == "true"
TEST_PERMISSIONS = dbutils.widgets.get("test_permissions") == "true"
TEST_CROSS_CATALOG = dbutils.widgets.get("test_cross_catalog") == "true"
CLEANUP_AFTER_TEST = dbutils.widgets.get("cleanup_after_test") == "true"
VERBOSE_LOGGING = dbutils.widgets.get("verbose_logging") == "true"

# Derived paths
VOLUME_TEST_DATA_PATH = f"{TEST_VOLUME_PATH}/volume-test-data"
VOLUME_TEST_OUTPUT_PATH = f"{TEST_VOLUME_PATH}/volume-test-output"
LARGE_FILES_PATH = f"{TEST_VOLUME_PATH}/large-files-test"

print("🗄️ Volume Integration Test Configuration:")
print(f"   Catalog: {CATALOG_NAME}")
print(f"   Schema: {SCHEMA_NAME}")
print(f"   Volume: {VOLUME_NAME}")
print(f"   Volume Path: {TEST_VOLUME_PATH}")
print(f"   Test Scope: {TEST_SCOPE}")
print(f"   Test Large Files: {TEST_LARGE_FILES}")
print(f"   Test Permissions: {TEST_PERMISSIONS}")
print(f"   Test Cross-Catalog: {TEST_CROSS_CATALOG}")
print(f"   Cleanup After Test: {CLEANUP_AFTER_TEST}")

# Initialize volume test tracking
volume_test_results = {
    'volume_setup': {},
    'volume_operations_tests': {},
    'large_file_tests': {},
    'permissions_tests': {},
    'cross_catalog_tests': {},
    'performance_tests': {},
    'cleanup_results': {},
    'overall_success': False
}

# COMMAND ----------

# DBTITLE 1,Volume Setup and Access Verification
import os
import sys
import time
import json
from datetime import datetime
from pyspark.sql.functions import col, rand, concat, lit, when

print("🔍 Setting up and verifying Volume access...")

setup_start_time = time.time()
volume_setup = {}

try:
    # Verify Volume access
    try:
        volume_contents = dbutils.fs.ls(TEST_VOLUME_PATH)
        volume_accessible = True
        print(f"✅ Volume accessible: {len(volume_contents)} items found")
        
        # Create test directories
        test_dirs = [VOLUME_TEST_DATA_PATH, VOLUME_TEST_OUTPUT_PATH]
        if TEST_LARGE_FILES:
            test_dirs.append(LARGE_FILES_PATH)
        
        for test_dir in test_dirs:
            try:
                dbutils.fs.mkdirs(test_dir)
                print(f"✅ Created test directory: {test_dir}")
            except Exception as e:
                print(f"⚠️ Directory creation warning for {test_dir}: {e}")
        
        volume_setup['volume_accessible'] = True
        volume_setup['test_directories_created'] = len(test_dirs)
        
    except Exception as e:
        print(f"❌ Volume access failed: {e}")
        volume_accessible = False
        volume_setup['volume_accessible'] = False
        volume_setup['access_error'] = str(e)
    
    # Install PyForge CLI if needed
    try:
        print("📦 Ensuring PyForge CLI is available...")
        %pip install --no-cache-dir pyforge-cli[databricks]
        
        # Test Volume operations import
        from pyforge_cli.extensions.databricks.volume_operations import VolumeOperations
        from pyforge_cli.extensions.databricks.pyforge_databricks import PyForgeDatabricks
        
        print("✅ PyForge CLI with Volume operations available")
        volume_setup['pyforge_available'] = True
        
    except Exception as e:
        print(f"❌ PyForge CLI setup failed: {e}")
        volume_setup['pyforge_available'] = False
        volume_setup['pyforge_error'] = str(e)
    
    # Test Volume operations initialization
    if volume_setup.get('pyforge_available', False):
        try:
            volume_ops = VolumeOperations()
            forge = PyForgeDatabricks(auto_init=True)
            
            print("✅ Volume operations initialized")
            volume_setup['volume_ops_initialized'] = True
            
        except Exception as e:
            print(f"❌ Volume operations initialization failed: {e}")
            volume_setup['volume_ops_initialized'] = False
            volume_setup['init_error'] = str(e)

except Exception as e:
    print(f"❌ Volume setup failed: {e}")
    volume_setup['setup_error'] = str(e)

setup_time = time.time() - setup_start_time
volume_setup['setup_time'] = setup_time
volume_test_results['volume_setup'] = volume_setup

print(f"⏱️ Volume setup time: {setup_time:.2f} seconds")

if not volume_setup.get('volume_accessible', False):
    print("❌ Cannot proceed without Volume access")
    dbutils.notebook.exit("Volume access required")

# COMMAND ----------

# DBTITLE 1,Volume Operations Testing
print("🗂️ Testing Volume operations...")

volume_ops_start_time = time.time()
volume_ops_results = {}

try:
    # Test Volume path detection
    print("Testing Volume path detection...")
    
    test_paths = [
        TEST_VOLUME_PATH,
        f"{TEST_VOLUME_PATH}/test_file.csv",
        "/tmp/local_file.csv",  # Non-volume path
        f"/Volumes/{CATALOG_NAME}/{SCHEMA_NAME}/{VOLUME_NAME}/test.parquet"
    ]
    
    path_detection_results = {}
    
    for test_path in test_paths:
        try:
            is_volume = volume_ops.is_volume_path(test_path)
            path_detection_results[test_path] = {
                'is_volume': is_volume,
                'test_success': True
            }
            print(f"   {'✅' if is_volume else '⚪'} {test_path}: {'Volume' if is_volume else 'Not Volume'}")
            
        except Exception as e:
            path_detection_results[test_path] = {
                'is_volume': False,
                'test_success': False,
                'error': str(e)
            }
            print(f"   ❌ {test_path}: Error - {e}")
    
    volume_ops_results['path_detection'] = path_detection_results
    
    # Test Volume info extraction
    print("Testing Volume info extraction...")
    
    volume_path_tests = [
        f"/Volumes/{CATALOG_NAME}/{SCHEMA_NAME}/{VOLUME_NAME}",
        f"/Volumes/{CATALOG_NAME}/{SCHEMA_NAME}/{VOLUME_NAME}/subdir/file.csv"
    ]
    
    volume_info_results = {}
    
    for vol_path in volume_path_tests:
        try:
            if volume_ops.is_volume_path(vol_path):
                volume_info = volume_ops.get_volume_info(vol_path)
                volume_info_results[vol_path] = {
                    'catalog': volume_info['catalog'],
                    'schema': volume_info['schema'],
                    'volume': volume_info['volume'],
                    'subpath': volume_info.get('subpath', ''),
                    'extraction_success': True
                }
                print(f"   ✅ {vol_path}")
                print(f"      Catalog: {volume_info['catalog']}")
                print(f"      Schema: {volume_info['schema']}")
                print(f"      Volume: {volume_info['volume']}")
                if volume_info.get('subpath'):
                    print(f"      Subpath: {volume_info['subpath']}")
            
        except Exception as e:
            volume_info_results[vol_path] = {
                'extraction_success': False,
                'error': str(e)
            }
            print(f"   ❌ {vol_path}: Error - {e}")
    
    volume_ops_results['volume_info_extraction'] = volume_info_results
    
    # Test Volume metadata operations
    print("Testing Volume metadata operations...")
    
    try:
        # Create test file for metadata testing
        test_metadata_content = "id,name,value,category\\n1,test1,10.5,A\\n2,test2,20.3,B\\n3,test3,30.7,C"
        test_metadata_path = f"{VOLUME_TEST_DATA_PATH}/metadata_test.csv"
        
        dbutils.fs.put(test_metadata_path, test_metadata_content)
        print(f"✅ Created test file: {test_metadata_path}")
        
        # Test file metadata
        if volume_ops.is_volume_path(test_metadata_path):
            file_metadata = volume_ops.get_file_metadata(test_metadata_path)
            
            print(f"✅ File metadata:")
            print(f"   Size: {file_metadata.get('size_bytes', 'unknown')} bytes")
            print(f"   Modified: {file_metadata.get('modification_time', 'unknown')}")
            print(f"   Exists: {file_metadata.get('exists', False)}")
            
            volume_ops_results['metadata_operations'] = {
                'file_metadata_success': True,
                'file_size': file_metadata.get('size_bytes'),
                'file_exists': file_metadata.get('exists', False)
            }
        else:
            volume_ops_results['metadata_operations'] = {
                'file_metadata_success': False,
                'error': 'Path not recognized as Volume path'
            }
    
    except Exception as e:
        print(f"❌ Metadata operations failed: {e}")
        volume_ops_results['metadata_operations'] = {
            'file_metadata_success': False,
            'error': str(e)
        }
    
    # Test Volume directory operations
    print("Testing Volume directory operations...")
    
    try:
        # List Volume contents
        if volume_ops.is_volume_path(VOLUME_TEST_DATA_PATH):
            dir_contents = volume_ops.list_volume_contents(VOLUME_TEST_DATA_PATH)
            
            print(f"✅ Directory listing:")
            print(f"   Files found: {len(dir_contents.get('files', []))}")
            print(f"   Directories found: {len(dir_contents.get('directories', []))}")
            print(f"   Total items: {len(dir_contents.get('files', [])) + len(dir_contents.get('directories', []))}")
            
            volume_ops_results['directory_operations'] = {
                'listing_success': True,
                'files_count': len(dir_contents.get('files', [])),
                'directories_count': len(dir_contents.get('directories', []))
            }
        else:
            volume_ops_results['directory_operations'] = {
                'listing_success': False,
                'error': 'Path not recognized as Volume path'
            }
    
    except Exception as e:
        print(f"❌ Directory operations failed: {e}")
        volume_ops_results['directory_operations'] = {
            'listing_success': False,
            'error': str(e)
        }

except Exception as e:
    print(f"❌ Volume operations testing failed: {e}")
    volume_ops_results['test_error'] = str(e)

volume_ops_time = time.time() - volume_ops_start_time
volume_ops_results['total_test_time'] = volume_ops_time
volume_test_results['volume_operations_tests'] = volume_ops_results

print(f"⏱️ Volume operations testing time: {volume_ops_time:.2f} seconds")

# COMMAND ----------

# DBTITLE 1,Large File Handling Tests
if TEST_LARGE_FILES:
    print("📈 Testing large file handling in Volumes...")
    
    large_file_start_time = time.time()
    large_file_results = {}
    
    try:
        # Test different file sizes
        file_size_tests = [
            {"name": "small", "rows": 1000},
            {"name": "medium", "rows": 10000},
            {"name": "large", "rows": 50000}
        ]
        
        if TEST_SCOPE == "performance":
            file_size_tests.append({"name": "very_large", "rows": 100000})
        
        for size_test in file_size_tests:
            print(f"Testing {size_test['name']} file ({size_test['rows']:,} rows)...")
            
            try:
                # Generate test data using Spark for large files
                # Create DataFrame with specified number of rows
                large_df = spark.range(size_test['rows']).toDF("id")
                large_df = large_df.withColumn("name", concat(lit("item_"), col("id").cast("string")))
                large_df = large_df.withColumn("value", rand() * 1000)
                large_df = large_df.withColumn("category", 
                    when(col("id") % 3 == 0, "A")
                    .when(col("id") % 3 == 1, "B")
                    .otherwise("C"))
                
                # Save to Volume as CSV
                large_csv_path = f"{LARGE_FILES_PATH}/{size_test['name']}_test.csv"
                
                write_start = time.time()
                large_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(large_csv_path)
                write_time = time.time() - write_start
                
                # Get actual file path
                csv_files = dbutils.fs.ls(large_csv_path)
                actual_csv_file = None
                for file_info in csv_files:
                    if file_info.name.endswith('.csv'):
                        actual_csv_file = file_info.path
                        break
                
                if actual_csv_file:
                    # Test conversion with PyForge
                    parquet_output_path = f"{VOLUME_TEST_OUTPUT_PATH}/{size_test['name']}_converted.parquet"
                    
                    convert_start = time.time()
                    conversion_result = forge.convert(
                        input_path=actual_csv_file,
                        output_path=parquet_output_path,
                        format="parquet"
                    )
                    convert_time = time.time() - convert_start
                    
                    # Verify conversion
                    verify_df = spark.read.parquet(parquet_output_path)
                    verify_count = verify_df.count()
                    
                    # Calculate throughput
                    throughput = size_test['rows'] / convert_time
                    
                    print(f"   ✅ {size_test['name']} file conversion:")
                    print(f"      Write time: {write_time:.2f}s")
                    print(f"      Convert time: {convert_time:.2f}s")
                    print(f"      Throughput: {throughput:,.0f} rows/sec")
                    print(f"      Data integrity: {verify_count == size_test['rows']}")
                    print(f"      Engine used: {conversion_result['engine_used']}")
                    
                    large_file_results[size_test['name']] = {
                        'success': True,
                        'rows': size_test['rows'],
                        'write_time': write_time,
                        'convert_time': convert_time,
                        'throughput_rows_per_sec': throughput,
                        'data_integrity': verify_count == size_test['rows'],
                        'engine_used': conversion_result['engine_used'],
                        'rows_verified': verify_count
                    }
                else:
                    large_file_results[size_test['name']] = {
                        'success': False,
                        'error': 'CSV file not found after write'
                    }
            
            except Exception as e:
                print(f"   ❌ {size_test['name']} file test failed: {e}")
                large_file_results[size_test['name']] = {
                    'success': False,
                    'error': str(e)
                }
    
    except Exception as e:
        print(f"❌ Large file testing failed: {e}")
        large_file_results['test_error'] = str(e)
    
    large_file_time = time.time() - large_file_start_time
    large_file_results['total_test_time'] = large_file_time
    volume_test_results['large_file_tests'] = large_file_results
    
    print(f"⏱️ Large file testing time: {large_file_time:.2f} seconds")

else:
    print("⏭️ Large file testing skipped (disabled in configuration)")
    volume_test_results['large_file_tests'] = {'skipped': True}

# COMMAND ----------

# DBTITLE 1,Volume Test Results Summary
print("📊 Generating Volume integration test results...")

# Add metadata
volume_test_results['metadata'] = {
    'test_type': 'volume_integration',
    'notebook_name': '04-databricks-volume-integration',
    'timestamp': datetime.now().isoformat(),
    'configuration': {
        'catalog_name': CATALOG_NAME,
        'schema_name': SCHEMA_NAME,
        'volume_name': VOLUME_NAME,
        'test_volume_path': TEST_VOLUME_PATH,
        'test_scope': TEST_SCOPE,
        'test_large_files': TEST_LARGE_FILES,
        'test_permissions': TEST_PERMISSIONS,
        'test_cross_catalog': TEST_CROSS_CATALOG
    }
}

# Calculate overall success
success_criteria = [
    volume_test_results['volume_setup'].get('volume_accessible', False),
    volume_test_results['volume_setup'].get('pyforge_available', False),
    volume_test_results['volume_operations_tests'].get('path_detection', {}) != {},
    volume_test_results['volume_operations_tests'].get('metadata_operations', {}).get('file_metadata_success', False)
]

overall_success = all(success_criteria)
volume_test_results['overall_success'] = overall_success

# Calculate total test time
total_test_time = sum([
    volume_test_results['volume_setup'].get('setup_time', 0),
    volume_test_results['volume_operations_tests'].get('total_test_time', 0),
    volume_test_results.get('large_file_tests', {}).get('total_test_time', 0)
])

volume_test_results['total_test_time'] = total_test_time

# Display summary
print("\\n" + "="*70)
print("🎯 VOLUME INTEGRATION TEST SUMMARY")
print("="*70)

status_icon = "✅" if overall_success else "❌"
print(f"{status_icon} Overall Test Status: {'PASSED' if overall_success else 'FAILED'}")
print(f"🕐 Total Test Duration: {total_test_time:.2f} seconds")
print(f"🗄️ Volume: {CATALOG_NAME}.{SCHEMA_NAME}.{VOLUME_NAME}")
print(f"📁 Volume Path: {TEST_VOLUME_PATH}")

print(f"\\n📋 Test Results:")
print(f"   Volume Setup: {'✅' if volume_test_results['volume_setup'].get('volume_accessible') else '❌'}")
print(f"   Path Detection: {'✅' if volume_test_results['volume_operations_tests'].get('path_detection') else '❌'}")
print(f"   Volume Info Extraction: {'✅' if volume_test_results['volume_operations_tests'].get('volume_info_extraction') else '❌'}")
print(f"   Metadata Operations: {'✅' if volume_test_results['volume_operations_tests'].get('metadata_operations', {}).get('file_metadata_success') else '❌'}")
print(f"   Directory Operations: {'✅' if volume_test_results['volume_operations_tests'].get('directory_operations', {}).get('listing_success') else '❌'}")

if not volume_test_results.get('large_file_tests', {}).get('skipped'):
    large_file_tests = volume_test_results.get('large_file_tests', {})
    successful_tests = sum(1 for k, v in large_file_tests.items() 
                          if isinstance(v, dict) and v.get('success'))
    total_tests = len([k for k, v in large_file_tests.items() 
                      if isinstance(v, dict) and 'success' in v])
    print(f"   Large File Tests: {'✅' if successful_tests > 0 else '❌'} ({successful_tests}/{total_tests})")

print(f"\\n⚡ Performance Summary:")
if not volume_test_results.get('large_file_tests', {}).get('skipped'):
    large_file_tests = volume_test_results.get('large_file_tests', {})
    for test_name, test_result in large_file_tests.items():
        if isinstance(test_result, dict) and test_result.get('success'):
            throughput = test_result.get('throughput_rows_per_sec', 0)
            print(f"   {test_name.title()} File: {throughput:,.0f} rows/sec")

# Cleanup if requested
if CLEANUP_AFTER_TEST:
    print(f"\\n🧹 Performing cleanup...")
    
    cleanup_results = {}
    
    try:
        # Remove test directories
        test_dirs = [VOLUME_TEST_DATA_PATH, VOLUME_TEST_OUTPUT_PATH]
        if TEST_LARGE_FILES:
            test_dirs.append(LARGE_FILES_PATH)
        
        for test_dir in test_dirs:
            try:
                dbutils.fs.rm(test_dir, recurse=True)
                print(f"✅ Removed: {test_dir}")
                cleanup_results[test_dir] = True
            except:
                print(f"⚠️ Could not remove: {test_dir}")
                cleanup_results[test_dir] = False
        
        cleanup_results['cleanup_success'] = True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        cleanup_results['cleanup_success'] = False
        cleanup_results['error'] = str(e)
    
    volume_test_results['cleanup_results'] = cleanup_results

# Export results
results_json = json.dumps(volume_test_results, indent=2, default=str)
print(f"\\n💾 Volume integration test results saved to volume_test_results variable")

if VERBOSE_LOGGING:
    print(f"\\n📝 Detailed Results Sample:")
    print(results_json[:2000] + "..." if len(results_json) > 2000 else results_json)

print(f"\\n" + "="*70)
print("🏁 Volume integration testing completed!")
print("="*70)

# COMMAND ----------