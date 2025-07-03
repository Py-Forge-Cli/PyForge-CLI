# Extension Development Best Practices

This document outlines best practices for developing PyForge CLI extensions based on experience from core development and community contributions.

## Table of Contents

1. [Architecture Best Practices](#architecture-best-practices)
2. [Error Handling](#error-handling)
3. [Performance Optimization](#performance-optimization)
4. [Testing Strategies](#testing-strategies)
5. [Documentation Guidelines](#documentation-guidelines)
6. [Security Considerations](#security-considerations)
7. [Deployment Best Practices](#deployment-best-practices)

## Architecture Best Practices

### 1. Single Responsibility Principle

Each extension should have a clear, focused purpose:

```python
# Good: Focused on Databricks integration
class DatabricksExtension(BaseExtension):
    """Databricks integration for PyForge CLI."""
    pass

# Avoid: Multiple unrelated responsibilities
class MegaExtension(BaseExtension):
    """Handles Databricks, AWS, Azure, and email notifications."""
    pass
```

### 2. Dependency Management

Minimize required dependencies and handle optional ones gracefully:

```python
def is_available(self) -> bool:
    """Check availability with graceful dependency handling."""
    required_available = True
    optional_features = {}
    
    # Check required dependencies
    try:
        import required_package
    except ImportError:
        required_available = False
    
    # Check optional dependencies
    try:
        import optional_package
        optional_features['advanced_features'] = True
    except ImportError:
        optional_features['advanced_features'] = False
    
    if required_available:
        self.optional_features = optional_features
    
    return required_available
```

### 3. Configuration Management

Use hierarchical configuration with sensible defaults:

```python
def _load_config(self) -> Dict[str, Any]:
    """Load configuration from multiple sources."""
    config = self._get_default_config()
    
    # 1. Environment variables
    config.update(self._load_env_config())
    
    # 2. User config file
    config.update(self._load_user_config())
    
    # 3. Project config file
    config.update(self._load_project_config())
    
    return config

def _get_default_config(self) -> Dict[str, Any]:
    """Get default configuration."""
    return {
        'enabled': True,
        'debug': False,
        'timeout': 30,
        'retry_attempts': 3
    }
```

### 4. State Management

Keep extension state minimal and predictable:

```python
class WellDesignedExtension(BaseExtension):
    def __init__(self):
        super().__init__()
        # Minimal state
        self.name = "well_designed"
        self.version = "1.0.0"
        self.config = {}
        self.client = None
        
    def initialize(self) -> bool:
        """Initialize with clear state transitions."""
        if self.initialized:
            return True
            
        try:
            self.config = self._load_config()
            self.client = self._create_client()
            self.initialized = True
            return True
        except Exception as e:
            self.cleanup()  # Ensure clean state on failure
            raise
```

## Error Handling

### 1. Graceful Degradation

Extensions should never break core functionality:

```python
def hook_pre_conversion(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Example of graceful error handling in hooks."""
    try:
        # Extension-specific processing
        enhanced_options = self._enhance_options(options)
        return enhanced_options
        
    except Exception as e:
        # Log error but don't break conversion
        self.logger.error(f"Extension enhancement failed: {e}")
        return options  # Return original options
```

### 2. Structured Error Logging

Use structured logging for better debugging:

```python
import logging
from typing import Any, Dict

class ExtensionWithGoodLogging(BaseExtension):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"pyforge.extensions.{self.name}")
        
    def _log_error(self, operation: str, error: Exception, context: Dict[str, Any] = None):
        """Structured error logging."""
        self.logger.error(
            "Extension operation failed",
            extra={
                'extension': self.name,
                'operation': operation,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context or {}
            }
        )
    
    def some_operation(self):
        try:
            # Operation code
            pass
        except ValueError as e:
            self._log_error('some_operation', e, {'input_type': 'invalid'})
            raise
```

### 3. Error Recovery Strategies

Implement intelligent error recovery:

```python
def hook_error_handling(self, error: Exception, context: Dict[str, Any]) -> bool:
    """Intelligent error recovery."""
    if isinstance(error, ConnectionError):
        return self._handle_connection_error(error, context)
    elif isinstance(error, TimeoutError):
        return self._handle_timeout_error(error, context)
    elif isinstance(error, ValueError):
        return self._handle_validation_error(error, context)
    
    return False  # Let default handling take over

def _handle_connection_error(self, error: ConnectionError, context: Dict[str, Any]) -> bool:
    """Handle connection errors with retry logic."""
    retry_count = context.get('retry_count', 0)
    max_retries = self.config.get('max_retries', 3)
    
    if retry_count < max_retries:
        self.logger.info(f"Retrying connection (attempt {retry_count + 1}/{max_retries})")
        time.sleep(2 ** retry_count)  # Exponential backoff
        return True  # Indicate error was handled
    
    return False  # Max retries reached
```

## Performance Optimization

### 1. Lazy Loading

Load resources only when needed:

```python
class OptimizedExtension(BaseExtension):
    def __init__(self):
        super().__init__()
        self._client = None
        self._config = None
    
    @property
    def client(self):
        """Lazy-loaded client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    @property  
    def config(self):
        """Lazy-loaded configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
```

### 2. Caching Strategies

Implement intelligent caching:

```python
import time
from functools import lru_cache, wraps

class CachingExtension(BaseExtension):
    def __init__(self):
        super().__init__()
        self._cache = {}
        self._cache_ttl = {}
    
    def _cached_with_ttl(self, ttl_seconds: int):
        """Decorator for caching with TTL."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                now = time.time()
                
                # Check if cached and not expired
                if (cache_key in self._cache and 
                    cache_key in self._cache_ttl and 
                    now < self._cache_ttl[cache_key]):
                    return self._cache[cache_key]
                
                # Compute and cache result
                result = func(*args, **kwargs)
                self._cache[cache_key] = result
                self._cache_ttl[cache_key] = now + ttl_seconds
                
                return result
            return wrapper
        return decorator
    
    @_cached_with_ttl(300)  # 5 minute cache
    def expensive_operation(self, data: str) -> str:
        """Example expensive operation with caching."""
        # Simulate expensive computation
        time.sleep(1)
        return f"processed_{data}"
```

### 3. Resource Management

Properly manage resources to avoid leaks:

```python
import contextlib
from typing import Generator

class ResourceManagedExtension(BaseExtension):
    @contextlib.contextmanager
    def _managed_connection(self) -> Generator[Any, None, None]:
        """Context manager for connection resources."""
        connection = None
        try:
            connection = self._create_connection()
            yield connection
        finally:
            if connection:
                connection.close()
    
    def process_with_connection(self, data: Any) -> Any:
        """Process data with managed connection."""
        with self._managed_connection() as conn:
            return conn.process(data)
```

## Testing Strategies

### 1. Comprehensive Test Coverage

Structure tests by functionality:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

class TestMyExtension:
    def setup_method(self):
        """Setup for each test method."""
        self.extension = MyExtension()
    
    def test_availability_check(self):
        """Test extension availability under different conditions."""
        # Test with all dependencies available
        with patch('my_extension.required_package'):
            assert self.extension.is_available() == True
        
        # Test with missing dependencies
        with patch('my_extension.required_package', side_effect=ImportError):
            assert self.extension.is_available() == False
    
    def test_initialization_success(self):
        """Test successful initialization."""
        with patch.object(self.extension, 'is_available', return_value=True):
            assert self.extension.initialize() == True
            assert self.extension.initialized == True
    
    def test_initialization_failure(self):
        """Test initialization failure handling."""
        with patch.object(self.extension, 'is_available', return_value=False):
            assert self.extension.initialize() == False
            assert self.extension.initialized == False
    
    def test_hook_error_handling(self):
        """Test that hooks handle errors gracefully."""
        # Hooks should not raise exceptions
        result = self.extension.hook_pre_conversion(
            Path("test.csv"), Path("test.parquet"), {}
        )
        assert result is not None
    
    def test_cleanup_idempotent(self):
        """Test that cleanup can be called multiple times safely."""
        self.extension.cleanup()
        self.extension.cleanup()  # Should not raise
```

### 2. Integration Testing

Test extension integration with PyForge CLI:

```python
import subprocess
import tempfile
from pathlib import Path

def test_extension_cli_integration():
    """Test extension works with CLI."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "test.csv"
        output_file = Path(tmpdir) / "test.parquet"
        
        # Create test input
        input_file.write_text("id,name\n1,test\n2,example")
        
        # Run CLI with extension
        result = subprocess.run([
            "pyforge", "convert", 
            str(input_file), str(output_file),
            "--verbose"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert output_file.exists()
```

### 3. Performance Testing

Test extension performance impact:

```python
import time
import pytest

def test_hook_performance():
    """Test that hooks don't significantly impact performance."""
    extension = MyExtension()
    extension.initialize()
    
    # Test hook execution time
    start_time = time.time()
    
    for _ in range(100):
        extension.hook_pre_conversion(
            Path("test.csv"), Path("test.parquet"), {}
        )
    
    total_time = time.time() - start_time
    
    # Hook should be fast (< 10ms per call on average)
    assert total_time < 1.0  # 100 calls in less than 1 second
```

## Documentation Guidelines

### 1. Code Documentation

Use comprehensive docstrings:

```python
def hook_pre_conversion(
    self, 
    input_file: Path, 
    output_file: Path, 
    options: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Hook called before conversion starts.
    
    This hook allows the extension to modify conversion options
    before the conversion process begins. It can be used to:
    - Add metadata to the conversion
    - Modify conversion parameters
    - Validate input files
    - Set up external resources
    
    Args:
        input_file: Path to the input file being converted
        output_file: Path where the output will be written
        options: Dictionary of conversion options that can be modified
        
    Returns:
        Optional[Dict[str, Any]]: Modified options dictionary or None
        to leave options unchanged. If None is returned, the original
        options will be used without modification.
        
    Raises:
        This method should not raise exceptions. Any errors should be
        logged and handled gracefully, returning the original options.
        
    Example:
        >>> extension = MyExtension()
        >>> options = {"format": "parquet"}
        >>> result = extension.hook_pre_conversion(
        ...     Path("data.csv"), Path("data.parquet"), options
        ... )
        >>> assert "metadata" in result
    """
```

### 2. User Documentation

Provide clear usage documentation:

```markdown
# MyExtension Usage Guide

## Installation

```bash
pip install my-pyforge-extension
```

## Configuration

Create `~/.pyforge/my_extension.json`:

```json
{
    "api_key": "your-api-key",
    "endpoint": "https://api.example.com",
    "timeout": 30
}
```

## Usage Examples

### Basic Usage
```bash
pyforge convert data.csv data.parquet
```

### With Extension Commands
```bash
pyforge my-extension-status
pyforge my-extension-config show
```
```

### 3. API Documentation

Document all public methods and hooks:

```python
class DocumentedExtension(BaseExtension):
    """
    Well-documented extension example.
    
    This extension demonstrates proper documentation practices
    for PyForge CLI extensions.
    
    Attributes:
        name (str): Extension name
        version (str): Extension version
        config (Dict[str, Any]): Extension configuration
        
    Example:
        >>> ext = DocumentedExtension()
        >>> if ext.is_available():
        ...     ext.initialize()
        ...     print(f"Extension {ext.name} ready")
    """
    
    def custom_method(self, param1: str, param2: int = 10) -> bool:
        """
        Custom method example.
        
        Args:
            param1: Description of string parameter
            param2: Description of integer parameter (default: 10)
            
        Returns:
            bool: True if operation successful
            
        Raises:
            ValueError: If param1 is empty
            ConnectionError: If external service unavailable
        """
        if not param1:
            raise ValueError("param1 cannot be empty")
        
        # Method implementation
        return True
```

## Security Considerations

### 1. Input Validation

Always validate inputs:

```python
def validate_file_path(self, file_path: Path) -> bool:
    """Validate file path for security."""
    try:
        # Check if path is absolute and within allowed directories
        resolved_path = file_path.resolve()
        
        # Prevent directory traversal
        if ".." in str(file_path):
            self.logger.warning(f"Potential directory traversal: {file_path}")
            return False
        
        # Check file size limits
        if resolved_path.exists():
            file_size = resolved_path.stat().st_size
            max_size = self.config.get('max_file_size', 100 * 1024 * 1024)  # 100MB
            if file_size > max_size:
                self.logger.warning(f"File too large: {file_size} > {max_size}")
                return False
        
        return True
        
    except Exception as e:
        self.logger.error(f"Path validation error: {e}")
        return False
```

### 2. Credential Management

Handle credentials securely:

```python
import os
from pathlib import Path

def _load_credentials(self) -> Dict[str, str]:
    """Load credentials securely."""
    credentials = {}
    
    # 1. Environment variables (preferred)
    if os.environ.get('MY_EXTENSION_API_KEY'):
        credentials['api_key'] = os.environ['MY_EXTENSION_API_KEY']
    
    # 2. Secure credential file
    cred_file = Path.home() / '.pyforge' / 'credentials' / f'{self.name}.json'
    if cred_file.exists():
        # Ensure file has secure permissions
        file_stat = cred_file.stat()
        if file_stat.st_mode & 0o077:  # Check if readable by others
            self.logger.warning(f"Credential file has insecure permissions: {cred_file}")
        else:
            with open(cred_file) as f:
                credentials.update(json.load(f))
    
    return credentials
```

### 3. Data Sanitization

Sanitize data before processing:

```python
import re
from typing import Any

def sanitize_input(self, data: Any) -> Any:
    """Sanitize input data."""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', data)
        # Limit length
        max_length = self.config.get('max_string_length', 1000)
        return sanitized[:max_length]
    
    elif isinstance(data, dict):
        return {k: self.sanitize_input(v) for k, v in data.items()}
    
    elif isinstance(data, list):
        return [self.sanitize_input(item) for item in data]
    
    return data
```

## Deployment Best Practices

### 1. Version Management

Use semantic versioning and compatibility checks:

```python
class VersionAwareExtension(BaseExtension):
    REQUIRED_PYFORGE_VERSION = "0.5.0"
    
    def is_available(self) -> bool:
        """Check version compatibility."""
        if not self._check_pyforge_version():
            return False
        
        return super().is_available()
    
    def _check_pyforge_version(self) -> bool:
        """Check PyForge CLI version compatibility."""
        try:
            import pyforge_cli
            from packaging import version
            
            current_version = version.parse(pyforge_cli.__version__)
            required_version = version.parse(self.REQUIRED_PYFORGE_VERSION)
            
            if current_version < required_version:
                self.logger.error(
                    f"PyForge CLI {self.REQUIRED_PYFORGE_VERSION}+ required, "
                    f"found {current_version}"
                )
                return False
            
            return True
            
        except ImportError:
            self.logger.error("packaging library required for version checking")
            return False
```

### 2. Backward Compatibility

Maintain backward compatibility:

```python
def hook_pre_conversion(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Hook with backward compatibility."""
    # Handle old option names
    if 'old_option_name' in options:
        self.logger.warning("'old_option_name' is deprecated, use 'new_option_name'")
        options['new_option_name'] = options.pop('old_option_name')
    
    # Provide default values for new options
    options.setdefault('new_option', 'default_value')
    
    return options
```

### 3. Monitoring and Metrics

Add monitoring capabilities:

```python
import time
from collections import defaultdict

class MonitoredExtension(BaseExtension):
    def __init__(self):
        super().__init__()
        self.metrics = defaultdict(int)
        self.timing_data = defaultdict(list)
    
    def _record_timing(self, operation: str, duration: float):
        """Record operation timing."""
        self.timing_data[operation].append(duration)
        self.metrics[f"{operation}_count"] += 1
    
    def hook_pre_conversion(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hook with timing measurement."""
        start_time = time.time()
        
        try:
            result = self._do_pre_conversion(input_file, output_file, options)
            self.metrics['pre_conversion_success'] += 1
            return result
        except Exception as e:
            self.metrics['pre_conversion_error'] += 1
            raise
        finally:
            duration = time.time() - start_time
            self._record_timing('pre_conversion', duration)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get extension metrics."""
        return {
            'counters': dict(self.metrics),
            'timing': {
                op: {
                    'count': len(times),
                    'avg': sum(times) / len(times) if times else 0,
                    'min': min(times) if times else 0,
                    'max': max(times) if times else 0
                }
                for op, times in self.timing_data.items()
            }
        }
```

These best practices ensure that your extensions are robust, maintainable, secure, and performant. Following these guidelines will help create extensions that integrate seamlessly with PyForge CLI and provide value to users.