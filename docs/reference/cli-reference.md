# CLI Command Reference

Complete reference for all PyForge CLI commands, options, and usage patterns.

## Main Commands

### `pyforge convert`

Convert files between different formats.

```bash
pyforge convert <input_file> [output_file] [options]
```

#### Examples

```bash
# Basic conversion
pyforge convert document.pdf

# With custom output
pyforge convert document.pdf extracted_text.txt

# PDF with page range
pyforge convert report.pdf --pages "1-10"

# Excel with specific sheets
pyforge convert data.xlsx --sheets "Sheet1,Summary"

# Database conversion
pyforge convert database.mdb output_directory/
```

#### Options

| Option | Type | Description | Applies To |
|--------|------|-------------|------------|
| `--pages <range>` | string | Page range to convert (e.g., "1-10") | PDF |
| `--metadata` | flag | Include file metadata in output | PDF |
| `--sheets <names>` | string | Comma-separated sheet names | Excel |
| `--combine` | flag | Combine sheets into single output | Excel |
| `--separate` | flag | Keep sheets as separate files | Excel |
| `--interactive` | flag | Interactive sheet selection | Excel |
| `--compression <type>` | string | Compression type (gzip, snappy, lz4) | Parquet outputs |
| `--encoding <encoding>` | string | Character encoding (e.g., cp1252) | DBF |
| `--tables <names>` | string | Comma-separated table names | MDB/ACCDB |
| `--password <password>` | string | Database password | MDB/ACCDB |
| `--force` | flag | Overwrite existing output files | All |
| `--verbose` | flag | Enable detailed output | All |

### `pyforge info`

Display detailed information about a file.

```bash
pyforge info <input_file> [options]
```

#### Examples

```bash
# Basic file information
pyforge info document.pdf

# Detailed information
pyforge info spreadsheet.xlsx --verbose

# JSON output format
pyforge info database.mdb --format json
```

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--format <type>` | string | Output format: table, json, yaml |
| `--verbose` | flag | Show detailed information |

### `pyforge validate`

Validate if a file can be processed by PyForge CLI.

```bash
pyforge validate <input_file> [options]
```

#### Examples

```bash
# Validate PDF file
pyforge validate document.pdf

# Validate with detailed output
pyforge validate spreadsheet.xlsx --verbose

# Batch validate files
for file in *.xlsx; do pyforge validate "$file"; done
```

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--verbose` | flag | Show detailed validation information |

### `pyforge formats`

List all supported input and output formats.

```bash
pyforge formats [options]
```

#### Examples

```bash
# List all formats
pyforge formats

# Show format details
pyforge formats --verbose

# Filter by input format
pyforge formats --input pdf
```

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--input <format>` | string | Filter by input format |
| `--output <format>` | string | Filter by output format |
| `--verbose` | flag | Show detailed format information |

## Global Options

These options work with all commands:

| Option | Description | Example |
|--------|-------------|---------|
| `--help, -h` | Show help message | `pyforge --help` |
| `--version` | Show version information | `pyforge --version` |
| `--verbose, -v` | Enable verbose output | `pyforge convert file.pdf --verbose` |

## Environment Variables

PyForge CLI recognizes these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PYFORGE_OUTPUT_DIR` | Default output directory | Current directory |
| `PYFORGE_TEMP_DIR` | Temporary file directory | System temp |
| `PYFORGE_MAX_MEMORY` | Maximum memory usage (MB) | Auto-detect |
| `PYFORGE_COMPRESSION` | Default compression for Parquet | snappy |

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | General Error | Unknown or general error |
| 2 | File Not Found | Input file does not exist |
| 3 | Permission Error | Cannot read input or write output |
| 4 | Format Error | Unsupported or corrupted file format |
| 5 | Validation Error | File failed validation |
| 6 | Memory Error | Insufficient memory for operation |

## Configuration File

PyForge CLI can use a configuration file for default settings:

**Location**: `~/.pyforge/config.yaml`

```yaml
# Default settings
defaults:
  compression: gzip
  output_dir: ~/conversions
  verbose: false

# PDF-specific settings
pdf:
  include_metadata: true
  
# Excel-specific settings
excel:
  combine_sheets: false
  compression: snappy

# Database settings
database:
  encoding: utf-8
```

## Advanced Usage Patterns

### Batch Processing

```bash
# Process all PDFs in directory
find . -name "*.pdf" -exec pyforge convert {} \;

# Convert with consistent naming
for file in *.xlsx; do
    pyforge convert "$file" "${file%.xlsx}.parquet"
done

# Parallel processing
ls *.pdf | xargs -P 4 -I {} pyforge convert {}
```

### Pipeline Integration

```bash
# Use in shell pipeline
pyforge info *.xlsx | grep "Sheets:" | wc -l

# With other tools
find /data -name "*.mdb" | while read file; do
    pyforge convert "$file" && echo "Converted: $file"
done
```

### Error Handling

```bash
# Check exit code
if pyforge convert file.pdf; then
    echo "Conversion successful"
else
    echo "Conversion failed with code $?"
fi

# Conditional processing
pyforge validate file.xlsx && pyforge convert file.xlsx
```

## Format-Specific Examples

### PDF Processing

```bash
# Extract specific pages
pyforge convert manual.pdf chapter1.txt --pages "1-25"

# Include metadata and page markers
pyforge convert report.pdf --metadata --pages "1-10"

# Process multiple page ranges
pyforge convert book.pdf intro.txt --pages "1-5"
pyforge convert book.pdf content.txt --pages "6-200"
pyforge convert book.pdf appendix.txt --pages "201-"
```

### Excel Processing

```bash
# Interactive sheet selection
pyforge convert workbook.xlsx --interactive

# Specific sheets with compression
pyforge convert data.xlsx --sheets "Data,Summary" --compression gzip

# Combine all sheets
pyforge convert financial.xlsx combined.parquet --combine

# Separate files for each sheet
pyforge convert report.xlsx --separate
```

### Database Processing

```bash
# Convert with password
pyforge convert secure.mdb --password "secret123"

# Specific tables only
pyforge convert database.mdb --tables "customers,orders,products"

# Custom output directory
pyforge convert large.accdb /output/database/
```

### DBF Processing

```bash
# With specific encoding
pyforge convert legacy.dbf --encoding cp1252

# Force processing corrupted files
pyforge convert damaged.dbf --force

# Verbose output for debugging
pyforge convert complex.dbf --verbose
```

## Troubleshooting Commands

### Debug Information

```bash
# System information
pyforge --version
python --version
pip show pyforge-cli

# File analysis
pyforge info problematic_file.pdf --verbose
pyforge validate problematic_file.pdf --verbose

# Test with minimal options
pyforge convert test_file.pdf --verbose
```

### Common Issues

```bash
# Permission problems
sudo chown $USER output_directory/
chmod 755 output_directory/

# Memory issues
PYFORGE_MAX_MEMORY=1024 pyforge convert large_file.xlsx

# Encoding problems
pyforge convert file.dbf --encoding utf-8 --verbose
```

## Performance Monitoring

### Timing Commands

```bash
# Time conversion
time pyforge convert large_file.xlsx

# Monitor memory usage
/usr/bin/time -v pyforge convert file.mdb

# Progress tracking
pyforge convert large_file.pdf --verbose
```

### Optimization

```bash
# Use compression for large outputs
pyforge convert file.xlsx --compression gzip

# Process in chunks
pyforge convert large.pdf chunk1.txt --pages "1-100"
pyforge convert large.pdf chunk2.txt --pages "101-200"

# Parallel processing
ls *.dbf | xargs -P $(nproc) -I {} pyforge convert {}
```

## Integration Examples

### Makefile Integration

```makefile
%.txt: %.pdf
	pyforge convert $< $@

%.parquet: %.xlsx
	pyforge convert $< $@ --combine

all-pdfs: $(patsubst %.pdf,%.txt,$(wildcard *.pdf))
```

### Python Subprocess

```python
import subprocess
import json

def convert_file(input_path, output_path=None, **options):
    cmd = ["pyforge", "convert", input_path]
    if output_path:
        cmd.append(output_path)
    
    for key, value in options.items():
        cmd.append(f"--{key.replace('_', '-')}")
        if value is not True:
            cmd.append(str(value))
    
    return subprocess.run(cmd, capture_output=True, text=True)

def get_file_info(file_path):
    result = subprocess.run(
        ["pyforge", "info", file_path, "--format", "json"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.returncode == 0 else None
```

## See Also

- **[Options Matrix](options.md)** - All options organized by converter
- **[Output Formats](output-formats.md)** - Output format specifications
- **[Tutorials](../tutorials/index.md)** - Real-world usage examples
- **[Troubleshooting](../tutorials/troubleshooting.md)** - Common issues and solutions