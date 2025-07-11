# Databricks notebook source
# MAGIC %md
# MAGIC # Debug MDB Subprocess Backend in Databricks Serverless
# MAGIC 
# MAGIC This notebook helps debug why the subprocess backend is not being detected as available.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Check Environment Variables

# COMMAND ----------

import os
import sys

print("=" * 80)
print("ENVIRONMENT VARIABLES")
print("=" * 80)

# Key Databricks Serverless indicators
env_vars = [
    'IS_SERVERLESS',
    'SPARK_CONNECT_MODE_ENABLED',
    'DB_INSTANCE_TYPE',
    'POD_NAME',
    'DATABRICKS_RUNTIME_VERSION',
    'JAVA_HOME',
    'PATH'
]

for var in env_vars:
    value = os.environ.get(var, 'NOT SET')
    print(f"{var}: {value}")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Check Java Availability

# COMMAND ----------

import subprocess

print("=" * 80)
print("JAVA AVAILABILITY CHECK")
print("=" * 80)

# Check if java command is available
try:
    result = subprocess.run(['which', 'java'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Java found at: {result.stdout.strip()}")
    else:
        print("Java not found in PATH")
except Exception as e:
    print(f"Error checking java: {e}")

# Try different java locations
java_locations = [
    'java',
    '/usr/bin/java',
    '/usr/lib/jvm/java-8-openjdk-amd64/bin/java',
    '/usr/lib/jvm/java-11-openjdk-amd64/bin/java',
    '/databricks/jdk/bin/java'
]

print("\nChecking specific Java locations:")
for java_path in java_locations:
    try:
        if java_path == 'java':
            result = subprocess.run([java_path, '-version'], capture_output=True, text=True, timeout=5)
        else:
            if os.path.exists(java_path):
                result = subprocess.run([java_path, '-version'], capture_output=True, text=True, timeout=5)
            else:
                print(f"  {java_path}: Does not exist")
                continue
        
        if result.returncode == 0:
            version = result.stderr if result.stderr else result.stdout
            print(f"  {java_path}: WORKS - {version.split()[0] if version else 'Unknown version'}")
        else:
            print(f"  {java_path}: Failed with code {result.returncode}")
    except Exception as e:
        print(f"  {java_path}: Error - {e}")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Test Backend Detection Logic

# COMMAND ----------

# Test the backend detection with detailed logging
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("=" * 80)
print("TESTING BACKEND DETECTION")
print("=" * 80)

# Import backends
try:
    from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend
    from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend
    from pyforge_cli.backends.pyodbc_backend import PyODBCBackend
    
    print("\n1. Testing UCanAccess Backend (JPype):")
    backend1 = UCanAccessBackend()
    available1 = backend1.is_available()
    print(f"   Available: {available1}")
    
    print("\n2. Testing UCanAccess Subprocess Backend:")
    backend2 = UCanAccessSubprocessBackend()
    available2 = backend2.is_available()
    print(f"   Available: {available2}")
    
    print("\n3. Testing PyODBC Backend:")
    backend3 = PyODBCBackend()
    available3 = backend3.is_available()
    print(f"   Available: {available3}")
    
    print(f"\nSummary: {sum([available1, available2, available3])} backends available")
    
except Exception as e:
    print(f"Error importing backends: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Test JAR File Detection

# COMMAND ----------

from pathlib import Path

print("=" * 80)
print("JAR FILE DETECTION")
print("=" * 80)

# Check for JAR files in various locations
try:
    import pyforge_cli
    package_dir = Path(pyforge_cli.__file__).parent
    
    jar_locations = [
        package_dir / 'data' / 'jars',
        package_dir / 'backends' / 'jars',
        Path('/local_disk0/tmp/') / 'pyforge_jars',
        Path('/databricks/jars'),
        Path.home() / '.pyforge' / 'jars',
    ]
    
    print("Checking for UCanAccess JAR files:")
    for location in jar_locations:
        if location.exists():
            jar_files = list(location.glob('*.jar'))
            if jar_files:
                print(f"\n{location}:")
                for jar in jar_files[:5]:  # Show first 5 JARs
                    print(f"  - {jar.name}")
            else:
                print(f"\n{location}: No JAR files found")
        else:
            print(f"\n{location}: Directory does not exist")
            
except Exception as e:
    print(f"Error checking JAR locations: {e}")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Direct Subprocess Backend Test

# COMMAND ----------

# Test the subprocess backend directly with manual environment override
print("=" * 80)
print("DIRECT SUBPROCESS BACKEND TEST")
print("=" * 80)

try:
    # Temporarily set environment variable to force Databricks Serverless detection
    original_is_serverless = os.environ.get('IS_SERVERLESS')
    os.environ['IS_SERVERLESS'] = 'TRUE'
    
    from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend
    
    backend = UCanAccessSubprocessBackend()
    print(f"Is Databricks Serverless: {backend._is_databricks_serverless()}")
    print(f"Is Available: {backend.is_available()}")
    
    # Test connection if available
    if backend.is_available():
        test_file = "/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/access_sakila.mdb"
        if os.path.exists(test_file):
            print(f"\nTesting connection to: {test_file}")
            if backend.connect(test_file):
                print("✓ Connection successful")
                tables = backend.list_tables()
                print(f"✓ Found {len(tables)} tables")
                backend.close()
            else:
                print("✗ Connection failed")
        else:
            print(f"\nTest file not found: {test_file}")
    
    # Restore original environment
    if original_is_serverless is None:
        del os.environ['IS_SERVERLESS']
    else:
        os.environ['IS_SERVERLESS'] = original_is_serverless
        
except Exception as e:
    print(f"Error in direct test: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC This notebook helps identify why the subprocess backend might not be detected as available in Databricks Serverless.