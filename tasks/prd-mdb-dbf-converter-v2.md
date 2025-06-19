# PRD: MDB/DBF to Parquet Converter Enhancement (Revised)

## Document Information
- **Document Type**: Product Requirements Document (PRD)
- **Project**: CortexPy CLI Enhancement - Database File Converter
- **Version**: 2.0
- **Date**: June 19, 2025
- **Author**: Development Team
- **Status**: Revised Draft
- **Changes**: Focused on MDB/DBF files for Phase 1, MDF files moved to Phase 2

## Executive Summary

This PRD outlines the phased enhancement of CortexPy CLI to support conversion of database file formats to Apache Parquet. **Phase 1** focuses on Microsoft Access (MDB) and dBase (DBF) files with simplified string-based data conversion. **Phase 2** will add SQL Server (MDF) support with full data type mapping.

## 1. Problem Statement

### Current Challenges
- **Limited Database Support**: Current tool only supports PDF to text conversion
- **Legacy Format Migration**: Many organizations have data trapped in MDB/DBF formats
- **Manual Processing**: Users manually extract and convert legacy database tables
- **Data Type Complexity**: Initial users need simple, consistent output format

### Business Impact
- **Accessibility**: Legacy data in MDB/DBF files is difficult to access with modern tools
- **Integration Barriers**: Cannot easily load MDB/DBF data into modern analytics platforms
- **Time Investment**: Manual conversion processes take hours per database
- **Data Quality**: Manual processes introduce errors and inconsistencies

## 2. Solution Overview

### Phased Approach

#### Phase 1: MDB/DBF Conversion (This PRD)
- Support for Microsoft Access (.mdb, .accdb) files
- Support for dBase (.dbf) files
- **Simplified data conversion**: All data types converted to strings
- Multi-table batch processing with progress tracking
- Excel reports with conversion summaries

#### Phase 2: MDF Support (Future PRD)
- SQL Server database file (.mdf) support
- Full data type mapping and preservation
- Advanced connection options
- Performance optimizations

### Key Design Decision: String-Based Conversion

For Phase 1, all data types will be converted to string format using consistent rules:
- **Simplified Implementation**: Faster development and testing
- **Data Integrity**: No data loss during conversion
- **User Flexibility**: Users can parse strings as needed in downstream tools
- **Consistent Output**: Predictable format across all source data types

## 3. Target Users

### Primary Users (Phase 1)
- **Data Analysts**: Converting legacy Access and DBF databases
- **Business Users**: Migrating departmental databases to modern formats
- **Data Engineers**: Quick extraction from legacy systems
- **Researchers**: Accessing historical data in old formats

### User Personas
1. **Sarah - Data Analyst**
   - Has 20+ Access databases from various departments
   - Needs quick conversion to analyze in modern BI tools
   - Values simplicity over complex type preservation

2. **Mike - Business User**
   - Inherited DBF files from legacy systems
   - Needs to extract data for reporting
   - Not concerned with original data types

## 4. Functional Requirements

### 4.1 File Format Support (Phase 1)

#### Input Formats
- **MDB Files**: Microsoft Access Database Files
  - .mdb (Access 97-2003 format)
  - .accdb (Access 2007+ format)
  - Password-protected database support
  - Multi-table databases

- **DBF Files**: dBase Database Files
  - .dbf (dBase III, IV, V formats)
  - FoxPro variants
  - Memo field support (.dbt, .fpt files)
  - Index awareness (ignore .idx, .cdx files)

#### Output Format
- **Parquet Files**: Apache Parquet format (.parquet)
  - All columns stored as STRING type
  - UTF-8 encoding for all text
  - Snappy compression by default
  - One Parquet file per table

### 4.2 Data Type Conversion Rules

All source data types will be converted to strings using these rules:

#### Text Types
- **VARCHAR, CHAR, TEXT, MEMO**: Direct string conversion
- **Encoding**: Convert to UTF-8, handle special characters
- **Trimming**: Preserve original spacing

#### Numeric Types
- **INTEGER, LONG, SMALLINT**: Convert to string as-is
- **DECIMAL, NUMERIC, FLOAT, DOUBLE**: 
  - Format with 5 decimal places: "123.45000"
  - Use period (.) as decimal separator
  - No thousand separators
  - Preserve sign for negative numbers

#### Date/Time Types
- **DATE**: ISO 8601 format "YYYY-MM-DD"
- **TIME**: ISO 8601 format "HH:MM:SS"
- **DATETIME/TIMESTAMP**: ISO 8601 format "YYYY-MM-DD HH:MM:SS"
- **Null dates**: Empty string ""
- **Invalid dates**: Original value as string with warning

#### Boolean Types
- **BOOLEAN, BIT**: Convert to "true" or "false" (lowercase)
- **Numeric booleans**: 1 → "true", 0 → "false"

#### Binary Types
- **BLOB, BINARY**: Base64 encoded string
- **OLE Objects**: Extract type info + "[Binary Data]" placeholder

#### Special Values
- **NULL**: Empty string ""
- **Empty**: Empty string ""
- **Errors**: Original value + error flag in report

### 4.3 Discovery and Analysis Phase

#### Stage 1: File Analysis
```
Analyzing the file...
✓ File format: Microsoft Access 2007 (.accdb)
✓ File size: 45.2 MB
✓ Password protected: No
✓ Estimated tables: Scanning...
```

#### Stage 2: Table Discovery
```
Listing all tables...
✓ Found 5 user tables (excluding system tables)
✓ Total estimated records: ~50,000
✓ Largest table: customers (15,234 records)
```

#### Stage 3: Summary Extraction
```
Extracting summary...
┌─────────────────┬─────────────┬─────────────┬─────────────┐
│ Table Name      │ Records     │ Columns     │ Est. Size   │
├─────────────────┼─────────────┼─────────────┼─────────────┤
│ customers       │ 15,234      │ 12          │ 3.2 MB      │
│ orders          │ 28,456      │ 8           │ 5.1 MB      │
│ products        │ 1,245       │ 15          │ 0.8 MB      │
│ inventory       │ 3,567       │ 6           │ 0.5 MB      │
│ suppliers       │ 234         │ 10          │ 0.1 MB      │
└─────────────────┴─────────────┴─────────────┴─────────────┘
```

### 4.4 Conversion Process

#### Stage 4: Pre-conversion Overview
```
Conversion Strategy:
✓ All data types → STRING format
✓ Dates → ISO 8601 format
✓ Numbers → Decimal with 5 precision
✓ Compression: Snappy
✓ Output directory: /data/output/
```

#### Stage 5: Table Conversion
```
Converting tables...

[1/5] customers ████████████░░░░ 75% (11,425/15,234 records)
      ├─ Reading data    ████████████░░ 85%
      ├─ Converting      ███████████░░░ 82%  
      └─ Writing parquet ██████░░░░░░░░ 45%
      Speed: 2,847 records/sec | ETA: 1m 20s

Recently completed:
✓ suppliers.parquet (234 records, 0.1 MB, 2.1s)

Data Conversion Examples:
- Date: 2024-03-15 → "2024-03-15"
- Number: 123.4 → "123.40000"
- Boolean: True → "true"
```

#### Stage 6: Report Generation
```
Generating Excel report...
✓ Creating summary sheet
✓ Adding sample data (10 rows per table)
✓ Including conversion statistics
✓ Report saved: conversion_report_20250619_143022.xlsx
```

### 4.5 CLI Command Structure

#### Basic Commands
```bash
# Convert MDB file
cortexpy convert database.mdb output_directory/

# Convert DBF file  
cortexpy convert data.dbf output_directory/

# Convert with options
cortexpy convert database.accdb output/ --compression gzip --sample-rows 20
```

#### Command Parameters (Phase 1)
- `--tables, -t`: Specific tables to convert (comma-separated)
- `--exclude-tables, -e`: Tables to exclude
- `--compression, -c`: Parquet compression (snappy, gzip, none)
- `--batch-size, -b`: Records per batch (default: 10000)
- `--decimal-precision, -d`: Decimal places for numbers (default: 5)
- `--date-format`: Date format (default: ISO 8601)
- `--include-report, -r`: Generate Excel report (default: true)
- `--sample-rows, -s`: Sample rows in report (default: 10)
- `--password, -p`: Database password (MDB only)
- `--encoding`: Source file encoding (default: auto-detect)

### 4.6 Progress Tracking

```
CortexPy Database Converter - MDB/DBF to Parquet

Input: sales_data.mdb (45.2 MB)
Output: /data/output/

Stage 1: Analyzing file... ✓ (2.3s)
Stage 2: Discovering tables... ✓ (1.8s)
Stage 3: Extracting summary... ✓ (3.2s)

Found 5 tables with 48,736 total records

Stage 4: Converting to Parquet (STRING format)...

Overall: ███████████░░░░░ 68% (3/5 tables)

Current: orders (28,456 records)
Progress: ████████░░░░░░░░ 45% (12,805/28,456)
Speed: 3,250 records/sec
Memory: 127 MB / 500 MB limit
ETA: 4m 48s

Completed:
✓ suppliers.parquet (234 records, 0.08 MB)
✓ products.parquet (1,245 records, 0.52 MB)
✓ inventory.parquet (3,567 records, 0.31 MB)

Stage 5: Generating report... ⟳
```

### 4.7 Excel Report Structure

#### Summary Sheet
```
Database Conversion Report
Generated: 2025-06-19 14:30:45

Source: sales_data.mdb
Type: Microsoft Access 2007
Size: 45.2 MB
Tables: 5

Conversion Settings:
- All data types converted to STRING
- Decimal precision: 5
- Date format: ISO 8601 (YYYY-MM-DD)
- Compression: Snappy

Results:
┌─────────────┬──────────┬─────────┬──────────┬────────────┐
│ Table       │ Records  │ Columns │ Parquet  │ Time       │
│             │          │         │ Size     │            │
├─────────────┼──────────┼─────────┼──────────┼────────────┤
│ customers   │ 15,234   │ 12      │ 2.8 MB   │ 4.2s       │
│ orders      │ 28,456   │ 8       │ 4.3 MB   │ 8.7s       │
│ products    │ 1,245    │ 15      │ 0.5 MB   │ 0.4s       │
│ inventory   │ 3,567    │ 6       │ 0.3 MB   │ 1.1s       │
│ suppliers   │ 234      │ 10      │ 0.1 MB   │ 0.1s       │
└─────────────┴──────────┴─────────┴──────────┴────────────┘

Total: 48,736 records | 8.0 MB | 14.5s
```

#### Sample Data Sheets
Each table gets a sheet showing:
- First 10 records (configurable)
- All columns converted to STRING
- Original data type information
- Conversion examples

## 5. Technical Requirements

### 5.1 Dependencies (Phase 1 Only)

```python
# MDB Support
pandas-access>=0.0.1     # Pure Python Access reader
pyodbc>=4.0.35          # Windows ODBC support
mdbtools                # Linux/macOS support (system package)

# DBF Support  
dbfread>=2.0.7          # Pure Python DBF reader
simpledbf>=0.2.6        # Alternative DBF library

# Parquet
pyarrow>=12.0.0         # Parquet writer
fastparquet>=0.8.3      # Alternative option

# Progress & Reporting
rich>=13.0.0            # Progress bars
openpyxl>=3.1.0        # Excel reports
tqdm>=4.65.0           # Fallback progress

# Data Processing
pandas>=2.0.0           # Data manipulation
python-dateutil>=2.8.2  # Date parsing
chardet>=5.0.0         # Encoding detection
```

### 5.2 Platform Support

#### Windows
- Native ODBC drivers for MDB
- Direct DBF file reading
- Full feature support

#### Linux/macOS  
- mdbtools for MDB access
- Pure Python DBF reading
- Some MDB limitations (no .accdb write)

#### Docker Option
- Consistent cross-platform environment
- Pre-installed mdbtools
- Simplified deployment

### 5.3 Performance Requirements

#### Phase 1 Targets
- **Small files** (<10 MB): <10 seconds
- **Medium files** (10-100 MB): <60 seconds  
- **Large files** (100-500 MB): <5 minutes
- **Memory usage**: <500 MB regardless of file size
- **Conversion speed**: >2,000 records/second

#### Simplified Processing
- String conversion eliminates type validation overhead
- Consistent formatting reduces processing complexity
- Batch processing for memory efficiency

## 6. User Experience

### 6.1 Simplified Workflow

1. **One Command**: `cortexpy convert database.mdb output/`
2. **Automatic Detection**: File type identified by extension
3. **Progress Visibility**: Real-time conversion tracking
4. **String Output**: All data in consistent string format
5. **Excel Report**: Summary and samples for validation

### 6.2 Error Handling

#### Common Scenarios
```
Error: Password required
→ Solution: Use --password option

Error: Table not found
→ Solution: List available tables with --list-tables

Error: Corrupted DBF file
→ Solution: Try --repair-dbf option

Warning: Date conversion failed
→ Action: Original value preserved, noted in report
```

### 6.3 Success Confirmation

```
✅ Conversion completed successfully!

Summary:
- Files created: 5
- Records converted: 48,736  
- Output size: 8.0 MB (17% of original)
- Time elapsed: 14.5 seconds
- Report: conversion_report_20250619_143022.xlsx

Output directory: /data/output/
├── customers.parquet
├── orders.parquet
├── products.parquet
├── inventory.parquet
├── suppliers.parquet
└── conversion_report_20250619_143022.xlsx
```

## 7. Success Metrics

### Phase 1 Metrics
- **Adoption**: 50+ users within first month
- **File Support**: 95% of MDB/DBF files convert successfully
- **Performance**: Meet speed targets for 90% of files
- **User Satisfaction**: <5 minutes average conversion time
- **Data Integrity**: 100% of records preserved as strings

### Quality Metrics
- **Conversion Accuracy**: All data readable in output
- **Report Usefulness**: Users validate data using samples
- **Error Rate**: <5% of conversions require intervention
- **Cross-platform**: Works on Windows, Linux, macOS

## 8. Implementation Timeline

### Phase 1: MDB/DBF Support (4 weeks)

#### Week 1: Core Infrastructure
- File detection for MDB/DBF
- Basic table discovery
- String conversion framework

#### Week 2: Conversion Engine  
- MDB reader implementation
- DBF reader implementation
- Parquet writer with string schema

#### Week 3: Progress & Reporting
- 6-stage progress system
- Excel report generation
- Sample data extraction

#### Week 4: Testing & Polish
- Cross-platform testing
- Performance optimization
- Documentation

### Phase 2: MDF Support (Future - 4 weeks)
- SQL Server connectivity
- Full data type mapping
- Advanced features

## 9. Risk Mitigation

### Technical Risks
1. **MDB Compatibility**: Some .accdb features unsupported on Linux
   - *Mitigation*: Clear platform limitations in docs
   
2. **DBF Variants**: Many DBF format variations exist
   - *Mitigation*: Support common formats, document limitations

3. **Large Files**: Memory constraints with huge tables
   - *Mitigation*: Streaming/batch processing

### User Risks
1. **String Conversion**: Users expect typed data
   - *Mitigation*: Clear documentation, Phase 2 roadmap

2. **Data Validation**: Can't validate string data
   - *Mitigation*: Excel samples for manual validation

## 10. Future Enhancements

### Phase 2 (Next Release)
- MDF file support
- Full data type preservation
- Type mapping configuration
- Performance optimizations

### Phase 3 (Future)
- Cloud storage integration
- Incremental conversion
- Data quality validation
- Custom transformations

## 11. Acceptance Criteria

### Must Have (Phase 1)
- [x] Convert MDB files to Parquet (all strings)
- [x] Convert DBF files to Parquet (all strings)
- [x] 6-stage progress tracking
- [x] Excel report with samples
- [x] Cross-platform support (with limitations)
- [x] Consistent string formatting rules

### Should Have  
- [x] Password-protected MDB support
- [x] Batch size configuration
- [x] Compression options
- [x] Custom sample size

### Could Have (Deferred to Phase 2)
- [ ] MDF file support
- [ ] Type preservation
- [ ] Custom type mappings
- [ ] Advanced validation

## Appendix

### A. String Conversion Examples

```
Source Type    | Source Value      | Converted String
---------------|-------------------|-----------------
INTEGER        | 42                | "42"
DECIMAL(10,2)  | 123.45            | "123.45000"
FLOAT          | 3.14159           | "3.14159"
DATE           | 2024-03-15        | "2024-03-15"
DATETIME       | 2024-03-15 14:30  | "2024-03-15 14:30:00"
BOOLEAN        | True              | "true"
VARCHAR(50)    | "Hello World"     | "Hello World"
NULL           | NULL              | ""
MEMO           | Long text...      | "Long text..."
BLOB           | [Binary Data]     | "QmluYXJ5RGF0YQ=="
```

### B. Command Examples

```bash
# Basic conversion
cortexpy convert customer_db.mdb /output/

# Convert specific tables
cortexpy convert sales.accdb /output/ --tables "orders,customers"

# DBF conversion with custom precision
cortexpy convert legacy.dbf /output/ --decimal-precision 2

# Password-protected Access database
cortexpy convert secure.mdb /output/ --password "mypass"

# Custom report settings
cortexpy convert data.mdb /output/ --sample-rows 25 --compression gzip
```

### C. Platform-Specific Notes

**Windows**: Full MDB/DBF support with native drivers
**Linux**: MDB via mdbtools, DBF via pure Python
**macOS**: Similar to Linux, install mdbtools via Homebrew

---

This revised PRD focuses on Phase 1 implementation with MDB/DBF files and simplified string conversion, making the initial release more achievable while providing immediate value to users.