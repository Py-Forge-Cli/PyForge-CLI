# PyForge CLI

<div align="center">
  <img src="assets/icon_pyforge_forge.svg" alt="PyForge CLI" width="128" height="128">
</div>

<div align="center">
  <strong>A powerful command-line tool for data format conversion and synthetic data generation</strong>
</div>

<div align="center">
  <a href="https://github.com/Py-Forge-Cli/PyForge-CLI/releases">
    <img src="https://img.shields.io/github/v/release/Py-Forge-Cli/PyForge-CLI?label=Latest%20Release" alt="Latest Release">
  </a>
  <a href="https://pypi.org/project/pyforge-cli/">
    <img src="https://img.shields.io/pypi/v/pyforge-cli.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/pyforge-cli/">
    <img src="https://img.shields.io/pypi/pyversions/pyforge-cli.svg" alt="Python versions">
  </a>
  <a href="https://github.com/Py-Forge-Cli/PyForge-CLI/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Py-Forge-Cli/PyForge-CLI.svg" alt="License">
  </a>
  <a href="https://github.com/Py-Forge-Cli/PyForge-CLI/actions">
    <img src="https://github.com/Py-Forge-Cli/PyForge-CLI/workflows/CI/badge.svg" alt="CI Status">
  </a>
</div>

## What is PyForge CLI?

PyForge CLI is a modern, fast, and intuitive command-line tool designed for data practitioners who need to convert between various data formats. Whether you're working with legacy databases, processing documents, or preparing data for analysis, PyForge CLI provides the tools you need with a beautiful terminal interface.

## Quick Start

Get up and running in under 2 minutes:

=== "Install from PyPI"

    ```bash
    pip install pyforge-cli
    ```

=== "Install with pipx"

    ```bash
    pipx install pyforge-cli
    ```

=== "Install with uv"

    ```bash
    uv add pyforge-cli
    ```

### Your First Conversion

```bash
# Install sample datasets for testing
pyforge install sample-datasets

# Convert a PDF to text
pyforge convert document.pdf

# Convert Excel to Parquet
pyforge convert spreadsheet.xlsx

# Convert Access database
pyforge convert database.mdb

# Convert XML with intelligent flattening
pyforge convert api_response.xml

# Get help
pyforge --help
```

## Supported Formats

| Input Format | Output Format | Status | Description |
|-------------|---------------|--------|-------------|
| **PDF** (.pdf) | Text (.txt) | ✅ Available | Extract text with metadata and page ranges |
| **Excel** (.xlsx) | Parquet (.parquet) | ✅ Available | Multi-sheet support with intelligent merging |
| **XML** (.xml, .xml.gz, .xml.bz2) | Parquet (.parquet) | ✅ Available | Intelligent flattening with configurable strategies |
| **Access** (.mdb/.accdb) | Parquet (.parquet) | ✅ Available | Cross-platform database conversion |
| **DBF** (.dbf) | Parquet (.parquet) | ✅ Available | Legacy database with encoding detection |
| **CSV** (.csv) | Parquet (.parquet) | ✅ Available | Auto-detection of delimiters and encoding |

## Key Features

### 🚀 **Fast & Efficient**
Built with performance in mind, PyForge CLI handles large files efficiently with progress tracking and memory optimization.

### 🎨 **Beautiful Interface**
Rich terminal output with progress bars, colored text, and structured tables make the CLI a pleasure to use.

### 🔧 **Intelligent Processing**
- Automatic encoding detection for legacy files
- Smart table discovery and column matching
- Metadata preservation across conversions

### 🔌 **Extensible Architecture**
Plugin-based system allows for easy addition of new format converters and custom processing logic.

### 📊 **Data Practitioner Focused**
Designed specifically for data engineers, scientists, and analysts with real-world use cases in mind.

## Popular Use Cases

!!! example "Document Processing"
    Convert legal documents, reports, and contracts from PDF to searchable text for analysis.
    
    ```bash
    pyforge convert contract.pdf --pages "1-10" --metadata
    ```

!!! example "Legacy Database Migration"
    Modernize old Access and DBF databases by converting to Parquet format for cloud analytics.
    
    ```bash
    pyforge convert legacy_system.mdb
    pyforge convert customer_data.dbf --encoding cp1252
    ```

!!! example "Excel Data Processing"
    Convert complex Excel workbooks to Parquet for efficient data processing and analysis.
    
    ```bash
    pyforge convert financial_report.xlsx --combine --compression gzip
    ```

!!! example "XML API Data Processing"
    Convert XML API responses and configuration files to Parquet for data analysis.
    
    ```bash
    pyforge convert api_response.xml --flatten-strategy aggressive --array-handling expand
    pyforge convert config.xml --namespace-handling strip
    ```

## Getting Started

Choose your path based on your experience level:

<div class="grid cards" markdown>

-   :material-rocket-launch: **Quick Start**

    ---

    Jump right in with our 5-minute tutorial

    [:octicons-arrow-right-24: Quick Start Guide](getting-started/quick-start.md)

-   :material-download: **Installation**

    ---

    Detailed installation instructions for all platforms

    [:octicons-arrow-right-24: Installation Guide](getting-started/installation.md)

-   :material-database: **Sample Datasets**

    ---

    Curated test datasets for all supported formats

    [:octicons-arrow-right-24: Browse Datasets](sample-datasets.md)

-   :material-book-open: **Tutorials**

    ---

    Step-by-step guides for common workflows

    [:octicons-arrow-right-24: Browse Tutorials](tutorials/index.md)

-   :material-microsoft: **Databricks Guide**

    ---

    Complete guide with interactive notebook

    [:octicons-arrow-right-24: Databricks Guide](databricks-serverless-guide.md) | [📓 Download Notebook](https://github.com/Py-Forge-Cli/PyForge-CLI/blob/main/notebooks/testing/functional/10-databricks-serverless-user-guide.ipynb)

-   :material-api: **API Reference**

    ---

    Complete command reference and options

    [:octicons-arrow-right-24: CLI Reference](reference/cli-reference.md)

</div>

## Community & Support

- **📖 Documentation**: Comprehensive guides and examples
- **🐛 Issues**: [Report bugs](https://github.com/Py-Forge-Cli/PyForge-CLI/issues) and request features
- **💬 Discussions**: [GitHub Discussions](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions) for questions and ideas
- **📦 PyPI**: [Package repository](https://pypi.org/project/pyforge-cli/) with installation stats

## What's New

### Version 1.0.9 (Latest) 🚀
- 🎯 **Databricks Serverless Support**: Complete file conversion support in Databricks Serverless environments
- ✅ **Subprocess Backend**: Specialized backend for MDB/ACCDB files due to Java SDK dependencies
- ✅ **Unity Catalog Integration**: Native support for `/Volumes/` paths with automatic file handling
- ✅ **Shell Command Support**: CSV, XML, Excel, and DBF files can use standard `%sh` magic commands
- ✅ **Enhanced Error Handling**: Proper exception chaining for better debugging
- ✅ **Smart Backend Selection**: Automatic detection and selection based on environment
- ✅ **Performance Improvements**: Memory-efficient processing and optimized conversions
- ✅ **Interactive Notebook**: Ready-to-use Jupyter notebook for Databricks Serverless

### Version 1.0.8
- ✅ **Complete Testing Infrastructure Overhaul**: Fixed 13 major issues across infrastructure
- ✅ **Sample Datasets Installation**: Fixed with intelligent fallback versioning system
- ✅ **Missing Dependencies**: Added PyMuPDF, chardet, requests to resolve import errors
- ✅ **Convert Command Fix**: Resolved TypeError in ConverterRegistry API
- ✅ **Comprehensive Testing Framework**: Created systematic testing with 402 lines of test code
- ✅ **Notebook Organization**: Restructured with proper unit/integration/functional hierarchy

### Version 0.5.0
- 🎉 **Sample Datasets Collection**: 23 curated test datasets across all supported formats
- ✅ **Automated Installation**: `pyforge install sample-datasets` command with GitHub Releases integration
- ✅ **Format Filtering**: Install specific formats with `--formats pdf,excel,xml`
- ✅ **Size Categories**: Small (<100MB), Medium (100MB-1GB), Large (>1GB) datasets
- ✅ **Progress Tracking**: Rich terminal UI with download progress and checksums
- ✅ **Dataset Management**: List releases, show installed datasets, and uninstall options

### Version 0.4.0
- 🚀 **MDF Tools Installer**: Complete SQL Server infrastructure for MDF file processing
- ✅ **Docker Integration**: Automated Docker Desktop and SQL Server Express installation
- ✅ **Container Management**: Full lifecycle commands for SQL Server container control
- ✅ **Cross-Platform Support**: Windows, macOS, and Linux compatibility

### Version 0.3.0
- ✅ **XML to Parquet Converter**: Complete implementation with intelligent flattening
- ✅ **Automatic Structure Detection**: Analyzes XML hierarchy and array patterns
- ✅ **Flexible Flattening Strategies**: Conservative, moderate, and aggressive options
- ✅ **Advanced Array Handling**: Expand, concatenate, or JSON string modes
- ✅ **Namespace Support**: Configurable namespace processing
- ✅ **Schema Preview**: Optional structure preview before conversion
- ✅ **Comprehensive Documentation**: User guide and quick reference
- ✅ **Compressed XML Support**: Handles .xml.gz and .xml.bz2 files

### Version 0.2.5
- ✅ Fixed package build configuration and PyPI publication metadata
- ✅ Resolved InvalidDistribution errors for wheel packaging
- ✅ Updated hatchling build configuration for src layout

### Version 0.2.4
- ✅ Fixed GitHub Actions deprecation warnings and workflow failures
- ✅ Updated pypa/gh-action-pypi-publish to latest version
- ✅ Removed redundant sigstore signing steps

### Version 0.2.3
- 🎉 **Major Feature**: CSV to Parquet conversion with auto-detection
- ✅ Intelligent delimiter detection (comma, semicolon, tab, pipe)
- ✅ Smart encoding detection (UTF-8, Latin-1, Windows-1252, UTF-16)
- ✅ Header detection with fallback to generic column names
- ✅ String-based conversion consistent with Phase 1 architecture

### Version 0.2.2
- ✅ Enhanced GitHub workflow templates for structured development
- ✅ Updated README documentation with CSV support
- ✅ Comprehensive testing and documentation for CSV converter

### Version 0.2.1
- ✅ Fixed GitHub Actions workflow for automated PyPI publishing
- ✅ Updated CI/CD pipeline to use API token authentication

### Version 0.2.0
- ✅ Excel to Parquet conversion with multi-sheet support
- ✅ MDB/ACCDB to Parquet conversion with cross-platform support
- ✅ DBF to Parquet conversion with encoding detection
- ✅ Interactive mode for Excel sheet selection
- ✅ Progress tracking with rich terminal UI

[View Complete Changelog](about/changelog.md){ .md-button .md-button--primary }

---

<div align="center">
  <strong>Ready to transform your data workflows?</strong><br>
  <a href="getting-started/installation.md" class="md-button md-button--primary">Get Started Now</a>
  <a href="https://github.com/Py-Forge-Cli/PyForge-CLI" class="md-button">View on GitHub</a>
</div>