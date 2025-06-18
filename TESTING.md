# CortexPy CLI - Local Testing Guide

Complete guide for testing the CortexPy CLI tool locally before distribution.

## 🚀 Quick Start Testing

### 1. **Basic Functionality Test**

```bash
# Test CLI is working
uv run cortexpy --version
uv run cortexpy --help

# Test format listing
uv run cortexpy formats

# Test help for all commands
uv run cortexpy convert --help
uv run cortexpy info --help
uv run cortexpy validate --help
```

### 2. **Automated Test Scripts**

We've created several test scripts for different scenarios:

```bash
# Quick automated test (recommended)
python simple_test.py

# Comprehensive test suite
./test_locally.sh

# Run actual test suite
make test
```

## 📄 **PDF Testing (Primary Feature)**

### Find Test PDF Files

The tool automatically looks for PDF files in common locations:
- Current directory
- `~/Downloads/`
- `~/Documents/`
- `~/Desktop/`

### Manual PDF Testing

```bash
# 1. Copy any PDF to current directory
cp ~/Downloads/your_file.pdf test.pdf

# 2. Validate the PDF
uv run cortexpy validate test.pdf

# 3. Extract metadata
uv run cortexpy info test.pdf
uv run cortexpy info test.pdf --format json

# 4. Convert to text
uv run cortexpy convert test.pdf

# 5. Test page ranges
uv run cortexpy convert test.pdf page1.txt --pages "1"
uv run cortexpy convert test.pdf first5.txt --pages "1-5"

# 6. Test with metadata markers
uv run cortexpy convert test.pdf with_meta.txt --metadata

# 7. Test verbose mode
uv run cortexpy --verbose convert test.pdf
```

## 🧪 **Comprehensive Testing Scenarios**

### Error Handling Tests

```bash
# Test with non-existent file (should fail gracefully)
uv run cortexpy validate nonexistent.pdf

# Test with unsupported format
echo "test" > test.txt
uv run cortexpy validate test.txt

# Test with corrupted PDF (create empty file with .pdf extension)
touch corrupted.pdf
uv run cortexpy validate corrupted.pdf
```

### Advanced Feature Testing

```bash
# Test different page ranges
uv run cortexpy convert test.pdf --pages "1"      # Single page
uv run cortexpy convert test.pdf --pages "1-3"    # Page range
uv run cortexpy convert test.pdf --pages "2-"     # From page 2 to end
uv run cortexpy convert test.pdf --pages "-5"     # First 5 pages

# Test force overwrite
uv run cortexpy convert test.pdf output.txt
uv run cortexpy convert test.pdf output.txt --force

# Test JSON metadata export
uv run cortexpy info test.pdf --format json > metadata.json
cat metadata.json | jq '.page_count'  # If you have jq installed
```

### Batch Processing Testing

```bash
# Test multiple files (if you have several PDFs)
for file in *.pdf; do
    echo "Processing: $file"
    uv run cortexpy validate "$file" && \
    uv run cortexpy convert "$file"
done

# Test with find command
find . -name "*.pdf" -exec uv run cortexpy validate {} \;
```

## 🔧 **Development Testing**

### Run Test Suite

```bash
# Install dev dependencies
uv sync --group dev

# Run tests with coverage
make test

# Run individual test categories
uv run pytest tests/ -v
uv run pytest tests/test_pdf_converter.py -v

# Code quality checks
make lint
make type-check
make format
```

### Build Testing

```bash
# Test build process
make build

# Verify build artifacts
ls -la dist/

# Test wheel installation (in separate environment)
pip install dist/cortexpy_cli-0.1.0-py3-none-any.whl
```

### Plugin System Testing

```bash
# Test plugin loading
uv run python -c "
from cortexpy_cli.plugins import plugin_loader, registry
plugin_loader.load_all()
print('Loaded plugins:', plugin_loader.get_loaded_plugins())
print('Formats:', registry.list_supported_formats())
"
```

## 📊 **Performance Testing**

### Large File Testing

```bash
# Test with large PDFs (if available)
uv run cortexpy --verbose convert large_document.pdf

# Test memory usage (macOS)
time uv run cortexpy convert large_document.pdf
```

### Benchmark Testing

```bash
# Time conversion
time uv run cortexpy convert test.pdf

# Compare with other tools (if available)
time pdftotext test.pdf comparison.txt
```

## 🐛 **Troubleshooting Tests**

### Dependency Issues

```bash
# Check Python environment
python --version
uv --version

# Verify dependencies
uv run python -c "import fitz; print('PyMuPDF:', fitz.__version__)"
uv run python -c "import click; print('Click:', click.__version__)"
uv run python -c "import rich; print('Rich:', rich.__version__)"
```

### Installation Issues

```bash
# Test clean installation
uv sync --reinstall

# Test from wheel
pip uninstall cortexpy-cli
pip install dist/cortexpy_cli-0.1.0-py3-none-any.whl
cortexpy --version
```

## 📱 **Platform-Specific Testing**

### macOS Testing

```bash
# Test with system PDFs
uv run cortexpy convert /System/Library/Documentation/Acknowledgments.pdf

# Test with Finder integration
open -a "Terminal" .
uv run cortexpy convert "file with spaces.pdf"
```

### Cross-Platform Testing

```bash
# Test path handling
uv run cortexpy convert "path/with/subdirs/file.pdf"

# Test Unicode handling
uv run cortexpy convert "файл.pdf"  # If you have non-ASCII filenames
```

## 🧩 **Integration Testing**

### Pipeline Testing

```bash
# Test with other CLI tools
uv run cortexpy convert test.pdf | head -10
uv run cortexpy convert test.pdf | wc -w
uv run cortexpy info test.pdf --format json | jq '.page_count'

# Test output redirection
uv run cortexpy convert test.pdf > output.txt
uv run cortexpy info test.pdf --format json > metadata.json
```

### Scripting Integration

```bash
# Test in shell scripts
#!/bin/bash
if uv run cortexpy validate "$1"; then
    uv run cortexpy convert "$1"
    echo "Conversion completed"
else
    echo "Invalid PDF file"
fi
```

## ✅ **Testing Checklist**

Before distribution, ensure all these tests pass:

- [ ] **Basic functionality**: `--version`, `--help`, `formats`
- [ ] **PDF validation**: Works with valid PDFs, rejects invalid files
- [ ] **PDF conversion**: Produces readable text output
- [ ] **Metadata extraction**: Returns accurate file information
- [ ] **Page ranges**: Correctly extracts specified pages
- [ ] **Error handling**: Graceful failure with helpful messages
- [ ] **Help system**: All commands show comprehensive help
- [ ] **Build system**: `make build` produces valid packages
- [ ] **Test suite**: All unit tests pass
- [ ] **Code quality**: Linting and type checking pass

## 🎯 **Expected Results**

### Successful Test Indicators

1. **Version check**: Returns `cortexpy, version 0.1.0`
2. **Format listing**: Shows PDF to TXT conversion support
3. **PDF validation**: ✓ or ✗ with appropriate message
4. **Text conversion**: Creates `.txt` file with extracted content
5. **Metadata**: Shows document properties in table or JSON format
6. **Error messages**: Clear, helpful error descriptions
7. **Progress bars**: Smooth progress indication for large files

### Performance Expectations

- **Small PDFs** (< 1MB): Near-instant conversion
- **Medium PDFs** (1-10MB): 1-5 seconds with progress bar
- **Large PDFs** (> 10MB): Progress tracking, reasonable memory usage

## 🔄 **Continuous Testing**

### During Development

```bash
# Quick development test
make pre-commit

# After changes
python simple_test.py
make test
```

### Before Releases

```bash
# Full test suite
./test_locally.sh
make all

# Clean build test
make clean
make build
```

This testing guide ensures your CortexPy CLI tool works correctly across different scenarios and edge cases before distribution!