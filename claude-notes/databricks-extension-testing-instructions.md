# Databricks Extension Testing Instructions

## Deployment Summary

**Date**: July 7, 2025  
**Version**: pyforge_cli-1.0.9.dev53  
**Username**: usa-sdandey@deloitte.com  

### Deployed Components

1. **PyForge CLI Wheel**:
   - Location: `/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/usa-sdandey@deloitte.com/pyforge_cli-1.0.9.dev53-py3-none-any.whl`
   - Includes Databricks Extension V2 with all Spark converters

2. **Test Notebooks**:
   - Workspace Path: `/Workspace/CoreDataEngineers/usa-sdandey@deloitte.com/pyforge_notebooks/`
   - Key Databricks Extension Notebooks:
     - `functional/04-databricks-extension-functional.ipynb` - Main functional tests
     - `functional/05-databricks-extension-serverless.ipynb` - Serverless-specific tests
     - `functional/06-databricks-extension-comprehensive.ipynb` - Comprehensive tests

## Testing Instructions

### Step 1: Install PyForge CLI with Databricks Extension

In your Databricks notebook, run:

```python
# Install the wheel with proper PyPI index
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/usa-sdandey@deloitte.com/pyforge_cli-1.0.9.dev53-py3-none-any.whl --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

# Restart Python kernel to ensure clean import
dbutils.library.restartPython()
```

### Step 2: Verify Installation

```python
# Test basic imports
import pyforge_cli
print(f"PyForge CLI version: {pyforge_cli.__version__}")

# Test Databricks extension
from pyforge_cli.extensions.databricks import PyForgeDatabricks
print("✓ Databricks extension imported successfully")

# Check if extension is available
forge = PyForgeDatabricks()
env_info = forge.get_environment_info()
print(f"Environment: {env_info}")
```

### Step 3: Test Notebooks

Navigate to the following notebooks in your Databricks workspace:

1. **Basic Functional Testing**: 
   - Open: `/Workspace/CoreDataEngineers/usa-sdandey@deloitte.com/pyforge_notebooks/functional/04-databricks-extension-functional.ipynb`
   - This notebook tests all core PyForgeDatabricks API methods

2. **Serverless Environment Testing**:
   - Open: `/Workspace/CoreDataEngineers/usa-sdandey@deloitte.com/pyforge_notebooks/functional/05-databricks-extension-serverless.ipynb`
   - Tests specifically for Databricks Serverless compute

3. **Comprehensive Testing**:
   - Open: `/Workspace/CoreDataEngineers/usa-sdandey@deloitte.com/pyforge_notebooks/functional/06-databricks-extension-comprehensive.ipynb`
   - Full end-to-end testing suite

## Task Progress (from TASKS-Databricks-Extension.md)

### Completed Tasks (1-39) ✅

**Phase 1: Plugin Architecture Foundation (Tasks 1-15)** - Complete
- Plugin discovery, loader, registry
- CLI integration and hooks
- Unit and integration tests
- Documentation

**Phase 2: Databricks Extension (Tasks 16-39)** - Complete
- Environment detection (Serverless/Classic)
- Volume operations
- Spark converters (CSV, Excel, XML)
- Python API (PyForgeDatabricks)
- Comprehensive testing notebooks

### Remaining Tasks (40-53)

**Current Focus: TASK-040 - Performance Optimization**
- Profile all converters
- Optimize hot paths
- Reduce memory usage
- Achieve 3x speedup target

**Next Tasks:**
- TASK-041: Error Messages improvement
- TASK-042: Example Notebooks
- TASK-043: Documentation Update
- TASK-044-053: Testing & Release phases

## Test Scenarios to Validate

### 1. Environment Detection
```python
forge = PyForgeDatabricks()
print(forge.get_environment_info())
```

### 2. File Conversion
```python
# Test CSV conversion
result = forge.convert(
    input_path="/Volumes/cortex_dev_catalog/sandbox_testing/sample-datasets/csv/sample.csv",
    output_format="parquet"
)
print(result)
```

### 3. Batch Processing
```python
# Test batch conversion
results = forge.batch_convert(
    pattern="/Volumes/cortex_dev_catalog/sandbox_testing/sample-datasets/csv/*.csv",
    output_format="parquet"
)
```

### 4. Sample Datasets Installation
```python
# Install sample datasets for testing
datasets = forge.install_sample_datasets(
    formats=["csv", "excel", "xml"],
    max_size_mb=10
)
```

## Known Issues to Test

1. **JSON Parsing**: Fixed - notebooks now have valid JSON
2. **Environment Detection**: Should automatically detect Serverless vs Classic
3. **Fallback Mechanism**: Test with files that might fail Spark processing
4. **Volume Operations**: Verify Unity Catalog volume access

## Support

If you encounter issues:
1. Check the notebook outputs for detailed error messages
2. Verify you're using the correct Databricks runtime
3. Ensure Unity Catalog access permissions
4. Review logs in the notebook cells

## Next Steps After Testing

1. Document any issues found during testing
2. Performance metrics collection for TASK-040
3. Prepare feedback for error message improvements (TASK-041)
4. Note any missing functionality for documentation updates