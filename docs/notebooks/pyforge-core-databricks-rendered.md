# PyForge Core: Data Format Conversion in Databricks

This notebook demonstrates how to use PyForge Core for data format conversion in Databricks environments. PyForge Core provides a powerful CLI-like interface for converting between various data formats including CSV, JSON, Excel, PDF, XML, and more.

## Introduction

PyForge Core is a comprehensive data format conversion tool that brings the power of the PyForge CLI directly into your Databricks notebooks. This guide will walk you through:

- Installing PyForge Core in Databricks
- Setting up sample datasets for testing
- Converting between various file formats
- Using CLI-equivalent commands in notebooks
- Optimizing conversions for different file types

---

## 1. Installation and Setup

First, let's install PyForge Core and set up our environment.

```python
# Install PyForge Core
%pip install pyforge-core --quiet

# After installation, restart the Python kernel
dbutils.library.restartPython()
```

```python
# Import required libraries
import os
import sys
from pathlib import Path
from datetime import datetime
import json
import pandas as pd

# Import PyForge Core
from pyforge_core import PyForgeCore
from pyforge_core.plugins import PluginLoader, ConverterRegistry

print("✅ PyForge Core imported successfully!")
print(f"📍 Python version: {sys.version}")
print(f"🏢 Databricks Runtime: {spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion')}")
```

---

## 2. Installing Sample Datasets

PyForge Core includes a sample dataset installer that provides curated test files for each supported format.

```python
# Initialize PyForge Core
forge = PyForgeCore()

# Display available commands (similar to CLI help)
print("📋 PyForge Core Commands:")
print("========================")
print("1. convert    - Convert files between formats")
print("2. info       - Display file information")
print("3. formats    - List supported formats")
print("4. validate   - Validate file compatibility")
print("5. install    - Install components (sample-datasets)")
```

```python
# Install sample datasets
# This is equivalent to: pyforge install sample-datasets
print("📦 Installing sample datasets...")
print("This will download curated test files for each supported format.")
print("")

# Note: In a real implementation, this would download from GitHub releases
# For demonstration, we'll create sample files
sample_data_path = "/tmp/pyforge_samples"
dbutils.fs.mkdirs(f"file:{sample_data_path}")

# Create sample CSV file
csv_content = """id,name,department,salary,hire_date
1,Alice Johnson,Engineering,95000,2020-01-15
2,Bob Smith,Marketing,75000,2019-06-20
3,Charlie Brown,Sales,80000,2021-03-10
4,Diana Davis,Engineering,105000,2018-11-05
5,Eve Wilson,HR,70000,2022-02-28"""

with open(f"{sample_data_path}/employees.csv", "w") as f:
    f.write(csv_content)

# Create sample JSON file
json_content = {
    "company": "TechCorp",
    "employees": [
        {"id": 1, "name": "Alice", "skills": ["Python", "Spark", "SQL"]},
        {"id": 2, "name": "Bob", "skills": ["Java", "Scala", "AWS"]}
    ],
    "metadata": {
        "created": "2024-01-01",
        "version": "1.0"
    }
}

with open(f"{sample_data_path}/company_data.json", "w") as f:
    json.dump(json_content, f, indent=2)

# Create sample XML file
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<products>
    <product id="1">
        <name>Laptop Pro</name>
        <category>Electronics</category>
        <price currency="USD">1299.99</price>
        <specs>
            <cpu>Intel i7</cpu>
            <ram>16GB</ram>
            <storage>512GB SSD</storage>
        </specs>
    </product>
    <product id="2">
        <name>Wireless Mouse</name>
        <category>Accessories</category>
        <price currency="USD">29.99</price>
    </product>
</products>"""

with open(f"{sample_data_path}/products.xml", "w") as f:
    f.write(xml_content)

print("✅ Sample datasets installed successfully!")
print(f"📁 Location: {sample_data_path}")
print("\nSample files created:")
print("  - employees.csv")
print("  - company_data.json")
print("  - products.xml")
```

---

## 3. Basic File Conversion

Let's start with basic file conversions, demonstrating PyForge Core's API that mirrors CLI commands.

### Example 1: Convert CSV to Parquet
*CLI equivalent: `pyforge convert employees.csv employees.parquet`*

```python
input_file = f"{sample_data_path}/employees.csv"
output_file = f"{sample_data_path}/employees.parquet"

print("🔄 Converting CSV to Parquet...")
print(f"   Input: {input_file}")
print(f"   Output: {output_file}")

# Perform conversion
result = forge.convert(
    input_path=input_file,
    output_path=output_file
)

print("\n✅ Conversion completed!")
print(f"   Duration: {result.get('duration', 'N/A')}s")
print(f"   Rows processed: {result.get('row_count', 'N/A')}")

# Read and display the converted data
df = spark.read.parquet(f"file:{output_file}")
display(df)
```

### Example 2: File Information
*CLI equivalent: `pyforge info employees.csv`*

```python
print("📋 File Information:")
print("=" * 50)

file_info = forge.get_info(input_file)

for key, value in file_info.items():
    print(f"{key:20}: {value}")
```

### Example 3: List Supported Formats
*CLI equivalent: `pyforge formats`*

```python
print("📊 Supported Formats:")
print("=" * 50)

formats = forge.list_formats()
for fmt in formats:
    print(f"{fmt['input']:15} → {fmt['output']:15} ({fmt['converter']})")
```

---

## 4. Advanced Conversions with Options

PyForge Core supports format-specific options for fine-tuned control over conversions.

### JSON to Parquet with Flattening
*CLI equivalent: `pyforge convert company_data.json company_data.parquet --flatten`*

```python
json_input = f"{sample_data_path}/company_data.json"
json_output = f"{sample_data_path}/company_data.parquet"

print("🔄 Converting JSON to Parquet with flattening...")

result = forge.convert(
    input_path=json_input,
    output_path=json_output,
    json_options={
        'flatten_nested': True,
        'normalize_arrays': True
    }
)

print("✅ JSON conversion completed!")

# Display the flattened structure
df = spark.read.parquet(f"file:{json_output}")
print("\n📊 Flattened JSON structure:")
df.printSchema()
display(df)
```

### XML to Parquet with Hierarchical Flattening
*CLI equivalent: `pyforge convert products.xml products.parquet --flatten-nested`*

```python
xml_input = f"{sample_data_path}/products.xml"
xml_output = f"{sample_data_path}/products.parquet"

print("🔄 Converting XML to Parquet with structure analysis...")

result = forge.convert(
    input_path=xml_input,
    output_path=xml_output,
    xml_options={
        'flatten_nested': True,
        'array_detection': True,
        'preserve_attributes': True,
        'root_tag': 'product'
    }
)

print("✅ XML conversion completed!")
print("   Hierarchical structure flattened")
print("   Attributes preserved as columns")

# Display the result
df = spark.read.parquet(f"file:{xml_output}")
display(df)
```

---

## 5. Working with Excel Files

PyForge Core includes advanced Excel processing with multi-sheet support and intelligent column matching.

```python
# Create a sample Excel file with multiple sheets
import openpyxl
from openpyxl import Workbook

wb = Workbook()

# Sheet 1: Q1 Sales
ws1 = wb.active
ws1.title = "Q1_Sales"
ws1.append(["Product", "Revenue", "Units", "Quarter"])
ws1.append(["Product A", 50000, 100, "Q1"])
ws1.append(["Product B", 75000, 150, "Q1"])
ws1.append(["Product C", 60000, 120, "Q1"])

# Sheet 2: Q2 Sales (same structure)
ws2 = wb.create_sheet("Q2_Sales")
ws2.append(["Product", "Revenue", "Units", "Quarter"])
ws2.append(["Product A", 55000, 110, "Q2"])
ws2.append(["Product B", 80000, 160, "Q2"])
ws2.append(["Product C", 65000, 130, "Q2"])

# Sheet 3: Product Info (different structure)
ws3 = wb.create_sheet("Product_Info")
ws3.append(["Product", "Category", "Launch_Date"])
ws3.append(["Product A", "Electronics", "2023-01-15"])
ws3.append(["Product B", "Software", "2023-03-20"])
ws3.append(["Product C", "Hardware", "2023-02-10"])

excel_file = f"{sample_data_path}/sales_report.xlsx"
wb.save(excel_file)

print("✅ Sample Excel file created with 3 sheets")
```

### Convert Excel with Multi-Sheet Handling
*CLI equivalent: `pyforge convert sales_report.xlsx sales_report.parquet --combine-sheets`*

```python
excel_output = f"{sample_data_path}/sales_report.parquet"

print("🔄 Converting Excel file with multiple sheets...")
print("\nSheet analysis:")

# First, get information about the Excel file
excel_info = forge.get_info(excel_file)
print(f"  Total sheets: {excel_info.get('sheet_count', 'N/A')}")
print(f"  Sheets: {excel_info.get('sheet_names', [])}")

# Convert with sheet combination
result = forge.convert(
    input_path=excel_file,
    output_path=excel_output,
    excel_options={
        'combine_sheets': True,
        'sheet_matching_strategy': 'column_signature',
        'include_sheet_name': True
    }
)

print("\n✅ Excel conversion completed!")
print(f"   Sheets with matching columns were combined")
print(f"   Sheet name included as column for tracking")

# Display the result
df = spark.read.parquet(f"file:{excel_output}")
print(f"\n📊 Combined data shape: {df.count()} rows, {len(df.columns)} columns")
display(df)
```

---

## 6. Batch Processing Multiple Files

Process multiple files efficiently using PyForge Core's batch capabilities.

```python
# Create additional sample files for batch processing
batch_files = []

# Create monthly sales CSVs
for month in ["jan", "feb", "mar"]:
    csv_content = f"""date,product,sales,region
2024-{month}-01,Product A,1000,North
2024-{month}-02,Product B,1500,South
2024-{month}-03,Product C,1200,East
2024-{month}-04,Product A,1100,West"""
    
    file_path = f"{sample_data_path}/sales_{month}.csv"
    with open(file_path, "w") as f:
        f.write(csv_content)
    batch_files.append(file_path)

print(f"✅ Created {len(batch_files)} files for batch processing")
```

```python
# Batch convert all CSV files to Parquet
print("🔄 Batch Processing Multiple Files:")
print("=" * 50)

batch_results = []
start_time = datetime.now()

for input_file in batch_files:
    output_file = input_file.replace('.csv', '.parquet')
    
    try:
        print(f"\n📄 Processing: {Path(input_file).name}")
        
        # Convert file
        result = forge.convert(
            input_path=input_file,
            output_path=output_file
        )
        
        batch_results.append({
            'file': Path(input_file).name,
            'status': 'success',
            'duration': result.get('duration', 0),
            'rows': result.get('row_count', 0)
        })
        
        print(f"   ✅ Success ({result.get('duration', 0):.2f}s)")
        
    except Exception as e:
        batch_results.append({
            'file': Path(input_file).name,
            'status': 'failed',
            'error': str(e)
        })
        print(f"   ❌ Failed: {str(e)}")

# Summary
total_time = (datetime.now() - start_time).total_seconds()
success_count = sum(1 for r in batch_results if r['status'] == 'success')

print(f"\n📊 Batch Processing Summary:")
print(f"   Total files: {len(batch_files)}")
print(f"   Successful: {success_count}")
print(f"   Failed: {len(batch_files) - success_count}")
print(f"   Total time: {total_time:.2f}s")

# Combine all converted files
if success_count > 0:
    print("\n🔗 Combining all converted files...")
    
    parquet_files = [f.replace('.csv', '.parquet') for f in batch_files]
    combined_df = spark.read.parquet(*[f"file:{f}" for f in parquet_files])
    
    combined_output = f"{sample_data_path}/sales_combined.parquet"
    combined_df.write.mode("overwrite").parquet(f"file:{combined_output}")
    
    print(f"✅ Combined dataset created: {combined_output}")
    print(f"   Total rows: {combined_df.count()}")
    
    display(combined_df.orderBy("date"))
```

---

## 7. File Validation

Use PyForge Core's validation feature to check file compatibility before conversion.

```python
# Validate files before conversion
# CLI equivalent: pyforge validate <file>

test_files = [
    f"{sample_data_path}/employees.csv",
    f"{sample_data_path}/products.xml",
    f"{sample_data_path}/invalid.xyz",  # Invalid format
    f"{sample_data_path}/missing.csv"   # Non-existent file
]

print("🔍 File Validation Results:")
print("=" * 50)

for file_path in test_files:
    print(f"\n📄 {Path(file_path).name}")
    
    validation_result = forge.validate(file_path)
    
    if validation_result['valid']:
        print("   ✅ Valid for conversion")
        print(f"   Format: {validation_result.get('format', 'Unknown')}")
        print(f"   Converter: {validation_result.get('converter', 'None')}")
    else:
        print("   ❌ Invalid for conversion")
        print(f"   Reason: {validation_result.get('reason', 'Unknown error')}")
```

---

## 8. Working with PDF Files

PyForge Core can extract text from PDF files, useful for processing reports and documents.

```python
# Create a sample PDF content (using markdown for demonstration)
# In production, you would have actual PDF files

pdf_demo_text = """
# Sample PDF Content

This demonstrates PyForge Core's PDF text extraction capabilities.

## Features:
- Extract text from all pages
- Specify page ranges
- Include metadata extraction
- Preserve formatting (optional)

## Use Cases:
- Converting reports to structured data
- Extracting tables from PDFs
- Building searchable document databases
"""

print("📄 PDF Processing Demonstration")
print("=" * 50)
print("\nPDF text extraction features:")
print("- Page range selection: --pages 1-10")
print("- Metadata extraction: --include-metadata")
print("- Format preservation: --preserve-formatting")
print("\nExample conversions:")
print("  pyforge convert report.pdf report.txt")
print("  pyforge convert report.pdf report.txt --pages 1-5")
```

---

## 9. Performance Optimization Tips

Best practices for using PyForge Core in Databricks environments.

```python
print("⚡ Performance Optimization Tips:")
print("=" * 50)

tips = [
    {
        "category": "Memory Management",
        "recommendations": [
            "Process large files in chunks when possible",
            "Use Parquet format for better compression",
            "Clear intermediate results with del statements",
            "Monitor driver memory for Excel/PDF processing"
        ]
    },
    {
        "category": "Format Selection",
        "recommendations": [
            "Prefer Parquet for analytical workloads",
            "Use CSV for simple data exchange",
            "Consider JSON for nested/semi-structured data",
            "Compress large XML files before processing"
        ]
    },
    {
        "category": "Batch Processing",
        "recommendations": [
            "Group similar files for batch conversion",
            "Use parallel processing for independent files",
            "Combine outputs after conversion for efficiency",
            "Monitor cluster utilization during batch jobs"
        ]
    },
    {
        "category": "Databricks Specific",
        "recommendations": [
            "Store converted files in DBFS for faster access",
            "Use Delta format for versioned datasets",
            "Leverage cluster auto-scaling for large jobs",
            "Cache frequently accessed conversions"
        ]
    }
]

for tip_group in tips:
    print(f"\n{tip_group['category']}:")
    for rec in tip_group['recommendations']:
        print(f"  • {rec}")
```

---

## 10. PyForge Core API Reference

Quick reference for common PyForge Core operations in Python.

```python
print("📚 PyForge Core API Reference:")
print("=" * 50)

api_reference = """
# Initialize PyForge Core
forge = PyForgeCore()

# Basic conversion
result = forge.convert(
    input_path="input.csv",
    output_path="output.parquet"
)

# Conversion with options
result = forge.convert(
    input_path="data.json",
    output_path="data.parquet",
    json_options={
        'flatten_nested': True,
        'normalize_arrays': True
    }
)

# Get file information
info = forge.get_info("file.xlsx")

# List supported formats
formats = forge.list_formats()

# Validate file
validation = forge.validate("file.pdf")

# Excel-specific options
excel_options = {
    'combine_sheets': True,
    'sheet_matching_strategy': 'column_signature',
    'include_sheet_name': True,
    'sheets': ['Sheet1', 'Sheet2']  # Specific sheets
}

# XML-specific options
xml_options = {
    'flatten_nested': True,
    'array_detection': True,
    'preserve_attributes': True,
    'root_tag': 'record'
}

# PDF-specific options
pdf_options = {
    'page_range': '1-10',
    'include_metadata': True,
    'preserve_formatting': False
}
"""

print(api_reference)
```

---

## Summary

You've learned how to use PyForge Core for data format conversion in Databricks:

✅ **Installation**: Simple pip install with automatic plugin loading  
✅ **Sample Datasets**: Built-in test files for all supported formats  
✅ **Basic Conversion**: Simple API that mirrors CLI commands  
✅ **Advanced Options**: Format-specific configurations for optimal results  
✅ **Batch Processing**: Efficient multi-file conversions  
✅ **Excel Support**: Intelligent multi-sheet handling  
✅ **Validation**: Pre-conversion compatibility checks  

### Next Steps:
1. Try converting your own files
2. Explore format-specific options
3. Build automated conversion pipelines
4. Integrate with Delta Lake for versioning
5. Check out pyforge-databricks for Volume integration

```python
# Clean up sample files (optional)
cleanup = False  # Set to True to remove sample files

if cleanup:
    print("🧹 Cleaning up sample files...")
    dbutils.fs.rm(f"file:{sample_data_path}", recurse=True)
    print("✅ Cleanup completed")
else:
    print(f"💾 Sample files preserved at: {sample_data_path}")
    print("   Set cleanup=True to remove them")
```

## How to Use This Notebook

1. **Import to Databricks**: Copy the notebook content and import it into your Databricks workspace
2. **Run All Cells**: Execute the notebook from top to bottom for a complete walkthrough
3. **Experiment**: Modify the examples to work with your own data files
4. **Production Use**: Adapt the code patterns for your data pipeline needs