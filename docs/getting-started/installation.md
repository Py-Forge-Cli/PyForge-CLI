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
- **Python 3.8+** (recommended: Python 3.11+)
- Works on Python 3.8, 3.9, 3.10, 3.11, 3.12

### Operating Systems
- **Windows** 10/11 (x64)
- **macOS** 10.14+ (Intel and Apple Silicon)
- **Linux** (Ubuntu 18.04+, CentOS 7+, and other distributions)

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
pyforge, version 0.2.1
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
pip install pyforge-cli==0.2.1
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