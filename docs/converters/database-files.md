# MDB/ACCDB Database Conversion

Convert Microsoft Access database files (.mdb and .accdb) to efficient Parquet format with automatic table discovery and cross-platform support.

## Overview

PyForge CLI provides comprehensive Microsoft Access database conversion with:

- **Cross-platform support** (Windows, macOS, Linux)
- **Automatic table discovery** and metadata extraction
- **Batch table processing** with progress tracking
- **Excel summary reports** with sample data
- **Data type preservation** and optimization
- **Error handling** for corrupted or protected databases

## Supported Formats

| Format | Extension | Description | Support Level |
|--------|-----------|-------------|---------------|
| **Access 2000-2003** | `.mdb` | Legacy Jet database format | ✅ Full |
| **Access 2007+** | `.accdb` | Modern Access database format | ✅ Full |
| **Access Runtime** | `.mdb/.accdb` | Runtime-only databases | ✅ Full |

## Basic Usage

### Convert Entire Database

```bash
# Convert all tables in database
pyforge convert company.mdb

# Output: company/ directory with all tables as parquet files
```

### Convert with Custom Output

```bash
# Specify output directory
pyforge convert database.accdb reports/

# Convert to specific location
pyforge convert crm.mdb /data/converted/
```

## System Requirements

### Windows
```bash
# Native support - no additional setup required
pyforge convert database.mdb
```

### macOS
```bash
# Install mdbtools using Homebrew
brew install mdbtools

# Then convert normally
pyforge convert database.mdb
```

### Linux (Ubuntu/Debian)
```bash
# Install mdbtools
sudo apt-get install mdbtools

# Convert database
pyforge convert database.mdb
```

## Conversion Options

### Basic Conversion

=== "All Tables"
    ```bash
    # Convert all tables (default)
    pyforge convert inventory.mdb
    ```

=== "Specific Tables"
    ```bash
    # Convert only specified tables
    pyforge convert crm.accdb --tables "Customers,Orders,Products"
    ```

=== "With Summary"
    ```bash
    # Generate Excel summary report
    pyforge convert database.mdb --summary
    ```

### Advanced Options

```bash
# Verbose output for monitoring
pyforge convert large_db.accdb --verbose

# Force overwrite existing files
pyforge convert database.mdb --force

# Custom compression
pyforge convert data.accdb --compression gzip

# Include system tables (advanced)
pyforge convert db.mdb --include-system-tables
```

## Output Structure

### Standard Output

```
Input:  company.mdb
Output: company/
        ├── Customers.parquet
        ├── Orders.parquet
        ├── Products.parquet
        ├── Employees.parquet
        └── _summary.xlsx (if --summary used)
```

### Summary Report

The optional Excel summary includes:

- **Overview**: Table counts, record counts, conversion status
- **Schema**: Column names, types, nullable status for each table
- **Samples**: First 10 rows from each table for verification
- **Errors**: Any issues encountered during conversion

## Table Discovery

PyForge automatically discovers and processes:

### User Tables
- Regular data tables created by users
- Linked tables (converted if accessible)
- Views and queries (data only, not definitions)

### System Tables (Optional)
```bash
# Include Access system tables
pyforge convert db.mdb --include-system-tables
```

### Table Information Display
```bash
# List tables without converting
pyforge info database.accdb
```

Shows:
- Table names and record counts
- Column information and data types
- Relationships and constraints
- Database version and properties

## Data Type Mapping

PyForge handles Access data types intelligently:

| Access Type | Parquet Type | Notes |
|-------------|--------------|-------|
| **AutoNumber** | int64 | Primary key preservation |
| **Number** | int64/float64 | Based on field size |
| **Currency** | float64 | Maintains precision |
| **Text/Short Text** | string | UTF-8 encoded |
| **Long Text/Memo** | string | Full content preserved |
| **Date/Time** | datetime64 | Timezone aware |
| **Yes/No** | bool | True/False conversion |
| **OLE Object** | binary | Base64 encoded |
| **Hyperlink** | string | URL text only |

## Error Handling

### Common Issues and Solutions

**Password Protected Databases**:
```bash
# PyForge will prompt for password
pyforge convert protected.mdb
# Enter password: [hidden input]
```

**Corrupted Tables**:
```bash
# Skip corrupted tables and continue
pyforge convert damaged.accdb --skip-errors
# Warning: Table 'CorruptedTable' could not be read, skipping...
```

**Missing Dependencies**:
```bash
# Install required tools
# macOS:
brew install mdbtools

# Linux:
sudo apt-get install mdbtools
```

**Large Tables**:
```bash
# Process large tables in chunks
pyforge convert huge_db.accdb --chunk-size 50000
```

## Performance Optimization

### Large Databases

```bash
# Optimize for large databases
pyforge convert big_database.accdb \
  --chunk-size 100000 \
  --compression gzip \
  --verbose

# Parallel table processing
pyforge convert multi_table.mdb --max-workers 4
```

### Memory Management

```bash
# Reduce memory usage for large tables
pyforge convert database.accdb \
  --chunk-size 25000 \
  --low-memory

# Process one table at a time
pyforge convert db.mdb --sequential
```

## Validation and Quality Checks

### Pre-conversion Inspection

```bash
# Analyze database before conversion
pyforge info database.mdb

# Check for potential issues
pyforge validate database.accdb --check-integrity
```

### Post-conversion Verification

```bash
# Verify conversion results
pyforge validate output_directory/ --source database.mdb

# Compare record counts
pyforge info output_directory/ --compare-source database.mdb
```

## Examples

### Business Database Migration

```bash
# Convert CRM database with full reporting
pyforge convert CRM_Database.accdb \
  --summary \
  --compression gzip \
  --verbose

# Results in:
#   CRM_Database/
#   ├── Customers.parquet
#   ├── Orders.parquet
#   ├── Products.parquet
#   ├── Sales_Rep.parquet
#   └── _summary.xlsx
```

### ETL Pipeline Integration

```bash
# Automated conversion with validation
#!/bin/bash
DB_FILE="monthly_data.mdb"
OUTPUT_DIR="processed_data"

# Convert database
if pyforge convert "$DB_FILE" "$OUTPUT_DIR" --summary; then
    echo "Conversion successful"
    
    # Validate results
    pyforge validate "$OUTPUT_DIR" --source "$DB_FILE"
    
    # Process with your ETL tool
    python etl_pipeline.py --input "$OUTPUT_DIR"
else
    echo "Conversion failed"
    exit 1
fi
```

### Batch Processing

```bash
# Convert multiple databases
for db_file in databases/*.mdb databases/*.accdb; do
    echo "Converting: $db_file"
    pyforge convert "$db_file" \
      --compression gzip \
      --summary \
      --verbose
done
```

## Integration Examples

### Python/Pandas

```python
import pandas as pd
import os

# Read all converted tables
def load_access_tables(parquet_dir):
    tables = {}
    for file in os.listdir(parquet_dir):
        if file.endswith('.parquet'):
            table_name = file.replace('.parquet', '')
            tables[table_name] = pd.read_parquet(f'{parquet_dir}/{file}')
    return tables

# Usage
tables = load_access_tables('converted_database/')
customers = tables['Customers']
orders = tables['Orders']

# Join tables
customer_orders = customers.merge(orders, on='CustomerID')
```

### Spark/PySpark

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("AccessData").getOrCreate()

# Read all parquet files as Spark DataFrames
def load_spark_tables(parquet_dir):
    tables = {}
    for file in os.listdir(parquet_dir):
        if file.endswith('.parquet'):
            table_name = file.replace('.parquet', '')
            tables[table_name] = spark.read.parquet(f'{parquet_dir}/{file}')
    return tables

# Usage
tables = load_spark_tables('converted_database/')
customers_df = tables['Customers']
customers_df.createOrReplaceTempView('customers')

# SQL queries on converted data
result = spark.sql("SELECT * FROM customers WHERE State = 'CA'")
```

## Troubleshooting

### Common Issues

**"Could not open database"**:
- Verify file path and permissions
- Check if database is password protected
- Ensure database isn't corrupted

**"mdbtools not found"** (macOS/Linux):
```bash
# macOS
brew install mdbtools

# Ubuntu/Debian
sudo apt-get install mdbtools

# CentOS/RHEL
sudo yum install mdbtools
```

**"Table not found"**:
- Use `pyforge info database.mdb` to list available tables
- Check table name spelling and case sensitivity
- Verify table isn't hidden or system table

**Memory errors with large databases**:
```bash
# Reduce chunk size
pyforge convert large.accdb --chunk-size 10000

# Use sequential processing
pyforge convert large.accdb --sequential
```

## Best Practices

1. **Backup First**: Always backup original database files
2. **Test Small**: Try conversion on a copy or subset first
3. **Use Summary Reports**: Generate Excel summaries for validation
4. **Check Dependencies**: Install mdbtools on macOS/Linux before conversion
5. **Validate Results**: Always verify record counts and data integrity
6. **Optimize Settings**: Use appropriate chunk sizes for your system memory
7. **Handle Passwords**: Be prepared to enter passwords for protected databases

## Security Considerations

- **Password Handling**: Passwords are not stored or logged
- **File Permissions**: Converted files inherit system default permissions
- **Sensitive Data**: Consider encryption for sensitive converted data
- **Audit Trail**: Use `--verbose` to maintain conversion logs

For complete command reference and advanced options, see the [CLI Reference](../reference/cli-reference.md).