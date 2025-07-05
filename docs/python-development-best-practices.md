# Python Local Development and Testing Environment Best Practices

## Executive Summary

This document outlines industry-standard best practices for Python local development and testing environments based on research of popular Python projects, PEPs, and current ecosystem standards as of 2025.

## 1. Virtual Environment Naming Conventions

### Recommended Names
Based on official Python documentation and community consensus:

- **`.venv`** (Preferred) - Official Python documentation recommendation
  - Hidden by default in file explorers and shells
  - Explains purpose clearly
  - Prevents clashing with `.env` environment variable files

- **`venv`** - Widely used convention
  - Readily available in ignore file templates
  - Good for consistency across teams

### Names to Avoid
- `env` - Can be confused with environment variables
- Custom names - Makes `.gitignore` configuration harder
- Version-specific names (e.g., `venv38`) - Reduces portability

## 2. Directory Structure for Test Environments

### Modern Python Project Structure (2025)

```
my-python-project/
├── .venv/                    # Virtual environment (ignored)
├── src/                      # Source code
│   └── my_package/
│       ├── __init__.py
│       └── module.py
├── tests/                    # Test suite
│   ├── unit/
│   ├── integration/
│   └── functional/
├── docs/                     # Documentation
├── notebooks/                # Jupyter notebooks
│   └── testing/             # Test notebooks
├── pyproject.toml           # Project configuration
├── .gitignore               # Git ignore patterns
├── .pre-commit-config.yaml  # Pre-commit hooks
└── README.md                # Project documentation
```

### Key Principles
- **Separation of Concerns**: Clear separation between source, tests, and documentation
- **Src Layout**: Using `src/` prevents accidental imports from the project root
- **Test Organization**: Group tests by type (unit, integration, functional)
- **Configuration Centralization**: Use `pyproject.toml` as single source of truth

## 3. Requirements Management Best Practices

### Modern Approach with pyproject.toml

```toml
[project]
dependencies = [
    "pandas>=1.5.0,<2.0",  # Abstract dependencies with ranges
    "click>=8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
test = [
    "pytest>=7.0.0",
    "pytest-mock>=3.10.0",
]
docs = [
    "mkdocs>=1.4.0",
    "mkdocs-material>=9.0.0",
]

[dependency-groups]  # PEP 735 (2025)
dev = ["bandit>=1.7.10", "twine>=6.1.0"]
test-pyspark = ["pyspark==3.5.2", "findspark>=2.0.1"]
```

### Requirements Files Strategy
1. **Development**: Abstract dependencies in `pyproject.toml`
2. **Production**: Pin exact versions in `requirements.txt` for deployments
3. **Lock Files**: Use `uv.lock` or `poetry.lock` for reproducible environments

### Best Practice Pattern
```bash
# Development installation
pip install -e ".[dev,test]"

# Production deployment
pip install -r requirements.txt  # Pinned versions
```

## 4. Git Ignore Patterns

### Comprehensive Python .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
.venv/
venv/
ENV/
env/
.env

# Testing
.tox/
.nox/
.pytest_cache/
.coverage
coverage.xml
htmlcov/
.hypothesis/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json
.pytype/
.pyre/

# Distribution
build/
dist/
*.egg-info/
.eggs/

# Jupyter
.ipynb_checkpoints/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
uv.lock
.setuptools_scm/
```

## 5. Test Environment Management Tools

### Tool Comparison (2025)

| Tool | Use Case | Pros | Cons |
|------|----------|------|------|
| **tox** | Multi-version testing | - Declarative config<br>- Industry standard<br>- CI/CD friendly | - Slower with venvs<br>- Limited flexibility |
| **nox** | Complex test scenarios | - Python-based config<br>- Flexible workflows<br>- Conditional logic | - More verbose<br>- Less standardized |
| **pytest** | Test execution | - Feature-rich<br>- Plugin ecosystem<br>- Fast | - Not for env management |
| **uv** | Modern tooling | - Very fast<br>- Built-in caching<br>- Modern UX | - Newer tool<br>- Less ecosystem |

### Recommended Approach
- **Simple projects**: Use `uv` or `pytest` directly
- **Libraries**: Use `tox` for multi-version testing
- **Complex scenarios**: Use `nox` for programmatic control
- **Modern workflow**: Combine `uv` with `just` for task automation

## 6. Avoiding Environment Recreation

### Strategies

1. **Use Tool Caching**
   ```bash
   # uv automatically caches environments
   uv sync  # Fast on subsequent runs
   ```

2. **Named Environments**
   ```bash
   # Create once, activate many times
   python -m venv .venv
   source .venv/bin/activate  # Reuse existing
   ```

3. **Tox Environment Reuse**
   ```ini
   [testenv]
   recreate = False  # Don't recreate unless needed
   ```

4. **Check Before Creating**
   ```bash
   # Script pattern
   if [ ! -d ".venv" ]; then
       python -m venv .venv
   fi
   ```

## 7. Environment Activation Best Practices

### Manual Activation
```bash
# Unix/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Deactivation (all platforms)
deactivate
```

### Automated with direnv
```bash
# .envrc file
layout python3
# or for pyenv users
layout pyenv 3.11.0
```

Benefits:
- Automatic activation on directory entry
- Automatic deactivation on exit
- No manual commands needed
- Security through manual approval

### IDE Integration
- **VS Code**: Automatically detects `.venv`
- **PyCharm**: Configure interpreter to use `.venv`
- **Both**: Support workspace-specific settings

## 8. Development Workflow Patterns

### Popular Python Project Examples

**Flask** (Minimalist Web Framework):
```
flask/
├── src/flask/          # Source code
├── tests/              # Test suite
├── docs/               # Documentation
├── examples/           # Example applications
├── pyproject.toml      # Modern config
└── .pre-commit-config.yaml
```

**Django** (Full-Featured Web Framework):
```
django-project/
├── manage.py
├── myproject/          # Project config
├── apps/               # Django apps
│   ├── app1/
│   └── app2/
├── requirements/       # Separated requirements
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
└── .env.example
```

**Pandas** (Data Science Library):
```
pandas/
├── pandas/             # Source code
├── pandas/tests/       # Integrated tests
├── doc/                # Sphinx documentation
├── scripts/            # Utility scripts
├── pyproject.toml
└── environment.yml     # Conda environment
```

## 9. Specific Recommendations for PyForge-CLI

Based on the analysis, here are specific recommendations for the PyForge-CLI project:

### 1. Virtual Environment
- Standardize on `.venv` as the virtual environment name
- Update documentation to reflect this convention
- Add clear setup instructions in README

### 2. Test Environment Management
- Continue using `pytest` for test execution
- Consider `tox` for testing across Python 3.8-3.12
- Use `uv` for fast local development cycles

### 3. Requirements Organization
- Keep current `pyproject.toml` structure
- Consider adding `requirements/` directory for deployment scenarios:
  ```
  requirements/
  ├── base.txt      # Core dependencies (from pyproject.toml)
  ├── dev.txt       # Development dependencies
  ├── test.txt      # Test-only dependencies
  └── prod.txt      # Production pinned versions
  ```

### 4. Development Workflow Enhancement
```bash
# One-time setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test]"

# Daily development (with direnv)
cd /path/to/pyforge-cli  # Auto-activates
pytest                    # Run tests
pyforge convert ...       # Test CLI

# CI/CD testing
tox -e py38,py39,py310,py311,py312
```

### 5. Testing Structure Enhancement
- Current structure is good, consider adding:
  ```
  tests/
  ├── unit/           # Fast, isolated tests
  ├── integration/    # Component interaction tests
  ├── functional/     # End-to-end tests
  ├── fixtures/       # Shared test data
  └── benchmarks/     # Performance tests
  ```

## 10. Modern Python Development Stack (2025)

### Recommended Tool Stack
1. **Package Management**: `uv` or `poetry`
2. **Virtual Environments**: Built-in `venv` with `.venv` name
3. **Testing**: `pytest` with `pytest-cov`
4. **Linting**: `ruff` (fast, combines multiple tools)
5. **Formatting**: `ruff format` or `black`
6. **Type Checking**: `mypy` with strict mode
7. **Pre-commit**: `pre-commit` hooks
8. **Task Runner**: `just` or `make`
9. **Documentation**: `mkdocs` with `mkdocs-material`
10. **CI/CD**: GitHub Actions with `tox` or `nox`

### Environment Variables Best Practice
```bash
# .env.example (committed)
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=your-api-key-here

# .env (not committed)
DATABASE_URL=postgresql://real:pass@prod/db
API_KEY=actual-secret-key
```

## Conclusion

The Python ecosystem has evolved significantly, with modern tools like `uv` offering speed improvements while maintaining compatibility with traditional workflows. The key is to choose tools that match your project's complexity and team's needs while following established conventions for maximum compatibility and developer experience.