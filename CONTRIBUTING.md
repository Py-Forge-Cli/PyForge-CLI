# Contributing to PyForge CLI

Thank you for your interest in contributing to PyForge CLI! We welcome contributions from the community.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- For MDB/Access file support: `mdbtools` (Linux/macOS only)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PyForge-CLI.git
   cd PyForge-CLI
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pyforge_cli

# Run specific test file
pytest tests/test_specific.py
```

### Code Quality
We use several tools to maintain code quality:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Testing Your Changes
```bash
# Install in development mode
pip install -e .

# Test the CLI
pyforge --help
pyforge convert path/to/test/file.xlsx
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