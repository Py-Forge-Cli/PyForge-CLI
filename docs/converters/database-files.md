# Database File Conversion

Convert Microsoft Access (.mdb/.accdb) and SQL Server (.mdf) database files to efficient Parquet format with automatic table discovery and cross-platform support.

## Overview

PyForge CLI provides comprehensive database conversion for Access and SQL Server files with:

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
| **SQL Server Master** | `.mdf` | SQL Server database files | 🚧 In Development |
| **Databricks Serverless** | `.mdb/.accdb` | Subprocess-based processing | ✅ Full (v1.0.9+) |

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

### Databricks Serverless
```bash
# Install PyForge CLI in Databricks Serverless notebook
%pip install pyforge-cli --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

# Convert database files from Unity Catalog volumes
pyforge convert dbfs:/Volumes/catalog/schema/volume/database.mdb

# Or use subprocess backend explicitly
pyforge convert database.mdb --backend subprocess
```

## Databricks Serverless Support

PyForge CLI v1.0.9+ provides full support for Databricks Serverless environments with specialized optimizations for cloud-native database conversion.

### Subprocess Backend

Databricks Serverless uses a **subprocess-based backend** for database conversion that provides:

- **Isolated Processing**: Each conversion runs in a separate subprocess for better resource isolation
- **Memory Optimization**: Optimized memory usage for Databricks Serverless compute constraints
- **Error Isolation**: Subprocess failures don't crash the main notebook kernel
- **Progress Tracking**: Real-time progress updates visible in notebook output

### Unity Catalog Volume Support

PyForge CLI automatically detects and handles Unity Catalog volume paths:

```python
# Direct volume path conversion
pyforge convert dbfs:/Volumes/catalog/schema/volume/database.mdb

# Output to specific volume location
pyforge convert dbfs:/Volumes/catalog/schema/volume/input.mdb dbfs:/Volumes/catalog/schema/volume/output/

# Batch processing from volume
pyforge convert dbfs:/Volumes/catalog/schema/volume/*.mdb
```

### Installation and Configuration

#### Step 1: Install PyForge CLI
```python
# Always use the complete installation command for Databricks Serverless
%pip install pyforge-cli --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

# Restart Python to ensure clean imports
dbutils.library.restartPython()
```

#### Step 2: Verify Installation
```python
# Test the installation
import subprocess
result = subprocess.run(['pyforge', '--version'], capture_output=True, text=True)
print(f"PyForge CLI Version: {result.stdout.strip()}")
```

#### Step 3: Configure Backend (Optional)
```python
# PyForge automatically detects Databricks Serverless environment
# Manual backend specification (if needed)
import os
os.environ['PYFORGE_BACKEND'] = 'subprocess'
```

### Usage Examples for Databricks Serverless

#### Basic Conversion
```python
# Convert MDB file from Unity Catalog volume
import subprocess

# Single file conversion
result = subprocess.run([
    'pyforge', 'convert', 
    'dbfs:/Volumes/catalog/schema/volume/database.mdb',
    '--verbose'
], capture_output=True, text=True)

print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
```

#### Advanced Conversion with Options
```python
# Convert with specific options
result = subprocess.run([
    'pyforge', 'convert',
    'dbfs:/Volumes/catalog/schema/volume/company.accdb',
    'dbfs:/Volumes/catalog/schema/volume/converted/',
    '--tables', 'Customers,Orders,Products',
    '--compression', 'gzip',
    '--verbose'
], capture_output=True, text=True)

print("Conversion completed!")
print("Output:", result.stdout)
```

#### Batch Processing
```python
# Process multiple database files
import os
import subprocess

# List all MDB files in volume
volume_path = "dbfs:/Volumes/catalog/schema/volume/"
files_to_process = [
    f"{volume_path}sales.mdb",
    f"{volume_path}inventory.accdb",
    f"{volume_path}customers.mdb"
]

for db_file in files_to_process:
    print(f"Processing: {db_file}")
    result = subprocess.run([
        'pyforge', 'convert', db_file,
        '--compression', 'gzip',
        '--verbose'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Successfully converted: {db_file}")
    else:
        print(f"❌ Failed to convert: {db_file}")
        print(f"Error: {result.stderr}")
```

### Performance Optimization for Databricks Serverless

#### Memory-Efficient Processing
```python
# For large databases, use chunked processing
result = subprocess.run([
    'pyforge', 'convert',
    'dbfs:/Volumes/catalog/schema/volume/large_database.mdb',
    '--compression', 'gzip',
    '--backend', 'subprocess',
    '--verbose'
], capture_output=True, text=True)
```

#### Parallel Processing
```python
# Process multiple files in parallel using Databricks jobs
from concurrent.futures import ThreadPoolExecutor
import subprocess

def convert_database(db_path):
    """Convert a single database file"""
    result = subprocess.run([
        'pyforge', 'convert', db_path,
        '--compression', 'gzip',
        '--verbose'
    ], capture_output=True, text=True)
    return db_path, result.returncode == 0

# Process files in parallel
database_files = [
    "dbfs:/Volumes/catalog/schema/volume/db1.mdb",
    "dbfs:/Volumes/catalog/schema/volume/db2.accdb",
    "dbfs:/Volumes/catalog/schema/volume/db3.mdb"
]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(convert_database, database_files))

for db_path, success in results:
    status = "✅ Success" if success else "❌ Failed"
    print(f"{status}: {db_path}")
```

### Working with Converted Data

#### Load Converted Parquet Files
```python
# Load converted parquet files in Databricks
import pandas as pd

# Read converted table
df = pd.read_parquet('dbfs:/Volumes/catalog/schema/volume/database/Customers.parquet')
print(f"Loaded {len(df)} customer records")
display(df.head())
```

#### Spark DataFrame Integration
```python
# Load as Spark DataFrame for large datasets
customers_df = spark.read.parquet('dbfs:/Volumes/catalog/schema/volume/database/Customers.parquet')

# Register as temporary view
customers_df.createOrReplaceTempView('customers')

# Query with SQL
result = spark.sql("SELECT COUNT(*) as customer_count FROM customers")
display(result)
```

### Troubleshooting Databricks Serverless

#### Common Issues and Solutions

**Installation Issues**:
```python
# If pip install fails, try with specific index
%pip install pyforge-cli --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org --upgrade

# Clear pip cache if needed
%pip cache purge
```

**Path Issues**:
```python
# Ensure proper dbfs:// prefix for volume paths
# ✅ Correct
path = "dbfs:/Volumes/catalog/schema/volume/database.mdb"

# ❌ Incorrect
path = "/Volumes/catalog/schema/volume/database.mdb"
```

**Memory Issues**:
```python
# For large databases, process one table at a time
result = subprocess.run([
    'pyforge', 'convert',
    'dbfs:/Volumes/catalog/schema/volume/large_db.mdb',
    '--tables', 'LargeTable1',
    '--compression', 'gzip'
], capture_output=True, text=True)
```

**Subprocess Errors**:
```python
# Check subprocess backend availability
import subprocess
try:
    result = subprocess.run(['pyforge', '--version'], capture_output=True, text=True)
    print(f"PyForge available: {result.stdout.strip()}")
except FileNotFoundError:
    print("PyForge CLI not found. Please reinstall.")
```

### Performance Notes for Databricks Serverless

- **Subprocess Overhead**: Slight performance overhead due to subprocess communication
- **Memory Efficiency**: Optimized for Databricks Serverless memory constraints
- **I/O Optimization**: Efficient handling of Unity Catalog volume operations
- **Parallel Processing**: Supports concurrent conversions for multiple files
- **Progress Tracking**: Real-time progress updates in notebook output

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

# Specify backend (auto-detected by default)
pyforge convert database.mdb --backend subprocess

# Unity Catalog volume processing
pyforge convert dbfs:/Volumes/catalog/schema/volume/database.mdb --compression gzip
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

### Databricks Serverless Processing

```python
# Convert database in Databricks Serverless notebook
import subprocess

# Single database conversion
result = subprocess.run([
    'pyforge', 'convert',
    'dbfs:/Volumes/catalog/schema/volume/sales_data.mdb',
    'dbfs:/Volumes/catalog/schema/volume/converted/',
    '--compression', 'gzip',
    '--verbose'
], capture_output=True, text=True)

print("Conversion Result:")
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
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

### Databricks Serverless Integration

```python
# Complete Databricks Serverless workflow
import subprocess
import pandas as pd

# Step 1: Convert database
conversion_result = subprocess.run([
    'pyforge', 'convert',
    'dbfs:/Volumes/catalog/schema/volume/business_data.accdb',
    'dbfs:/Volumes/catalog/schema/volume/converted/',
    '--compression', 'gzip',
    '--verbose'
], capture_output=True, text=True)

if conversion_result.returncode == 0:
    print("✅ Conversion successful!")
    
    # Step 2: Load converted data
    customers_df = pd.read_parquet('dbfs:/Volumes/catalog/schema/volume/converted/business_data/Customers.parquet')
    orders_df = pd.read_parquet('dbfs:/Volumes/catalog/schema/volume/converted/business_data/Orders.parquet')
    
    # Step 3: Basic analysis
    print(f"Customers: {len(customers_df)}")
    print(f"Orders: {len(orders_df)}")
    
    # Step 4: Create Spark DataFrames for large-scale processing
    customers_spark = spark.createDataFrame(customers_df)
    orders_spark = spark.createDataFrame(orders_df)
    
    # Step 5: Register as temporary views
    customers_spark.createOrReplaceTempView('customers')
    orders_spark.createOrReplaceTempView('orders')
    
    # Step 6: Run analytics
    result = spark.sql("""
        SELECT c.CustomerName, COUNT(o.OrderID) as OrderCount
        FROM customers c
        LEFT JOIN orders o ON c.CustomerID = o.CustomerID
        GROUP BY c.CustomerName
        ORDER BY OrderCount DESC
        LIMIT 10
    """)
    
    display(result)
else:
    print("❌ Conversion failed!")
    print(conversion_result.stderr)
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

**Databricks Serverless Issues**:
```python
# Installation problems
%pip install pyforge-cli --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org --upgrade
dbutils.library.restartPython()

# Path resolution issues
# ✅ Correct - use dbfs:// prefix
path = "dbfs:/Volumes/catalog/schema/volume/database.mdb"

# ❌ Incorrect - missing dbfs:// prefix
path = "/Volumes/catalog/schema/volume/database.mdb"

# Subprocess backend issues
import subprocess
try:
    result = subprocess.run(['pyforge', '--version'], capture_output=True, text=True)
    print("PyForge available:", result.stdout.strip())
except FileNotFoundError:
    print("PyForge CLI not found in PATH")
    %pip install pyforge-cli --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
```

**Unity Catalog Volume Permission Issues**:
```python
# Check volume access permissions
try:
    dbutils.fs.ls("dbfs:/Volumes/catalog/schema/volume/")
    print("✅ Volume access confirmed")
except Exception as e:
    print(f"❌ Volume access error: {e}")
    print("Check Unity Catalog permissions and volume path")
```

## Best Practices

1. **Backup First**: Always backup original database files
2. **Test Small**: Try conversion on a copy or subset first
3. **Use Summary Reports**: Generate Excel summaries for validation
4. **Check Dependencies**: Install mdbtools on macOS/Linux before conversion
5. **Validate Results**: Always verify record counts and data integrity
6. **Optimize Settings**: Use appropriate chunk sizes for your system memory
7. **Handle Passwords**: Be prepared to enter passwords for protected databases

### Databricks Serverless Best Practices

8. **Use Proper Installation**: Always use the complete pip install command with index URL
9. **Volume Path Prefix**: Always use `dbfs://` prefix for Unity Catalog volume paths
10. **Memory Management**: Use compression for large databases to reduce memory usage
11. **Error Handling**: Implement proper subprocess error handling in notebooks
12. **Batch Processing**: Use parallel processing for multiple database files
13. **Progress Monitoring**: Use `--verbose` flag to monitor conversion progress
14. **Restart Python**: Always restart Python after installing PyForge CLI
15. **Permission Verification**: Check Unity Catalog volume permissions before conversion

## SQL Server MDF Files

### Prerequisites for MDF Processing

Before processing SQL Server MDF files, you need to install the MDF Tools:

```bash
# Install Docker Desktop and SQL Server Express
pyforge install mdf-tools

# Verify installation
pyforge mdf-tools status

# Test SQL Server connectivity
pyforge mdf-tools test
```

**System Requirements for MDF Processing:**
- Docker Desktop installed and running
- SQL Server Express container (automatically configured)
- Minimum 4GB RAM available for SQL Server
- Internet connection for initial setup

### MDF Container Management

```bash
# Start SQL Server (if not running)
pyforge mdf-tools start

# Check status
pyforge mdf-tools status

# View SQL Server logs
pyforge mdf-tools logs

# Stop when finished
pyforge mdf-tools stop
```

### MDF Conversion (Coming Soon)

Once the MDF converter is implemented, you'll be able to process SQL Server database files:

```bash
# Convert MDF database (planned feature)
# pyforge convert database.mdf --format parquet

# With custom options (planned)
# pyforge convert large.mdf --tables "Users,Orders" --exclude-system-tables
```

**MDF Processing Features (In Development):**
- Automatic MDF file mounting in SQL Server Express
- String-based data conversion (Phase 1 implementation)
- Table filtering with `--exclude-system-tables` option
- Chunk-based processing for large databases
- Same 6-stage conversion process as MDB files

For detailed MDF Tools documentation, see [MDF Tools Installer](mdf-tools-installer.md).

## Security Considerations

- **Password Handling**: Passwords are not stored or logged
- **File Permissions**: Converted files inherit system default permissions
- **Sensitive Data**: Consider encryption for sensitive converted data
- **Audit Trail**: Use `--verbose` to maintain conversion logs

For complete command reference and advanced options, see the [CLI Reference](../reference/cli-reference.md).