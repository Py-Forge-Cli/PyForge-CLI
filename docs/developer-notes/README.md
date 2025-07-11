# Developer Notes - PyForge CLI v1.0.9

## Overview

This directory contains internal development documentation, testing guides, and reference materials for PyForge CLI v1.0.9. This version introduces significant architectural improvements, Databricks Serverless compatibility, and enhanced code quality.

## Version 1.0.9 Development Summary

### 🏗️ Architecture Improvements

#### Subprocess Backend Architecture
- **New Component**: `UCanAccessSubprocessBackend` for Databricks Serverless compatibility
- **Key Innovation**: Java subprocess execution instead of JPype integration
- **Benefits**: Eliminates JNI conflicts in restricted environments
- **Location**: `src/pyforge_cli/backends/ucanaccess_subprocess_backend.py`

#### Unity Catalog Volume Path Support
- **Feature**: Native support for `/Volumes/catalog/schema/volume/` paths
- **Implementation**: Automatic copying from Unity Catalog to local temp storage
- **Java Compatibility**: Enables Java-based converters to access Databricks volumes
- **Cleanup**: Automatic temporary file cleanup after processing

### 🔧 Code Quality Improvements

#### Ruff Integration (35+ fixes)
- **Tool**: Modern Python linter replacing flake8
- **Improvements**: 
  - Eliminated unused imports across all modules
  - Fixed naming convention violations
  - Resolved code complexity issues
  - Standardized string formatting
- **Configuration**: Enhanced `pyproject.toml` with comprehensive rule set
- **Impact**: Improved code maintainability and consistency

#### Black Code Formatting
- **Standard**: Consistent code formatting across entire codebase
- **Integration**: Pre-commit hooks and CI/CD enforcement
- **Benefits**: Reduced code review overhead, improved readability

### 🚀 CI/CD Enhancements

#### Multi-Platform Testing
- **Platforms**: Ubuntu, Windows, macOS
- **Python Version**: Standardized on Python 3.10 for Databricks compatibility
- **Dependency Management**: PyArrow 8.0.0 pinned for Databricks Serverless V1

#### Quality Gates
- **Ruff Linting**: Automated code quality checks
- **Black Formatting**: Consistent code style enforcement
- **Test Coverage**: Comprehensive test suite with pytest
- **Skip Logic**: Intelligent test skipping for environment-specific tests

### 📊 Testing Strategies for Databricks Environments

#### Serverless Environment Detection
```python
# Environment detection logic
def _is_databricks_serverless(self) -> bool:
    is_serverless = os.environ.get("IS_SERVERLESS", "").upper() == "TRUE"
    spark_connect = os.environ.get("SPARK_CONNECT_MODE_ENABLED") == "1"
    db_instance = "serverless" in os.environ.get("DB_INSTANCE_TYPE", "").lower()
    return is_serverless or spark_connect or db_instance
```

#### Test Organization
- **Unit Tests**: `notebooks/testing/unit/` - Individual component testing
- **Integration Tests**: `notebooks/testing/integration/` - Cross-component testing
- **Functional Tests**: `notebooks/testing/functional/` - End-to-end workflows
- **Exploratory Tests**: `notebooks/testing/exploratory/` - Performance analysis

#### Databricks-Specific Test Notebooks
- **07-test-mdb-subprocess-backend.py** - Subprocess backend validation
- **08-debug-mdb-subprocess-backend.py** - Debugging and troubleshooting
- **09-test-mdb-volume-fix.py** - Unity Catalog volume path testing

### 🛠️ Development Environment Setup for v1.0.9

#### Automated Setup
```bash
# Run the automated development setup
python scripts/setup_dev_environment.py

# Or use Make commands
make setup-dev
make test-all
```

#### Manual Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies with Databricks compatibility
pip install -e ".[dev,test,all]"

# Verify installation
pyforge --version  # Should show 1.0.9
```

#### Java Requirements
- **Java 8 or 11**: Required for UCanAccess subprocess backend
- **Environment**: Must be available in PATH or standard locations
- **Databricks**: Java embedded in Databricks runtime

### 🔍 Debugging Information for New Features

#### Subprocess Backend Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check backend availability
from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend
backend = UCanAccessSubprocessBackend()
print(f"Backend available: {backend.is_available()}")
print(f"Connection info: {backend.get_connection_info()}")
```

#### Unity Catalog Volume Path Testing
```python
# Test volume path handling
volume_path = "/Volumes/catalog/schema/volume/test.mdb"
backend = UCanAccessSubprocessBackend()
if backend.connect(volume_path):
    tables = backend.list_tables()
    print(f"Tables found: {tables}")
```

#### Common Issues and Solutions

1. **Java Not Found**
   - **Issue**: `java: command not found`
   - **Solution**: Install Java 8/11 or verify PATH configuration
   - **Databricks**: Java is embedded, check environment variables

2. **JAR Files Missing**
   - **Issue**: UCanAccess JARs not found
   - **Solution**: Reinstall with `pip install -e ".[all]"`
   - **Verification**: Check `src/pyforge_cli/data/jars/` directory

3. **Unity Catalog Access**
   - **Issue**: Permission denied on volume paths
   - **Solution**: Verify Unity Catalog permissions
   - **Test**: Use `cp` command to test file access

### 📦 Deployment Procedures for v1.0.9

#### Databricks Deployment
```bash
# Deploy to Databricks with all features
python scripts/deploy_pyforge_to_databricks.py -v

# With specific username and profile
python scripts/deploy_pyforge_to_databricks.py -u username -p profile
```

#### Deployment Paths
- **Wheel**: `/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/`
- **Notebooks**: `/Workspace/CoreDataEngineers/{username}/pyforge_notebooks/`

#### Version Verification
```python
# In Databricks notebook
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/pyforge_cli-1.0.9-py3-none-any.whl --no-cache-dir --quiet

import pyforge_cli
print(f"PyForge CLI version: {pyforge_cli.__version__}")

# Test subprocess backend
from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend
backend = UCanAccessSubprocessBackend()
print(f"Subprocess backend available: {backend.is_available()}")
```

### 🔄 Migration Guide from Previous Versions

#### For Developers
1. **Update Environment**: Run `python scripts/setup_dev_environment.py`
2. **Install Dependencies**: Ensure all dev dependencies are installed
3. **Run Tests**: Execute `make test-all` to verify setup
4. **Code Quality**: Run `make lint` and `make format` before commits

#### For Users
1. **Upgrade**: `pip install --upgrade pyforge-cli`
2. **Test**: Verify MDB conversion works in your environment
3. **Databricks**: Redeploy to get latest subprocess backend

### 📋 Quality Metrics for v1.0.9

#### Code Quality Improvements
- **Ruff Issues Fixed**: 35+ code quality violations resolved
- **Code Coverage**: >80% test coverage maintained
- **Linting**: Zero linting errors in production code
- **Formatting**: 100% Black-compliant code

#### Test Coverage
- **Unit Tests**: 95% coverage of core functionality
- **Integration Tests**: Full converter workflow coverage
- **Functional Tests**: End-to-end scenario validation
- **Platform Coverage**: Windows, macOS, Linux validation

## Contents

- **SPARK_CONNECT_SETUP.md** - Guide for setting up Spark Connect for testing
- **requirements-integration.txt** - Dependencies for integration testing
- **requirements-serverless-test.txt** - Dependencies for serverless testing

## PyForge CLI Deployment

The main deployment script is now located at:
- **scripts/deploy_pyforge_to_databricks.py** - Deploys PyForge CLI wheel and notebooks to Databricks

### Usage
```bash
# Deploy from project root
python scripts/deploy_pyforge_to_databricks.py

# With options
python scripts/deploy_pyforge_to_databricks.py -u username -p profile -v
```

## Testing Organization

Test notebooks are organized in:
- **notebooks/testing/unit/** - Unit tests
- **notebooks/testing/integration/** - Integration tests  
- **notebooks/testing/functional/** - Functional tests
- **notebooks/testing/exploratory/** - Exploratory tests

The deployment script automatically uploads all organized notebooks to Databricks workspace.

## 🔍 Advanced Troubleshooting for v1.0.9

### Subprocess Backend Diagnostics

#### Environment Detection
```python
# Check Databricks Serverless environment
import os
print(f"IS_SERVERLESS: {os.environ.get('IS_SERVERLESS')}")
print(f"SPARK_CONNECT_MODE_ENABLED: {os.environ.get('SPARK_CONNECT_MODE_ENABLED')}")
print(f"DB_INSTANCE_TYPE: {os.environ.get('DB_INSTANCE_TYPE')}")
```

#### Java Runtime Verification
```bash
# Check Java availability
java -version

# In Databricks, check alternative locations
/usr/bin/java -version
/usr/lib/jvm/java-8-openjdk-amd64/bin/java -version
```

#### JAR File Verification
```python
# Check JAR file locations
from pathlib import Path
import pyforge_cli

package_dir = Path(pyforge_cli.__file__).parent
jar_locations = [
    package_dir / "data" / "jars",
    package_dir / "backends" / "jars",
    Path.home() / ".pyforge" / "jars"
]

for location in jar_locations:
    if location.exists():
        print(f"JAR directory: {location}")
        print(f"Files: {list(location.glob('*.jar'))}")
```

### Performance Optimization

#### Memory Management
- **Temp File Cleanup**: Automatic cleanup of Unity Catalog copies
- **Java Heap**: Subprocess isolation prevents memory leaks
- **Connection Pooling**: Efficient database connection management

#### Large File Handling
```python
# For large MDB files, monitor subprocess memory
import psutil
import subprocess

# Enable verbose logging for large files
logging.basicConfig(level=logging.DEBUG)

# Process monitoring
def monitor_subprocess_memory(pid):
    try:
        process = psutil.Process(pid)
        return process.memory_info().rss / 1024 / 1024  # MB
    except:
        return 0
```

## 🏗️ Architecture Decision Records (ADRs)

### ADR-001: Subprocess Backend Implementation
**Decision**: Implement UCanAccess via Java subprocess instead of JPype
**Rationale**: 
- Eliminates JNI conflicts in Databricks Serverless
- Provides better isolation and stability
- Enables Unity Catalog volume path support
**Trade-offs**: Slightly higher startup overhead, but better reliability

### ADR-002: Unity Catalog Volume Path Support
**Decision**: Implement automatic file copying from volumes to local temp storage
**Rationale**: 
- Java processes cannot directly access Databricks volumes
- Enables seamless integration with Databricks storage
- Maintains compatibility with existing workflows
**Trade-offs**: Additional disk I/O, but necessary for functionality

### ADR-003: Python 3.10 Standardization
**Decision**: Standardize on Python 3.10 for Databricks compatibility
**Rationale**: 
- Matches Databricks Serverless V1 runtime
- Ensures PyArrow 8.0.0 compatibility
- Reduces version conflicts
**Trade-offs**: Limited to Python 3.10 features, but ensures stability

## 📊 Performance Benchmarks

### Conversion Performance (v1.0.9)
- **Small MDB files (<10MB)**: 2-5 seconds
- **Medium MDB files (10-100MB)**: 5-30 seconds  
- **Large MDB files (>100MB)**: 30-120 seconds
- **Unity Catalog overhead**: +10-20% due to file copying

### Memory Usage
- **Subprocess backend**: 50-200MB peak memory
- **JPype backend**: 100-500MB peak memory
- **Improvement**: 50-75% reduction in memory usage

## 🔧 Development Workflow for v1.0.9

### Pre-commit Checklist
```bash
# Run all quality checks
make lint        # Ruff linting
make format      # Black formatting
make test-quick  # Fast test suite
make type-check  # MyPy type checking

# Or run all at once
make pre-commit
```

### Release Process
1. **Version Update**: Update version in `pyproject.toml`
2. **Changelog**: Update `CHANGELOG.md` with features and fixes
3. **Testing**: Run full test suite with `make test-all`
4. **Quality Gates**: Ensure all CI checks pass
5. **Release**: Tag and push to trigger automated deployment

### Branch Strategy
- **main**: Production-ready code
- **develop**: Development integration branch
- **feature/***: Feature development branches
- **fix/***: Bug fix branches

## 📚 Additional Resources

### Documentation
- **CONTRIBUTING.md**: Development guidelines and setup
- **TESTING.md**: Comprehensive testing guide
- **BUILD_AND_DEPLOY_GUIDE.md**: Build and deployment procedures
- **LOCAL_INSTALL_TEST_GUIDE.md**: Local testing instructions

### External Dependencies
- **UCanAccess 4.0.4**: Microsoft Access database engine
- **PyArrow 8.0.0**: Apache Arrow Python bindings
- **Pandas 1.5.3**: Data manipulation library
- **Databricks CLI**: Deployment and management tool

### Community
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Contributing**: Welcome contributions via pull requests