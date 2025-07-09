# Claude Memory - User Profile

## User Preferences

### Git Commit Messages
- **No AI Attribution**: Do not include "Generated with Claude Code" or similar AI attribution in commit messages
- **Clean Professional Format**: Use standard commit message format without AI generation notices

### Documentation Organization
- **All documentation artifacts**: Always create all documentation files requested by the user under the `claude-notes/` folder
- **Structured organization**: Keep documentation organized by topic/feature within the claude-notes directory
- **No documentation in root**: Never create documentation files in the project root unless explicitly requested

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

### Project Build, Test, and Report Generation Instructions
- **Build Instructions**:
  - Use `pyproject.toml` for build configuration
  - Run `python -m build` to create distribution packages
  - Verify wheel and source distributions in `dist/` directory

- **Testing Framework**:
  - Use `pytest` for comprehensive testing
  - Organize tests in `tests/` directory with clear structure
  - Run tests with `pytest` or `python -m pytest`

- **Test Report Generation**:
  - Use `pytest-html` for generating HTML test reports
  - Command: `pytest --html=test_report.html`
  - Generates detailed test result visualization
  - Save reports in `reports/test-results-YYYY-MM-DD.html`

- **Coverage Reporting**:
  - Use `pytest-cov` for code coverage analysis
  - Command: `pytest --cov=pyforge_cli --cov-report=html`
  - Generates detailed coverage report in `htmlcov/` directory
  - Aim for >80% code coverage across modules

### Local Development Workflow
- **Always look into @docs/development-setup-changes.md to understand local development and unit-testing commands**

### Development Guidelines
- **Always follow @CONTRIBUTING.md instructions to understand the project setup and follow those guidelines for development and testing**

## Logging and Tracking Guidelines
- Always keep the generated logs into a `claude-logs` with a date and time-stamp included for easy traceability
- **Logging Directive**: Always create comprehensive logs for each long running session that you spend more than 5 mins in agentic coding