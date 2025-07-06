# Contributing to PyForge CLI

Thank you for your interest in contributing to PyForge CLI! We welcome contributions from the community.

## Getting Started

### Prerequisites
- Python 3.8 or higher (Python 3.10.12 recommended for Databricks Serverless V1 compatibility)
- Git
- For MDB/Access file support: `mdbtools` (Linux/macOS only)
- For PySpark/Databricks tests: Java 8 or 11

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PyForge-CLI.git
   cd PyForge-CLI
   ```

2. **Run the automated setup script (recommended)**
   ```bash
   python scripts/setup_dev_environment.py
   ```

   This will:
   - Create a virtual environment (`.venv`)
   - Install all dependencies including dev, test, and optional extras
   - Set up pre-commit hooks (if configured)
   - Create a `.env` template file
   - Check for Java installation (needed for PySpark 3.5.0 tests)

3. **Or set up manually**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -e ".[dev,test,all]"
   pip install -r requirements-dev.txt
   
   # Verify installation
   pyforge --version
   ```

4. **Alternative: Use Make commands**
   ```bash
   make setup-dev  # Complete development setup
   make help       # See all available commands
   ```

## Development Workflow

### Running Tests

We provide multiple ways to run tests:

```bash
# Using Make commands (recommended)
make test           # Run tests
make test-quick     # Run quick tests (skip slow/integration)
make test-all       # Run all tests with full reporting
make test-cov       # Run tests with coverage
make test-report    # Generate test report summary

# Using pytest directly
pytest                      # Run all tests
pytest -v                   # Verbose output
pytest --cov=pyforge_cli    # With coverage
pytest -k "not slow"        # Skip slow tests
pytest tests/test_csv_converter.py  # Specific test file
```

#### Test Categories
Tests are marked with categories:
- `slow` - Tests that take >1 second
- `integration` - Tests requiring external resources
- `pyspark` - Tests requiring Java/PySpark 3.5.0

### Code Quality

We maintain high code quality standards using automated tools:

```bash
# Using Make commands (recommended)
make lint          # Run linting with ruff
make format        # Format code with black
make type-check    # Run type checking with mypy
make pre-commit    # Run all checks before committing

# Or run tools directly
black src/ tests/              # Format code
ruff check src/ tests/          # Lint code
mypy src/                       # Type checking

# Fix common issues automatically
ruff check --fix src/ tests/    # Auto-fix linting issues
```

### Testing Your Changes

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Test the CLI installation
pyforge --version
pyforge --help

# Test specific conversions
pyforge convert test_files/sample.xlsx
pyforge convert test_files/document.pdf --verbose

# Run quick test suite before committing
make test-quick
```

### Test Environment Management

For comprehensive testing with all dependencies:

```bash
# Create dedicated test environment
make test-env

# Run full test suite with reporting
make test-all

# This generates:
# - HTML report: pytest_html_report.html
# - Coverage report: htmlcov/index.html
# - JUnit XML: junit/test-results.xml
# - JSON report: test-report.json
```

## Contributing Guidelines

### Code Style
- We use [Black](https://black.readthedocs.io/) for code formatting
- We use [Ruff](https://docs.astral.sh/ruff/) for linting
- We use [mypy](https://mypy.readthedocs.io/) for type checking
- Follow PEP 8 guidelines
- Write clear, descriptive variable and function names

### Commit Messages
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

feat(excel): add support for XLSM files
fix(dbf): handle encoding detection errors
docs(readme): update installation instructions
test(mdb): add tests for large database files
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Test additions/modifications
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests for new functionality
   - Ensure all tests pass
   - Update documentation if needed

3. **Test thoroughly**
   ```bash
   # Run the full test suite
   pytest

   # Test with different file types
   pyforge convert test.xlsx
   pyforge convert test.pdf
   pyforge convert test.mdb
   ```

4. **Submit a pull request**
   - Use a clear, descriptive title
   - Provide detailed description of changes
   - Reference any related issues
   - Ensure CI checks pass

### Adding New Converters

To add support for a new file format:

1. **Create converter class** in `src/pyforge_cli/converters/`
   ```python
   from .base import BaseConverter
   
   class NewFormatConverter(BaseConverter):
       def convert(self, input_file, output_file=None, **kwargs):
           # Implementation
           pass
   ```

2. **Register the converter** in `src/pyforge_cli/plugins/loader.py`

3. **Add tests** in `tests/test_new_format_converter.py`

4. **Update documentation** in README.md and docs/

### Reporting Issues

When reporting issues, please include:

- **Environment details**: OS, Python version, PyForge CLI version
- **Steps to reproduce**: Clear, minimal example
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Sample files**: If applicable (ensure no sensitive data)

### Feature Requests

For feature requests:

- **Use case**: Describe the problem you're trying to solve
- **Proposed solution**: How you think it should work
- **Alternative solutions**: Other approaches you've considered
- **Impact**: Who would benefit from this feature

## Development Guidelines

### Architecture Principles

1. **Plugin-based**: New converters should be easily pluggable
2. **Error handling**: Graceful handling of corrupt/invalid files
3. **Performance**: Handle large files efficiently
4. **User experience**: Clear progress indicators and error messages
5. **Cross-platform**: Support Windows, macOS, and Linux

### Testing Requirements

- **Unit tests**: Test individual components
- **Integration tests**: Test complete conversion workflows
- **Edge cases**: Handle corrupt files, edge cases gracefully
- **Performance tests**: Ensure reasonable performance with large files

### Documentation

- **Docstrings**: All public functions should have clear docstrings
- **Type hints**: Use type hints for better code clarity
- **Examples**: Include usage examples in documentation
- **README**: Keep README.md up to date with new features

## Release Process

We follow semantic versioning (SemVer):

- **Major** (x.0.0): Breaking changes
- **Minor** (0.x.0): New features, backward compatible
- **Patch** (0.0.x): Bug fixes, backward compatible

## Community

- **Be respectful**: Follow our Code of Conduct
- **Be helpful**: Help other contributors and users
- **Be patient**: Reviews take time, and feedback is meant to be constructive

## Questions?

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: dd.santosh@gmail.com for private matters

Thank you for contributing to PyForge CLI! 🚀