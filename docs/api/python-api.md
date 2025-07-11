# Python API Reference

PyForge CLI v1.0.9 provides a comprehensive Python API for programmatic access to all conversion functionality, including specialized support for Databricks environments.

## Core Classes

### BaseConverter

The foundation class for all format converters.

```python
from pyforge_cli.converters.base import BaseConverter
from pathlib import Path
from typing import Any, Dict, Optional

class BaseConverter(ABC):
    """Abstract base class for all format converters."""
    
    def __init__(self):
        self.supported_inputs: set = set()
        self.supported_outputs: set = set()
    
    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """Convert input file to output format."""
        pass
    
    def validate_input(self, input_path: Path) -> bool:
        """Validate if input file can be processed."""
        pass
    
    def get_output_extension(self, output_format: str) -> str:
        """Get appropriate file extension for output format."""
        pass
    
    def get_metadata(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from input file."""
        pass
```

### ConverterRegistry

Manages and provides access to all registered converters.

```python
from pyforge_cli.plugins.registry import ConverterRegistry
from pathlib import Path
from typing import Optional

class ConverterRegistry:
    """Registry for managing format converters."""
    
    def register(self, name: str, converter_class: Type[BaseConverter]) -> None:
        """Register a converter class."""
        pass
    
    def get_converter(self, input_path: Path) -> Optional[BaseConverter]:
        """Get appropriate converter for input file."""
        pass
    
    def list_converters(self) -> Dict[str, Type[BaseConverter]]:
        """List all registered converters."""
        pass
```

## Database Backend API

### DatabaseBackend

Abstract base class for database connection backends.

```python
from pyforge_cli.backends.base import DatabaseBackend
from typing import List
import pandas as pd

class DatabaseBackend(ABC):
    """Abstract base class for database connection backends."""
    
    def is_available(self) -> bool:
        """Check if backend dependencies are available."""
        pass
    
    def connect(self, db_path: str, password: str = None) -> bool:
        """Connect to database."""
        pass
    
    def list_tables(self) -> List[str]:
        """List all readable tables in the database."""
        pass
    
    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read table data as DataFrame."""
        pass
    
    def close(self):
        """Close database connection and cleanup resources."""
        pass
```

### UCanAccessSubprocessBackend

**New in v1.0.9**: Subprocess-based backend for Databricks Serverless compatibility.

```python
from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend
from pathlib import Path
from typing import List
import pandas as pd

class UCanAccessSubprocessBackend(DatabaseBackend):
    """UCanAccess backend using subprocess for Databricks Serverless compatibility."""
    
    def __init__(self):
        """Initialize subprocess backend."""
        self.logger = logging.getLogger(__name__)
        self.jar_manager = UCanAccessJARManager()
        self.db_path = None
        self._temp_file_path = None
        self._tables_cache = None
    
    def is_available(self) -> bool:
        """Check if subprocess UCanAccess backend is available.
        
        Returns:
            True if Java is available via subprocess, False otherwise
        """
        pass
    
    def connect(self, db_path: str, password: str = None) -> bool:
        """Connect to Access database (prepare for subprocess operations).
        
        Args:
            db_path: Path to Access database file (supports Unity Catalog volumes)
            password: Optional password (not supported in subprocess mode)
            
        Returns:
            True if file is accessible, False otherwise
        """
        pass
    
    def list_tables(self) -> List[str]:
        """List all user tables using Java subprocess.
        
        Returns:
            List of table names, or empty list on error
        """
        pass
    
    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read table data using Java subprocess to export to CSV.
        
        Args:
            table_name: Name of table to read
            
        Returns:
            DataFrame containing table data
        """
        pass
    
    def get_connection_info(self) -> dict:
        """Get information about the current connection.
        
        Returns:
            Dictionary with connection information
        """
        pass
```

## Databricks Environment API

### DatabricksEnvironment

**New in v1.0.9**: Comprehensive Databricks environment detection and management.

```python
from pyforge_cli.databricks.environment import DatabricksEnvironment, detect_databricks_environment
from typing import Any, Dict, Optional

class DatabricksEnvironment:
    """Class representing a Databricks environment."""
    
    def __init__(self, env_vars: Dict[str, str], is_databricks: bool = False, version: str = None):
        """Initialize Databricks environment.
        
        Args:
            env_vars: Environment variables
            is_databricks: Whether running in Databricks
            version: Databricks runtime version
        """
        pass
    
    @property
    def is_databricks(self) -> bool:
        """Check if running in Databricks environment."""
        pass
    
    @property
    def version(self) -> Optional[str]:
        """Get Databricks runtime version."""
        pass
    
    def is_serverless(self) -> bool:
        """Check if running in Databricks serverless environment."""
        pass
    
    @property
    def cluster_id(self) -> Optional[str]:
        """Get Databricks cluster ID."""
        pass
    
    @property
    def workspace_id(self) -> Optional[str]:
        """Get Databricks workspace ID."""
        pass
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information."""
        pass

# Utility functions
def detect_databricks_environment() -> DatabricksEnvironment:
    """Detect if running in Databricks environment."""
    pass

def is_running_in_databricks() -> bool:
    """Simple check if running in Databricks environment."""
    pass

def is_running_in_serverless() -> bool:
    """Check if running in Databricks serverless environment."""
    pass
```

## Unity Catalog Volume Path Utilities

**New in v1.0.9**: Built-in support for Unity Catalog volume paths.

```python
# Unity Catalog volume path detection
def is_unity_catalog_path(path: str) -> bool:
    """Check if path is a Unity Catalog volume path.
    
    Args:
        path: File path to check
        
    Returns:
        True if path starts with /Volumes/
    """
    return path.startswith("/Volumes/")

# Example usage in UCanAccessSubprocessBackend
if db_path.startswith("/Volumes/"):
    # Handle Unity Catalog volume paths
    # Copy to local storage for Java access
    import tempfile
    temp_dir = tempfile.gettempdir()
    file_name = os.path.basename(db_path)
    local_path = os.path.join(temp_dir, f"pyforge_{os.getpid()}_{file_name}")
    
    # Copy from volume to local storage
    copy_cmd = f"cp '{db_path}' '{local_path}'"
    result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True, timeout=60)
```

## Dependency Checker API

Utility for checking system dependencies.

```python
from pyforge_cli.utils.dependency_checker import DependencyChecker
from typing import Tuple, Optional

class DependencyChecker:
    """Check and validate dependencies for database backends."""
    
    def check_java(self) -> Tuple[bool, Optional[str]]:
        """Check if Java runtime is available.
        
        Returns:
            Tuple of (is_available, version_string)
        """
        pass
    
    def check_jaydebeapi(self) -> Tuple[bool, Optional[str]]:
        """Check if JayDeBeApi is available.
        
        Returns:
            Tuple of (is_available, version_string)
        """
        pass
```

## Usage Examples

### Basic Conversion

```python
from pyforge_cli.plugins.registry import ConverterRegistry
from pyforge_cli.plugins.loader import load_plugins
from pathlib import Path

# Load all plugins
load_plugins()

# Get registry
registry = ConverterRegistry()

# Convert a file
input_path = Path("data.xlsx")
output_path = Path("data.parquet")

converter = registry.get_converter(input_path)
if converter:
    success = converter.convert(input_path, output_path)
    print(f"Conversion {'successful' if success else 'failed'}")
```

### Databricks Environment Detection

```python
from pyforge_cli.databricks.environment import detect_databricks_environment

# Detect environment
env = detect_databricks_environment()

if env.is_databricks:
    print(f"Running in Databricks {env.version}")
    if env.is_serverless():
        print("Serverless environment detected")
        # Use subprocess backend for MDB files
        from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend
        backend = UCanAccessSubprocessBackend()
    else:
        print("Classic cluster environment")
else:
    print("Not running in Databricks")
```

### Unity Catalog Volume File Processing

```python
from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend
from pathlib import Path

# Process file from Unity Catalog volume
volume_path = "/Volumes/catalog/schema/volume/database.mdb"
backend = UCanAccessSubprocessBackend()

if backend.is_available():
    # Connect handles volume path automatically
    if backend.connect(volume_path):
        tables = backend.list_tables()
        print(f"Found tables: {tables}")
        
        # Read table data
        if tables:
            df = backend.read_table(tables[0])
            print(f"Read {len(df)} rows from {tables[0]}")
        
        backend.close()
```

### Databricks Serverless Integration

```python
from pyforge_cli.converters.enhanced_mdb_converter import EnhancedMDBConverter
from pyforge_cli.databricks.environment import is_running_in_serverless
from pathlib import Path

# Enhanced MDB conversion in Databricks Serverless
if is_running_in_serverless():
    # Install required packages with proper index URL
    import subprocess
    cmd = [
        "pip", "install", 
        "/Volumes/catalog/schema/volume/pyforge-cli-1.0.9-py3-none-any.whl",
        "--no-cache-dir", "--quiet",
        "--index-url", "https://pypi.org/simple/",
        "--trusted-host", "pypi.org"
    ]
    subprocess.run(cmd, check=True)
    
    # Use enhanced converter with subprocess backend
    converter = EnhancedMDBConverter()
    
    # Convert Unity Catalog volume file
    volume_mdb = Path("/Volumes/catalog/schema/volume/database.mdb")
    output_dir = Path("/Volumes/catalog/schema/volume/output/")
    
    success = converter.convert(volume_mdb, output_dir)
    print(f"Conversion {'successful' if success else 'failed'}")
```

### Error Handling and Logging

```python
import logging
from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use backend with error handling
backend = UCanAccessSubprocessBackend()

try:
    if not backend.is_available():
        logger.error("Backend not available")
        exit(1)
    
    if not backend.connect("/path/to/database.mdb"):
        logger.error("Failed to connect to database")
        exit(1)
    
    # Get connection info
    info = backend.get_connection_info()
    logger.info(f"Connected using: {info['method']}")
    
    # Process tables
    tables = backend.list_tables()
    for table in tables:
        try:
            df = backend.read_table(table)
            logger.info(f"Read {len(df)} rows from {table}")
        except Exception as e:
            logger.error(f"Failed to read table {table}: {e}")
    
except Exception as e:
    logger.error(f"Error: {e}")
finally:
    backend.close()
```

## Class Hierarchy

```
BaseConverter
├── CSVConverter
├── ExcelConverter
├── PDFConverter
├── XMLConverter
├── DBFConverter
└── MDBConverter
    └── EnhancedMDBConverter

DatabaseBackend
├── PyODBCBackend
├── UCanAccessBackend
└── UCanAccessSubprocessBackend (v1.0.9)

DatabricksEnvironment (v1.0.9)
├── Environment detection
├── Serverless identification
└── Runtime version parsing
```

## Version 1.0.9 New Features

1. **Subprocess Backend**: `UCanAccessSubprocessBackend` for Databricks Serverless compatibility
2. **Environment Detection**: `DatabricksEnvironment` class with comprehensive detection
3. **Unity Catalog Support**: Built-in volume path handling for `/Volumes/` paths
4. **Serverless Optimization**: Automatic environment detection and backend selection
5. **Enhanced Error Handling**: Improved logging and error reporting
6. **JAR Management**: Automatic JAR file discovery and management

## Error Handling

All API methods use proper exception handling:

```python
try:
    converter = registry.get_converter(input_path)
    if converter:
        success = converter.convert(input_path, output_path)
    else:
        raise ValueError(f"No converter found for {input_path}")
except Exception as e:
    logger.error(f"Conversion failed: {e}")
    raise
```

## Next Steps

- [CLI Reference](../reference/cli-reference.md) - Complete command documentation
- [Converters](../converters/index.md) - Format-specific conversion guides
- [Tutorials](../tutorials/index.md) - Real-world examples
- [Databricks Integration](../databricks/index.md) - Databricks-specific features