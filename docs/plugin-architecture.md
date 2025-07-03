# PyForge Plugin Architecture

## Overview

PyForge uses Python's entry points mechanism for plugin discovery, enabling seamless extension of functionality without modifying core code.

## Architecture Design

### Entry Point Naming Convention

PyForge defines two entry point groups:
- `pyforge.extensions`: For complete extensions (e.g., Databricks, AWS)
- `pyforge.converters`: For individual converter plugins

### Plugin Discovery Flow

```
Application Start
    ↓
Load Core Components
    ↓
Discover Entry Points (pyforge.extensions)
    ↓
Check Extension Availability
    ↓
Initialize Available Extensions
    ↓
Register Extension Components
    ↓
Ready for Use
```

### Entry Point Structure

```toml
[project.entry-points."pyforge.extensions"]
databricks = "pyforge_cli.extensions.databricks:DatabricksExtension"

[project.entry-points."pyforge.converters"]
spark_csv = "pyforge_cli.extensions.databricks.converters:SparkCSVConverter"
```

## Compatibility

The plugin system supports Python 3.8-3.12 using:
- `importlib.metadata` for Python 3.8+
- Graceful fallback for different `entry_points()` APIs
- Compatible with setuptools and modern pyproject.toml

## Error Handling

- Missing dependencies: Log warning, skip extension
- Import errors: Graceful degradation
- Initialization failures: Extension marked as unavailable
- Timeout protection: 5-second initialization limit

## Extension Interface

All extensions must implement the `BaseExtension` interface:

```python
class BaseExtension(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if extension can be used"""
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the extension"""
        
    def get_commands(self) -> List[click.Command]:
        """Optional: Additional CLI commands"""
        
    def enhance_convert_command(self, ctx, **kwargs) -> Dict:
        """Optional: Enhance conversion parameters"""
```

## Security Considerations

- Extensions run in the same process (no sandboxing)
- Only install trusted extensions
- Extensions have full access to PyForge APIs
- No automatic updates or remote loading

## Performance

- Discovery happens once at startup
- Lazy loading of extension components
- Minimal overhead for unused extensions
- < 100ms discovery time target