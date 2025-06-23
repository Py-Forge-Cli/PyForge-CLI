# Tools Prerequisites

Before processing certain file formats, you may need to install additional tools and dependencies. PyForge CLI provides automated installers to set up these prerequisites with minimal effort.

## Overview

Some file formats require specialized software or services to process effectively. Rather than requiring manual setup, PyForge CLI includes automated installers that handle the complete setup process.

**Available Tool Installers:**
- **MDF Tools**: Docker Desktop + SQL Server Express for SQL Server MDF files
- **Future Tools**: Additional installers will be added for other specialized formats

## MDF Tools Installation

### What are MDF Tools?

MDF Tools provide the infrastructure needed to process SQL Server Master Database Files (.mdf). This includes:

- **Docker Desktop**: Container runtime for SQL Server
- **SQL Server Express 2019**: Database engine for MDF file processing
- **Container Management**: Lifecycle management tools for the database

### Quick Installation

```bash
# Install MDF processing tools
pyforge install mdf-tools

# Verify installation
pyforge mdf-tools status

# Test connectivity
pyforge mdf-tools test
```

### System Requirements

**Minimum Requirements:**
- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **Memory**: 4GB RAM total (1.4GB for SQL Server + 2.6GB for host)
- **Storage**: 4GB free space (2GB for Docker + 2GB for SQL Server)
- **Network**: Internet connection (~700MB download)

**Recommended Requirements:**
- **Memory**: 8GB RAM (for optimal performance)
- **Storage**: 20GB free space (for multiple databases)
- **CPU**: 4+ cores (SQL Server Express limited to 4 cores max)

### Installation Process

The MDF Tools installer follows a 5-stage automated process:

#### Stage 1: System Requirements Check
```
✓ Operating System: macOS 14.5.0 (supported)
✓ Docker Desktop: Installed
✓ Docker SDK for Python: Available
```

#### Stage 2: Docker Setup (if needed)
```
[2/5] Docker Installation Required
Docker Desktop is required for MDF file conversion.

Would you like to:
  1. Install automatically using Homebrew (recommended)
  2. Get installation instructions
  3. Skip (I'll install manually)
```

#### Stage 3: Docker Startup
```
[3/5] Starting Docker Desktop...
✓ Docker Desktop is running
```

#### Stage 4: SQL Server Express Setup
```
[4/5] Setting up SQL Server Express...
📥 Pulling SQL Server image: mcr.microsoft.com/mssql/server:2019-latest
🚀 Creating SQL Server container...
⏳ Waiting for SQL Server to start (this may take a minute)...
✓ SQL Server is ready
```

#### Stage 5: Configuration Complete
```
[5/5] Installation Complete!
              SQL Server Connection Details              
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property    ┃ Value                                   ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Host        │ localhost                               │
│ Port        │ 1433                                    │
│ Username    │ sa                                      │
│ Password    │ PyForge@2024!                           │
│ Container   │ pyforge-sql-server                      │
│ Config File │ /Users/username/.pyforge/mdf-config.json│
└─────────────┴─────────────────────────────────────────┘
```

### Container Management

After installation, manage the SQL Server container with these commands:

#### Check Status
```bash
pyforge mdf-tools status
```

Shows comprehensive status of all components:
```
                      MDF Tools Status                       
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Component             ┃ Status ┃ Details                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Docker Installed      │ ✓ OK   │ Docker command available │
│ Docker Running        │ ✓ OK   │ Docker daemon responsive │
│ SQL Container Exists  │ ✓ OK   │ Container created        │
│ SQL Container Running │ ✓ OK   │ Container active         │
│ SQL Server Responding │ ✓ OK   │ Database accessible      │
│ Configuration File    │ ✓ OK   │ Settings saved           │
└───────────────────────┴────────┴──────────────────────────┘

✅ All systems operational - ready for MDF processing!
```

#### Lifecycle Management
```bash
# Start SQL Server (if stopped)
pyforge mdf-tools start

# Stop SQL Server (when finished)
pyforge mdf-tools stop

# Restart SQL Server
pyforge mdf-tools restart

# View SQL Server logs
pyforge mdf-tools logs

# Test connectivity
pyforge mdf-tools test

# Show configuration
pyforge mdf-tools config
```

#### Complete Removal
```bash
# Remove everything (with confirmation)
pyforge mdf-tools uninstall
```

### SQL Server Express Limitations

**Important Constraints to Consider:**

| Limitation | Value | Impact |
|------------|-------|---------|
| **Database Size** | 10 GB maximum | Large MDF files (>10GB) cannot be processed |
| **Memory** | 1.4 GB buffer pool | Performance limited with large datasets |
| **CPU Cores** | 4 cores maximum | Cannot utilize high-core systems fully |
| **Parallelism** | Disabled (DOP=1) | Single-threaded query execution |

**When to Consider Upgrading:**
- MDF files larger than 10 GB
- Need for high-performance processing
- Multiple concurrent users
- Advanced SQL Server features

### Troubleshooting

#### Common Issues

**Docker Desktop Not Starting:**
```bash
# Check Docker status
docker info

# Restart Docker Desktop manually
# macOS: Click Docker in menu bar → Restart
# Windows: Right-click Docker in system tray → Restart
```

**SQL Server Connection Failed:**
```bash
# Check container status
pyforge mdf-tools status

# View detailed logs
pyforge mdf-tools logs -n 20

# Restart SQL Server
pyforge mdf-tools restart
```

**Port Already in Use:**
```bash
# Use custom port during installation
pyforge install mdf-tools --port 1434
```

#### Getting Help

For detailed troubleshooting, see:
- [MDF Tools Installer Documentation](../converters/mdf-tools-installer.md)
- [Troubleshooting Guide](../tutorials/troubleshooting.md#mdf-tools-troubleshooting)

## Platform-Specific Notes

### macOS
- **Docker Installation**: Automatic via Homebrew
- **Permissions**: May require admin privileges for Docker
- **Performance**: Excellent on both Intel and Apple Silicon

### Windows
- **Docker Installation**: Automatic via Winget
- **WSL2 Required**: Docker Desktop requires WSL2 for containers
- **Restart Required**: Computer restart may be needed after Docker installation

### Linux
- **Docker Installation**: Manual via package manager (apt/yum)
- **User Groups**: Add user to docker group: `sudo usermod -aG docker $USER`
- **Service Management**: Enable Docker service: `sudo systemctl enable docker`

## Configuration Files

### MDF Tools Configuration
Location: `~/.pyforge/mdf-config.json`

```json
{
  "sql_server": {
    "container_name": "pyforge-sql-server",
    "image": "mcr.microsoft.com/mssql/server:2019-latest",
    "host": "localhost",
    "port": 1433,
    "username": "sa",
    "password": "PyForge@2024!",
    "data_volume": "pyforge-sql-data",
    "mdf_volume": "pyforge-mdf-files"
  },
  "docker": {
    "installed_version": "Docker version 20.10.17",
    "installation_date": "2024-01-15T10:30:00Z"
  },
  "installer_version": "1.0.0"
}
```

### Customization Options

**Custom Password:**
```bash
pyforge install mdf-tools --password "YourSecurePassword123!"
```

**Custom Port:**
```bash
pyforge install mdf-tools --port 1434
```

**Non-Interactive Mode:**
```bash
pyforge install mdf-tools --non-interactive
```

## Future Tools

PyForge CLI will continue to add automated installers for other specialized file formats that require additional software dependencies.

**Planned Tool Installers:**
- Oracle database tools (for .dbf files from Oracle)
- SAP tools (for SAP data formats)
- Legacy database tools (for older database formats)

## Security Considerations

### Password Security
- Default passwords meet SQL Server complexity requirements
- Custom passwords should be strong (8+ characters, mixed case, numbers, symbols)
- Passwords stored locally in configuration files (not transmitted)

### Network Security
- SQL Server only accessible on localhost by default
- Container isolated in Docker bridge network
- No external network exposure unless explicitly configured

### Container Security
- Uses official Microsoft SQL Server images
- Automatic security updates through image updates
- Container runs with minimal privileges

## Best Practices

### Resource Management
1. **Monitor System Resources**: Check available memory and disk space
2. **Stop When Not Needed**: Stop SQL Server container when not processing MDF files
3. **Regular Cleanup**: Remove old containers and images periodically

### Performance Optimization
1. **Adequate RAM**: Ensure 8GB+ RAM for optimal performance
2. **SSD Storage**: Use SSD for Docker volumes when possible
3. **Close Other Applications**: Free up resources during large file processing

### Maintenance
1. **Keep Docker Updated**: Regularly update Docker Desktop
2. **Update SQL Server Image**: Periodically pull latest SQL Server image
3. **Backup Configuration**: Save configuration files before major changes

## Related Documentation

- [MDF Tools Installer](../converters/mdf-tools-installer.md) - Complete installation guide
- [Database Files](../converters/database-files.md) - Database conversion overview
- [CLI Reference](../reference/cli-reference.md) - All command documentation
- [Troubleshooting](../tutorials/troubleshooting.md) - Common issues and solutions