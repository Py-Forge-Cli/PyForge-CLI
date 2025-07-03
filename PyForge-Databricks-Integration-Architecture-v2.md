# PyForge Databricks Integration Architecture v2
## Modular Package Ecosystem with Databricks SDK Integration

### Executive Summary

This document presents the revised architecture for PyForge's Databricks integration using a modular two-package ecosystem. The design focuses on seamless Databricks Volumes integration, serverless compute optimization, and maintains compatibility with Databricks SDK pinned versions for production stability.

---

## 1. Architecture Overview

### 1.1 Package Structure

**Modular Ecosystem Design:**

```
pyforge-core (v0.6.0)
├── Core conversion functionality
├── Plugin architecture
├── Base converters
└── CLI interface

pyforge-databricks (v0.1.0)
├── Databricks environment detection
├── Volume file system operations
├── Distributed processing optimizations
├── SDK integration layer
└── Serverless compute adaptations
```

### 1.2 Key Design Principles

1. **Separation of Concerns**: Core functionality remains independent of Databricks
2. **Optional Dependencies**: Databricks features available only when needed
3. **SDK-First Approach**: Leverage Databricks SDK for all platform operations
4. **Volume-Native**: Direct integration with Unity Catalog Volumes
5. **Serverless Optimized**: Auto-detection and optimization for serverless compute

---

## 2. Databricks SDK Integration

### 2.1 Supported SDK Operations

**File System Operations via WorkspaceClient.files:**
- Read files from Volumes
- Write files to Volumes
- List directory contents
- Check file existence
- Get file metadata

**Volume Management via WorkspaceClient.volumes:**
- Create/manage volumes
- List available volumes
- Access volume metadata

### 2.2 Library Versions (Pinned for Stability)

Based on Databricks Serverless Environment Version 2:

```toml
[dependencies]
databricks-sdk = "==0.36.0"
pyspark = "==3.5.0"  # Pre-installed in serverless
pandas = "==1.5.3"
pyarrow = "==14.0.1"
numpy = "==1.23.5"
```

### 2.3 Volume Path Formats

```python
# Unity Catalog Volume paths
volume_path = "/Volumes/catalog_name/schema_name/volume_name/path/to/file"

# DBFS paths (CLI operations)
dbfs_path = "dbfs:/Volumes/catalog_name/schema_name/volume_name/path/to/file"

# Direct cloud storage (external volumes)
cloud_path = "s3://bucket/prefix" # or "abfss://container@account.dfs.core.windows.net/path"
```

---

## 3. Package Architecture Details

### 3.1 pyforge-core

**Purpose**: Maintains all core conversion functionality without Databricks dependencies

```python
# pyforge_core/__init__.py
from .converters import BaseConverter
from .plugins import ConverterRegistry, PluginLoader
from .cli import cli

__version__ = "0.6.0"

# Core API remains unchanged
class PyForgeCore:
    def __init__(self):
        self.registry = ConverterRegistry()
        self.loader = PluginLoader()
        self.loader.load_all()
    
    def convert(self, input_path, output_path, **options):
        """Core conversion method"""
        converter = self.registry.get_converter(input_path)
        return converter.convert(input_path, output_path, **options)
```

### 3.2 pyforge-databricks

**Purpose**: Adds Databricks-specific optimizations and Volume integration

```python
# pyforge_databricks/__init__.py
from databricks.sdk import WorkspaceClient
from .environment import DatabricksEnvironment
from .volume_handler import VolumeHandler
from .distributed_processor import DistributedProcessor

__version__ = "0.1.0"

class PyForgeDatabricks:
    def __init__(self, workspace_client=None):
        self.w = workspace_client or WorkspaceClient()
        self.env = DatabricksEnvironment()
        self.volume_handler = VolumeHandler(self.w)
        self.processor = DistributedProcessor(self.w, self.env)
    
    def convert(self, input_path, output_path=None, **options):
        """Convert files with automatic Volume detection and optimization
        
        Args:
            input_path: Input file path (local or Volume path)
            output_path: Output file path (optional, auto-generated if not provided)
            **options: Conversion options including format_options
        """
        # Detect if paths are Volume paths
        input_is_volume = self._is_volume_path(input_path)
        output_is_volume = self._is_volume_path(output_path) if output_path else input_is_volume
        
        # Auto-generate output path if not provided
        if not output_path:
            output_path = self._generate_output_path(input_path, options.get('output_format', 'parquet'))
        
        # Route to appropriate processing
        if self.env.is_serverless and input_is_volume:
            return self._serverless_optimized_convert(input_path, output_path, **options)
        else:
            return self._standard_convert(input_path, output_path, **options)
```

---

## 4. Environment Detection and Optimization

### 4.1 Serverless Environment Detection

```python
class DatabricksEnvironment:
    def __init__(self):
        self.is_databricks = self._detect_databricks()
        self.is_serverless = self._detect_serverless()
        self.runtime_version = self._get_runtime_version()
        self.environment_version = self._get_environment_version()
    
    def _detect_databricks(self):
        return any([
            'DATABRICKS_RUNTIME_VERSION' in os.environ,
            'SPARK_LOCAL_HOSTNAME' in os.environ,
            self._check_spark_session()
        ])
    
    def _detect_serverless(self):
        # Serverless detection based on compute type
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                compute_type = spark.conf.get("spark.databricks.compute.type", "")
                return compute_type == "serverless"
        except:
            pass
        return False
    
    def _get_environment_version(self):
        # Detect serverless environment version (1 or 2)
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor == 11:
            return 2  # Environment v2 uses Python 3.11
        elif python_version.major == 3 and python_version.minor == 10:
            return 1  # Environment v1 uses Python 3.10
        return None
```

### 4.2 Processing Strategy Selection

```python
class ProcessingStrategySelector:
    def __init__(self, environment):
        self.env = environment
    
    def get_strategy(self, file_format):
        """Select optimal processing strategy based on format and environment"""
        
        # Native Databricks processing for supported formats
        if self.env.is_databricks and file_format in ['.csv', '.json', '.xml', '.parquet']:
            if self.env.is_serverless:
                return 'serverless_native'
            else:
                return 'databricks_native'
        
        # Hybrid processing for Excel (use PyForge parsing, Spark output)
        elif self.env.is_databricks and file_format == '.xlsx':
            return 'hybrid_excel'
        
        # PyForge converters for specialized formats
        elif file_format in ['.pdf', '.mdb', '.dbf']:
            return 'pyforge_converter'
        
        # Default pandas processing
        else:
            return 'pandas_local'
```

---

## 5. Volume File Operations

### 5.1 Volume Handler Implementation

```python
class VolumeHandler:
    def __init__(self, workspace_client):
        self.w = workspace_client
    
    def read_file(self, volume_path):
        """Read file from Unity Catalog Volume"""
        # Use WorkspaceClient.files API
        with self.w.files.download(volume_path) as f:
            return f.read()
    
    def write_file(self, volume_path, content):
        """Write file to Unity Catalog Volume"""
        # Use WorkspaceClient.files API
        self.w.files.upload(volume_path, content)
    
    def list_files(self, volume_path):
        """List files in Volume directory"""
        return list(self.w.files.list(volume_path))
    
    def file_exists(self, volume_path):
        """Check if file exists in Volume"""
        try:
            self.w.files.get_status(volume_path)
            return True
        except:
            return False
    
    def get_volume_info(self, catalog, schema, volume):
        """Get Volume metadata"""
        return self.w.volumes.read(f"{catalog}.{schema}.{volume}")
```

### 5.2 Direct Volume-to-Volume Processing

```python
class VolumeProcessor:
    def __init__(self, workspace_client, environment):
        self.w = workspace_client
        self.env = environment
        self.volume_handler = VolumeHandler(workspace_client)
    
    def process_in_volume(self, input_volume_path, output_volume_path, format_options):
        """Process files directly between Volumes without local downloads"""
        
        # For supported formats, use Spark direct read/write
        if self._can_use_spark_direct(input_volume_path):
            spark = SparkSession.getActiveSession()
            
            # Read directly from Volume
            df = self._read_with_spark(spark, input_volume_path, format_options)
            
            # Process if needed
            df = self._apply_transformations(df, format_options)
            
            # Write directly to Volume
            self._write_with_spark(df, output_volume_path, format_options)
            
            return output_volume_path
        
        # For unsupported formats, use streaming approach
        else:
            return self._process_with_streaming(input_volume_path, output_volume_path, format_options)
```

---

## 6. Folder Structure for Modular Packages

### 6.1 pyforge-core Package Structure

```
pyforge-core/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── pyforge_core/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py
│       ├── converters/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── csv_converter.py
│       │   ├── excel_converter.py
│       │   ├── pdf_converter.py
│       │   ├── xml_converter.py
│       │   ├── mdb_converter.py
│       │   └── dbf_converter.py
│       ├── plugins/
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   └── loader.py
│       └── utils/
│           ├── __init__.py
│           └── string_converter.py
├── tests/
│   ├── __init__.py
│   └── test_converters.py
└── .github/
    └── workflows/
        └── publish-core.yml
```

### 6.2 pyforge-databricks Package Structure

```
pyforge-databricks/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── pyforge_databricks/
│       ├── __init__.py
│       ├── environment/
│       │   ├── __init__.py
│       │   ├── detector.py
│       │   └── serverless.py
│       ├── volume/
│       │   ├── __init__.py
│       │   ├── handler.py
│       │   └── processor.py
│       ├── distributed/
│       │   ├── __init__.py
│       │   ├── spark_processor.py
│       │   └── optimizations.py
│       ├── converters/
│       │   ├── __init__.py
│       │   ├── databricks_csv.py
│       │   ├── databricks_json.py
│       │   ├── databricks_xml.py
│       │   └── databricks_parquet.py
│       └── integration/
│           ├── __init__.py
│           └── pyforge_bridge.py
├── tests/
│   ├── __init__.py
│   ├── test_environment.py
│   └── test_volume_operations.py
├── examples/
│   ├── basic_conversion.py
│   ├── volume_operations.py
│   └── serverless_optimization.py
└── .github/
    └── workflows/
        └── publish-databricks.yml
```

---

## 7. Package Configuration Files

### 7.1 pyforge-core/pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "pyforge-core"
version = "0.6.0"
description = "Core data format conversion functionality for PyForge"
authors = [{name = "PyForge Team"}]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.8"
dependencies = [
    "click>=8.0.0",
    "rich>=10.0.0",
    "pandas==1.5.3",
    "pyarrow==14.0.1",
    "openpyxl>=3.0.0",
    "pymupdf>=1.23.0",
    "chardet>=4.0.0",
]

[project.scripts]
pyforge = "pyforge_core.cli.main:cli"

[project.entry-points."pyforge.converters"]
csv = "pyforge_core.converters.csv_converter:CSVConverter"
excel = "pyforge_core.converters.excel_converter:ExcelConverter"
pdf = "pyforge_core.converters.pdf_converter:PDFConverter"
xml = "pyforge_core.converters.xml_converter:XMLConverter"
mdb = "pyforge_core.converters.mdb_converter:MDBConverter"
dbf = "pyforge_core.converters.dbf_converter:DBFConverter"
```

### 7.2 pyforge-databricks/pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "pyforge-databricks"
version = "0.1.0"
description = "Databricks integration for PyForge with Volume support"
authors = [{name = "PyForge Team"}]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"  # Minimum for serverless v1
dependencies = [
    "pyforge-core>=0.6.0",
    "databricks-sdk==0.36.0",
    "pyspark>=3.5.0",  # Will use pre-installed in serverless
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-mock>=3.0.0",
    "black>=22.0.0",
    "ruff>=0.1.0",
]

[project.entry-points."pyforge.extensions"]
databricks = "pyforge_databricks:PyForgeDatabricks"
```

---

## 8. Installation and Usage

### 8.1 Installation Options

```bash
# Option 1: Core only (for non-Databricks environments)
pip install pyforge-core

# Option 2: Core + Databricks integration
pip install pyforge-core pyforge-databricks

# Option 3: From source with development dependencies
pip install -e ".[dev]"
```

### 8.2 Usage Examples

**Basic CLI Usage (unchanged):**
```bash
pyforge convert data.csv output.parquet
pyforge info document.pdf
pyforge formats
```

**Databricks Volume Integration (Python):**
```python
from pyforge_databricks import PyForgeDatabricks

# Initialize with automatic environment detection
forge = PyForgeDatabricks()

# Convert file with automatic Volume detection
forge.convert(
    input_path="/Volumes/main/bronze/raw_data/sales.csv",
    output_path="/Volumes/main/silver/processed/sales.parquet",
    format_options={
        'compression': 'snappy',
        'partition_by': ['year', 'month']
    }
)

# Direct conversion with Volume paths
forge.convert(
    "/Volumes/main/bronze/data.xlsx",
    "/Volumes/main/silver/processed.parquet",
    excel_options={'combine_sheets': True}
)

# Or with auto-generated output path
result = forge.convert(
    "/Volumes/main/bronze/data.csv",
    output_format="parquet"
)
```

---

## 9. Benefits of Modular Architecture

1. **Clean Separation**: Core functionality independent of cloud platforms
2. **Reduced Dependencies**: Users only install what they need
3. **Easier Testing**: Each package can be tested independently
4. **Version Management**: Independent versioning for core and extensions
5. **Platform Flexibility**: Easy to add AWS, GCP, or other platform support
6. **Backward Compatibility**: Core API remains stable across versions

---

## 10. Migration Path

For existing PyForge users:

```bash
# Step 1: Update to new package structure
pip uninstall pyforge-cli
pip install pyforge-core

# Step 2: Add Databricks support if needed
pip install pyforge-databricks

# Step 3: Update imports in code
# Old: from pyforge_cli import PyForge
# New: from pyforge_core import PyForgeCore
#      from pyforge_databricks import PyForgeDatabricks
```

---

## 11. Future Extensibility

The modular architecture enables future platform-specific packages:

```
pyforge-aws/          # S3 and EMR optimizations
pyforge-gcp/          # GCS and Dataproc support
pyforge-azure/        # Azure Storage and Synapse integration
pyforge-snowflake/    # Snowflake native processing
```

Each package would follow the same pattern:
- Depend on pyforge-core
- Add platform-specific optimizations
- Maintain consistent API
- Use platform SDK with pinned versions