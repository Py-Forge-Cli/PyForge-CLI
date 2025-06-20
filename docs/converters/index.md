# Format Converters

PyForge CLI supports conversion between multiple data formats. Each converter is optimized for its specific format with intelligent processing and error handling.

## Available Converters

<div class="grid cards" markdown>

-   :material-file-pdf-box: **PDF to Text**

    ---

    Extract text from PDF documents with page range support

    [:octicons-arrow-right-24: Learn More](pdf-to-text.md)

-   :material-microsoft-excel: **Excel to Parquet**

    ---

    Convert Excel workbooks to high-performance Parquet format

    [:octicons-arrow-right-24: Learn More](excel-to-parquet.md)

-   :material-database: **Database Files**

    ---

    Convert Access databases (MDB/ACCDB) to Parquet

    [:octicons-arrow-right-24: Learn More](database-files.md)

-   :material-file-table: **DBF Files**

    ---

    Convert legacy DBF database files to Parquet

    [:octicons-arrow-right-24: Learn More](dbf-files.md)

</div>

## Format Compatibility Matrix

| Input Format | File Extensions | Output Format | Status | Platform Support |
|-------------|-----------------|---------------|--------|-------------------|
| **PDF** | `.pdf` | Text (`.txt`) | ✅ Stable | Windows, macOS, Linux |
| **Excel** | `.xlsx` | Parquet (`.parquet`) | ✅ Stable | Windows, macOS, Linux |
| **Access** | `.mdb`, `.accdb` | Parquet (`.parquet`) | ✅ Stable | Windows, macOS*, Linux* |
| **DBF** | `.dbf` | Parquet (`.parquet`) | ✅ Stable | Windows, macOS, Linux |
| **CSV** | `.csv` | Parquet (`.parquet`) | 🚧 Coming Soon | Windows, macOS, Linux |

*Requires mdbtools installation

## Conversion Features

### Universal Features

All converters support these common features:

- **Progress Tracking**: Real-time progress bars and status updates
- **Error Handling**: Graceful error recovery and detailed error messages
- **Metadata Preservation**: Maintain important file metadata where possible
- **Batch Processing**: Convert multiple files with consistent options
- **Verbose Output**: Detailed logging for troubleshooting
- **Force Overwrite**: Option to overwrite existing output files

### Format-Specific Features

Each converter includes specialized features:

#### PDF Converter
- Page range selection (`--pages "1-10"`)
- Metadata extraction (`--metadata`)
- Text formatting preservation
- Font and layout information

#### Excel Converter
- Multi-sheet processing
- Sheet selection (`--sheets "Sheet1,Sheet2"`)
- Column matching for combining sheets
- Compression options (`--compression gzip`)
- Interactive mode for sheet selection

#### Database Converters
- Automatic table discovery
- Cross-platform compatibility
- Password-protected database support
- Custom output directory structure
- Table filtering options

#### DBF Converter
- Automatic encoding detection
- Support for various DBF formats
- Field type preservation
- Corrupted file recovery

## Quick Start Examples

### Basic Conversions

```bash
# Convert PDF to text
pyforge convert document.pdf

# Convert Excel to Parquet
pyforge convert spreadsheet.xlsx

# Convert Access database
pyforge convert database.mdb

# Convert DBF file
pyforge convert legacy.dbf
```

### Advanced Options

```bash
# PDF with page range and metadata
pyforge convert report.pdf --pages "1-20" --metadata

# Excel with specific sheets and compression
pyforge convert data.xlsx --sheets "Data,Summary" --compression gzip

# Database with custom output
pyforge convert database.mdb output_directory/

# DBF with specific encoding
pyforge convert legacy.dbf --encoding cp1252
```

## Performance Considerations

### File Size Guidelines

| Format | Small | Medium | Large | Very Large |
|--------|-------|--------|-------|------------|
| **PDF** | < 10 MB | 10-100 MB | 100 MB - 1 GB | > 1 GB |
| **Excel** | < 50 MB | 50-200 MB | 200 MB - 1 GB | > 1 GB |
| **Access** | < 100 MB | 100 MB - 1 GB | 1-10 GB | > 10 GB |
| **DBF** | < 50 MB | 50-500 MB | 500 MB - 2 GB | > 2 GB |

### Optimization Tips

!!! tip "Memory Management"
    For large files, PyForge CLI automatically optimizes memory usage:
    
    - Streaming processing for large datasets
    - Chunked reading to prevent memory overflow
    - Progress reporting for long-running operations

!!! tip "Performance"
    To maximize performance:
    
    - Use SSD storage for input and output files
    - Ensure sufficient free disk space (2x file size recommended)
    - Close other applications when processing very large files
    - Consider using compression for output files

## Error Handling

PyForge CLI provides comprehensive error handling:

### Common Issues and Solutions

| Error Type | Description | Solution |
|------------|-------------|----------|
| **File Not Found** | Input file doesn't exist | Check file path and permissions |
| **Permission Denied** | Cannot write output file | Check directory permissions |
| **Corrupted File** | Input file is damaged | Try with `--force` option or repair file |
| **Encoding Issues** | Character encoding problems | Specify encoding with `--encoding` |
| **Memory Error** | File too large for available memory | Close other applications or use streaming mode |

### Troubleshooting Commands

```bash
# Validate file before conversion
pyforge validate input_file.xlsx

# Get detailed file information
pyforge info input_file.pdf

# Run with verbose output
pyforge convert file.mdb --verbose

# Test with force option
pyforge convert file.dbf --force
```

## Output Formats

### Text Output (PDF Converter)
- **Format**: Plain text (.txt)
- **Encoding**: UTF-8
- **Features**: Preserves line breaks, basic formatting

### Parquet Output (All Other Converters)
- **Format**: Apache Parquet (.parquet)
- **Compression**: SNAPPY (default), GZIP, LZ4, ZSTD
- **Schema**: Automatically inferred from source data
- **Features**: Column-oriented, highly compressed, fast read/write

## Next Steps

Choose a converter to learn more about:

- **[PDF to Text](pdf-to-text.md)** - Document processing and text extraction
- **[Excel to Parquet](excel-to-parquet.md)** - Spreadsheet data conversion
- **[Database Files](database-files.md)** - Access database migration
- **[DBF Files](dbf-files.md)** - Legacy database modernization

Or explore other sections:

- **[CLI Reference](../reference/cli-reference.md)** - Complete command documentation
- **[Tutorials](../tutorials/index.md)** - Real-world examples and workflows
- **[API Documentation](../api/index.md)** - Using PyForge as a Python library