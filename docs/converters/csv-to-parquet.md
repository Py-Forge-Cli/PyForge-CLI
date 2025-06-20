# CSV to Parquet Conversion

Convert CSV, TSV, and delimited text files to efficient Parquet format with automatic delimiter and encoding detection.

## Overview

PyForge CLI provides intelligent CSV to Parquet conversion with:

- **Automatic delimiter detection** (comma, semicolon, tab, pipe)
- **Encoding auto-detection** (UTF-8, Latin-1, Windows-1252, UTF-16)
- **Header detection** and flexible handling
- **String-based conversion** for data consistency
- **Progress tracking** with detailed reports
- **Compression options** for optimal storage

## Basic Usage

### Simple Conversion

```bash
# Convert CSV file to Parquet
pyforge convert data.csv

# Output: data.parquet
```

### With Custom Output

```bash
# Specify output file
pyforge convert sales_data.csv reports/sales.parquet

# Convert to specific directory
pyforge convert dataset.csv processed/
```

## Auto-Detection Features

### Delimiter Detection

PyForge automatically detects common delimiters:

```bash
# Comma-separated (default)
pyforge convert data.csv

# Automatically detects semicolon
pyforge convert european_data.csv

# Automatically detects tab-separated
pyforge convert data.tsv

# Automatically detects pipe-separated
pyforge convert legacy_data.txt
```

**Supported Delimiters:**
- **Comma (,)**: Standard CSV format
- **Semicolon (;)**: European CSV format
- **Tab (\t)**: TSV format
- **Pipe (|)**: Legacy database exports

### Encoding Detection

Automatic encoding detection handles international data:

```bash
# UTF-8 files (default)
pyforge convert modern_data.csv

# Latin-1/ISO-8859-1 encoded files
pyforge convert european_legacy.csv

# Windows-1252 encoded files
pyforge convert windows_export.csv
```

**Supported Encodings:**
- **UTF-8**: Modern standard encoding
- **Latin-1 (ISO-8859-1)**: Western European
- **Windows-1252**: Windows default encoding
- **UTF-16**: Unicode with BOM

### Header Detection

Smart header detection:

```bash
# Files with headers (automatically detected)
pyforge convert data_with_headers.csv

# Files without headers (auto-generates column names)
pyforge convert raw_data.csv
```

## Advanced Options

### Compression Options

```bash
# Use GZIP compression (recommended for storage)
pyforge convert data.csv --compression gzip

# Use Snappy compression (default, faster)
pyforge convert data.csv --compression snappy

# No compression
pyforge convert data.csv --compression none
```

### Processing Options

```bash
# Force overwrite existing files
pyforge convert data.csv output.parquet --force

# Verbose output with detailed processing info
pyforge convert data.csv --verbose

# Specify output format explicitly
pyforge convert data.csv --format parquet
```

## Data Type Handling

PyForge converts all CSV data to string format for maximum compatibility:

| CSV Content | Parquet Type | Notes |
|-------------|--------------|-------|
| **Numbers** | string | Decimal precision preserved as text |
| **Dates** | string | Date format preserved as-is |
| **Text** | string | UTF-8 encoded |
| **Mixed Types** | string | No data type inference conflicts |
| **Empty Values** | string | Preserved as empty strings |
| **Special Characters** | string | International characters supported |

!!! note "String-Based Conversion"
    PyForge CLI uses a string-based conversion approach to ensure consistent behavior across all data formats (Excel, MDB, DBF, CSV). While this preserves data integrity and precision, you may need to cast types in your analysis tools (pandas, Spark, etc.) if you require native numeric or datetime types.

## File Format Support

### Input Formats

| Extension | Description | Auto-Detection |
|-----------|-------------|-----------------|
| **`.csv`** | Comma-Separated Values | ✅ Full support |
| **`.tsv`** | Tab-Separated Values | ✅ Full support |
| **`.txt`** | Delimited text files | ✅ Full support |

### Output Format

- **Parquet**: Columnar storage with compression and efficient analytics support

## Error Handling

### Common Issues and Solutions

**Encoding Problems**:
```bash
# PyForge automatically detects encoding
# If issues occur, check verbose output
pyforge convert problematic.csv --verbose
```

**Delimiter Detection Issues**:
```bash
# Check file content and delimiter detection
pyforge info suspicious.csv

# Use verbose mode to see detection details
pyforge convert file.csv --verbose
```

**Large Files**:
```bash
# Use compression for large files
pyforge convert huge_dataset.csv --compression gzip

# Monitor progress with verbose output
pyforge convert large_file.csv --verbose
```

**Mixed Encodings**:
```bash
# Auto-detection handles most cases
pyforge convert mixed_encoding.csv --verbose
```

## Validation and Inspection

### Pre-conversion Analysis

```bash
# Inspect CSV file structure
pyforge info dataset.csv
```

Shows:
- File size and estimated row count
- Detected encoding and confidence
- Detected delimiter and quote character
- Header detection status
- File modification date

### File Validation

```bash
# Validate CSV file before conversion
pyforge validate dataset.csv
```

## Performance Optimization

### Large File Processing

```bash
# Optimize for large CSV files
pyforge convert massive_dataset.csv \
  --compression gzip \
  --verbose

# Monitor memory usage and processing time
pyforge convert big_file.csv --verbose
```

### Batch Processing

```bash
# Convert multiple CSV files
for csv_file in data/*.csv; do
    echo "Converting: $csv_file"
    pyforge convert "$csv_file" \
      --compression gzip \
      --verbose
done
```

## Examples

### Business Data Processing

```bash
# Convert sales data with automatic detection
pyforge convert "Q4_Sales_Report.csv" \
  --compression gzip \
  --verbose

# Output includes detection details and conversion summary
```

### International Data

```bash
# Handle European CSV with semicolon delimiters
pyforge convert european_sales.csv \
  --verbose

# Automatic detection handles:
# - Semicolon delimiters
# - European encoding (Latin-1/Windows-1252)
# - International characters
```

### Legacy System Migration

```bash
# Convert old database exports
pyforge convert legacy_export.txt \
  --compression gzip \
  --force

# Handles various delimiters and encodings automatically
```

### Data Analysis Pipeline

```bash
# Convert for analysis workflow
pyforge convert raw_data.csv processed_data.parquet \
  --compression snappy \
  --verbose

# Result: Efficient Parquet file ready for pandas/Spark
```

## Integration Examples

### Python/Pandas

```python
import pandas as pd

# Read converted parquet file (all columns are strings)
df = pd.read_parquet('converted_data.parquet')

# Convert string columns to appropriate types
def convert_csv_types(df):
    for col in df.columns:
        # Try to convert to numeric (will stay string if not possible)
        df[col] = pd.to_numeric(df[col], errors='ignore')
        
        # Try to convert to datetime (will stay string if not possible)
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except:
                pass
    return df

# Apply type conversion
df = convert_csv_types(df)

# Now you can perform analysis with proper types
print(f"Records: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Data types after conversion:\n{df.dtypes}")
```

### Spark Integration

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import *

spark = SparkSession.builder.appName("CSVData").getOrCreate()

# Read converted parquet file (all columns are strings)
df = spark.read.parquet('converted_data.parquet')

# Convert specific columns to appropriate types
df_typed = df.select(
    col("id").cast(IntegerType()).alias("id"),
    col("amount").cast(DoubleType()).alias("amount"),
    col("date").cast(DateType()).alias("date"),
    col("description")  # Keep as string
)

df_typed.show()
```

## Troubleshooting

### Common Solutions

**File Not Recognized**:
```bash
# Check file extension and content
pyforge info unknown_file.txt
pyforge validate unknown_file.txt
```

**Detection Failures**:
```bash
# Use verbose mode to see detection process
pyforge convert file.csv --verbose

# Check file has content and proper structure
```

**Memory Issues**:
```bash
# Use compression to reduce memory usage
pyforge convert large_file.csv --compression gzip
```

**Character Encoding Issues**:
```bash
# Auto-detection usually handles this
# Check verbose output for encoding confidence
pyforge convert file.csv --verbose
```

### Debug Information

```bash
# Get detailed processing information
pyforge convert data.csv --verbose
```

This shows:
- Encoding detection process and confidence
- Delimiter detection results
- Header detection decision
- Row and column counts
- Conversion statistics
- Processing time

## Best Practices

1. **Use Verbose Mode**: Always use `--verbose` for important conversions to verify detection accuracy
2. **Validate First**: Use `pyforge info` and `pyforge validate` before converting critical data
3. **Choose Compression**: Use GZIP for storage, Snappy for speed
4. **Batch Process**: Convert multiple files using shell scripts for efficiency
5. **Verify Output**: Check converted data structure and content
6. **Handle Large Files**: Monitor memory usage for very large CSV files

## Character Encoding Reference

Common CSV encodings by source:

| Source | Encoding | Description |
|--------|----------|-------------|
| **Modern Systems** | UTF-8 | Unicode standard, handles all characters |
| **Windows Excel** | Windows-1252 | Windows default, Western European |
| **European Systems** | ISO-8859-1 (Latin-1) | Western European characters |
| **Legacy Systems** | ASCII | Basic English characters only |
| **International** | UTF-16 | Unicode with BOM marker |

For complete command options and advanced features, see the [CLI Reference](../reference/cli-reference.md).