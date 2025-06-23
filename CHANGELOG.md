# CortexPy CLI - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0] - 2025-06-23

### 🎉 Major Feature: MDF Tools Installer

**Complete SQL Server MDF file processing infrastructure** - Automated Docker Desktop and SQL Server Express 2019 installation with container management for MDF file conversion preparation.

### ✨ Added

#### MDF Tools Installer
- **Docker Desktop Installation**: Automated installation across platforms
  - macOS: Homebrew Cask installation (`brew install --cask docker`)
  - Windows: Winget installation (`winget install Docker.DockerDesktop`)
  - Linux: Package manager installation (apt/yum)
  - Installation verification and status checking
  - Automatic Docker daemon startup

- **SQL Server Express 2019 Container**: Production-ready database server
  - Microsoft SQL Server Express 2019 (latest)
  - Container name: `pyforge-sql-server`
  - Default credentials: sa user with secure password generation
  - Persistent data storage via Docker volumes
  - Health checks and connection testing
  - Memory limit: 2GB, optimized for development

#### Interactive Setup Wizard
- **Smart Installation Detection**: Checks existing Docker and SQL Server installations
- **User-Guided Setup**: Interactive prompts for configuration options
- **Non-Interactive Mode**: `--non-interactive` flag for automation
- **Progress Tracking**: Real-time installation progress with Rich UI
- **Error Recovery**: Robust error handling with user-friendly messages

#### Container Management Commands
- **Status Monitoring**: `pyforge mdf-tools status` - Complete system status
- **Lifecycle Management**: 
  - `pyforge mdf-tools start` - Start SQL Server container
  - `pyforge mdf-tools stop` - Stop SQL Server container  
  - `pyforge mdf-tools restart` - Restart SQL Server container
- **Maintenance Operations**:
  - `pyforge mdf-tools logs` - View SQL Server logs
  - `pyforge mdf-tools test` - Test database connectivity
  - `pyforge mdf-tools config` - Show configuration details
  - `pyforge mdf-tools uninstall` - Complete removal of tools

#### Cross-Platform Support
- **Windows**: Native Docker Desktop with Winget
- **macOS**: Docker Desktop via Homebrew
- **Linux**: Docker CE via package managers
- **Container Portability**: Consistent SQL Server across all platforms
- **Platform Detection**: Automatic OS detection and appropriate installation

### 🔧 Enhanced

#### Installation Infrastructure
- **System Package Managers**: Uses native OS package managers instead of pip
- **Dependency Validation**: Comprehensive prerequisite checking
- **Path Detection**: Automatic Docker and SQL Server path resolution
- **Service Integration**: Proper system service management

#### Configuration Management
- **Configuration File**: JSON-based configuration storage
- **Credential Management**: Secure password generation and storage
- **Port Management**: Configurable SQL Server port (default: 1433)
- **Volume Management**: Persistent data storage configuration

#### Error Handling & Recovery
- **Interactive Prompts**: Graceful handling of EOF errors in non-interactive environments
- **Fallback Strategies**: Multiple installation methods per platform
- **Detailed Logging**: Comprehensive error reporting and debugging
- **User Guidance**: Clear next-step instructions on failures

### 🔍 CLI Integration

#### New Command Structure
```bash
# Installation command group
pyforge install mdf-tools          # Interactive installer

# Management command group  
pyforge mdf-tools status           # System status
pyforge mdf-tools start           # Start SQL Server
pyforge mdf-tools stop            # Stop SQL Server
pyforge mdf-tools restart         # Restart SQL Server
pyforge mdf-tools logs            # View logs
pyforge mdf-tools test            # Test connectivity
pyforge mdf-tools config          # Show configuration
pyforge mdf-tools uninstall       # Complete removal

# Non-interactive mode
pyforge install mdf-tools --non-interactive
```

#### Rich Terminal UI
- **Status Tables**: Beautiful tabular status displays
- **Progress Bars**: Real-time installation progress
- **Color Coding**: Status indicators with color-coded output
- **Structured Output**: Clean, professional terminal formatting

### 🐛 Fixed

#### Docker Installation Issues
- **Fixed**: Attempted pip installation of Docker Desktop
- **Solution**: Use system package managers (brew, winget, apt, yum)
- **Impact**: Proper Docker Desktop installation across all platforms

#### Interactive Prompt Handling
- **Fixed**: EOFError when reading lines in non-interactive environments
- **Solution**: Comprehensive try/catch with fallback to defaults
- **Result**: Reliable operation in CI/CD and automated environments

#### SQL Server Connection Testing
- **Fixed**: Incorrect sqlcmd path in container
- **Solution**: Use correct path `/opt/mssql-tools18/bin/sqlcmd`
- **Result**: Successful database connectivity testing

#### Container Resource Management
- **Enhanced**: Memory limits and resource constraints
- **Result**: Stable SQL Server operation in development environments

### 📊 Technical Specifications

#### SQL Server Express 2019 Limitations
- **Database Size**: Maximum 10GB per database
- **Memory Usage**: Maximum 1.4GB RAM utilization
- **CPU Cores**: Maximum 4 cores utilization
- **Compute Power**: Limited compared to full SQL Server editions
- **Advanced Features**: Limited replication, analysis services, and reporting

#### Container Configuration
- **Base Image**: `mcr.microsoft.com/mssql/server:2019-latest`
- **Memory Limit**: 2GB container limit
- **Port Mapping**: 1433:1433 (configurable)
- **Volume Mount**: Persistent data storage
- **Environment**: Production-optimized settings

#### System Requirements
- **Docker Desktop**: 4.0+ with 2GB RAM allocation
- **Available Memory**: Minimum 4GB system RAM (8GB recommended)
- **Disk Space**: 2GB for SQL Server image + data storage
- **Network**: Port 1433 available (configurable)

### 📝 Documentation

#### Comprehensive User Guides
- **MDF Tools Installer Documentation**: Complete setup and usage guide
- **Architecture Diagrams**: ASCII art diagrams showing system architecture
- **Live Terminal Examples**: Real macOS terminal session outputs
- **Troubleshooting Guide**: Common issues and solutions
- **Tools Prerequisites**: New Getting Started section

#### Developer Documentation
- **Plugin Architecture**: Integration patterns for database tools
- **Container Management**: Docker integration best practices
- **Cross-Platform Development**: OS-specific implementation notes
- **Testing Framework**: Automated and manual testing procedures

### 🔮 MDF Converter Preparation

This release prepares the foundation for the upcoming MDF Converter feature:

- **Infrastructure Ready**: Docker and SQL Server environment established
- **Connection Framework**: Database connectivity and testing implemented  
- **Management Tools**: Complete lifecycle management for SQL Server
- **Cross-Platform Base**: Consistent environment across all operating systems

### 💡 Migration Notes

#### For New Users
- Run `pyforge install mdf-tools` for one-time setup
- MDF conversion will be available in the next release
- All existing format converters remain unchanged

#### For Developers
- New installer plugin system for complex tool chains
- Container management patterns for database processing
- Rich terminal UI components for interactive installations

---

## [0.2.4] - 2025-06-21

### 🔧 Fixed
- **Package Build Configuration**: Fixed wheel packaging metadata issues
  - Corrected hatchling build configuration for src layout
  - Fixed missing Name and Version fields in wheel metadata
  - Updated package metadata to include proper project information
  - Resolved InvalidDistribution errors during PyPI publication

---

## [0.2.3] - 2025-06-21

### 🔧 Fixed
- **GitHub Actions Workflow**: Fixed deprecation warnings and failures
  - Updated pypa/gh-action-pypi-publish to v1.11.0 (latest version)
  - Removed redundant sigstore signing step (PyPI handles signing automatically)
  - Fixed deprecated actions/upload-artifact v3 usage causing workflow failures
  - Simplified and improved workflow reliability

---

## [0.2.2] - 2025-06-21

### 🎉 Major Feature: CSV to Parquet Conversion with Auto-Detection

**Complete CSV file conversion support** - Full CSV, TSV, and delimited text file conversion with intelligent auto-detection of delimiters, encoding, and headers.

### ✨ Added

#### CSV File Format Support
- **CSV/TSV/TXT Conversion**: Comprehensive delimited file conversion support
  - Auto-detection of delimiters (comma, semicolon, tab, pipe)
  - Intelligent encoding detection (UTF-8, Latin-1, Windows-1252, UTF-16)
  - Smart header detection with fallback to generic column names
  - Support for quoted fields with embedded delimiters and newlines
  - International character set handling

#### String-Based Conversion (Consistent with Phase 1)
- **Unified Data Output**: All CSV data converted to strings for consistency
  - Numbers: Preserved as-is from source (e.g., `"123.45"`, `"1000"`)
  - Dates: Original format preserved (e.g., `"2024-03-15"`, `"03/15/2024"`)
  - Text: UTF-8 encoded strings
  - Empty values: Preserved as empty strings

#### Performance Optimizations
- **Memory Efficient Processing**: Chunked reading for large files
- **Streaming Conversion**: Processes files without loading entirely into memory
- **Progress Tracking**: Real-time conversion statistics and progress bars

### 🔧 Enhanced

#### CLI Integration
- **Seamless Format Detection**: Automatic CSV format recognition in `pyforge formats`
- **Consistent Options**: Full compatibility with existing CLI flags
  - `--compression`: snappy (default), gzip, none
  - `--force`: Overwrite existing output files
  - `--verbose`: Detailed conversion statistics and progress

#### GitHub Workflow Enhancements
- **Enhanced Issue Templates**: Structured Product Requirements Documents for complex features
- **Task Implementation**: Execution tracking templates for development workflow
- **Multi-Agent Development**: Templates support parallel Claude agent collaboration

### 🐛 Fixed

#### Documentation Accuracy
- **README Sync**: Updated supported formats table to show CSV as available
- **Status Correction**: Changed CSV from "🚧 Coming Soon" to "✅ Available"
- **Example Additions**: Added comprehensive CSV conversion examples

### 🧪 Comprehensive Testing
- **Unit Tests**: 200+ test cases covering all CSV scenarios
- **Integration Tests**: End-to-end CLI testing
- **Test Coverage**: Multi-format samples with international data

### 📊 Performance Metrics
- **Small CSV files** (<1MB): <5 seconds with full auto-detection
- **Medium CSV files** (1-50MB): <30 seconds with progress tracking
- **Auto-detection accuracy**: >95% for common CSV formats

---

## [0.2.0] - 2025-06-19

### 🎉 Major Feature: MDB/DBF to Parquet Conversion (Phase 1)

**Complete database file conversion support** - Full MDB (Microsoft Access) and DBF (dBase) file conversion support with string-only output and enterprise-grade features.

### ✨ Added

#### Database File Support
- **MDB/ACCDB Conversion**: Full Microsoft Access database conversion support
  - Cross-platform compatibility (Windows/macOS/Linux)
  - Password-protected file detection (Windows ODBC + mdbtools fallback)
  - System table filtering (excludes MSys* tables)
  - Multi-table batch conversion
  - NumPy 2.0 compatibility with fallback strategies

- **DBF Conversion**: Complete dBase file format support
  - All DBF versions supported via dbfread library
  - Robust upfront encoding detection with 8 candidate encodings
  - Strategic sampling from beginning, middle, and end of files
  - Early exit optimization for perfect encoding matches
  - Memo field processing (.dbt/.fpt files)
  - Field type preservation in metadata

#### String-Only Data Conversion (Phase 1)
- **Unified Data Types**: All source data converted to strings per Phase 1 specification
  - Numbers: Decimal format with 5 precision (e.g., `123.40000`)
  - Dates: ISO 8601 format (e.g., `2024-03-15`, `2024-03-15 14:30:00`)
  - Booleans: Lowercase strings (`"true"`, `"false"`)
  - Binary: Base64 encoding
  - NULL values: Empty strings (`""`)

#### 6-Stage Progress Tracking
- **Stage 1**: File analysis with format detection
- **Stage 2**: Table discovery and listing
- **Stage 3**: Summary data extraction
- **Stage 4**: Pre-conversion table overview with record/column counts
- **Stage 5**: Table-by-table conversion with progress bars
- **Stage 6**: Excel report generation

#### Rich Terminal UI
- Beautiful table displays with proper alignment
- Color-coded status messages and progress indicators
- Real-time conversion metrics
- Progress bars for multi-table operations
- Clean, professional output formatting

#### Excel Report Generation
- **Summary Sheet**: Conversion metadata and table overview
- **Sample Data Sheets**: First 10 records from each converted table
- **Timestamped Reports**: `{filename}_conversion_report_{timestamp}.xlsx`
- **Comprehensive Metadata**: File paths, record counts, conversion statistics

### 🔧 Enhanced

#### Cross-Platform Database Access
- **Windows**: ODBC-based reading with pyodbc
- **macOS/Linux**: mdbtools integration with pandas-access
- **NumPy 2.0 Compatibility**: Fixed deprecated NumPy alias issues
- **Fallback Strategies**: Automatic method selection based on platform

#### File Detection & Validation
- **Magic Byte Detection**: Robust file format identification
- **Database File Detector**: Comprehensive validation for MDB/DBF files
- **Password Protection Detection**: Identifies encrypted Access databases
- **Version Information**: Extracts database version details

#### Memory Efficient Processing
- **Streaming Readers**: Large file support with controlled memory usage
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Compressed Output**: Snappy compression by default for Parquet files
- **Memory Cleanup**: Garbage collection for large datasets

### 🔍 CLI Enhancements

#### New Commands & Options
```bash
# Database conversion with various options
cortexpy convert database.mdb --format parquet
cortexpy convert data.dbf output_dir/ --format parquet --compression gzip
cortexpy convert secure.accdb --password "secret" --tables "customers,orders"

# File information and validation
cortexpy info database.mdb --format json
cortexpy validate database.mdb
cortexpy formats  # Shows supported database formats
```

#### Enhanced Help Documentation
- Comprehensive help text for all commands
- Format-specific examples and use cases
- Platform-specific usage notes
- Progress tracking explanations

### 🐛 Fixed

#### NumPy Compatibility
- **Fixed**: `np.float_` deprecated alias issues with NumPy 2.0+
- **Solution**: Global compatibility patches for pandas-access library
- **Impact**: Ensures compatibility with latest NumPy versions

#### Integer Column NA Values
- **Fixed**: "Integer column has NA values in column 16" error in large Access databases
- **Solution**: Implemented fallback reading methods with mdb-export CSV conversion
- **Result**: Large databases (Database1.accdb with 2.3M records) now convert successfully

#### DBF Encoding Detection
- **Fixed**: "'ascii' codec can't decode byte 0x98 in position 16" errors
- **Solution**: Comprehensive upfront encoding detection prioritizing Windows encodings
- **Result**: JE4COR4.DBF (1.48M records) correctly detects cp1252 encoding

#### Table Summary Display
- **Fixed**: Table overview showing 0 records/columns in Stage 4
- **Solution**: Improved table info retrieval with proper error handling
- **Result**: Accurate record and column counts displayed

#### Output Path Generation
- **Enhanced**: Automatic output directory creation for database conversions
- **Format**: `{input_name}_parquet/` for multi-table outputs
- **Behavior**: Preserves source file directory structure

### 📊 Performance & Statistics

#### Conversion Performance
- **Small files** (<10MB): <10 seconds
- **Medium files** (10-100MB): <60 seconds  
- **Large files** (100-500MB): <5 minutes
- **Very large files** (1.4M+ records): Progress tracking with timeouts
- **Memory usage**: Consistently <500MB

#### Throughput Metrics
- **String conversion rate**: 37,000+ records/second
- **Cross-platform consistency**: Verified on Windows/macOS/Linux
- **Compression efficiency**: Average 3-5x size reduction with Snappy
- **Encoding detection**: Optimized with early exit for large files

### 🧪 Testing & Quality

#### Comprehensive Test Suite
- **Unit Tests**: 63+ passing tests across all modules
- **Integration Tests**: Real database file conversion validation
- **Cross-Platform Tests**: Windows/macOS/Linux compatibility verification
- **Performance Tests**: Memory and speed benchmarking
- **Large File Tests**: Database1.accdb (848MB), JE4COR4.DBF (357MB)

#### Code Quality
- **Type Hints**: Comprehensive typing throughout codebase
- **Error Handling**: Robust exception management with user-friendly messages
- **Logging**: Detailed debug information for troubleshooting
- **Documentation**: Extensive docstrings and inline comments

### 📝 Documentation Updates

#### User Documentation
- Updated CLI help with database conversion examples
- Platform-specific installation and setup guides
- Performance optimization recommendations
- Troubleshooting guide for common issues

#### Developer Documentation
- Plugin architecture for adding new database formats
- String conversion rule specifications
- Cross-platform development guidelines
- Testing framework documentation

### 🔮 Next Phase Preview

#### Phase 2: MDF Support (Planned)
- SQL Server MDF file support
- Full data type preservation (non-string output)
- Advanced connection options
- Performance optimizations for large enterprise databases

### 💡 Migration Notes

#### For Existing Users
- All existing PDF conversion functionality preserved
- No breaking changes to existing CLI commands
- New database formats automatically detected and supported

#### For Developers
- New plugin registration system for database converters
- Extended BaseConverter class for database-specific implementations
- Rich terminal UI components available for custom progress displays

---

## [0.1.0] - 2025-06-18

### Added
- **Core Features**
  - PDF to text conversion with PyMuPDF backend
  - Rich CLI interface with Click framework
  - Beautiful terminal output with progress bars
  - File validation and metadata extraction
  - Page range selection for PDF processing
  - Extensible plugin architecture for future format support

- **CLI Commands**
  - `convert` - Convert files between formats with advanced options
  - `info` - Display file metadata in table or JSON format
  - `validate` - Check if files can be processed
  - `formats` - List all supported input/output formats

- **Advanced Features**
  - Automatic output path generation in same directory as input
  - Verbose mode with detailed progress information
  - Force overwrite option for existing files
  - Support for complex filenames with spaces and dots
  - Plugin discovery and loading system

- **Documentation**
  - Comprehensive CLI help system with detailed examples
  - Complete README with usage guide
  - Extensive testing documentation (TESTING.md)
  - Example scripts and demonstrations

- **Development Tools**
  - UV package management with fast dependency resolution
  - Complete test suite with pytest and coverage
  - Code quality tools: Black, Ruff, MyPy
  - Makefile with development and deployment commands
  - PyPI-ready distribution setup

- **Testing Infrastructure**
  - Automated test scripts for local verification
  - Comprehensive test suite with 94% coverage on core functionality
  - Output path behavior testing and validation
  - Cross-platform compatibility testing

### Technical Details
- **Dependencies**: Click 8.0+, Rich 13.0+, PyMuPDF 1.23+, tqdm 4.64+
- **Python Support**: 3.8+
- **Package Format**: Modern pyproject.toml configuration
- **Architecture**: Plugin-based converter system with registry pattern

### Performance
- **Small PDFs** (< 1MB): Near-instant conversion
- **Medium PDFs** (1-10MB): 1-5 seconds with progress tracking
- **Large PDFs** (> 10MB): Efficient streaming with memory management

### Behavior Changes
- Output files are created in the same directory as input files by default
- When no output path specified, preserves original filename with new extension
- Explicit output paths override default behavior
- Verbose mode shows auto-generated output paths

---

## [Unreleased]

### Planned Features
- SQL Server MDF file support (Phase 2)
- Full data type preservation for Phase 2
- Advanced connection options
- Configuration file support
- Additional output formats
- Performance optimizations

---

## Migration Guide

### From Command Line Tools
If you're migrating from other data processing tools:

```bash
# PDF Processing
# Instead of: pdftotext document.pdf output.txt
cortexpy convert document.pdf output.txt

# Database Processing (New in v0.2.0)
cortexpy convert database.mdb --format parquet
cortexpy convert data.dbf --format parquet

# File Information
# Instead of: pdfinfo document.pdf
cortexpy info document.pdf

# New capabilities
cortexpy convert document.pdf --pages "1-5"
cortexpy info database.mdb --format json
cortexpy validate data.dbf
```

### For Developers
The plugin system allows easy extension:

```python
from cortexpy_cli.converters.base import BaseConverter
from cortexpy_cli.plugins import registry

class MyDatabaseConverter(BaseConverter):
    def __init__(self):
        super().__init__()
        self.supported_inputs = {'.mydb'}
        self.supported_outputs = {'.parquet', '.csv'}
    
    def convert(self, input_path, output_path, **options):
        # Your conversion logic here
        return True

# Register the converter
registry.register('my_database_converter', MyDatabaseConverter)
```

## Support

- **Documentation**: See README.md and docs/ directory
- **Issues**: Report bugs and feature requests on GitHub
- **Testing**: Use provided test scripts for local verification
- **Development**: Follow contribution guidelines in the project repository

---

*This release represents a major milestone in CortexPy CLI's evolution, adding comprehensive database conversion capabilities while maintaining the tool's focus on simplicity and performance.*