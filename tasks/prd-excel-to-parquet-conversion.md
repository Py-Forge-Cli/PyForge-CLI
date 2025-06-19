# PRD: Excel to Parquet Conversion with Multi-Tab Support

## 1. Overview

### 1.1 Purpose
Develop a robust Excel (.xlsx) to Parquet conversion tool that intelligently handles multi-tab workbooks, performs data validation, and provides user interaction for optimal conversion strategies.

### 1.2 Scope
- Convert Excel files (.xlsx only) to Parquet format
- Handle multi-tab workbooks with intelligent column signature detection
- All data converted to string format (Phase 1)
- Interactive CLI for user decisions on conversion strategy

## 2. Functional Requirements

### 2.1 File Format Support
- **Input**: Excel files (.xlsx format only)
- **Output**: Parquet files with all columns as string type
- **Exclusions**: .xls format (legacy Excel)

### 2.2 Sheet Processing

#### 2.2.1 Sheet Identification
- Automatically detect and list all sheets in the workbook
- Display sheet names and basic metadata (row count, column count)
- Handle empty sheets gracefully with appropriate warnings

#### 2.2.2 Column Signature Analysis
- Extract column headers from each sheet
- Compare column signatures across sheets with:
  - Exact column name matching
  - Column order consideration
  - Case-insensitive comparison
- Group sheets with identical signatures

#### 2.2.3 Table Detection
- Identify distinct tables within the workbook
- Provide summary of:
  - Number of unique table structures
  - Sheets belonging to each table structure
  - Record count per sheet

### 2.3 Data Conversion

#### 2.3.1 Data Type Handling
- Convert all data to string format
- Numeric values: Use decimal precision up to 27 digits
- Date/DateTime values: Convert to ISO 8601 format (YYYY-MM-DD HH:MM:SS)
- Formula cells: 
  - Extract calculated values
  - Display warning: "Detected calculated values. System will convert all formula results to string"
- Empty cells: Preserve as empty strings

#### 2.3.2 Output Strategy
- **Matching Signatures**: Single parquet file with original column names
  - Column naming: `{original_column_name}` (no sheet name prefix)
  - All matching sheets combined into single file
- **Different Signatures**: Multiple parquet files
  - File naming: `{original_filename}_{sheet_name}.parquet`
- No nested structures in parquet output

### 2.4 User Interaction

#### 2.4.1 Multi-Tab Detection Flow
1. Display analysis results:
   - List of sheets detected
   - Column signature groups
   - Table structure summary
   - Record counts per sheet

2. For matching signatures:
   - Prompt: "Multiple tabs detected with same data model. Options:"
     - [1] Combine into single parquet file (default)
     - [2] Keep as separate parquet files
   - Default action: Combine if no response

3. For different signatures:
   - Inform: "Multiple table structures detected. Will create separate parquet files"
   - Show mapping of sheets to output files

#### 2.4.2 Validation and Error Handling
- Pre-conversion validation:
  - File accessibility check
  - Password protection detection
  - File corruption check
  - Empty workbook detection
  
- Display validation results and seek confirmation:
  - "Validation complete. [n] issues found. Proceed with conversion? (Y/n)"
  
- Error scenarios:
  - Empty sheets: Warning with option to skip
  - Headers-only sheets: Warning with option to skip
  - Corrupted data: Error with detailed message
  - Protected files: Error requesting password or skip

### 2.5 Progress and Reporting

#### 2.5.1 Processing Feedback
- Progress bar for large files
- Current sheet being processed
- Estimated time remaining

#### 2.5.2 Conversion Summary
- Total sheets processed
- Output files created
- Record counts per output
- Any warnings or skipped content
- Total processing time

## 3. Technical Requirements

### 3.1 Performance
- Stream processing for large files (>100MB)
- Memory-efficient handling of multi-sheet workbooks
- Parallel processing where applicable

### 3.2 Data Integrity
- Validate output parquet files
- Row count verification
- Sample data comparison
- Checksum generation for traceability

### 3.3 Logging
- Detailed conversion log
- Warning/error tracking
- Audit trail of user decisions

## 4. User Interface

### 4.1 Command Line Interface
```bash
cortexpy convert excel <input_file.xlsx> --format parquet [options]
```

### 4.2 Options
- `--output-dir`: Specify output directory
- `--prefix`: Custom prefix for output files
- `--force`: Skip all prompts, use defaults
- `--verbose`: Detailed logging
- `--dry-run`: Analyze without conversion
- `--combine`: Force combination of matching sheets (default: true)
- `--separate`: Keep all sheets as separate files

## 5. Future Enhancements (Out of Scope)

### 5.1 Phase 2 - Data Type Mapping
- Intelligent data type detection
- Configurable type mapping rules
- Schema inference and validation

### 5.2 Batch Processing
- Non-interactive mode
- Configuration file support
- Multiple file processing
- Automated decision rules

### 5.3 Additional Formats
- Support for .xls files
- CSV output option
- JSON output option

## 6. Acceptance Criteria

1. Successfully converts single-sheet Excel files to parquet
2. Detects and groups sheets with matching column signatures
3. Provides clear user prompts for conversion decisions
4. Handles all Excel data types by converting to strings
5. Generates valid parquet files readable by standard tools
6. Provides comprehensive summary of conversion results
7. Gracefully handles error scenarios with informative messages

## 7. Example Workflows

### 7.1 Single Table, Multiple Sheets
```text
$ cortexpy convert excel sales_data.xlsx --format parquet

🔍 Analyzing Excel file...
✓ File validation passed
✓ 3 sheets detected: Q1_Sales, Q2_Sales, Q3_Sales

📊 Data Summary:
┌─────────────┬──────────┬──────────┐
│ Sheet       │ Rows     │ Columns  │
├─────────────┼──────────┼──────────┤
│ Q1_Sales    │ 15,234   │ 12       │
│ Q2_Sales    │ 18,456   │ 12       │
│ Q3_Sales    │ 21,789   │ 12       │
└─────────────┴──────────┴──────────┘

✓ Column signature analysis complete
ℹ️  All 3 sheets have matching column signatures

Multiple tabs detected with same data model. Options:
[1] Combine into single parquet file (default)
[2] Keep as separate parquet files
Enter choice [1]: 1

Converting to Parquet...
[████████████████████] 100% | Processing Q3_Sales | Time: 00:02:15

✅ Conversion Complete!
📁 Output: sales_data.parquet
📊 Total records: 55,479
⏱️  Processing time: 2m 15s
```

### 7.2 Multiple Tables
```text
$ cortexpy convert excel company_data.xlsx --format parquet

🔍 Analyzing Excel file...
✓ File validation passed
✓ 3 sheets detected: Employees, Products, Sales

📊 Data Summary:
┌─────────────┬──────────┬──────────┐
│ Sheet       │ Rows     │ Columns  │
├─────────────┼──────────┼──────────┤
│ Employees   │ 1,234    │ 8        │
│ Products    │ 5,678    │ 15       │
│ Sales       │ 45,789   │ 10       │
└─────────────┴──────────┴──────────┘

✓ Column signature analysis complete
⚠️  3 different table structures detected
ℹ️  Will create separate parquet files for each table

Proceed with conversion? (Y/n): Y

Converting to Parquet...
[████████████████████] 100% | Processing Sales | Time: 00:01:45

✅ Conversion Complete!
📁 Output files:
   - company_data_Employees.parquet (1,234 records)
   - company_data_Products.parquet (5,678 records)
   - company_data_Sales.parquet (45,789 records)
⏱️  Total processing time: 1m 45s
```

### 7.3 Mixed Scenario with Warnings
```text
$ cortexpy convert excel quarterly_report.xlsx --format parquet

🔍 Analyzing Excel file...
✓ File validation passed
✓ 4 sheets detected: Q1_2024, Q2_2024, Q3_2024, Summary

⚠️  Warning: Detected calculated values in Summary sheet
    System will convert all formula results to string

📊 Data Summary:
┌─────────────┬──────────┬──────────┬─────────────┐
│ Sheet       │ Rows     │ Columns  │ Formulas    │
├─────────────┼──────────┼──────────┼─────────────┤
│ Q1_2024     │ 12,345   │ 10       │ 0           │
│ Q2_2024     │ 14,567   │ 10       │ 0           │
│ Q3_2024     │ 16,789   │ 10       │ 0           │
│ Summary     │ 50       │ 5        │ 25          │
└─────────────┴──────────┴──────────┴─────────────┘

✓ Column signature analysis complete
ℹ️  Sheets Q1_2024, Q2_2024, Q3_2024 have matching signatures
ℹ️  Sheet Summary has different structure

Combine Q1-Q3 into single file? (Y/n): Y

Converting to Parquet...
[████████████████████] 100% | Processing Summary | Time: 00:02:30

✅ Conversion Complete!
📁 Output files:
   - quarterly_report_sales.parquet (43,701 records from Q1-Q3)
   - quarterly_report_Summary.parquet (50 records)
⚠️  25 formula cells converted to string values
⏱️  Total processing time: 2m 30s
```