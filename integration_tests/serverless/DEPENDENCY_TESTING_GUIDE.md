# PyForge CLI Dependency Testing Guide for Databricks Serverless V1

## 🔍 Issue Summary

Based on our investigation, there appears to be a dependency management issue when installing PyForge CLI in Databricks Serverless V1 environment. This guide provides manual steps to diagnose and resolve the issue.

## 📋 Test Notebooks Available

We've created several test notebooks that are now available in your Databricks workspace:

1. **Full Integration Test**: `/Workspace/CoreDataEngineers/usa-sdandey@deloitte.com/pyforge_notebooks/PyForge_Manual_Test_Steps`
   - Complete testing workflow with all features

2. **Simple Dependency Test**: `/Workspace/CoreDataEngineers/usa-sdandey@deloitte.com/pyforge_notebooks/test_simple_dependency`
   - Focused test on dependency installation and imports

3. **Original Test Notebook**: `/Workspace/CoreDataEngineers/usa-sdandey@deloitte.com/pyforge_notebooks/PyForge_Databricks_Test_Notebook`
   - Comprehensive test with performance benchmarks

## 🧪 Manual Testing Steps

### Step 1: Open Databricks Workspace
Navigate to: https://adb-270181971930646.6.azuredatabricks.net

### Step 2: Create a New Serverless V1 Notebook
1. Create a new notebook
2. Ensure it's attached to a Serverless compute resource
3. Verify it's using V1 (Python 3.10)

### Step 3: Run Dependency Diagnosis

Copy and run these cells in order:

#### Cell 1: Environment Check
```python
import sys
import os
print(f"Python: {sys.version}")
print(f"Runtime: {os.environ.get('DATABRICKS_RUNTIME_VERSION', 'unknown')}")
print(f"Serverless: {os.environ.get('DATABRICKS_SERVERLESS_COMPUTE_ID', 'not set')}")
```

#### Cell 2: Install PyForge with Verbose Output
```python
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/usa-sdandey@deloitte.com/pyforge_cli-0.5.9-py3-none-any.whl -i https://pypi.org/simple --force-reinstall --verbose
```

**Watch for:**
- Dependency resolution conflicts
- PyPI index access issues
- Installation errors

#### Cell 3: Restart Kernel
```python
dbutils.library.restartPython()
```

#### Cell 4: Test Imports
```python
# Test results dictionary
results = {}

# Test PyForge import
try:
    import pyforge_cli
    results["pyforge_cli"] = "✅ SUCCESS"
    print("✅ PyForge CLI imported successfully")
except Exception as e:
    results["pyforge_cli"] = f"❌ FAILED: {e}"
    print(f"❌ PyForge CLI import failed: {e}")

# Check installed packages
import subprocess
pip_list = subprocess.run([sys.executable, "-m", "pip", "list"], 
                         capture_output=True, text=True)
print("\n📦 Installed packages:")
print(pip_list.stdout)

# Test individual dependencies
for dep in ["pandas", "pyarrow", "jaydebeapi", "jpype1"]:
    try:
        __import__(dep)
        results[dep] = "✅ SUCCESS"
        print(f"✅ {dep} imported successfully")
    except Exception as e:
        results[dep] = f"❌ FAILED: {e}"
        print(f"❌ {dep} import failed: {e}")

# Test backend
try:
    from pyforge_cli.backends.ucanaccess_backend import UCanAccessBackend
    backend = UCanAccessBackend()
    available = backend.is_available()
    results["backend"] = f"✅ Available: {available}"
    print(f"✅ Backend available: {available}")
except Exception as e:
    results["backend"] = f"❌ FAILED: {e}"
    print(f"❌ Backend failed: {e}")

# Summary
print("\n📊 DEPENDENCY TEST SUMMARY:")
for test, result in results.items():
    print(f"  {test}: {result}")
```

## 🔧 Common Issues and Solutions

### Issue 1: Dependency Not Found
**Symptom**: `ModuleNotFoundError: No module named 'jaydebeapi'`

**Solutions**:
1. Install dependencies separately first:
   ```python
   %pip install jaydebeapi==1.2.3 jpype1==1.3.0 -i https://pypi.org/simple
   %pip install /Volumes/.../pyforge_cli-0.5.9-py3-none-any.whl --no-deps
   ```

2. Check if dependencies are in the wheel:
   ```python
   import zipfile
   with zipfile.ZipFile("/dbfs/Volumes/.../pyforge_cli-0.5.9-py3-none-any.whl", 'r') as z:
       print("METADATA:", z.read("pyforge_cli-0.5.9.dist-info/METADATA").decode())
   ```

### Issue 2: PyPI Index Issues
**Symptom**: Timeout or connection errors during installation

**Solutions**:
1. Try without index specification:
   ```python
   %pip install /Volumes/.../pyforge_cli-0.5.9-py3-none-any.whl --force-reinstall
   ```

2. Use Databricks default index:
   ```python
   %pip install /Volumes/.../pyforge_cli-0.5.9-py3-none-any.whl --index-url https://pypi.org/simple --extra-index-url https://pypi.org/simple
   ```

### Issue 3: Java/JPype Issues
**Symptom**: `RuntimeError: Unable to start JVM`

**Solutions**:
1. Check Java version:
   ```python
   import subprocess
   java_version = subprocess.run(["java", "-version"], capture_output=True, text=True)
   print(java_version.stderr)
   ```

2. Set Java paths:
   ```python
   import os
   os.environ['JAVA_HOME'] = '/usr/lib/jvm/zulu8-ca-amd64'
   ```

## 📊 Expected Successful Output

When everything works correctly, you should see:
```
✅ PyForge CLI imported successfully
✅ pandas imported successfully
✅ pyarrow imported successfully
✅ jaydebeapi imported successfully
✅ jpype1 imported successfully
✅ Backend available: True
```

## 🚨 Reporting Issues

If you encounter dependency issues:

1. **Capture pip install output**: Copy the full verbose output
2. **Check pip list**: Note which packages are installed
3. **Error messages**: Copy exact import error messages
4. **Environment details**: Python version, runtime version

## 💡 Alternative Approaches

### Option 1: Pre-install Dependencies
```python
# Install dependencies first
%pip install pandas pyarrow jaydebeapi==1.2.3 jpype1==1.3.0 -i https://pypi.org/simple

# Then install PyForge without dependencies
%pip install /Volumes/.../pyforge_cli-0.5.9-py3-none-any.whl --no-deps --force-reinstall
```

### Option 2: Use Requirements File
Create a requirements.txt:
```
pandas
pyarrow
jaydebeapi>=1.2.3,<1.3.0
jpype1>=1.3.0,<1.4.0
/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/usa-sdandey@deloitte.com/pyforge_cli-0.5.9-py3-none-any.whl
```

Then install:
```python
%pip install -r requirements.txt -i https://pypi.org/simple
```

### Option 3: Build Complete Package
Consider building a "fat wheel" that bundles all dependencies to avoid resolution issues.

## 📝 Notes

- PyForge CLI v0.5.9 includes jaydebeapi and jpype1 as core dependencies
- The `-i https://pypi.org/simple` flag ensures packages come from standard PyPI
- Databricks Serverless V1 uses Python 3.10 and Java 8
- File system restrictions may affect temporary file operations

## ✅ Success Criteria

The dependency installation is successful when:
1. All imports work without errors
2. `backend.is_available()` returns `True`
3. MDB files can be read successfully
4. No Java or JPype errors occur

Run the simple dependency test notebook first to quickly identify any issues!