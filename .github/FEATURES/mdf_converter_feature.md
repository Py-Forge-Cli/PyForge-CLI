---
name: ✨ Feature Request - MDF to Parquet Converter
about: Add MDF (SQL Server) to Parquet file conversion capability
title: '[FEATURE] MDF to Parquet Converter'
labels: 'enhancement, claude-ready, feature-request, prd-workflow, converter, new-format'
assignees: ''
---

## 🚀 Feature Request Overview
<!-- Convert SQL Server MDF files to Parquet format using Docker-based processing -->

**Feature Name**: MDF to Parquet Converter
**Type**: [ ] New Command [x] Enhancement [ ] Integration [ ] Performance [ ] Other: ___

## 📋 Implementation Workflow
This feature request follows the **PRD → Tasks → Implementation** workflow:

1. **📝 PRD Creation**: Complete this issue to create a comprehensive PRD document
2. **🎯 Task Generation**: Generate structured task list from approved PRD  
3. **⚡ Implementation**: Execute tasks one-by-one with approval checkpoints

---

## 📋 PRD REQUIREMENTS GATHERING

### 🎯 Problem Statement
Users have SQL Server MDF files that need conversion to modern Parquet format but face challenges:
- No Python libraries can directly read proprietary MDF format
- Existing solutions require complex SQL Server installations
- Large MDF files need streaming conversion to avoid memory issues
- Need simple, consistent conversion approach aligned with existing converters

### 💡 Proposed Solution Overview
Extend PyForge CLI converter architecture to support MDF files with string-only conversion:
- Integrate with Docker-based SQL Server Express (from MDF Tools Installer)
- Attach MDF files temporarily to extract data
- Convert all data to string format (consistent with existing converters)
- Stream large tables in chunks to avoid memory issues
- Follow existing CLI patterns and options structure

### 👥 Target Users
- **Data Engineers**: Converting legacy SQL Server databases to data lakes
- **Business Analysts**: Processing MDF files from various business systems
- **Data Scientists**: Needing Parquet format for analytics workflows
- **Skill Levels**: Intermediate (familiar with CLI tools and data formats)

### 🔄 User Journey
1. User starts with: MDF file and MDF Tools Installer already configured
2. User runs: `pyforge convert database.mdf --format parquet`
3. Tool processes: 6-stage conversion process (identical to MDB converter)
4. User receives: Directory with Parquet files (one per table) + Excel conversion report
5. User can then: Use Parquet files in analytics tools or data pipelines

### 📊 Requirements Breakdown
#### Functional Requirements
- [ ] Analyze existing PyForge converter patterns and CLI options structure
- [ ] Implement identical 6-stage conversion process as MDB converter
- [ ] Validate MDF Tools Installer prerequisites are met
- [ ] Attach MDF files to SQL Server Express container (replaces MDB connection)
- [ ] Extract all tables and convert to string format (no type inference)
- [ ] Stream large tables in configurable chunks (--chunk-size option)
- [ ] Exclude system tables by default (--exclude-system-tables option)
- [ ] Generate Excel conversion report identical to MDB pattern
- [ ] Clean up temporary databases after conversion

#### Non-Functional Requirements  
- [ ] **Performance**: Handle databases up to 10GB with streaming
- [ ] **Compatibility**: Support SQL Server 2008+ MDF files
- [ ] **Usability**: Follow existing converter CLI patterns exactly
- [ ] **Reliability**: Graceful handling of corrupted or locked MDF files

### 🖥️ Command Line Interface Design
**IMPORTANT**: Must analyze existing `pyforge convert --help` and follow current patterns exactly.

```bash
# Basic conversion following existing pattern (creates database_parquet/ directory)
pyforge convert database.mdf --format parquet

# MDF-specific options (simplified, consistent with existing patterns)
pyforge convert sales.mdf \
    --format parquet \
    --chunk-size 50000 \
    --compression gzip \
    --exclude-system-tables \
    --force

# Validation and info commands (already exist in framework)
pyforge validate database.mdf        # Check if MDF is valid
pyforge info database.mdf           # Display database metadata

# Existing options that should work with MDF
pyforge convert database.mdf --format parquet --compression snappy --verbose
```

**Key Constraints**:
- Must use existing `--format parquet` option (not new format)
- Must use existing `--compression` options (snappy, gzip, none)
- Must use existing `--force` flag for overwrite behavior
- Must create output directory like other database converters (MDB, DBF)
- No new CLI options except `--chunk-size` and `--exclude-system-tables`

### 📁 Input/Output Specifications
- **Input Types**: .mdf files (with optional .ldf files)
- **Output Types**: Directory with Parquet files (one per table), following MDB/DBF pattern
- **Processing Options**: String-only conversion, compression, system table exclusion
- **Configuration**: Uses MDF tools configuration from installer (~/.pyforge/mdf-config.json)

### 🔍 Technical Architecture
- **Core Components**: 
  - `MdfConverter` extending `StringDatabaseConverter` (like MDB converter)
  - Identical 6-stage progress tracking with Rich console output
  - SQL Server container integration via MDF tools configuration
  - String-only data extraction (no type inference, matching MDB pattern)
  - Excel report generation with summary and sample data
- **Dependencies**: pyodbc, sqlalchemy (new), existing converter framework
- **Integration Points**: Plugin loader registration, existing CLI command structure
- **Data Flow**: MDF → Docker Volume → SQL Server → String Extraction → Parquet + Excel Report

### 6-Stage Conversion Process (Identical to MDB)
**CRITICAL**: Must implement exact same stages as MDB converter:

#### Stage 1: Analyzing the file
- Validate MDF file exists and is accessible
- Check MDF Tools Installer prerequisites (Docker + SQL Server)
- Display file format, size, and validation status
- Set up SQL Server connection parameters

#### Stage 2: Listing all tables
- Attach MDF file to SQL Server Express container
- Connect to attached database
- Enumerate all user tables (exclude system tables by default)
- Display table discovery progress

#### Stage 3: Extracting summary
- Get metadata for each table (record count, column count)
- Calculate total records and estimated size
- Build table information structure

#### Stage 4: Table Overview
- Display Rich table with columns: Table Name, Records, Columns
- Show totals row with aggregate statistics
- Format numbers with commas (e.g., "1,234 records")

#### Stage 5: Converting tables to Parquet
- Create output directory (database_name_parquet/)
- Rich progress bar showing current table being processed
- Convert each table: SQL → DataFrame → String conversion → Parquet
- Display success/failure for each table with record counts

#### Stage 6: Conversion Summary + Excel Report
- Display final statistics (files created, records converted, output size)
- List all output files with record counts
- Generate Excel report with summary sheet and sample data sheets
- Clean up SQL Server (detach database)

### 🧪 Testing Strategy
- **Unit Tests**: Converter logic, string conversion, CLI option handling
- **Integration Tests**: Full conversion pipeline, various MDF formats, directory output
- **Performance Tests**: Large file handling (chunking), memory usage, streaming
- **Edge Cases**: Corrupted files, missing LDF, system table handling, container issues

---

## 🎯 PRD APPROVAL CHECKLIST
**Complete this section before generating tasks:**

- [ ] Problem statement clearly defines user pain points
- [ ] Solution approach is technically feasible
- [ ] Requirements are specific and measurable
- [ ] CLI interface follows project conventions
- [ ] Testing strategy covers all scenarios
- [ ] Performance requirements are realistic
- [ ] Implementation approach is approved

---

## 📋 TASK GENERATION TRIGGER
**Once PRD is approved, use this section to generate implementation tasks:**

### Task List Creation
- [ ] **Ready to generate tasks**: PRD approved and complete
- [ ] **Task file created**: `/tasks/tasks-mdf-converter.md`
- [ ] **Implementation started**: First task marked in_progress

### Claude Implementation Commands
```bash
# Generate PRD document
"Create a PRD for MDF to Parquet Converter based on the requirements above"

# Generate task list from PRD  
"Generate tasks from /tasks/prd-mdf-converter.md"

# Start implementation
"Start working on /tasks/tasks-mdf-converter.md"
```

---

## 🔍 CLAUDE GUIDANCE SECTION

### File Structure for Implementation
```
/tasks/
  ├── prd-mdf-converter.md           # Product Requirements Document
  ├── tasks-mdf-converter.md         # Implementation task list
  └── ...

@docs/                              # Documentation under docs folder
  ├── converters/
  │   ├── mdf-to-parquet.md         # Converter guide
  │   └── mdf-troubleshooting.md    # Common issues
  └── ...
```

### Key Investigation Areas
```bash
# CRITICAL: Analyze existing CLI patterns first
pyforge convert --help                    # Study current options structure
grep -r "chunk.*size" src/pyforge_cli/    # Check if chunk-size exists
grep -r "exclude.*system" src/pyforge_cli/ # Check for system table options

# Study MDB converter implementation (reference pattern)
src/pyforge_cli/converters/mdb_converter.py   # 6-stage process implementation
src/pyforge_cli/converters/string_database_converter.py  # Base class
src/pyforge_cli/readers/mdb_reader.py          # Database connection pattern

# Examine existing converter patterns  
grep -r "StringDatabaseConverter" src/pyforge_cli/
grep -r "convert_with_progress" src/pyforge_cli/
grep -r "_generate_excel_report" src/pyforge_cli/

# Core files to analyze and modify
# - src/pyforge_cli/main.py (CLI options - analyze existing patterns)
# - src/pyforge_cli/converters/mdb_converter.py (EXACT reference for 6-stage process)
# - src/pyforge_cli/converters/mdf_converter.py (new - copy MDB pattern exactly)
# - src/pyforge_cli/readers/mdf_reader.py (new - SQL Server connection)
# - src/pyforge_cli/plugins/loader.py (register converter)
```

### Implementation Checkpoints
- [ ] **Phase 1**: Study MDB converter and copy exact 6-stage process structure
- [ ] **Phase 2**: Create MDF reader for SQL Server Express integration
- [ ] **Phase 3**: Implement MdfConverter extending StringDatabaseConverter
- [ ] **Phase 4**: Add chunked streaming and system table exclusion options
- [ ] **Phase 5**: Integrate with CLI and comprehensive documentation updates

### Documentation Requirements
**CRITICAL**: Must audit and update ALL existing documentation to include MDF support:

#### Documentation Audit Scope
```bash
# Read and analyze current documentation structure
# Update ALL references to supported formats
docs/
├── index.md                    # Add MDF to main overview
├── README.md                   # Update supported formats list  
├── CHANGELOG.md                # Add MDF converter release notes
├── converters/
│   ├── index.md               # Add MDF converter to list
│   ├── mdf-to-parquet.md      # New comprehensive guide
│   └── ...
├── cli-reference.md           # Add MDF examples
└── github-pages/**            # Update ALL pages mentioning formats
```

#### Required Documentation Updates
- [ ] **Main README.md**: Add MDF to supported formats, update examples
- [ ] **docs/index.md**: Add MDF converter to overview and quick start
- [ ] **docs/converters/index.md**: Add MDF converter with description
- [ ] **docs/cli-reference.md**: Add MDF conversion examples and options
- [ ] **CHANGELOG.md**: Document new MDF converter feature
- [ ] **mkdocs.yml**: Add MDF documentation to navigation
- [ ] **All format lists**: Update every instance mentioning supported formats
- [ ] **GitHub Pages**: Audit all published pages for format references

---

## 📊 SUCCESS CRITERIA
- [ ] PRD document created and approved
- [ ] Task list generated with clear acceptance criteria
- [ ] All tasks completed with user approval at each step
- [ ] CLI patterns analyzed and MDF options integrated consistently
- [ ] Converter follows StringDatabaseConverter architecture exactly (like MDB)
- [ ] Implements identical 6-stage conversion process with Rich progress
- [ ] Successfully converts MDF files to directory with Parquet files (string format)
- [ ] Generates Excel report with summary and sample data (like MDB)
- [ ] Handles large databases with chunked streaming
- [ ] System tables excluded by default with option to include
- [ ] All existing documentation updated with MDF support
- [ ] Test coverage meets project standards
- [ ] User experience identical to MDB converter (familiar workflow)

---

## 🔗 RELATED WORK
- **Related Issues**: MDF Tools Installer feature
- **Depends On**: MDF Tools Installer (prerequisite)
- **Blocks**: None
- **Similar Features**: XML converter, CSV converter, Excel converter

---

## 📅 PRIORITIZATION
- **Business Impact**: High (enables SQL Server data migration)
- **Technical Complexity**: High (SQL Server integration, streaming)  
- **User Demand**: Medium (specialized use case)
- **Implementation Timeline**: 2-3 weeks

---
**For Maintainers - PRD Workflow:**
- [ ] Issue reviewed and PRD requirements complete
- [ ] Technical feasibility confirmed
- [ ] PRD document creation approved
- [ ] Task generation authorized
- [ ] Implementation approach validated