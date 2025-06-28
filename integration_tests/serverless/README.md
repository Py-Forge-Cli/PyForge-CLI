# PyForge CLI Serverless Testing Framework

Simple and practical testing framework for PyForge CLI on Databricks Serverless V1 environment with clear issue monitoring and reporting.

## Overview

This testing framework provides:
- 🔍 **Environment Verification** - Checks V1 compatibility (Python 3.10, Java 8)
- 📦 **Installation Testing** - Tests PyForge CLI with V1-specific dependencies  
- 📄 **MDB File Validation** - Tests Microsoft Access database connectivity
- 📊 **Performance Monitoring** - Tracks Spark and backend performance
- 🔧 **Issue Reporting** - Clear error identification and fix suggestions

## Quick Start

### Prerequisites

1. **Databricks CLI Configuration**
```bash
databricks configure --profile DEFAULT
```

2. **Environment Setup**
```bash
# Clear conflicting variables
unset DATABRICKS_CLIENT_ID
unset DATABRICKS_CLIENT_SECRET

# Set serverless compute
export DATABRICKS_SERVERLESS_COMPUTE_ID=auto
```

3. **Install Dependencies**
```bash
pip install databricks-connect==14.3.7
pip install databricks-sdk
```

### Running Tests

#### Option 1: Python Script (Command Line)
```bash
# Run all tests
python run_simple_tests.py --verbose

# Quick run
python run_simple_tests.py
```

#### Option 2: Databricks Notebook (Recommended)
1. Upload `PyForge_V1_Testing_Notebook.py` to Databricks workspace
2. Run all cells sequentially
3. Review results in each section

## Test Coverage

### 1. Environment Verification
- Python version check (should be 3.10.x for V1)
- Java version detection (should be Java 8)
- Databricks runtime verification (should be client.1.x)
- Serverless compute confirmation
- Basic Spark functionality test

### 2. PyForge CLI Installation
- Installs PyForge CLI wheel with V1-compatible dependencies:
  - `jaydebeapi>=1.2.3,<1.3.0`
  - `jpype1>=1.3.0,<1.4.0`
- Monitors installation for errors
- Provides specific fix suggestions for common issues

### 3. Import and Backend Testing
- Verifies PyForge CLI imports correctly
- Tests UCanAccessBackend initialization
- Checks individual components (Java, JayDeBeApi, JARs)
- Reports backend availability status

### 4. MDB File Access Validation
- Tests with real Access database files:
  - `Northwind_2007_VBNet.accdb` (modern format)
  - `access_sakila.mdb` (legacy format)
- Validates connection, table listing, and data reading
- Measures performance and reports issues

### 5. Performance Monitoring
- Tests Spark SQL performance
- Reports session information
- Monitors resource usage
- Tracks execution times

## V1 Environment Specifications

Based on Databricks Serverless V1 compatibility analysis:

| Component | Version |
|-----------|---------|
| Python | 3.10.12 |
| Java | 8 (Zulu OpenJDK) |
| Databricks Connect | 14.3.7 |
| Runtime | client.1.13 |
| UCanAccess | 4.0.4 |

**Recommended Dependencies:**
```toml
jaydebeapi>=1.2.3,<1.3.0
jpype1>=1.3.0,<1.4.0
pandas<=1.5.3
pyarrow>=10.0.0
```

## Expected Results

### Successful Test Run
```
🔍 DATABRICKS V1 ENVIRONMENT CHECK
==================================================
🐍 Python Version: 3.10.12
  ✅ Correct for Databricks V1
☕ Java Home: /usr/lib/jvm/zulu8-ca-amd64/jre/
  ✅ Java 8 detected - compatible with UCanAccess 4.0.4
🔧 Databricks Runtime: client.1.13
  ✅ V1 runtime confirmed
⚡ Serverless: True
  ✅ Running on serverless compute

📦 PYFORGE CLI INSTALLATION
========================================
✅ Installation command executed

📥 PYFORGE CLI IMPORT VERIFICATION
=============================================
✅ pyforge_cli imported successfully
✅ UCanAccessBackend imported successfully
✅ Backend fully functional!

📄 MDB FILE ACCESS TEST
==============================
📁 Testing: Northwind_2007_VBNet.accdb
  File exists: True
  ✅ Connected successfully (1.23s)
  📋 Tables found: 15
  📊 Read 29 records from 'Customers'
```

## Common Issues and Fixes

The framework identifies common issues and provides specific fix suggestions:

| Issue | Detection | Fix Suggestion |
|-------|-----------|---------------|
| **Dependency Conflict** | `conflicting dependencies` in pip output | `%pip install --no-deps` with specific versions |
| **Java Version Mismatch** | `UnsupportedClassVersionError` | Ensure UCanAccess 4.0.4 (Java 8 compatible) |
| **Import Failures** | `ModuleNotFoundError` | Check installation, restart Python kernel |
| **File System Restrictions** | `Operation not supported` | Use memory=true connection mode |
| **Missing JAR Files** | `ClassNotFoundException` | Verify JAR bundling in wheel package |
| **Connection Timeouts** | Connection takes too long | Check file size and cluster resources |

## Output Files

Test results are saved to DBFS:
- `dbfs:/tmp/pyforge_tests/installation_report.txt` - Installation attempts log
- `dbfs:/tmp/pyforge_tests/mdb_validation_report.json` - MDB test results

## Troubleshooting

### Authentication Issues
```bash
# Re-configure Databricks CLI
databricks configure --profile DEFAULT

# Clear cached credentials
rm -rf ~/.databrickscfg
```

### Spark Connect Issues
```bash
# Verify Databricks Connect
python -c "from databricks.connect import DatabricksSession; print('OK')"

# Check environment
echo $DATABRICKS_SERVERLESS_COMPUTE_ID  # Should be 'auto'
```

### Missing Dependencies
```bash
# Install all required packages
pip install databricks-connect==14.3.7 databricks-sdk pytest
```

## Advanced Usage

### Custom Test Configuration

Create a custom test by extending `PyForgeServerlessTestCase`:

```python
from spark_setup_serverless import PyForgeServerlessTestCase

class MyCustomTest(PyForgeServerlessTestCase):
    def test_custom_functionality(self):
        # Your test code here
        result = self.spark.sql("SELECT 1").collect()
        self.assertEqual(result[0][0], 1)
```

### Environment Detection

The framework includes V1 environment verification:

```python
env_info = self.verify_environment()
print(f"Python: {env_info['python_version']}")
print(f"Java: {env_info['java_version']}")
print(f"Runtime: {env_info['databricks_runtime']}")
```

## Integration with CI/CD

Example GitHub Actions workflow:

```yaml
name: PyForge Serverless Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure Databricks
        run: |
          echo "[DEFAULT]" > ~/.databrickscfg
          echo "host = ${{ secrets.DATABRICKS_HOST }}" >> ~/.databrickscfg
          echo "token = ${{ secrets.DATABRICKS_TOKEN }}" >> ~/.databrickscfg
      
      - name: Run Tests
        run: |
          export DATABRICKS_SERVERLESS_COMPUTE_ID=auto
          python tests/serverless/run_serverless_tests.py --suite all
```

## Contributing

When adding new tests:
1. Extend `PyForgeServerlessTestCase` for Spark access
2. Follow the iterative testing pattern
3. Include error analysis and corrections
4. Generate comprehensive reports
5. Document expected results

## License

This testing framework is part of the PyForge CLI project and follows the same license terms.