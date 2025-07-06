# PyForge CLI User Migration Guide

This guide helps existing PyForge CLI users understand the new Databricks Extension and how to migrate to using the enhanced functionality without any breaking changes.

## Summary

**Good News**: The Databricks Extension introduces **no breaking changes** to existing PyForge CLI functionality. All your current commands, scripts, and workflows will continue to work exactly as before.

## What's New

The Databricks Extension adds powerful new capabilities while maintaining full backward compatibility:

### New Features Available
- **Environment Auto-Detection**: Automatically detects Databricks environments
- **Unity Catalog Volume Integration**: Seamless dataset management
- **PySpark Optimization**: Automatic performance enhancements in Databricks
- **Sample Dataset Installation**: Easy access to curated datasets
- **Serverless Environment Support**: Optimized for Databricks serverless compute

### Your Existing Workflows Remain Unchanged
- All current `pyforge convert` commands work exactly the same
- No changes to command syntax or options
- Same file format support and conversion quality
- Identical CLI interface and behavior

## Installation Options

### Option 1: Automatic Installation (Recommended)
The Databricks Extension will be included in future PyForge CLI releases:

```bash
# Update to latest version (when available)
pip install --upgrade pyforge-cli
```

### Option 2: Extension-Only Installation
Install just the Databricks Extension:

```bash
# Install the extension separately
pip install pyforge-databricks-extension
```

### Option 3: Development Installation
For early access or testing:

```bash
# Clone and install from source
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI
pip install -e ".[databricks]"
```

## Verification

Confirm the extension is working:

```bash
# Check extension status
pyforge --list-extensions

# Should show:
# Available Extensions:
#   ✅ databricks v1.0.0 - Databricks integration with Unity Catalog support
```

## New Commands Available

The extension adds helpful new commands, but **your existing commands remain unchanged**:

### Install Sample Datasets
```bash
# Install curated datasets to Unity Catalog Volume
pyforge install-datasets --volume-path /Volumes/catalog/schema/volume
```

### List Available Volumes
```bash
# Show Unity Catalog Volumes (in Databricks environment)
pyforge list-volumes
```

### Check Environment
```bash
# Display detected environment information
pyforge env-info
```

## Behavior Changes (Enhancements Only)

### In Databricks Environments
When running in Databricks, you'll automatically get:

1. **PySpark Acceleration**: Large datasets use PySpark for better performance
2. **Serverless Optimization**: Automatic tuning for serverless environments
3. **Unity Catalog Integration**: Seamless volume access
4. **Enhanced Logging**: Better error messages and debugging info

### In Non-Databricks Environments
- **Zero changes**: Exact same behavior as before
- Extension remains dormant and doesn't affect performance

## Migration Examples

### Example 1: Basic Conversion (No Changes)
```bash
# This command works exactly the same as before
pyforge convert data.csv output.parquet

# In Databricks: Gets automatic PySpark optimization
# Outside Databricks: Works exactly as before
```

### Example 2: Batch Processing (No Changes)
```bash
# Your existing scripts continue to work
for file in *.csv; do
    pyforge convert "$file" "${file%.csv}.parquet"
done
```

### Example 3: CI/CD Pipelines (No Changes)
```yaml
# GitHub Actions, Jenkins, etc. - no changes needed
- name: Convert data
  run: pyforge convert input.csv output.parquet
```

## Configuration

### No Configuration Required
The extension works out-of-the-box with sensible defaults.

### Optional Configuration
Create `~/.pyforge/databricks.json` for custom settings:

```json
{
  "auto_detect_environment": true,
  "enable_pyspark_optimization": true,
  "default_volume_path": "/Volumes/main/default/pyforge",
  "performance_logging": false
}
```

## Troubleshooting

### Common Questions

#### Q: Will this break my existing scripts?
**A**: No. All existing functionality remains identical.

#### Q: Do I need to change my CI/CD pipelines?
**A**: No changes required. The extension enhances but doesn't alter existing behavior.

#### Q: What if I don't use Databricks?
**A**: The extension remains inactive and has zero impact on your workflows.

#### Q: Can I disable the extension?
**A**: Yes, set environment variable: `export DATABRICKS_EXTENSION_DISABLED=true`

### Issues and Solutions

#### Extension Not Detected in Databricks
```bash
# Check environment variables
env | grep DATABRICKS

# Verify extension installation
pyforge --list-extensions

# Enable debug logging
pyforge convert data.csv output.parquet --verbose
```

#### Performance Issues
```bash
# Disable PySpark optimization if needed
pyforge convert data.csv output.parquet --no-pyspark

# Check system resources
pyforge env-info
```

#### Volume Access Problems
```bash
# Check volume permissions
pyforge list-volumes

# Verify volume path
ls /Volumes/catalog/schema/volume/
```

## FAQ

### General Questions

**Q: Is this a major version change?**
A: No, this is a minor enhancement that maintains full backward compatibility.

**Q: Do I need to retrain my team?**
A: No, all existing commands and workflows remain the same.

**Q: Will this affect performance outside Databricks?**
A: No impact. The extension only activates in Databricks environments.

### Technical Questions

**Q: How does environment detection work?**
A: The extension checks for `DATABRICKS_RUNTIME_VERSION` environment variable.

**Q: Can I use this with custom Spark configurations?**
A: Yes, the extension respects existing Spark configurations.

**Q: Does this work with Databricks Connect?**
A: Yes, the extension automatically detects Databricks Connect environments.

### Databricks-Specific Questions

**Q: Which Databricks Runtime versions are supported?**
A: All current LTS and standard runtime versions (7.3+).

**Q: Does this work with Databricks SQL warehouses?**
A: The extension optimizes for compute clusters; SQL warehouses use standard behavior.

**Q: Can I use this with ML Runtime?**
A: Yes, full compatibility with Databricks ML Runtime.

## Advanced Usage

### Custom Environment Detection
```python
# For programmatic usage
from pyforge_cli.extensions.databricks import DatabricksExtension

ext = DatabricksExtension()
if ext.is_available():
    env_info = ext.hook_environment_detection()
    print(f"Runtime: {env_info.get('runtime_version')}")
    print(f"Serverless: {env_info.get('serverless')}")
```

### Performance Tuning
```bash
# Explicit PySpark options
pyforge convert large_dataset.csv output.parquet \
    --spark-config spark.sql.adaptive.enabled=true \
    --spark-config spark.sql.adaptive.coalescePartitions.enabled=true
```

### Volume Management
```bash
# Install datasets with custom configuration
pyforge install-datasets \
    --volume-path /Volumes/main/datasets/pyforge \
    --include-samples true \
    --format parquet
```

## Best Practices

### For Databricks Users
1. **Use Volume Paths**: Store datasets in Unity Catalog Volumes for better management
2. **Enable Adaptive Query Execution**: Let the extension optimize Spark configurations
3. **Monitor Performance**: Use `--verbose` to see optimization details
4. **Regular Updates**: Keep the extension updated for latest optimizations

### For Non-Databricks Users
1. **No Action Required**: Continue using PyForge CLI as normal
2. **Monitor for Updates**: The extension may add value in future cloud environments
3. **Consider Cloud Migration**: The extension makes Databricks adoption seamless

## Getting Help

### Documentation
- [Main Documentation](../README.md)
- [Extension Developer Guide](../api/extension-developer-guide.md)
- [API Reference](../api/)

### Community Support
- [GitHub Discussions](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions)
- [Issues](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/pyforge-cli)

### Commercial Support
Contact the PyForge CLI team for enterprise support and custom integration services.

## What's Next

### Upcoming Features
- **Azure Synapse Integration**: Similar extension for Azure environments
- **AWS EMR Support**: Optimizations for Amazon EMR
- **Google Dataproc**: Integration with Google Cloud Dataproc
- **Snowflake Connector**: Direct integration with Snowflake

### Community Extensions
The extension system allows third-party developers to create specialized extensions. See the [Extension Developer Guide](../api/extension-developer-guide.md) to build your own.

---

**Remember**: This migration introduces only enhancements and new capabilities. Your existing workflows, scripts, and integrations continue to work without any changes.