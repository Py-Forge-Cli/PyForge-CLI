# PyForge CLI - Testing Guide

Comprehensive guide for testing PyForge CLI during development and before releases.

## 🚀 Quick Start

### Environment Setup

The recommended way to set up a testing environment:

```bash
# Clone and enter the repository
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI

# Automated setup (recommended)
python scripts/setup_dev_environment.py

# Or use make commands
make setup-dev      # Development environment
make test-env       # Dedicated test environment
```

### Running Tests

```bash
# Quick tests (recommended for development)
make test-quick

# Full test suite with reporting
make test-all

# Specific test categories
pytest -k "not slow and not integration"
pytest -m "not pyspark"  # Skip PySpark tests if Java not installed
```

## 📊 Test Organization

Tests are organized into categories:

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests that require external resources
- **Slow Tests**: Tests that take >1 second (marked with `@pytest.mark.slow`)
- **PySpark Tests**: Tests requiring Java/PySpark (marked with `@pytest.mark.pyspark`)

### Test Structure

```
tests/
├── test_csv_converter.py        # CSV conversion tests
├── test_pdf_converter.py        # PDF conversion tests
├── test_excel_converter.py      # Excel conversion tests
├── test_database_converters.py  # MDB/DBF conversion tests
├── test_xml_multi_document.py   # XML conversion tests
├── test_extension_system.py     # Extension system tests
└── conftest.py                  # Shared fixtures
```

## 🧪 Test Commands

### Using Make (Recommended)

```bash
# Environment Management
make venv           # Create virtual environment
make test-env       # Create dedicated test environment

# Running Tests
make test           # Run standard tests
make test-quick     # Skip slow/integration tests
make test-all       # Full suite with all reports
make test-cov       # Run with coverage analysis
make test-report    # Generate test summary

# Code Quality
make lint           # Run linting
make format         # Format code
make type-check     # Type checking
make pre-commit     # All checks before commit
```

### Using pytest Directly

```bash
# Basic test runs
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest -vv                      # Very verbose
pytest --tb=short               # Short traceback

# Selective testing
pytest tests/test_csv_converter.py              # Single file
pytest -k "test_csv_conversion"                  # Pattern matching
pytest -m "not slow"                            # Exclude markers

# With coverage
pytest --cov=pyforge_cli                        # Basic coverage
pytest --cov=pyforge_cli --cov-report=html      # HTML report
pytest --cov=pyforge_cli --cov-report=term-missing  # Terminal report

# Parallel execution (if pytest-xdist installed)
pytest -n auto                  # Use all CPU cores
pytest -n 4                     # Use 4 workers
```

## 📈 Test Reporting

When you run `make test-all`, the following reports are generated:

### 1. HTML Test Report
- **File**: `pytest_html_report.html`
- **Contents**: Detailed test results with pass/fail status
- **Usage**: Open in browser for interactive viewing

### 2. Coverage Report
- **Directory**: `htmlcov/`
- **Main file**: `htmlcov/index.html`
- **Contents**: Line-by-line coverage analysis
- **Usage**: Identify untested code paths

### 3. JUnit XML Report
- **File**: `junit/test-results.xml`
- **Contents**: Machine-readable test results
- **Usage**: CI/CD integration

### 4. JSON Report
- **File**: `test-report.json`
- **Contents**: Detailed test metrics
- **Usage**: Custom analysis and reporting

### Viewing Reports

```bash
# Generate all reports
make test-all

# View summary
make test-report

# Open HTML reports (macOS)
open pytest_html_report.html
open htmlcov/index.html

# Open HTML reports (Linux)
xdg-open pytest_html_report.html
xdg-open htmlcov/index.html
```

## 🔍 Testing Specific Features

### PDF Conversion Testing

```bash
# Create test PDF
echo "Test content" | pandoc -o test.pdf  # If pandoc installed

# Or use existing PDF
cp ~/Downloads/sample.pdf test.pdf

# Test conversions
pyforge validate test.pdf
pyforge info test.pdf
pyforge convert test.pdf
pyforge convert test.pdf --pages "1-5"
pyforge convert test.pdf --metadata
```

### Excel Conversion Testing

```bash
# Test multi-sheet Excel
pyforge convert test_data/multi_sheet.xlsx
pyforge convert test_data/multi_sheet.xlsx --interactive
pyforge convert test_data/multi_sheet.xlsx --sheets "Sheet1,Sheet3"
pyforge convert test_data/multi_sheet.xlsx --merge-sheets
```

### Database File Testing

```bash
# Test Access database
pyforge convert test_data/sample.mdb
pyforge info test_data/sample.mdb

# Test DBF file
pyforge convert test_data/legacy.dbf
pyforge convert test_data/legacy.dbf --encoding cp1252
```

### CSV Testing

```bash
# Test various CSV formats
pyforge convert test_data/comma.csv
pyforge convert test_data/semicolon.csv
pyforge convert test_data/tab_separated.tsv
pyforge convert test_data/international.csv --verbose
```

### XML Testing

```bash
# Test XML conversion strategies
pyforge convert test_data/catalog.xml
pyforge convert test_data/complex.xml --preview-schema
pyforge convert test_data/nested.xml --flatten-strategy aggressive
pyforge convert test_data/arrays.xml --array-handling expand
```

## 🐛 Debugging Tests

### Running Specific Tests

```bash
# Run single test method
pytest tests/test_csv_converter.py::TestCSVConverter::test_basic_csv_conversion -v

# Run with debugging output
pytest -vvs tests/test_pdf_converter.py

# Drop into debugger on failure
pytest --pdb tests/test_excel_converter.py

# Show local variables on failure
pytest -l tests/test_database_converters.py
```

### Common Issues

#### 1. Import Errors
```bash
# Ensure package is installed
pip install -e .

# Check import
python -c "import pyforge_cli; print(pyforge_cli.__version__)"
```

#### 2. PySpark Tests Failing
```bash
# Check Java installation
java -version

# Skip PySpark tests
pytest -m "not pyspark"
```

#### 3. Slow Tests
```bash
# Skip slow tests during development
make test-quick

# Or
pytest -m "not slow"
```

## ✅ Pre-Release Checklist

Before releasing, ensure all these pass:

- [ ] **Environment Setup**: `make setup-dev` completes successfully
- [ ] **All Tests Pass**: `make test-all` shows no failures
- [ ] **Coverage**: Maintain >80% coverage
- [ ] **Linting**: `make lint` shows no errors
- [ ] **Type Checking**: `make type-check` passes
- [ ] **Documentation**: All new features documented
- [ ] **Integration Tests**: Test with real files of each format
- [ ] **Performance**: Large file handling works properly
- [ ] **Cross-platform**: Test on Windows, macOS, Linux

## 🔄 Continuous Integration

Our CI pipeline runs automatically on every push:

1. **Test Matrix**: Python 3.8-3.10 on Ubuntu/macOS/Windows
2. **Coverage**: Reports sent to Codecov
3. **Artifacts**: Test reports uploaded for review
4. **Security**: Bandit and safety checks

### Local CI Simulation

```bash
# Run CI-like checks locally
make pre-commit

# Or manually
make format
make lint
make type-check
make test
```

## 📊 Performance Testing

### Memory Usage

```bash
# Monitor memory during conversion
pytest tests/test_csv_converter.py::test_large_file_conversion --memprof
```

### Execution Time

```bash
# Profile slow tests
pytest --durations=10

# Time specific operations
python -m cProfile -o profile.stats $(which pyforge) convert large_file.csv
```

## 🎯 Test-Driven Development

When adding new features:

1. **Write tests first**
   ```python
   def test_new_feature():
       # Arrange
       converter = NewConverter()
       
       # Act
       result = converter.convert("input.file")
       
       # Assert
       assert result.success
       assert Path("output.parquet").exists()
   ```

2. **Run tests (they should fail)**
   ```bash
   pytest tests/test_new_feature.py -v
   ```

3. **Implement feature**

4. **Run tests again (they should pass)**
   ```bash
   pytest tests/test_new_feature.py -v
   ```

5. **Check coverage**
   ```bash
   pytest tests/test_new_feature.py --cov=pyforge_cli.converters.new_converter
   ```

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [Test artifacts in CI](.github/workflows/ci.yml)
- [Development Setup Guide](docs/getting-started/development-setup.md)

Happy testing! 🧪