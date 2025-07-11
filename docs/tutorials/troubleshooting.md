# Troubleshooting Guide

Solutions to common issues and optimization tips for PyForge CLI.

## Common Issues

### Installation Problems

**Issue**: `command not found: pyforge`
**Solution**: 
```bash
# Check if installed
pip show pyforge-cli

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### File Not Found Errors

**Issue**: `FileNotFoundError: No such file or directory`
**Solutions**:
- Check file path and spelling
- Use absolute paths
- Verify file permissions

### Permission Errors

**Issue**: Permission denied when writing output
**Solutions**:
```bash
# Check directory permissions
ls -la output_directory/

# Create output directory
mkdir -p output_directory

# Change permissions
chmod 755 output_directory/
```

## Performance Tips

### Large File Processing

For files over 100MB:
- Use verbose mode to monitor progress
- Ensure sufficient disk space (3x file size)
- Close other applications
- Consider processing in chunks

### Memory Optimization

```bash
# Monitor memory usage
top -p $(pgrep pyforge)

# Process with limited memory
ulimit -v 2048000  # Limit to 2GB
pyforge convert large_file.xlsx
```

## MDF Tools Troubleshooting

### Docker Desktop Issues

**Issue**: `Docker daemon is not responding`

**Solutions**:
```bash
# Check Docker Desktop status
docker info

# Restart Docker Desktop manually
# macOS: Click Docker Desktop in menu bar → Restart
# Windows: Right-click Docker Desktop in system tray → Restart

# Check system resources
df -h  # Check disk space (need 4GB minimum)
free -h  # Check memory (need 4GB minimum)
```

**Issue**: `Docker Desktop not starting`

**Solutions**:
1. **Restart Computer**: Often resolves daemon startup issues
2. **Check System Resources**: Ensure adequate memory and disk space
3. **Update Docker**: Download latest version from docker.com
4. **Reset Docker**: 
   ```bash
   # macOS/Linux: Factory reset in Docker Desktop settings
   # Or manually clean up
   docker system prune -a
   ```

### SQL Server Container Issues

**Issue**: `SQL Server connection failed`

**Diagnostic Steps**:
```bash
# Check overall status
pyforge mdf-tools status

# View container logs
pyforge mdf-tools logs -n 20

# Test Docker connectivity
docker ps | grep pyforge-sql-server

# Check container details
docker inspect pyforge-sql-server
```

**Solutions**:
```bash
# Restart SQL Server container
pyforge mdf-tools restart

# If restart fails, recreate container
pyforge mdf-tools uninstall
pyforge install mdf-tools

# Check if port is available
lsof -i :1433  # Should show SQL Server process
```

**Issue**: `Container exits immediately`

**Causes & Solutions**:
1. **Insufficient Memory**: SQL Server needs 4GB minimum
   ```bash
   # Check Docker memory allocation
   docker system info | grep Memory
   ```

2. **Invalid Password**: Password must meet SQL Server requirements
   ```bash
   # Reinstall with strong password
   pyforge install mdf-tools --password "NewSecure123!"
   ```

3. **Port Conflict**: Another service using port 1433
   ```bash
   # Use different port
   pyforge install mdf-tools --port 1434
   ```

### Installation Issues

**Issue**: `Docker SDK not available`

**Solutions**:
```bash
# Install Docker SDK manually
pip install docker

# Check Python environment
which python
pip list | grep docker
```

**Issue**: `Permission denied` during installation

**Solutions**:
```bash
# macOS: Grant Docker Desktop permissions in System Preferences
# Linux: Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in

# Windows: Run as Administrator or check WSL2 setup
```

**Issue**: `Network timeout` during image download

**Solutions**:
```bash
# Check internet connection
ping mcr.microsoft.com

# Retry installation
pyforge install mdf-tools

# Use different DNS if needed
# Change DNS to 8.8.8.8 in network settings
```

### Configuration Issues

**Issue**: `Configuration file not found`

**Solutions**:
```bash
# Check config path
ls -la ~/.pyforge/

# Recreate configuration
pyforge install mdf-tools

# Manually verify config
pyforge mdf-tools config
```

**Issue**: `Connection string errors`

**Solutions**:
```bash
# Verify configuration
pyforge mdf-tools config

# Test basic connectivity
pyforge mdf-tools test

# Check password in config
# Note: Password should match installation settings
```

### Platform-Specific Issues

#### macOS Issues

**Issue**: `Homebrew not found` during Docker installation

**Solutions**:
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```

**Issue**: `Docker Desktop requires macOS 10.15+`

**Solutions**:
- Upgrade macOS to Monterey or later
- Use manual Docker installation instructions
- Consider using Docker via lima/colima as alternative

#### Windows Issues

**Issue**: `WSL2 required` for Docker Desktop

**Solutions**:
```powershell
# Enable WSL2
wsl --install

# Update WSL2 kernel
wsl --update

# Set WSL2 as default
wsl --set-default-version 2
```

**Issue**: `Winget not found` during installation

**Solutions**:
```powershell
# Install App Installer from Microsoft Store
# Or download from GitHub:
# https://github.com/microsoft/winget-cli/releases

# Alternative: Use Chocolatey
choco install docker-desktop
```

#### Linux Issues

**Issue**: `systemd not managing Docker`

**Solutions**:
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Check service status
sudo systemctl status docker
```

**Issue**: `Docker compose not found`

**Solutions**:
```bash
# Install docker-compose
sudo apt-get install docker-compose  # Ubuntu/Debian
sudo yum install docker-compose       # CentOS/RHEL

# Or use pip
pip install docker-compose
```

### Advanced Troubleshooting

#### Debug Mode

Enable verbose logging for detailed diagnostics:
```bash
# Run with verbose output
pyforge install mdf-tools --non-interactive -v

# Check system logs
# macOS
tail -f /var/log/system.log | grep -i docker

# Linux
journalctl -f -u docker
```

#### Container Inspection

```bash
# Get detailed container information
docker inspect pyforge-sql-server

# Check container resource usage
docker stats pyforge-sql-server

# Access container shell for debugging
docker exec -it pyforge-sql-server /bin/bash

# Test SQL Server directly in container
docker exec pyforge-sql-server /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "PyForge@2024!" -Q "SELECT @@VERSION" -C
```

#### Network Debugging

```bash
# Check Docker networks
docker network ls

# Inspect bridge network
docker network inspect bridge

# Test port connectivity
telnet localhost 1433
nc -zv localhost 1433
```

### Prevention Tips

1. **Regular Maintenance**:
   ```bash
   # Keep Docker images updated
   docker pull mcr.microsoft.com/mssql/server:2019-latest
   
   # Clean up unused resources
   docker system prune
   ```

2. **Monitor Resources**:
   ```bash
   # Check system resources before starting
   pyforge mdf-tools status
   
   # Monitor during processing
   docker stats
   ```

3. **Backup Configuration**:
   ```bash
   # Backup config file
   cp ~/.pyforge/mdf-config.json ~/.pyforge/mdf-config.json.backup
   ```

### Getting Support

If issues persist after trying these solutions:

1. **Collect Diagnostic Information**:
   ```bash
   # System information
   uname -a
   docker version
   docker info
   
   # PyForge status
   pyforge mdf-tools status
   pyforge mdf-tools logs -n 50
   
   # Configuration
   pyforge mdf-tools config
   ```

2. **Check Known Issues**: [GitHub Issues](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)

3. **Report Bugs**: Create new issue with diagnostic information

4. **Community Support**: [GitHub Discussions](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions)

## Databricks Serverless Troubleshooting

### Installation Issues

**Issue**: `ModuleNotFoundError: No module named 'pyforge_cli'`

**Solutions**:
```python
# Check if wheel is properly installed
%pip list | grep pyforge

# Reinstall with proper PyPI index (required for Databricks Serverless)
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/pyforge_cli-1.0.9-py3-none-any.whl --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

# Restart Python environment
dbutils.library.restartPython()
```

**Issue**: `pip install fails with SSL/certificate errors`

**Solutions**:
```python
# Use trusted host and proper index URL
%pip install package-name --index-url https://pypi.org/simple/ --trusted-host pypi.org

# For corporate environments, check with IT for approved PyPI URLs
```

### Unity Catalog Volume Path Problems

**Issue**: `FileNotFoundError: dbfs:/Volumes/... path not found`

**Solutions**:
```python
# Check volume permissions
%sql SHOW VOLUMES IN cortex_dev_catalog.sandbox_testing;

# Verify volume exists and is accessible
%fs ls dbfs:/Volumes/cortex_dev_catalog/sandbox_testing/

# Check username in path
import os
username = spark.sql("SELECT current_user()").collect()[0][0]
print(f"Current user: {username}")

# Use correct path format
wheel_path = f"/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/pyforge_cli-1.0.9-py3-none-any.whl"
```

**Issue**: `Permission denied accessing Unity Catalog volume`

**Solutions**:
```python
# Check catalog permissions
%sql SHOW GRANTS ON CATALOG cortex_dev_catalog;

# Verify schema access
%sql SHOW GRANTS ON SCHEMA cortex_dev_catalog.sandbox_testing;

# Check volume permissions
%sql SHOW GRANTS ON VOLUME cortex_dev_catalog.sandbox_testing.pkgs;
```

### Subprocess Backend Errors

**Issue**: `subprocess-backend is not available`

**Solutions**:
```python
# Install subprocess support for Databricks Serverless
%pip install subprocess32 --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

# Alternative: Use environment variable
import os
os.environ['PYFORGE_BACKEND'] = 'python'

# Restart Python after installation
dbutils.library.restartPython()
```

**Issue**: `Cannot run shell commands in Databricks Serverless`

**Solutions**:
```python
# Use Python-only conversion methods
from pyforge_cli.core.converter_registry import ConverterRegistry

# Initialize registry
registry = ConverterRegistry()

# Convert using Python backend
result = registry.convert_file(
    input_file="sample.xlsx",
    output_file="output.py",
    backend="python"
)
```

### Memory and Performance Issues

**Issue**: `Memory allocation failed` or `Out of memory`

**Solutions**:
```python
# Monitor memory usage
import psutil
print(f"Available memory: {psutil.virtual_memory().available / (1024**3):.2f} GB")

# Process files in smaller chunks
import pandas as pd

def process_large_file(file_path, chunk_size=10000):
    chunks = []
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        processed_chunk = chunk.head(1000)  # Process smaller subset
        chunks.append(processed_chunk)
    return pd.concat(chunks, ignore_index=True)

# Use memory-efficient options
pyforge_options = {
    'memory_limit': '1GB',
    'chunk_size': 5000,
    'optimize_memory': True
}
```

**Issue**: `Spark job fails with large files`

**Solutions**:
```python
# Configure Spark for large file processing
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB")

# Use Spark-native operations when possible
df = spark.read.option("header", "true").csv(file_path)
df.write.mode("overwrite").parquet(output_path)
```

### Common Error Messages and Fixes

**Issue**: `ImportError: cannot import name 'pyforge_cli'`

**Solutions**:
```python
# Check Python path
import sys
print(sys.path)

# Verify installation location
import subprocess
result = subprocess.run([sys.executable, "-m", "pip", "show", "pyforge-cli"], 
                       capture_output=True, text=True)
print(result.stdout)

# Reinstall if needed
%pip install pyforge-cli --force-reinstall --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
```

**Issue**: `ConverterRegistry not found`

**Solutions**:
```python
# Import the correct module
from pyforge_cli.core.converter_registry import ConverterRegistry

# Initialize registry
registry = ConverterRegistry()

# Check available converters
print(registry.get_supported_formats())
```

**Issue**: `pyspark.sql.utils.AnalysisException: Path does not exist`

**Solutions**:
```python
# Check if file exists in DBFS
%fs ls dbfs:/path/to/file

# Use proper DBFS path format
dbfs_path = "dbfs:/Volumes/catalog/schema/volume/file.csv"

# Or use /dbfs/ mount point
mount_path = "/dbfs/Volumes/catalog/schema/volume/file.csv"

# Verify file accessibility
import os
if os.path.exists(mount_path):
    print("File exists and accessible")
else:
    print("File not found or not accessible")
```

### Diagnostic Commands for Databricks

**Environment Diagnostics**:
```python
# Check Databricks environment
print(f"Databricks Runtime: {spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion')}")
print(f"Scala Version: {spark.version}")
print(f"Python Version: {sys.version}")

# Check cluster configuration
print(f"Driver node type: {spark.conf.get('spark.databricks.clusterUsageTags.driverNodeTypeId')}")
print(f"Worker node type: {spark.conf.get('spark.databricks.clusterUsageTags.workerNodeTypeId')}")

# Check available memory
import psutil
memory = psutil.virtual_memory()
print(f"Total memory: {memory.total / (1024**3):.2f} GB")
print(f"Available memory: {memory.available / (1024**3):.2f} GB")
```

**PyForge Diagnostics**:
```python
# Check PyForge installation
try:
    import pyforge_cli
    print(f"PyForge CLI version: {pyforge_cli.__version__}")
except ImportError as e:
    print(f"PyForge CLI not installed: {e}")

# Check converter registry
try:
    from pyforge_cli.core.converter_registry import ConverterRegistry
    registry = ConverterRegistry()
    print(f"Available converters: {registry.get_supported_formats()}")
except Exception as e:
    print(f"Converter registry error: {e}")

# Check backend support
try:
    from pyforge_cli.core.backend_detector import BackendDetector
    detector = BackendDetector()
    print(f"Available backends: {detector.get_available_backends()}")
except Exception as e:
    print(f"Backend detection error: {e}")
```

**Volume and Path Diagnostics**:
```python
# Check volume access
try:
    %fs ls dbfs:/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/
    print("Volume accessible")
except Exception as e:
    print(f"Volume access error: {e}")

# Check current user
current_user = spark.sql("SELECT current_user()").collect()[0][0]
print(f"Current user: {current_user}")

# Check catalog permissions
try:
    catalogs = spark.sql("SHOW CATALOGS").collect()
    print(f"Available catalogs: {[row.catalog for row in catalogs]}")
except Exception as e:
    print(f"Catalog access error: {e}")
```

### Best Practices for Databricks Serverless

1. **Dependency Management**:
   ```python
   # Always use proper PyPI index for installations
   %pip install package-name --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org
   
   # Restart Python after installations
   dbutils.library.restartPython()
   ```

2. **File Path Handling**:
   ```python
   # Use Unity Catalog volumes for file storage
   volume_path = "dbfs:/Volumes/catalog/schema/volume/file.ext"
   
   # Use /dbfs/ mount for local file operations
   local_path = "/dbfs/Volumes/catalog/schema/volume/file.ext"
   ```

3. **Memory Management**:
   ```python
   # Monitor memory usage
   import psutil
   memory_info = psutil.virtual_memory()
   
   # Process files in chunks for large datasets
   chunk_size = 10000
   for chunk in pd.read_csv(file_path, chunksize=chunk_size):
       process_chunk(chunk)
   ```

4. **Error Handling**:
   ```python
   # Wrap operations in try-except blocks
   try:
       result = pyforge_convert(input_file, output_file)
   except ImportError as e:
       print(f"Module import error: {e}")
   except FileNotFoundError as e:
       print(f"File not found: {e}")
   except Exception as e:
       print(f"Conversion error: {e}")
   ```

5. **Performance Optimization**:
   ```python
   # Use Spark-native operations when possible
   df = spark.read.option("header", "true").csv(input_path)
   df.write.mode("overwrite").parquet(output_path)
   
   # Configure Spark for optimal performance
   spark.conf.set("spark.sql.adaptive.enabled", "true")
   spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
   ```

### Version-Specific Fixes (v1.0.9+)

**Fixed Issues in v1.0.9**:
- Improved dependency management for Databricks Serverless
- Better error handling for Unity Catalog volumes
- Enhanced subprocess backend detection
- Fixed converter registry initialization issues

**New Features in v1.0.9**:
- Automatic backend detection for Databricks environments
- Improved memory management for large files
- Better error messages for common issues
- Enhanced logging for troubleshooting

**Migration from Earlier Versions**:
```python
# Uninstall old version
%pip uninstall pyforge-cli -y

# Install latest version
%pip install /Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/pyforge_cli-1.0.9-py3-none-any.whl --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

# Restart Python
dbutils.library.restartPython()

# Verify installation
import pyforge_cli
print(f"PyForge CLI version: {pyforge_cli.__version__}")
```

### Getting Support for Databricks Issues

If Databricks-specific issues persist:

1. **Collect Databricks Diagnostic Information**:
   ```python
   # Runtime information
   print(f"Runtime: {spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion')}")
   print(f"Cluster ID: {spark.conf.get('spark.databricks.clusterUsageTags.clusterId')}")
   
   # User and permissions
   print(f"Current user: {spark.sql('SELECT current_user()').collect()[0][0]}")
   
   # Volume access
   try:
       %fs ls dbfs:/Volumes/cortex_dev_catalog/sandbox_testing/
       print("Volume accessible")
   except Exception as e:
       print(f"Volume error: {e}")
   ```

2. **Check Databricks Community Forums**: [Databricks Community](https://community.databricks.com/)

3. **Consult Databricks Documentation**: [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html)

4. **Report PyForge-specific Issues**: Include Databricks runtime and environment details

## Getting Help

- Check [CLI Reference](../reference/cli-reference.md)
- Visit [GitHub Issues](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)
- Ask in [Discussions](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions)