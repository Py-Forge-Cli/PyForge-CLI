# PyForge CLI Databricks Extension - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying and testing the PyForge CLI Databricks extension notebooks in your Databricks workspace.

## Prerequisites

### Databricks Workspace Requirements
- Databricks workspace with Unity Catalog enabled
- Compute clusters (both serverless and classic) for comprehensive testing
- Unity Catalog Volume with write permissions
- Python 3.8+ runtime

### Permissions Required
- Workspace admin or ability to import notebooks
- Unity Catalog Volume read/write access
- Cluster creation/access permissions
- Package installation permissions

## Deployment Methods

### Method 1: Databricks CLI (Recommended)

#### 1. Install Databricks CLI
```bash
pip install databricks-cli
```

#### 2. Configure Authentication
```bash
databricks configure --token
```
Enter your Databricks workspace URL and personal access token.

#### 3. Upload Notebooks
```bash
# Navigate to the project directory
cd /path/to/PyForge-CLI

# Upload functional test notebooks
databricks workspace import notebooks/testing/functional/01-databricks-extension-functional.ipynb \
    /Workspace/Users/your-email@company.com/PyForge-Testing/01-databricks-extension-functional \
    --language PYTHON --format JUPYTER

databricks workspace import notebooks/testing/functional/03-databricks-extension-serverless-test.ipynb \
    /Workspace/Users/your-email@company.com/PyForge-Testing/03-databricks-extension-serverless-test \
    --language PYTHON --format JUPYTER

# Upload integration test notebooks (convert .py to .ipynb format first)
databricks workspace import notebooks/testing/integration/03-databricks-extension-integration.py \
    /Workspace/Users/your-email@company.com/PyForge-Testing/03-databricks-extension-integration \
    --language PYTHON

databricks workspace import notebooks/testing/integration/04-databricks-volume-integration.py \
    /Workspace/Users/your-email@company.com/PyForge-Testing/04-databricks-volume-integration \
    --language PYTHON
```

### Method 2: Databricks Web UI

#### 1. Access Databricks Workspace
- Log into your Databricks workspace
- Navigate to the Workspace section

#### 2. Create Test Directory
- Create a new folder: `PyForge-Testing`
- Create subfolders: `functional`, `integration`

#### 3. Import Notebooks
- In each subfolder, click "Import"
- Select "File" and upload the corresponding notebook files
- Ensure the language is set to "Python"

### Method 3: Git Integration (If Available)

#### 1. Setup Git Integration
- In Databricks, go to User Settings → Git Integration
- Connect your Git repository

#### 2. Clone Repository
- Clone the PyForge-CLI repository
- Navigate to `notebooks/testing/` directory

## Environment Setup

### 1. Create Unity Catalog Volume

```sql
-- Create catalog if not exists
CREATE CATALOG IF NOT EXISTS main;

-- Create schema if not exists  
CREATE SCHEMA IF NOT EXISTS main.default;

-- Create volume for testing
CREATE VOLUME IF NOT EXISTS main.default.pyforge
COMMENT 'Volume for PyForge CLI testing';
```

### 2. Set Volume Permissions

```sql
-- Grant permissions to your user/group
GRANT READ, WRITE ON VOLUME main.default.pyforge TO `your-email@company.com`;
```

### 3. Create Test Clusters

#### Serverless Cluster (Recommended)
- **Type**: Serverless
- **Runtime**: DBR 13.3 LTS or later
- **Auto-termination**: 60 minutes

#### Classic Cluster (For Fallback Testing)
- **Type**: All-purpose cluster
- **Runtime**: DBR 13.3 LTS
- **Node Type**: i3.xlarge (or similar)
- **Workers**: 1-2 workers
- **Auto-termination**: 60 minutes

## Pre-Deployment Testing Setup

### 1. Install PyForge CLI

Run this in a Databricks notebook cell:

```python
%pip install --no-cache-dir pyforge-cli[databricks]
```

### 2. Verify Installation

```python
# Test imports
from pyforge_cli.extensions.databricks.pyforge_databricks import PyForgeDatabricks
from pyforge_cli.extensions.databricks.volume_operations import VolumeOperations

# Test initialization
forge = PyForgeDatabricks(auto_init=True)
print("✅ PyForge Databricks extension ready!")

# Get environment info
env_info = forge.get_environment_info()
print(f"Environment: {env_info['compute_type']} ({env_info['runtime_version']})")
```

### 3. Test Volume Access

```python
# Test volume access
volume_path = "/Volumes/main/default/pyforge"
try:
    files = dbutils.fs.ls(volume_path)
    print(f"✅ Volume accessible: {len(files)} items found")
except Exception as e:
    print(f"❌ Volume access failed: {e}")
    print("Please create the volume and grant permissions")
```

## Testing Execution Plan

### Phase 1: Basic Functional Testing

#### 1. Run Functional Tests
- Open: `01-databricks-extension-functional.ipynb`
- Configure widgets:
  - PyForge Version: `latest`
  - Volume Path: `/Volumes/main/default/pyforge`
  - Test Scope: `basic`
  - Verbose Logging: `true`
- Run all cells
- Expected duration: 5-10 minutes

#### Expected Results:
```
✅ Overall Test Status: PASSED
🕐 Test Duration: ~300 seconds
🌐 Environment: serverless/classic
📦 PyForge Version: latest

📋 Test Results:
   Environment Detection: ✅
   Plugin Discovery: ✅
   Extensions Loaded: 1+
   API Methods: 5/6 passed
   Fallback Behavior: ✅
   Error Handling: ✅
```

### Phase 2: Serverless-Specific Testing

#### 1. Run Serverless Tests (On Serverless Cluster)
- Open: `03-databricks-extension-serverless-test.ipynb`
- Configure widgets:
  - Dataset Size: `medium`
  - Test Streaming: `true`
  - Test Delta Lake: `true`
  - Test Memory Optimization: `true`
- Run all cells
- Expected duration: 10-15 minutes

#### Expected Results:
```
✅ Overall Test Status: PASSED
🕐 Total Test Duration: ~600 seconds
📊 Dataset Size: medium (10,000 rows)

⚡ Performance Summary:
   CSV Conversion Throughput: 50,000+ rows/sec
   Engine Used: pyspark
   Memory Usage: <100 MB
   Delta Lake Support: ✅
```

### Phase 3: Integration Testing

#### 1. Run Comprehensive Integration Tests
- Open: `03-databricks-extension-integration.py`
- Configure widgets for comprehensive testing
- Run all cells
- Expected duration: 15-20 minutes

#### 2. Run Volume Integration Tests
- Open: `04-databricks-volume-integration.py`
- Configure widgets:
  - Catalog: `main`
  - Schema: `default`
  - Volume: `pyforge`
  - Test Large Files: `true`
- Run all cells
- Expected duration: 10-15 minutes

## Troubleshooting

### Common Issues and Solutions

#### 1. Installation Issues

**Issue**: `ModuleNotFoundError: No module named 'pyforge_cli'`
**Solution**: 
```python
%pip install --no-cache-dir --upgrade pyforge-cli[databricks]
dbutils.library.restartPython()
```

#### 2. Volume Access Issues

**Issue**: `Permission denied` or `Volume not found`
**Solution**:
- Verify Unity Catalog is enabled
- Check volume exists: `SHOW VOLUMES IN main.default;`
- Grant permissions: `GRANT READ, WRITE ON VOLUME main.default.pyforge TO ...;`

#### 3. Environment Detection Issues

**Issue**: `Environment not detected as serverless`
**Solution**:
- Verify you're using a serverless cluster
- Check runtime version (DBR 13.3+ required)
- Force environment in widget configuration

#### 4. Performance Issues

**Issue**: Slow conversion times
**Solution**:
- Check cluster resources
- Enable streaming mode for large files
- Verify PySpark availability

#### 5. Memory Errors

**Issue**: `OutOfMemoryError` during large file tests
**Solution**:
```python
# Reduce dataset size
TEST_DATASET_SIZE = "small"

# Enable streaming
TEST_STREAMING = True

# Increase cluster memory or use serverless
```

### Debugging Commands

```python
# Environment diagnostics
import os, sys
print(f"Runtime: {os.environ.get('DATABRICKS_RUNTIME_VERSION')}")
print(f"Python: {sys.version}")

# Check PySpark
try:
    import pyspark
    print(f"PySpark: {pyspark.__version__}")
    print(f"Spark Version: {spark.version}")
except:
    print("PySpark: Not available")

# Check Delta Lake
try:
    import delta
    print(f"Delta Lake: {delta.__version__}")
except:
    print("Delta Lake: Not available")

# Memory check
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

## Expected Test Results

### Serverless Environment
- **Plugin Discovery**: ✅ (1-2 seconds)
- **API Initialization**: ✅ (2-5 seconds)  
- **Environment Detection**: ✅ (serverless)
- **CSV Conversion**: ✅ (50,000+ rows/sec)
- **Volume Operations**: ✅ 
- **Delta Lake Support**: ✅
- **Memory Efficiency**: ✅ (<100MB for 10K rows)

### Classic Environment
- **Plugin Discovery**: ✅ (1-3 seconds)
- **API Initialization**: ✅ (5-10 seconds)
- **Environment Detection**: ✅ (classic)
- **CSV Conversion**: ✅ (20,000+ rows/sec with PySpark)
- **Fallback Behavior**: ✅ (pandas when PySpark unavailable)
- **Volume Operations**: ✅

## Success Criteria

### ✅ Functional Tests Pass
- All API methods work correctly
- Environment detection accurate
- Error handling graceful
- Performance within expected ranges

### ✅ Integration Tests Pass  
- Plugin system integration
- Volume operations functional
- Large file handling effective
- Cross-environment compatibility

### ✅ Performance Benchmarks Met
- Serverless: >50K rows/sec CSV conversion
- Classic: >20K rows/sec CSV conversion  
- Memory usage: <100MB per 10K rows
- Delta Lake: <5% performance overhead

## Post-Testing Actions

### 1. Results Documentation
- Save test results from each notebook
- Document any environment-specific issues
- Record performance benchmarks

### 2. Issue Reporting
- Report any test failures with environment details
- Include error logs and stack traces
- Suggest workarounds if found

### 3. Cleanup
- Remove test datasets from Volumes
- Terminate test clusters
- Archive test results

## Support

For additional support:
1. Check the main PyForge CLI documentation
2. Review the testing guide: `docs/testing/databricks-extension-testing-guide.md`
3. File issues in the PyForge CLI repository
4. Contact the development team with test results

## Next Steps

After successful testing:
1. Proceed with TASK-040: Performance Optimization
2. Continue with remaining tasks in the implementation plan
3. Prepare for beta release testing
4. Document any environment-specific optimizations needed