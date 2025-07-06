# Databricks and PySpark Compatibility Guide

## Overview

PyForge CLI includes a Databricks extension that requires specific versions of PySpark and related libraries to ensure compatibility with Databricks Serverless Environment V1.

## Version Requirements

### Databricks Serverless V1 Environment

Based on Databricks Runtime 14.3 LTS, the following versions are required:

- **Python**: 3.10.12
- **Apache Spark**: 3.5.0
- **PySpark**: 3.5.0
- **Delta Lake**: 3.1.0
- **PyArrow**: 8.0.0
- **Pandas**: 1.5.3
- **NumPy**: 1.23.5

### Development Environment Setup

#### 1. Python Version

For best compatibility, use Python 3.10:

```bash
# Check if Python 3.10 is installed
python3.10 --version

# Create virtual environment with Python 3.10
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
# Install with Databricks extension
pip install -e ".[databricks]"

# This installs:
# - pyspark==3.5.0
# - delta-spark==3.1.0
```

#### 3. Java Requirements

PySpark 3.5.0 requires Java 8 or 11:

```bash
# Check Java version
java -version

# Install Java 11 (Ubuntu/Debian)
sudo apt-get install openjdk-11-jdk

# Install Java 11 (macOS)
brew install openjdk@11
```

## Using Constraints Files

To ensure exact version compatibility with Databricks Serverless V1:

```bash
# Install with constraints
pip install -c constraints-databricks-serverless-v1.txt -e ".[databricks]"
```

The constraints file includes all library versions used in Databricks Serverless V1.

## Running Databricks Tests

### Prerequisites

1. Python 3.10 installed
2. Java 8 or 11 installed
3. PySpark 3.5.0 and delta-spark 3.1.0 installed

### Running Tests

```bash
# Run all Databricks tests
pytest tests/test_databricks_extension.py -v

# Run with coverage
pytest tests/test_databricks_extension.py --cov=src/pyforge_cli/extensions/databricks

# Run specific test
pytest tests/test_databricks_extension.py::TestDatabricksEnvironment -v
```

## Known Compatibility Issues

### 1. PySpark and Pandas Version Conflict

PySpark 3.5.0 typically requires Pandas >= 2.0.0, but Databricks Serverless V1 uses Pandas 1.5.3. This may generate deprecation warnings but should work correctly.

### 2. Python 3.11+ Compatibility

PyArrow 8.0.0 has build issues with Python 3.11+. Use Python 3.10 for best compatibility.

### 3. Library Version Constraints

Some libraries may have different version requirements. Always use the constraints file when installing for Databricks compatibility.

## CI/CD Configuration

The GitHub Actions workflow is configured to test with:

- Python versions: 3.9, 3.10 (not 3.11 due to PyArrow compatibility)
- PySpark version: 3.5.0
- Java version: 11

## Troubleshooting

### Issue: PySpark fails to initialize

**Solution**: Ensure Java is installed and JAVA_HOME is set:

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 11)  # macOS
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Linux
```

### Issue: Import errors with PySpark

**Solution**: Install all required dependencies:

```bash
pip install pyspark==3.5.0 delta-spark==3.1.0 py4j==0.10.9.7
```

### Issue: Version conflicts

**Solution**: Use the constraints file:

```bash
pip install -c constraints-databricks-serverless-v1.txt -e ".[databricks]"
```

## Development Tips

1. **Always use Python 3.10** for Databricks development
2. **Pin library versions** to match Databricks environment
3. **Test locally** before deploying to Databricks
4. **Use constraints files** to prevent version drift
5. **Monitor deprecation warnings** but don't let them block development

## References

- [Databricks Runtime 14.3 LTS Release Notes](https://docs.databricks.com/en/release-notes/runtime/14.3lts.html)
- [Databricks Serverless Environment V1](https://learn.microsoft.com/en-us/azure/databricks/release-notes/serverless/environment-version/one)
- [PySpark 3.5.0 Documentation](https://spark.apache.org/docs/3.5.0/)
- [Delta Lake 3.1.0 Documentation](https://docs.delta.io/3.1.0/)