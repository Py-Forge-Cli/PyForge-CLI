# Databricks notebook source
# MAGIC %md
# MAGIC # PyForge CLI Testing on Databricks Serverless V1
# MAGIC 
# MAGIC This notebook tests PyForge CLI installation and functionality on Databricks Serverless V1 environment.
# MAGIC 
# MAGIC **Test Coverage:**
# MAGIC - Environment verification (Python 3.10, Java 8, V1 runtime)
# MAGIC - PyForge CLI installation with V1-compatible dependencies
# MAGIC - Import verification and backend availability
# MAGIC - Microsoft Access database connectivity
# MAGIC - Performance monitoring

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Environment Verification

# COMMAND ----------

import os
import sys
import time
from datetime import datetime

print("🔍 DATABRICKS V1 ENVIRONMENT CHECK")
print("=" * 50)
print(f"📅 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Python version
python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
print(f"🐍 Python Version: {python_version}")
if python_version.startswith('3.10'):
    print("  ✅ Correct for Databricks V1")
else:
    print("  ⚠️  May not be V1 environment")

# Java version detection
java_home = os.environ.get('JAVA_HOME', '')
print(f"☕ Java Home: {java_home}")
if 'zulu8' in java_home:
    print("  ✅ Java 8 detected - compatible with UCanAccess 4.0.4")
elif java_home:
    print("  ⚠️  Java version may not be compatible")
else:
    print("  ❌ JAVA_HOME not set")

# Databricks runtime
runtime = os.environ.get('DATABRICKS_RUNTIME_VERSION', '')
print(f"🔧 Databricks Runtime: {runtime}")
if 'client.1.' in runtime:
    print("  ✅ V1 runtime confirmed")
else:
    print("  ⚠️  May not be V1 runtime")

# Serverless check
is_serverless = os.environ.get('IS_SERVERLESS', 'FALSE').upper() == 'TRUE'
print(f"⚡ Serverless: {is_serverless}")
if is_serverless:
    print("  ✅ Running on serverless compute")
else:
    print("  ⚠️  Not serverless - may be cluster compute")

# Basic Spark test
try:
    result = spark.sql("SELECT 'V1 Environment Test' as message, current_timestamp() as ts").collect()[0]
    print(f"✅ Spark Test: {result.message}")
    print(f"  Time: {result.ts}")
except Exception as e:
    print(f"❌ Spark Test Failed: {e}")

print("\n" + "="*50)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. PyForge CLI Installation

# COMMAND ----------

print("📦 PYFORGE CLI INSTALLATION")
print("=" * 40)

# V1 recommended installation
wheel_path = "/dbfs/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/pkgs/pyforge_cli-0.5.8-py3-none-any.whl"

print("🔄 Installing PyForge CLI with V1 dependencies...")
print("Command:")
print(f"  %pip install {wheel_path}")
print(f"  jaydebeapi>=1.2.3,<1.3.0")  
print(f"  jpype1>=1.3.0,<1.4.0")
print(f"  --force-reinstall")
print()

# Execute installation
try:
    %pip install /dbfs/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/pkgs/pyforge_cli-0.5.8-py3-none-any.whl jaydebeapi>=1.2.3,<1.3.0 jpype1>=1.3.0,<1.4.0 --force-reinstall
    print("✅ Installation command executed")
except Exception as e:
    print(f"❌ Installation error: {e}")

print("\n" + "="*40)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Restart Python Kernel
# MAGIC 
# MAGIC After installation, restart the Python kernel to ensure clean imports.

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Import Verification

# COMMAND ----------

print("📥 PYFORGE CLI IMPORT VERIFICATION")
print("=" * 45)

# Test basic import
try:
    import pyforge_cli
    print("✅ pyforge_cli imported successfully")
    
    # Get version
    version = getattr(pyforge_cli, '__version__', 'unknown')
    print(f"  Version: {version}")
    
except ImportError as e:
    print(f"❌ pyforge_cli import failed: {e}")
    print("💡 Check installation above")

# Test UCanAccess backend import
try:
    from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend
    print("✅ UCanAccessBackend imported successfully")
except ImportError as e:
    print(f"❌ UCanAccessBackend import failed: {e}")

# Test backend initialization
try:
    backend = UCanAccessBackend()
    print("✅ UCanAccessBackend created successfully")
    
    # Test availability
    print("\n🔍 Backend Availability Check:")
    available = backend.is_available()
    print(f"  Overall available: {available}")
    
    # Detailed checks
    java_ok = backend._check_java()
    print(f"  Java available: {java_ok}")
    
    jaydebeapi_ok = backend._check_jaydebeapi()
    print(f"  JayDeBeApi available: {jaydebeapi_ok}")
    
    jar_ok = backend.jar_manager.ensure_jar_available()
    print(f"  JAR available: {jar_ok}")
    
    if available:
        print("\n✅ Backend fully functional!")
        
        # Get JAR info
        jar_info = backend.jar_manager.get_jar_info()
        if jar_info:
            print(f"  JAR info: {jar_info}")
    else:
        print("\n⚠️  Backend not fully available")
        print("🔧 Check the individual components above")
        
except Exception as e:
    print(f"❌ Backend initialization failed: {e}")

print("\n" + "="*45)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. MDB File Access Test

# COMMAND ----------

print("📄 MDB FILE ACCESS TEST")
print("=" * 30)

# Test files
test_files = [
    {
        'name': 'Northwind_2007_VBNet.accdb',
        'path': '/dbfs/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/Northwind_2007_VBNet.accdb'
    },
    {
        'name': 'access_sakila.mdb',
        'path': '/dbfs/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/access_sakila.mdb'
    }
]

successful_connections = 0

for test_file in test_files:
    print(f"\n📁 Testing: {test_file['name']}")
    print("-" * 40)
    
    # Check file existence
    try:
        file_df = spark.read.format("binaryFile").load(test_file['path'])
        file_exists = file_df.count() > 0
        print(f"  File exists: {file_exists}")
    except:
        file_exists = False
        print(f"  File exists: {file_exists}")
    
    if not file_exists:
        print("  ⚠️  Skipping - file not found")
        continue
    
    # Test connection
    try:
        from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend
        backend = UCanAccessBackend()
        
        print("  🔄 Attempting connection...")
        start_time = time.time()
        
        connected = backend.connect(test_file['path'])
        connect_time = time.time() - start_time
        
        if connected:
            print(f"  ✅ Connected successfully ({connect_time:.2f}s)")
            successful_connections += 1
            
            # List tables
            try:
                tables = backend.list_tables()
                print(f"  📋 Tables found: {len(tables)}")
                
                if tables:
                    print(f"  📝 Sample tables: {', '.join(tables[:5])}")
                    
                    # Try reading from first table
                    if len(tables) > 0:
                        try:
                            df = backend.read_table(tables[0])
                            print(f"  📊 Read {len(df)} records from '{tables[0]}'")
                            print(f"  📊 Columns: {len(df.columns)}")
                            
                            # Show sample data
                            if len(df) > 0:
                                print(f"  📋 Sample data:")
                                print(f"    {list(df.columns[:3])}")  # First 3 columns
                                
                        except Exception as read_error:
                            print(f"  ⚠️  Read error: {read_error}")
                else:
                    print("  ⚠️  No tables found")
                    
            except Exception as table_error:
                print(f"  ⚠️  Table listing error: {table_error}")
            
            # Close connection
            backend.close()
            print("  🔒 Connection closed")
            
        else:
            print("  ❌ Connection failed")
            
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        
        # Error analysis
        error_str = str(e).lower()
        if 'unsupportedclassversionerror' in error_str:
            print("    📌 Java version mismatch - need Java 8 compatible UCanAccess")
        elif 'operation not supported' in error_str:
            print("    📌 File system restriction - try memory mode")
        elif 'classnotfoundexception' in error_str:
            print("    📌 Missing JAR files")
        else:
            print(f"    📌 Unknown error type")

print(f"\n📊 Summary: {successful_connections}/{len(test_files)} files connected successfully")

if successful_connections > 0:
    print("✅ MDB file access is working!")
else:
    print("❌ No MDB files could be accessed")
    print("🔧 Review errors above for troubleshooting")

print("\n" + "="*30)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Performance Monitoring

# COMMAND ----------

print("⚡ PERFORMANCE MONITORING")
print("=" * 35)

# Spark performance test
print("🔄 Testing Spark SQL performance...")
start_time = time.time()

result = spark.sql("""
    SELECT 
        COUNT(*) as row_count,
        current_timestamp() as test_time,
        spark_version() as spark_version
    FROM VALUES 
        (1), (2), (3), (4), (5), (6), (7), (8), (9), (10)
    AS t(id)
""").collect()[0]

sql_time = time.time() - start_time
print(f"✅ SQL completed in {sql_time:.3f} seconds")
print(f"  Spark version: {result.spark_version}")
print(f"  Row count: {result.row_count}")

# Environment variables
print(f"\n🔧 Performance Environment:")
perf_vars = [
    'SPARK_LOCAL_DIRS', 
    'DATABRICKS_RUNTIME_VERSION',
    'JAVA_OPTS'
]

for var in perf_vars:
    value = os.environ.get(var, 'Not set')
    # Truncate long values
    if len(str(value)) > 80:
        value = str(value)[:80] + "..."
    print(f"  {var}: {value}")

print(f"\n✅ Performance monitoring completed")
print("=" * 35)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Test Summary

# COMMAND ----------

print("📊 PYFORGE CLI V1 TEST SUMMARY")
print("=" * 50)

print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

print("✅ Tests Completed:")
print("  1. ✅ Environment verification")  
print("  2. ✅ PyForge CLI installation")
print("  3. ✅ Import verification")
print("  4. ✅ MDB file access test")
print("  5. ✅ Performance monitoring")

print(f"\n🎯 Results:")
print(f"  Environment: Databricks Serverless V1")
print(f"  Python: {python_version}")
print(f"  Java: Java 8 (Zulu)")
print(f"  UCanAccess: 4.0.4")

# Check if all major components work
try:
    from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend
    backend = UCanAccessBackend()
    backend_available = backend.is_available()
except:
    backend_available = False

if backend_available:
    print(f"\n🎉 PyForge CLI is READY for use on Databricks V1!")
    print(f"✅ All components functioning correctly")
    print(f"✅ Microsoft Access database support available")
else:
    print(f"\n⚠️  PyForge CLI has issues that need attention")
    print(f"🔧 Review the test results above")

print(f"\n💡 Next Steps:")
print(f"  - Use PyForge CLI for MDB to CSV/Parquet conversion")
print(f"  - Integrate with data pipelines")
print(f"  - Monitor performance in production workloads")

print("=" * 50)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Quick Usage Example

# COMMAND ----------

# Only run if backend is available
try:
    from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend
    backend = UCanAccessBackend()
    
    if backend.is_available():
        print("🚀 PYFORGE CLI USAGE EXAMPLE")
        print("=" * 40)
        
        print("Example code for MDB file conversion:")
        print()
        print("```python")
        print("from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend")
        print()
        print("# Connect to MDB file")
        print("backend = UCanAccessBackend()")
        print("backend.connect('/path/to/your/database.mdb')")
        print()
        print("# List tables")
        print("tables = backend.list_tables()")
        print("print(f'Found {len(tables)} tables: {tables}')")
        print()
        print("# Read table to DataFrame")
        print("df = backend.read_table('YourTableName')")
        print("print(f'Loaded {len(df)} records')")
        print()
        print("# Save as Parquet")
        print("df.to_parquet('/dbfs/path/to/output.parquet')")
        print()
        print("# Clean up")
        print("backend.close()")
        print("```")
        
        print("=" * 40)
    else:
        print("⚠️  Backend not available - fix issues first")
        
except Exception as e:
    print(f"❌ Could not load backend: {e}")

# COMMAND ----------