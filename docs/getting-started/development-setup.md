# Development Setup Guide

This guide covers setting up a local development environment for PyForge CLI following Python best practices.

## Quick Start

For the fastest setup, use our automated script:

```bash
# Clone the repository
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI

# Run the setup script
python scripts/setup_dev_environment.py

# Or use make
make setup-dev
```

## Manual Setup

### 1. Create Virtual Environment

Following Python best practices, we use `.venv` as the standard virtual environment name:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install package with all extras
pip install -e ".[dev,test,all,databricks]"
# Note: This installs PySpark 3.5.0 for Databricks compatibility

# Install additional dev dependencies
pip install -r requirements-dev.txt
```

### 3. Verify Installation

```bash
# Check the CLI is working
pyforge --version

# Run quick tests
pytest -k "not slow and not integration"
```

## Using Make Commands

We provide comprehensive Makefile commands for common tasks:

### Environment Management

```bash
make venv          # Create virtual environment
make venv-clean    # Remove virtual environment
make venv-activate # Show activation instructions
make setup-dev     # Complete dev setup
make test-env      # Create dedicated test environment
```

### Development Workflow

```bash
make test         # Run tests
make test-quick   # Run quick tests (skip slow/integration)
make test-all     # Run all tests with full reporting
make test-cov     # Run tests with coverage
make lint         # Run linting
make format       # Format code
make type-check   # Run type checking
```

### Test Reporting

When you run `make test-all`, it generates:
- HTML Report: `pytest_html_report.html`
- XML Report: `junit/test-results.xml`
- JSON Report: `test-report.json`
- Coverage HTML: `htmlcov/index.html`

## Environment Variables

Create a `.env` file for local configuration:

```bash
# Development settings
DEBUG=true
LOG_LEVEL=DEBUG

# Test settings
PYTEST_WORKERS=auto
PYTEST_TIMEOUT=300

# Java settings (for PySpark 3.5.0)
JAVA_HOME=/path/to/java/home  # Java 8 or 11 required

# Databricks settings (optional)
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=your-token
```

## Testing Best Practices

### Test Environment Isolation

We use separate environments for different purposes:
- `.venv` - Main development environment
- `.testenv` - Dedicated test environment with all test dependencies

### Running Tests

```bash
# Quick tests for rapid feedback
make test-quick

# Full test suite with reporting
make test-all

# Specific test file
pytest tests/test_csv_converter.py

# Specific test
pytest tests/test_csv_converter.py::TestCSVConverter::test_basic_csv_conversion
```

### Test Categories

Tests are categorized with markers:
- `slow` - Tests that take >1 second
- `integration` - Integration tests requiring external resources
- `pyspark` - Tests requiring PySpark 3.5.0/Java (Databricks Runtime 14.3 LTS compatible)

Skip categories:
```bash
pytest -k "not slow and not integration"
```

## Pre-commit Hooks

If using pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## IDE Integration

### VS Code

1. Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
2. Select "Python: Select Interpreter"
3. Choose `./.venv/bin/python`

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing Environment"
4. Choose `./.venv/bin/python`

## Troubleshooting

### Virtual Environment Not Found

```bash
# Ensure you're in the project root
pwd  # Should show /path/to/PyForge-CLI

# Check if .venv exists
ls -la .venv/

# If not, create it
make venv
```

### Import Errors

```bash
# Ensure package is installed in editable mode
pip install -e .

# Verify installation
pip list | grep pyforge-cli
```

### Test Failures

```bash
# Run with verbose output
pytest -vvs tests/failing_test.py

# Check test environment
which python  # Should point to .venv/bin/python
```

## Directory Structure

```
PyForge-CLI/
├── .venv/              # Main development virtual environment
├── .testenv/           # Dedicated test environment
├── src/                # Source code
│   └── pyforge_cli/
├── tests/              # Test files
├── docs/               # Documentation
├── scripts/            # Utility scripts
│   └── setup_dev_environment.py
├── requirements-dev.txt # Development dependencies
├── pyproject.toml      # Project configuration
├── Makefile            # Development commands
└── .gitignore          # Git ignore patterns
```

## Best Practices

1. **Always use virtual environments** - Never install packages globally
2. **Keep environments clean** - Use separate environments for different purposes
3. **Pin dependencies** - Use exact versions in requirements files
4. **Use editable installs** - Install with `-e` for development
5. **Run tests frequently** - Use `make test-quick` for rapid feedback
6. **Update regularly** - Keep dependencies and tools up to date

## Next Steps

- Read the [Contributing Guide](../about/contributing.md)
- Check out the [API Documentation](../api/index.md)
- Learn about [Extension Development](../api/extension-developer-guide.md)