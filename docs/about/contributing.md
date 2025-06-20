# Contributing to PyForge CLI

We welcome contributions! This guide explains how to contribute to the project.

## Ways to Contribute

- 🐛 **Report Bugs**: [Create an issue](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)
- 💡 **Suggest Features**: [Start a discussion](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions)
- 📖 **Improve Documentation**: Submit pull requests
- 🔧 **Code Contributions**: Fix bugs or add features

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,test]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pyforge_cli
```

## Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type check
mypy src
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Code of Conduct

Please be respectful and inclusive in all interactions.

## Questions?

Feel free to ask questions in [GitHub Discussions](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions).