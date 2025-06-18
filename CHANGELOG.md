# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-06-18

### Added
- **Core Features**
  - PDF to text conversion with PyMuPDF backend
  - Rich CLI interface with Click framework
  - Beautiful terminal output with progress bars
  - File validation and metadata extraction
  - Page range selection for PDF processing
  - Extensible plugin architecture for future format support

- **CLI Commands**
  - `convert` - Convert files between formats with advanced options
  - `info` - Display file metadata in table or JSON format
  - `validate` - Check if files can be processed
  - `formats` - List all supported input/output formats

- **Advanced Features**
  - Automatic output path generation in same directory as input
  - Verbose mode with detailed progress information
  - Force overwrite option for existing files
  - Support for complex filenames with spaces and dots
  - Plugin discovery and loading system

- **Documentation**
  - Comprehensive CLI help system with detailed examples
  - Complete README with usage guide
  - Extensive testing documentation (TESTING.md)
  - Example scripts and demonstrations

- **Development Tools**
  - UV package management with fast dependency resolution
  - Complete test suite with pytest and coverage
  - Code quality tools: Black, Ruff, MyPy
  - Makefile with development and deployment commands
  - PyPI-ready distribution setup

- **Testing Infrastructure**
  - Automated test scripts for local verification
  - Comprehensive test suite with 94% coverage on core functionality
  - Output path behavior testing and validation
  - Cross-platform compatibility testing

### Technical Details
- **Dependencies**: Click 8.0+, Rich 13.0+, PyMuPDF 1.23+, tqdm 4.64+
- **Python Support**: 3.8+
- **Package Format**: Modern pyproject.toml configuration
- **Architecture**: Plugin-based converter system with registry pattern

### Performance
- **Small PDFs** (< 1MB): Near-instant conversion
- **Medium PDFs** (1-10MB): 1-5 seconds with progress tracking
- **Large PDFs** (> 10MB): Efficient streaming with memory management

### Behavior Changes
- Output files are created in the same directory as input files by default
- When no output path specified, preserves original filename with new extension
- Explicit output paths override default behavior
- Verbose mode shows auto-generated output paths

## [Unreleased]

### Planned Features
- CSV to Parquet conversion
- DBF file support
- Excel file processing
- JSON data manipulation
- Batch processing capabilities
- Configuration file support
- Additional output formats
- Performance optimizations

---

## Migration Guide

### From Command Line Tools
If you're migrating from other PDF processing tools:

```bash
# Instead of: pdftotext document.pdf output.txt
cortexpy convert document.pdf output.txt

# Instead of: pdfinfo document.pdf
cortexpy info document.pdf

# New capabilities
cortexpy convert document.pdf --pages "1-5"
cortexpy info document.pdf --format json
```

### For Developers
The plugin system allows easy extension:

```python
from cortexpy_cli.converters.base import BaseConverter
from cortexpy_cli.plugins import registry

class MyConverter(BaseConverter):
    def __init__(self):
        super().__init__()
        self.supported_inputs = {'.myformat'}
        self.supported_outputs = {'.txt', '.json'}
    
    def convert(self, input_path, output_path, **options):
        # Your conversion logic here
        return True

# Register the converter
registry.register('my_converter', MyConverter)
```

## Support

- **Documentation**: See README.md and docs/USAGE.md
- **Issues**: Report bugs and feature requests on GitHub
- **Testing**: Use provided test scripts for local verification
- **Development**: Follow contribution guidelines in the project repository