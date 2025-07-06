# PyForge CLI Databricks Extension - Testing Guide

## Overview

This guide documents the comprehensive testing approach for the PyForge CLI Databricks extension, including environment-specific behaviors, known issues, and testing patterns.

## Test Infrastructure

### Directory Structure

```
notebooks/testing/
├── functional/
│   ├── 01-databricks-extension-functional.ipynb    # Core functional tests
│   ├── 02-databricks-extension-serverless.ipynb   # Environment-specific tests (placeholder)
│   └── 03-databricks-extension-serverless-test.ipynb  # Serverless-specific tests
├── integration/
│   ├── 03-databricks-extension-integration.py      # Comprehensive integration tests
│   └── 04-databricks-volume-integration.py         # Volume operations tests
└── unit/
    ├── test_databricks_extension.py                # Unit test scripts
    └── test_volume_operations.py                   # Volume unit tests
```

## Testing Patterns

### Widget Configuration

All test notebooks follow a consistent widget configuration pattern:

```python
# Core configuration widgets
dbutils.widgets.text("pyforge_version", "latest", "PyForge Version")
dbutils.widgets.dropdown("test_environment", "auto", ["auto", "serverless", "classic"], "Test Environment")
dbutils.widgets.dropdown("test_scope", "comprehensive", ["basic", "comprehensive", "performance"], "Test Scope")
dbutils.widgets.checkbox("verbose_logging", True, "Verbose Logging")

# Environment-specific widgets
dbutils.widgets.text("volume_path", "/Volumes/main/default/pyforge", "Volume Path")
dbutils.widgets.checkbox("cleanup_after_test", True, "Cleanup After Test")
```

### Test Result Tracking

```python
test_results = {
    'metadata': {
        'test_type': 'functional|integration|serverless|volume',
        'notebook_name': 'test-notebook-name',
        'timestamp': datetime.now().isoformat(),
        'configuration': {...}
    },
    'test_sections': {
        'section_name': {
            'success': True/False,
            'results': {...},
            'error': 'error_message' # if applicable
        }
    },
    'performance_metrics': {
        'metric_name': float_value
    },
    'overall_success': True/False
}
```

## Environment-Specific Behaviors

### Serverless Compute Environment

#### Characteristics
- **PySpark Availability**: Always available and optimized
- **Memory Management**: Automatic scaling and memory optimization
- **Performance**: Optimized for large dataset processing
- **Engine Selection**: Defaults to PySpark-based converters

#### Testing Focus
- PySpark-optimized converter performance
- Memory efficiency with large datasets
- Streaming support for very large files
- Delta Lake integration
- Unity Catalog Volume operations

#### Known Issues
1. **Cold Start Performance**: Initial Spark context creation can take 30-60 seconds
2. **Volume Path Resolution**: Absolute Volume paths required
3. **Large File Memory**: Files >1GB may require streaming mode

#### Optimization Recommendations
```python
# Recommended settings for serverless testing
TEST_DATASET_SIZE = "medium"  # Start with medium datasets
TEST_STREAMING = True         # Enable streaming for large files
TEST_DELTA_LAKE = True       # Test Delta Lake output
```

### Classic Compute Environment

#### Characteristics
- **PySpark Availability**: May or may not be available
- **Fallback Behavior**: Graceful degradation to pandas/pyarrow
- **Performance**: Variable depending on cluster configuration
- **Engine Selection**: Determined by available libraries

#### Testing Focus
- Fallback mechanism testing
- pandas/pyarrow compatibility
- Error handling for missing dependencies
- Performance comparison between engines

#### Known Issues
1. **Dependency Availability**: PySpark/Delta Lake may not be installed
2. **Memory Limitations**: Fixed cluster memory constraints
3. **Performance Variability**: Depends on cluster size and configuration

#### Fallback Testing Pattern
```python
# Test engine selection based on availability
if pyspark_available:
    expected_engine = "pyspark"
    expected_performance = "high"
else:
    expected_engine = "pandas"
    expected_performance = "moderate"
```

## API Method Testing

### Core API Methods

#### PyForgeDatabricks.convert()
**Test Coverage:**
- Input format detection (CSV, Excel, XML)
- Output format specification (Parquet, Delta)
- Engine selection (PySpark vs pandas)
- Error handling for invalid inputs
- Performance metrics collection

**Test Pattern:**
```python
# Basic conversion test
conversion_result = forge.convert(
    input_path="test_data.csv",
    output_path="output.parquet",
    format="parquet"
)

# Verify result structure
assert 'output_path' in conversion_result
assert 'rows_processed' in conversion_result
assert 'engine_used' in conversion_result
```

#### PyForgeDatabricks.get_info()
**Test Coverage:**
- File format detection
- Metadata extraction
- Size calculation
- Error handling for inaccessible files

#### PyForgeDatabricks.validate()
**Test Coverage:**
- File accessibility validation
- Format compatibility checking
- Permission verification

#### PyForgeDatabricks.batch_convert()
**Test Coverage:**
- Pattern-based file selection
- Parallel processing
- Progress tracking
- Error aggregation

### Volume Operations Testing

#### VolumeOperations.is_volume_path()
**Test Coverage:**
- Volume path detection accuracy
- Non-Volume path rejection
- Edge case handling

**Test Cases:**
```python
test_cases = [
    ("/Volumes/catalog/schema/volume/file.csv", True),
    ("/tmp/local_file.csv", False),
    ("/Volumes/invalid/path", False),
    ("relative/path.csv", False)
]
```

#### VolumeOperations.get_volume_info()
**Test Coverage:**
- Catalog/schema/volume extraction
- Subpath handling
- Error handling for invalid paths

## Performance Benchmarking

### Metrics Collection

#### Throughput Metrics
```python
throughput_metrics = {
    'rows_per_second': rows_processed / conversion_time,
    'mb_per_second': file_size_mb / conversion_time,
    'files_per_second': files_processed / total_time
}
```

#### Memory Metrics
```python
memory_metrics = {
    'peak_memory_mb': peak_memory_usage,
    'memory_efficiency': rows_processed / peak_memory_usage,
    'memory_growth_rate': (final_memory - initial_memory) / time_elapsed
}
```

### Performance Expectations

#### Serverless Environment
- **CSV Conversion**: >50,000 rows/second
- **Excel Conversion**: >10,000 rows/second
- **Memory Efficiency**: <100MB for 1M rows
- **Delta Lake**: <5% performance overhead

#### Classic Environment
- **CSV Conversion**: >20,000 rows/second (with PySpark)
- **Excel Conversion**: >5,000 rows/second
- **Fallback Performance**: 50-70% of PySpark performance

## Error Handling Patterns

### Expected Error Scenarios

#### Missing Dependencies
```python
try:
    import pyspark
except ImportError:
    # Graceful fallback to pandas
    fallback_engine = "pandas"
    performance_impact = "moderate"
```

#### Volume Access Errors
```python
try:
    volume_contents = dbutils.fs.ls(volume_path)
except Exception as e:
    if "ACCESS_DENIED" in str(e):
        error_type = "permission_error"
    elif "NOT_FOUND" in str(e):
        error_type = "path_not_found"
    else:
        error_type = "unknown_volume_error"
```

#### Conversion Errors
```python
conversion_errors = {
    'file_not_found': "Input file does not exist",
    'format_unsupported': "File format not supported",
    'permission_denied': "Insufficient permissions",
    'memory_error': "File too large for available memory",
    'engine_error': "Conversion engine failure"
}
```

### Error Recovery Strategies

1. **Automatic Fallback**: PySpark → pandas → error
2. **Retry with Streaming**: For memory errors
3. **Alternative Formats**: Suggest compatible output formats
4. **Incremental Processing**: For very large files

## Test Execution Guidelines

### Pre-Test Setup

1. **Environment Verification**
   ```python
   # Verify Databricks environment
   assert 'DATABRICKS_RUNTIME_VERSION' in os.environ
   
   # Verify Volume access
   assert dbutils.fs.ls(volume_path)
   
   # Verify PyForge installation
   import pyforge_cli.extensions.databricks
   ```

2. **Test Data Preparation**
   ```python
   # Generate test datasets of varying sizes
   test_datasets = {
       'small': {'rows': 1000, 'columns': 5},
       'medium': {'rows': 10000, 'columns': 10},
       'large': {'rows': 100000, 'columns': 15}
   }
   ```

### Test Execution Order

1. **Environment Detection Tests**
2. **Plugin Discovery and Loading Tests**
3. **API Functional Tests**
4. **Volume Operations Tests**
5. **Performance Benchmarks**
6. **Error Handling Tests**
7. **Cleanup Operations**

### Post-Test Validation

1. **Results Validation**
   ```python
   # Verify test completeness
   required_tests = ['environment', 'api', 'volume', 'performance']
   completed_tests = [t for t in required_tests if test_results.get(t, {}).get('success')]
   assert len(completed_tests) == len(required_tests)
   ```

2. **Performance Validation**
   ```python
   # Verify performance meets expectations
   throughput = test_results['performance']['throughput_rows_per_sec']
   assert throughput > minimum_expected_throughput
   ```

3. **Cleanup Verification**
   ```python
   # Verify test artifacts are cleaned up
   for test_dir in test_directories:
       assert not dbutils.fs.ls(test_dir), f"Test directory not cleaned: {test_dir}"
   ```

## Debugging and Troubleshooting

### Common Issues

#### Test Failures

1. **Environment Setup Failures**
   - Check Databricks runtime version compatibility
   - Verify Unity Catalog Volume permissions
   - Ensure PyForge CLI installation

2. **API Test Failures**
   - Verify test data creation
   - Check file path accessibility
   - Validate engine availability

3. **Performance Test Failures**
   - Check cluster resources
   - Verify data size expectations
   - Review memory constraints

#### Performance Issues

1. **Slow Conversion Times**
   - Check engine selection (PySpark vs pandas)
   - Verify cluster scaling
   - Review file optimization

2. **Memory Errors**
   - Enable streaming mode
   - Reduce batch sizes
   - Check available cluster memory

### Diagnostic Commands

```python
# Environment diagnostics
print(f"Runtime: {os.environ.get('DATABRICKS_RUNTIME_VERSION')}")
print(f"Python: {sys.version}")
print(f"PySpark: {pyspark.__version__ if 'pyspark' in globals() else 'Not available'}")

# Performance diagnostics
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
print(f"CPU: {psutil.cpu_percent()}%")

# Volume diagnostics
volume_info = forge.get_environment_info()
print(f"Volume access: {volume_info.get('volume_access', 'Unknown')}")
```

## Best Practices

### Test Development

1. **Comprehensive Coverage**: Test all API methods and edge cases
2. **Environment Awareness**: Account for serverless vs classic differences
3. **Performance Monitoring**: Include timing and memory metrics
4. **Error Handling**: Test both success and failure scenarios
5. **Cleanup**: Always clean up test artifacts

### Test Execution

1. **Environment Preparation**: Verify all prerequisites
2. **Incremental Testing**: Start with small datasets
3. **Error Tolerance**: Expect and handle environment variations
4. **Documentation**: Log all issues and workarounds
5. **Results Archive**: Save test results for comparison

### Test Maintenance

1. **Regular Updates**: Keep tests current with extension changes
2. **Environment Testing**: Test across different Databricks configurations
3. **Performance Baselines**: Update performance expectations
4. **Documentation Updates**: Keep this guide current
5. **Issue Tracking**: Document and track known issues

## Conclusion

This testing framework provides comprehensive coverage of the PyForge CLI Databricks extension across different environments and use cases. The structured approach ensures reliable extension operation while providing clear debugging guidance for issues that may arise.

For additional support or to report testing issues, refer to the main PyForge CLI documentation or file issues in the project repository.