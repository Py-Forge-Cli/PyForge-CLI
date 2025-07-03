# PyForge Modular Package Structure

This directory contains the recommended folder structure for the PyForge modular package ecosystem with two packages: `pyforge-core` and `pyforge-databricks`.

## Package Overview

### pyforge-core
The core package containing all fundamental conversion functionality without any cloud-specific dependencies. This package can be used standalone for local file conversions.

### pyforge-databricks
The Databricks integration package that adds:
- Databricks SDK integration for Volume operations
- Serverless compute detection and optimization
- Distributed processing with Spark
- Direct Volume-to-Volume conversions

## Directory Structure

```
package-structure/
├── pyforge-core/              # Core conversion functionality
├── pyforge-databricks/        # Databricks-specific features
└── scripts/                   # Build and deployment scripts
```

## Installation

### For Users

```bash
# Core only (local conversions)
pip install pyforge-core

# Core + Databricks integration
pip install pyforge-core pyforge-databricks
```

### For Developers

```bash
# Clone the repository
git clone https://github.com/PyForge/pyforge-packages.git
cd pyforge-packages

# Install in development mode
pip install -e ./pyforge-core
pip install -e ./pyforge-databricks
```

## Version Compatibility

- Python: 3.8+ for pyforge-core, 3.10+ for pyforge-databricks
- Databricks Runtime: 13.3 LTS and above
- Serverless Environment: Version 1 (Python 3.10) and Version 2 (Python 3.11)

## Key Features

### Modular Design
- Clean separation of concerns
- Optional cloud dependencies
- Independent versioning
- Backward compatibility

### Pinned Dependencies
All dependencies are pinned to specific versions to ensure stability in production environments, especially for Databricks serverless compute compatibility.

### Extensibility
The architecture is designed to support future platform-specific packages:
- pyforge-aws
- pyforge-gcp
- pyforge-azure
- pyforge-snowflake

## Development Workflow

1. Make changes in the appropriate package
2. Run tests: `pytest tests/`
3. Build packages: `python -m build`
4. Publish to PyPI (via CI/CD)

## License

MIT License - See individual package LICENSE files for details.