# PyForge CLI

<div align="center">
  <img src="assets/icon_pyforge_forge.svg" alt="PyForge CLI" width="128" height="128">
</div>

<div align="center">
  <strong>A powerful command-line tool for data format conversion and manipulation, built with Python and Click.</strong>
</div>

## 📖 Documentation

**[📚 Complete Documentation](https://py-forge-cli.github.io/PyForge-CLI/)** | **[🚀 Quick Start](https://py-forge-cli.github.io/PyForge-CLI/getting-started/quick-start)** | **[📦 Installation Guide](https://py-forge-cli.github.io/PyForge-CLI/getting-started/installation)** | **[🔧 CLI Reference](https://py-forge-cli.github.io/PyForge-CLI/reference/cli-reference)**

<div align="center">
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

## Features

- **PDF to Text Conversion**: Extract text from PDF documents with advanced options
- **Excel to Parquet Conversion**: Convert Excel files (.xlsx) to Parquet format with multi-sheet support
- **XML to Parquet Conversion**: Intelligent XML flattening with automatic structure detection and configurable strategies
- **Database File Conversion**: Convert Microsoft Access (.mdb/.accdb) and DBF files to Parquet
- **CSV to Parquet Conversion**: Smart delimiter detection and encoding handling
- **Rich CLI Interface**: Beautiful terminal output with progress bars and tables
- **Intelligent Processing**: Automatic encoding detection, structure analysis, and column matching
- **Extensible Architecture**: Plugin-based system for adding new format converters
- **Metadata Extraction**: Get detailed information about your files
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### From PyPI

```bash
pip install pyforge-cli
```

### From Source

```bash
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI
pip install -e ".[dev,test]"
```

### System Dependencies

For MDB/Access file support on non-Windows systems:

```bash
# Ubuntu/Debian
sudo apt-get install mdbtools

# macOS
brew install mdbtools
```

## Quick Start

### Convert PDF to Text

```bash
# Convert entire PDF
pyforge convert document.pdf

# Convert to specific output file
pyforge convert document.pdf output.txt

# Convert specific page range
pyforge convert document.pdf --pages "1-5"

# Include page metadata
pyforge convert document.pdf --metadata
```

### Convert Excel to Parquet

```bash
# Convert Excel file to Parquet
pyforge convert data.xlsx

# Convert with specific compression
pyforge convert data.xlsx --compression gzip

# Convert specific sheets only
pyforge convert data.xlsx --sheets "Sheet1,Sheet3"
```

### Convert Database Files

```bash
# Convert Access database to Parquet
pyforge convert database.mdb

# Convert DBF file with encoding detection
pyforge convert data.dbf

# Convert with custom output directory
pyforge convert database.accdb output_folder/
```

### Convert CSV Files

```bash
# Convert CSV with automatic delimiter and encoding detection
pyforge convert data.csv

# Convert TSV (tab-separated) file
pyforge convert data.tsv

# Convert with compression
pyforge convert sales_data.csv --compression gzip

# Convert delimited text file
pyforge convert export.txt
```

### Convert XML Files

```bash
# Convert XML with automatic structure detection
pyforge convert data.xml

# Convert with aggressive flattening for analytics
pyforge convert catalog.xml --flatten-strategy aggressive

# Handle arrays by expanding to multiple rows
pyforge convert orders.xml --array-handling expand

# Strip namespaces for cleaner column names
pyforge convert api_response.xml --namespace-handling strip

# Preview schema before conversion
pyforge convert complex.xml --preview-schema
```

### Get File Information

```bash
# Display file metadata as table
pyforge info document.pdf

# Get Excel file information
pyforge info spreadsheet.xlsx

# Output metadata as JSON
pyforge info database.mdb --format json
```

### List Supported Formats

```bash
pyforge formats
```

### Validate Files

```bash
pyforge validate document.pdf
pyforge validate data.xlsx
```

## Usage Examples

### Basic PDF Conversion

```bash
# Convert PDF to text (creates report.txt in same directory)
pyforge convert report.pdf

# Convert with custom output path
pyforge convert report.pdf /path/to/output.txt

# Convert with verbose output
pyforge convert report.pdf --verbose

# Force overwrite existing file
pyforge convert report.pdf output.txt --force
```

### Advanced PDF Options

```bash
# Convert pages 1-10
pyforge convert document.pdf --pages "1-10"

# Convert from page 5 to end
pyforge convert document.pdf --pages "5-"

# Convert up to page 10
pyforge convert document.pdf --pages "-10"

# Include page markers in output
pyforge convert document.pdf --metadata
```

### Excel Conversion Examples

```bash
# Convert Excel with all sheets
pyforge convert sales_data.xlsx

# Interactive mode - prompts for sheet selection
pyforge convert multi_sheet.xlsx --interactive

# Convert sheets with matching columns into single file
pyforge convert monthly_reports.xlsx --merge-sheets

# Generate summary report
pyforge convert data.xlsx --summary
```

### Database Conversion Examples

```bash
# Convert Access database (all tables)
pyforge convert company.mdb

# Convert with progress tracking
pyforge convert large_database.accdb --verbose

# Convert DBF with specific encoding
pyforge convert legacy.dbf --encoding cp1252

# Batch convert all DBF files in directory
for file in *.dbf; do pyforge convert "$file"; done
```

### CSV Conversion Examples

```bash
# Convert CSV with automatic detection
pyforge convert sales_data.csv

# Convert international CSV with auto-encoding detection
pyforge convert european_data.csv --verbose

# Convert semicolon-delimited CSV (European format)
pyforge convert data_semicolon.csv

# Convert tab-separated file with compression
pyforge convert data.tsv --compression gzip

# Batch convert multiple CSV files
for file in *.csv; do pyforge convert "$file" --compression snappy; done
```

### XML Conversion Examples

```bash
# Convert XML with automatic structure detection
pyforge convert catalog.xml

# Convert with aggressive flattening for data analysis
pyforge convert api_response.xml --flatten-strategy aggressive

# Handle arrays as concatenated strings
pyforge convert orders.xml --array-handling concatenate

# Strip namespaces for cleaner output
pyforge convert soap_response.xml --namespace-handling strip

# Preview structure before conversion
pyforge convert complex_structure.xml --preview-schema

# Convert compressed XML files
pyforge convert data.xml.gz --verbose

# Batch convert XML files with specific strategy
for file in *.xml; do pyforge convert "$file" --flatten-strategy moderate; done
```

### File Information

```bash
# Show file metadata
pyforge info document.pdf

# Excel file details (sheets, row counts)
pyforge info spreadsheet.xlsx

# Database file information (tables, record counts)
pyforge info database.mdb

# Export metadata as JSON
pyforge info document.pdf --format json > metadata.json
```

## Supported Formats

| Input Format | Output Formats | Status |
|-------------|----------------|---------|
| PDF (.pdf)  | Text (.txt)    | ✅ Available |
| Excel (.xlsx) | Parquet (.parquet) | ✅ Available |
| XML (.xml, .xml.gz, .xml.bz2) | Parquet (.parquet) | ✅ Available |
| Access (.mdb/.accdb) | Parquet (.parquet) | ✅ Available |
| DBF (.dbf)  | Parquet (.parquet) | ✅ Available |
| CSV (.csv, .tsv, .txt) | Parquet (.parquet) | ✅ Available |

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI

# Set up development environment
pip install -e ".[dev,test]"

# Run tests
pytest

# Format code
black src tests

# Run all checks
ruff check src tests
```

### Development Commands

```bash
# Testing
pytest                                    # Run tests
pytest --cov=pyforge_cli                 # Run tests with coverage

# Code Quality
black src tests                          # Format code
ruff check src tests                     # Run linting
mypy src                                 # Type checking

# Building
python -m build                          # Build distribution packages
twine upload dist/*                      # Publish to PyPI
```

### Project Structure

```text
PyForge-CLI/
├── src/pyforge_cli/            # Main package
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── converters/             # Format converters
│   │   ├── __init__.py
│   │   ├── base.py            # Base converter class
│   │   ├── pdf_converter.py   # PDF to text conversion
│   │   ├── excel_converter.py # Excel to Parquet conversion
│   │   ├── mdb_converter.py   # MDB/ACCDB to Parquet conversion
│   │   └── dbf_converter.py   # DBF to Parquet conversion
│   ├── plugins/               # Plugin system
│   │   └── loader.py          # Plugin loading
│   └── utils/                 # Utilities
│       ├── file_utils.py      # File operations
│       └── cli_utils.py       # CLI helpers
├── docs/                      # Documentation source
├── tests/                     # Test files
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Requirements

- Python 3.8+
- PyMuPDF (for PDF processing)
- Click (for CLI interface)
- Rich (for beautiful terminal output)
- Pandas & PyArrow (for data processing and Parquet support)
- pandas-access (for MDB file support)
- dbfread (for DBF file support)
- openpyxl (for Excel file support)
- chardet (for encoding detection)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check src tests`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

### Version 0.2.0 - Database & Spreadsheet Support (Completed)
- ✅ **Excel to Parquet Conversion**
  - Multi-sheet support with intelligent detection
  - Interactive sheet selection mode
  - Column matching for combined output
  - Progress tracking and summary reports
- ✅ **MDB/ACCDB to Parquet Conversion**
  - Microsoft Access database support (.mdb, .accdb)
  - Automatic table discovery
  - Cross-platform compatibility (Windows/Linux/macOS)
  - Excel summary reports with sample data
- ✅ **DBF to Parquet Conversion**
  - Automatic encoding detection
  - Support for various DBF formats
  - Robust error handling for corrupted files

### Version 0.3.0 - Enhanced Features (Released)
- ✅ **XML to Parquet Conversion**
  - Automatic XML structure detection and analysis
  - Intelligent flattening strategies (conservative, moderate, aggressive)
  - Array handling modes (expand, concatenate, json_string)
  - Namespace processing (preserve, strip, prefix)
  - Schema preview before conversion
  - Support for compressed XML files (.xml.gz, .xml.bz2)
- ✅ **CSV to Parquet conversion** with auto-detection (string-based)
- [ ] CSV schema inference and native type conversion
- [ ] JSON processing and flattening
- [ ] Data validation and cleaning options
- [ ] Batch processing with pattern matching
- [ ] Configuration file support
- [ ] REST API wrapper for notebook integration
- [ ] Data type preservation options (beyond string conversion)

### Version 0.4.0 - Advanced Features (Future)
- [ ] SQL query support for database files
- [ ] Data transformation pipelines
- [ ] Cloud storage integration (S3, Azure Blob)
- [ ] Incremental/delta conversions
- [ ] Custom plugin development SDK

## Support

If you encounter any issues or have questions:

1. Check the [📚 Complete Documentation](https://py-forge-cli.github.io/PyForge-CLI/)
2. Search [existing issues](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)
3. Create a [new issue](https://github.com/Py-Forge-Cli/PyForge-CLI/issues/new)
4. Join the [discussion](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions)

## Changelog

### 0.3.0 (Current Release)

- ✅ **XML to Parquet Converter**: Complete implementation with intelligent flattening
- ✅ **Automatic Structure Detection**: Analyzes XML hierarchy and array patterns
- ✅ **Flexible Flattening Strategies**: Conservative, moderate, and aggressive options
- ✅ **Advanced Array Handling**: Expand, concatenate, or JSON string modes
- ✅ **Namespace Support**: Configurable namespace processing
- ✅ **Schema Preview**: Optional structure preview before conversion
- ✅ **Comprehensive Documentation**: User guide and quick reference
- ✅ **Compressed XML Support**: Handles .xml.gz and .xml.bz2 files

### 0.2.1

- ✅ **Complete Documentation Site**: Comprehensive GitHub Pages documentation
- ✅ **Fixed CI/CD**: GitHub Actions workflow for automated PyPI publishing  
- ✅ **Improved Distribution**: API token authentication and automation
- ✅ **Better Navigation**: Fixed broken links and improved project structure

### 0.2.0 (Current Release)

- ✅ Excel to Parquet conversion with multi-sheet support
- ✅ MDB/ACCDB to Parquet conversion with cross-platform support
- ✅ DBF to Parquet conversion with encoding detection
- ✅ Interactive mode for Excel sheet selection
- ✅ Automatic table discovery for database files
- ✅ Progress tracking with rich terminal UI
- ✅ Excel summary reports for batch conversions
- ✅ Robust error handling and recovery

### 0.1.0 (Initial Release)

- PDF to text conversion
- CLI interface with Click
- Rich terminal output
- File metadata extraction
- Page range support
- Development tooling setup
