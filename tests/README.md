# PyForge CLI Test Suite

This directory contains the test suite for PyForge CLI, including unit tests, integration tests, and PySpark/Databricks extension tests.

## Prerequisites

### Local Development

1. **Java Installation** (Required for PySpark tests)
   - Java 8 or 11 is required
   - macOS: `brew install openjdk@11`
   - Ubuntu: `sudo apt-get install openjdk-11-jdk`
   - Windows: Download from [Adoptium](https://adoptium.net/)

2. **Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev,test]"
   ```

3. **PySpark Dependencies**
   ```bash
   pip install pyspark==3.5.2 delta-spark==3.1.0 databricks-sdk==0.19.0
   pip install pytest-xdist findspark py4j
   ```

### Environment Setup

Set the following environment variables:

```bash
export JAVA_HOME=/path/to/java  # e.g., /Library/Java/JavaVirtualMachines/jdk-11.0.13.jdk/Contents/Home
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=python3
export PYARROW_IGNORE_TIMEZONE=1
export SPARK_LOCAL_IP=127.0.0.1
unset SPARK_HOME  # Clear any existing SPARK_HOME
```

Or use the provided setup script:

```bash
bash scripts/setup_test_environment.sh
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Test Categories

```bash
# Unit tests only (excluding PySpark/integration)
pytest tests/ -v -m "not pyspark and not integration"

# PySpark tests
pytest tests/ -v -m "pyspark" --run-pyspark

# Databricks extension tests
pytest tests/test_databricks_extension.py tests/test_databricks_environment.py -v

# Integration tests
pytest tests/ -v -m "integration"

# Fast tests only (exclude slow tests)
pytest tests/ -v -m "not slow"
```

### Individual Test Files

```bash
# CSV converter tests
pytest tests/test_csv_converter.py -v

# PySpark CSV converter tests
pytest tests/test_pyspark_csv_converter.py -v

# Extension system tests
pytest tests/test_extension_system.py -v
```

### With Coverage

```bash
pytest tests/ --cov=pyforge_cli --cov-report=html --cov-report=term
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── data/                    # Test data files
│   ├── csv/                # CSV test files
│   └── ...                 # Other test data
├── fixtures/               # Test fixtures and utilities
├── utils/                  # Test utilities
│   ├── __init__.py
│   ├── mock_dbutils.py     # Mock Databricks utilities
│   └── pyspark_test_config.py  # PySpark test configuration
├── unit/                   # Unit tests
├── test_*.py              # Test modules
└── README.md              # This file
```

## Test Markers

- `@pytest.mark.pyspark` - Tests requiring PySpark
- `@pytest.mark.databricks` - Databricks-specific tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests

## CI/CD Configuration

Tests run automatically in GitHub Actions with:

1. **Main CI Workflow** (`ci.yml`)
   - Runs on push/PR to main/develop branches
   - Includes Java setup for PySpark
   - Runs all tests with coverage

2. **PySpark Tests Workflow** (`pyspark-tests.yml`)
   - Triggered by changes to PySpark/Databricks code
   - Focused testing for Spark functionality
   - Matrix testing across Python versions

## Troubleshooting

### PySpark Import Error

If you see `ModuleNotFoundError: No module named 'pyspark'`:

```bash
pip install pyspark==3.5.2
```

### Java Not Found

If you see Java-related errors:

1. Verify Java installation: `java -version`
2. Set JAVA_HOME: `export JAVA_HOME=/path/to/java`
3. Add to PATH: `export PATH=$JAVA_HOME/bin:$PATH`

### Spark Session Creation Failed

If Spark session fails to start:

1. Clear SPARK_HOME: `unset SPARK_HOME`
2. Set local IP: `export SPARK_LOCAL_IP=127.0.0.1`
3. Check Java is accessible: `which java`

### Test Discovery Issues

If tests aren't discovered:

```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose discovery
pytest tests/ --collect-only
```

## Writing Tests

### Basic Test Template

```python
import pytest
from pyforge_cli.module import function_to_test

class TestMyFeature:
    def test_basic_functionality(self):
        result = function_to_test("input")
        assert result == "expected"
    
    @pytest.mark.pyspark
    def test_with_spark(self, spark_session):
        df = spark_session.range(10)
        assert df.count() == 10
```

### Databricks Extension Test

```python
import pytest
from unittest.mock import patch
from pyforge_cli.extensions.databricks import DatabricksExtension

class TestDatabricksFeature:
    @pytest.mark.databricks
    def test_databricks_functionality(self, mock_dbutils):
        # Test with mock dbutils
        extension = DatabricksExtension()
        result = extension.some_method()
        assert result is not None
```

## Contributing

1. Write tests for new features
2. Ensure all tests pass locally
3. Add appropriate markers for test categorization
4. Update this README if adding new test categories
5. Verify CI passes before merging