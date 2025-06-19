# CortexPy CLI - Change Log

## [Version 0.2.0] - 2025-06-18

### 🎉 Major Feature: MDB/DBF to Parquet Conversion

**Phase 1 Implementation Complete** - Full MDB (Microsoft Access) and DBF (dBase) file conversion support with string-only output.

### ✨ New Features

#### Database File Support
- **MDB/ACCDB Conversion**: Full Microsoft Access database conversion support
  - Cross-platform compatibility (Windows/macOS/Linux)
  - Password-protected file detection (Windows ODBC + mdbtools fallback)
  - System table filtering (excludes MSys* tables)
  - Multi-table batch conversion

- **DBF Conversion**: Complete dBase file format support
  - All DBF versions supported via dbfread library
  - Memo field processing (.dbt/.fpt files)
  - Character encoding detection
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

### 🔧 Technical Improvements

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

### 🐛 Bug Fixes

#### NumPy Compatibility
- **Fixed**: `np.float_` deprecated alias issues with NumPy 2.0+
- **Solution**: Global compatibility patches for pandas-access library
- **Impact**: Ensures compatibility with latest NumPy versions

#### Table Summary Display
- **Fixed**: Table overview showing 0 records/columns
- **Solution**: Improved table info retrieval with proper error handling
- **Result**: Accurate record and column counts in Stage 4 display

#### Output Path Generation
- **Enhanced**: Automatic output directory creation for database conversions
- **Format**: `{input_name}_parquet/` for multi-table outputs
- **Behavior**: Preserves source file directory structure

### 📊 Performance & Statistics

#### Conversion Performance
- **Small files** (<10MB): <10 seconds
- **Medium files** (10-100MB): <60 seconds  
- **Large files** (100-500MB): <5 minutes
- **Memory usage**: Consistently <500MB

#### Throughput Metrics
- **String conversion rate**: 37,000+ records/second
- **Cross-platform consistency**: Verified on Windows/macOS/Linux
- **Compression efficiency**: Average 3-5x size reduction with Snappy

### 🧪 Testing & Quality

#### Comprehensive Test Suite
- **Unit Tests**: 63+ passing tests across all modules
- **Integration Tests**: Real database file conversion validation
- **Cross-Platform Tests**: Windows/macOS/Linux compatibility verification
- **Performance Tests**: Memory and speed benchmarking

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

## Previous Versions

### [Version 0.1.0] - Initial Release
- PDF to text conversion
- Basic CLI interface
- Plugin architecture foundation
- Cross-platform compatibility

---

*This release represents a major milestone in CortexPy CLI's evolution, adding comprehensive database conversion capabilities while maintaining the tool's focus on simplicity and performance.*