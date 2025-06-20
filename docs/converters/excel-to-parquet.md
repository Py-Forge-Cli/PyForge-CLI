# Excel to Parquet Conversion

Convert Excel spreadsheets (.xlsx files) to efficient Parquet format with multi-sheet support and intelligent data processing.

## Overview

PyForge CLI provides powerful Excel to Parquet conversion capabilities with:

- **Multi-sheet processing** with automatic detection
- **Interactive sheet selection** for complex workbooks
- **Column matching** for combining similar sheets
- **Data type preservation** and optimization
- **Compression options** for space efficiency
- **Progress tracking** with detailed reports

## Basic Usage

### Convert Single Excel File

```bash
# Convert entire Excel workbook
pyforge convert data.xlsx

# Output: data.parquet (if single sheet) or data/ directory (if multiple sheets)
```

### Convert with Custom Output

```bash
# Specify output file/directory
pyforge convert sales_data.xlsx reports/sales.parquet

# Convert to specific directory
pyforge convert monthly_data.xlsx output_folder/
```

## Advanced Options

### Sheet Selection

=== "All Sheets"
    ```bash
    # Convert all sheets (default behavior)
    pyforge convert workbook.xlsx
    ```

=== "Specific Sheets"
    ```bash
    # Convert only specified sheets
    pyforge convert workbook.xlsx --sheets "Sheet1,Summary,Data"
    ```

=== "Interactive Mode"
    ```bash
    # Interactive sheet selection
    pyforge convert workbook.xlsx --interactive
    ```

### Compression Options

```bash
# Use GZIP compression (recommended)
pyforge convert data.xlsx --compression gzip

# Use Snappy compression (faster)
pyforge convert data.xlsx --compression snappy

# No compression
pyforge convert data.xlsx --compression none
```

### Advanced Processing

```bash
# Merge sheets with matching columns
pyforge convert quarterly_reports.xlsx --merge-sheets

# Generate Excel summary report
pyforge convert data.xlsx --summary

# Force overwrite existing files
pyforge convert data.xlsx --force

# Verbose output for debugging
pyforge convert data.xlsx --verbose
```

## Multi-Sheet Processing

### Automatic Detection

PyForge automatically detects and handles multiple sheets:

```bash
# Input: sales_2023.xlsx (3 sheets: Q1, Q2, Q3)
pyforge convert sales_2023.xlsx

# Output: sales_2023/ directory containing:
#   ├── Q1.parquet
#   ├── Q2.parquet
#   ├── Q3.parquet
#   └── _summary.xlsx  # Optional summary report
```

### Column Matching

When sheets have similar structures, merge them:

```bash
# Combine sheets with matching columns
pyforge convert monthly_data.xlsx --merge-sheets

# Output: Single parquet file with combined data
```

### Interactive Selection

For complex workbooks, use interactive mode:

```bash
pyforge convert complex_workbook.xlsx --interactive
```

This will prompt you to:
1. Select which sheets to convert
2. Choose output format (separate files or combined)
3. Set column matching preferences

## Output Formats

### Single Sheet Workbooks

```
Input:  report.xlsx (1 sheet)
Output: report.parquet
```

### Multi-Sheet Workbooks

```
Input:  quarterly.xlsx (4 sheets)
Output: quarterly/ directory
        ├── Q1_Data.parquet
        ├── Q2_Data.parquet  
        ├── Q3_Data.parquet
        ├── Q4_Data.parquet
        └── _summary.xlsx
```

### Merged Output

```bash
pyforge convert monthly.xlsx --merge-sheets
# Output: monthly_merged.parquet
```

## Data Type Handling

PyForge converts all Excel data to string format for maximum compatibility:

| Excel Type | Parquet Type | Notes |
|------------|--------------|-------|
| Numbers | string | Decimal precision preserved up to 27 places |
| Dates | string | ISO 8601 format (YYYY-MM-DDTHH:MM:SS) |
| Text | string | UTF-8 encoding |
| Formulas | string | Formulas are evaluated, results stored as strings |
| Boolean | string | "True" or "False" string values |
| Merged Cells | string | First cell value, warns about merged cells |

!!! note "String-Based Conversion"
    PyForge CLI currently uses a string-based conversion approach to ensure consistent behavior across all database formats (Excel, MDB, DBF). While this preserves data integrity and precision, you may need to cast types in your analysis tools (pandas, Spark, etc.) if you require native numeric or datetime types.

## Performance Optimization

### Large Files

```bash
# For very large Excel files
pyforge convert huge_file.xlsx --chunk-size 10000

# Use efficient compression
pyforge convert large_data.xlsx --compression gzip
```

### Memory Management

```bash
# Process sheets individually to save memory
pyforge convert workbook.xlsx --no-merge-sheets

# Limit concurrent processing
pyforge convert workbook.xlsx --max-workers 2
```

## Error Handling

### Common Issues

**Empty Sheets**: Automatically skipped with warning
```bash
# Shows warning but continues processing
pyforge convert workbook.xlsx
# Warning: Sheet 'Empty_Sheet' is empty, skipping...
```

**Merged Cells**: Handled gracefully
```bash
# Warns about data loss potential
pyforge convert report.xlsx
# Warning: Merged cells detected in 'Summary' sheet
```

**Formula Errors**: Converts error values to null
```bash
# #DIV/0!, #N/A become null values in Parquet
pyforge convert calculations.xlsx
```

## Validation

### File Information

```bash
# Get Excel file details before conversion
pyforge info spreadsheet.xlsx
```

Output shows:
- Number of sheets
- Row counts per sheet
- Column information
- Data types summary

### Verify Conversion

```bash
# Check converted file
pyforge info output.parquet

# Compare row counts
pyforge validate output.parquet --source spreadsheet.xlsx
```

## Examples

### Business Reports

```bash
# Convert financial reports
pyforge convert "Q4_Financial_Report.xlsx" \
  --sheets "Income_Statement,Balance_Sheet" \
  --compression gzip \
  --summary

# Output:
#   Q4_Financial_Report/
#   ├── Income_Statement.parquet
#   ├── Balance_Sheet.parquet
#   └── _summary.xlsx
```

### Data Analysis Pipeline

```bash
# Convert multiple files for analysis
for file in data/*.xlsx; do
  pyforge convert "$file" --merge-sheets --compression snappy
done

# Result: Efficient parquet files ready for pandas/spark
```

### ETL Workflow

```bash
# Convert with validation
pyforge convert source_data.xlsx \
  --verbose \
  --summary \
  && echo "Conversion successful" \
  || echo "Conversion failed"
```

## Integration

### Python Integration

```python
import pandas as pd

# Read converted parquet file
df = pd.read_parquet('converted_data.parquet')

# Convert string columns to appropriate types
def convert_types(df):
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
df = convert_types(df)

# Multiple sheets with type conversion
import os
parquet_dir = 'multi_sheet_data/'
sheets = {}
for file in os.listdir(parquet_dir):
    if file.endswith('.parquet'):
        sheet_name = file.replace('.parquet', '')
        df = pd.read_parquet(f'{parquet_dir}/{file}')
        sheets[sheet_name] = convert_types(df)
```

### Spark Integration

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import *

spark = SparkSession.builder.appName("ExcelData").getOrCreate()

# Read parquet file (all columns will be strings)
df = spark.read.parquet('converted_data.parquet')

# Convert specific columns to appropriate types
df_typed = df.select(
    col("id").cast(IntegerType()).alias("id"),
    col("amount").cast(DoubleType()).alias("amount"), 
    col("date").cast(TimestampType()).alias("date"),
    col("description")  # Keep as string
)

df_typed.show()
```

## Troubleshooting

### Common Solutions

**Permission Errors**:
```bash
# Ensure file isn't open in Excel
pyforge convert data.xlsx --force
```

**Memory Issues**:
```bash
# Process sheets separately
pyforge convert large_file.xlsx --no-merge-sheets
```

**Encoding Problems**:
```bash
# Force UTF-8 encoding
pyforge convert data.xlsx --encoding utf-8
```

### Debug Mode

```bash
# Get detailed processing information
pyforge convert data.xlsx --verbose --debug
```

## Best Practices

1. **Preview First**: Use `pyforge info` to understand your Excel structure
2. **Use Compression**: GZIP provides good balance of size and speed
3. **Validate Output**: Check row counts and data types after conversion
4. **Interactive Mode**: Use for complex workbooks you haven't seen before
5. **Batch Processing**: Convert multiple files using shell loops or scripts

## Performance Notes

- **Sheet Processing**: Parallel processing for multiple sheets
- **Memory Efficient**: Streams data to avoid loading entire file in memory
- **Compression**: Significant space savings with GZIP compression
- **Type Optimization**: Automatically optimizes data types for Parquet format

For more advanced usage, see the [CLI Reference](../reference/cli-reference.md) for complete option details.