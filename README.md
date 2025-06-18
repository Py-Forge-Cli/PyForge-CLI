# CortexPy CLI

A powerful command-line tool for data format conversion and manipulation, built with Python and Click.

## Features

- **PDF to Text Conversion**: Extract text from PDF documents with advanced options
- **Rich CLI Interface**: Beautiful terminal output with progress bars and tables
- **Extensible Architecture**: Plugin-based system for adding new format converters
- **Metadata Extraction**: Get detailed information about your files
- **Page Range Support**: Convert specific page ranges from PDF documents
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### From PyPI

```bash
pip install cortexpy-cli
```

### From Source

```bash
git clone https://github.com/yourusername/cortexpy-cli.git
cd cortexpy-cli
make install
```

### Development Installation

```bash
git clone https://github.com/yourusername/cortexpy-cli.git
cd cortexpy-cli
make setup-dev
```

## Quick Start

### Convert PDF to Text

```bash
# Convert entire PDF
cortexpy convert document.pdf

# Convert to specific output file
cortexpy convert document.pdf output.txt

# Convert specific page range
cortexpy convert document.pdf --pages "1-5"

# Include page metadata
cortexpy convert document.pdf --metadata
```

### Get File Information

```bash
# Display file metadata as table
cortexpy info document.pdf

# Output metadata as JSON
cortexpy info document.pdf --format json
```

### List Supported Formats

```bash
cortexpy formats
```

### Validate Files

```bash
cortexpy validate document.pdf
```

## Usage Examples

### Basic PDF Conversion

```bash
# Convert PDF to text (creates report.txt in same directory)
cortexpy convert report.pdf

# Convert with custom output path
cortexpy convert report.pdf /path/to/output.txt

# Convert with verbose output
cortexpy convert report.pdf --verbose

# Force overwrite existing file
cortexpy convert report.pdf output.txt --force
```

### Advanced PDF Options

```bash
# Convert pages 1-10
cortexpy convert document.pdf --pages "1-10"

# Convert from page 5 to end
cortexpy convert document.pdf --pages "5-"

# Convert up to page 10
cortexpy convert document.pdf --pages "-10"

# Include page markers in output
cortexpy convert document.pdf --metadata
```

### File Information

```bash
# Show file metadata
cortexpy info document.pdf

# Export metadata as JSON
cortexpy info document.pdf --format json > metadata.json
```

## Supported Formats

| Input Format | Output Formats | Status |
|-------------|----------------|---------|
| PDF (.pdf)  | Text (.txt)    | ✅ Available |
| CSV (.csv)  | Parquet (.parquet) | 🚧 Coming Soon |
| DBF (.dbf)  | CSV (.csv), JSON (.json) | 🚧 Coming Soon |

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/cortexpy-cli.git
cd cortexpy-cli

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
cortexpy-cli/
├── src/cortexpy_cli/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   └── converters/
│       ├── __init__.py
│       ├── base.py          # Base converter class
│       └── pdf_converter.py # PDF conversion logic
├── tests/                   # Test files
├── pyproject.toml          # Project configuration
├── Makefile               # Development commands
└── README.md              # This file
```

## Requirements

- Python 3.8+
- PyMuPDF (for PDF processing)
- Click (for CLI interface)
- Rich (for beautiful terminal output)

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

- [ ] CSV to Parquet conversion
- [ ] DBF file support
- [ ] Excel file support
- [ ] JSON processing
- [ ] Data validation and cleaning
- [ ] Batch processing
- [ ] Configuration file support
- [ ] Plugin system for custom converters

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://github.com/yourusername/cortexpy-cli/wiki)
2. Search [existing issues](https://github.com/yourusername/cortexpy-cli/issues)
3. Create a [new issue](https://github.com/yourusername/cortexpy-cli/issues/new)

## Changelog

### 0.1.0 (Initial Release)

- PDF to text conversion
- CLI interface with Click
- Rich terminal output
- File metadata extraction
- Page range support
- Development tooling setup
