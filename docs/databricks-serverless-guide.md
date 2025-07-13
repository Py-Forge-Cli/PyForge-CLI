# Databricks Serverless Conversion Guide

This comprehensive guide walks you through using PyForge CLI in Databricks Serverless environments for converting various file formats including databases (.mdb/.accdb), DBF files, Excel spreadsheets, CSV files, and XML documents.

!!! note "Download Interactive Notebook"
    📓 **[Download the Jupyter Notebook](https://github.com/Py-Forge-Cli/PyForge-CLI/blob/main/notebooks/testing/functional/10-databricks-serverless-user-guide.ipynb)** - Ready-to-use notebook with all examples and code cells properly formatted for Databricks.

## Prerequisites

- Databricks Serverless workspace access
- Unity Catalog volume with read/write permissions
- Sample datasets or your own files to convert

## Step 1: Install PyForge CLI

In your Databricks Serverless notebook, install PyForge CLI with the proper PyPI index URL:

```python
# Cell 1: Install PyForge CLI
%pip install pyforge-cli==1.0.9 --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

# Cell 2: Restart Python kernel
dbutils.library.restartPython()

# Cell 3: Verify installation
import subprocess
result = subprocess.run(['pyforge', '--version'], capture_output=True, text=True)
print(f"PyForge CLI Version: {result.stdout.strip()}")
```

!!! important "Always Include PyPI Index URL"
    The `--index-url https://pypi.org/simple/ --trusted-host pypi.org` flags are **required** in Databricks Serverless environments for proper dependency resolution in corporate networks.

## Step 2: Install Sample Datasets

PyForge CLI includes a curated collection of sample datasets for testing all supported formats:

```bash
# Cell 4: Install sample datasets using shell command
%%sh
pyforge install sample-datasets --output /dbfs/Volumes/catalog/schema/volume/sample_datasets --verbose
```

```python
# Cell 5: Define volume path for Python usage
volume_path = "dbfs:/Volumes/catalog/schema/volume/sample_datasets"
```

## Step 3: List Available Sample Datasets

After installation, explore the available sample datasets:

```python
# Cell 5: List all sample datasets
import os

# List files in the sample datasets directory
files = dbutils.fs.ls(f"{volume_path}/")

# Organize by file type
file_types = {
    'mdb': [],
    'accdb': [],
    'dbf': [],
    'xlsx': [],
    'csv': [],
    'xml': [],
    'pdf': []
}

for file_info in files:
    file_name = file_info.name
    for ext in file_types.keys():
        if file_name.endswith(f'.{ext}'):
            file_types[ext].append(file_name)

# Display organized list
print("📁 Available Sample Datasets:\n")
for file_type, files in file_types.items():
    if files:
        print(f"**{file_type.upper()} Files:**")
        for file in files:
            print(f"  - {file}")
        print()
```

## Step 4: Database File Conversion (.mdb/.accdb)

!!! warning "Important: MDB/ACCDB Files Require Subprocess"
    Due to Java SDK dependencies, MDB/ACCDB files **must** use subprocess commands instead of `%sh` magic commands. All other file formats (CSV, XML, Excel, DBF) can use `%sh` commands.

### Convert MDB File (Subprocess Method - Correct)

```python
# Cell 6: Convert MDB database file
import subprocess

# Input and output paths
mdb_file = f"{volume_path}/Northwind.mdb"
output_dir = f"{volume_path}/converted/northwind/"

# Convert using subprocess (CORRECT method for Databricks Serverless)
result = subprocess.run([
    'pyforge', 'convert',
    mdb_file,
    output_dir,
    '--compression', 'gzip',
    '--verbose'
], capture_output=True, text=True)

print("Conversion Output:")
print(result.stdout)

# List converted files
if result.returncode == 0:
    converted_files = dbutils.fs.ls(output_dir)
    print("\n✅ Converted Tables:")
    for file in converted_files:
        if file.name.endswith('.parquet'):
            print(f"  - {file.name}")
else:
    print(f"❌ Conversion failed: {result.stderr}")
```

### Convert ACCDB File

```python
# Cell 7: Convert ACCDB database file
accdb_file = f"{volume_path}/AdventureWorks.accdb"
output_dir = f"{volume_path}/converted/adventureworks/"

result = subprocess.run([
    'pyforge', 'convert',
    accdb_file,
    output_dir,
    '--tables', 'Customers,Orders,Products',  # Convert specific tables
    '--compression', 'snappy',
    '--verbose'
], capture_output=True, text=True)

print("Conversion Output:")
print(result.stdout)
```

## Step 5: DBF File Conversion

```bash
# Cell 8: Convert DBF file using shell command
%%sh
echo "Converting DBF file..."
pyforge convert /dbfs/Volumes/catalog/schema/volume/sample_datasets/customer_data.dbf \
    /dbfs/Volumes/catalog/schema/volume/converted/customer_data.parquet \
    --encoding cp1252 \
    --verbose
```

```python
# Cell 9: Read and display converted data
import pandas as pd
output_file = f"{volume_path}/converted/customer_data.parquet"
df = pd.read_parquet(output_file.replace('dbfs:/', '/dbfs/'))
print(f"📊 Sample Data ({len(df)} rows):")
display(df.head())
```

## Step 6: Excel File Conversion

```bash
# Cell 10: Convert Excel file using shell command
%%sh
echo "Converting Excel file..."
pyforge convert /dbfs/Volumes/catalog/schema/volume/sample_datasets/financial_report.xlsx \
    /dbfs/Volumes/catalog/schema/volume/converted/financial/ \
    --combine \
    --compression gzip \
    --verbose
```

```python
# Cell 11: Load and analyze converted data
output_dir = f"{volume_path}/converted/financial/"
parquet_files = dbutils.fs.ls(output_dir)
for file in parquet_files:
    if file.name.endswith('.parquet'):
        df = pd.read_parquet(file.path.replace('dbfs:/', '/dbfs/'))
        print(f"\n📊 {file.name}: {len(df)} rows x {len(df.columns)} columns")
        display(df.head(3))
```

## Step 7: CSV File Conversion

```bash
# Cell 12: Convert CSV file using shell command
%%sh
echo "Converting CSV file..."
pyforge convert /dbfs/Volumes/catalog/schema/volume/sample_datasets/sales_data.csv \
    /dbfs/Volumes/catalog/schema/volume/converted/sales_data.parquet \
    --compression snappy \
    --verbose
```

```python
# Cell 13: Verify conversion
output_file = f"{volume_path}/converted/sales_data.parquet"
df = pd.read_parquet(output_file.replace('dbfs:/', '/dbfs/'))
print(f"✅ Successfully converted {len(df)} rows")
print(f"Columns: {', '.join(df.columns)}")
```

## Step 8: XML File Conversion

```bash
# Cell 14: Convert XML file using shell command
%%sh
echo "Converting XML file..."
pyforge convert /dbfs/Volumes/catalog/schema/volume/sample_datasets/books_catalog.xml \
    /dbfs/Volumes/catalog/schema/volume/converted/books_catalog.parquet \
    --flatten-strategy moderate \
    --array-handling expand \
    --compression gzip \
    --verbose
```

```python
# Cell 15: Display structured data
output_file = f"{volume_path}/converted/books_catalog.parquet"
df = pd.read_parquet(output_file.replace('dbfs:/', '/dbfs/'))
print(f"📚 Books Catalog: {len(df)} records")
display(df.head())
```

## Step 9: Batch Processing Multiple Files

```python
# Cell 12: Batch convert multiple files
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def convert_file(file_path, output_dir):
    """Convert a single file and return status"""
    file_name = os.path.basename(file_path)
    
    result = subprocess.run([
        'pyforge', 'convert',
        file_path,
        output_dir,
        '--compression', 'gzip',
        '--verbose'
    ], capture_output=True, text=True)
    
    return {
        'file': file_name,
        'success': result.returncode == 0,
        'output': result.stdout,
        'error': result.stderr
    }

# Files to convert
files_to_convert = [
    f"{volume_path}/Northwind.mdb",
    f"{volume_path}/financial_report.xlsx",
    f"{volume_path}/customer_data.dbf",
    f"{volume_path}/sales_data.csv",
    f"{volume_path}/books_catalog.xml"
]

output_base = f"{volume_path}/batch_converted/"

# Process files in parallel
results = []
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(convert_file, file, output_base): file 
               for file in files_to_convert}
    
    for future in as_completed(futures):
        result = future.result()
        results.append(result)
        
        # Print status
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['file']}")

print(f"\n📊 Conversion Summary:")
print(f"Total files: {len(results)}")
print(f"Successful: {sum(1 for r in results if r['success'])}")
print(f"Failed: {sum(1 for r in results if not r['success'])}")
```

## Step 10: Working with Converted Data

```python
# Cell 13: Load and analyze converted data
import pandas as pd
import pyspark.sql.functions as F

# Load converted Northwind customers as Pandas DataFrame
customers_pd = pd.read_parquet(
    f'/dbfs/{volume_path.replace("dbfs:/", "")}/converted/northwind/Customers.parquet'
)
print(f"Pandas DataFrame: {len(customers_pd)} customers")
display(customers_pd.head())

# Load as Spark DataFrame for large-scale processing
customers_spark = spark.read.parquet(
    f"{volume_path}/converted/northwind/Customers.parquet"
)

# Register as temporary view
customers_spark.createOrReplaceTempView("customers")

# Run SQL analytics
result = spark.sql("""
    SELECT 
        Country,
        COUNT(*) as customer_count
    FROM customers
    GROUP BY Country
    ORDER BY customer_count DESC
    LIMIT 10
""")

print("\n📊 Customers by Country:")
display(result)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Installation Failures

```python
# If installation fails, try clearing cache
%pip cache purge
%pip install pyforge-cli==1.0.9 --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org --upgrade
dbutils.library.restartPython()
```

#### 2. Path Resolution Issues

```python
# Always use dbfs:// prefix for Unity Catalog volumes
✅ correct_path = "dbfs:/Volumes/catalog/schema/volume/file.mdb"
❌ incorrect_path = "/Volumes/catalog/schema/volume/file.mdb"
```

#### 3. Subprocess Command Not Found

```python
# Verify PyForge is in PATH after installation
import subprocess
import sys

# Check Python executable location
print(f"Python: {sys.executable}")

# Find pyforge location
result = subprocess.run(['which', 'pyforge'], capture_output=True, text=True)
print(f"PyForge location: {result.stdout.strip()}")
```

#### 4. Memory Issues with Large Files

```python
# Process large files with specific tables or chunking
result = subprocess.run([
    'pyforge', 'convert',
    'large_database.mdb',
    '--tables', 'Table1,Table2',  # Convert specific tables only
    '--compression', 'gzip',       # Use compression
    '--verbose'
], capture_output=True, text=True)
```

## Best Practices

1. **Use %sh commands** for CSV, XML, Excel, and DBF file conversions
2. **Use subprocess only** for MDB/ACCDB files due to Java SDK dependencies
3. **Include PyPI index URL** in all pip install commands
4. **Use dbfs:// prefix** for Unity Catalog volume paths in Python code
5. **Use /dbfs/ prefix** for shell commands
6. **Restart Python kernel** after installing PyForge CLI
7. **Use compression** for large files to save storage
8. **Verify conversions** by checking output and return codes

## Performance Tips

### Parallel Processing for Multiple Files

```python
# Use ThreadPoolExecutor for concurrent conversions
from concurrent.futures import ThreadPoolExecutor

# Limit workers to avoid overwhelming the cluster
max_workers = min(3, len(files_to_convert))
```

### Memory-Efficient Processing

```python
# For very large databases, process one table at a time
tables = ['Customers', 'Orders', 'OrderDetails', 'Products']
for table in tables:
    result = subprocess.run([
        'pyforge', 'convert', 'large_db.mdb',
        '--tables', table,
        '--compression', 'gzip'
    ], capture_output=True, text=True)
```

### Optimize Spark Reading

```python
# Use partition discovery for better performance
df = spark.read.option("mergeSchema", "true").parquet(
    f"{volume_path}/converted/data/*.parquet"
)
```

## Next Steps

- Explore the [CLI Reference](reference/cli-reference.md) for all available options
- Learn about [XML conversion strategies](converters/xml-to-parquet.md)
- Review [database conversion details](converters/database-files.md)
- Check [troubleshooting guide](tutorials/troubleshooting.md) for more solutions

## Summary

This guide demonstrated how to:

✅ Install PyForge CLI in Databricks Serverless with proper PyPI configuration  
✅ Install and explore sample datasets in Unity Catalog volumes  
✅ Convert database files (.mdb/.accdb) using subprocess commands  
✅ Process DBF, Excel, CSV, and XML files with various options  
✅ Perform batch conversions with parallel processing  
✅ Load and analyze converted Parquet files with Pandas and Spark  
✅ Handle common issues and optimize performance  

Remember: Use subprocess commands for MDB/ACCDB files only. All other formats (CSV, XML, Excel, DBF) can use standard `%sh` commands!