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

## Getting Help

- Check [CLI Reference](../reference/cli-reference.md)
- Visit [GitHub Issues](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)
- Ask in [Discussions](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions)