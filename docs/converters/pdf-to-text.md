# PDF to Text Converter

Convert PDF documents to plain text with advanced extraction options, page range selection, and metadata preservation.

## Quick Start

```bash
# Basic conversion
pyforge convert document.pdf

# With page range
pyforge convert document.pdf --pages "1-10"

# With metadata
pyforge convert document.pdf --metadata

# Custom output file
pyforge convert document.pdf extracted_text.txt
```

## Overview

The PDF to Text converter uses PyMuPDF (fitz) to extract text from PDF documents with high accuracy and performance. It supports:

- **Text Extraction**: High-quality text extraction preserving formatting
- **Page Selection**: Convert specific pages or page ranges
- **Metadata Extraction**: Include document metadata in output
- **Layout Preservation**: Maintain basic text layout and structure
- **Error Recovery**: Handle corrupted or complex PDF files

## Command Syntax

```bash
pyforge convert <pdf_file> [output_file] [options]
```

### Basic Examples

```bash
# Convert entire PDF
pyforge convert report.pdf

# Specify output file
pyforge convert report.pdf extracted_report.txt

# Convert with progress tracking
pyforge convert large_document.pdf --verbose
```

## Page Selection

Control which pages to convert using the `--pages` option:

### Page Range Syntax

| Syntax | Description | Example |
|--------|-------------|---------|
| `"1-10"` | Pages 1 through 10 | `--pages "1-10"` |
| `"5-"` | Page 5 to end of document | `--pages "5-"` |
| `"-10"` | First 10 pages | `--pages "-10"` |
| `"1,3,5"` | Specific pages only | `--pages "1,3,5"` |
| `"1-5,10-15"` | Multiple ranges | `--pages "1-5,10-15"` |

### Page Selection Examples

```bash
# First 5 pages
pyforge convert manual.pdf --pages "-5"

# Pages 10 to 20
pyforge convert manual.pdf --pages "10-20"

# From page 25 to end
pyforge convert manual.pdf --pages "25-"

# Specific pages
pyforge convert manual.pdf --pages "1,5,10,25"

# Multiple ranges
pyforge convert manual.pdf --pages "1-3,10-12,20-25"

# Complex selection
pyforge convert manual.pdf summary.txt --pages "1,3-7,15,20-"
```

## Metadata Options

Include document metadata in the output using `--metadata`:

```bash
# Include metadata
pyforge convert document.pdf --metadata

# Combine with page selection
pyforge convert document.pdf --pages "1-10" --metadata
```

### Metadata Information

When `--metadata` is enabled, the output includes:

- Document title
- Author information
- Creation and modification dates
- Page count
- File size
- PDF version
- Security settings

**Example Output with Metadata:**
```
========================================
PDF METADATA
========================================
Title: Annual Report 2023
Author: Finance Department
Creator: Microsoft Word
Producer: Adobe PDF Library
Creation Date: 2023-12-01 14:30:25
Modification Date: 2023-12-15 09:45:12
Pages: 45
File Size: 2.4 MB
PDF Version: 1.7
Security: Not Encrypted
========================================

[Document text content follows...]
```

## Advanced Options

### Output Control

```bash
# Force overwrite existing files
pyforge convert document.pdf --force

# Specify custom output location
pyforge convert document.pdf /path/to/output.txt

# Verbose output for debugging
pyforge convert document.pdf --verbose
```

### Error Handling

```bash
# Attempt to process corrupted PDFs
pyforge convert damaged.pdf --force

# Skip problematic pages
pyforge convert complex.pdf --skip-errors
```

## Text Extraction Quality

### What Works Well

- **Standard Text**: Regular paragraphs and headings
- **Tables**: Simple table structures (converted to aligned text)
- **Lists**: Bulleted and numbered lists
- **Headers/Footers**: Page headers and footers
- **Multi-column**: Basic multi-column layouts

### Limitations

- **Complex Layouts**: Heavily formatted documents may lose structure
- **Images**: Text within images is not extracted (OCR not included)
- **Forms**: Interactive form fields may not be captured
- **Annotations**: Comments and annotations are not included
- **Embedded Objects**: Charts, diagrams converted to placeholder text

### Quality Tips

!!! tip "Best Results"
    For the best text extraction:
    
    - Use PDFs created from text documents (not scanned images)
    - Prefer PDFs with selectable text
    - Avoid heavily graphical or artistic layouts
    - Consider the source application (Word docs convert better than InDesign layouts)

## File Information

Get detailed information about a PDF before conversion:

```bash
# Basic file info
pyforge info document.pdf

# Detailed information
pyforge info document.pdf --verbose
```

**Example Output:**
```
📄 File: annual_report.pdf
📊 Type: PDF Document
📏 Size: 2.4 MB
📋 Pages: 45
🔒 Encrypted: No
📝 Text Extractable: Yes
🎨 Has Images: Yes
📑 Has Forms: No

┌─────────────┬─────────────────────────┐
│ Property    │ Value                   │
├─────────────┼─────────────────────────┤
│ Title       │ Annual Report 2023      │
│ Author      │ Finance Department      │
│ Creator     │ Microsoft Word          │
│ Producer    │ Adobe PDF Library       │
│ Created     │ 2023-12-01 14:30:25    │
│ Modified    │ 2023-12-15 09:45:12    │
│ PDF Version │ 1.7                     │
└─────────────┴─────────────────────────┘
```

## Validation

Validate PDF files before conversion:

```bash
# Check if file can be processed
pyforge validate document.pdf

# Detailed validation
pyforge validate document.pdf --verbose
```

## Performance

### Processing Speed

| Document Type | Pages | Typical Speed |
|---------------|-------|---------------|
| **Text-heavy** | 1-50 | 10-50 pages/sec |
| **Mixed content** | 1-50 | 5-20 pages/sec |
| **Image-heavy** | 1-50 | 2-10 pages/sec |
| **Large files** | 100+ | 5-15 pages/sec |

### Memory Usage

- **Small PDFs** (< 10 MB): 50-100 MB RAM
- **Medium PDFs** (10-100 MB): 100-500 MB RAM
- **Large PDFs** (> 100 MB): 500 MB - 2 GB RAM

### Optimization Tips

!!! tip "Large File Processing"
    For large PDF files:
    
    ```bash
    # Process in smaller chunks
    pyforge convert large.pdf --pages "1-50"
    pyforge convert large.pdf --pages "51-100"
    
    # Use verbose mode to monitor progress
    pyforge convert large.pdf --verbose
    
    # Ensure sufficient disk space (3x file size recommended)
    ```

## Common Use Cases

### Legal Document Processing

```bash
# Extract contract text
pyforge convert contract.pdf --pages "1-10" --metadata

# Process multiple legal documents
for file in contracts/*.pdf; do
    pyforge convert "$file" "processed/$(basename "$file" .pdf).txt"
done
```

### Research Paper Processing

```bash
# Extract paper content (skip references)
pyforge convert research_paper.pdf --pages "1-25" 

# Include metadata for citation
pyforge convert research_paper.pdf --metadata
```

### Report Processing

```bash
# Extract executive summary
pyforge convert annual_report.pdf summary.txt --pages "3-8"

# Full report with metadata
pyforge convert annual_report.pdf --metadata --verbose
```

## Troubleshooting

### Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Encrypted PDF** | "Password required" error | Decrypt PDF first or provide password option |
| **Corrupted File** | "Invalid PDF" error | Try `--force` option |
| **No Text Output** | Empty or minimal text | PDF may be image-based (needs OCR) |
| **Garbled Text** | Strange characters | Check PDF encoding/font issues |
| **Memory Error** | Process crashes | Reduce page range or close other applications |

### Troubleshooting Commands

```bash
# Check file validity
pyforge validate problematic.pdf

# Try force processing
pyforge convert problematic.pdf --force

# Get detailed file information
pyforge info problematic.pdf --verbose

# Process small page range first
pyforge convert problematic.pdf test.txt --pages "1-5"
```

## Output Format

### Text Structure

The extracted text maintains:

- **Paragraph breaks**: Preserved from original
- **Line breaks**: Maintained where appropriate
- **Spacing**: Basic spacing preserved
- **Headers/Footers**: Included in extraction
- **Page breaks**: Marked with page numbers (if `--metadata` used)

### Example Output Structure

```
Page 1
======

ANNUAL REPORT 2023
Finance Department

Executive Summary

This report provides a comprehensive overview of our 
financial performance for the fiscal year 2023...

Key Highlights:
• Revenue increased by 15%
• Profit margins improved
• Successful market expansion

Page 2
======

Financial Overview

The following table shows our quarterly performance:

Q1    $2.5M    15%
Q2    $2.8M    18%
Q3    $3.1M    20%
Q4    $3.4M    22%

...
```

## Integration Examples

### Bash Scripting

```bash
#!/bin/bash
# Process all PDFs in a directory

for pdf in *.pdf; do
    echo "Processing $pdf..."
    pyforge convert "$pdf" "${pdf%.pdf}.txt" --metadata
    echo "✓ Completed $pdf"
done
```

### Python Integration

```python
import subprocess
import os

def extract_pdf_text(pdf_path, output_path=None, pages=None):
    """Extract text from PDF using PyForge CLI"""
    cmd = ["pyforge", "convert", pdf_path]
    
    if output_path:
        cmd.append(output_path)
    
    if pages:
        cmd.extend(["--pages", pages])
    
    cmd.append("--metadata")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# Usage
success = extract_pdf_text("report.pdf", "extracted.txt", "1-10")
```

## Next Steps

- **[Excel Converter](excel-to-parquet.md)** - Learn about Excel to Parquet conversion
- **[CLI Reference](../reference/cli-reference.md)** - Complete command documentation
- **[Tutorials](../tutorials/index.md)** - Real-world PDF processing workflows
- **[Troubleshooting](../tutorials/troubleshooting.md)** - Solve common PDF issues