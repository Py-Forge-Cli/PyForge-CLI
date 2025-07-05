# PyForge CLI - Local Installation and Testing Guide

This guide covers how to install and test PyForge CLI locally during development and before deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Installation](#development-installation)
3. [Local Package Installation](#local-package-installation)
4. [Testing Installation](#testing-installation)
5. [Functional Testing](#functional-testing)
6. [Troubleshooting](#troubleshooting)
7. [Uninstallation](#uninstallation)

---

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **UV**: Modern Python package manager (recommended)
- **Git**: For cloning the repository
- **Virtual Environment**: For isolated testing

### Installation Tools
```bash
# Check Python version
python --version  # Should be 3.8+

# Install uv if not already installed (macOS with Homebrew)
brew install uv

# Or install uv with curl (cross-platform)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify uv installation
uv --version
```

---

## Development Installation

### 1. Clone Repository
```bash
# Clone the repository
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI

# Or if already cloned, ensure you're in the project directory
cd /path/to/PyForge-CLI
```

### 2. Set Up Development Environment

#### Automated Setup (Recommended)
```bash
# Run the setup script
python scripts/setup_dev_environment.py
```

#### Using Make Commands
```bash
# Complete development setup
make setup-dev
```

#### Manual Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,test,all]"
pip install -r requirements-dev.txt
```

### 3. Verify Development Setup
```bash
# Check installation
pyforge --version

# Test CLI in development mode  
pyforge --help

# Run quick tests
make test-quick
```

---

## Local Package Installation

### Method 1: Install from Built Package (Recommended)

#### Step 1: Build the Package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package with uv
uv build --native-tls

# Verify build
ls -la dist/
# Should see:
# - pyforge_cli-0.2.0-py3-none-any.whl
# - pyforge_cli-0.2.0.tar.gz
```

#### Step 2: Validate Package
```bash
# Add twine if not already available
uv add --dev twine --native-tls

# Check package integrity
uv run twine check dist/*
# Should show: PASSED for both files
```

#### Step 3: Install in Clean Environment
```bash
# Create clean test environment
python -m venv test_install_env
source test_install_env/bin/activate  # On Windows: test_install_env\Scripts\activate

# Install from wheel
pip install dist/pyforge_cli-0.2.0-py3-none-any.whl

# Or install from source distribution
pip install dist/pyforge_cli-0.2.0.tar.gz
```

### Method 2: Editable Development Install
```bash
# Create virtual environment
python -m venv dev_env
source dev_env/bin/activate

# Install in editable mode (changes reflect immediately)
pip install -e .

# Or with uv (in existing environment)
uv pip install -e .
```

### Method 3: Direct Install from Source
```bash
# Create virtual environment
python -m venv source_env
source source_env/bin/activate

# Install directly from current directory
pip install .

# This builds and installs in one step
```

---

## Testing Installation

### 1. Basic Functionality Tests
```bash
# Activate your test environment
source test_install_env/bin/activate

# Test 1: CLI availability
pyforge --help
# Should display full help text

# Test 2: Version check
pyforge --version
# Should show: pyforge, version 0.2.0

# Test 3: List supported formats
pyforge formats
# Should show table with PDF, MDB, DBF, Excel converters
```

### 2. Command Structure Tests
```bash
# Test main commands exist
pyforge convert --help
pyforge info --help
pyforge validate --help
pyforge formats --help

# Test verbose mode
pyforge --verbose formats
```

### 3. Plugin System Tests
```bash
# Verify all plugins load
pyforge formats
# Should show: "Loaded plugins: pdf, mdb, dbf, excel"

# Test converter discovery
pyforge convert --help
# Should show format options
```

### 4. Import Tests
```bash
# Test Python imports
python -c "
import pyforge_cli
print(f'Package version: {pyforge_cli.__version__}')
print(f'Package author: {pyforge_cli.__author__}')
"

# Test submodule imports
python -c "
from pyforge_cli.converters import PDFConverter, MDBConverter
from pyforge_cli.main import cli
print('All imports successful')
"
```

---

## Functional Testing

### 1. Create Test Files
```bash
# Create test directory
mkdir -p test_files
cd test_files

# Create a simple test file for validation
echo "Test content for conversion" > test.txt
```

### 2. PDF Testing (if you have PDF files)
```bash
# Test PDF info (replace with actual PDF file)
pyforge info sample.pdf

# Test PDF validation
pyforge validate sample.pdf

# Test PDF conversion
pyforge convert sample.pdf --format txt
```

### 3. Excel Testing (if you have Excel files)
```bash
# Test Excel info
pyforge info sample.xlsx

# Test Excel conversion
pyforge convert sample.xlsx --format parquet

# Test with specific options
pyforge convert sample.xlsx --format parquet --separate
```

### 4. Database Testing (if you have database files)
```bash
# Test MDB/Access database
pyforge info database.mdb
pyforge convert database.mdb --format parquet

# Test DBF file
pyforge info data.dbf
pyforge convert data.dbf --format parquet
```

### 5. Error Handling Tests
```bash
# Test with non-existent file
pyforge info nonexistent.pdf
# Should show appropriate error message

# Test with unsupported format
pyforge convert test.txt --format parquet
# Should show format not supported message
```

---

## Comprehensive Test Script

Create a test script to automate testing:

```bash
# Create test_installation.sh
cat > test_installation.sh << 'EOF'
#!/bin/bash

echo "🧪 PyForge CLI Installation Test Script"
echo "======================================"

# Test 1: Basic CLI
echo "✅ Testing CLI availability..."
if pyforge --help > /dev/null 2>&1; then
    echo "   ✓ CLI command available"
else
    echo "   ❌ CLI command not found"
    exit 1
fi

# Test 2: Version
echo "✅ Testing version..."
VERSION=$(pyforge --version 2>&1)
if [[ $VERSION == *"0.2.0"* ]]; then
    echo "   ✓ Version: $VERSION"
else
    echo "   ❌ Unexpected version: $VERSION"
fi

# Test 3: Formats
echo "✅ Testing formats command..."
if pyforge formats > /dev/null 2>&1; then
    echo "   ✓ Formats command works"
    PLUGINS=$(pyforge formats 2>&1 | grep "Loaded plugins")
    echo "   ✓ $PLUGINS"
else
    echo "   ❌ Formats command failed"
fi

# Test 4: Python imports
echo "✅ Testing Python imports..."
if python -c "import pyforge_cli; from pyforge_cli.main import cli" 2>/dev/null; then
    echo "   ✓ Python imports successful"
else
    echo "   ❌ Python import failed"
fi

# Test 5: Help commands
echo "✅ Testing help commands..."
COMMANDS=("convert" "info" "validate" "formats")
for cmd in "${COMMANDS[@]}"; do
    if pyforge $cmd --help > /dev/null 2>&1; then
        echo "   ✓ $cmd --help works"
    else
        echo "   ❌ $cmd --help failed"
    fi
done

echo ""
echo "🎉 Installation test completed!"
echo "   Run 'pyforge --help' to get started"
EOF

# Make executable and run
chmod +x test_installation.sh
./test_installation.sh
```

---

## Performance and Memory Testing

### 1. Import Time Test
```bash
# Measure import performance
time python -c "import pyforge_cli"

# Should be under 1 second for good performance
```

### 2. Memory Usage Test
```bash
# Basic memory usage
python -c "
import psutil
import os
import pyforge_cli

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f'Memory usage after import: {memory_mb:.1f} MB')
"
```

### 3. CLI Startup Time
```bash
# Measure CLI startup time
time pyforge --help > /dev/null
```

---

## Testing Different Python Versions

### Using pyenv (if available)
```bash
# Test with different Python versions
for version in 3.8.10 3.9.7 3.10.5 3.11.3 3.12.0; do
    if pyenv versions | grep -q $version; then
        echo "Testing with Python $version"
        pyenv shell $version
        python -m venv test_py_${version//./_}
        source test_py_${version//./_}/bin/activate
        pip install dist/pyforge_cli-0.2.0-py3-none-any.whl
        pyforge --version
        deactivate
    fi
done
```

### Using Docker
```bash
# Test with different Python versions using Docker
cat > test_docker.sh << 'EOF'
#!/bin/bash
for version in 3.8 3.9 3.10 3.11 3.12; do
    echo "Testing Python $version"
    docker run --rm -v $(pwd):/app python:$version-slim bash -c "
        cd /app && 
        pip install dist/pyforge_cli-0.2.0-py3-none-any.whl && 
        pyforge --version
    "
done
EOF

chmod +x test_docker.sh
./test_docker.sh
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Command Not Found
```bash
# Problem: pyforge command not found
# Solution: Check if installed correctly
pip list | grep pyforge
which pyforge

# If not found, reinstall
pip uninstall pyforge-cli
pip install dist/pyforge_cli-0.2.0-py3-none-any.whl
```

#### 2. Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Check Python path
python -c "
import sys
print('Python path:')
for path in sys.path:
    print(f'  {path}')
"

# Reinstall if needed
pip install --force-reinstall dist/pyforge_cli-0.2.0-py3-none-any.whl
```

#### 3. Dependency Issues
```bash
# Problem: Missing dependencies
# Solution: Install with dependencies
pip install --upgrade dist/pyforge_cli-0.2.0-py3-none-any.whl

# Or check what's missing
pip check
```

#### 4. Permission Issues
```bash
# Problem: Permission denied during installation
# Solution: Use --user flag
pip install --user dist/pyforge_cli-0.2.0-py3-none-any.whl

# Or fix virtual environment permissions
chmod -R 755 test_install_env/
```

#### 5. Version Conflicts
```bash
# Problem: Conflicting package versions
# Solution: Create fresh environment
rm -rf conflicted_env
python -m venv fresh_env
source fresh_env/bin/activate
pip install dist/pyforge_cli-0.2.0-py3-none-any.whl
```

### Debug Information Collection
```bash
# Collect system information for debugging
cat > debug_info.sh << 'EOF'
#!/bin/bash
echo "=== Debug Information ==="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Virtual env: $VIRTUAL_ENV"
echo "Platform: $(uname -a)"
echo ""
echo "=== Package Information ==="
pip show pyforge-cli
echo ""
echo "=== Dependencies ==="
pip list
echo ""
echo "=== CLI Test ==="
pyforge --version 2>&1
EOF

chmod +x debug_info.sh
./debug_info.sh > debug_output.txt
```

### Log Analysis
```bash
# Enable verbose logging for debugging
export PYFORGE_DEBUG=1
pyforge --verbose info nonexistent.file 2>&1 | tee debug.log
```

---

## Uninstallation

### Clean Uninstall
```bash
# Uninstall the package
pip uninstall pyforge-cli

# Remove virtual environments
rm -rf test_install_env dev_env source_env

# Clean build artifacts
rm -rf dist/ build/ *.egg-info/
rm -rf .venv/

# Remove test files
rm -rf test_files/
rm -f test_installation.sh debug_info.sh test_docker.sh
```

### Verify Uninstallation
```bash
# Check that command is no longer available
pyforge --version 2>&1 | grep "command not found"

# Check Python imports fail
python -c "import pyforge_cli" 2>&1 | grep "No module named"

# Verify pip list
pip list | grep -i pyforge
# Should show no results
```

---

## Best Practices

### 1. Development Workflow
```bash
# Always test in clean environment before release
rm -rf test_env && python -m venv test_env
source test_env/bin/activate
pip install dist/pyforge_cli-0.2.0-py3-none-any.whl
./test_installation.sh
deactivate && rm -rf test_env
```

### 2. Continuous Testing
```bash
# Add to your development script
cat > dev_test.sh << 'EOF'
#!/bin/bash
set -e

echo "🔄 Running development tests..."

# Build package
uv build --native-tls

# Validate package
uv run twine check dist/*

# Test installation
python -m venv temp_test
source temp_test/bin/activate
pip install dist/pyforge_cli-0.2.0-py3-none-any.whl
pyforge --version
pyforge formats
deactivate
rm -rf temp_test

echo "✅ All tests passed!"
EOF

chmod +x dev_test.sh
```

### 3. Pre-commit Testing
```bash
# Test before every commit
git add dev_test.sh
echo "./dev_test.sh" >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## Integration with CI/CD

### GitHub Actions Integration
```yaml
# Add to .github/workflows/test-install.yml
name: Test Local Installation

on: [push, pull_request]

jobs:
  test-install:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      run: pip install uv
    
    - name: Build package
      run: uv build
    
    - name: Test installation
      run: |
        python -m venv test_env
        source test_env/bin/activate  # On Windows: test_env\Scripts\activate
        pip install dist/*.whl
        pyforge --version
        pyforge formats
```

---

## Quick Reference

### Essential Commands
```bash
# Build and test workflow
uv build --native-tls
uv run twine check dist/*
python -m venv test && source test/bin/activate
pip install dist/pyforge_cli-0.2.0-py3-none-any.whl
pyforge --version && pyforge formats
deactivate && rm -rf test
```

### One-liner Test
```bash
# Complete test in one command
uv build && python -m venv quick_test && source quick_test/bin/activate && pip install dist/*.whl && pyforge --version && deactivate && rm -rf quick_test
```

---

*This guide ensures comprehensive testing of PyForge CLI installations across different environments and scenarios. Follow these procedures before any release to ensure reliability.*