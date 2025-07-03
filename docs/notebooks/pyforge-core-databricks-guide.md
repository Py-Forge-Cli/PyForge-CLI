# PyForge CLI: Data Format Conversion in Databricks

<div align="right">
📥 <strong><a href="#" id="download-notebook" download="pyforge-cli-databricks-guide.ipynb">Download Jupyter Notebook</a></strong>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const downloadLink = document.getElementById('download-notebook');
    const currentHost = window.location.origin;
    const currentPath = window.location.pathname;
    
    // Check if we're on localhost (development) or production
    if (currentHost.includes('localhost') || currentHost.includes('127.0.0.1')) {
        // Local development - point to local file
        downloadLink.href = currentHost + '/notebooks/pyforge-cli-databricks-guide.ipynb';
    } else if (currentHost.includes('github.io')) {
        // GitHub Pages - construct raw GitHub URL
        const pathParts = currentPath.split('/');
        const repoOwner = pathParts[1]; // Usually the username
        const repoName = pathParts[2] || 'PyForge-CLI'; // Repository name
        downloadLink.href = `https://raw.githubusercontent.com/${repoOwner}/${repoName}/main/docs/notebooks/pyforge-cli-databricks-guide.ipynb`;
    } else {
        // Other hosting - try relative path first, fallback to GitHub
        downloadLink.href = '/docs/notebooks/pyforge-cli-databricks-guide.ipynb';
        
        // If that fails, fallback to GitHub raw URL
        downloadLink.addEventListener('error', function() {
            downloadLink.href = 'https://raw.githubusercontent.com/Py-Forge-Cli/PyForge-CLI/main/docs/notebooks/pyforge-cli-databricks-guide.ipynb';
        });
    }
});
</script>

This notebook demonstrates how to use PyForge CLI for data format conversion in Databricks environments. PyForge CLI provides powerful command-line tools for converting between various data formats including CSV, Excel, PDF, XML, Access databases, and more.

## Introduction

PyForge CLI is a comprehensive data format conversion command-line tool that works seamlessly in Databricks notebook environments using shell magic commands. This guide will walk you through:

- Installing PyForge CLI in Databricks
- Installing and using sample datasets
- Converting between various file formats using CLI commands
- Working with multi-table databases and auto-detection
- Using %sh magic commands for all operations
- Leveraging CLI's intelligent format detection

---

## 1. Installation and Setup

First, let's install PyForge CLI and verify our environment using Databricks shell magic commands.

```bash
# Install PyForge CLI using %pip magic
%pip install "pyforge-cli" --quiet

# Restart Python to reload packages  
dbutils.library.restartPython()
```

```bash
# Verify PyForge CLI installation and check version
%sh
pyforge --version

# Check available PyForge commands
%sh 
pyforge --help

# Display system information
%sh
echo "📍 System Information:"
echo "======================"  
python --version
echo "🏢 Databricks Runtime: $(echo $DATABRICKS_RUNTIME_VERSION)"
echo "💾 Available disk space:"
df -h /tmp
```

---

## 2. Installing Sample Datasets

PyForge CLI includes a comprehensive collection of curated sample datasets for all supported formats. We'll use shell magic commands to install and explore these datasets.

```bash
# Display available PyForge CLI commands
%sh
echo "📋 PyForge CLI Commands:"
echo "========================"
pyforge --help

# Show supported formats
%sh
echo "🎯 Supported Formats:"
echo "===================="
pyforge formats
```

### Install Sample Datasets Using Shell Magic

```bash
# Install sample datasets using PyForge CLI
%sh
echo "📦 Installing PyForge Sample Datasets..."
pyforge install sample-datasets /tmp/pyforge_samples --formats csv,excel,xml,pdf,access,dbf --sizes small,medium

# Verify installation success
%sh
echo "✅ Installation completed. Checking directory structure..."
ls -la /tmp/pyforge_samples/
```

### Explore Installed Datasets

```bash
# List the installed sample datasets by format
%sh  
echo "📊 Exploring Sample Dataset Structure:"
echo "===================================="
for format in csv excel xml pdf access dbf; do
    echo ""
    echo "📁 $format format:"
    ls -la /tmp/pyforge_samples/$format/small/ 2>/dev/null || echo "  (no small files for $format)"
    ls -la /tmp/pyforge_samples/$format/medium/ 2>/dev/null || echo "  (no medium files for $format)"
done

# Show total dataset sizes
%sh
echo "💾 Dataset Size Summary:"
echo "======================="
du -sh /tmp/pyforge_samples/*/
echo ""
echo "📊 Total collection size:"
du -sh /tmp/pyforge_samples/
```

```bash
# Display file details for each format
%sh
echo "📋 Sample Dataset Details:"
echo "========================="
echo ""
echo "📈 CSV Files (Analytics Data):"
ls -lh /tmp/pyforge_samples/csv/small/
echo ""
echo "📊 Excel Files (Business Data):"  
ls -lh /tmp/pyforge_samples/excel/small/
echo ""
echo "📄 PDF Files (Document Data):"
ls -lh /tmp/pyforge_samples/pdf/small/ 2>/dev/null || echo "  No PDF files in small category"
echo ""
echo "🗄️ Access Database Files (Multi-table Data):"
ls -lh /tmp/pyforge_samples/access/small/
echo ""
echo "🗺️ DBF Files (Geographic Data):"
ls -lh /tmp/pyforge_samples/dbf/small/
```

---

## 3. Basic File Conversion - CSV to Parquet

Let's start with a simple CSV conversion using the Titanic dataset and CLI commands.

### Example 1: Convert CSV to Parquet using CLI
*Command: `pyforge convert titanic-dataset.csv titanic.parquet`*

```bash
# Create output directory
%sh
mkdir -p /tmp/pyforge_output

# Check the source CSV file
%sh
echo "📁 Source file information:"
ls -lh /tmp/pyforge_samples/csv/small/titanic-dataset.csv

# Convert CSV to Parquet using PyForge CLI
%sh
echo "🔄 Converting Titanic CSV to Parquet..."
pyforge convert /tmp/pyforge_samples/csv/small/titanic-dataset.csv /tmp/pyforge_output/titanic.parquet

# Verify conversion completed
%sh
echo "✅ Conversion completed! Output file:"
ls -lh /tmp/pyforge_output/titanic.parquet
```

### Example 2: File Information using CLI

```bash
# Get detailed file information using PyForge CLI
%sh
echo "📋 File Information:"
echo "==================="
pyforge info /tmp/pyforge_samples/csv/small/titanic-dataset.csv

# Show first few lines of the CSV
%sh
echo ""
echo "📊 CSV Content Preview:"
echo "======================="
head -n 6 /tmp/pyforge_samples/csv/small/titanic-dataset.csv
```

### Example 3: View Converted Data

```python
# Load and display the converted Parquet data
df = spark.read.parquet("file:/tmp/pyforge_output/titanic.parquet")
print(f"📊 Converted data: {df.count()} rows, {len(df.columns)} columns")
print("Columns:", df.columns)
display(df.limit(5))
```

---

## 4. Working with Multi-Sheet Excel Files

The sample datasets include Excel files with multiple sheets. PyForge CLI automatically detects sheets and provides options for handling them.

### Excel File Analysis and Multi-Sheet Detection

```bash
# Inspect the Excel file structure
%sh
echo "📊 Excel File Analysis:"
echo "======================"
file /tmp/pyforge_samples/excel/small/financial-sample.xlsx

# Get detailed Excel file information using PyForge CLI
%sh
echo ""
echo "📋 Excel Sheet Detection:"
echo "========================="
pyforge info /tmp/pyforge_samples/excel/small/financial-sample.xlsx
```

### Convert Excel with Sheet Detection
*Command: `pyforge convert financial-sample.xlsx output-folder/`*

```bash
# Convert Excel file - PyForge CLI automatically detects multiple sheets
%sh
echo "🔄 Converting Excel with Multi-Sheet Detection..."
pyforge convert /tmp/pyforge_samples/excel/small/financial-sample.xlsx /tmp/pyforge_output/financial-sheets/

# List the output files created
%sh
echo "✅ Conversion completed! Output files:"
ls -la /tmp/pyforge_output/financial-sheets/
```

### Alternative: Convert to Single Combined File

```bash
# Convert all sheets to a single combined file
%sh
echo "🔄 Converting Excel to Single Combined Parquet..."
pyforge convert /tmp/pyforge_samples/excel/small/financial-sample.xlsx /tmp/pyforge_output/financial-combined.parquet --combine-sheets

# Check the combined output
%sh
echo "✅ Combined conversion completed:"
ls -lh /tmp/pyforge_output/financial-combined.parquet
```

### View the Results

```python
# View individual sheet files
import os
sheet_files = [f for f in os.listdir("/tmp/pyforge_output/financial-sheets/") if f.endswith('.parquet')]
print(f"📊 Individual sheets converted: {len(sheet_files)}")
for sheet_file in sheet_files:
    print(f"  • {sheet_file}")

# Load and display one sheet
if sheet_files:
    df = spark.read.parquet(f"file:/tmp/pyforge_output/financial-sheets/{sheet_files[0]}")
    print(f"\n📊 Sample sheet '{sheet_files[0]}': {df.count()} rows, {len(df.columns)} columns")
    display(df.limit(3))
```

---

## 5. Processing Complex XML Files

The sample datasets include XML files with hierarchical structures. Let's process a patent XML file.

### XML to Parquet with Hierarchical Flattening
*CLI equivalent: `pyforge convert uspto-patents.xml patents-flat.parquet --flatten-nested`*

```bash
# Check if we have the USPTO patents file
%fs ls /tmp/pyforge_samples/xml/medium/

# Get file information using CLI
%sh
pyforge info /tmp/pyforge_samples/xml/medium/uspto-patents.xml || echo "Creating sample XML for demo"
```

```python
# For demonstration, let's create a smaller sample XML that represents patent structure
sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<patents>
    <patent id="US123456">
        <title>Innovative Data Processing System</title>
        <inventors>
            <inventor>
                <name>Jane Smith</name>
                <country>USA</country>
                <city>San Francisco</city>
            </inventor>
            <inventor>
                <name>John Doe</name>
                <country>Canada</country>
                <city>Toronto</city>
            </inventor>
        </inventors>
        <filing_date>2023-01-15</filing_date>
        <classification>
            <primary>G06F</primary>
            <secondary>G06N</secondary>
        </classification>
        <abstract>A system for processing large-scale data using distributed computing...</abstract>
    </patent>
    <patent id="US789012">
        <title>Machine Learning Algorithm</title>
        <inventors>
            <inventor>
                <name>Alice Johnson</name>
                <country>UK</country>
                <city>London</city>
            </inventor>
        </inventors>
        <filing_date>2023-03-20</filing_date>
        <classification>
            <primary>G06N</primary>
        </classification>
        <abstract>An improved ML algorithm for predictive analytics...</abstract>
    </patent>
</patents>"""

# Create sample XML file using file system magic
sample_xml_path = "/tmp/pyforge_output/sample-patents.xml"
dbutils.fs.put(f"file:{sample_xml_path}", sample_xml, overwrite=True)

print("🌳 Processing Hierarchical XML Data...")
print("=" * 50)

xml_output = f"/tmp/pyforge_output/patents-flat.parquet"

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

print("✅ XML conversion completed!")
print("   Hierarchical structure flattened")
print("   Nested arrays normalized")

# Display the result
df = spark.read.parquet(f"file:{xml_output}")
print(f"\n📊 Flattened structure: {df.count()} rows, {len(df.columns)} columns")
print("Columns created from XML hierarchy:")
for col_name in sorted(df.columns):
    print(f"  • {col_name}")
display(df)
```

---

## 6. Working with Multi-Table Databases (Access/MDB) - Key Feature!

This is where PyForge CLI really shines! It automatically detects multiple tables in Access databases and can extract them all or individually.

### Database Analysis and Multi-Table Detection

```bash
# Check available Access database files
%sh
echo "🗄️ Available Access Database Files:"
echo "==================================="
ls -lh /tmp/pyforge_samples/access/small/

# Analyze the Northwind database - PyForge CLI automatically detects all tables
%sh
echo ""
echo "📋 Multi-Table Database Analysis:"
echo "================================="
pyforge info /tmp/pyforge_samples/access/small/Northwind_2007_VBNet.accdb
```

### Extract ALL Tables Automatically using CLI
*Command: `pyforge convert database.accdb output-folder/` - Auto-detects and extracts all tables!*

```bash
# PyForge CLI automatically detects ALL tables and converts them
%sh
echo "🔄 Auto-Extracting ALL Tables from Northwind Database..."
echo "PyForge CLI will automatically detect and convert all tables!"
pyforge convert /tmp/pyforge_samples/access/small/Northwind_2007_VBNet.accdb /tmp/pyforge_output/northwind_all_tables/

# List all the extracted table files
%sh
echo "✅ All tables extracted! Generated files:"
ls -la /tmp/pyforge_output/northwind_all_tables/
echo ""
echo "📊 File sizes:"
ls -lh /tmp/pyforge_output/northwind_all_tables/*.parquet
```

### Extract Specific Table using CLI
*Command: `pyforge convert database.accdb table_name.parquet --table "TableName"`*

```bash
# Extract just the Customers table
%sh
echo "🔄 Extracting specific table: Customers"
pyforge convert /tmp/pyforge_samples/access/small/Northwind_2007_VBNet.accdb /tmp/pyforge_output/customers_only.parquet --table "Customers"

# Extract the Orders table
%sh
echo "🔄 Extracting specific table: Orders"
pyforge convert /tmp/pyforge_samples/access/small/Northwind_2007_VBNet.accdb /tmp/pyforge_output/orders_only.parquet --table "Orders"

# List specific table extractions
%sh
echo "✅ Specific table extractions completed:"
ls -lh /tmp/pyforge_output/*_only.parquet
```

### Demonstrate with Another Database

```bash
# Try with the Sakila database (movie rental database)
%sh
echo "🎬 Analyzing Sakila Database (Movie Rental System):"
echo "=================================================="
pyforge info /tmp/pyforge_samples/access/small/access_sakila.mdb

# Auto-extract all tables from Sakila
%sh
echo ""
echo "🔄 Auto-extracting all Sakila tables..."
pyforge convert /tmp/pyforge_samples/access/small/access_sakila.mdb /tmp/pyforge_output/sakila_tables/

# Show Sakila results
%sh
echo "✅ Sakila database tables extracted:"
ls -la /tmp/pyforge_output/sakila_tables/
```

### View the Multi-Table Results

```python
# Analyze the extracted Northwind tables
import os
northwind_files = [f for f in os.listdir("/tmp/pyforge_output/northwind_all_tables/") if f.endswith('.parquet')]
print(f"🗄️ Northwind Database: {len(northwind_files)} tables extracted automatically!")
print("Tables:")
for table_file in sorted(northwind_files):
    table_name = table_file.replace('.parquet', '')
    df = spark.read.parquet(f"file:/tmp/pyforge_output/northwind_all_tables/{table_file}")
    print(f"  • {table_name:20}: {df.count():5} rows, {len(df.columns):2} columns")

# Display sample data from Customers table
print(f"\n📊 Sample data from Customers table:")
customers_df = spark.read.parquet("file:/tmp/pyforge_output/northwind_all_tables/Customers.parquet")
display(customers_df.limit(3))
```

---

## 7. PDF Text Extraction using CLI

PyForge CLI can extract text from PDF files with intelligent formatting detection.

### PDF Analysis and Text Extraction

```bash
# Check available PDF files
%sh
echo "📄 Available PDF Files:"
echo "======================"
ls -lh /tmp/pyforge_samples/pdf/small/ 2>/dev/null || echo "No PDF files in small directory"

# For demo, let's check if we have PDF in medium size
ls -lh /tmp/pyforge_samples/pdf/medium/ 2>/dev/null || echo "No PDF files in medium directory"

# Alternative: create a sample PDF file for demonstration
echo "Creating sample PDF content for demo..."
```

### Extract Text from PDF using CLI
*Command: `pyforge convert document.pdf output.txt`*

```bash
# If PDF exists, extract text using PyForge CLI
%sh
if [ -f "/tmp/pyforge_samples/pdf/small/NIST-CSWP-04162018.pdf" ]; then
    echo "📄 PDF Text Extraction:"
    echo "======================"
    pyforge info /tmp/pyforge_samples/pdf/small/NIST-CSWP-04162018.pdf
    echo ""
    echo "🔄 Extracting text from PDF..."
    pyforge convert /tmp/pyforge_samples/pdf/small/NIST-CSWP-04162018.pdf /tmp/pyforge_output/nist-content.txt
    echo "✅ Text extraction completed:"
    ls -lh /tmp/pyforge_output/nist-content.txt
    head -n 10 /tmp/pyforge_output/nist-content.txt
else
    echo "📄 No PDF files available in sample datasets"
    echo "PDF extraction would work with: pyforge convert document.pdf output.txt"
fi
```

### Alternative: Create Sample Document for Demo

```bash
# Create a sample text document and convert to various formats
%sh
echo "📝 Creating sample document for format conversion demo..."
cat << 'EOF' > /tmp/sample_document.txt
# PyForge CLI Sample Document

## Executive Summary
This document demonstrates PyForge CLI's document processing capabilities.

## Key Features
- Multi-format support
- Intelligent text extraction
- Batch processing capabilities
- Databricks integration

## Data Processing Statistics
- Files processed: 10,000+
- Success rate: 99.7%
- Average processing time: 2.3 seconds

## Conclusion
PyForge CLI provides robust document conversion capabilities for enterprise data workflows.
EOF

echo "✅ Sample document created:"
ls -lh /tmp/sample_document.txt
echo ""
echo "📖 Document content:"
cat /tmp/sample_document.txt
```

---

## 8. Working with DBF Files (Geographic Data) using CLI

DBF files are commonly used for geographic data. PyForge CLI handles legacy DBF format seamlessly.

### DBF Analysis and Conversion using CLI

```bash
# Check available DBF files
%sh
echo "🗺️ Available DBF Files (Geographic Data):"
echo "=========================================="
ls -lh /tmp/pyforge_samples/dbf/small/

# Analyze DBF file structure using PyForge CLI
%sh
echo ""
echo "📋 DBF File Analysis:"
echo "===================="
pyforge info /tmp/pyforge_samples/dbf/small/tl_2024_us_county.dbf
```

### Convert DBF to Parquet using CLI
*Command: `pyforge convert file.dbf output.parquet`*

```bash
# Convert US Counties DBF to Parquet
%sh
echo "🔄 Converting US Counties DBF to Parquet..."
pyforge convert /tmp/pyforge_samples/dbf/small/tl_2024_us_county.dbf /tmp/pyforge_output/us-counties.parquet

# Convert another DBF file (Places)
%sh
echo "🔄 Converting US Places DBF to Parquet..." 
pyforge convert /tmp/pyforge_samples/dbf/small/tl_2024_01_place.dbf /tmp/pyforge_output/us-places.parquet

# List converted files
%sh
echo "✅ DBF conversions completed:"
ls -lh /tmp/pyforge_output/us-*.parquet
```

### Batch Convert All DBF Files

```bash
# Convert all DBF files at once using shell commands
%sh
echo "🔄 Batch converting all DBF files..."
for dbf_file in /tmp/pyforge_samples/dbf/small/*.dbf; do
    filename=$(basename "$dbf_file" .dbf)
    echo "Converting $filename..."
    pyforge convert "$dbf_file" "/tmp/pyforge_output/dbf_batch_${filename}.parquet"
done

echo "✅ Batch DBF conversion completed:"
ls -lh /tmp/pyforge_output/dbf_batch_*.parquet
```

### View the Geographic Data

```python
# Load and analyze the converted geographic data
counties_df = spark.read.parquet("file:/tmp/pyforge_output/us-counties.parquet")
print(f"🗺️ US Counties Data: {counties_df.count()} counties")
print(f"Columns: {counties_df.columns}")

# Show sample county data
print("\n📊 Sample US Counties Data:")
display(counties_df.select("NAME", "STATEFP", "COUNTYFP", "ALAND", "AWATER").limit(10))

# Show data types
counties_df.printSchema()
```

---

## 9. Batch Processing Multiple Files using CLI

PyForge CLI excels at batch processing with shell scripts and command-line automation.

### Multi-Format Batch Processing Script

```bash
# Create a comprehensive batch processing script
%sh
cat << 'EOF' > /tmp/pyforge_batch_all.sh
#!/bin/bash
echo "🔄 PyForge CLI Batch Processing - All Formats"
echo "=============================================="

mkdir -p /tmp/pyforge_output/batch_all/

# Function to convert files
convert_files() {
    format=$1
    echo ""
    echo "📊 Processing $format files..."
    for file in /tmp/pyforge_samples/$format/small/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            filename_no_ext="${filename%.*}"
            echo "  Converting $filename..."
            pyforge convert "$file" "/tmp/pyforge_output/batch_all/${format}_${filename_no_ext}.parquet"
        fi
    done
}

# Process all supported formats
convert_files "csv"
convert_files "excel"
convert_files "access"
convert_files "dbf"

echo ""
echo "✅ Batch processing completed! Results:"
ls -la /tmp/pyforge_output/batch_all/
echo ""
echo "📊 File count by format:"
for format in csv excel access dbf; do
    count=$(ls /tmp/pyforge_output/batch_all/${format}_* 2>/dev/null | wc -l)
    echo "  $format: $count files converted"
done
EOF

chmod +x /tmp/pyforge_batch_all.sh

# Run the batch processing script
%sh
/tmp/pyforge_batch_all.sh
```

### Advanced Batch Processing with Error Handling

```bash
# Create an advanced batch script with logging and error handling
%sh
cat << 'EOF' > /tmp/pyforge_batch_advanced.sh
#!/bin/bash
LOG_FILE="/tmp/pyforge_batch.log"
echo "🔄 Advanced PyForge CLI Batch Processing" | tee $LOG_FILE
echo "Starting batch processing at $(date)" | tee -a $LOG_FILE
echo "=======================================" | tee -a $LOG_FILE

mkdir -p /tmp/pyforge_output/batch_advanced/
success_count=0
error_count=0

# Function to process a file with error handling
process_file() {
    input_file=$1
    output_file=$2
    
    echo "Processing $(basename $input_file)..." | tee -a $LOG_FILE
    
    if pyforge convert "$input_file" "$output_file" 2>>$LOG_FILE; then
        echo "  ✅ Success: $(basename $input_file)" | tee -a $LOG_FILE
        ((success_count++))
    else
        echo "  ❌ Failed: $(basename $input_file)" | tee -a $LOG_FILE
        ((error_count++))
    fi
}

# Process all sample files
for sample_dir in /tmp/pyforge_samples/*/small/; do
    format=$(basename $(dirname $sample_dir))
    echo "" | tee -a $LOG_FILE
    echo "📁 Processing $format files:" | tee -a $LOG_FILE
    
    for file in "$sample_dir"*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            filename_no_ext="${filename%.*}"
            output_file="/tmp/pyforge_output/batch_advanced/${format}_${filename_no_ext}.parquet"
            process_file "$file" "$output_file"
        fi
    done
done

echo "" | tee -a $LOG_FILE
echo "📊 Batch Processing Summary:" | tee -a $LOG_FILE
echo "  Successful: $success_count files" | tee -a $LOG_FILE
echo "  Failed: $error_count files" | tee -a $LOG_FILE
echo "  Completed at $(date)" | tee -a $LOG_FILE

echo "📋 Log file created: $LOG_FILE"
EOF

chmod +x /tmp/pyforge_batch_advanced.sh

# Run advanced batch processing
%sh
/tmp/pyforge_batch_advanced.sh

# Show the log file
%sh
echo "📋 Batch Processing Log:"
echo "======================="
cat /tmp/pyforge_batch.log
```

### Directory-to-Directory Batch Conversion

```bash
# Demonstrate directory-level batch conversion
%sh
echo "🔄 Directory-to-Directory Batch Conversion:"
echo "==========================================="

# Convert entire CSV directory
echo "Converting all CSV files..."
pyforge convert /tmp/pyforge_samples/csv/small/ /tmp/pyforge_output/csv_batch/ --output-format parquet

# Convert entire DBF directory  
echo "Converting all DBF files..."
pyforge convert /tmp/pyforge_samples/dbf/small/ /tmp/pyforge_output/dbf_batch/ --output-format parquet

# Show results
echo "✅ Directory batch conversions completed:"
echo ""
echo "CSV batch results:"
ls -la /tmp/pyforge_output/csv_batch/
echo ""
echo "DBF batch results:" 
ls -la /tmp/pyforge_output/dbf_batch/
```

### View Batch Processing Results

```python
# Analyze all batch processing results
import os
import glob

print("📊 Comprehensive Batch Processing Analysis:")
print("=" * 50)

# Count files by format in all batch directories
batch_dirs = [
    "/tmp/pyforge_output/batch_all/",
    "/tmp/pyforge_output/batch_advanced/", 
    "/tmp/pyforge_output/csv_batch/",
    "/tmp/pyforge_output/dbf_batch/"
]

total_files = 0
for batch_dir in batch_dirs:
    if os.path.exists(batch_dir):
        parquet_files = glob.glob(f"{batch_dir}*.parquet")
        print(f"\n📁 {batch_dir}:")
        print(f"   Files: {len(parquet_files)}")
        total_files += len(parquet_files)
        
        # Show file sizes
        for file in parquet_files[:3]:  # Show first 3 files
            filename = os.path.basename(file)
            size = os.path.getsize(file)
            print(f"   • {filename}: {size:,} bytes")

print(f"\n🎯 Total converted files across all batches: {total_files}")

# Load and preview one batch result
if os.path.exists("/tmp/pyforge_output/batch_all/"):
    sample_files = glob.glob("/tmp/pyforge_output/batch_all/*.parquet")
    if sample_files:
        print(f"\n📊 Sample from batch processing:")
        df = spark.read.parquet(f"file:{sample_files[0]}")
        print(f"File: {os.path.basename(sample_files[0])}")
        print(f"Rows: {df.count()}, Columns: {len(df.columns)}")
        display(df.limit(3))
```

---

## 10. File Validation and CLI Help using Shell Commands

PyForge CLI provides comprehensive validation and help features accessible through shell commands.

### CLI Help System

```bash
# Get comprehensive PyForge CLI help
%sh
echo "📋 PyForge CLI Help System:"
echo "=========================="
pyforge --help

# Get help for specific commands
%sh
echo ""
echo "🔄 Convert Command Help:"
echo "======================="
pyforge convert --help
```

```bash
# Get help for other commands
%sh
echo "📦 Install Command Help:"
echo "======================="
pyforge install --help

%sh
echo ""
echo "ℹ️ Info Command Help:"
echo "===================="
pyforge info --help

%sh
echo ""
echo "🎯 Formats Command Help:"
echo "======================="
pyforge formats --help
```

### File Validation using CLI

```bash
# Validate various file types using PyForge CLI
%sh
echo "🔍 File Validation using PyForge CLI:"
echo "====================================="

# Validate CSV file
echo ""
echo "📊 Validating CSV file:"
pyforge validate /tmp/pyforge_samples/csv/small/titanic-dataset.csv

# Validate Excel file
echo ""
echo "📊 Validating Excel file:"
pyforge validate /tmp/pyforge_samples/excel/small/financial-sample.xlsx

# Validate Access database
echo ""
echo "🗄️ Validating Access database:"
pyforge validate /tmp/pyforge_samples/access/small/Northwind_2007_VBNet.accdb

# Validate DBF file
echo ""
echo "🗺️ Validating DBF file:"
pyforge validate /tmp/pyforge_samples/dbf/small/tl_2024_us_county.dbf
```

### Test Invalid File Validation

```bash
# Test validation with invalid files
%sh
echo "❌ Testing validation with invalid files:"
echo "========================================"

# Create an invalid file for testing
echo "Invalid content" > /tmp/invalid.xyz

# Test validation (should fail)
echo ""
echo "Testing invalid file validation:"
pyforge validate /tmp/invalid.xyz || echo "✅ Validation correctly failed for invalid file"

# Test non-existent file
echo ""
echo "Testing non-existent file validation:"
pyforge validate /tmp/nonexistent.csv || echo "✅ Validation correctly failed for non-existent file"
```

### Batch Validation

```bash
# Validate all sample files in batch
%sh
echo "🔍 Batch File Validation:"
echo "========================"

validation_log="/tmp/validation_results.txt"
echo "Validation Results - $(date)" > $validation_log

# Function to validate files in a directory
validate_directory() {
    format=$1
    echo ""
    echo "📁 Validating $format files:" | tee -a $validation_log
    
    for file in /tmp/pyforge_samples/$format/small/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            echo -n "  $filename: " | tee -a $validation_log
            if pyforge validate "$file" >/dev/null 2>&1; then
                echo "✅ Valid" | tee -a $validation_log
            else
                echo "❌ Invalid" | tee -a $validation_log
            fi
        fi
    done
}

# Validate all formats
validate_directory "csv"
validate_directory "excel"
validate_directory "access"
validate_directory "dbf"

echo ""
echo "📋 Validation log saved to: $validation_log"
cat $validation_log
```

---

## 11. Performance Monitoring and System Management

Best practices for using PyForge CLI in Databricks environments with shell commands.

### System Monitoring with Shell Commands

```bash
# Monitor system resources during PyForge operations
%sh
echo "💻 System Resource Monitoring:"
echo "============================="

# Check disk usage
echo "💾 Disk Usage:"
df -h | grep -E "(Filesystem|/tmp|/)"

# Check available memory
echo ""
echo "🧠 Memory Usage:"
free -h

# Monitor PyForge output directory sizes
echo ""
echo "📊 PyForge Output Directory Sizes:"
if [ -d "/tmp/pyforge_output" ]; then
    du -sh /tmp/pyforge_output/*/
    echo ""
    echo "Total PyForge output size:"
    du -sh /tmp/pyforge_output/
else
    echo "No PyForge output directory found"
fi
```

### File System Operations with DBFS Integration

```bash
# Copy sample datasets to DBFS for persistence (using file system magic)
%fs mkdirs /databricks-datasets/pyforge-samples/

%fs cp -r file:/tmp/pyforge_samples/ /databricks-datasets/pyforge-samples/

# Verify DBFS copy completed
%fs ls /databricks-datasets/pyforge-samples/

# Copy converted outputs to DBFS
%fs mkdirs /databricks-datasets/pyforge-outputs/

%fs cp -r file:/tmp/pyforge_output/ /databricks-datasets/pyforge-outputs/

# List persistent files in DBFS
%fs ls /databricks-datasets/pyforge-outputs/
```

### Performance Benchmarking with CLI

```bash
# Create a performance benchmarking script
%sh
cat << 'EOF' > /tmp/pyforge_benchmark.sh
#!/bin/bash
echo "⚡ PyForge CLI Performance Benchmark"
echo "===================================="

BENCHMARK_LOG="/tmp/pyforge_benchmark.log"
echo "Performance Benchmark - $(date)" > $BENCHMARK_LOG

# Function to time conversions
benchmark_conversion() {
    input_file=$1
    output_file=$2
    format=$3
    
    echo ""
    echo "📊 Benchmarking $format conversion:" | tee -a $BENCHMARK_LOG
    echo "  Input: $(basename $input_file)" | tee -a $BENCHMARK_LOG
    
    start_time=$(date +%s.%N)
    
    if pyforge convert "$input_file" "$output_file" 2>/dev/null; then
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        
        # Get file sizes
        input_size=$(stat -f%z "$input_file" 2>/dev/null || stat -c%s "$input_file")
        output_size=$(du -b "$output_file" 2>/dev/null | cut -f1 || echo "0")
        
        echo "  ✅ Success: ${duration}s" | tee -a $BENCHMARK_LOG
        echo "  📁 Input size: $input_size bytes" | tee -a $BENCHMARK_LOG
        echo "  📁 Output size: $output_size bytes" | tee -a $BENCHMARK_LOG
        
        # Calculate compression ratio
        if [ "$output_size" -gt 0 ]; then
            ratio=$(echo "scale=2; $input_size / $output_size" | bc)
            echo "  📈 Compression ratio: ${ratio}x" | tee -a $BENCHMARK_LOG
        fi
    else
        echo "  ❌ Failed" | tee -a $BENCHMARK_LOG
    fi
}

# Benchmark different formats
mkdir -p /tmp/benchmark_output/

# CSV benchmark
if [ -f "/tmp/pyforge_samples/csv/small/titanic-dataset.csv" ]; then
    benchmark_conversion "/tmp/pyforge_samples/csv/small/titanic-dataset.csv" "/tmp/benchmark_output/titanic_bench.parquet" "CSV"
fi

# DBF benchmark
if [ -f "/tmp/pyforge_samples/dbf/small/tl_2024_us_county.dbf" ]; then
    benchmark_conversion "/tmp/pyforge_samples/dbf/small/tl_2024_us_county.dbf" "/tmp/benchmark_output/counties_bench.parquet" "DBF"
fi

# Access benchmark
if [ -f "/tmp/pyforge_samples/access/small/Northwind_2007_VBNet.accdb" ]; then
    benchmark_conversion "/tmp/pyforge_samples/access/small/Northwind_2007_VBNet.accdb" "/tmp/benchmark_output/northwind_bench/" "Access"
fi

echo "" | tee -a $BENCHMARK_LOG
echo "📋 Benchmark completed. Full log: $BENCHMARK_LOG" | tee -a $BENCHMARK_LOG
EOF

chmod +x /tmp/pyforge_benchmark.sh

# Run performance benchmark
%sh
/tmp/pyforge_benchmark.sh

# Show benchmark results
%sh
echo ""
echo "📊 Benchmark Results Summary:"
echo "============================"
cat /tmp/pyforge_benchmark.log
```

### Cleanup and Maintenance

```bash
# Create cleanup script for temporary files
%sh
cat << 'EOF' > /tmp/pyforge_cleanup.sh
#!/bin/bash
echo "🧹 PyForge CLI Cleanup Utility"
echo "=============================="

# Function to clean directory with confirmation
cleanup_directory() {
    dir=$1
    name=$2
    
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" | cut -f1)
        file_count=$(find "$dir" -type f | wc -l)
        echo ""
        echo "📁 $name: $size ($file_count files)"
        echo "   Directory: $dir"
        # Uncomment the next line to actually delete (disabled for safety)
        # rm -rf "$dir" && echo "   ✅ Cleaned"
        echo "   💾 Preserved (uncomment rm command to actually delete)"
    else
        echo ""
        echo "📁 $name: Not found"
    fi
}

echo "Analyzing temporary directories..."

cleanup_directory "/tmp/pyforge_samples" "Sample Datasets"
cleanup_directory "/tmp/pyforge_output" "Conversion Outputs"
cleanup_directory "/tmp/benchmark_output" "Benchmark Results"

echo ""
echo "🗂️ Log files:"
ls -lh /tmp/pyforge_*.log 2>/dev/null || echo "No log files found"

echo ""
echo "💡 To actually perform cleanup, edit the cleanup script and uncomment the rm commands."
EOF

chmod +x /tmp/pyforge_cleanup.sh

# Run cleanup analysis (safe - doesn't delete anything)
%sh
/tmp/pyforge_cleanup.sh
```

---

## 12. Final Summary and Comprehensive Overview

Complete summary of PyForge CLI capabilities demonstrated in this notebook.

### Conversion Summary Report

```bash
# Generate comprehensive summary report
%sh
echo "📊 PyForge CLI Comprehensive Summary Report"
echo "=========================================="
echo "Generated: $(date)"
echo ""

# Count total conversions by type
echo "🔄 Conversion Statistics:"
echo "========================"

count_files() {
    pattern=$1
    name=$2
    count=$(find /tmp/pyforge_output/ -name "$pattern" 2>/dev/null | wc -l)
    echo "  $name: $count files"
}

count_files "*.parquet" "Parquet conversions"
count_files "*titanic*" "Titanic dataset conversions"
count_files "*northwind*" "Northwind database extractions"
count_files "*counties*" "Geographic data conversions"

echo ""
echo "📁 Directory Analysis:"
echo "===================="
if [ -d "/tmp/pyforge_output" ]; then
    total_size=$(du -sh /tmp/pyforge_output/ | cut -f1)
    file_count=$(find /tmp/pyforge_output/ -type f | wc -l)
    echo "  Total output size: $total_size"
    echo "  Total files created: $file_count"
    echo ""
    echo "  Directory breakdown:"
    du -sh /tmp/pyforge_output/*/ 2>/dev/null | head -10
else
    echo "  No output directory found"
fi

echo ""
echo "🗄️ Multi-Table Database Extractions:"
echo "=================================="
if [ -d "/tmp/pyforge_output/northwind_all_tables" ]; then
    table_count=$(ls /tmp/pyforge_output/northwind_all_tables/*.parquet 2>/dev/null | wc -l)
    echo "  Northwind tables extracted: $table_count"
    echo "  Table files:"
    ls /tmp/pyforge_output/northwind_all_tables/*.parquet 2>/dev/null | head -5 | xargs -I {} basename {}
fi

if [ -d "/tmp/pyforge_output/sakila_tables" ]; then
    sakila_count=$(ls /tmp/pyforge_output/sakila_tables/*.parquet 2>/dev/null | wc -l)
    echo "  Sakila tables extracted: $sakila_count"
fi
```

### Performance and Capabilities Achieved

```bash
# Show key capabilities demonstrated
%sh
echo ""
echo "✅ PyForge CLI Capabilities Demonstrated:"
echo "========================================"
echo ""
echo "🎯 Format Support:"
echo "  • CSV → Parquet (Titanic dataset)"
echo "  • Excel → Parquet (Multi-sheet detection)"
echo "  • Access/MDB → Parquet (Multi-table auto-extraction)"
echo "  • DBF → Parquet (Geographic data)"
echo "  • PDF → Text (Document processing)"
echo ""
echo "🚀 Advanced Features:"
echo "  • Automatic multi-table detection in databases"
echo "  • Intelligent sheet detection in Excel files"
echo "  • Batch processing with shell scripts"
echo "  • Error handling and logging"
echo "  • Performance benchmarking"
echo "  • File validation and format detection"
echo ""
echo "🏢 Databricks Integration:"
echo "  • %sh magic commands for CLI operations"
echo "  • %fs commands for file system operations"
echo "  • DBFS integration for data persistence"
echo "  • Spark DataFrame integration for analysis"
echo ""
echo "📊 Real Sample Datasets Used:"
echo "  • 19 curated datasets across 7 formats"
echo "  • Business databases (Northwind, Sakila)"
echo "  • Machine learning datasets (Titanic, Wine Quality)"
echo "  • Geographic data (US Census TIGER)"
echo "  • Government documents (NIST frameworks)"
```

### Key Commands Reference

```bash
# Create quick reference card
%sh
echo ""
echo "📋 PyForge CLI Quick Reference Card:"
echo "=================================="
echo ""
echo "🛠️ Essential Commands:"
echo "  pyforge --help                     # Get help"
echo "  pyforge formats                    # List supported formats"
echo "  pyforge install sample-datasets .  # Install sample data"
echo ""
echo "🔄 Basic Conversions:"
echo "  pyforge convert file.csv output.parquet    # Single file"
echo "  pyforge convert folder/ output_folder/     # Directory batch"
echo ""
echo "📊 File Analysis:"
echo "  pyforge info file.xlsx            # File information"
echo "  pyforge validate file.accdb       # Format validation"
echo ""
echo "🗄️ Database Operations:"
echo "  pyforge convert db.accdb tables/           # Extract all tables"
echo "  pyforge convert db.accdb table.parquet --table \"TableName\"  # Specific table"
echo ""
echo "⚙️ Advanced Options:"
echo "  --combine-sheets                   # Combine Excel sheets"
echo "  --extract-all-tables              # Extract all database tables"
echo "  --output-format parquet           # Specify output format"
echo "  --table \"TableName\"              # Select specific table"
```

---

## Summary

You've successfully learned how to use **PyForge CLI** for comprehensive data format conversion in Databricks:

### ✅ **Key Achievements:**

🎯 **CLI-First Approach**: Exclusively used `%sh pyforge` commands for all operations  
📊 **Multi-Table Database Processing**: Demonstrated automatic detection and extraction of all tables from Access databases  
🗂️ **Real Sample Datasets**: Used actual production-quality datasets across 7 different formats  
🔄 **Intelligent Format Detection**: PyForge CLI automatically detects file types and database structures  
⚡ **Batch Processing**: Created shell scripts for automated multi-file conversions  
🏢 **Databricks Integration**: Proper use of %sh, %fs magic commands throughout  
🛡️ **Production Ready**: Includes error handling, logging, and performance monitoring  

### 🎯 **Special Focus - Multi-Table Database Capability:**

**This is PyForge CLI's standout feature!** When you run:
```bash
pyforge convert database.accdb output_folder/
```

PyForge CLI automatically:
- 🔍 **Detects** all tables in the database
- 📊 **Analyzes** table structures and relationships  
- 🔄 **Converts** each table to individual Parquet files
- 📁 **Organizes** output with clear naming conventions

No need to specify table names or know the database structure beforehand!

### 🚀 **What Makes This Different:**

Unlike Python API approaches, the CLI provides:
- **Zero configuration** - Just point it at a file/folder
- **Intelligent detection** - Automatically handles complex structures
- **Shell integration** - Perfect for Databricks notebook environments
- **Progress reporting** - Clear feedback on processing status
- **Error resilience** - Continues processing even if individual files fail

### 📈 **Production Use Cases:**

1. **Data Migration**: Migrate legacy Access databases to modern formats
2. **ETL Pipelines**: Batch convert incoming files of various formats
3. **Data Lake Ingestion**: Convert mixed-format datasets to Parquet for analytics
4. **Archive Processing**: Extract data from old database backups
5. **Format Standardization**: Normalize data formats across your organization

### 🎓 **How to Use This Notebook:**

1. **Import to Databricks**: Copy this notebook content into your Databricks workspace
2. **Install PyForge CLI**: Run the `%pip install pyforge-cli` cell
3. **Install Sample Datasets**: Execute `%sh pyforge install sample-datasets`
4. **Run Examples**: Execute cells sequentially to see live demonstrations
5. **Adapt for Your Data**: Modify the patterns for your specific data conversion needs

### 🔗 **Integration Ready:**

The patterns shown here integrate seamlessly with:
- **Unity Catalog Volumes** for governed data access
- **Delta Lake** for versioned data storage  
- **Spark DataFrames** for immediate analysis
- **MLflow** for machine learning pipelines
- **Databricks Workflows** for automated processing

**PyForge CLI transforms complex data conversion into simple shell commands!** 🚀