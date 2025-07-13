# Claude Memory - User Profile

## User Preferences

### Git Commit Messages
- **No AI Attribution**: Do not include "Generated with Claude Code" or similar AI attribution in commit messages
- **Clean Professional Format**: Use standard commit message format without AI generation notices

### Testing Requirements
- **MANDATORY Virtual Environment**: Always activate the virtual environment `.venv` before running any tests or PyForge commands
- **Command Format**: `source .venv/bin/activate && <command>`
- **This applies to**: All pytest runs, make commands, pyforge CLI usage, and any Python operations

## Python Code Generation Standards

### Critical Ruff Compliance Rules

**ALWAYS follow these patterns when generating Python code:**

#### 1. Exception Handling (B904 - most common violation)
```python
# ❌ WRONG - Missing exception chaining
try:
    risky_operation()
except SomeException:
    raise CustomException("Something went wrong")

# ✅ CORRECT - Proper exception chaining
try:
    risky_operation()
except SomeException as e:
    raise CustomException("Something went wrong") from e

# ✅ ALTERNATIVE - Suppress chaining when intentional
try:
    risky_operation()
except SomeException:
    raise CustomException("Something went wrong") from None
```

#### 2. Bare Except Clauses (E722 - second most common)
```python
# ❌ WRONG - Bare except
try:
    operation()
except:
    handle_error()

# ✅ CORRECT - Specific exceptions
try:
    operation()
except (ValueError, TypeError) as e:
    handle_error(e)

# ✅ ACCEPTABLE - When you really need to catch everything
try:
    operation()
except Exception as e:
    handle_error(e)
```

#### 3. Unused Imports (F401)
```python
# ❌ WRONG - Import for availability check
try:
    import optional_library
    HAS_LIBRARY = True
except ImportError:
    HAS_LIBRARY = False

# ✅ CORRECT - Use importlib for availability
import importlib.util
HAS_LIBRARY = importlib.util.find_spec("optional_library") is not None

if HAS_LIBRARY:
    import optional_library
```

#### 4. Loop Variable Binding (B023)
```python
# ❌ WRONG - Function captures loop variable
functions = []
for item in items:
    functions.append(lambda: process(item))  # 'item' captured by reference

# ✅ CORRECT - Explicit binding
functions = []
for item in items:
    functions.append(lambda x=item: process(x))  # 'item' bound by value
```

### Ruff Configuration Compliance

**Current project settings:**
- Line length: 88 characters
- Target Python: 3.8+
- Enabled rules: E, W, F, I, B, C4, UP

### Code Generation Template

**When writing any Python function, use this pattern:**

```python
def function_name(param: type) -> return_type:
    """
    Brief description.
    
    Args:
        param: Parameter description
        
    Returns:
        Return description
        
    Raises:
        SpecificException: When this happens
    """
    try:
        # Main logic here
        result = some_operation(param)
        return result
    except (SpecificError1, SpecificError2) as e:
        # Handle specific errors
        logger.error(f"Operation failed: {e}")
        raise CustomError("Descriptive message") from e
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise CustomError("Unexpected error occurred") from e
```

### Import Organization

```python
# Standard library imports
import importlib.util
import logging
from pathlib import Path
from typing import Optional, Union

# Third-party imports
import pandas as pd
import pyarrow as pa

# Local imports
from pyforge_cli.converters.base import BaseConverter
from pyforge_cli.utils.dependency_checker import check_dependency

# Conditional imports with proper checking
HAS_OPTIONAL_LIB = importlib.util.find_spec("optional_lib") is not None
if HAS_OPTIONAL_LIB:
    import optional_lib
```

### Error Message Standards

```python
# ✅ Descriptive error messages with context
raise ValueError(f"Invalid file format '{ext}'. Expected: {supported_formats}")

# ✅ Include original error information
raise ConversionError(f"Failed to parse {file_path}: {original_error}") from e

# ✅ User-friendly messages for CLI
logger.error(f"Conversion failed for '{input_file}': {error_summary}")
```

## Jupyter Notebook Organization Best Practices

### Directory Structure for Testing Notebooks
```
cortexpy-cli/
   notebooks/
      testing/
         unit/
            01-test-cli-commands.ipynb
            02-test-module-functions.ipynb
         integration/
            01-test-workflow-integration.ipynb
            02-test-data-pipeline.ipynb
         functional/
            01-test-cli-end-to-end.ipynb
            02-test-user-scenarios.ipynb
         exploratory/
             01-performance-analysis.ipynb
             02-error-investigation.ipynb
      documentation/
         01-getting-started.ipynb
         02-api-examples.ipynb
      reports/
          test-results-YYYY-MM-DD.ipynb
```

### Naming Conventions
- **Pattern**: `[sequence]-[test-type]-[component]-[description].ipynb`
- **Examples**: 
  - `01-unit-cli-argument-parsing.ipynb`
  - `02-integration-cli-workflow-end-to-end.ipynb`
  - `03-functional-user-scenario-project-creation.ipynb`

### Test Organization Types
- **Unit**: Test individual functions/modules
- **Integration**: Test component interactions
- **Functional**: Test complete user workflows and scenarios
- **Exploratory**: Performance analysis, debugging, and investigation

### Version Control
- Use `nbstripout` to clean outputs before commits
- Implement pre-commit hooks for notebook formatting
- Remove sensitive metadata and execution counts

### Notebook Structure Standards
- Include setup/teardown cells
- Use markdown cells for documentation and context
- Implement automated cleanup in final cells
- Keep notebooks focused on specific test scenarios
- Use ASCII-only text to avoid encoding issues

## PyForge CLI Deployment Process

### Deployment Scripts Location
- **Deployment Script**: `scripts/deploy_pyforge_to_databricks.py`
- **Notebooks Source**: `notebooks/testing/` (organized by test type)
- **Developer Documentation**: `docs/developer-notes/`

### Notebook Organization
- **Unit Tests**: `notebooks/testing/unit/` - Individual function/module tests
- **Integration Tests**: `notebooks/testing/integration/` - Component interaction tests
- **Functional Tests**: `notebooks/testing/functional/` - End-to-end user scenarios
- **Exploratory Tests**: `notebooks/testing/exploratory/` - Performance and debugging

### Deployment Paths
- **Wheel Location**: `/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{databricks_username}/`
- **Notebooks Location**: `/Workspace/CoreDataEngineers/{databricks_username}/pyforge_notebooks/`

### Usage Commands
```bash
# Deploy PyForge CLI wheel and all organized notebooks
python scripts/deploy_pyforge_to_databricks.py

# With username override
python scripts/deploy_pyforge_to_databricks.py -u your_username

# With custom profile
python scripts/deploy_pyforge_to_databricks.py -p custom-profile

# Verbose output
python scripts/deploy_pyforge_to_databricks.py -v
```

### Deployment Process
1. **Prerequisites Check**: Python build tools, Databricks CLI
2. **Username Detection**: Prioritizes Databricks authenticated user
3. **Build**: Creates wheel file in `dist/`
4. **Upload Wheel**: To Unity Catalog volume
5. **Upload Notebooks**: All notebooks from `notebooks/testing/` with preserved structure
6. **Summary**: Shows deployment locations and next steps

### Supported Notebook Types
- **Jupyter Notebooks** (`.ipynb`): Uploaded as JUPYTER format
- **Python Files** (`.py`): Uploaded as SOURCE format with PYTHON language

### Key Testing Notebooks
- `notebooks/testing/unit/01-csv-testing-notebook.py` - CSV conversion unit tests
- `notebooks/testing/integration/01-pyforge-integration-testing.py` - Integration testing
- `notebooks/testing/integration/02-pyforge-v1-testing.py` - V1 compatibility testing
- `notebooks/testing/integration/03-enhanced-pyforge-testing.py` - Enhanced testing suite
- `notebooks/testing/functional/01-test-cli-end-to-end.ipynb` - CLI end-to-end testing

## CortexPy Deployment Process

### Deployment Scripts Location
- **Bash Script**: `scripts/deploy_to_databricks.sh`
- **Python Script**: `scripts/deploy_to_databricks.py`

### Username Strategy (Updated)
- **Primary**: Databricks authenticated username via `databricks current-user me`
- **Fallback**: Git username or user override
- **Result**: Both volume and workspace paths use the same username for consistency

### Deployment Paths
- **Wheel Location**: `/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{databricks_username}/`
- **Notebooks Location**: `/Workspace/CoreDataEngineers/{databricks_username}/cortexpy_notebooks/`

### Usage Commands
```bash
# Bash script (auto-detects Databricks username)
./scripts/deploy_to_databricks.sh

# Python script (cross-platform)
python scripts/deploy_to_databricks.py

# With username override
./scripts/deploy_to_databricks.sh -u your_username
python scripts/deploy_to_databricks.py -u your_username

# With custom profile
./scripts/deploy_to_databricks.sh -p custom-profile
python scripts/deploy_to_databricks.py -p custom-profile
```

### Deployment Process
1. **Prerequisites Check**: Python build tools, Databricks CLI
2. **Username Detection**: Prioritizes Databricks authenticated user
3. **Build**: Creates wheel file in `dist/`
4. **Upload Wheel**: To Unity Catalog volume
5. **Upload Notebooks**: To Databricks workspace
6. **Summary**: Shows deployment locations and next steps

### Key Notebooks
- `data-integrity-check-spark-sql.py` - Standard DIC implementation
- `data-integrity-check-spark-sql-v2.py` - Enhanced V2 DIC with optimization
- `test-dic-v2-developer.py` - Comprehensive testing framework

### Notebook Wheel Installation
```python
# Notebooks automatically detect and use deployed wheels
# Manual installation if needed:
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/cortexpy-{version}-py3-none-any.whl
```

### Recent Updates (Latest Session)
- Updated both scripts to use Databricks username as primary source
- Fixed path consistency between volume and workspace
- Enhanced error handling and fallback strategies
- Added comprehensive command-line options
- Created detailed documentation and troubleshooting guides

### Dependency Management Fixes (Latest Session)
- **Added PyMuPDF**: Fixed PDF converter auto-loading dependency issues
- **Added chardet**: Fixed CSV encoding detection dependency issues  
- **Added requests**: Fixed installer/downloader dependency issues
- **Updated pyproject.toml**: All previously optional dependencies now included in core dependencies to prevent runtime import errors

### Critical Bug Fixes (Latest Session)
- **Fixed ConverterRegistry.get_converter()**: Removed extra parameter causing TypeError on all conversion attempts
  - File: `src/pyforge_cli/main.py:295`
  - Issue: `registry.get_converter(input_file, options)` → `registry.get_converter(input_file)`
  - Result: CSV and XML conversions now working correctly

- **Fixed Sample Datasets Installer**: Added intelligent fallback to v1.0.5 when current version has no assets
  - File: `src/pyforge_cli/installers/sample_datasets_installer.py`
  - Issue: Latest release (v1.0.7) has no sample dataset assets
  - Fix: Automatic fallback to known good versions (v1.0.5, v1.0.4, v1.0.3) when assets missing
  - Result: Sample datasets installation now works reliably

### Test Results Summary (Latest Session)
- **CSV to Parquet**: ✅ Working
- **XML to Parquet**: ✅ Working  
- **Excel to Parquet**: ❌ URI parsing issue with filenames containing spaces
- **PDF conversion**: Not tested (requires PDF files)
- **MDB/Access conversion**: Not tested (requires MDB files)
- **DBF conversion**: Not tested (requires DBF files)

### User Environment
- **Git Username**: sdandey
- **Databricks Username**: usa-sdandey@deloitte.com
- **Project Path**: /Users/sdandey/Documents/code/cortexpy
- **Branch**: dic-performance-v2

### Common Issues & Solutions
1. **Username Mismatch**: Scripts now auto-detect Databricks username
2. **Notebook Path Errors**: Use `.py` extension in `dbutils.notebook.run()` calls
3. **Permission Issues**: Verify Unity Catalog and workspace permissions
4. **CLI Config**: Use `databricks configure --token --profile DEFAULT`

## Databricks Serverless Notebook Configuration

### PyPI Index URL for Serverless Notebooks
**IMPORTANT**: All pip installation commands in Databricks Serverless notebooks must include the proper PyPI index URL for dependency resolution in corporate environments.

#### Standard Template for %pip install commands:
```python
# Always use this format for pip installs in Databricks Serverless notebooks
%pip install {package_path_or_name} --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
```

#### Example for wheel installation from Unity Catalog volume:
```python
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/package-{version}-py3-none-any.whl --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
```

#### Example for PyPI package installation:
```python
%pip install package-name==version --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
```

### Required Flags for Serverless Notebooks:
- `--no-cache-dir`: Ensures fresh installation without cached packages
- `--quiet`: Reduces installation output verbosity
- `--index-url https://pypi.org/simple/`: Specifies PyPI index for dependency resolution
- `--trusted-host pypi.org`: Trusts PyPI host for secure downloads

### Usage Notes:
- This configuration is required for all Databricks Serverless environments
- Standard PyPI index URL works for most corporate environments
- If corporate firewall blocks PyPI, consult IT for approved index URL
- Always restart Python after wheel installations: `dbutils.library.restartPython()`

## Automated Ruff Integration

### Pre-commit Hook Configuration
```bash
# Install pre-commit
pip install pre-commit

# Add to .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

### Development Workflow
```bash
# Before committing, always run:
ruff check --fix src/
ruff format src/

# Or use make target:
make lint-fix
```

### Claude Code Generation Checklist
When Claude generates code, ensure:
- [ ] Exception chaining with `from e` or `from None`
- [ ] Specific exception types instead of bare `except:`
- [ ] Proper import organization and unused import removal
- [ ] Loop variable binding for lambdas in loops
- [ ] Type hints where appropriate
- [ ] Descriptive error messages
- [ ] Consistent formatting (88 char line length)

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Project Settings and Guidelines

### Virtual Environment Management
- **Always activate the virtual environment `.venv` before running any tests**
- **Mandatory step for every test performed on pyforge**
- Ensures consistent dependency and environment configuration
- Prevents potential conflicts with system-wide Python installations

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.