# PyForge CLI

A powerful command-line tool for data format conversion and manipulation, built with Python and Click.

## Features

- **PDF to Text Conversion**: Extract text from PDF documents with advanced options
- **Excel to Parquet Conversion**: Convert Excel files (.xlsx) to Parquet format with multi-sheet support
- **Database File Conversion**: Convert Microsoft Access (.mdb/.accdb) and DBF files to Parquet
- **Rich CLI Interface**: Beautiful terminal output with progress bars and tables
- **Intelligent Processing**: Automatic encoding detection, table discovery, and column matching
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
git clone https://github.com/yourusername/pyforge-cli.git
cd pyforge-cli
make install
```

### Development Installation

```bash
git clone https://github.com/yourusername/pyforge-cli.git
cd pyforge-cli
make setup-dev
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
| Access (.mdb/.accdb) | Parquet (.parquet) | ✅ Available |
| DBF (.dbf)  | Parquet (.parquet) | ✅ Available |
| CSV (.csv)  | Parquet (.parquet) | 🚧 Coming Soon |

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/pyforge-cli.git
cd pyforge-cli

# Set up development environment
make setup-dev

# Run tests
make test

# Format code
make format

# Run all checks
make pre-commit
```

### Available Make Commands

```bash
make help              # Show all available commands
make install          # Install package
make install-dev      # Install with development dependencies
make test             # Run tests
make test-cov         # Run tests with coverage
make lint             # Run linting
make format           # Format code
make type-check       # Run type checking
make build            # Build distribution packages
make publish-test     # Publish to Test PyPI
make publish          # Publish to PyPI
make clean            # Clean build artifacts
```

### Project Structure

```text
pyforge-cli/
├── src/cortexpy_cli/
│   ├── __init__.py
│   ├── main.py                  # CLI entry point
│   ├── converters/
│   │   ├── __init__.py
│   │   ├── base.py             # Base converter class
│   │   ├── converter_factory.py # Factory pattern implementation
│   │   ├── pdf_converter.py    # PDF to text conversion
│   │   ├── excel_converter.py  # Excel to Parquet conversion
│   │   ├── mdb_converter.py    # MDB/ACCDB to Parquet conversion
│   │   └── dbf_converter.py    # DBF to Parquet conversion
│   ├── plugins/
│   │   └── loader.py           # Plugin loading system
│   └── utils/
│       ├── file_utils.py       # File type detection
│       └── cli_utils.py        # CLI formatting utilities
├── tests/                      # Test files
├── pyproject.toml             # Project configuration
├── Makefile                   # Development commands
└── README.md                  # This file
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
4. Run tests and linting (`make pre-commit`)
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

### Version 0.3.0 - Enhanced Features (Planned)
- [ ] CSV to Parquet conversion with schema inference
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

1. Check the [documentation](https://github.com/yourusername/cortexpy-cli/wiki)
2. Search [existing issues](https://github.com/yourusername/cortexpy-cli/issues)
3. Create a [new issue](https://github.com/yourusername/cortexpy-cli/issues/new)

## Changelog

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
