# MDF Tools Installer

## Overview

The MDF Tools Installer provides an interactive setup wizard that automates the installation and configuration of prerequisites needed for processing SQL Server MDF (Master Database Files). This includes Docker Desktop installation, SQL Server Express container setup, and comprehensive container management tools.

## Features

- **🐋 Docker Desktop Integration**: Automatic detection and installation across platforms
- **🗄️ SQL Server Express Setup**: Containerized SQL Server 2019 Express with persistent storage
- **⚙️ Interactive Configuration**: Guided setup with customizable passwords and ports
- **📊 Real-time Status Monitoring**: Comprehensive health checks for all components
- **🔧 Container Lifecycle Management**: Complete control over SQL Server container
- **🔒 Secure Configuration**: Encrypted password storage and configurable security settings

## Quick Start

```bash
# Install MDF processing tools
pyforge install mdf-tools

# Check installation status
pyforge mdf-tools status

# Test SQL Server connectivity
pyforge mdf-tools test
```

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **Memory**: 4GB RAM total (1.4GB for SQL Server + 2.6GB for host system)
- **Storage**: 4GB free space (2GB for Docker images + 2GB for SQL Server data)
- **Network**: Internet connection for downloading Docker images (~700MB)
- **Docker**: Docker Desktop 4.0+ with container support

### Recommended Requirements
- **Memory**: 8GB RAM (for optimal performance with multiple databases)
- **Storage**: 20GB free space (for multiple MDF files and conversions)
- **CPU**: 4+ cores (though SQL Server Express limited to 4 cores max)
- **Network**: Broadband connection for faster image downloads

### SQL Server Express Constraints
- **Maximum Database Size**: 10GB per attached MDF file
- **Memory Limit**: 1.4GB buffer pool (cannot be increased)
- **CPU Utilization**: 1 socket or 4 cores maximum
- **Concurrent Connections**: Practical limit of 5-10 users
- **Query Parallelism**: Disabled (DOP = 1)

### Supported Platforms
- ✅ **macOS** (Intel and Apple Silicon)
- ✅ **Windows** (Windows 10/11 with WSL2)
- ✅ **Linux** (Ubuntu, CentOS, RHEL, Debian)

## Architecture Overview

### MDF Tools Installation Architecture

```mermaid
graph TB
    subgraph "Host System"
        CLI[PyForge CLI]
        USER[User]
        CONFIG[~/.pyforge/mdf-config.json]
    end
    
    subgraph "Docker Desktop"
        DAEMON[Docker Daemon]
        subgraph "SQL Server Container"
            SQLSERVER[SQL Server Express 2019]
            SQLCMD[sqlcmd Tools]
            MASTER[master database]
            ATTACHED[Attached MDF Database]
        end
        subgraph "Docker Volumes"
            DATAVOL[pyforge-sql-data<br/>SQL Server Data]
            MDFVOL[pyforge-mdf-files<br/>MDF Files Mount]
        end
    end
    
    USER -->|pyforge install mdf-tools| CLI
    CLI -->|1. Check Docker| DAEMON
    CLI -->|2. Pull Image| DAEMON
    CLI -->|3. Create Container| SQLSERVER
    CLI -->|4. Configure Volumes| DATAVOL
    CLI -->|4. Configure Volumes| MDFVOL
    CLI -->|5. Test Connection| SQLCMD
    CLI -->|6. Save Config| CONFIG
    
    SQLSERVER -.->|Port 1433| CLI
    DATAVOL -.->|Mount /var/opt/mssql| SQLSERVER
    MDFVOL -.->|Mount /mdf-files| SQLSERVER
    
    classDef user fill:#e1f5fe
    classDef cli fill:#f3e5f5
    classDef docker fill:#e8f5e8
    classDef sql fill:#fff3e0
    classDef config fill:#fce4ec
    
    class USER user
    class CLI cli
    class DAEMON,DATAVOL,MDFVOL docker
    class SQLSERVER,SQLCMD,MASTER,ATTACHED sql
    class CONFIG config
```

### Installation Workflow Components

**1. Host System Components:**
- **PyForge CLI**: Main application orchestrating the installation
- **Configuration File**: Persistent settings stored locally
- **Docker Desktop**: Container runtime environment

**2. Container Infrastructure:**
- **SQL Server Express 2019**: Database engine for MDF processing
- **Persistent Volumes**: Data survival across container restarts
- **Network Mapping**: Port 1433 exposed to host system

**3. Data Flow:**
- **Installation**: CLI → Docker → SQL Server → Configuration
- **MDF Processing**: MDF File → Volume Mount → SQL Server → Parquet Output
- **Management**: CLI Commands → Docker API → Container Lifecycle

### System Integration Points

| Component | Purpose | Technology | Persistence |
|-----------|---------|------------|-------------|
| **Docker Desktop** | Container orchestration | Docker Engine | System service |
| **SQL Server Container** | Database engine | SQL Server Express 2019 | Container lifecycle |
| **Data Volume** | SQL Server system data | Docker volume | Persistent across restarts |
| **MDF Volume** | User MDF files | Docker volume | Persistent across restarts |
| **Configuration** | Connection settings | JSON file | Local filesystem |
| **Network Bridge** | Host-container communication | Docker bridge | Dynamic port mapping |

### MDF Processing Workflow

```mermaid
sequenceDiagram
    participant User
    participant CLI as PyForge CLI
    participant Docker as Docker Engine
    participant SQL as SQL Server Express
    participant Vol as MDF Volume
    
    User->>CLI: pyforge convert database.mdf
    CLI->>Vol: Copy MDF file to volume
    CLI->>SQL: ATTACH DATABASE command
    Note over SQL: Validate MDF file structure
    SQL-->>CLI: Database attached successfully
    CLI->>SQL: Query table metadata
    SQL-->>CLI: Return table schemas
    CLI->>SQL: Execute data extraction queries
    SQL-->>CLI: Return table data (chunked)
    CLI->>CLI: Convert to Parquet format
    CLI->>User: Output Parquet files + summary
    CLI->>SQL: DETACH DATABASE command
    Note over Vol: MDF file remains in volume
```

### Supported MDF File Types

| SQL Server Version | MDF Compatibility | Processing Status |
|-------------------|------------------|-------------------|
| **SQL Server 2019** | ✅ Native | Optimal performance |
| **SQL Server 2017** | ✅ Compatible | Full support |
| **SQL Server 2016** | ✅ Compatible | Full support |
| **SQL Server 2014** | ✅ Compatible | Full support |
| **SQL Server 2012** | ✅ Compatible | Full support |
| **SQL Server 2008/R2** | ⚠️ Limited | May require upgrade |
| **SQL Server 2005** | ❌ Incompatible | Not supported |

**Note**: MDF files from newer SQL Server versions (2022+) may not be compatible with SQL Server Express 2019.

## Installation Process

The installer follows a structured 5-stage process:

### Stage 1: System Requirements Check
- Validates operating system compatibility
- Checks Docker Desktop installation status
- Verifies Docker SDK for Python availability

### Stage 2: Docker Installation (if needed)
- **macOS**: Automatic installation via Homebrew
- **Windows**: Automatic installation via Winget
- **Linux**: Package manager instructions (apt/yum)
- **Manual**: Step-by-step installation guides

### Stage 3: Docker Startup
- Connects to Docker daemon
- Waits for Docker Desktop to be fully operational
- Validates Docker API accessibility

### Stage 4: SQL Server Express Setup
- Downloads Microsoft SQL Server 2019 Express image
- Creates and configures container with:
  - Persistent data volume (`pyforge-sql-data`)
  - MDF files mount point (`pyforge-mdf-files`)
  - Default port mapping (1433)
  - Secure password configuration

### Stage 5: Configuration and Validation
- Saves configuration to `~/.pyforge/mdf-config.json`
- Tests SQL Server connectivity using sqlcmd
- Displays connection details and next steps

## macOS Installation Walkthrough

### Scenario 1: Docker Already Installed

```bash
$ pyforge install mdf-tools
```

```
╭──────────────────────────────────────────────────────────────────────────╮
│ PyForge MDF Tools Setup Wizard                                           │
│ Setting up Docker Desktop and SQL Server Express for MDF file processing │
╰──────────────────────────────────────────────────────────────────────────╯

[1/5] Checking system requirements...
✓ Operating System: macOS 14.5.0 (supported)
✓ Docker Desktop: Installed
✓ Docker SDK for Python: Available

[3/5] Starting Docker Desktop...
✓ Docker Desktop is running

[4/5] Setting up SQL Server Express...
📥 Pulling SQL Server image: mcr.microsoft.com/mssql/server:2019-latest
⠴ ✓ SQL Server image downloaded
🚀 Creating SQL Server container...
⏳ Waiting for SQL Server to start (this may take a minute)...
✓ SQL Server is ready

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

🎉 Setup completed successfully!
```

### Scenario 2: Docker NOT Installed

```bash
$ pyforge install mdf-tools
```

```
╭──────────────────────────────────────────────────────────────────────────╮
│ PyForge MDF Tools Setup Wizard                                           │
│ Setting up Docker Desktop and SQL Server Express for MDF file processing │
╰──────────────────────────────────────────────────────────────────────────╯

[1/5] Checking system requirements...
✓ Operating System: macOS 14.5.0 (supported)
❌ Docker Desktop: Not found

[2/5] Docker Installation Required
Docker Desktop is required for MDF file conversion.

Would you like to:
  1. Install automatically using Homebrew (recommended)
  2. Get installation instructions
  3. Skip (I'll install manually)
  4. Continue without Docker (installation will fail)

Choice [1]: 1

📦 Installing Docker Desktop (this may take several minutes)...
✅ Docker Desktop installed successfully!
🚀 Launching Docker Desktop...

⏳ Waiting for Docker Desktop to start...
✅ Docker Desktop is running!

[4/5] Setting up SQL Server Express...
📥 Pulling SQL Server image: mcr.microsoft.com/mssql/server:2019-latest
⠴ ✓ SQL Server image downloaded
🚀 Creating SQL Server container...
⏳ Waiting for SQL Server to start (this may take a minute)...
✓ SQL Server is ready

[5/5] Installation Complete!
```

## Command Reference

### Installation Commands

#### `pyforge install mdf-tools`
Interactive installation wizard for MDF processing tools.

**Usage:**
```bash
pyforge install mdf-tools [OPTIONS]
```

**Options:**
- `--password PASSWORD`: Custom SQL Server password (default: PyForge@2024!)
- `--port PORT`: Custom SQL Server port (default: 1433)
- `--non-interactive`: Run in non-interactive mode for automation

**Examples:**
```bash
# Default installation
pyforge install mdf-tools

# Custom password and port
pyforge install mdf-tools --password "MySecure123!" --port 1433

# Non-interactive mode (for scripts)
pyforge install mdf-tools --non-interactive
```

### Container Management Commands

#### `pyforge mdf-tools status`
Displays comprehensive status of all MDF tools components.

**Usage:**
```bash
pyforge mdf-tools status
```

**Sample Output:**
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

#### `pyforge mdf-tools start`
Starts the SQL Server Express container.

**Usage:**
```bash
pyforge mdf-tools start
```

**Sample Output:**
```
🚀 Starting SQL Server container...
⏳ Waiting for SQL Server to start (this may take a minute)...
✓ SQL Server is ready
```

#### `pyforge mdf-tools stop`
Stops the SQL Server Express container.

**Usage:**
```bash
pyforge mdf-tools stop
```

**Sample Output:**
```
🛑 Stopping SQL Server container...
✓ SQL Server container stopped
```

#### `pyforge mdf-tools restart`
Restarts the SQL Server Express container.

**Usage:**
```bash
pyforge mdf-tools restart
```

**Sample Output:**
```
🛑 Stopping SQL Server container...
✓ SQL Server container stopped
🚀 Starting SQL Server container...
⏳ Waiting for SQL Server to start (this may take a minute)...
✓ SQL Server is ready
```

#### `pyforge mdf-tools logs`
Displays SQL Server container logs.

**Usage:**
```bash
pyforge mdf-tools logs [OPTIONS]
```

**Options:**
- `--lines N`, `-n N`: Number of log lines to show (default: 50)

**Examples:**
```bash
# Show last 50 lines (default)
pyforge mdf-tools logs

# Show last 100 lines
pyforge mdf-tools logs --lines 100

# Show last 10 lines
pyforge mdf-tools logs -n 10
```

#### `pyforge mdf-tools config`
Displays current MDF tools configuration.

**Usage:**
```bash
pyforge mdf-tools config
```

**Sample Output:**
```
Configuration file: /Users/username/.pyforge/mdf-config.json
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

#### `pyforge mdf-tools test`
Tests SQL Server connectivity and responsiveness.

**Usage:**
```bash
pyforge mdf-tools test
```

**Sample Output:**
```
🔍 Testing SQL Server connection...
✅ SQL Server connection successful!
```

#### `pyforge mdf-tools uninstall`
Removes SQL Server container and cleans up all data.

**Usage:**
```bash
pyforge mdf-tools uninstall
```

**Sample Output:**
```
Are you sure you want to remove SQL Server and all data? [y/n]: y
🛑 Stopping and removing container...
✓ Container removed
✓ Data volume removed
✓ MDF files volume removed
✓ Configuration file removed
✅ Uninstall completed successfully
```

## Configuration

### Configuration File Location
The installer saves configuration to `~/.pyforge/mdf-config.json`:

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

### Customizable Settings

#### Custom Password
```bash
pyforge install mdf-tools --password "YourSecurePassword123!"
```

#### Custom Port
```bash
pyforge install mdf-tools --port 1434
```

### Docker Volumes

The installer creates two persistent Docker volumes:

#### `pyforge-sql-data`
- **Mount Point**: `/var/opt/mssql`
- **Purpose**: SQL Server system databases and data files
- **Persistence**: Survives container restarts and recreations

#### `pyforge-mdf-files`
- **Mount Point**: `/mdf-files`
- **Purpose**: MDF files to be processed
- **Access**: Shared between host and container

## SQL Server Express 2019 Technical Details

### Database Engine Specifications

The MDF Tools Installer uses **Microsoft SQL Server Express 2019**, the free edition of SQL Server's enterprise database engine. This provides a robust, production-grade database environment for MDF file processing.

**SQL Server Express 2019 Key Features:**
- **Core Engine**: Same database engine as Enterprise edition
- **T-SQL Support**: Full Transact-SQL language support
- **Security**: Enterprise-grade security features
- **Reliability**: ACID compliance and transaction support
- **Performance**: Query optimizer and execution engine
- **Backup/Restore**: Full backup and restore capabilities

### Edition Limitations and Constraints

**⚠️ Important Limitations to Consider:**

| Limitation | SQL Server Express 2019 | Impact on MDF Processing |
|------------|-------------------------|--------------------------|
| **Database Size** | 10 GB per database maximum | Large MDF files (>10GB) cannot be processed |
| **Memory (RAM)** | 1.4 GB buffer pool limit | Performance may be limited with large datasets |
| **CPU Cores** | 1 socket or 4 cores maximum | Processing may be slower on high-core systems |
| **Concurrent Users** | No enforced limit (practical ~5-10) | Multiple simultaneous conversions may impact performance |
| **Parallelism** | Degree of Parallelism (DOP) = 1 | Queries cannot use parallel execution |

**❌ Features Not Available:**
- SQL Server Agent (automated jobs)
- Advanced Services (Analysis Services, Reporting Services)
- Advanced security features (Always Encrypted, Row-Level Security)
- Advanced performance features (In-Memory OLTP, Columnstore)
- Enterprise backup compression
- Database mirroring and log shipping

**✅ Features Available for MDF Processing:**
- Full T-SQL query support
- ATTACH DATABASE functionality
- All standard data types
- Backup and restore operations
- Database schemas and relationships
- Indexes and constraints

### Performance Characteristics

**Optimal MDF File Sizes:**
- **Small MDF files**: < 1 GB (Excellent performance)
- **Medium MDF files**: 1-5 GB (Good performance)
- **Large MDF files**: 5-10 GB (Acceptable performance, may require chunking)
- **Very Large MDF files**: > 10 GB (❌ Cannot be processed - requires SQL Server Standard/Enterprise)

**Memory Usage Patterns:**
- **Container Base**: ~500 MB (SQL Server Express)
- **Available for Data**: ~900 MB (after system overhead)
- **Recommended Host RAM**: 4 GB minimum (for container + host OS)

## Database Connection Details

### Connection Parameters
- **Server**: `localhost`
- **Port**: `1433` (default) or custom port
- **Database**: `master` (default system database)
- **Authentication**: SQL Server Authentication
- **Username**: `sa` (system administrator)
- **Password**: `PyForge@2024!` (default) or custom password
- **Edition**: SQL Server Express 2019
- **Version**: Microsoft SQL Server 2019 (RTM) - 15.0.4430.1

### Connection String Examples

#### Python (pyodbc)
```python
import pyodbc

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=master;"
    "UID=sa;"
    "PWD=PyForge@2024!"
)

conn = pyodbc.connect(connection_string)
```

#### Command Line (sqlcmd)
```bash
# From host (requires SQL Server tools)
sqlcmd -S localhost,1433 -U sa -P "PyForge@2024!" -Q "SELECT 1"

# From container
docker exec pyforge-sql-server /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "PyForge@2024!" -Q "SELECT 1" -C
```

## Scaling Beyond SQL Server Express

### When to Consider Upgrading

**Upgrade to SQL Server Standard/Enterprise if you encounter:**
- MDF files larger than 10 GB
- Need for high-performance parallel processing
- Requirements for SQL Server Agent automation
- Advanced security features (Always Encrypted, etc.)
- Multiple concurrent users (>10)
- Enterprise backup and restore features

### Alternative Solutions

**For Large MDF Files (>10 GB):**
1. **Split Processing**: Break large tables into chunks using date ranges or ID ranges
2. **SQL Server Standard**: Upgrade to paid edition with higher limits
3. **Cloud Solutions**: Use Azure SQL Database or SQL Managed Instance
4. **Alternative Tools**: Consider specialized MDF extraction utilities

**Migration Path Examples:**
```bash
# Option 1: Cloud-based processing
# Upload MDF to Azure SQL Database
# Process using cloud resources
# Download results

# Option 2: Chunked processing (when converter supports it)
# pyforge convert large.mdf --chunk-size 1000000 --date-range "2020-2023"
# pyforge convert large.mdf --chunk-size 1000000 --date-range "2019-2020"
```

### Cost Considerations

| Edition | Cost | Database Size Limit | Memory Limit | Use Case |
|---------|------|-------------------|--------------|----------|
| **Express** | Free | 10 GB | 1.4 GB | Development, small applications |
| **Standard** | ~$1,500+ | 524 PB | OS limit | Medium applications |
| **Enterprise** | ~$5,000+ | 524 PB | OS limit | Large enterprise applications |

## Security Considerations

### Password Security
- Default password meets SQL Server complexity requirements
- Custom passwords should be strong (8+ characters, mixed case, numbers, symbols)
- Passwords are stored in local configuration file (not transmitted)

### Network Security
- SQL Server only accessible on localhost by default
- Container isolated in Docker bridge network
- No external network exposure unless explicitly configured

### Container Security
- Runs SQL Server Express (free edition with limitations)
- Container uses official Microsoft SQL Server image
- Automatic security updates through image updates

## Troubleshooting

### Common Issues

#### Docker Desktop Not Starting
**Symptoms**: "Docker daemon is not responding"
**Solutions**:
1. Manually launch Docker Desktop application
2. Restart Docker Desktop
3. Check system resources (memory, disk space)
4. Restart computer if needed

#### SQL Server Connection Failed
**Symptoms**: "SQL Server connection failed"
**Solutions**:
1. Check container status: `pyforge mdf-tools status`
2. View container logs: `pyforge mdf-tools logs`
3. Restart container: `pyforge mdf-tools restart`
4. Verify password in config: `pyforge mdf-tools config`

#### Port Already in Use
**Symptoms**: "Port 1433 is already allocated"
**Solutions**:
1. Stop other SQL Server instances
2. Use custom port: `pyforge install mdf-tools --port 1434`
3. Check for conflicting containers: `docker ps`

#### Insufficient Memory
**Symptoms**: Container exits with memory errors
**Solutions**:
1. Increase Docker memory allocation (4GB minimum)
2. Close other applications to free memory
3. Check available system resources

### Debug Commands

```bash
# Check Docker status
docker info

# List all containers
docker ps -a

# Check container logs
docker logs pyforge-sql-server

# Inspect container configuration
docker inspect pyforge-sql-server

# Check Docker volumes
docker volume ls

# Test SQL Server directly
docker exec pyforge-sql-server /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "PyForge@2024!" -Q "SELECT @@VERSION" -C
```

### Getting Help

If you encounter issues not covered in this guide:

1. **Check Status**: Run `pyforge mdf-tools status` for diagnostic information
2. **View Logs**: Use `pyforge mdf-tools logs` to see SQL Server startup messages
3. **Restart Services**: Try `pyforge mdf-tools restart` to resolve temporary issues
4. **Reinstall**: Use `pyforge mdf-tools uninstall` followed by `pyforge install mdf-tools`

## Next Steps

After successful installation:

1. **Verify Installation**: Run `pyforge mdf-tools status` to confirm all components are operational
2. **Test Connectivity**: Use `pyforge mdf-tools test` to verify SQL Server is responding
3. **Install MDF Converter**: Install the MDF to Parquet converter (when available)
4. **Process MDF Files**: Use PyForge to convert your MDF files to modern formats

## Related Documentation

- [MDF to Parquet Converter](mdf-to-parquet.md) (coming soon)
- [Database Files Overview](database-files.md)
- [CLI Reference](../reference/cli-reference.md)
- [Troubleshooting Guide](../tutorials/troubleshooting.md)