# PyPI Publishing Guide for PyForge CLI

## Current Status Analysis

### ✅ What We Have (Good)
- **src/ layout** - Already following modern best practice
- **pyproject.toml** - Modern Python packaging configuration
- **Organized tests/** - Proper test structure
- **Documentation** - README, docs/, etc.
- **Version control** - Git with proper history

### ❌ What's Missing for PyPI
- **LICENSE file** - Required for open source
- **CONTRIBUTING.md** - Community guidelines
- **SECURITY.md** - Security policy
- **MANIFEST.in** - Control what gets included in package
- **GitHub workflows** - CI/CD automation
- **Updated author info** - Real contact details
- **Package classifiers** - Proper categorization

## PyPI Publishing Process

### 1. Account Setup
```bash
# Create accounts on both TestPyPI and PyPI
# https://test.pypi.org/account/register/
# https://pypi.org/account/register/

# Enable 2FA (required as of 2024)
```

### 2. Build Tools Setup
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the built package
twine check dist/*
```

### 3. Test on TestPyPI First
```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ pyforge-cli
```

### 4. Publish to PyPI
```bash
# Upload to real PyPI
twine upload dist/*
```

## Modern Open Source Project Structure (2024)

### Recommended Structure
```
pyforge-cli/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Continuous Integration
│   │   ├── publish.yml         # Automated PyPI publishing
│   │   └── security.yml        # Security scanning
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                       # Documentation
├── src/
│   └── pyforge_cli/           # Package name should match PyPI name
│       ├── __init__.py
│       ├── main.py
│       ├── converters/
│       ├── detectors/
│       ├── plugins/
│       └── readers/
├── tests/                     # Test suite
├── .gitignore                # Git ignore rules
├── .pre-commit-config.yaml   # Pre-commit hooks
├── LICENSE                   # Required for open source
├── README.md                 # Project description
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── SECURITY.md             # Security policy
├── CODE_OF_CONDUCT.md      # Community standards
├── MANIFEST.in             # Package inclusion rules
├── pyproject.toml          # Modern Python configuration
├── requirements-dev.txt    # Development dependencies
└── tox.ini                # Testing configuration
```

## pyproject.toml Updates Needed

### Current Issues
1. **Author info** - Placeholder values
2. **Repository URLs** - Generic placeholders
3. **Missing classifiers** - Package categorization
4. **Missing dependencies** - Development tools
5. **Build configuration** - Missing options

### Required Updates
```toml
[project]
name = "pyforge-cli"
version = "0.2.0"
description = "A powerful CLI tool for data format conversion and synthetic data generation"
authors = [
    {name = "Santosh Dandey", email = "dd.santosh@gmail.com"},
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"

classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Database :: Database Engines/Servers",
    "Topic :: Office/Business",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Archiving :: Conversion",
    "Topic :: Text Processing :: Markup",
    "Topic :: Utilities",
]

keywords = ["cli", "data", "conversion", "pdf", "csv", "parquet", "excel", "database", "mdb", "dbf"]

[project.urls]
Homepage = "https://github.com/Py-Forge-Cli/PyForge-CLI"
Repository = "https://github.com/Py-Forge-Cli/PyForge-CLI"
Issues = "https://github.com/Py-Forge-Cli/PyForge-CLI/issues"
Documentation = "https://github.com/Py-Forge-Cli/PyForge-CLI/blob/main/docs"
Changelog = "https://github.com/Py-Forge-Cli/PyForge-CLI/blob/main/CHANGELOG.md"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
    "build>=0.10.0",
    "twine>=4.0.0",
]
```

## GitHub Actions for Automated Publishing

### Benefits of Trusted Publishers (2024)
- **No API tokens** - More secure
- **Automatic publishing** - On release tags
- **PyPI integration** - Direct GitHub → PyPI

### Setup Process
1. **Configure on PyPI**: Add GitHub repository as trusted publisher
2. **GitHub workflow**: Automated build and publish
3. **Release process**: Tag-based publishing

## Security Best Practices

### 2-Factor Authentication (Required 2024)
- **PyPI account** - 2FA mandatory
- **GitHub account** - 2FA recommended
- **Trusted publishers** - Preferred over API keys

### Package Security
- **Dependency scanning** - GitHub Dependabot
- **Code scanning** - GitHub CodeQL
- **Supply chain security** - Pin dependencies

## Next Steps

1. **Update package structure** to follow modern standards
2. **Add missing files** for open source compliance
3. **Update pyproject.toml** with real metadata
4. **Set up GitHub Actions** for CI/CD
5. **Test on TestPyPI** before production
6. **Configure trusted publishers** for secure publishing

## Estimated Timeline

- **Project restructure**: 2-3 hours
- **Documentation**: 1-2 hours  
- **CI/CD setup**: 1-2 hours
- **Testing & publishing**: 1 hour

**Total**: 5-8 hours for complete PyPI-ready setup