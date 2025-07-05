# PyForge Databricks Notebook API Reference

**Document Version**: 2.0  
**Created**: 2025-01-03  
**Purpose**: Simplified reference for PyForge install-datasets and convert commands in Databricks notebooks  

---

## 📚 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Install Sample Datasets](#install-sample-datasets)
3. [Convert Command](#convert-command)
4. [Environment Detection](#environment-detection)
5. [File Type Support](#file-type-support)
6. [Help Commands](#help-commands)
7. [Examples](#examples)

---

## 1. Installation & Setup

### Quick Install

```python
# Cell 1: Install PyForge with Databricks extension
%pip install pyforge-cli[databricks] --quiet

# Cell 2: Restart Python kernel
dbutils.library.restartPython()

# Cell 3: Import PyForge
from pyforge_cli.extensions.databricks import PyForgeDatabricks, forge
```

---

## 2. Install Sample Datasets

### Basic Command

```bash
# Install all sample datasets
%sh pyforge install sample-datasets /path/to/destination

# Install specific formats only
%sh pyforge install sample-datasets /tmp/samples --formats csv,excel,xml

# Install specific size categories
%sh pyforge install sample-datasets /tmp/samples --sizes small,medium,large
```

### Python API

```python
# Install sample datasets using Python API
result = forge.install_sample_datasets(
    destination="/tmp/samples",
    formats=["csv", "excel", "xml"],  # Optional: specific formats
    sizes=["small", "medium"]         # Optional: specific sizes
)

print(f"Installed {result['total_files']} sample files")
```

---

## 3. Convert Command

### Basic Conversion

```bash
# Auto-detect output format from extension
%sh pyforge convert input.csv output.parquet

# Convert with explicit format
%sh pyforge convert data.xlsx --output-format parquet

# Convert to Unity Catalog Volume
%sh pyforge convert /tmp/data.csv /Volumes/catalog/schema/volume/data.parquet
```

### Python API

```python
# Basic conversion
result = forge.convert("input.csv", "output.parquet")

# Auto-generate output path
result = forge.convert("data.xlsx")  # Creates data.parquet

# Convert with options
result = forge.convert(
    "large_file.xml",
    output_format="parquet",
    compression="snappy"
)
```

---

## 4. Environment Detection

PyForge automatically detects the Databricks environment and optimizes conversions accordingly.

### Detection Logic for CSV, XML, and Excel

```python
# Check current environment
env = forge.get_environment_info()

if env['is_serverless']:
    print("✅ Serverless environment detected - using PySpark")
else:
    print("📦 Classic environment - using Pandas/PyArrow")
```

### Conversion Strategy by File Type

| File Type | Serverless Environment | Classic Environment |
|-----------|------------------------|---------------------|
| **CSV**   | PySpark DataFrame API  | Pandas + PyArrow    |
| **Excel** | PySpark with pandas_api| Pandas + openpyxl   |
| **XML**   | PySpark XML reader     | xml.etree + Pandas  |
| **PDF**   | Core PDF parser        | Core PDF parser     |
| **MDB/ACCDB** | Core mdbtools      | Core mdbtools       |
| **DBF**   | Core dbfread          | Core dbfread        |

---

## 5. File Type Support

### Supported Input Formats
PyForge supports the following input file formats:
- **CSV** (.csv, .tsv, .txt) - Comma/Tab separated values
- **Excel** (.xlsx) - Microsoft Excel workbooks (multi-sheet support)
- **XML** (.xml, .xml.gz, .xml.bz2) - Extensible Markup Language
- **PDF** (.pdf) - Portable Document Format (text extraction)
- **Access** (.mdb, .accdb) - Microsoft Access databases
- **DBF** (.dbf) - dBase database files

**Note**: JSON files are not currently supported as input format.

### CSV Files

#### Serverless Environment (PySpark)
```python
# Automatic PySpark usage in serverless
result = forge.convert("large.csv", "output.parquet")
# Uses: spark.read.csv() internally
```

#### Classic Environment (Pandas)
```python
# Automatic Pandas usage in classic compute
result = forge.convert("data.csv", "output.parquet")
# Uses: pd.read_csv() + to_parquet() internally
```

### Excel Files

#### Multi-Sheet Detection and Combination
```python
# Automatic multi-sheet detection
info = forge.get_info("multi_sheet_workbook.xlsx")
print(f"Sheets found: {info['sheets']}")  # ['Sales', 'Inventory', 'Orders']

# Combine sheets with matching schemas
result = forge.convert(
    "multi_sheet_workbook.xlsx",
    excel_options={
        'combine_sheets': True,  # Auto-detect and combine similar sheets
        'sheet_matching_strategy': 'column_signature',  # Match by columns
        'include_sheet_name': True  # Add sheet_name column
    }
)
```

#### Serverless Environment (PySpark with pandas API)
```python
# Automatic PySpark pandas API in serverless
result = forge.convert("spreadsheet.xlsx", "output.parquet")
# Uses: spark.pandas.read_excel() internally

# Multi-sheet processing with PySpark
result = forge.convert(
    "workbook.xlsx",
    excel_options={'combine_sheets': True}
)
# Automatically uses PySpark pandas API for sheet combination
```

#### Classic Environment (Pandas)
```python
# Automatic Pandas usage in classic compute
result = forge.convert("workbook.xlsx", "output.parquet")
# Uses: pd.read_excel() internally

# Multi-sheet processing with Pandas
result = forge.convert(
    "workbook.xlsx",
    excel_options={'combine_sheets': True}
)
# Uses Pandas concat() for sheet combination
```

### XML Files

#### Serverless Environment (PySpark XML)
```python
# Automatic PySpark XML reader in serverless
result = forge.convert("data.xml", "output.parquet")
# Uses: spark.read.format("xml") internally
```

#### Classic Environment (xml.etree + Pandas)
```python
# Automatic XML parsing with Pandas in classic
result = forge.convert("document.xml", "output.parquet")
# Uses: xml.etree.ElementTree + pd.DataFrame internally
```

---

## 6. Help Commands

### General Help

```bash
# Main help
%sh pyforge --help

# Convert command help
%sh pyforge convert --help

# Install datasets help
%sh pyforge install sample-datasets --help
```

### File Type Specific Options

#### CSV Options
```bash
# CSV conversion options
%sh pyforge convert data.csv output.parquet --help

# Available CSV options:
# --delimiter CHAR     Field delimiter (default: ,)
# --encoding TEXT      File encoding (default: utf-8)
# --header            First row contains headers
# --skip-rows INT     Number of rows to skip
# --compression TEXT   Input compression (auto-detected)
```

#### Excel Options
```bash
# Excel conversion options
%sh pyforge convert data.xlsx output.parquet --help

# Available Excel options:
# --sheets TEXT        Comma-separated sheet names or "all"
# --combine-sheets     Combine all sheets into one
# --skip-rows INT      Rows to skip per sheet
# --password TEXT      Password for protected files
```

#### XML Options
```bash
# XML conversion options
%sh pyforge convert data.xml output.parquet --help

# Available XML options:
# --flatten-nested     Flatten nested structures
# --array-handling     How to handle arrays: expand|concatenate|json_string
# --preserve-attributes Keep XML attributes
# --namespace-handling  How to handle namespaces: strip|preserve|prefix
# --root-tag TEXT      Specific root element to process
```

#### Parquet Options (Output)
```bash
# Parquet output options
%sh pyforge convert input.csv output.parquet --help

# Available Parquet options:
# --compression TEXT   Compression: snappy|gzip|lz4|zstd|none
# --row-group-size INT Rows per row group
# --use-dictionary     Enable dictionary encoding
```

---

## 7. Examples

### Example 1: Install and Convert Sample Datasets

```python
# Install sample datasets
forge.install_sample_datasets("/tmp/samples", formats=["csv", "excel", "xml"])

# Convert all CSV files
import glob
csv_files = glob.glob("/tmp/samples/**/*.csv", recursive=True)

for file in csv_files:
    result = forge.convert(file)
    print(f"✅ Converted {file} -> {result['output_path']}")
```

### Example 2: Environment-Aware Batch Processing

```python
# Check environment first
env = forge.get_environment_info()
print(f"Environment: {env['compute_type']}")
print(f"Engine: {'PySpark' if env['is_serverless'] else 'Pandas/PyArrow'}")

# Batch convert with appropriate engine
files = [
    "/Volumes/main/default/bronze/data1.csv",
    "/Volumes/main/default/bronze/data2.xlsx",
    "/Volumes/main/default/bronze/data3.xml"
]

results = []
for file in files:
    result = forge.convert(file, output_format="parquet")
    results.append({
        'file': file,
        'success': result['success'],
        'engine': result['processing_engine'],
        'duration': result['duration']
    })

# Display results
import pandas as pd
df = pd.DataFrame(results)
display(df)
```

### Example 3: Convert with Format-Specific Options

```python
# CSV with custom delimiter
result = forge.convert(
    "semicolon_data.csv",
    csv_options={'delimiter': ';', 'encoding': 'latin-1'}
)

# Excel with specific sheets
result = forge.convert(
    "multi_sheet.xlsx",
    excel_options={'sheets': ['Sales', 'Inventory'], 'combine_sheets': True}
)

# XML with flattening
result = forge.convert(
    "nested_structure.xml",
    xml_options={'flatten_nested': True, 'array_handling': 'expand'}
)
```

### Example 4: Quick Validation and Conversion

```python
# Validate before converting
files_to_process = ["data1.csv", "data2.xlsx", "data3.xml"]

for file in files_to_process:
    # Validate first
    validation = forge.validate(file)
    
    if validation['valid']:
        # Convert if valid
        result = forge.convert(file)
        print(f"✅ {file}: Converted successfully")
    else:
        print(f"❌ {file}: Validation failed - {validation['issues']}")
```

### Example 5: Command Line Quick Reference

```bash
# Install datasets
%sh pyforge install sample-datasets /tmp/data

# Convert CSV (auto-detects serverless/classic)
%sh pyforge convert /tmp/data/sales.csv /tmp/output/sales.parquet

# Convert Excel with options
%sh pyforge convert report.xlsx report.parquet --sheets "Q1,Q2" --combine-sheets

# Convert XML with flattening
%sh pyforge convert nested.xml flat.parquet --flatten-nested --array-handling expand

# Get help for any file type
%sh pyforge convert --help
```

---

## 📝 Quick Reference Card

### Essential Commands

```python
# Import
from pyforge_cli.extensions.databricks import forge

# Install sample datasets
forge.install_sample_datasets("/path/to/destination")

# Basic conversion (auto-detects environment)
result = forge.convert("input.csv")  # Creates input.parquet

# Convert with output path
result = forge.convert("input.xlsx", "output.parquet")

# Check environment
env = forge.get_environment_info()
is_serverless = env['is_serverless']

# Validate file
validation = forge.validate("data.xml")
if validation['valid']:
    result = forge.convert("data.xml")
```

### Environment Detection Summary

| Condition | CSV/Excel/XML Engine | Other Formats |
|-----------|---------------------|---------------|
| Serverless Compute | PySpark | PySpark or Core |
| Classic Compute | Pandas + PyArrow | Core libraries |
| Force Core | `force_core=True` | Core libraries |

---

This simplified reference focuses on the install-datasets and convert commands, with clear environment detection logic for CSV, Excel, and XML files. The help command examples show all available options for each file type.