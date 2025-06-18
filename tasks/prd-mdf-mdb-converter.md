# PRD: MDF/MDB to Parquet Converter Enhancement

## Document Information
- **Document Type**: Product Requirements Document (PRD)
- **Project**: CortexPy CLI Enhancement - Database File Converter
- **Version**: 1.0
- **Date**: June 18, 2025
- **Author**: Development Team
- **Status**: Draft

## Executive Summary

This PRD outlines the enhancement of CortexPy CLI to support conversion of Microsoft Database File formats (MDF/MDB) to Apache Parquet format. The enhancement will provide comprehensive database analysis, multi-table extraction, real-time progress tracking, and detailed reporting capabilities.

## 1. Problem Statement

### Current Challenges
- **Limited Database Support**: Current tool only supports PDF to text conversion
- **Manual Database Processing**: Users manually extract tables from database files
- **No Bulk Conversion**: No efficient way to convert all tables at once
- **Lack of Progress Visibility**: Users have no insight into conversion progress
- **Missing Analysis Reports**: No summary or sample data reports generated

### Business Impact
- **Time Consuming**: Manual table-by-table extraction takes hours
- **Error Prone**: Manual processes lead to missed tables or corrupted data
- **No Audit Trail**: Lack of conversion summaries and validation reports
- **Poor User Experience**: No progress feedback during long conversions

## 2. Solution Overview

### Core Capability
Extend CortexPy CLI with intelligent MDF/MDB database conversion that automatically:
- Analyzes database file structure
- Discovers all tables and their schemas
- Converts tables to Parquet format with progress tracking
- Generates comprehensive conversion reports

### Key Differentiators
- **Intelligent Discovery**: Automatic table detection and analysis
- **Real-time Progress**: Multi-stage progress tracking with detailed insights
- **Batch Processing**: Convert all tables in a single command
- **Rich Reporting**: Excel reports with summaries and sample data
- **Error Resilience**: Continue processing even if individual tables fail

## 3. Target Users

### Primary Users
- **Data Engineers**: Converting legacy database files to modern formats
- **Data Analysts**: Migrating Access databases to analytical platforms
- **Database Administrators**: Archiving and modernizing database systems
- **Business Users**: Converting departmental Access databases

### User Personas
1. **Sarah - Data Engineer**
   - Needs to migrate 50+ Access databases to data lake
   - Requires automated conversion with progress tracking
   - Needs validation reports for data quality assurance

2. **Mike - Business Analyst**
   - Works with legacy Access databases from various departments
   - Needs quick conversion to analyze data in modern tools
   - Requires sample data preview to verify conversion accuracy

## 4. Functional Requirements

### 4.1 File Format Support

#### Input Formats
- **MDF Files**: SQL Server Database Files (.mdf)
  - Support for SQL Server 2008 and later
  - Handle both data and schema information
  - Support for various encodings and collations

- **MDB Files**: Microsoft Access Database Files (.mdb, .accdb)
  - Support for Access 97-2003 format (.mdb)
  - Support for Access 2007+ format (.accdb)
  - Handle password-protected databases

#### Output Format
- **Parquet Files**: Apache Parquet format (.parquet)
  - Columnar storage optimization
  - Schema preservation with proper data types
  - Compression support (Snappy, GZIP, LZ4)

### 4.2 Discovery and Analysis Phase

#### File Analysis
```
Stage 1: Analyzing the file
- Validate file format and integrity
- Check file permissions and accessibility
- Detect database version and encoding
- Estimate processing time based on file size
```

#### Table Discovery
```
Stage 2: Listing all tables
- Enumerate all user tables (exclude system tables)
- Detect table relationships and dependencies
- Identify primary keys and indexes
- Catalog view definitions and stored procedures
```

#### Metadata Collection
```
Stage 3: Found [X] tables
- Display table count and names
- Show estimated row counts per table
- Identify data types and schema information
- Calculate total estimated processing time
```

### 4.3 Data Extraction Process

#### Summary Generation
```
Stage 4: Extracting summary
- Generate table-by-table statistics
- Identify potential data quality issues
- Create conversion strategy based on table sizes
- Prepare optimization settings
```

#### Table Preview
```
Stage 5: Table overview
┌─────────────────┬─────────────────┬─────────────────┐
│ Table Name      │ Record Count    │ Estimated Size  │
├─────────────────┼─────────────────┼─────────────────┤
│ customers       │ 10,234          │ 2.1 MB          │
│ orders          │ 45,678          │ 8.7 MB          │
│ products        │ 1,567           │ 0.9 MB          │
│ order_details   │ 123,456         │ 15.2 MB         │
└─────────────────┴─────────────────┴─────────────────┘
Total: 4 tables, 180,935 records, ~27 MB
```

#### Table Extraction
```
Stage 6: Converting tables
For each table:
- Extract table: [customers] ████████░░ 80% (8,187/10,234 rows)
- Apply data type mappings
- Handle null values and special characters
- Write to destination/customers.parquet
- Validate row count and schema
```

### 4.4 CLI Command Structure

#### Basic Conversion
```bash
cortexpy convert database.mdb output_directory/
cortexpy convert database.mdf /path/to/parquet/files/
```

#### Advanced Options
```bash
cortexpy convert database.mdb output/ \
  --tables "customers,orders" \
  --compression snappy \
  --batch-size 10000 \
  --include-report \
  --password "secret123"
```

#### Command Parameters
- `--tables, -t`: Specify tables to convert (comma-separated)
- `--exclude-tables, -e`: Tables to exclude from conversion
- `--compression, -c`: Parquet compression (snappy, gzip, lz4, none)
- `--batch-size, -b`: Number of rows to process per batch
- `--include-report, -r`: Generate Excel summary report
- `--report-path`: Custom path for the report file
- `--password, -p`: Database password (for protected files)
- `--connection-string`: Custom connection parameters
- `--max-sample-rows`: Number of sample rows in report (default: 10)

### 4.5 Progress Tracking System

#### Multi-Level Progress Display
```
Converting database.mdb to Parquet format...

Overall Progress: ████████░░ 80% (3/4 tables completed)

Current: Extracting table 'order_details'
├─ Reading data    ███████░░░ 70% (86,419/123,456 rows)
├─ Type conversion ████████░░ 80% 
├─ Writing parquet ██░░░░░░░░ 20%
└─ ETA: 2m 15s

Recently completed:
✓ customers.parquet (10,234 rows, 2.1 MB)
✓ orders.parquet (45,678 rows, 8.7 MB)  
✓ products.parquet (1,567 rows, 0.9 MB)

Next: Generating conversion report...
```

#### Progress Information Components
1. **Overall Progress**: Total tables processed vs remaining
2. **Current Table**: Active table conversion progress
3. **Sub-tasks**: Reading, converting, writing progress
4. **Performance Metrics**: Rows/second, ETA, file sizes
5. **Completion Log**: Successfully converted tables
6. **Error Handling**: Failed tables with error descriptions

### 4.6 Report Generation

#### Excel Report Structure

**Sheet 1: Conversion Summary**
```
Database Conversion Report
Generated: 2025-06-18 14:30:45

Source Information:
├─ File: database.mdb
├─ Format: Microsoft Access 2007
├─ Size: 156.7 MB
├─ Tables Found: 4
└─ Conversion Date: 2025-06-18

Conversion Results:
┌─────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Table Name      │ Records     │ Parquet Size│ Status      │ Notes       │
├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ customers       │ 10,234      │ 1.8 MB      │ ✓ Success   │ No issues   │
│ orders          │ 45,678      │ 7.2 MB      │ ✓ Success   │ No issues   │  
│ products        │ 1,567       │ 0.7 MB      │ ✓ Success   │ No issues   │
│ order_details   │ 123,456     │ 12.8 MB     │ ✓ Success   │ No issues   │
└─────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘

Summary:
├─ Total Records: 180,935
├─ Total Size: 22.5 MB (compression: 19.2% of original)
├─ Processing Time: 4m 32s
├─ Success Rate: 100% (4/4 tables)
└─ Output Location: /path/to/output/directory/
```

**Sheet 2-N: Sample Data (per table)**
```
Table: customers (Sample of 10 records)
┌─────────┬─────────────────┬─────────────────┬─────────────┬─────────────┐
│ id      │ company_name    │ contact_name    │ city        │ country     │
├─────────┼─────────────────┼─────────────────┼─────────────┼─────────────┤
│ 1       │ Alfreds Futterk │ Maria Anders    │ Berlin      │ Germany     │
│ 2       │ Ana Trujillo    │ Ana Trujillo    │ México D.F. │ Mexico      │
│ 3       │ Antonio Moreno  │ Antonio Moreno  │ México D.F. │ Mexico      │
│ ...     │ ...             │ ...             │ ...         │ ...         │
└─────────┴─────────────────┴─────────────────┴─────────────┴─────────────┘

Schema Information:
├─ Primary Key: id
├─ Total Columns: 11
├─ Data Types: INTEGER (2), TEXT (8), DATE (1)
└─ Nullable Columns: contact_name, city, postal_code
```

## 5. Technical Requirements

### 5.1 Dependencies and Libraries

#### Core Dependencies
```python
# Database connectivity
pyodbc>=4.0.35           # SQL Server MDF files
pypyodbc>=1.3.3          # Alternative ODBC driver
pymsql>=1.0.0           # MySQL connector (if needed)

# Access database support  
mdb-tools>=0.9.0        # Linux MDB tools
adodbapi>=2.6.0         # Windows COM-based Access
pandas-access>=0.0.1    # Pandas Access integration

# Parquet handling
pyarrow>=12.0.0         # Parquet read/write
fastparquet>=0.8.3      # Alternative Parquet library

# Excel reporting
openpyxl>=3.1.0         # Excel file creation
xlsxwriter>=3.1.0       # Excel formatting and charts

# Progress and UI
rich>=13.0.0            # Enhanced progress bars
tqdm>=4.65.0           # Fallback progress bars
```

#### Platform-Specific Requirements
```bash
# Windows (recommended for MDB/MDF support)
- Microsoft Access Database Engine Redistributable
- ODBC Driver for SQL Server
- .NET Framework 4.7.2+

# Linux (limited MDB support)
- mdb-tools package
- unixODBC development libraries
- FreeTDS for SQL Server connectivity

# macOS (limited support)
- Homebrew mdb-tools
- Custom ODBC drivers
```

### 5.2 Architecture Integration

#### Plugin System Extension
```python
# New converter classes
class MDBConverter(BaseConverter):
    supported_inputs = {'.mdb', '.accdb'}
    supported_outputs = {'.parquet'}

class MDFConverter(BaseConverter):  
    supported_inputs = {'.mdf', '.ldf'}
    supported_outputs = {'.parquet'}
```

#### Registry Integration
```python
# Auto-registration with existing plugin system
registry.register('mdb', MDBConverter)
registry.register('mdf', MDFConverter)
```

### 5.3 Performance Requirements

#### Processing Capabilities
- **Small Databases** (< 100 MB): < 30 seconds conversion time
- **Medium Databases** (100 MB - 1 GB): < 5 minutes with progress tracking
- **Large Databases** (1-10 GB): < 30 minutes with detailed progress
- **Memory Usage**: < 500 MB RAM regardless of database size
- **Concurrent Processing**: Support for parallel table conversion

#### Scalability Targets
- **Maximum Tables**: 1000+ tables per database
- **Maximum Rows**: 100M+ rows per table (with batching)
- **File Size Limit**: 50 GB input database files
- **Compression Ratio**: 60-80% size reduction vs original

## 6. User Experience Requirements

### 6.1 Progress Feedback

#### Visual Progress Elements
```
1. File Analysis Phase (5-10 seconds)
   ◐ Analyzing database.mdb...
   
2. Discovery Phase (10-30 seconds)  
   ◑ Discovering tables... Found: customers, orders, products
   
3. Summary Phase (5-15 seconds)
   ◒ Analyzing table structures and row counts...
   
4. Conversion Phase (60-80% of total time)
   Per-table progress with sub-stages:
   ├─ Reading: ████████░░ 80%
   ├─ Converting: ██████░░░░ 60% 
   └─ Writing: ███░░░░░░░ 30%
   
5. Report Generation (10-20 seconds)
   ◓ Generating Excel report...
```

#### Information Display
- **Real-time Metrics**: Rows/second, MB/second, ETA
- **Memory Usage**: Current memory consumption
- **Error Recovery**: Automatic retry with exponential backoff
- **Warning Messages**: Data type conversion warnings
- **Success Confirmation**: File paths and sizes of created files

### 6.2 Error Handling

#### Graceful Degradation
```
Scenarios and Responses:
1. Corrupted Database → Skip corrupted tables, report in summary
2. Permission Denied → Clear error message with solutions
3. Insufficient Disk Space → Early detection and user warning
4. Network Interruption → Retry mechanism with progress preservation
5. Memory Limitations → Automatic batch size adjustment
```

#### Error Reporting
```
Error Summary in Excel Report:
┌─────────────────┬─────────────────┬─────────────────────────────┐
│ Table Name      │ Error Type      │ Details                     │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ temp_table      │ Access Denied   │ Table locked by another     │
│                 │                 │ process                     │
│ corrupted_data  │ Data Corruption │ Invalid date values in      │
│                 │                 │ column 'created_at'         │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

## 7. Success Metrics

### 7.1 Performance Metrics
- **Conversion Speed**: > 10,000 rows/second average
- **Memory Efficiency**: < 500 MB peak usage regardless of DB size
- **Compression Ratio**: 60-80% size reduction
- **Success Rate**: > 95% of tables converted successfully

### 7.2 User Experience Metrics
- **Time to First Progress**: < 10 seconds after command execution
- **Progress Update Frequency**: Every 2-3 seconds during conversion
- **Error Recovery Rate**: > 90% of transient errors automatically resolved
- **Report Generation Time**: < 30 seconds for any database size

### 7.3 Quality Metrics
- **Data Integrity**: 100% row count preservation
- **Schema Preservation**: > 99% data type accuracy
- **Report Accuracy**: 100% match between actual and reported results
- **Cross-platform Support**: Windows (full), Linux/macOS (best effort)

## 8. Implementation Phases

### Phase 1: Core Infrastructure (2 weeks)
- [ ] Set up MDB/MDF detection and validation
- [ ] Implement basic table discovery
- [ ] Create progress tracking framework
- [ ] Add Parquet writing capabilities

### Phase 2: Conversion Engine (3 weeks)
- [ ] Implement table-by-table conversion
- [ ] Add data type mapping and transformation
- [ ] Implement batch processing for large tables
- [ ] Add error handling and recovery

### Phase 3: Progress and Reporting (2 weeks)
- [ ] Implement multi-stage progress tracking
- [ ] Create Excel report generation
- [ ] Add sample data extraction
- [ ] Implement conversion summaries

### Phase 4: Polish and Testing (1 week)
- [ ] Comprehensive testing across database types
- [ ] Performance optimization
- [ ] Documentation and help updates
- [ ] CLI integration and option handling

## 9. Risk Assessment

### High Risk Items
1. **Platform Dependencies**: MDB/MDF drivers vary by platform
   - *Mitigation*: Provide clear installation guides per platform
   
2. **Memory Management**: Large tables could exhaust memory
   - *Mitigation*: Implement streaming and batching mechanisms

3. **Database Compatibility**: Variations in MDB/MDF versions
   - *Mitigation*: Extensive testing across database versions

### Medium Risk Items
1. **Performance**: Large database conversion times
   - *Mitigation*: Parallel processing and optimization
   
2. **Data Type Mapping**: Complex types might not map cleanly
   - *Mitigation*: Comprehensive type mapping with fallbacks

## 10. Acceptance Criteria

### Must Have
- [ ] Convert all tables from MDB/MDF to Parquet format
- [ ] Display real-time progress with 6 distinct stages
- [ ] Generate Excel report with summary and sample data
- [ ] Handle databases with 100+ tables and 1M+ rows
- [ ] Preserve data integrity (100% row count match)

### Should Have
- [ ] Support password-protected databases
- [ ] Parallel table processing for performance
- [ ] Automatic error recovery and retry logic
- [ ] Cross-platform compatibility (best effort)
- [ ] Compression options for Parquet output

### Could Have
- [ ] Custom data type mapping configuration
- [ ] Incremental conversion (skip existing files)
- [ ] Integration with cloud storage (S3, Azure, GCP)
- [ ] SQL query preview in reports
- [ ] Data profiling and quality metrics

## 11. Future Enhancements

### Version 0.2.0 Considerations
- Support for Oracle, MySQL, PostgreSQL database files
- Advanced data profiling and quality assessment
- Integration with data catalog systems
- Custom transformation rules and data cleansing
- API endpoints for programmatic access

### Integration Opportunities
- Data pipeline automation tools
- Cloud data platform connectors
- Business intelligence tool integration
- Data governance and lineage tracking

---

## Appendix

### A. Command Examples
```bash
# Basic conversion
cortexpy convert sales.mdb /data/parquet/

# With specific tables and options
cortexpy convert hr_database.mdf /output/ \
  --tables "employees,departments,salaries" \
  --compression snappy \
  --include-report \
  --batch-size 5000

# Password-protected database
cortexpy convert secure.accdb /output/ \
  --password "mypassword" \
  --report-path /reports/conversion_summary.xlsx

# Verbose mode with detailed progress
cortexpy --verbose convert legacy.mdb /modern/ \
  --max-sample-rows 20 \
  --compression gzip
```

### B. Expected Output Structure
```
/output/directory/
├── customers.parquet
├── orders.parquet
├── products.parquet
├── order_details.parquet
└── conversion_report.xlsx
    ├── Sheet1: Summary
    ├── Sheet2: customers_sample
    ├── Sheet3: orders_sample
    ├── Sheet4: products_sample
    └── Sheet5: order_details_sample
```

### C. Progress Output Examples
```
Stage 1: 🔍 Analyzing database.mdb... ✓ (3.2s)
Stage 2: 📋 Discovering tables... Found 4 tables ✓ (1.8s) 
Stage 3: 📊 Extracting summary... ✓ (2.1s)

Tables discovered:
┌─────────────────┬─────────────┬─────────────┐
│ Table           │ Records     │ Est. Size   │
├─────────────────┼─────────────┼─────────────┤
│ customers       │ 10,234      │ 2.1 MB      │
│ orders          │ 45,678      │ 8.7 MB      │
│ products        │ 1,567       │ 0.9 MB      │
│ order_details   │ 123,456     │ 15.2 MB     │
└─────────────────┴─────────────┴─────────────┘

Stage 4: 🔄 Converting tables...

[1/4] customers ████████████████████ 100% ✓ (8.2s)
      → customers.parquet (1.8 MB, 10,234 rows)

[2/4] orders ███████████████████████ 100% ✓ (23.4s)  
      → orders.parquet (7.2 MB, 45,678 rows)

[3/4] products ████████████████████ 100% ✓ (2.1s)
      → products.parquet (0.7 MB, 1,567 rows)

[4/4] order_details ████████████░░░ 85% (104,838/123,456)
      ├─ Reading    ████████████░░░ 85%
      ├─ Converting ████████████████ 100%  
      └─ Writing    ████████░░░░░░░ 60%
      ETA: 12s (8,547 rows/sec)

Stage 5: 📑 Generating report... ✓ (4.3s)

✅ Conversion completed successfully!
   📁 Output: /data/parquet/
   📊 Report: /data/parquet/conversion_report.xlsx
   ⏱️  Total time: 4m 12s
   📈 Processing rate: 12,847 rows/sec
```