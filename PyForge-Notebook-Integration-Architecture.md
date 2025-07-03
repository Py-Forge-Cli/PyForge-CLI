# PyForge CLI Notebook Integration Architecture
## Comprehensive Analysis and Technology Options for Databricks Integration

### Executive Summary

This document presents a comprehensive analysis of the PyForge CLI architecture and proposes a robust solution for notebook integration with Databricks capabilities. The proposed architecture includes an optional "databricks" wrapper component that enables specialists to integrate PyForge directly into notebook workflows with intelligent environment detection and format-specific optimization.

---

## 1. Current PyForge CLI Architecture Analysis

### 1.1 Core Architecture Overview

PyForge CLI is built on a sophisticated plugin-based architecture with the following key components:

**Entry Point Structure:**
- **Binary**: `pyforge` (Click-based CLI framework)
- **Version**: 0.5.1 
- **Core Framework**: Click + Rich for enhanced terminal experience

**Primary Commands:**
- `pyforge convert` - Core data format conversion
- `pyforge info` - File metadata extraction  
- `pyforge formats` - Supported format enumeration
- `pyforge validate` - File validation
- `pyforge install` - Component installation (sample-datasets, mdf-tools)
- `pyforge mdf-tools` - SQL Server MDF management

### 1.2 Conversion Architecture

**Plugin System (`src/pyforge_cli/plugins/`):**
- **Registry Pattern**: Central `ConverterRegistry` for format mapping
- **Plugin Loader**: Multi-source discovery (built-in, entry points, directories)
- **Extension Points**: `~/.cortexpy/plugins/` for user plugins

**Converter Framework (`src/pyforge_cli/converters/`):**
- **Base Interface**: `BaseConverter` abstract class
- **Template Method Pattern**: Standardized conversion workflow
- **Strategy Pattern**: Format-specific implementations

**Data Processing Philosophy:**
- **Phase 1 Approach**: Universal string conversion for consistency
- **String Type Converter**: Standardized normalization rules
- **Format Support**: PDF, Excel, XML, CSV, MDB, DBF, Access, SQL Server

### 1.3 Current Format Capabilities

| Input Format | Extensions | Output | Processing Engine |
|--------------|------------|--------|-------------------|
| PDF | `.pdf` | `.txt` | PyMuPDF (text extraction) |
| Excel | `.xlsx` | `.parquet` | openpyxl + intelligent multi-sheet |
| XML | `.xml`, `.xml.gz` | `.parquet` | Custom hierarchical flattening |
| CSV | `.csv`, `.tsv` | `.parquet` | pandas + auto-dialect detection |
| Access | `.mdb`, `.accdb` | `.parquet` | Database table extraction |
| DBF | `.dbf` | `.parquet` | dBase format handling |
| SQL Server | `.mdf` | `.parquet` | Docker-based SQL Server |

---

## 2. Technology Options for Notebook Integration

### 2.1 Core Integration Approaches

#### Option A: Direct API Wrapper (Recommended)
**Architecture**: Create a Python SDK that wraps existing PyForge converters
**Benefits**: 
- Leverages existing codebase
- Maintains consistency with CLI
- Minimal development overhead
- Plugin system reusability

**Implementation Pattern**:
```python
from pyforge_notebook import PyForgeNotebook

forge = PyForgeNotebook()
df = forge.convert_to_dataframe("data.xlsx", target_format="parquet")
```

#### Option B: Jupyter Magic Commands
**Architecture**: IPython magic commands for notebook integration
**Benefits**:
- Native notebook experience
- Cell-level integration
- Progress visualization

**Implementation Pattern**:
```python
%load_ext pyforge_magic
%%pyforge convert data.xlsx --format parquet --output df
```

#### Option C: Hybrid Approach (Optimal)
**Architecture**: Combine API wrapper with optional magic commands
**Benefits**: 
- Flexibility for different user preferences
- Programmatic and interactive interfaces
- Seamless integration paths

### 2.2 Databricks Integration Technologies

#### 2.2.1 Environment Detection Stack
**Primary Detection Methods**:
- **Spark Context Detection**: `pyspark.sql.SparkSession.getActiveSession()`
- **Databricks Runtime**: Environment variable analysis (`DATABRICKS_RUNTIME_VERSION`)
- **Spark Connect Mode**: `spark.conf.get("spark.api.mode")` 
- **Cluster Type**: Shared vs. Single-user detection

#### 2.2.2 Native Databricks Capabilities
**Format-Optimized Processing**:
- **CSV/JSON/XML**: Leverage Spark's native distributed readers
- **Excel/MDB/DBF/PDF**: Fall back to PyForge converters with memory optimization
- **Delta Lake Integration**: Direct write to Delta tables
- **Auto-scaling**: Leverage cluster compute for large files

#### 2.2.3 Databricks Connect Architecture (2024)
**Spark Connect Benefits**:
- **Client-Server Architecture**: Thin client, server-side processing
- **Unified Authentication**: Standard Databricks SDK integration
- **Version Compatibility**: Runtime 13.3+ with feature parity
- **API Consistency**: Seamless switching between Classic and Connect modes

### 2.3 Package Architecture Options

#### Option 1: Monolithic Package with Optional Dependencies
```
pyforge-notebook/
├── core/           # Core PyForge functionality
├── databricks/     # Databricks-specific optimizations
├── jupyter/        # Jupyter magic commands
└── utils/          # Environment detection
```

#### Option 2: Modular Package Ecosystem (Recommended)
```
pyforge-core        # Base conversion functionality
pyforge-notebook    # Notebook integration wrapper
pyforge-databricks  # Databricks optimizations (optional)
```

**Benefits**: 
- User choice in dependencies
- Faster installation for non-Databricks users
- Cleaner separation of concerns
- Better testing isolation

---

## 3. Proposed Architecture: PyForge Databricks Integration

### 3.1 Core Architecture Design

```
┌─────────────────────────────────────────────────────────┐
│                 PyForge Notebook SDK                    │
├─────────────────────────────────────────────────────────┤
│  Environment Detection Layer                            │
│  ├── Databricks Runtime Detection                       │
│  ├── Spark Context Analysis                             │
│  └── Capability Assessment                              │
├─────────────────────────────────────────────────────────┤
│  Format Processing Router                               │
│  ├── Native Databricks (CSV, JSON, XML)                │
│  ├── Hybrid Processing (Excel, PDF)                     │
│  └── PyForge Fallback (MDB, DBF)                        │
├─────────────────────────────────────────────────────────┤
│  Data Integration Layer                                 │
│  ├── Spark DataFrame Output                             │
│  ├── Pandas DataFrame Conversion                        │
│  └── Delta Lake Integration                             │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Environment Detection Algorithm

```python
class EnvironmentDetector:
    def detect_environment(self):
        env = {
            'is_databricks': self._detect_databricks(),
            'spark_available': self._detect_spark(),
            'spark_mode': self._detect_spark_mode(),
            'runtime_version': self._get_databricks_runtime(),
            'cluster_type': self._detect_cluster_type()
        }
        return env
    
    def _detect_databricks(self):
        return (
            'DATABRICKS_RUNTIME_VERSION' in os.environ or
            'SPARK_LOCAL_HOSTNAME' in os.environ or
            self._check_databricks_dbutils()
        )
    
    def _detect_spark_mode(self):
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                return spark.conf.get("spark.api.mode", "classic")
        except ImportError:
            return None
        return None
```

### 3.3 Format-Specific Processing Strategy

#### 3.3.1 Native Databricks Optimization (CSV, JSON, XML)
```python
class DatabricksNativeProcessor:
    def process_csv(self, file_path, **options):
        """Use Spark's native CSV reader for distributed processing"""
        return spark.read.csv(file_path, **self._optimize_csv_options(options))
    
    def process_json(self, file_path, **options):
        """Use Spark's native JSON reader with schema inference"""
        return spark.read.json(file_path, **options)
    
    def process_xml(self, file_path, **options):
        """Use Spark XML library for distributed XML processing"""
        return spark.read.format("xml").load(file_path, **options)
```

#### 3.3.2 Hybrid Processing (Excel, PDF)
```python
class HybridProcessor:
    def process_excel(self, file_path, **options):
        """
        Use PyForge converter but optimize for Databricks memory management
        """
        # Check file size and memory constraints
        if self._should_use_distributed_processing(file_path):
            return self._distributed_excel_processing(file_path, options)
        else:
            return self._pyforge_excel_processing(file_path, options)
    
    def process_pdf(self, file_path, **options):
        """
        Use PyForge PDF converter with Spark DataFrame output
        """
        text_content = self.pyforge_converter.convert(file_path, **options)
        return self._create_spark_dataframe(text_content)
```

#### 3.3.3 PyForge Fallback (MDB, DBF)
```python
class PyForgeFallbackProcessor:
    def process_mdb(self, file_path, **options):
        """Use PyForge converter for unsupported formats"""
        parquet_path = self.pyforge_converter.convert(file_path, **options)
        return spark.read.parquet(parquet_path)
    
    def process_dbf(self, file_path, **options):
        """Process DBF files using PyForge with memory optimization"""
        return self._process_with_memory_management(file_path, options)
```

### 3.4 Integration API Design

#### 3.4.1 Primary Interface
```python
from pyforge_notebook import PyForge

# Initialize with automatic environment detection
forge = PyForge(auto_detect_environment=True)

# Convert with automatic optimization
df = forge.convert(
    "data.xlsx", 
    output_format="spark_dataframe",  # or "pandas", "delta_table"
    databricks_optimize=True
)

# Environment-aware processing
if forge.environment.is_databricks:
    # Use Delta Lake for large datasets
    forge.save_as_delta_table(df, "my_catalog.my_schema.my_table")
else:
    # Standard file output
    df.to_csv("output.csv")
```

#### 3.4.2 Advanced Configuration
```python
# Manual environment configuration
forge = PyForge(
    environment_config={
        'force_databricks_mode': True,
        'spark_config': {
            'spark.sql.adaptive.enabled': True,
            'spark.sql.adaptive.coalescePartitions.enabled': True
        }
    }
)

# Format-specific optimizations
df = forge.convert(
    "large_data.csv",
    processing_strategy="databricks_native",
    spark_options={
        'header': True,
        'inferSchema': True,
        'multiline': True
    }
)
```

---

## 4. Sample Notebook Implementation

### 4.1 Installation and Setup
```python
# Cell 1: Installation
%pip install pyforge-notebook[databricks]

# Cell 2: Basic Setup and Environment Detection
import os
from pyforge_notebook import PyForge, EnvironmentInfo

# Initialize PyForge with automatic environment detection
forge = PyForge()

# Display environment information
env_info = forge.get_environment_info()
print(f"Environment: {env_info.environment_type}")
print(f"Spark Available: {env_info.spark_available}")
print(f"Databricks Runtime: {env_info.databricks_runtime}")
print(f"Cluster Type: {env_info.cluster_type}")
```

### 4.2 Basic Data Conversion Examples
```python
# Cell 3: CSV Processing with Databricks Optimization
csv_df = forge.convert(
    "/FileStore/shared_uploads/data.csv",
    output_format="spark_dataframe",
    auto_optimize=True
)

# Display results
display(csv_df.limit(10))
print(f"Total rows: {csv_df.count()}")
print(f"Schema: {csv_df.schema}")
```

```python
# Cell 4: Excel Multi-Sheet Processing
excel_df = forge.convert(
    "/FileStore/shared_uploads/financial_data.xlsx",
    output_format="spark_dataframe",
    excel_options={
        'combine_sheets': True,
        'sheet_matching_strategy': 'column_signature'
    }
)

# Show sheet analysis
sheet_info = forge.get_last_conversion_metadata()
print("Sheets processed:")
for sheet in sheet_info['sheets']:
    print(f"  - {sheet['name']}: {sheet['rows']} rows, {sheet['columns']} columns")
```

### 4.3 Format-Specific Processing
```python
# Cell 5: PDF Text Extraction
pdf_df = forge.convert(
    "/FileStore/shared_uploads/document.pdf",
    output_format="spark_dataframe",
    pdf_options={
        'page_range': '1-10',
        'extract_metadata': True
    }
)

# Display text content
display(pdf_df.select("page_number", "text_content").limit(5))
```

```python
# Cell 6: XML Hierarchical Data Processing
xml_df = forge.convert(
    "/FileStore/shared_uploads/complex_data.xml",
    output_format="spark_dataframe",
    xml_options={
        'flatten_nested': True,
        'array_detection': True
    }
)

# Show flattened structure
print("Flattened columns:")
for col in xml_df.columns:
    print(f"  - {col}")
```

### 4.4 Advanced Databricks Integration
```python
# Cell 7: Delta Lake Integration
# Convert and save directly to Delta Lake
forge.convert_and_save_delta(
    input_path="/FileStore/shared_uploads/sales_data.xlsx",
    catalog="main",
    schema="sales",
    table="monthly_reports",
    mode="overwrite",
    partition_by=["year", "month"]
)

# Verify Delta table creation
spark.sql("DESCRIBE EXTENDED main.sales.monthly_reports").show()
```

```python
# Cell 8: Batch Processing with Progress Tracking
files_to_convert = [
    "/FileStore/shared_uploads/file1.csv",
    "/FileStore/shared_uploads/file2.xlsx", 
    "/FileStore/shared_uploads/file3.pdf"
]

# Batch conversion with progress bar
results = forge.batch_convert(
    file_paths=files_to_convert,
    output_format="delta_table",
    target_catalog="main",
    target_schema="processed_data",
    show_progress=True
)

# Display batch results
for result in results:
    print(f"File: {result['input_file']}")
    print(f"Status: {result['status']}")
    print(f"Output: {result['output_location']}")
    print(f"Processing time: {result['duration']:.2f}s")
    print("---")
```

### 4.5 CLI Command Equivalents in Notebook
```python
# Cell 9: Replicating CLI Commands in Notebook

# Equivalent to: pyforge info data.xlsx
file_info = forge.get_file_info("/FileStore/shared_uploads/data.xlsx")
print("File Information:")
for key, value in file_info.items():
    print(f"  {key}: {value}")

# Equivalent to: pyforge formats
supported_formats = forge.list_supported_formats()
print("\nSupported Formats:")
for format_info in supported_formats:
    print(f"  {format_info['input']} → {format_info['output']}")

# Equivalent to: pyforge validate data.xlsx
validation_result = forge.validate_file("/FileStore/shared_uploads/data.xlsx")
print(f"\nValidation Result: {validation_result['status']}")
if validation_result['errors']:
    print("Errors:")
    for error in validation_result['errors']:
        print(f"  - {error}")
```

### 4.6 Performance Optimization Examples
```python
# Cell 10: Memory and Performance Optimization
# Configure for large file processing
forge.configure_performance(
    max_memory="8g",
    enable_adaptive_query_execution=True,
    enable_columnar_cache=True,
    partition_strategy="auto"
)

# Process large file with optimization
large_df = forge.convert(
    "/FileStore/shared_uploads/large_dataset.csv",
    output_format="spark_dataframe",
    performance_mode="optimize_for_size",
    cache_intermediate_results=True
)

# Show processing statistics
stats = forge.get_last_conversion_stats()
print(f"Processing time: {stats['duration']:.2f}s")
print(f"Memory usage: {stats['peak_memory_mb']}MB")
print(f"Partitions created: {stats['output_partitions']}")
```

---

## 5. Implementation Roadmap

### Phase 1: Core Integration (Weeks 1-4)
- [ ] Create `pyforge-notebook` package structure
- [ ] Implement environment detection system
- [ ] Build basic API wrapper around existing converters
- [ ] Add Spark DataFrame output support
- [ ] Create simple notebook examples

### Phase 2: Databricks Optimization (Weeks 5-8)
- [ ] Implement native Databricks format processors
- [ ] Add Delta Lake integration
- [ ] Build memory optimization for large files
- [ ] Create batch processing capabilities
- [ ] Add comprehensive error handling

### Phase 3: Advanced Features (Weeks 9-12)
- [ ] Implement Jupyter magic commands
- [ ] Add progress tracking and visualization
- [ ] Build configuration management system
- [ ] Create comprehensive documentation
- [ ] Add performance monitoring and optimization

### Phase 4: Production Ready (Weeks 13-16)
- [ ] Comprehensive testing suite
- [ ] Performance benchmarking
- [ ] Security audit and validation
- [ ] Documentation and examples
- [ ] Community feedback integration

---

## 6. Technology Stack Recommendations

### 6.1 Core Dependencies
```toml
[dependencies]
pyforge-cli = "^0.5.1"
pyspark = "^3.5.0"
databricks-sdk = "^0.18.0"
jupyter = "^1.0.0"
ipython = "^8.0.0"
pandas = "^2.0.0"
pyarrow = "^14.0.0"

[optional-dependencies]
databricks = [
    "databricks-connect",
    "delta-spark",
    "mlflow"
]
visualization = [
    "plotly",
    "seaborn", 
    "matplotlib"
]
```

### 6.2 Architecture Patterns
- **Plugin Architecture**: Leverage existing PyForge plugin system
- **Adapter Pattern**: Wrap CLI functionality for notebook consumption
- **Strategy Pattern**: Environment-specific processing strategies  
- **Factory Pattern**: Dynamic converter creation based on environment
- **Observer Pattern**: Progress tracking and event handling

### 6.3 Testing Strategy
- **Unit Tests**: Individual converter functionality
- **Integration Tests**: End-to-end notebook workflows
- **Performance Tests**: Large file processing benchmarks
- **Environment Tests**: Databricks and local Jupyter testing
- **Compatibility Tests**: Multiple Python and Spark versions

---

## 7. Conclusion

The proposed PyForge notebook integration architecture provides a robust, scalable solution that:

1. **Preserves PyForge's Core Strengths**: Leverages existing conversion algorithms and plugin architecture
2. **Optimizes for Databricks**: Intelligent environment detection and native capability utilization
3. **Maintains Flexibility**: Supports both local Jupyter and cloud Databricks environments
4. **Ensures Performance**: Smart routing of processing based on file formats and cluster capabilities
5. **Enables Scalability**: Distributed processing for supported formats, efficient fallback for others

This architecture positions PyForge as a comprehensive data processing solution that seamlessly integrates with modern notebook workflows while maintaining its sophisticated conversion capabilities.

The modular package design (`pyforge-core`, `pyforge-notebook`, `pyforge-databricks`) ensures users can choose their integration level while maintaining clean separation of concerns and optimal installation sizes.

Implementation should begin with Phase 1 to establish the foundation, then progressively add Databricks optimizations and advanced features based on user feedback and adoption patterns.