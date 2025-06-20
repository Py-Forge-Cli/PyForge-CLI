# Quick Start Guide

Get started with PyForge CLI in just 5 minutes! This guide will walk you through your first file conversion.

## Step 1: Install PyForge CLI

If you haven't already installed PyForge CLI:

```bash
pip install pyforge-cli
```

Verify the installation:

```bash
pyforge --version
```

## Step 2: Get Sample Files

We'll start with some sample files. You can download these or use your own:

=== "PDF Sample"

    Create a simple text file and save it as `sample.txt`:
    ```
    This is a sample document.
    It has multiple lines.
    Perfect for testing PDF conversion.
    ```

=== "Excel Sample"

    You can use any Excel file you have, or create one with:
    - Sheet1: Some data with headers
    - Sheet2: More data
    
=== "Use Your Own Files"

    PyForge CLI works with:
    - PDF files (.pdf)
    - Excel files (.xlsx)
    - Access databases (.mdb, .accdb)
    - DBF files (.dbf)

## Step 3: Your First Conversion

Let's start with the most common operations:

### Convert PDF to Text

```bash
# Convert entire PDF to text
pyforge convert document.pdf

# Convert with specific pages
pyforge convert document.pdf --pages "1-5"

# Convert with metadata
pyforge convert document.pdf --metadata
```

**Example Output:**
```
Converting document.pdf...
✓ Extracted text from 5 pages
✓ Saved to document.txt
📊 Conversion completed in 1.2 seconds
```

### Convert Excel to Parquet

```bash
# Convert all sheets
pyforge convert spreadsheet.xlsx

# Convert specific sheets
pyforge convert spreadsheet.xlsx --sheets "Sheet1,Data"

# Interactive sheet selection
pyforge convert spreadsheet.xlsx --interactive
```

**Example Output:**
```
Converting spreadsheet.xlsx...
📋 Found 3 sheets: Sheet1, Sheet2, Summary
✓ Converted Sheet1 (1,250 rows)
✓ Converted Sheet2 (890 rows)
✓ Converted Summary (45 rows)
📊 Total: 2,185 rows converted
📁 Saved to spreadsheet_combined.parquet
```

### Convert Database Files

```bash
# Convert Access database
pyforge convert database.mdb

# Convert DBF file
pyforge convert data.dbf
```

## Step 4: Explore Options

### Get File Information

Before converting, check what's in your file:

```bash
# Show file metadata
pyforge info document.pdf

# Excel file details
pyforge info spreadsheet.xlsx

# Database file info
pyforge info database.mdb
```

**Example Output:**
```
📄 File: spreadsheet.xlsx
📊 Type: Excel Workbook
📏 Size: 2.4 MB
📋 Sheets: 3
┌─────────┬──────┬─────────┬────────────────┐
│ Sheet   │ Rows │ Columns │ Sample Columns │
├─────────┼──────┼─────────┼────────────────┤
│ Sheet1  │ 1250 │ 8       │ ID, Name, Date │
│ Sheet2  │ 890  │ 12      │ Product, Price │
│ Summary │ 45   │ 5       │ Total, Count   │
└─────────┴──────┴─────────┴────────────────┘
```

### List Supported Formats

```bash
pyforge formats
```

### Validate Files

Check if a file can be processed:

```bash
pyforge validate document.pdf
pyforge validate spreadsheet.xlsx
```

## Step 5: Common Options

Here are the most useful options for each converter:

### PDF Options

```bash
# Page ranges
pyforge convert doc.pdf --pages "1-10"     # Pages 1 to 10
pyforge convert doc.pdf --pages "5-"       # Page 5 to end
pyforge convert doc.pdf --pages "-10"      # First 10 pages

# Include metadata
pyforge convert doc.pdf --metadata

# Custom output
pyforge convert doc.pdf output.txt
```

### Excel Options

```bash
# Sheet selection
pyforge convert file.xlsx --sheets "Sheet1,Sheet3"

# Combine sheets with matching columns
pyforge convert file.xlsx --combine

# Keep sheets separate
pyforge convert file.xlsx --separate

# Compression
pyforge convert file.xlsx --compression gzip
```

### Database Options

```bash
# With encoding (for DBF files)
pyforge convert data.dbf --encoding cp1252

# Specific tables (for MDB files)
pyforge convert db.mdb --tables "customers,orders"

# Custom output directory
pyforge convert database.mdb output_folder/
```

## Step 6: Check Your Output

After conversion, you'll find your files in the same directory:

```bash
# List files
ls -la

# Check Parquet file (if you have pandas installed)
python -c "import pandas as pd; print(pd.read_parquet('output.parquet').head())"
```

## Common Workflows

### Batch Processing

Convert multiple files at once:

```bash
# Convert all PDFs in a directory
for file in *.pdf; do
    pyforge convert "$file"
done

# Convert all Excel files
for file in *.xlsx; do
    pyforge convert "$file" --combine
done
```

### With Progress and Verbose Output

```bash
# Verbose mode for detailed output
pyforge convert large_file.xlsx --verbose

# Force overwrite existing files
pyforge convert file.pdf --force
```

## What's Next?

Now that you've completed your first conversion:

1. **[Explore Converters](../converters/index.md)** - Learn about each format in detail
2. **[CLI Reference](../reference/cli-reference.md)** - Complete command documentation
3. **[Tutorials](../tutorials/index.md)** - Real-world examples and workflows
4. **[Troubleshooting](../tutorials/troubleshooting.md)** - Solutions to common issues

## Quick Reference Card

| Task | Command |
|------|---------|
| **Convert PDF** | `pyforge convert document.pdf` |
| **Convert Excel** | `pyforge convert spreadsheet.xlsx` |
| **Convert Database** | `pyforge convert database.mdb` |
| **Get File Info** | `pyforge info filename` |
| **Show Help** | `pyforge --help` |
| **List Formats** | `pyforge formats` |
| **Validate File** | `pyforge validate filename` |

## Need Help?

- 📖 **[Complete Documentation](../index.md)**
- 🔧 **[Troubleshooting Guide](../tutorials/troubleshooting.md)**
- 💬 **[GitHub Discussions](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions)**
- 🐛 **[Report Issues](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)**

Congratulations! You've successfully completed your first file conversion with PyForge CLI. 🎉