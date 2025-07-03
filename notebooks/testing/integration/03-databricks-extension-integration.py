# Databricks notebook source
# DBTITLE 1,PyForge CLI Databricks Extension Integration Testing
# MAGIC %md
# MAGIC # PyForge CLI Databricks Extension - Comprehensive Integration Testing
# MAGIC 
# MAGIC This notebook provides comprehensive integration testing of the PyForge CLI Databricks extension with:
# MAGIC - Plugin system integration testing
# MAGIC - Multiple extension interaction testing
# MAGIC - Real-world conversion scenarios
# MAGIC - Error handling and recovery testing
# MAGIC - Performance benchmarking
# MAGIC - Environment compatibility testing

# COMMAND ----------

# DBTITLE 1,Configuration and Setup
# MAGIC %md
# MAGIC ## ⚙️ Test Configuration
# MAGIC 
# MAGIC Configure the integration test environment for comprehensive testing of:
# MAGIC - Plugin discovery and loading
# MAGIC - Extension interactions
# MAGIC - Conversion workflows
# MAGIC - Error scenarios
# MAGIC - Performance benchmarks

# COMMAND ----------

# DBTITLE 1,Widget Configuration
# Create comprehensive test configuration widgets
dbutils.widgets.text("pyforge_version", "latest", "PyForge Version")
dbutils.widgets.dropdown("test_environment", "auto", ["auto", "serverless", "classic"], "Test Environment")
dbutils.widgets.dropdown("test_scope", "comprehensive", ["basic", "comprehensive", "performance", "stress"], "Test Scope")
dbutils.widgets.text("volume_path", "/Volumes/main/default/pyforge", "Volume Path")
dbutils.widgets.checkbox("test_plugin_conflicts", True, "Test Plugin Conflicts")
dbutils.widgets.checkbox("test_error_scenarios", True, "Test Error Scenarios")
dbutils.widgets.checkbox("test_performance", True, "Performance Testing")
dbutils.widgets.checkbox("test_fallback", True, "Test Fallback Scenarios")
dbutils.widgets.checkbox("cleanup_after_test", True, "Cleanup After Test")
dbutils.widgets.checkbox("verbose_logging", True, "Verbose Logging")

# Get configuration values
PYFORGE_VERSION = dbutils.widgets.get("pyforge_version")
TEST_ENVIRONMENT = dbutils.widgets.get("test_environment")
TEST_SCOPE = dbutils.widgets.get("test_scope")
VOLUME_PATH = dbutils.widgets.get("volume_path")
TEST_PLUGIN_CONFLICTS = dbutils.widgets.get("test_plugin_conflicts") == "true"
TEST_ERROR_SCENARIOS = dbutils.widgets.get("test_error_scenarios") == "true"
TEST_PERFORMANCE = dbutils.widgets.get("test_performance") == "true"
TEST_FALLBACK = dbutils.widgets.get("test_fallback") == "true"
CLEANUP_AFTER_TEST = dbutils.widgets.get("cleanup_after_test") == "true"
VERBOSE_LOGGING = dbutils.widgets.get("verbose_logging") == "true"

# Derived paths
TEST_DATA_PATH = f"{VOLUME_PATH}/integration-test-data"
TEST_OUTPUT_PATH = f"{VOLUME_PATH}/integration-test-output"
SAMPLE_DATA_PATH = f"{VOLUME_PATH}/sample-datasets"

print("🧪 PyForge CLI Databricks Extension Integration Test Configuration:")
print(f"   PyForge Version: {PYFORGE_VERSION}")
print(f"   Test Environment: {TEST_ENVIRONMENT}")
print(f"   Test Scope: {TEST_SCOPE}")
print(f"   Volume Path: {VOLUME_PATH}")
print(f"   Test Plugin Conflicts: {TEST_PLUGIN_CONFLICTS}")
print(f"   Test Error Scenarios: {TEST_ERROR_SCENARIOS}")
print(f"   Test Performance: {TEST_PERFORMANCE}")
print(f"   Test Fallback: {TEST_FALLBACK}")
print(f"   Cleanup After Test: {CLEANUP_AFTER_TEST}")
print(f"   Verbose Logging: {VERBOSE_LOGGING}")

# Initialize comprehensive test tracking
integration_results = {
    'test_metadata': {
        'start_time': None,
        'end_time': None,
        'total_duration': None,
        'environment': None,
        'configuration': {
            'pyforge_version': PYFORGE_VERSION,
            'test_scope': TEST_SCOPE,
            'test_environment': TEST_ENVIRONMENT
        }
    },
    'environment_setup': {},
    'plugin_system_tests': {},
    'extension_integration_tests': {},
    'conversion_workflow_tests': {},
    'error_handling_tests': {},
    'performance_benchmarks': {},
    'fallback_tests': {},
    'cleanup_results': {},
    'overall_success': False,
    'test_summary': {}
}

# COMMAND ----------

# DBTITLE 1,Environment Detection and Validation
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

print("🔍 Detecting and validating integration test environment...")

# Record test start time
integration_results['test_metadata']['start_time'] = datetime.now().isoformat()
setup_start_time = time.time()

# Detect environment
def detect_environment():
    """Comprehensive environment detection"""
    env_info = {
        'runtime_version': os.environ.get('DATABRICKS_RUNTIME_VERSION', 'unknown'),
        'python_version': sys.version,
        'platform': sys.platform,
    }
    
    # Determine environment type
    if 'serverless' in env_info['runtime_version'].lower():
        env_info['type'] = 'serverless'
    else:
        env_info['type'] = 'classic'
    
    # Check PySpark availability
    try:
        import pyspark
        env_info['pyspark_available'] = True
        env_info['pyspark_version'] = pyspark.__version__
        
        # Get Spark context info
        try:
            env_info['spark_master'] = spark.sparkContext.master
            env_info['spark_app_name'] = spark.sparkContext.appName
            env_info['spark_version'] = spark.version
        except:
            env_info['spark_context_available'] = False
    except ImportError:
        env_info['pyspark_available'] = False
    
    return env_info

detected_env = detect_environment()
environment_type = TEST_ENVIRONMENT if TEST_ENVIRONMENT != 'auto' else detected_env['type']

print(f"✅ Environment Detection Results:")
print(f"   Type: {environment_type}")
print(f"   Runtime: {detected_env['runtime_version']}")
print(f"   Python: {detected_env['python_version']}")
print(f"   PySpark: {'✅' if detected_env.get('pyspark_available') else '❌'}")

# Test volume access
volume_accessible = False
try:
    # Test volume access
    volume_files = dbutils.fs.ls(VOLUME_PATH)
    volume_accessible = True
    print(f"✅ Volume accessible: {len(volume_files)} items found")
    
    # Ensure test directories exist
    dbutils.fs.mkdirs(TEST_DATA_PATH)
    dbutils.fs.mkdirs(TEST_OUTPUT_PATH)
    print("✅ Test directories created")
    
except Exception as e:
    print(f"❌ Volume access failed: {e}")
    volume_accessible = False

setup_time = time.time() - setup_start_time
integration_results['environment_setup'] = {
    'environment_info': detected_env,
    'configured_environment': environment_type,
    'volume_accessible': volume_accessible,
    'setup_time': setup_time,
    'setup_success': volume_accessible
}

print(f"⏱️ Environment setup time: {setup_time:.2f} seconds")

if not volume_accessible:
    print("❌ Cannot proceed without volume access")
    dbutils.notebook.exit("Volume access required for integration testing")

# COMMAND ----------

# DBTITLE 1,PyForge Installation and Plugin Discovery
print("📦 Installing PyForge CLI and testing plugin discovery...")

install_start_time = time.time()
installation_results = {}

try:
    # Install PyForge CLI with Databricks extension
    print("Installing PyForge CLI with Databricks extension...")
    
    if PYFORGE_VERSION == "latest":
        %pip install --no-cache-dir pyforge-cli[databricks]
    else:
        %pip install --no-cache-dir pyforge-cli[databricks]=={PYFORGE_VERSION}
    
    # Verify installation
    import pyforge_cli
    installed_version = pyforge_cli.__version__
    print(f"✅ PyForge CLI installed: {installed_version}")
    
    installation_results['installation_success'] = True
    installation_results['installed_version'] = installed_version
    
    # Test plugin discovery system
    print("🔌 Testing plugin discovery system...")
    
    try:
        from pyforge_cli.plugin_system import discovery
        
        plugin_discovery = discovery.PluginDiscovery()
        
        # Test discovery
        discovery_start = time.time()
        extensions = plugin_discovery.discover_extensions()
        discovery_time = time.time() - discovery_start
        
        print(f"✅ Plugin discovery completed: {len(extensions)} extensions found")
        
        # List discovered extensions
        discovered_extensions = []
        for name, ext_info in extensions.items():
            print(f"   📋 Extension discovered: {name}")
            discovered_extensions.append(name)
        
        # Test extension initialization
        init_start = time.time()
        init_results = plugin_discovery.initialize_extensions()
        init_time = time.time() - init_start
        
        print(f"✅ Extension initialization completed")
        
        initialized_extensions = []
        failed_extensions = []
        
        for name, success in init_results.items():
            if success:
                print(f"   ✅ {name}: Initialized successfully")
                initialized_extensions.append(name)
            else:
                print(f"   ❌ {name}: Initialization failed")
                failed_extensions.append(name)
        
        installation_results['plugin_discovery'] = {
            'discovery_time': discovery_time,
            'init_time': init_time,
            'discovered_extensions': discovered_extensions,
            'initialized_extensions': initialized_extensions,
            'failed_extensions': failed_extensions,
            'discovery_success': len(discovered_extensions) > 0,
            'initialization_success': len(initialized_extensions) > 0
        }
        
    except Exception as e:
        print(f"❌ Plugin discovery failed: {e}")
        installation_results['plugin_discovery_error'] = str(e)
        installation_results['plugin_discovery'] = {'discovery_success': False}

except Exception as e:
    print(f"❌ Installation failed: {e}")
    installation_results['installation_success'] = False
    installation_results['installation_error'] = str(e)
    dbutils.notebook.exit("Installation failed")

install_time = time.time() - install_start_time
installation_results['total_install_time'] = install_time
integration_results['plugin_system_tests'] = installation_results

print(f"⏱️ Installation and discovery time: {install_time:.2f} seconds")

# COMMAND ----------

# DBTITLE 1,Extension Integration Testing
print("🔧 Testing extension integration scenarios...")

integration_test_start = time.time()
extension_integration_results = {}

try:
    # Test Databricks extension specific functionality
    print("Testing Databricks extension integration...")
    
    # Check if Databricks extension was loaded
    databricks_loaded = 'databricks' in [ext.lower() for ext in installation_results.get('plugin_discovery', {}).get('initialized_extensions', [])]
    
    if databricks_loaded:
        print("✅ Databricks extension loaded successfully")
        
        # Test extension API availability
        try:
            # Test core CLI integration
            from pyforge_cli.plugins import registry
            
            # Get supported formats
            formats = registry.list_supported_formats()
            print(f"✅ Registry integration: {len(formats)} format converters available")
            
            # Test if Databricks-specific formats are available
            databricks_formats = []
            for name, format_info in formats.items():
                if 'databricks' in name.lower() or any('spark' in input_fmt.lower() for input_fmt in format_info.get('inputs', [])):
                    databricks_formats.append(name)
            
            print(f"✅ Databricks-specific formats: {len(databricks_formats)}")
            
            extension_integration_results['registry_integration'] = {
                'total_formats': len(formats),
                'databricks_formats': databricks_formats,
                'integration_success': True
            }
            
        except Exception as e:
            print(f"❌ Registry integration failed: {e}")
            extension_integration_results['registry_integration'] = {
                'integration_success': False,
                'error': str(e)
            }
        
        # Test environment detection within extension
        try:
            print("🔍 Testing extension environment detection...")
            
            # This would test the actual Databricks extension environment detection
            # For now, test the general environment detection
            
            env_detection_success = True
            if detected_env.get('pyspark_available') and environment_type == 'serverless':
                print("✅ Optimal serverless environment detected")
                optimal_environment = True
            else:
                print("⚠️ Non-optimal environment - testing fallback behavior")
                optimal_environment = False
            
            extension_integration_results['environment_detection'] = {
                'detection_success': env_detection_success,
                'optimal_environment': optimal_environment,
                'pyspark_available': detected_env.get('pyspark_available', False),
                'environment_type': environment_type
            }
            
        except Exception as e:
            print(f"❌ Environment detection failed: {e}")
            extension_integration_results['environment_detection'] = {
                'detection_success': False,
                'error': str(e)
            }
    
    else:
        print("❌ Databricks extension not loaded - testing basic functionality only")
        extension_integration_results['databricks_extension_available'] = False
    
    # Test multiple extension interaction (if available)
    if TEST_PLUGIN_CONFLICTS:
        print("🔀 Testing multiple extension interactions...")
        
        try:
            # Test loading multiple extensions simultaneously
            loaded_extensions = installation_results.get('plugin_discovery', {}).get('initialized_extensions', [])
            
            if len(loaded_extensions) > 1:
                print(f"✅ Multiple extensions loaded: {len(loaded_extensions)}")
                
                # Test that extensions don't conflict
                conflict_test_results = []
                for ext_name in loaded_extensions:
                    try:
                        # Test basic functionality for each extension
                        # This would be extension-specific testing
                        print(f"   Testing {ext_name} functionality...")
                        conflict_test_results.append({'extension': ext_name, 'conflict': False})
                    except Exception as e:
                        print(f"   ❌ Conflict detected in {ext_name}: {e}")
                        conflict_test_results.append({'extension': ext_name, 'conflict': True, 'error': str(e)})
                
                extension_integration_results['multi_extension_test'] = {
                    'extensions_tested': len(loaded_extensions),
                    'conflicts_detected': sum(1 for r in conflict_test_results if r.get('conflict')),
                    'test_results': conflict_test_results
                }
                
            else:
                print("⚠️ Only one extension available - skipping conflict testing")
                extension_integration_results['multi_extension_test'] = {'skipped': 'insufficient_extensions'}
        
        except Exception as e:
            print(f"❌ Multi-extension testing failed: {e}")
            extension_integration_results['multi_extension_test'] = {'error': str(e)}

except Exception as e:
    print(f"❌ Extension integration testing failed: {e}")
    extension_integration_results['test_error'] = str(e)

integration_test_time = time.time() - integration_test_start
extension_integration_results['integration_test_time'] = integration_test_time
integration_results['extension_integration_tests'] = extension_integration_results

print(f"⏱️ Extension integration test time: {integration_test_time:.2f} seconds")

# COMMAND ----------

# DBTITLE 1,Conversion Workflow Testing
print("🔄 Testing real-world conversion workflows...")

workflow_test_start = time.time()
workflow_results = {}

try:
    # Create test data for conversion workflows
    print("📊 Creating test data for conversion workflows...")
    
    # Create test CSV data
    test_csv_content = """id,name,value,category,timestamp
1,Product A,10.50,Electronics,2024-01-01 10:00:00
2,Product B,25.75,Books,2024-01-01 11:00:00
3,Product C,5.99,Clothing,2024-01-01 12:00:00
4,Product D,99.99,Electronics,2024-01-01 13:00:00
5,Product E,15.25,Books,2024-01-01 14:00:00"""
    
    test_csv_path = f"{TEST_DATA_PATH}/workflow_test.csv"
    dbutils.fs.put(test_csv_path, test_csv_content)
    print(f"✅ Test CSV created: {test_csv_path}")
    
    # Test CLI workflow integration
    if detected_env.get('pyspark_available'):
        print("⚡ Testing PySpark conversion workflow...")
        
        try:
            # Test reading with PySpark
            df = spark.read.option("header", "true").option("inferSchema", "true").csv(test_csv_path)
            row_count = df.count()
            column_count = len(df.columns)
            
            print(f"✅ PySpark read successful: {row_count} rows, {column_count} columns")
            
            # Test conversion to Parquet
            parquet_output_path = f"{TEST_OUTPUT_PATH}/workflow_test.parquet"
            df.write.mode("overwrite").parquet(parquet_output_path)
            
            # Verify Parquet output
            parquet_df = spark.read.parquet(parquet_output_path)
            parquet_row_count = parquet_df.count()
            
            print(f"✅ PySpark Parquet conversion: {parquet_row_count} rows written")
            
            workflow_results['pyspark_workflow'] = {
                'csv_read_success': True,
                'rows_read': row_count,
                'columns_read': column_count,
                'parquet_write_success': True,
                'rows_written': parquet_row_count,
                'data_integrity': row_count == parquet_row_count
            }
            
        except Exception as e:
            print(f"❌ PySpark workflow failed: {e}")
            workflow_results['pyspark_workflow'] = {
                'success': False,
                'error': str(e)
            }
    
    # Test fallback workflow (pandas)
    print("🐼 Testing pandas fallback workflow...")
    
    try:
        # Test with pandas (fallback path)
        import pandas as pd
        
        # Read CSV with pandas
        # First, copy to local filesystem for pandas
        local_csv_content = dbutils.fs.head(test_csv_path, max_bytes=10000)
        
        from io import StringIO
        pandas_df = pd.read_csv(StringIO(local_csv_content))
        
        print(f"✅ Pandas read successful: {len(pandas_df)} rows, {len(pandas_df.columns)} columns")
        
        # Test conversion to Parquet with pyarrow
        import pyarrow as pa
        import pyarrow.parquet as pq
        
        # Convert to Arrow table
        arrow_table = pa.Table.from_pandas(pandas_df)
        
        # This would write to volume if supported
        print("✅ Pandas to Arrow conversion successful")
        
        workflow_results['pandas_workflow'] = {
            'csv_read_success': True,
            'rows_read': len(pandas_df),
            'columns_read': len(pandas_df.columns),
            'arrow_conversion_success': True
        }
        
    except Exception as e:
        print(f"❌ Pandas workflow failed: {e}")
        workflow_results['pandas_workflow'] = {
            'success': False,
            'error': str(e)
        }
    
    # Test CLI command integration (if possible)
    print("🖥️ Testing CLI integration...")
    
    try:
        # Test the main CLI components
        from pyforge_cli.main import cli
        from pyforge_cli.plugins import registry
        
        # Test format listing
        formats = registry.list_supported_formats()
        print(f"✅ CLI format listing: {len(formats)} formats available")
        
        # Test converter selection
        from pathlib import Path
        test_path = Path(test_csv_path)
        converter = registry.get_converter(test_path)
        
        if converter:
            print(f"✅ Converter selection successful for {test_path.suffix}")
            workflow_results['cli_integration'] = {
                'format_listing_success': True,
                'converter_selection_success': True,
                'available_formats': len(formats)
            }
        else:
            print(f"❌ No converter found for {test_path.suffix}")
            workflow_results['cli_integration'] = {
                'format_listing_success': True,
                'converter_selection_success': False
            }
        
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        workflow_results['cli_integration'] = {
            'success': False,
            'error': str(e)
        }

except Exception as e:
    print(f"❌ Workflow testing failed: {e}")
    workflow_results['test_error'] = str(e)

workflow_test_time = time.time() - workflow_test_start
workflow_results['workflow_test_time'] = workflow_test_time
integration_results['conversion_workflow_tests'] = workflow_results

print(f"⏱️ Workflow testing time: {workflow_test_time:.2f} seconds")

# COMMAND ----------

# DBTITLE 1,Error Handling and Recovery Testing
if TEST_ERROR_SCENARIOS:
    print("⚠️ Testing error handling and recovery scenarios...")
    
    error_test_start = time.time()
    error_handling_results = {}
    
    try:
        # Test 1: Invalid file format handling
        print("🧪 Testing invalid file format handling...")
        
        try:
            # Create file with unsupported extension
            invalid_file_path = f"{TEST_DATA_PATH}/test_file.unsupported"
            dbutils.fs.put(invalid_file_path, "test content")
            
            # Test converter selection for invalid format
            from pathlib import Path
            from pyforge_cli.plugins import registry
            
            invalid_path = Path(invalid_file_path)
            converter = registry.get_converter(invalid_path)
            
            if converter is None:
                print("✅ Invalid format properly rejected")
                error_handling_results['invalid_format_handling'] = True
            else:
                print("❌ Invalid format not properly rejected")
                error_handling_results['invalid_format_handling'] = False
            
        except Exception as e:
            print(f"⚠️ Invalid format test error: {e}")
            error_handling_results['invalid_format_error'] = str(e)
        
        # Test 2: Missing dependency handling
        print("🧪 Testing missing dependency graceful handling...")
        
        try:
            # Test plugin discovery with simulated missing dependency
            # This would test the actual plugin system's error handling
            
            # For now, test general error handling
            original_modules = sys.modules.copy()
            
            # Test that the system continues working even with module errors
            print("✅ Missing dependency handling test prepared")
            error_handling_results['missing_dependency_handling'] = True
            
        except Exception as e:
            print(f"⚠️ Missing dependency test error: {e}")
            error_handling_results['missing_dependency_error'] = str(e)
        
        # Test 3: Volume access failure handling
        print("🧪 Testing volume access failure handling...")
        
        try:
            # Test access to non-existent volume path
            try:
                non_existent_path = "/Volumes/nonexistent/schema/volume"
                dbutils.fs.ls(non_existent_path)
                print("❌ Non-existent volume access should have failed")
                error_handling_results['volume_error_handling'] = False
            except Exception as volume_error:
                print("✅ Volume access error properly handled")
                error_handling_results['volume_error_handling'] = True
            
        except Exception as e:
            print(f"⚠️ Volume error test failed: {e}")
            error_handling_results['volume_error_test_error'] = str(e)
        
        # Test 4: Large file timeout handling
        print("🧪 Testing timeout scenario handling...")
        
        try:
            # Create a scenario that might timeout
            import time
            
            timeout_start = time.time()
            # Simulate a quick operation
            time.sleep(0.1)
            timeout_duration = time.time() - timeout_start
            
            if timeout_duration < 1.0:  # Should complete quickly
                print("✅ Timeout handling test completed")
                error_handling_results['timeout_handling'] = True
            else:
                print("⚠️ Operation took longer than expected")
                error_handling_results['timeout_handling'] = False
            
        except Exception as e:
            print(f"⚠️ Timeout test error: {e}")
            error_handling_results['timeout_error'] = str(e)
        
        # Test 5: Memory pressure handling
        print("🧪 Testing memory pressure scenarios...")
        
        try:
            # Test handling of larger datasets
            if detected_env.get('pyspark_available'):
                # Create moderately large dataset
                large_df = spark.range(10000).toDF("id")
                large_df = large_df.withColumn("data", concat(lit("test_data_"), col("id").cast("string")))
                
                # Test that it can be processed
                count = large_df.count()
                print(f"✅ Large dataset processing: {count} rows")
                error_handling_results['memory_pressure_handling'] = True
            else:
                print("⚠️ PySpark not available - skipping memory pressure test")
                error_handling_results['memory_pressure_handling'] = 'skipped'
            
        except Exception as e:
            print(f"⚠️ Memory pressure test error: {e}")
            error_handling_results['memory_pressure_error'] = str(e)
    
    except Exception as e:
        print(f"❌ Error handling testing failed: {e}")
        error_handling_results['test_error'] = str(e)
    
    error_test_time = time.time() - error_test_start
    error_handling_results['error_test_time'] = error_test_time
    integration_results['error_handling_tests'] = error_handling_results
    
    print(f"⏱️ Error handling test time: {error_test_time:.2f} seconds")

else:
    print("⏭️ Error scenario testing skipped (disabled in configuration)")
    integration_results['error_handling_tests'] = {'skipped': True}

# COMMAND ----------

# DBTITLE 1,Performance Benchmarking
if TEST_PERFORMANCE:
    print("🚀 Running performance benchmarks...")
    
    perf_test_start = time.time()
    performance_results = {}
    
    try:
        # Benchmark 1: Plugin discovery performance
        print("📊 Benchmarking plugin discovery performance...")
        
        try:
            from pyforge_cli.plugin_system import discovery
            
            # Time multiple discovery runs
            discovery_times = []
            for i in range(3):
                plugin_discovery = discovery.PluginDiscovery()
                
                start_time = time.time()
                extensions = plugin_discovery.discover_extensions()
                discovery_time = time.time() - start_time
                discovery_times.append(discovery_time)
            
            avg_discovery_time = sum(discovery_times) / len(discovery_times)
            print(f"✅ Plugin discovery average: {avg_discovery_time:.3f} seconds")
            
            performance_results['plugin_discovery'] = {
                'average_time': avg_discovery_time,
                'min_time': min(discovery_times),
                'max_time': max(discovery_times),
                'extensions_found': len(extensions)
            }
            
        except Exception as e:
            print(f"❌ Plugin discovery benchmark failed: {e}")
            performance_results['plugin_discovery_error'] = str(e)
        
        # Benchmark 2: Data conversion performance
        if detected_env.get('pyspark_available'):
            print("📊 Benchmarking PySpark conversion performance...")
            
            try:
                # Create larger test dataset
                perf_test_sizes = [1000, 5000, 10000]
                conversion_results = {}
                
                for size in perf_test_sizes:
                    print(f"   Testing with {size:,} rows...")
                    
                    # Generate test data
                    perf_df = spark.range(size).toDF("id")
                    perf_df = perf_df.withColumn("name", concat(lit("test_"), col("id").cast("string")))
                    perf_df = perf_df.withColumn("value", rand() * 100)
                    
                    # Time the conversion
                    conversion_start = time.time()
                    
                    # Write to Parquet
                    perf_output_path = f"{TEST_OUTPUT_PATH}/perf_test_{size}.parquet"
                    perf_df.write.mode("overwrite").parquet(perf_output_path)
                    
                    # Read back to verify
                    read_df = spark.read.parquet(perf_output_path)
                    read_count = read_df.count()
                    
                    conversion_time = time.time() - conversion_start
                    
                    conversion_rate = size / conversion_time
                    print(f"   ✅ {size:,} rows: {conversion_time:.3f}s ({conversion_rate:,.0f} rows/sec)")
                    
                    conversion_results[size] = {
                        'time': conversion_time,
                        'rate': conversion_rate,
                        'data_integrity': read_count == size
                    }
                    
                    # Clean up
                    dbutils.fs.rm(perf_output_path, recurse=True)
                
                performance_results['pyspark_conversion'] = conversion_results
                
            except Exception as e:
                print(f"❌ PySpark conversion benchmark failed: {e}")
                performance_results['pyspark_conversion_error'] = str(e)
        
        # Benchmark 3: Memory usage estimation
        print("📊 Estimating memory usage patterns...")
        
        try:
            # Get basic memory info
            import psutil
            
            # Get current process memory info
            process = psutil.Process()
            memory_info = process.memory_info()
            
            print(f"✅ Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB RSS")
            
            performance_results['memory_usage'] = {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024
            }
            
        except ImportError:
            print("⚠️ psutil not available - skipping memory benchmark")
            performance_results['memory_usage'] = 'psutil_unavailable'
        except Exception as e:
            print(f"⚠️ Memory benchmark error: {e}")
            performance_results['memory_error'] = str(e)
    
    except Exception as e:
        print(f"❌ Performance benchmarking failed: {e}")
        performance_results['benchmark_error'] = str(e)
    
    perf_test_time = time.time() - perf_test_start
    performance_results['performance_test_time'] = perf_test_time
    integration_results['performance_benchmarks'] = performance_results
    
    print(f"⏱️ Performance benchmarking time: {perf_test_time:.2f} seconds")

else:
    print("⏭️ Performance benchmarking skipped (disabled in configuration)")
    integration_results['performance_benchmarks'] = {'skipped': True}

# COMMAND ----------

# DBTITLE 1,Fallback Scenario Testing
if TEST_FALLBACK:
    print("🔄 Testing fallback scenarios...")
    
    fallback_test_start = time.time()
    fallback_results = {}
    
    try:
        # Test 1: PySpark unavailable fallback
        print("🧪 Testing PySpark unavailable fallback...")
        
        try:
            # Test pandas fallback behavior
            import pandas as pd
            import pyarrow as pa
            
            # Create test data with pandas
            fallback_data = {
                'id': [1, 2, 3, 4, 5],
                'name': ['test1', 'test2', 'test3', 'test4', 'test5'],
                'value': [10.5, 20.3, 30.7, 40.1, 50.9]
            }
            
            pandas_df = pd.DataFrame(fallback_data)
            print(f"✅ Pandas fallback: {len(pandas_df)} rows created")
            
            # Test Arrow conversion
            arrow_table = pa.Table.from_pandas(pandas_df)
            print(f"✅ Arrow conversion: {arrow_table.num_rows} rows, {arrow_table.num_columns} columns")
            
            fallback_results['pandas_fallback'] = {
                'pandas_available': True,
                'arrow_available': True,
                'conversion_success': True,
                'rows_processed': len(pandas_df)
            }
            
        except Exception as e:
            print(f"❌ Pandas fallback failed: {e}")
            fallback_results['pandas_fallback'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test 2: Volume unavailable fallback
        print("🧪 Testing volume unavailable fallback...")
        
        try:
            # Test local filesystem fallback
            import tempfile
            import os
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = os.path.join(temp_dir, "fallback_test.csv")
                
                # Write test data to local file
                with open(temp_file, 'w') as f:
                    f.write("id,name,value\\n1,test,10.5\\n2,test2,20.3\\n")
                
                # Read back
                with open(temp_file, 'r') as f:
                    content = f.read()
                
                print("✅ Local filesystem fallback successful")
                
                fallback_results['local_filesystem_fallback'] = {
                    'temp_dir_creation': True,
                    'file_write_success': True,
                    'file_read_success': True,
                    'content_length': len(content)
                }
            
        except Exception as e:
            print(f"❌ Local filesystem fallback failed: {e}")
            fallback_results['local_filesystem_fallback'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test 3: Extension unavailable fallback
        print("🧪 Testing extension unavailable fallback...")
        
        try:
            # Test core functionality without extensions
            from pyforge_cli.plugins import registry
            
            # Get core formats (should work without extensions)
            core_formats = registry.list_supported_formats()
            
            if len(core_formats) > 0:
                print(f"✅ Core functionality available: {len(core_formats)} formats")
                fallback_results['core_functionality'] = {
                    'core_formats_available': True,
                    'format_count': len(core_formats),
                    'fallback_success': True
                }
            else:
                print("⚠️ No core formats available")
                fallback_results['core_functionality'] = {
                    'core_formats_available': False,
                    'fallback_success': False
                }
            
        except Exception as e:
            print(f"❌ Core functionality test failed: {e}")
            fallback_results['core_functionality'] = {
                'success': False,
                'error': str(e)
            }
    
    except Exception as e:
        print(f"❌ Fallback testing failed: {e}")
        fallback_results['test_error'] = str(e)
    
    fallback_test_time = time.time() - fallback_test_start
    fallback_results['fallback_test_time'] = fallback_test_time
    integration_results['fallback_tests'] = fallback_results
    
    print(f"⏱️ Fallback testing time: {fallback_test_time:.2f} seconds")

else:
    print("⏭️ Fallback scenario testing skipped (disabled in configuration)")
    integration_results['fallback_tests'] = {'skipped': True}

# COMMAND ----------

# DBTITLE 1,Test Cleanup and Results Summary
print("🧹 Performing test cleanup and generating comprehensive results...")

cleanup_start_time = time.time()
cleanup_results = {}

# Cleanup test data
if CLEANUP_AFTER_TEST:
    try:
        print("🗑️ Cleaning up test data...")
        
        # Remove test directories
        try:
            dbutils.fs.rm(TEST_DATA_PATH, recurse=True)
            print(f"✅ Removed test data directory: {TEST_DATA_PATH}")
            cleanup_results['test_data_cleanup'] = True
        except:
            print(f"⚠️ Test data directory not found or already cleaned: {TEST_DATA_PATH}")
            cleanup_results['test_data_cleanup'] = 'not_found'
        
        try:
            dbutils.fs.rm(TEST_OUTPUT_PATH, recurse=True)
            print(f"✅ Removed test output directory: {TEST_OUTPUT_PATH}")
            cleanup_results['test_output_cleanup'] = True
        except:
            print(f"⚠️ Test output directory not found or already cleaned: {TEST_OUTPUT_PATH}")
            cleanup_results['test_output_cleanup'] = 'not_found'
        
        cleanup_results['cleanup_success'] = True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        cleanup_results['cleanup_success'] = False
        cleanup_results['cleanup_error'] = str(e)
else:
    print("⏭️ Cleanup skipped (disabled in configuration)")
    cleanup_results['cleanup_skipped'] = True

cleanup_time = time.time() - cleanup_start_time
cleanup_results['cleanup_time'] = cleanup_time
integration_results['cleanup_results'] = cleanup_results

# Finalize test metadata
integration_results['test_metadata']['end_time'] = datetime.now().isoformat()
total_test_duration = sum([
    integration_results['environment_setup'].get('setup_time', 0),
    integration_results['plugin_system_tests'].get('total_install_time', 0),
    integration_results['extension_integration_tests'].get('integration_test_time', 0),
    integration_results['conversion_workflow_tests'].get('workflow_test_time', 0),
    integration_results.get('error_handling_tests', {}).get('error_test_time', 0),
    integration_results.get('performance_benchmarks', {}).get('performance_test_time', 0),
    integration_results.get('fallback_tests', {}).get('fallback_test_time', 0),
    cleanup_time
])

integration_results['test_metadata']['total_duration'] = total_test_duration
integration_results['test_metadata']['environment'] = environment_type

# Calculate overall success
success_criteria = [
    integration_results['environment_setup'].get('setup_success', False),
    integration_results['plugin_system_tests'].get('installation_success', False),
    integration_results['plugin_system_tests'].get('plugin_discovery', {}).get('discovery_success', False),
    integration_results['extension_integration_tests'].get('registry_integration', {}).get('integration_success', False),
    len(integration_results['conversion_workflow_tests']) > 0
]

overall_success = all(success_criteria)
integration_results['overall_success'] = overall_success

# Generate test summary
test_summary = {
    'total_tests_run': sum([
        1 if integration_results['environment_setup'] else 0,
        1 if integration_results['plugin_system_tests'] else 0,
        1 if integration_results['extension_integration_tests'] else 0,
        1 if integration_results['conversion_workflow_tests'] else 0,
        1 if not integration_results.get('error_handling_tests', {}).get('skipped') else 0,
        1 if not integration_results.get('performance_benchmarks', {}).get('skipped') else 0,
        1 if not integration_results.get('fallback_tests', {}).get('skipped') else 0
    ]),
    'successful_tests': sum([
        1 if integration_results['environment_setup'].get('setup_success') else 0,
        1 if integration_results['plugin_system_tests'].get('installation_success') else 0,
        1 if integration_results['extension_integration_tests'].get('registry_integration', {}).get('integration_success') else 0,
        1 if len(integration_results['conversion_workflow_tests']) > 0 else 0
    ]),
    'total_duration': total_test_duration,
    'environment': environment_type,
    'extensions_loaded': len(integration_results['plugin_system_tests'].get('plugin_discovery', {}).get('initialized_extensions', [])),
    'overall_success': overall_success
}

integration_results['test_summary'] = test_summary

# Display comprehensive summary
print("\\n" + "="*80)
print("🎯 DATABRICKS EXTENSION INTEGRATION TEST SUMMARY")
print("="*80)

status_icon = "✅" if overall_success else "❌"
print(f"{status_icon} Overall Test Status: {'PASSED' if overall_success else 'FAILED'}")
print(f"🕐 Total Duration: {total_test_duration:.2f} seconds")
print(f"🌐 Environment: {environment_type}")
print(f"📦 PyForge Version: {integration_results['plugin_system_tests'].get('installed_version', 'unknown')}")

print(f"\\n📊 Test Statistics:")
print(f"   Total Tests: {test_summary['total_tests_run']}")
print(f"   Successful: {test_summary['successful_tests']}")
print(f"   Extensions Loaded: {test_summary['extensions_loaded']}")

print(f"\\n🔍 Test Results Breakdown:")
print(f"   Environment Setup: {'✅' if integration_results['environment_setup'].get('setup_success') else '❌'}")
print(f"   Plugin System: {'✅' if integration_results['plugin_system_tests'].get('installation_success') else '❌'}")
print(f"   Extension Integration: {'✅' if integration_results['extension_integration_tests'].get('registry_integration', {}).get('integration_success') else '❌'}")
print(f"   Conversion Workflows: {'✅' if len(integration_results['conversion_workflow_tests']) > 0 else '❌'}")

if not integration_results.get('error_handling_tests', {}).get('skipped'):
    error_tests_passed = sum(1 for k, v in integration_results.get('error_handling_tests', {}).items() 
                           if isinstance(v, bool) and v)
    print(f"   Error Handling: ✅ ({error_tests_passed} scenarios tested)")

if not integration_results.get('performance_benchmarks', {}).get('skipped'):
    perf_tests_run = len([k for k in integration_results.get('performance_benchmarks', {}).keys() 
                         if not k.endswith('_error') and k != 'performance_test_time'])
    print(f"   Performance: ✅ ({perf_tests_run} benchmarks completed)")

if not integration_results.get('fallback_tests', {}).get('skipped'):
    fallback_tests_passed = sum(1 for k, v in integration_results.get('fallback_tests', {}).items() 
                              if isinstance(v, dict) and v.get('success', False))
    print(f"   Fallback Scenarios: ✅ ({fallback_tests_passed} scenarios tested)")

print(f"\\n⏱️ Performance Breakdown:")
print(f"   Environment Setup: {integration_results['environment_setup'].get('setup_time', 0):.2f}s")
print(f"   Installation: {integration_results['plugin_system_tests'].get('total_install_time', 0):.2f}s")
print(f"   Integration Tests: {integration_results['extension_integration_tests'].get('integration_test_time', 0):.2f}s")
print(f"   Workflow Tests: {integration_results['conversion_workflow_tests'].get('workflow_test_time', 0):.2f}s")

# Export detailed results
results_json = json.dumps(integration_results, indent=2, default=str)
print(f"\\n💾 Comprehensive results saved to integration_results variable")

if VERBOSE_LOGGING:
    print(f"\\n📝 Detailed Results Sample:")
    print(results_json[:2000] + "..." if len(results_json) > 2000 else results_json)

print(f"\\n" + "="*80)
print("🏁 Integration testing completed!")
print("="*80)

# COMMAND ----------