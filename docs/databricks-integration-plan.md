# Databricks Integration Plan for CortexPy-CLI (PyForge)

## Executive Summary

This document outlines a comprehensive plan to enable CortexPy-CLI (PyForge) to work seamlessly within Databricks notebooks and perform file conversions using Unity Catalog volumes (`dbfs:/Volumes/` paths). The current CLI tool has zero existing Databricks functionality but provides an excellent architectural foundation for integration.

## Current State Analysis

### CLI Tool Architecture
- **Entry Point**: `pyforge` command via Click framework
- **Core Functionality**: Converts 8+ file formats (PDF, Excel, XML, Access, DBF, MDF, CSV) to Parquet
- **Architecture**: Plugin-based converter system with `BaseConverter` abstract class
- **Dependencies**: Rich ecosystem including pandas, pyarrow, docker, requests
- **Notable Gap**: No cloud storage integration currently exists

### Databricks Environment Requirements
- **Installation Method**: Wheel files via `%pip install` in notebooks
- **Storage Access**: Unity Catalog volumes (`/Volumes/catalog/schema/volume/path`)
- **Path Schemes**: Both POSIX (`/Volumes/...`) and DBFS (`dbfs:/Volumes/...`) supported
- **Python Environment**: Databricks Runtime 13.3+ recommended for full volume support

## Implementation Strategy

### Phase 1: Foundation Setup (Week 1-2)

#### 1.1 Add Databricks Dependencies
```toml
# pyproject.toml additions
[project.dependencies]
databricks-sdk = ">=0.20.0"
# Alternative: databricks-cli if REST API approach preferred
```

#### 1.2 Create Storage Abstraction Layer
**New File**: `src/pyforge_cli/storage/databricks_adapter.py`
```python
class DatabricksStorageAdapter:
    """Handles Unity Catalog volume operations for file conversion"""
    
    def __init__(self, workspace_url: str = None, token: str = None):
        # Initialize Databricks SDK client
        
    def download_file(self, dbfs_path: str, local_path: Path) -> bool:
        """Download file from Unity Catalog volume to local temp"""
        
    def upload_file(self, local_path: Path, dbfs_path: str) -> bool:
        """Upload converted file to Unity Catalog volume"""
        
    def list_files(self, dbfs_path: str) -> List[str]:
        """List files in Unity Catalog volume directory"""
        
    def exists(self, dbfs_path: str) -> bool:
        """Check if file exists in Unity Catalog volume"""
```

#### 1.3 Extend Base Converter
**Modified File**: `src/pyforge_cli/converters/base.py`
```python
class BaseConverter(ABC):
    def __init__(self, storage_adapter: Optional[StorageAdapter] = None):
        self.storage_adapter = storage_adapter
        
    def convert_cloud(self, input_path: str, output_path: str, **options) -> bool:
        """New method for cloud-based conversions"""
        # Download → Convert → Upload pattern
```

### Phase 2: CLI Integration (Week 2-3)

#### 2.1 Add Databricks Command Group
**New File**: `src/pyforge_cli/commands/databricks.py`
```python
@click.group()
def databricks():
    """Databricks-specific commands"""
    pass

@databricks.command()
@click.argument('input_path')
@click.argument('output_path') 
@click.option('--workspace-url', envvar='DATABRICKS_HOST')
@click.option('--token', envvar='DATABRICKS_TOKEN')
def convert(input_path, output_path, workspace_url, token):
    """Convert files using Unity Catalog volumes"""
    # Implementation using DatabricksStorageAdapter
```

#### 2.2 Update Main CLI
**Modified File**: `src/pyforge_cli/main.py`
```python
from .commands.databricks import databricks

@click.group()
def cli():
    pass

cli.add_command(databricks)  # Add databricks command group
```

### Phase 3: Notebook Integration (Week 3-4)

#### 3.1 Create Notebook Helper Module
**New File**: `src/pyforge_cli/notebook/helpers.py`
```python
def convert_in_notebook(
    input_path: str,
    output_path: str = None,
    format_type: str = "auto",
    **conversion_options
) -> str:
    """
    Simplified function for notebook usage
    
    Args:
        input_path: Unity Catalog volume path (e.g., '/Volumes/catalog/schema/volume/file.xlsx')
        output_path: Optional output path (auto-generated if None)
        format_type: Target format (default: 'parquet')
        
    Returns:
        Path to converted file
    """
    # Auto-detect if running in Databricks environment
    if is_databricks_environment():
        return convert_with_databricks_adapter(input_path, output_path, **conversion_options)
    else:
        # Fallback to local conversion
        return convert_local(input_path, output_path, **conversion_options)
```

#### 3.2 Create Installation Helper
**New File**: `src/pyforge_cli/installers/databricks_installer.py`
```python
class DatabricksInstaller:
    """Handles Databricks CLI setup and authentication"""
    
    def install_databricks_cli(self):
        """Install Databricks CLI if not present"""
        
    def configure_authentication(self):
        """Guide user through authentication setup"""
        
    def test_connection(self):
        """Verify connectivity to Databricks workspace"""
```

### Phase 4: Enhanced Integration (Week 4-5)

#### 4.1 Add Batch Processing Support
```python
def batch_convert_folder(
    input_folder: str,  # '/Volumes/catalog/schema/volume/input/'
    output_folder: str,  # '/Volumes/catalog/schema/volume/output/'
    file_pattern: str = "*",
    format_type: str = "parquet"
) -> List[str]:
    """Convert all matching files in a Unity Catalog folder"""
```

#### 4.2 Add Configuration Management
**New File**: `src/pyforge_cli/config/databricks_config.py`
```python
class DatabricksConfig:
    """Manage Databricks connection settings"""
    
    def load_from_environment(self):
        """Load from DATABRICKS_HOST, DATABRICKS_TOKEN, etc."""
        
    def load_from_databricks_cli(self):
        """Load from ~/.databrickscfg"""
        
    def save_config(self, workspace_url: str, token: str):
        """Save configuration for future use"""
```

## Technical Implementation Details

### File Conversion Workflow
1. **Path Validation**: Detect Unity Catalog volume paths (`/Volumes/...` or `dbfs:/Volumes/...`)
2. **Authentication**: Use Databricks SDK with token or CLI config
3. **Download**: Stream file from Unity Catalog to local temp directory
4. **Convert**: Use existing converter logic (no changes needed)
5. **Upload**: Stream converted file back to Unity Catalog volume
6. **Cleanup**: Remove temporary local files

### Error Handling Strategy
```python
class DatabricksConversionError(Exception):
    """Base exception for Databricks conversion errors"""
    pass

class UnityVolumesAuthError(DatabricksConversionError):
    """Authentication failed for Unity Catalog volumes"""
    pass

class UnityVolumesPermissionError(DatabricksConversionError):
    """Insufficient permissions for Unity Catalog operations"""
    pass
```

### Performance Considerations
- **Streaming**: Use streaming downloads/uploads for large files
- **Parallel Processing**: Support concurrent conversions for batch operations
- **Progress Tracking**: Leverage existing Rich progress bars for notebook display
- **Memory Management**: Process large files in chunks to avoid memory issues

## Installation and Usage Guide

### For Data Scientists/Analysts

#### Step 1: Install in Databricks Notebook
```python
# Install from PyPI (after package is updated)
%pip install pyforge-cli[databricks]

# Or install from wheel file in Unity Catalog
%pip install /Volumes/catalog/schema/volume/wheels/pyforge_cli-0.3.0-py3-none-any.whl
```

#### Step 2: Configure Authentication (One-time)
```python
from pyforge_cli.notebook import setup_databricks

# Interactive setup - prompts for workspace URL and token
setup_databricks()

# Or programmatic setup
setup_databricks(
    workspace_url="https://your-workspace.cloud.databricks.com",
    token="dapi1234567890abcdef"
)
```

#### Step 3: Convert Files
```python
from pyforge_cli.notebook import convert_file

# Simple conversion
output_path = convert_file(
    input_path="/Volumes/dev_catalog/raw_data/files/sample.xlsx",
    output_path="/Volumes/dev_catalog/processed_data/files/sample.parquet"
)

# Auto-generate output path
output_path = convert_file(
    "/Volumes/dev_catalog/raw_data/files/sample.xlsx"
)
print(f"Converted file saved to: {output_path}")

# Batch conversion
from pyforge_cli.notebook import batch_convert

converted_files = batch_convert(
    input_folder="/Volumes/dev_catalog/raw_data/excel_files/",
    output_folder="/Volumes/dev_catalog/processed_data/parquet_files/",
    file_pattern="*.xlsx"
)
```

### For CLI Users in Databricks

#### Using pyforge Command
```bash
# Convert single file
pyforge databricks convert \
  --workspace-url $DATABRICKS_HOST \
  --token $DATABRICKS_TOKEN \
  "/Volumes/catalog/schema/volume/input.xlsx" \
  "/Volumes/catalog/schema/volume/output.parquet"

# Batch convert folder
pyforge databricks batch-convert \
  "/Volumes/catalog/schema/volume/input_folder/" \
  "/Volumes/catalog/schema/volume/output_folder/"
```

## Configuration Options

### Environment Variables
```bash
# Required
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi1234567890abcdef

# Optional
PYFORGE_DATABRICKS_CATALOG=default_catalog
PYFORGE_DATABRICKS_SCHEMA=default_schema
PYFORGE_TEMP_DIR=/tmp/pyforge_conversions
```

### Configuration File (Optional)
**Location**: `~/.pyforge/databricks.yaml`
```yaml
workspace_url: https://your-workspace.cloud.databricks.com
default_catalog: dev_catalog
default_schema: raw_data
temp_directory: /tmp/pyforge_conversions
max_file_size_mb: 1000
chunk_size_mb: 10
```

## Testing Strategy

### Unit Tests
- Mock Databricks SDK responses
- Test path validation and normalization
- Test authentication handling
- Test error scenarios

### Integration Tests
- Require live Databricks workspace for testing
- Test actual file upload/download operations
- Test conversion end-to-end
- Test batch processing

### Notebook Tests
- Create sample notebooks demonstrating usage
- Test in different Databricks Runtime versions
- Validate progress tracking and error display

## Security Considerations

### Authentication
- Support multiple auth methods: token, OAuth, service principal
- Never log or expose authentication tokens
- Validate workspace URL format
- Handle token expiration gracefully

### File Access
- Validate Unity Catalog paths before operations
- Check permissions before attempting operations
- Sanitize file paths to prevent directory traversal
- Implement file size limits for conversions

### Data Protection
- Use secure temporary directories
- Clean up temporary files after conversion
- Support encryption in transit for sensitive data
- Respect Databricks workspace security settings

## Migration Path

### Existing CLI Users
1. **No Breaking Changes**: All existing functionality remains unchanged
2. **Opt-in Databricks Features**: New functionality is in separate command group
3. **Backward Compatibility**: Existing scripts continue to work

### New Databricks Users
1. **Simple Installation**: Single wheel file installation
2. **Guided Setup**: Interactive configuration helpers
3. **Rich Documentation**: Notebook examples and tutorials

## Dependencies and Requirements

### New Dependencies
```toml
[project.optional-dependencies]
databricks = [
    "databricks-sdk>=0.20.0",
    "databricks-cli>=0.17.0",  # Alternative/fallback
]
```

### Databricks Runtime Requirements
- **Minimum**: Databricks Runtime 11.3 LTS (basic functionality)
- **Recommended**: Databricks Runtime 13.3 LTS+ (full Unity Catalog support)
- **Python Version**: 3.8+ (already supported by existing CLI)

### Permissions Required
- **Unity Catalog**: READ/WRITE access to target volumes
- **Workspace**: READ access for configuration
- **Compute**: Access to clusters for notebook execution

## Future Enhancements

### Phase 2 Features (Future)
1. **Spark Integration**: Use Databricks Spark for very large file processing
2. **Delta Lake Support**: Direct conversion to Delta tables
3. **Workflow Integration**: Integration with Databricks Workflows/Jobs
4. **MLflow Integration**: Log conversion metadata to MLflow
5. **Auto-scaling**: Dynamic resource allocation for large batch jobs

### Advanced Features
1. **Schema Evolution**: Handle schema changes in ongoing conversions
2. **Data Quality**: Built-in data validation and quality checks
3. **Monitoring**: Integration with Databricks monitoring and alerts
4. **Governance**: Integration with Unity Catalog lineage and metadata

## Success Metrics

### Technical Metrics
- **Installation Success Rate**: >95% successful installations
- **Conversion Success Rate**: >99% for supported file formats
- **Performance**: <2x overhead compared to local conversions
- **Error Recovery**: Graceful handling of network/auth issues

### User Experience Metrics
- **Time to First Conversion**: <5 minutes from installation
- **Documentation Clarity**: User feedback and support ticket volume
- **Feature Adoption**: Usage statistics from Databricks telemetry

## Risk Assessment and Mitigation

### Technical Risks
1. **Network Latency**: Mitigate with chunked transfers and progress tracking
2. **Authentication Changes**: Support multiple auth methods for resilience
3. **Databricks API Changes**: Use official SDK and maintain version compatibility
4. **File Size Limits**: Implement streaming and chunked processing

### Operational Risks
1. **Breaking Changes**: Maintain backward compatibility and version testing
2. **Support Complexity**: Provide comprehensive documentation and examples
3. **Security Vulnerabilities**: Regular dependency updates and security scanning

## Conclusion

This comprehensive plan enables CortexPy-CLI to seamlessly integrate with Databricks notebooks and Unity Catalog volumes. The implementation leverages the existing robust architecture while adding cloud-native capabilities. The phased approach ensures minimal risk while delivering immediate value to Databricks users.

The key success factors are:
1. **Maintain Simplicity**: Easy installation and intuitive API
2. **Leverage Existing Architecture**: Build on proven converter patterns
3. **Provide Rich Documentation**: Comprehensive examples and guides
4. **Ensure Security**: Robust authentication and data protection
5. **Plan for Scale**: Support for large files and batch operations

Implementation of this plan will position CortexPy-CLI as the premier file conversion tool for Databricks environments, enabling data scientists and engineers to efficiently process diverse file formats within their existing workflows.