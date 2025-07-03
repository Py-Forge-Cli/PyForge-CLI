# PyForge Databricks: Advanced Volume Integration and Serverless Optimization

<div align="right">
📥 <strong><a href="#" id="download-notebook" download="pyforge-databricks-volume-guide.ipynb">Download Jupyter Notebook</a></strong>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const downloadLink = document.getElementById('download-notebook');
    const currentHost = window.location.origin;
    const currentPath = window.location.pathname;
    
    // Check if we're on localhost (development) or production
    if (currentHost.includes('localhost') || currentHost.includes('127.0.0.1')) {
        // Local development - point to local file
        downloadLink.href = currentHost + '/notebooks/pyforge-databricks-volume-guide.ipynb';
    } else if (currentHost.includes('github.io')) {
        // GitHub Pages - construct raw GitHub URL
        const pathParts = currentPath.split('/');
        const repoOwner = pathParts[1]; // Usually the username
        const repoName = pathParts[2] || 'PyForge-CLI'; // Repository name
        downloadLink.href = `https://raw.githubusercontent.com/${repoOwner}/${repoName}/main/docs/notebooks/pyforge-databricks-volume-guide.ipynb`;
    } else {
        // Other hosting - try relative path first, fallback to GitHub
        downloadLink.href = '/docs/notebooks/pyforge-databricks-volume-guide.ipynb';
        
        // If that fails, fallback to GitHub raw URL
        downloadLink.addEventListener('error', function() {
            downloadLink.href = 'https://raw.githubusercontent.com/Py-Forge-Cli/PyForge-CLI/main/docs/notebooks/pyforge-databricks-volume-guide.ipynb';
        });
    }
});
</script>

This notebook demonstrates using PyForge CLI in Databricks environments with Unity Catalog Volume support, showing how to work with volumes and process data using command-line tools.

## Introduction

PyForge CLI works seamlessly in Databricks environments. This guide covers:

- Installing and using PyForge sample datasets in Volumes
- Working with Unity Catalog Volumes using CLI commands
- Direct Volume-to-Volume file conversions
- Working with multi-table databases in Volumes
- Batch processing using shell commands
- CLI integration with Databricks file systems

### Key Features:
- **Unity Catalog Volumes**: Direct read/write operations on Volume paths using CLI
- **Shell Integration**: Use %sh magic commands for all file operations  
- **Multi-format Support**: Convert between CSV, Excel, PDF, XML, Access databases and more
- **Volume-Native**: Works directly with `/Volumes/` paths
- **Batch Processing**: Process multiple files efficiently using shell commands

---

## 1. Installation and Environment Setup

Install PyForge CLI using Databricks magic commands.

```python
# Install PyForge CLI using Databricks %pip magic
%pip install "pyforge-cli" --quiet

# Restart Python to reload packages
dbutils.library.restartPython()
```

```python
# Import required libraries
import os
import sys
from datetime import datetime
from pathlib import Path
import json

# Databricks SDK
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import catalog

# PyForge imports
from pyforge_core import PyForgeCore
from pyforge_databricks import PyForgeDatabricks

# Spark imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp, count, sum as spark_sum

print("🚀 PyForge Databricks Integration loaded!")
print(f"📍 Python version: {sys.version.split()[0]}")
print(f"🏢 Databricks Runtime: {spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion')}")
```

---

## 2. Environment Detection and Validation

PyForge Databricks automatically detects your environment and optimizes accordingly.

```python
# Initialize PyForge Databricks
forge = PyForgeDatabricks()

# Get detailed environment information
env_info = forge.env.get_environment_info()

print("🔍 Environment Detection Results:")
print("=" * 60)

# Display environment details
env_details = [
    ("Databricks Environment", env_info['is_databricks'], "✅" if env_info['is_databricks'] else "❌"),
    ("Serverless Compute", env_info['is_serverless'], "⚡" if env_info['is_serverless'] else "🖥️"),
    ("Environment Version", env_info['environment_version'], f"v{env_info['environment_version']}"),
    ("Python Version", env_info['python_version'], "🐍"),
    ("Spark Version", env_info['spark_version'], "✨"),
    ("Cluster Type", env_info['cluster_type'], "🏢")
]

for label, value, icon in env_details:
    print(f"{icon} {label:25}: {value}")

# Validate SDK connection
print("\n🔌 Validating Databricks SDK connection...")
try:
    current_user = forge.w.current_user.me()
    print(f"✅ Connected as: {current_user.display_name}")
    print(f"📧 Email: {current_user.user_name}")
    sdk_connected = True
except Exception as e:
    print(f"❌ SDK connection failed: {str(e)}")
    print("   Note: Some features may be limited without SDK access")
    sdk_connected = False
```

---

## 3. Unity Catalog Volume Setup

Configure Unity Catalog paths and verify Volume access using Databricks file system magic.

```python
# Configure your Unity Catalog settings
CATALOG = "main"          # Replace with your catalog
SCHEMA = "default"        # Replace with your schema
BRONZE_VOLUME = "bronze"  # Raw data volume
SILVER_VOLUME = "silver"  # Processed data volume
GOLD_VOLUME = "gold"      # Curated data volume

# Construct Volume paths
bronze_path = f"/Volumes/{CATALOG}/{SCHEMA}/{BRONZE_VOLUME}"
silver_path = f"/Volumes/{CATALOG}/{SCHEMA}/{SILVER_VOLUME}"
gold_path = f"/Volumes/{CATALOG}/{SCHEMA}/{GOLD_VOLUME}"

print("📁 Unity Catalog Volume Configuration:")
print("=" * 60)
print(f"📦 Catalog: {CATALOG}")
print(f"📋 Schema: {SCHEMA}")
print(f"\nVolume Paths:")
print(f"  🥉 Bronze (Raw): {bronze_path}")
print(f"  🥈 Silver (Processed): {silver_path}")
print(f"  🥇 Gold (Curated): {gold_path}")
```

### Check and Create Volume Directories

```bash
# List available volumes using file system magic
%fs ls /Volumes/

# Check if our volumes exist
%fs ls /Volumes/main/default/ || echo "Please ensure Unity Catalog is configured"

# Create necessary subdirectories in Volumes
%fs mkdirs /Volumes/main/default/bronze/sample_datasets/
%fs mkdirs /Volumes/main/default/silver/
%fs mkdirs /Volumes/main/default/gold/
```

```python
# List available volumes using SDK
if sdk_connected:
    print("\n📂 Available Volumes:")
    try:
        volumes = forge.w.volumes.list(catalog_name=CATALOG, schema_name=SCHEMA)
        for vol in volumes:
            vol_type = "📁" if vol.volume_type == "MANAGED" else "🔗"
            print(f"  {vol_type} {vol.name} ({vol.volume_type})")
    except Exception as e:
        print(f"  ⚠️ Could not list volumes: {str(e)}")
else:
    print("\n⚠️ SDK not connected - skipping volume listing")
```

---

## 4. Installing Sample Datasets to Volumes

Install PyForge's curated sample datasets directly into Unity Catalog Volumes using CLI and file system magic.

### Download Sample Datasets Using Shell Magic

```bash
# Install sample datasets using PyForge CLI
%sh
pyforge install sample-datasets /tmp/pyforge_samples --formats csv,excel,xml,pdf,access,dbf --sizes small,medium

# List the downloaded datasets
%sh
find /tmp/pyforge_samples -type f | head -20
```

### Copy Datasets to Volumes Using File System Magic

```bash
# Copy sample datasets to Bronze Volume using file system magic
%fs cp -r file:/tmp/pyforge_samples/ /Volumes/main/default/bronze/sample_datasets/

# Verify the copy operation
%fs ls /Volumes/main/default/bronze/sample_datasets/

# List datasets by format
%fs ls /Volumes/main/default/bronze/sample_datasets/csv/small/
%fs ls /Volumes/main/default/bronze/sample_datasets/excel/small/
%fs ls /Volumes/main/default/bronze/sample_datasets/access/small/
```

```python
print("📦 PyForge Sample Datasets Installed to Volumes:")
print("=" * 60)

sample_volume_path = f"{bronze_path}/sample_datasets"

# Display installed datasets information
datasets_info = {
    "CSV": ["titanic-dataset.csv", "wine-quality.csv"],
    "Excel": ["financial-sample.xlsx", "global-superstore.xlsx"],
    "XML": ["uspto-patents.xml"],
    "PDF": ["NIST-CSWP-04162018.pdf"],
    "Access": ["Northwind_2007_VBNet.accdb", "access_sakila.mdb"],
    "DBF": ["tl_2024_us_county.dbf", "tl_2024_01_place.dbf"]
}

for format_name, files in datasets_info.items():
    print(f"\n{format_name}:")
    for file in files:
        print(f"  • {file}")

# Clean up temp directory using shell magic
%sh
rm -rf /tmp/pyforge_samples

print("\n✅ Sample datasets installation to Volumes completed!")
```

---

## 5. Basic Volume-to-Volume Conversions

Use the simplified `forge.convert()` API for Volume operations with real sample data.

### Convert CSV to Parquet using automatic Volume detection

```python
print("🔄 Converting Titanic CSV to Parquet...")
print("=" * 60)

# Input and output paths using real sample data in Volumes
input_csv = f"{sample_volume_path}/csv/small/titanic-dataset.csv"
output_parquet = f"{silver_path}/titanic.parquet"

print(f"📄 Input: {input_csv}")
print(f"📦 Output: {output_parquet}")
```

```bash
# Check file size using file system magic
%fs ls /Volumes/main/default/bronze/sample_datasets/csv/small/titanic-dataset.csv
```

```python
# Perform conversion - PyForge automatically detects Volume paths
result = forge.convert(
    input_path=input_csv,
    output_path=output_parquet,
    format_options={
        'compression': 'snappy',
        'schema_inference': True
    }
)

print(f"\n✅ Conversion successful!")
print(f"⏱️  Duration: {result['duration']:.2f}s")
print(f"📊 Rows processed: {result['row_count']}")
print(f"🔧 Processing engine: {result['processing_engine']}")
```

```bash
# Verify output file was created using file system magic
%fs ls /Volumes/main/default/silver/titanic.parquet/
```

```python
# Read and display the converted data
df = spark.read.parquet(output_parquet)
print(f"\n📋 Schema of converted data:")
df.printSchema()
print(f"\n📊 Data preview (showing first 5 rows):")
display(df.limit(5))
```

### Convert Wine Quality CSV with Auto-Generated Output

```python
print("🔄 Converting Wine Quality Dataset...")
print("=" * 60)

# Convert wine quality dataset without specifying output path
wine_input = f"{sample_volume_path}/csv/small/wine-quality.csv"

print(f"📄 Converting: {wine_input}")
print("📍 Output path will be auto-generated in the same volume")

result = forge.convert(
    input_path=wine_input,
    output_format="parquet"
)

print(f"\n✅ Conversion successful!")
print(f"📦 Output: {result['output_path']}")
print(f"⏱️  Duration: {result['duration']:.2f}s")
print(f"📊 Rows: {result['row_count']}")

# Analyze wine quality data
df = spark.read.parquet(result['output_path'])
print("\n🍷 Wine Quality Analysis:")
quality_dist = df.groupBy("quality").count().orderBy("quality")
display(quality_dist)
```

---

## 6. Working with Multi-Sheet Excel Files

Process Excel files with multiple sheets using real financial sample data in Volumes.

### Get Excel File Information Using CLI

```bash
# Use PyForge CLI to inspect Excel file in Volume
%sh
pyforge info /Volumes/main/default/bronze/sample_datasets/excel/small/financial-sample.xlsx
```

```python
print("📊 Processing Multi-Sheet Financial Excel File...")
print("=" * 60)

# Use real financial sample from datasets in Volume
excel_input = f"{sample_volume_path}/excel/small/financial-sample.xlsx"
excel_output = f"{silver_path}/financial-analysis.parquet"

# Get information about the Excel file using Python API
excel_info = forge.get_info(excel_input)
print(f"📋 Excel File Information:")
print(f"   File: financial-sample.xlsx")
print(f"   Sheets: {excel_info.get('sheet_count', 0)}")
print(f"   Sheet names: {excel_info.get('sheet_names', [])}")

# Convert with sheet combination
result = forge.convert(
    input_path=excel_input,
    output_path=excel_output,
    excel_options={
        'combine_sheets': True,
        'sheet_matching_strategy': 'column_signature',
        'include_sheet_name': True
    }
)

print(f"\n✅ Excel conversion completed!")
print(f"📊 Processing summary:")
print(f"   Sheets processed: {result['sheets_processed']}")
print(f"   Total rows: {result['row_count']}")
print(f"   Processing engine: {result['processing_engine']}")
```

```bash
# Check output using file system magic
%fs ls /Volumes/main/default/silver/financial-analysis.parquet/
```

```python
# Display combined data
df = spark.read.parquet(excel_output)
print(f"\n📋 Combined data structure:")
sheet_summary = df.groupBy("sheet_name").agg(
    count("*").alias("row_count")
)
display(sheet_summary)

# Show sample data from each sheet
for sheet in excel_info.get('sheet_names', [])[:3]:
    print(f"\n📄 Sample from sheet: {sheet}")
    display(df.filter(col("sheet_name") == sheet).limit(3))
```

---

## 7. Processing Complex XML with Patents Data

Work with hierarchical XML structures using Volume-stored data.

```python
print("🌳 Processing USPTO Patents XML Data...")
print("=" * 60)

# For demonstration, create a sample patent XML representing the structure
sample_patent_xml = """<?xml version="1.0" encoding="UTF-8"?>
<patents>
    <patent number="US10123456B2">
        <title>Distributed Data Processing System for Real-time Analytics</title>
        <inventors>
            <inventor sequence="1">
                <name>Dr. Sarah Johnson</name>
                <city>San Francisco</city>
                <country>US</country>
            </inventor>
            <inventor sequence="2">
                <name>Prof. Michael Chen</name>
                <city>Boston</city>
                <country>US</country>
            </inventor>
        </inventors>
        <assignee>
            <organization>Tech Innovations Corp</organization>
            <country>US</country>
        </assignee>
        <abstract>
            A distributed data processing system that enables real-time analytics
            on streaming data using advanced machine learning algorithms...
        </abstract>
        <claims count="20">
            <claim number="1">A method for processing streaming data...</claim>
            <claim number="2">The method of claim 1, wherein...</claim>
        </claims>
        <filing_date>2022-03-15</filing_date>
        <grant_date>2024-01-20</grant_date>
    </patent>
</patents>"""

# Create sample XML in Bronze Volume using file system magic
sample_xml_path = f"{bronze_path}/sample_patent.xml"
dbutils.fs.put(sample_xml_path, sample_patent_xml, overwrite=True)

xml_output = f"{silver_path}/patents_flattened.parquet"

print("📄 Converting XML with hierarchical flattening...")
print(f"   Input: {sample_xml_path}")
print(f"   Output: {xml_output}")

# Perform conversion with XML-specific options
result = forge.convert(
    input_path=sample_xml_path,
    output_path=xml_output,
    xml_options={
        'flatten_nested': True,
        'array_detection': True,
        'preserve_attributes': True,
        'root_tag': 'patent'
    }
)

print(f"\n✅ XML conversion successful!")
print(f"🔧 Processing details:")
print(f"   • Nested structures flattened")
print(f"   • Inventor arrays normalized")
print(f"   • XML attributes preserved as columns")

# Display the flattened result
df = spark.read.parquet(xml_output)
print(f"\n📊 Flattened structure ({df.count()} rows, {len(df.columns)} columns)")
print("📋 Columns created from XML hierarchy:")
for col_name in sorted(df.columns):
    print(f"   • {col_name}")
display(df)
```

---

## 8. Multi-Table Database Processing (Northwind)

Extract and convert multiple tables from the Northwind Access database stored in Volumes.

### Get Database Information Using CLI

```bash
# Use PyForge CLI to inspect the Northwind database in Volume
%sh
pyforge info /Volumes/main/default/bronze/sample_datasets/access/small/Northwind_2007_VBNet.accdb
```

```python
print("🗄️ Processing Northwind Multi-Table Database...")
print("=" * 60)

# Use Northwind database from sample datasets in Volume
northwind_path = f"{sample_volume_path}/access/small/Northwind_2007_VBNet.accdb"

# Get database information
db_info = forge.get_info(northwind_path)
print(f"📄 Database: Northwind_2007_VBNet.accdb")
print(f"   Tables found: {db_info.get('table_count', 'N/A')}")
print(f"   Tables: {', '.join(db_info.get('tables', [])[:5])}...")

# Define key tables to extract for analysis
key_tables = ['Customers', 'Orders', 'Products', 'Order Details', 'Employees']
```

```bash
# Create output directory in Silver Volume
%fs mkdirs /Volumes/main/default/silver/northwind/
```

```python
# Extract each table to Silver Volume
for table_name in key_tables:
    if table_name in db_info.get('tables', []):
        # Clean table name for file system
        clean_table_name = table_name.replace(' ', '_').lower()
        table_output = f"{silver_path}/northwind/{clean_table_name}.parquet"
        
        print(f"\n📊 Extracting table: {table_name}")
        
        try:
            result = forge.convert(
                input_path=northwind_path,
                output_path=table_output,
                access_options={
                    'table_name': table_name,
                    'preserve_types': True
                }
            )
            
            print(f"   ✅ Converted successfully")
            print(f"   📊 Rows: {result['row_count']}")
            
            # Preview the table
            df = spark.read.parquet(table_output)
            print(f"   📋 Columns: {', '.join(df.columns[:5])}...")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
```

```bash
# List all extracted tables using file system magic
%fs ls /Volumes/main/default/silver/northwind/
```

### Extract All Tables Using CLI

```bash
# Alternative: Use CLI to extract all tables at once to Volume
%sh
pyforge convert /Volumes/main/default/bronze/sample_datasets/access/small/Northwind_2007_VBNet.accdb /Volumes/main/default/silver/northwind_cli/ --extract-all-tables --output-format parquet

# List the extracted tables
%fs ls /Volumes/main/default/silver/northwind_cli/
```

### Analyze the Data with Spark

```python
# Create a joined dataset for analysis
print("\n🔗 Creating joined dataset for analysis...")
customers_df = spark.read.parquet(f"{silver_path}/northwind/customers.parquet")
orders_df = spark.read.parquet(f"{silver_path}/northwind/orders.parquet")

# Join customers with orders
customer_orders = customers_df.join(
    orders_df, 
    customers_df["CustomerID"] == orders_df["CustomerID"], 
    "inner"
).select(
    customers_df["CompanyName"],
    customers_df["Country"],
    orders_df["OrderID"],
    orders_df["OrderDate"],
    orders_df["ShippedDate"]
)

print("📊 Customer Orders Summary:")
country_summary = customer_orders.groupBy("Country").agg(
    count("OrderID").alias("total_orders")
).orderBy("total_orders", ascending=False)
display(country_summary.limit(10))
```

---

## 9. PDF Text Extraction at Scale

Extract text from government PDFs stored in Volumes for analysis.

### PDF Processing Using CLI

```bash
# Extract text using PyForge CLI from Volume-stored PDF
%sh
pyforge convert /Volumes/main/default/bronze/sample_datasets/pdf/small/NIST-CSWP-04162018.pdf /Volumes/main/default/silver/nist_framework.txt --pdf-pages 1-10

# Preview extracted text
%fs head /Volumes/main/default/silver/nist_framework.txt --max-bytes 2000
```

```python
print("📄 Processing NIST Cybersecurity Framework PDF...")
print("=" * 60)

# Use NIST PDF from sample datasets in Volume
pdf_input = f"{sample_volume_path}/pdf/small/NIST-CSWP-04162018.pdf"
text_output = f"{silver_path}/nist_framework_python.txt"

# Get PDF information
pdf_info = forge.get_info(pdf_input)
print(f"📄 Document: NIST-CSWP-04162018.pdf")
print(f"   Pages: {pdf_info.get('page_count', 'N/A')}")
print(f"   Size: ~1.0 MB")

# Extract text from PDF using Python API
result = forge.convert(
    input_path=pdf_input,
    output_path=text_output,
    pdf_options={
        'page_range': '1-10',  # Extract first 10 pages
        'preserve_formatting': True,
        'include_metadata': True
    }
)

print(f"\n✅ PDF text extraction completed!")
print(f"   Pages processed: 10")
print(f"   Processing engine: {result['processing_engine']}")
```

```bash
# Check file size using shell magic
%sh
ls -lh /Volumes/main/default/silver/nist_framework_python.txt
```

```python
# Analyze the extracted text using Spark
text_df = spark.read.text(text_output)
print(f"\n📊 Text statistics:")
print(f"   Total lines: {text_df.count()}")

# Find key framework components
framework_keywords = ["Identify", "Protect", "Detect", "Respond", "Recover"]
for keyword in framework_keywords:
    keyword_count = text_df.filter(col("value").contains(keyword)).count()
    print(f"   '{keyword}' mentions: {keyword_count}")
```

---

## 10. Geographic Data Processing (DBF)

Process US Census TIGER geographic data files stored in Volumes.

### DBF Processing Using CLI and Python

```bash
# Convert using CLI from Volume
%sh
pyforge convert /Volumes/main/default/bronze/sample_datasets/dbf/small/tl_2024_us_county.dbf /Volumes/main/default/silver/us_counties_cli.parquet

# Check output
%fs ls /Volumes/main/default/silver/us_counties_cli.parquet/
```

```python
print("🗺️ Processing US Census Geographic Data...")
print("=" * 60)

# Use Census county data from Volume samples
dbf_input = f"{sample_volume_path}/dbf/small/tl_2024_us_county.dbf"
geo_output = f"{silver_path}/us_counties_geo.parquet"

# Get DBF information
dbf_info = forge.get_info(dbf_input)
print(f"📄 File: tl_2024_us_county.dbf")
print(f"   Records: {dbf_info.get('record_count', 'N/A')}")
print(f"   Fields: {dbf_info.get('field_count', 'N/A')}")

# Convert DBF to Parquet using Python API
result = forge.convert(
    input_path=dbf_input,
    output_path=geo_output,
    dbf_options={
        'encoding': 'latin-1',
        'include_deleted': False
    }
)

print(f"\n✅ DBF conversion successful!")
print(f"   Counties processed: {result['row_count']}")

# Analyze geographic data
geo_df = spark.read.parquet(geo_output)
print(f"\n📊 Geographic Data Schema:")
geo_df.printSchema()

# County statistics by state
state_summary = geo_df.groupBy("STATEFP").agg(
    count("*").alias("county_count"),
    spark_sum("ALAND").alias("total_land_area"),
    spark_sum("AWATER").alias("total_water_area")
).orderBy("county_count", ascending=False)

print("\n🏛️ Top 10 States by County Count:")
display(state_summary.limit(10))

# Find largest counties by land area
print("\n🌍 Top 10 Largest Counties by Land Area:")
largest_counties = geo_df.orderBy(col("ALAND").desc()).select(
    "NAME", "STATEFP", "ALAND", "AWATER"
).limit(10)
display(largest_counties)
```

---

## 11. Batch Processing with Parallel Execution

Process multiple files efficiently using PyForge Databricks batch capabilities with Volume storage.

### Batch Processing Using Shell Script

```bash
# Create a batch processing script for Volume operations
%sh
cat << 'EOF' > /tmp/volume_batch_convert.sh
#!/bin/bash
echo "🔄 Volume Batch Processing with PyForge CLI"
echo "==========================================="

# Convert CSV files from Volume to Volume
echo "Processing CSV files..."
pyforge convert /Volumes/main/default/bronze/sample_datasets/csv/small/titanic-dataset.csv /Volumes/main/default/silver/batch/titanic.parquet
pyforge convert /Volumes/main/default/bronze/sample_datasets/csv/small/wine-quality.csv /Volumes/main/default/silver/batch/wine.parquet

# Convert DBF files from Volume to Volume
echo "Processing DBF files..."
pyforge convert /Volumes/main/default/bronze/sample_datasets/dbf/small/tl_2024_us_county.dbf /Volumes/main/default/silver/batch/us_counties.parquet
pyforge convert /Volumes/main/default/bronze/sample_datasets/dbf/small/tl_2024_01_place.dbf /Volumes/main/default/silver/batch/alabama_places.parquet

echo "✅ Volume batch processing completed!"
EOF

chmod +x /tmp/volume_batch_convert.sh

# Create batch output directory in Silver Volume
%fs mkdirs /Volumes/main/default/silver/batch/

# Run batch conversion
%sh
/tmp/volume_batch_convert.sh

# List batch output
%fs ls /Volumes/main/default/silver/batch/
```

### Parallel Processing Using Python API

```python
print("🔄 Batch Processing Multiple Dataset Files...")
print("=" * 60)

from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Define Volume files to process in batch
batch_files = [
    (f"{sample_volume_path}/csv/small/titanic-dataset.csv", "titanic"),
    (f"{sample_volume_path}/csv/small/wine-quality.csv", "wine"),
    (f"{sample_volume_path}/dbf/small/tl_2024_01_place.dbf", "alabama_places"),
    (f"{sample_volume_path}/excel/small/financial-sample.xlsx", "financial")
]

def convert_volume_file(input_info):
    """Convert a single file in Volume"""
    input_path, output_name = input_info
    output_path = f"{silver_path}/batch_python/{output_name}.parquet"
    
    start_time = time.time()
    try:
        result = forge.convert(
            input_path=input_path,
            output_path=output_path,
            format_options={'compression': 'snappy'}
        )
        
        return {
            'file': output_name,
            'status': 'success',
            'duration': time.time() - start_time,
            'rows': result.get('row_count', 0),
            'engine': result.get('processing_engine', 'Unknown'),
            'output': output_path
        }
    except Exception as e:
        return {
            'file': output_name,
            'status': 'failed',
            'error': str(e),
            'duration': time.time() - start_time
        }

# Create output directory
%fs mkdirs /Volumes/main/default/silver/batch_python/

# Process files in parallel
batch_start = time.time()
results = []

print(f"📊 Processing {len(batch_files)} Volume files in parallel...")

with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit all conversion tasks
    future_to_file = {executor.submit(convert_volume_file, f): f for f in batch_files}
    
    # Process completed conversions
    for future in as_completed(future_to_file):
        result = future.result()
        results.append(result)
        
        if result['status'] == 'success':
            print(f"✅ {result['file']} → Converted in {result['duration']:.2f}s using {result['engine']}")
        else:
            print(f"❌ {result['file']} → Failed: {result['error']}")

# Summary statistics
batch_duration = time.time() - batch_start
success_count = sum(1 for r in results if r['status'] == 'success')
total_rows = sum(r.get('rows', 0) for r in results if r['status'] == 'success')

print(f"\n📊 Batch Processing Summary:")
print(f"   Total files: {len(batch_files)}")
print(f"   Successful: {success_count}")
print(f"   Failed: {len(batch_files) - success_count}")
print(f"   Total duration: {batch_duration:.2f}s")
print(f"   Average time per file: {batch_duration/len(batch_files):.2f}s")
print(f"   Total rows processed: {total_rows:,}")

# Show processing engines used
engines_used = set(r.get('engine', 'Unknown') for r in results if r['status'] == 'success')
print(f"\n🔧 Processing Engines Used:")
for engine in engines_used:
    print(f"   • {engine}")
```

```bash
# List all batch output files
%fs ls /Volumes/main/default/silver/batch_python/
```

---

## 12. Delta Lake Integration

Convert data to Delta Lake format for versioning and time travel capabilities in Volumes.

```python
# Convert Titanic dataset to Delta Lake format in Gold Volume
print("🔺 Converting to Delta Lake Format with Optimization...")
print("=" * 60)

# Source data in Silver Volume
source_parquet = f"{silver_path}/titanic.parquet"
delta_table_path = f"{gold_path}/titanic_delta"

print(f"📄 Source: {source_parquet}")
print(f"🔺 Target Delta: {delta_table_path}")

# Convert to Delta with optimization
result = forge.convert(
    input_path=source_parquet,
    output_path=delta_table_path,
    output_format="delta",
    delta_options={
        'mode': 'overwrite',
        'optimizeWrite': True,
        'autoCompact': True,
        'dataChange': True
    }
)

print(f"\n✅ Delta conversion successful!")
print(f"⏱️  Duration: {result['duration']:.2f}s")
print(f"🔧 Processing engine: {result['processing_engine']}")
```

```bash
# Verify Delta table creation in Volume
%fs ls /Volumes/main/default/gold/titanic_delta/
```

```python
# Create Delta table
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS titanic_delta
    USING DELTA
    LOCATION '{delta_table_path}'
""")

print("\n📊 Delta Table Information:")
display(spark.sql("DESCRIBE DETAIL titanic_delta"))

# Perform data quality improvements
print("\n🔧 Performing data quality updates...")
spark.sql("""
    UPDATE titanic_delta 
    SET Age = 30 
    WHERE Age IS NULL
""")

spark.sql("""
    UPDATE titanic_delta 
    SET Embarked = 'S' 
    WHERE Embarked IS NULL
""")

# Show Delta table history
print("\n📜 Delta Table History:")
display(spark.sql("DESCRIBE HISTORY titanic_delta"))

# Time travel query
print("\n⏰ Time Travel: View data before updates")
display(spark.sql("SELECT * FROM titanic_delta VERSION AS OF 0 LIMIT 5"))
```

---

## 13. Performance Monitoring and Optimization

Monitor conversion performance and resource utilization in Databricks environment with Volume operations.

### System Monitoring Using Shell Magic

```bash
# Monitor system resources
%sh
echo "📊 System Resource Monitoring"
echo "=============================="
df -h | grep -E "(Filesystem|/)"
echo ""
echo "Memory usage:"
free -h
echo ""
echo "Process information:"
ps aux | grep pyforge | head -5
```

### Volume Storage Analysis

```bash
# Analyze Volume storage usage
%fs ls /Volumes/main/default/bronze/ -l
%fs ls /Volumes/main/default/silver/ -l
%fs ls /Volumes/main/default/gold/ -l

# Check specific Volume sizes (if supported)
# Note: Volume size commands may vary by implementation
%sh
echo "Volume storage analysis would go here"
```

```python
print("📊 Performance Monitoring Dashboard")
print("=" * 60)

# Get conversion statistics
stats = forge.get_conversion_statistics()

if stats:
    print("\n📈 Session Conversion Statistics:")
    print(f"   Total conversions: {stats['total_conversions']}")
    print(f"   Successful: {stats['successful']}")
    print(f"   Failed: {stats['failed']}")
    print(f"   Average duration: {stats['avg_duration']:.2f}s")
    print(f"   Total data processed: {stats['total_bytes_processed'] / (1024**3):.2f} GB")

# Check serverless optimizations
if forge.env.is_serverless:
    print("\n⚡ Serverless Optimizations Active:")
    optimizations = [
        ("Photon Acceleration", "2-10x faster processing"),
        ("Adaptive Query Execution", "Dynamic optimization"),
        ("Auto-scaling", "Resources scale with workload"),
        ("Columnar Caching", "Faster repeated queries"),
        ("Dynamic File Pruning", "Reduced I/O operations")
    ]
    
    for opt, benefit in optimizations:
        print(f"   ✅ {opt}: {benefit}")
    
    # Show key Spark configurations
    print("\n🔧 Spark Configuration:")
    configs = [
        "spark.databricks.compute.type",
        "spark.databricks.photon.enabled",
        "spark.sql.adaptive.enabled",
        "spark.sql.adaptive.coalescePartitions.enabled",
        "spark.sql.adaptive.skewJoin.enabled"
    ]
    
    for config in configs:
        try:
            value = spark.conf.get(config)
            print(f"   {config}: {value}")
        except:
            print(f"   {config}: Not set")

# Memory usage guidelines by format for Volume operations
print("\n💾 Memory Usage Guidelines by Format (Volume Operations):")
memory_guide = {
    'CSV': {'factor': 1.5, 'note': 'Optimized with Spark', 'engine': 'Spark'},
    'JSON': {'factor': 2.5, 'note': 'Spark JSON parsing', 'engine': 'Spark'},
    'XML': {'factor': 3.5, 'note': 'Spark XML processing', 'engine': 'Spark'},
    'Excel': {'factor': 2.5, 'note': 'Hybrid processing', 'engine': 'Hybrid'},
    'Parquet': {'factor': 0.3, 'note': 'Native Spark format', 'engine': 'Spark'},
    'PDF': {'factor': 1.5, 'note': 'Text extraction', 'engine': 'PyForge'},
    'Access': {'factor': 2, 'note': 'Database extraction', 'engine': 'PyForge'},
    'DBF': {'factor': 1.2, 'note': 'Optimized parsing', 'engine': 'PyForge'}
}

for format_type, info in memory_guide.items():
    print(f"   {format_type}: ~{info['factor']}x file size ({info['note']}) - {info['engine']}")
```

---

## 14. Production Best Practices for Volume Operations

Guidelines for using PyForge Databricks in production environments with Unity Catalog Volumes.

```python
print("📚 Production Best Practices for Volume Operations")
print("=" * 60)

best_practices = {
    "🗂️ Volume Organization": [
        "Follow medallion architecture (Bronze → Silver → Gold) with Volumes",
        "Use Unity Catalog permissions for fine-grained access control",
        "Implement Volume retention policies for each layer",
        "Use descriptive naming with timestamps and versions",
        "Leverage Volume lineage tracking for data governance"
    ],
    
    "⚡ Performance Optimization": [
        "Use %fs commands for Volume operations (faster than shell)",
        "Leverage serverless compute for variable workloads",
        "Enable Photon acceleration for supported formats",
        "Use Volume caching for frequently accessed datasets",
        "Implement parallel processing for batch Volume operations"
    ],
    
    "🔒 Security & Governance": [
        "Use Unity Catalog for centralized governance",
        "Implement Volume-level access controls",
        "Enable audit logging for all Volume operations",
        "Use service principals for automated workflows",
        "Tag resources for cost tracking and compliance"
    ],
    
    "🛠️ Error Handling & Reliability": [
        "Implement retry logic for Volume operations",
        "Use checkpointing for long-running conversions",
        "Monitor Volume space and quotas",
        "Set up alerts for failed conversions",
        "Maintain backup strategies for critical data"
    ],
    
    "📈 Monitoring & Observability": [
        "Track conversion metrics across Volumes",
        "Monitor Volume storage costs and usage",
        "Use Databricks observability for pipeline health",
        "Set up dashboards for data lineage",
        "Regular performance benchmarking"
    ],
    
    "🎯 Volume-Specific Tips": [
        "Use %fs cp for efficient Volume-to-Volume transfers",
        "Implement Volume partitioning for large datasets",
        "Leverage Delta Lake for versioning in Gold Volume",
        "Use managed tables for important datasets",
        "Regular Volume maintenance and optimization"
    ]
}

for category, practices in best_practices.items():
    print(f"\n{category}:")
    for practice in practices:
        print(f"  • {practice}")
```

---

## Summary

You've learned how to use PyForge Databricks for advanced data processing with Unity Catalog Volumes:

✅ **Databricks Magic Commands**: Proper use of %sh, %pip, %fs for PyForge and Volume operations  
✅ **Volume Integration**: Direct operations on Unity Catalog Volumes with governance  
✅ **Sample Datasets**: Real-world files installed and processed in Volumes  
✅ **Multi-Table Databases**: Extract and join database tables in Volume storage  
✅ **Smart Routing**: Optimal processing engine selection for Volume operations  
✅ **Batch Processing**: Parallel execution for multiple Volume files  
✅ **Delta Lake**: Native support for versioned data in Gold Volume  
✅ **Performance**: Monitoring and optimization for Volume workloads  
✅ **Production Ready**: Best practices with Unity Catalog governance  

### Key Advantages:
- **Volume-Native**: Direct operations on Unity Catalog Volumes
- **Unified API**: Simple `forge.convert()` works with Volume paths
- **Auto-optimization**: Detects and uses best processing engine
- **Serverless-ready**: Scales automatically with workload
- **Governed**: Full Unity Catalog integration for compliance

### Next Steps:
1. Configure Unity Catalog Volumes in your environment
2. Install PyForge packages: `%pip install pyforge-core pyforge-databricks`
3. Install sample datasets to Volumes using `%sh pyforge install`
4. Build production pipelines with Volume-based medallion architecture
5. Monitor and optimize performance with Databricks observability

### Key Databricks Magic Commands for Volumes:
- `%pip install` - Package installation across cluster
- `%sh pyforge` - PyForge CLI commands for Volume operations
- `%fs ls/cp/mkdirs` - Volume file system operations
- `%fs head/cat` - Volume file content preview
- Volume path handling: `/Volumes/catalog/schema/volume/`

```python
# Display package versions and environment
print("📦 Package Information:")
print("=" * 60)
print(f"pyforge-core version: {PyForgeCore.__version__}")
print(f"pyforge-databricks version: {PyForgeDatabricks.__version__}")
print(f"Databricks SDK version: {forge.w.version}")
print(f"Python version: {sys.version.split()[0]}")
print(f"Spark version: {spark.version}")

# Volume dataset summary
print("\n📊 Sample Datasets in Volumes:")
print("   • CSV: Titanic, Wine Quality")
print("   • Excel: Financial Sample, Global Superstore")
print("   • XML: USPTO Patents")
print("   • PDF: NIST Cybersecurity Framework")
print("   • Access: Northwind, Sakila databases")
print("   • DBF: US Census TIGER geographic data")

print("\n🎉 Happy converting with PyForge Databricks and Unity Catalog Volumes!")
```

## How to Use This Notebook

1. **Import to Databricks**: Copy the notebook content and create a new notebook in your Databricks workspace
2. **Configure Unity Catalog**: Ensure you have access to Unity Catalog and Volumes
3. **Update Volume Paths**: Update CATALOG, SCHEMA, and VOLUME names to match your environment
4. **Install PyForge**: Run the %pip install cells to get both packages
5. **Install Sample Datasets**: Use %sh and %fs commands to install datasets to Volumes
6. **Run Examples**: Execute cells in order to see different conversions with Volume storage
7. **Production Use**: Adapt examples to your specific use cases with governed data access