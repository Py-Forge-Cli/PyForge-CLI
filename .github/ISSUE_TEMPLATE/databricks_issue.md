---
name: 🔥 Databricks Integration Issue
about: Report issues specific to Databricks environments, Unity Catalog, or Serverless runtimes
title: '[DATABRICKS] '
labels: 'databricks, unity-catalog, serverless, environment-specific'
assignees: ''
---

## 🔥 Databricks Integration Issue

### 🎯 Issue Type
- [ ] **Environment Detection**: PyForge not detecting Databricks environment correctly
- [ ] **Unity Catalog Volume**: Issues with volume path access or permissions
- [ ] **Serverless Runtime**: Databricks Serverless V1/V2 compatibility issues
- [ ] **Classic Runtime**: Databricks Classic cluster issues
- [ ] **Spark Context**: PySpark initialization or configuration problems
- [ ] **File Operations**: Reading/writing files in Databricks environment
- [ ] **Package Installation**: %pip install issues or dependency conflicts
- [ ] **Performance**: Slow performance in Databricks environment
- [ ] **Other**: [specify]

### 🏗️ Databricks Environment Details
**Runtime Information**:
- **Databricks Runtime**: [e.g., 13.3 LTS, 14.3 LTS, Serverless]
- **Cluster Type**: [ ] Single Node [ ] Multi-Node [ ] Serverless [ ] Job Cluster
- **Node Type**: [e.g., i3.xlarge, Standard_DS3_v2]
- **Databricks CLI Version**: [run `databricks --version`]
- **Unity Catalog**: [ ] Enabled [ ] Disabled [ ] Unknown

**PyForge Installation**:
- **PyForge CLI Version**: [1.0.9]
- **Installation Method**: [ ] %pip install [ ] Wheel upload [ ] Git clone [ ] Other: ___
- **Installation Command**: [exact command used]

### 🔍 Unity Catalog Context (if applicable)
- **Catalog Name**: [e.g., cortex_dev_catalog]
- **Schema Name**: [e.g., sandbox_testing]
- **Volume Path**: [e.g., /Volumes/catalog/schema/volume/]
- **Permissions**: [ ] Read [ ] Write [ ] Execute [ ] Unknown
- **Metastore**: [if known]

### 💻 Environment Detection Results
```python
# Run this in a Databricks notebook to gather environment info
import os
import sys
print(f"Python version: {sys.version}")
print(f"Is Databricks environment: {os.environ.get('DATABRICKS_RUNTIME_VERSION', 'Not detected')}")
print(f"Runtime version: {os.environ.get('DATABRICKS_RUNTIME_VERSION', 'N/A')}")
print(f"Cluster ID: {os.environ.get('DATABRICKS_CLUSTER_ID', 'N/A')}")
print(f"Unity Catalog enabled: {os.environ.get('UNITY_CATALOG_ENABLED', 'N/A')}")

# Check PyForge CLI installation
try:
    import pyforge_cli
    print(f"PyForge CLI version: {pyforge_cli.__version__}")
    print(f"PyForge CLI location: {pyforge_cli.__file__}")
except ImportError as e:
    print(f"PyForge CLI import error: {e}")
```

### 🐛 Problem Description
<!-- Describe the specific issue you're experiencing -->

### 🔄 Reproduction Steps
1. **Environment Setup**: [notebook, cluster configuration]
2. **PyForge Installation**: [how PyForge was installed]
3. **Command/Code Executed**: 
   ```python
   # Paste the exact code that causes the issue
   ```
4. **Expected Behavior**: [what should happen]
5. **Actual Behavior**: [what actually happens]

### 🚨 Error Messages and Stack Traces
```
# Paste complete error messages and stack traces here
```

### 📋 Databricks-Specific Troubleshooting

#### Environment Detection Test
```python
# Test environment detection
from pyforge_cli.extensions.databricks import environment
env_info = environment.detect_databricks_environment()
print(f"Environment detection result: {env_info}")
```

#### Unity Catalog Access Test
```python
# Test Unity Catalog volume access (if applicable)
import os
volume_path = "/Volumes/your_catalog/your_schema/your_volume/"
try:
    files = os.listdir(volume_path)
    print(f"Volume accessible: {len(files)} files found")
except Exception as e:
    print(f"Volume access error: {e}")
```

#### Spark Context Test
```python
# Test Spark context (if applicable)
try:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    print(f"Spark version: {spark.version}")
    print(f"Spark master: {spark.sparkContext.master}")
except Exception as e:
    print(f"Spark context error: {e}")
```

### 🎯 Expected Resolution
- [ ] **Environment Detection**: Properly detect Databricks environment
- [ ] **Volume Access**: Successfully read/write files to Unity Catalog volumes
- [ ] **Dependency Resolution**: Resolve package conflicts or missing dependencies
- [ ] **Performance**: Achieve acceptable performance in Databricks environment
- [ ] **Compatibility**: Work correctly with specified Databricks runtime version
- [ ] **Error Handling**: Provide clear error messages for Databricks-specific issues

### 🔧 Workarounds
<!-- List any temporary workarounds you've discovered -->

### 📊 Impact Assessment
- **Severity**: [ ] Blocks all Databricks usage [ ] Limits functionality [ ] Performance impact [ ] Minor inconvenience
- **Affected Users**: [ ] All Databricks users [ ] Specific runtime versions [ ] Specific configurations [ ] Few users
- **Business Impact**: [describe impact on workflows]

### 🔗 Related Information
- **Related Issues**: #
- **Documentation**: [links to relevant docs]
- **Databricks Support Case**: [if applicable]
- **Community Forum**: [if discussed elsewhere]

### 🧪 Testing Environment
<!-- If you have a test environment, please provide details -->
- **Test Dataset**: [size, format, source]
- **Test Scenario**: [specific use case being tested]
- **Cluster Configuration**: [node type, size, auto-scaling settings]

---

## 🔍 For PyForge Maintainers

### Investigation Areas
- [ ] **Environment Detection Logic**: Check detection algorithms
- [ ] **Runtime Compatibility**: Verify version compatibility matrix
- [ ] **Unity Catalog Integration**: Test volume operations
- [ ] **Dependency Management**: Check for version conflicts
- [ ] **Performance Optimization**: Profile Databricks performance

### Testing Requirements
- [ ] **Classic Runtime Test**: Verify fix works on Classic clusters
- [ ] **Serverless Runtime Test**: Verify fix works on Serverless
- [ ] **Unity Catalog Test**: Verify volume operations work correctly
- [ ] **Performance Test**: Ensure acceptable performance benchmarks
- [ ] **Integration Test**: End-to-end workflow validation

### Documentation Updates
- [ ] **Databricks Integration Guide**: Update if needed
- [ ] **Troubleshooting Guide**: Add new troubleshooting steps
- [ ] **Compatibility Matrix**: Update supported runtime versions
- [ ] **Known Issues**: Document any known limitations