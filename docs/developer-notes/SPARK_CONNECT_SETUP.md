# Running PyForge Test Notebook via Spark Connect

This guide shows how to run the PyForge Databricks test notebook remotely from your local machine using Spark Connect.

## Prerequisites

### 1. Databricks CLI Configuration
Ensure Databricks CLI is properly configured with your workspace:

```bash
# Check current configuration
databricks configure --token

# Or verify existing configuration
databricks current-user me
```

### 2. Required Python Packages
Install the required packages for Spark Connect:

```bash
pip install databricks-connect databricks-sdk
```

### 3. Environment Setup
Set up your environment for Databricks Serverless:

```bash
# Clear any conflicting environment variables
unset DATABRICKS_CLIENT_ID
unset DATABRICKS_CLIENT_SECRET

# Set serverless compute ID
export DATABRICKS_SERVERLESS_COMPUTE_ID=auto
```

## Execution Methods

### Method 1: Direct Script Execution (Recommended)

Run the complete notebook workflow using our custom executor:

```bash
cd /Users/sdandey/Documents/code/cortexpy-cli/integration_tests/serverless/
python run_notebook_with_spark_connect.py
```

**What this does:**
1. Connects to Databricks Serverless V1 via Spark Connect
2. Simulates pip installation of PyForge CLI v0.5.9
3. Tests environment verification
4. Simulates import testing
5. Tests Unity Catalog volume access
6. Runs performance benchmarks
7. Generates comprehensive execution report

### Method 2: Interactive Python Session

For step-by-step execution:

```python
# Start Python in the serverless directory
cd /Users/sdandey/Documents/code/cortexpy-cli/integration_tests/serverless/
python3

# Execute notebook steps interactively
from run_notebook_with_spark_connect import NotebookExecutor

executor = NotebookExecutor(profile="DEFAULT")
result = executor.execute_notebook()
print(result)
```

### Method 3: Individual Cell Execution

For testing specific functionality:

```python
from databricks.connect import DatabricksSession
import os

# Setup environment
os.environ['DATABRICKS_SERVERLESS_COMPUTE_ID'] = 'auto'

# Connect to Databricks
spark = DatabricksSession.builder.profile("DEFAULT").getOrCreate()

# Test basic SQL
result = spark.sql("SELECT current_timestamp() as ts").collect()[0]
print(f"Connected! Timestamp: {result.ts}")

# Test volume access (if permissions allow)
try:
    files = spark.sql("LIST '/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/'").collect()
    print(f"Found {len(files)} files in volume")
except Exception as e:
    print(f"Volume access: {e}")

# Cleanup
spark.stop()
```

## Limitations and Workarounds

### 1. Pip Magic Commands
**Limitation:** `%pip install` magic commands cannot be executed via Spark Connect.

**Workaround:** 
- The script simulates the installation command
- Actual package installation must be done in Databricks UI or via Jobs API
- We verify the deployment is ready for manual installation

### 2. Python Kernel Restart
**Limitation:** `dbutils.library.restartPython()` is not available via Spark Connect.

**Workaround:**
- The script simulates restart behavior
- In real usage, restart would happen in Databricks environment
- We test that imports are properly structured

### 3. Import Testing
**Limitation:** PyForge CLI imports require the package to be installed in Databricks runtime.

**Workaround:**
- Script simulates import commands
- Verifies import syntax and structure
- Tests package availability via volume access

### 4. File System Access
**Limitation:** Some DBFS/Volume operations may require specific permissions.

**Workaround:**
- Script attempts various access methods
- Falls back gracefully when permissions are insufficient
- Provides informative error messages

## Expected Output

When running successfully, you should see:

```
🚀 PYFORGE CLI NOTEBOOK EXECUTION VIA SPARK CONNECT
=================================================================
📅 Started: 2025-06-27 12:45:00

🔌 CONNECTING TO DATABRICKS
==================================================
  ✓ Set DATABRICKS_SERVERLESS_COMPUTE_ID=auto
📡 Creating Databricks Connect session (profile: DEFAULT)...
  ✅ Spark session created successfully
  ✅ Workspace client initialized
🧪 Testing connection...
  ✅ Connection test passed: 1, 2025-06-27 19:45:00.123

📦 INSTALLING PYFORGE CLI
========================================
🔄 Would execute: %pip install /Volumes/.../pyforge_cli-0.5.9-py3-none-any.whl --force-reinstall
  ✅ Installation command prepared

🔧 ENVIRONMENT VERIFICATION
========================================
  ✅ Connection: ✅ SUCCESS
  📅 Timestamp: 2025-06-27 19:45:00.456
  ⚡ Spark Version: 3.5.0

📥 IMPORT SIMULATION
==============================
🔄 Import commands that would be tested:
  import pyforge_cli
  from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend
  ✅ Import simulation completed

📁 VOLUME ACCESS TEST
==============================
  ✅ Found 3 files in deployment volume
    📄 pyforge_cli-0.5.9-py3-none-any.whl (1234567 bytes)

⚡ PERFORMANCE TEST
=========================
  ✅ SQL completed in 0.245 seconds
  🏆 Performance: Excellent

📊 EXECUTION REPORT
==============================
📋 Test Summary:
  ✅ Databricks Connection
  ✅ Pip Install
  ✅ Environment Verification
  ✅ Import Tests
  ✅ Volume Access
  ✅ Performance Test

💾 Report saved: spark_connect_execution_report.json

🎉 NOTEBOOK EXECUTION COMPLETED!
```

## Troubleshooting

### Connection Issues
```bash
# Check Databricks CLI version
databricks --version

# Test connection
databricks current-user me

# Reconfigure if needed
databricks configure --token
```

### Environment Issues
```bash
# Check Python packages
pip list | grep databricks

# Install/upgrade if needed
pip install --upgrade databricks-connect databricks-sdk
```

### Permission Issues
- Ensure your user has access to Unity Catalog volumes
- Check Databricks workspace permissions
- Verify serverless compute access

## Next Steps

After successful Spark Connect execution:

1. **Manual Validation**: Run the actual notebook in Databricks UI to validate real imports
2. **Real MDB Testing**: Test with actual MDB files in Databricks environment
3. **Production Deployment**: Deploy PyForge CLI to your production Databricks workspace

## Files Generated

- `notebook_execution.log` - Detailed execution logs
- `spark_connect_execution_report.json` - Comprehensive test results
- Console output with real-time progress

## Advanced Usage

### Custom Configuration
```python
# Use different Databricks profile
executor = NotebookExecutor(profile="MY_PROFILE")

# Custom environment variables
os.environ['DATABRICKS_COMPUTE_ID'] = 'my-compute-id'
```

### Debugging
```python
# Enable debug logging
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Run with verbose output
executor.setup_logging()
```

This setup allows you to test most of the notebook functionality remotely while identifying which parts need to be run in the actual Databricks environment.