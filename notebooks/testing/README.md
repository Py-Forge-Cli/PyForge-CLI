# PyForge CLI Databricks Extension Testing Infrastructure

This directory contains comprehensive testing infrastructure for the PyForge CLI Databricks extension, organized into functional, integration, and unit tests following established Databricks testing patterns.

## Directory Structure

```
notebooks/testing/
├── functional/                           # Functional tests (.ipynb files)
│   ├── 01-databricks-extension-functional.ipynb
│   └── 02-databricks-extension-serverless.ipynb
├── integration/                          # Integration tests (.py files)
│   ├── 03-databricks-extension-integration.py
│   └── 04-databricks-volume-integration.py
├── unit/                                 # Unit test scripts (.py files)
│   ├── test_databricks_extension.py
│   └── test_volume_operations.py
└── README.md                             # This documentation
```

## Testing Categories

### 🧪 Functional Tests (Jupyter Notebooks)

Interactive notebook tests designed to run in Databricks environments with widget configuration and comprehensive error handling.

#### `01-databricks-extension-functional.ipynb`
- **Purpose**: Core Databricks extension functionality testing
- **Features**:
  - Widget-based configuration for environment parameters
  - Plugin discovery and extension loading tests
  - Environment detection (serverless vs classic compute)
  - API method testing and validation
  - Fallback behavior verification
  - Error handling scenarios
  - Performance metrics collection

- **Key Test Areas**:
  - Extension discovery mechanism
  - Plugin initialization and lifecycle
  - Environment-specific behavior
  - API integration testing
  - Graceful error degradation

#### `02-databricks-extension-serverless.ipynb` 
- **Purpose**: Serverless-specific functionality and optimizations
- **Features**:
  - PySpark integration testing
  - Unity Catalog Volume operations
  - Performance benchmarking for large datasets
  - Serverless environment detection
  - Cross-volume conversion workflows

- **Key Test Areas**:
  - PySpark DataFrame operations
  - Serverless compute optimization
  - Volume access and permissions
  - Large-scale data processing
  - Performance metrics and rates

### 🔧 Integration Tests (Python Scripts)

Comprehensive integration tests that can be executed as Databricks notebook cells or standalone scripts.

#### `03-databricks-extension-integration.py`
- **Purpose**: End-to-end integration testing of the complete extension system
- **Features**:
  - Multi-extension interaction testing
  - Real-world conversion workflows
  - Error scenario simulation
  - Performance benchmarking
  - Configuration management testing

- **Key Test Areas**:
  - Plugin system integration
  - Extension conflict detection
  - Conversion workflow validation
  - Error handling and recovery
  - Performance benchmarks

#### `04-databricks-volume-integration.py`
- **Purpose**: Unity Catalog Volume-specific integration testing
- **Features**:
  - Cross-volume operations
  - Multi-catalog testing
  - Volume permissions validation
  - Large file operation testing
  - Volume discovery and enumeration

- **Key Test Areas**:
  - Volume access patterns
  - Cross-catalog operations
  - Permission and security testing
  - Bulk operation performance
  - Volume configuration management

### 📝 Unit Tests (Python Scripts)

Traditional unit tests using unittest framework for component-level testing.

#### `test_databricks_extension.py`
- **Purpose**: Unit tests for core Databricks extension components
- **Features**:
  - Plugin discovery mechanism testing
  - Extension base class validation
  - Registry functionality testing
  - Environment detection validation
  - Configuration management testing

- **Test Classes**:
  - `TestDatabricksExtensionDiscovery`
  - `TestDatabricksExtensionBase`
  - `TestDatabricksExtensionRegistry`
  - `TestEnvironmentDetection`
  - `TestDatabricksExtensionAPI`
  - `TestErrorHandling`
  - `TestConfigurationManagement`
  - `TestPerformanceMetrics`

#### `test_volume_operations.py`
- **Purpose**: Unit tests for Unity Catalog Volume operations
- **Features**:
  - Volume path validation
  - Volume access simulation
  - Cross-volume operation testing
  - Error handling validation
  - Performance measurement

- **Test Classes**:
  - `TestVolumePathValidation`
  - `TestVolumeAccessSimulation`
  - `TestCrossVolumeOperations`
  - `TestVolumeErrorHandling`
  - `TestVolumePerformance`
  - `TestVolumeConfiguration`

## Testing Patterns and Standards

### Widget Configuration Pattern
All functional notebooks use consistent widget configuration:

```python
# Standard widget configuration
dbutils.widgets.text("pyforge_version", "latest", "PyForge Version")
dbutils.widgets.dropdown("test_environment", "auto", ["auto", "serverless", "classic"], "Test Environment")
dbutils.widgets.dropdown("test_scope", "basic", ["basic", "comprehensive", "performance"], "Test Scope")
dbutils.widgets.checkbox("verbose_logging", True, "Verbose Logging")
```

### Error Handling Pattern
Comprehensive error handling with graceful degradation:

```python
try:
    # Test operation
    result = perform_test_operation()
    test_results['operation_success'] = True
    test_results['result'] = result
except Exception as e:
    print(f"❌ Operation failed: {e}")
    test_results['operation_success'] = False
    test_results['error'] = str(e)
```

### Performance Metrics Pattern
Consistent performance measurement and reporting:

```python
import time

operation_start = time.time()
# Perform operation
operation_time = time.time() - operation_start

test_results['performance_metrics'][operation_name] = {
    'duration': operation_time,
    'rate': items_processed / operation_time,
    'success': operation_success
}
```

### Results Tracking Pattern
Structured results collection with metadata:

```python
test_results = {
    'test_metadata': {
        'start_time': datetime.now().isoformat(),
        'test_type': 'functional',
        'environment': environment_type
    },
    'test_category_results': {},
    'performance_metrics': {},
    'overall_success': False
}
```

## Running the Tests

### Functional Tests (Databricks Notebooks)
1. Import notebooks into Databricks workspace
2. Attach to serverless or classic compute cluster
3. Configure widgets with appropriate parameters
4. Run all cells in sequence
5. Review comprehensive test results and metrics

### Integration Tests (Databricks Python Scripts)
1. Copy script content to Databricks notebook cells
2. Configure test parameters in the first cell
3. Execute all cells to run comprehensive integration tests
4. Analyze detailed results and performance metrics

### Unit Tests (Local or Databricks)
```bash
# Run individual test files
python notebooks/testing/unit/test_databricks_extension.py
python notebooks/testing/unit/test_volume_operations.py

# Run with pytest for enhanced output
pytest notebooks/testing/unit/ -v
```

## Test Configuration Options

### Environment Configuration
- **`auto`**: Automatically detect environment type
- **`serverless`**: Force serverless testing mode
- **`classic`**: Force classic compute testing mode

### Test Scope Configuration
- **`basic`**: Essential functionality only
- **`comprehensive`**: Full feature testing
- **`performance`**: Performance benchmarking focus
- **`stress`**: High-load stress testing

### Volume Configuration
- **`single_volume`**: Single volume operations
- **`cross_volume`**: Cross-volume operations
- **`multi_catalog`**: Multi-catalog testing

## Expected Test Results

### Success Criteria
- ✅ All critical tests pass
- ✅ Extension discovery and loading successful
- ✅ Environment detection accurate
- ✅ API methods functional
- ✅ Error handling graceful
- ✅ Performance within acceptable ranges

### Performance Benchmarks
- **Plugin Discovery**: < 5 seconds
- **Extension Loading**: < 10 seconds
- **Data Generation**: > 1,000 rows/second
- **Volume Operations**: > 1 MB/second
- **Cross-Volume Copy**: > 500 rows/second

### Error Handling Validation
- ✅ Invalid file format rejection
- ✅ Missing dependency graceful handling
- ✅ Volume access failure recovery
- ✅ Timeout scenario management
- ✅ Memory pressure handling

## Troubleshooting Common Issues

### Extension Not Found
- Verify PyForge CLI installation with Databricks extension
- Check entry points configuration in pyproject.toml
- Ensure extension dependencies are installed

### Volume Access Denied
- Verify Unity Catalog permissions
- Check volume path formatting
- Ensure catalog and schema exist

### Performance Issues
- Check cluster configuration and resources
- Verify data size expectations
- Monitor memory usage during tests

### Widget Configuration Errors
- Ensure all required widgets are defined
- Check widget value types and validation
- Verify widget names match code references

## Contributing to Tests

### Adding New Test Cases
1. Follow established patterns for error handling and metrics
2. Use consistent widget configuration approach
3. Include comprehensive documentation
4. Add performance measurements where appropriate

### Test Categories
- **Functional**: User-facing feature testing
- **Integration**: End-to-end workflow testing
- **Unit**: Component-level testing
- **Performance**: Benchmarking and optimization

### Documentation Requirements
- Clear test purpose and scope
- Step-by-step execution instructions
- Expected results and success criteria
- Troubleshooting guidance for common issues

## Testing Infrastructure Benefits

### Comprehensive Coverage
- **Multiple test levels**: Unit, integration, functional
- **Environment coverage**: Serverless and classic compute
- **Error scenarios**: Comprehensive edge case testing
- **Performance validation**: Benchmarking and optimization

### Maintainable Design
- **Consistent patterns**: Standardized approach across all tests
- **Modular structure**: Easy to extend and modify
- **Clear documentation**: Well-documented for team collaboration
- **Automated reporting**: Structured results and metrics

### Production Readiness
- **Real-world scenarios**: Tests mirror actual usage patterns
- **Scalability testing**: Large dataset and bulk operation validation
- **Security testing**: Permission and access control validation
- **Reliability testing**: Error handling and recovery validation

This testing infrastructure ensures the PyForge CLI Databricks extension is thoroughly validated across all environments and use cases, providing confidence for production deployment and ongoing maintenance.