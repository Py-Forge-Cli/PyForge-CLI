# CortexPy CLI - Usage Guide

Complete usage documentation for the CortexPy CLI data conversion tool.

## Table of Contents

- [Quick Start](#quick-start)
- [Commands Overview](#commands-overview)
- [Detailed Command Reference](#detailed-command-reference)
- [Examples](#examples)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Quick Start

```bash
# Install the tool
pip install cortexpy-cli

# List supported formats
cortexpy formats

# Convert a PDF to text
cortexpy convert document.pdf

# Convert XML to Parquet with intelligent flattening
cortexpy convert api_response.xml --flatten-strategy aggressive

# Convert Excel to Parquet
cortexpy convert spreadsheet.xlsx --format parquet

# Get file information
cortexpy info document.pdf

# Validate a file
cortexpy validate document.pdf
```

## Commands Overview

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `convert` | Convert files between formats | `--pages`, `--metadata`, `--force` |
| `info` | Display file metadata | `--format json` |
| `formats` | List supported formats | None |
| `validate` | Check file validity | None |

## Detailed Command Reference

### Global Options

```bash
cortexpy [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**
- `--version` - Show version and exit
- `-v, --verbose` - Enable detailed progress information
- `--help` - Show help and exit

### convert - File Conversion

Convert files between different formats with advanced options.

```bash
cortexpy convert [OPTIONS] INPUT_FILE [OUTPUT_FILE]
```

**Arguments:**
- `INPUT_FILE` - Path to input file (required)
- `OUTPUT_FILE` - Path to output file (optional, auto-generated if not provided)

**Options:**
- `-f, --format [txt]` - Output format (default: txt)
- `-p, --pages RANGE` - Page range for PDF conversion
- `-m, --metadata` - Include page metadata in output
- `--force` - Overwrite existing files

**Page Range Examples:**
- `"5"` - Convert only page 5
- `"1-10"` - Convert pages 1 through 10
- `"5-"` - Convert from page 5 to end
- `"-10"` - Convert from start to page 10

### info - File Information

Display detailed file metadata and properties.

```bash
cortexpy info [OPTIONS] INPUT_FILE
```

**Arguments:**
- `INPUT_FILE` - Path to file to analyze

**Options:**
- `-f, --format [table|json]` - Output format (default: table)

**Output Formats:**
- `table` - Human-readable formatted table with colors
- `json` - Machine-readable JSON for scripting

### validate - File Validation

Check if files can be processed by the tool.

```bash
cortexpy validate [OPTIONS] INPUT_FILE
```

**Arguments:**
- `INPUT_FILE` - Path to file to validate

**Exit Codes:**
- `0` - File is valid and can be processed
- `1` - File is invalid or unsupported

### formats - Supported Formats

List all supported input and output format combinations.

```bash
cortexpy formats [OPTIONS]
```

**Output:**
- Table of converters and supported formats
- List of loaded plugins
- Format capability matrix

## Examples

### Basic PDF Conversion

```bash
# Convert entire PDF to text
cortexpy convert report.pdf

# Convert with custom output name
cortexpy convert report.pdf extracted_text.txt

# Convert with verbose output
cortexpy convert report.pdf --verbose
```

### Advanced PDF Processing

```bash
# Convert only specific pages
cortexpy convert document.pdf --pages "1-5"
cortexpy convert document.pdf --pages "10-"
cortexpy convert document.pdf --pages "-20"

# Include page metadata
cortexpy convert document.pdf --metadata

# Combine options
cortexpy convert document.pdf output.txt --pages "5-15" --metadata --force
```

### File Information and Metadata

```bash
# Display file info as table
cortexpy info document.pdf

# Export metadata as JSON
cortexpy info document.pdf --format json

# Save metadata to file
cortexpy info document.pdf --format json > metadata.json

# Extract specific metadata field
cortexpy info document.pdf --format json | jq '.page_count'
```

### Batch Processing

```bash
# Validate all PDFs in directory
for file in *.pdf; do
    cortexpy validate "$file" && echo "✓ $file is valid"
done

# Convert all valid PDFs
for file in *.pdf; do
    if cortexpy validate "$file" >/dev/null 2>&1; then
        cortexpy convert "$file"
    fi
done

# Process files with specific naming
find . -name "*.pdf" -exec cortexpy convert {} {}.txt \\;
```

### Scripting and Automation

```bash
#!/bin/bash
# Batch conversion script

INPUT_DIR="./pdfs"
OUTPUT_DIR="./text_files"

mkdir -p "$OUTPUT_DIR"

for pdf in "$INPUT_DIR"/*.pdf; do
    filename=$(basename "$pdf" .pdf)
    output="$OUTPUT_DIR/${filename}.txt"
    
    echo "Processing: $pdf"
    
    if cortexpy validate "$pdf"; then
        cortexpy convert "$pdf" "$output" --verbose
        echo "✓ Converted: $output"
    else
        echo "✗ Skipped invalid file: $pdf"
    fi
done
```

## Advanced Usage

### Working with Large Files

```bash
# Use verbose mode for progress tracking
cortexpy convert large_document.pdf --verbose

# Process in chunks by page range
cortexpy convert large_document.pdf part1.txt --pages "1-100"
cortexpy convert large_document.pdf part2.txt --pages "101-200"
```

### Metadata Extraction for Analysis

```bash
# Extract metadata from multiple files
for file in *.pdf; do
    echo "=== $file ==="
    cortexpy info "$file" --format json | jq '{
        title: .title,
        pages: .page_count,
        size: .file_size
    }'
done

# Create metadata summary
cortexpy info *.pdf --format json | jq -s 'map({
    file: input_filename,
    pages: .page_count,
    size: .file_size
})' > summary.json
```

### Integration with Other Tools

```bash
# Combine with grep for content search
cortexpy convert document.pdf && grep -i "keyword" document.txt

# Use with text analysis tools
cortexpy convert report.pdf | wc -w  # Word count
cortexpy convert report.pdf | head -n 20  # First 20 lines

# Pipeline processing
cortexpy convert document.pdf --pages "1-10" | \
    sed 's/[[:space:]]\+/ /g' | \
    tr '[:upper:]' '[:lower:]' > cleaned.txt
```

## Error Handling

### Common Issues and Solutions

**File not found:**
```bash
# Check file path
ls -la document.pdf
cortexpy validate document.pdf
```

**Unsupported format:**
```bash
# Check supported formats
cortexpy formats

# Verify file extension
file document.pdf
```

**Permission errors:**
```bash
# Check file permissions
ls -la document.pdf

# Fix permissions if needed
chmod 644 document.pdf
```

**Corrupted files:**
```bash
# Validate before processing
cortexpy validate document.pdf

# Check file integrity
file document.pdf
```

## Performance Tips

1. **Use page ranges** for large documents to process only needed sections
2. **Validate files first** in batch processing to skip invalid files
3. **Use verbose mode** for large files to monitor progress
4. **Process in parallel** for multiple files:

```bash
# GNU parallel example
parallel -j 4 cortexpy convert {} {.}.txt ::: *.pdf
```

## Plugin System

The tool supports plugins for extending format support:

```bash
# Check loaded plugins
cortexpy formats

# Plugins are automatically discovered from:
# - ~/.cortexpy/plugins/
# - Installed Python packages with cortexpy_cli entry points
```

## Getting Help

```bash
# General help
cortexpy --help

# Command-specific help
cortexpy convert --help
cortexpy info --help
cortexpy validate --help
cortexpy formats --help

# Show version
cortexpy --version
```

## Troubleshooting

### Debug Mode

```bash
# Enable verbose output for debugging
cortexpy convert document.pdf --verbose

# Check what formats are available
cortexpy formats
```

### Common Solutions

1. **Update the tool**: `pip install --upgrade cortexpy-cli`
2. **Check dependencies**: Ensure PyMuPDF is installed
3. **Verify Python version**: Requires Python 3.8+
4. **File permissions**: Ensure read access to input files
5. **Disk space**: Check available space for output files

### Getting Support

- Check the [documentation](README.md)
- Search [existing issues](https://github.com/yourusername/cortexpy-cli/issues)
- Create a [new issue](https://github.com/yourusername/cortexpy-cli/issues/new) with:
  - Command used
  - Error message
  - File information (`file yourfile.pdf`)
  - System information (`cortexpy --version`)