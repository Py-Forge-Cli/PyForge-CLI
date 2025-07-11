# Installation Guide

This guide covers all the ways to install PyForge CLI on your system.

## Quick Install

The fastest way to get started:

```bash
pip install pyforge-cli
```

## Installation Methods

### Method 1: pip (Recommended)

Install from PyPI using pip:

=== "Global Installation"

    ```bash
    pip install pyforge-cli
    ```

=== "User Installation"

    ```bash
    pip install --user pyforge-cli
    ```

=== "Virtual Environment"

    ```bash
    python -m venv pyforge-env
    source pyforge-env/bin/activate  # On Windows: pyforge-env\Scripts\activate
    pip install pyforge-cli
    ```

### Method 2: pipx (Isolated)

Install in an isolated environment using pipx:

```bash
# Install pipx if you don't have it
pip install pipx

# Install PyForge CLI
pipx install pyforge-cli
```

### Method 3: uv (Fast)

Install using the ultrafast uv package manager:

```bash
# Install uv if you don't have it
pip install uv

# Install PyForge CLI
uv add pyforge-cli
```

### Method 4: From Source

For development or latest features:

```bash
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI
pip install -e .
```

## System Requirements

### Python Version
- **Python 3.8+** (recommended: Python 3.10.12 for Databricks compatibility)
- Works on Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Databricks Serverless**: Requires Python 3.10.12 for full compatibility

### Operating Systems
- **Windows** 10/11 (x64)
- **macOS** 10.14+ (Intel and Apple Silicon)
- **Linux** (Ubuntu 18.04+, CentOS 7+, and other distributions)
- **Databricks Serverless** (Python 3.10.12 runtime)

### Compatibility Matrix

| Environment | Python Version | PyForge CLI Version | Notes |
|-------------|---------------|-------------------|--------|
| Local Development | 3.8-3.12 | 1.0.9 | Full feature support |
| Databricks Serverless V1 | 3.10.12 | 1.0.9 | Optimized dependencies |
| Databricks Classic | 3.8-3.11 | 1.0.9 | Standard installation |
| Production Servers | 3.10+ | 1.0.9 | Recommended for stability |

## Databricks Serverless Installation

!!! important "Databricks Serverless Requirements"
    PyForge CLI version 1.0.9 includes specialized support for Databricks Serverless environments with optimized dependency management.

### Prerequisites

1. **Unity Catalog Volume Access**: Ensure you have access to a Unity Catalog volume for storing wheels
2. **Databricks CLI**: Install and configure the Databricks CLI
3. **Python Environment**: Databricks Serverless runs Python 3.10.12

### Installation Steps

#### Step 1: Install PyForge CLI Wheel

```python
# In a Databricks Serverless notebook cell
%pip install pyforge-cli==1.0.9 --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
```

#### Step 2: Install from Unity Catalog Volume (Alternative)

If you have deployed PyForge CLI to a Unity Catalog volume:

```python
# Replace {username} with your Databricks username
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/pyforge_cli-1.0.9-py3-none-any.whl --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
```

#### Step 3: Restart Python Environment

```python
# Restart Python to ensure clean import
dbutils.library.restartPython()
```

#### Step 4: Verify Installation

```python
# Verify PyForge CLI is installed and working
import pyforge_cli
print(f"PyForge CLI version: {pyforge_cli.__version__}")

# Test basic functionality
from pyforge_cli.main import cli
print("PyForge CLI installed successfully!")
```

### Databricks Serverless Configuration

#### Subprocess Backend Configuration

PyForge CLI automatically configures the subprocess backend for Databricks Serverless environments:

```python
# No additional configuration needed - PyForge CLI handles this automatically
# The subprocess backend is optimized for Databricks Serverless constraints
```

#### Memory and Resource Management

```python
# For large file processing in Databricks Serverless
import pyforge_cli.config as config

# Configure for serverless environment
config.set_serverless_mode(True)
config.set_memory_limit("2GB")  # Adjust based on your cluster configuration
```

### Usage in Databricks Serverless

#### Converting Files

```python
# Convert files using the Python API (recommended for Databricks)
from pyforge_cli.converters import CSVConverter

# Example: Convert CSV to Parquet
converter = CSVConverter()
converter.convert(
    input_file="/Volumes/catalog/schema/volume/data.csv",
    output_file="/Volumes/catalog/schema/volume/data.parquet"
)
```

#### Using CLI Commands

```python
# Run CLI commands programmatically
import subprocess

# Example: List supported formats
result = subprocess.run(
    ["python", "-m", "pyforge_cli", "formats"],
    capture_output=True,
    text=True
)
print(result.stdout)
```

### Troubleshooting Databricks Serverless

#### Common Issues

1. **Import Errors**: Ensure you've restarted Python after installation
   ```python
   dbutils.library.restartPython()
   ```

2. **Path Issues**: Always use `dbfs:/` prefix for Unity Catalog volumes
   ```python
   # Correct path format
   input_path = "/Volumes/catalog/schema/volume/file.csv"
   ```

3. **Memory Issues**: For large files, process in chunks
   ```python
   # Configure chunk processing
   converter.convert(input_file, output_file, chunk_size=10000)
   ```

4. **Dependency Conflicts**: Use the exact PyPI installation command
   ```python
   %pip install pyforge-cli==1.0.9 --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
   ```

#### Required Flags for Serverless

- `--no-cache-dir`: Ensures fresh installation without cached packages
- `--quiet`: Reduces installation output verbosity
- `--index-url https://pypi.org/simple/`: Specifies PyPI index for dependency resolution
- `--trusted-host pypi.org`: Trusts PyPI host for secure downloads

## Platform-Specific Setup

### Windows

=== "Command Prompt"

    ```cmd
    pip install pyforge-cli
    pyforge --version
    ```

=== "PowerShell"

    ```powershell
    pip install pyforge-cli
    pyforge --version
    ```

=== "Windows Terminal"

    ```bash
    pip install pyforge-cli
    pyforge --version
    ```

!!! note "Windows Path Issues"
    If `pyforge` is not found after installation, you may need to add Python's Scripts directory to your PATH. The installer should do this automatically, but if it doesn't:
    
    1. Find your Python installation directory
    2. Add `Python\Scripts` to your PATH environment variable
    3. Restart your terminal

### macOS

=== "Terminal"

    ```bash
    pip install pyforge-cli
    pyforge --version
    ```

=== "Homebrew Python"

    ```bash
    # If using Homebrew Python
    pip3 install pyforge-cli
    pyforge --version
    ```

!!! tip "macOS Setup"
    For the best experience on macOS, we recommend:
    
    ```bash
    # Install Homebrew if you don't have it
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Install Python via Homebrew
    brew install python
    
    # Install PyForge CLI
    pip3 install pyforge-cli
    ```

### Linux

=== "Ubuntu/Debian"

    ```bash
    # Update package list
    sudo apt update
    
    # Install Python and pip
    sudo apt install python3 python3-pip
    
    # Install PyForge CLI
    pip3 install pyforge-cli
    ```

=== "CentOS/RHEL/Fedora"

    ```bash
    # Install Python and pip
    sudo dnf install python3 python3-pip
    
    # Install PyForge CLI
    pip3 install pyforge-cli
    ```

=== "Arch Linux"

    ```bash
    # Install Python and pip
    sudo pacman -S python python-pip
    
    # Install PyForge CLI
    pip install pyforge-cli
    ```

## Additional Dependencies

### Core Dependencies (Version 1.0.9)

PyForge CLI 1.0.9 includes optimized dependencies for Databricks Serverless compatibility:

- **pandas==1.5.3** - Databricks Serverless V1 compatible
- **pyarrow==8.0.0** - Exact version match for Databricks
- **numpy==1.23.5** - Databricks Serverless V1 compatible
- **click==8.1.3** - CLI framework
- **rich==12.6.0** - Enhanced terminal output

### Format-Specific Dependencies

All format-specific dependencies are now included by default in version 1.0.9:

- **PyMuPDF>=1.20.0** - PDF processing (included by default)
- **openpyxl>=3.0.0** - Excel file support (included by default)
- **chardet>=3.0.0** - Character encoding detection (included by default)
- **requests>=2.25.0** - HTTP client for downloads (included by default)
- **jaydebeapi>=1.2.3** - MDB/Access support (included by default)
- **jpype1>=1.3.0** - Java integration for MDB files (included by default)
- **dbfread>=2.0.0** - DBF file support (included by default)

### For MDB/Access File Support

PyForge CLI requires additional tools for Microsoft Access database conversion:

=== "Ubuntu/Debian"

    ```bash
    sudo apt install mdbtools
    ```

=== "macOS"

    ```bash
    brew install mdbtools
    ```

=== "Windows"

    MDB support is built-in on Windows. No additional tools needed.

=== "CentOS/RHEL/Fedora"

    ```bash
    sudo dnf install mdbtools
    ```

### For PDF Processing

PDF support is included by default with PyMuPDF. No additional setup required.

### For Excel Files

Excel support is included by default with openpyxl. No additional setup required.

### For SQL Server MDF Files

MDF file processing requires specialized tools that can be installed automatically:

```bash
# Install Docker Desktop and SQL Server Express
pyforge install mdf-tools

# Verify installation
pyforge mdf-tools status
```

For detailed setup instructions, see [Tools Prerequisites](tools-prerequisites.md).

## Verification

After installation, verify that PyForge CLI is working correctly:

```bash
# Check version
pyforge --version

# Show help
pyforge --help

# List supported formats
pyforge formats

# Test with a simple command
pyforge validate --help
```

Expected output:
```
pyforge, version 1.0.9
```

## Troubleshooting

### Command Not Found

If you get `command not found: pyforge` after installation:

1. **Check if it's in your PATH**:
   ```bash
   python -m pip show pyforge-cli
   ```

2. **Find the installation directory**:
   ```bash
   python -c "import sys; print([p for p in sys.path if 'site-packages' in p][0])"
   ```

3. **Run directly with Python**:
   ```bash
   python -m pyforge_cli --help
   ```

### Permission Errors

If you get permission errors during installation:

=== "Use --user flag"

    ```bash
    pip install --user pyforge-cli
    ```

=== "Use virtual environment"

    ```bash
    python -m venv pyforge-env
    source pyforge-env/bin/activate
    pip install pyforge-cli
    ```

### Import Errors

If you encounter import errors:

1. **Update pip**:
   ```bash
   pip install --upgrade pip
   ```

2. **Reinstall PyForge CLI**:
   ```bash
   pip uninstall pyforge-cli
   pip install pyforge-cli
   ```

3. **Check for conflicting packages**:
   ```bash
   pip list | grep -i pyforge
   ```

### Dependency Conflicts

If you have dependency conflicts:

1. **Use a virtual environment** (recommended)
2. **Update all packages**:
   ```bash
   pip install --upgrade pyforge-cli
   ```

### Databricks Serverless Issues

For Databricks Serverless specific issues:

1. **Wheel not found**: Ensure the wheel is deployed to the correct Unity Catalog volume
2. **Import errors after installation**: Always restart Python after wheel installation
3. **Version conflicts**: Use the exact PyPI installation command with flags
4. **Path resolution**: Use absolute paths starting with `/Volumes/`

### Automated Deployment to Databricks

For automated deployment to Databricks environments:

```bash
# Use the deployment script (requires Databricks CLI configured)
python scripts/deploy_pyforge_to_databricks.py

# With custom username
python scripts/deploy_pyforge_to_databricks.py -u your_username

# With custom profile
python scripts/deploy_pyforge_to_databricks.py -p custom-profile
```

This script will:
- Build PyForge CLI wheel (version 1.0.9)
- Upload to Unity Catalog volume
- Upload notebooks to Databricks workspace
- Provide installation instructions

## Development Installation

For contributing to PyForge CLI:

```bash
# Clone the repository
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,test]"

# Verify installation
pyforge --version
```

## Updating PyForge CLI

To update to the latest version:

```bash
pip install --upgrade pyforge-cli
```

To update to a specific version:

```bash
pip install pyforge-cli==1.0.9
```

## Uninstalling

To remove PyForge CLI:

```bash
pip uninstall pyforge-cli
```

## Next Steps

Now that you have PyForge CLI installed:

1. **[Quick Start](quick-start.md)** - Convert your first file
2. **[First Conversion](first-conversion.md)** - Detailed walkthrough
3. **[CLI Reference](../reference/cli-reference.md)** - Complete command documentation

## Getting Help

If you're still having installation issues:

- Check our [Troubleshooting Guide](../tutorials/troubleshooting.md)
- Search [existing issues](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)
- Create a [new issue](https://github.com/Py-Forge-Cli/PyForge-CLI/issues/new) with:
  - Your operating system and version
  - Python version (`python --version`)
  - Complete error message
  - Installation method used