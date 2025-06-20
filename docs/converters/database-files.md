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

=== "With Verbose Output"
    ```bash
    # Show detailed conversion progress
    pyforge convert database.mdb --verbose
    ```

### Advanced Options

```bash
# Password-protected databases
pyforge convert secured.mdb --password mypassword

# Verbose output for monitoring
pyforge convert large_db.accdb --verbose

# Force overwrite existing files
pyforge convert database.mdb --force

# Custom compression (default is snappy)
pyforge convert data.accdb --compression gzip
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

PyForge converts all Access data to string format for maximum compatibility:

| Access Type | Parquet Type | Notes |
|-------------|--------------|-------|
| **AutoNumber** | string | Numeric values preserved as strings |
| **Number** | string | Decimal precision up to 5 places, no trailing zeros |
| **Currency** | string | Monetary values as decimal strings |
| **Text/Short Text** | string | UTF-8 encoded |
| **Long Text/Memo** | string | Full content preserved |
| **Date/Time** | string | ISO 8601 format (YYYY-MM-DDTHH:MM:SS) |
| **Yes/No** | string | "true" or "false" lowercase strings |
| **OLE Object** | string | Base64 encoded |
| **Hyperlink** | string | URL text only |

!!! note "String-Based Conversion"
    PyForge CLI currently uses a string-based conversion approach to ensure consistent behavior across all database formats (Excel, MDB, DBF). While this preserves data integrity and precision, you may need to cast types in your analysis tools (pandas, Spark, etc.) if you require native numeric or datetime types.

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
# Use verbose mode to see detailed error information
pyforge convert damaged.accdb --verbose
# Will show specific errors for problematic tables
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
# Monitor progress with verbose output
pyforge convert huge_db.accdb --verbose
```

## Performance Optimization

### Large Databases

```bash
# Optimize for large databases
pyforge convert big_database.accdb \
  --compression gzip \
  --verbose

# Process specific tables only to reduce load
pyforge convert multi_table.mdb --tables "LargeTable1,LargeTable2"
```

### Memory Management

PyForge automatically optimizes memory usage for large databases:
- Processes tables sequentially to minimize memory footprint
- Uses streaming writes for large datasets
- Provides 6-stage progress tracking with real-time metrics
- Automatically handles memory-efficient conversion
```

## Validation and Quality Checks

### Pre-conversion Inspection

```bash
# Analyze database before conversion
pyforge info database.mdb

# Validate database file
pyforge validate database.accdb
```

### Post-conversion Verification

```bash
# Check converted files
pyforge info output_directory/

# Validate individual parquet files
for file in output_directory/*.parquet; do
    pyforge validate "$file"
done
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

# Convert string columns to appropriate types
def convert_table_types(df):
    for col in df.columns:
        # Try to convert to numeric (will stay string if not possible)
        df[col] = pd.to_numeric(df[col], errors='ignore')
        
        # Try to convert to datetime (will stay string if not possible)
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except:
                pass
        
        # Convert boolean strings
        if df[col].dtype == 'object':
            bool_mask = df[col].isin(['true', 'false'])
            if bool_mask.any():
                df.loc[bool_mask, col] = df.loc[bool_mask, col].map({'true': True, 'false': False})
    return df

# Usage
tables = load_access_tables('converted_database/')
customers = convert_table_types(tables['Customers'])
orders = convert_table_types(tables['Orders'])

# Join tables (ensure matching types for join keys)
customer_orders = customers.merge(orders, on='CustomerID')
```

### Spark/PySpark

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.sql.types import *

spark = SparkSession.builder.appName("AccessData").getOrCreate()

# Read all parquet files as Spark DataFrames
def load_spark_tables(parquet_dir):
    tables = {}
    for file in os.listdir(parquet_dir):
        if file.endswith('.parquet'):
            table_name = file.replace('.parquet', '')
            tables[table_name] = spark.read.parquet(f'{parquet_dir}/{file}')
    return tables

# Convert string columns to appropriate types
def convert_spark_types(df, type_mapping):
    """
    Convert DataFrame columns to specified types
    type_mapping: dict like {'CustomerID': IntegerType(), 'OrderDate': TimestampType()}
    """
    for column, data_type in type_mapping.items():
        if column in df.columns:
            df = df.withColumn(column, col(column).cast(data_type))
    
    # Convert boolean strings
    string_cols = [field.name for field in df.schema.fields if field.dataType == StringType()]
    for column in string_cols:
        df = df.withColumn(column, 
            when(col(column) == "true", True)
            .when(col(column) == "false", False)
            .otherwise(col(column))
        )
    
    return df

# Usage
tables = load_spark_tables('converted_database/')
customers_raw = tables['Customers']

# Define type mappings for specific tables
customer_types = {
    'CustomerID': IntegerType(),
    'DateCreated': TimestampType(),
    'Balance': DoubleType()
}

customers_df = convert_spark_types(customers_raw, customer_types)
customers_df.createOrReplaceTempView('customers')

# SQL queries on converted data
result = spark.sql("SELECT CustomerID, Balance FROM customers WHERE Balance > 1000")
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
# Use verbose output to monitor memory usage
pyforge convert large.accdb --verbose

# Use compression to reduce output size
pyforge convert large.accdb --compression gzip
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