---
name: ✨ Feature Request - MDF Tools Installer
about: Add interactive Docker and SQL Server setup for MDF file processing
title: '[FEATURE] MDF Tools Installer (`pyforge install mdf-tools`)'
labels: 'enhancement, claude-ready, feature-request, prd-workflow, installer, docker'
assignees: ''
---

## 🚀 Feature Request Overview
<!-- Interactive installation system for MDF processing prerequisites -->

**Feature Name**: MDF Tools Installer
**Type**: [x] New Command [ ] Enhancement [ ] Integration [ ] Performance [ ] Other: ___

## 📋 Implementation Workflow
This feature request follows the **PRD → Tasks → Implementation** workflow:

1. **📝 PRD Creation**: Complete this issue to create a comprehensive PRD document
2. **🎯 Task Generation**: Generate structured task list from approved PRD  
3. **⚡ Implementation**: Execute tasks one-by-one with approval checkpoints

---

## 📋 PRD REQUIREMENTS GATHERING

### 🎯 Problem Statement
Users want to process SQL Server MDF files but face significant barriers:
- Setting up SQL Server locally is complex and platform-specific
- Docker container configuration requires technical expertise
- No automated way to verify prerequisites for MDF processing
- Manual setup leads to configuration errors and connectivity issues

### 💡 Proposed Solution Overview
Create an interactive installation command `pyforge install mdf-tools` that automates the entire setup process:
- Detects and guides Docker Desktop installation
- Pulls and configures SQL Server Express container
- Creates secure default configuration
- Provides container management commands
- Validates setup with connectivity tests

### 👥 Target Users
- **Data Engineers**: Need to convert legacy SQL Server databases
- **Business Analysts**: Working with MDF files from various sources
- **Developers**: Building data pipelines with MDF inputs
- **Skill Levels**: Beginner to intermediate (no Docker expertise required)

### 🔄 User Journey
1. User starts with: Raw MDF file and need to process it
2. User runs: `pyforge install mdf-tools`
3. Tool processes: Interactive wizard for Docker and SQL Server setup
4. User receives: Fully configured SQL Server Express container
5. User can then: Use MDF conversion tools or manage containers

### 📊 Requirements Breakdown
#### Functional Requirements
- [ ] Detect Docker Desktop installation across platforms (Windows, macOS, Linux)
- [ ] Guide users through Docker installation with platform-specific instructions
- [ ] Pull and configure Microsoft SQL Server Express container
- [ ] Create secure configuration with customizable passwords
- [ ] Provide container lifecycle management (start, stop, restart, status)
- [ ] Validate setup with connectivity and health checks
- [ ] Save configuration for future MDF processing tools

#### Non-Functional Requirements  
- [ ] **Performance**: Installation completes within 5 minutes on standard hardware
- [ ] **Compatibility**: Support Windows 10+, macOS 10.15+, Ubuntu 18.04+
- [ ] **Usability**: Clear progress indicators and error messages
- [ ] **Reliability**: Graceful handling of network issues and resource constraints

### 🖥️ Command Line Interface Design
```bash
# Primary installation command
pyforge install mdf-tools

# Container management commands
pyforge mdf-tools status      # Check Docker and SQL Server status
pyforge mdf-tools start       # Start SQL Server container
pyforge mdf-tools stop        # Stop SQL Server container
pyforge mdf-tools restart     # Restart SQL Server container
pyforge mdf-tools logs        # View SQL Server logs
pyforge mdf-tools config      # Display current configuration
pyforge mdf-tools test        # Test SQL Server connectivity
pyforge mdf-tools uninstall   # Remove SQL Server and clean up

# Example installation flow
pyforge install mdf-tools --password "MySecure123!" --port 1433
```

### 📁 Input/Output Specifications
- **Input Types**: User preferences (password, port), system environment
- **Output Types**: Docker container, configuration files, status reports
- **Processing Options**: Custom passwords, port configuration, resource limits
- **Configuration**: `~/.pyforge/mdf-config.json` with connection details

### 🔍 Technical Architecture
- **Core Components**: 
  - `MdfToolsInstaller` class for installation logic
  - `DockerManager` for container operations
  - `ConfigManager` for settings persistence
  - Platform-specific installation handlers
- **Dependencies**: docker-py, psutil, requests
- **Integration Points**: CLI command registration, configuration system
- **Data Flow**: User input → Docker setup → Container creation → Configuration save

### 🧪 Testing Strategy
- **Unit Tests**: Docker detection, configuration management, platform handlers
- **Integration Tests**: Full installation workflow, container lifecycle
- **Performance Tests**: Installation speed, resource usage
- **Edge Cases**: No Docker, network failures, permission issues, port conflicts

---

## 🎯 PRD APPROVAL CHECKLIST
**Complete this section before generating tasks:**

- [ ] Problem statement clearly defines user pain points
- [ ] Solution approach is technically feasible
- [ ] Requirements are specific and measurable
- [ ] CLI interface follows project conventions
- [ ] Testing strategy covers all scenarios
- [ ] Performance requirements are realistic
- [ ] Implementation approach is approved

---

## 📋 TASK GENERATION TRIGGER
**Once PRD is approved, use this section to generate implementation tasks:**

### Task List Creation
- [ ] **Ready to generate tasks**: PRD approved and complete
- [ ] **Task file created**: `/tasks/tasks-mdf-tools-installer.md`
- [ ] **Implementation started**: First task marked in_progress

### Claude Implementation Commands
```bash
# Generate PRD document
"Create a PRD for MDF Tools Installer based on the requirements above"

# Generate task list from PRD  
"Generate tasks from /tasks/prd-mdf-tools-installer.md"

# Start implementation
"Start working on /tasks/tasks-mdf-tools-installer.md"
```

---

## 🔍 CLAUDE GUIDANCE SECTION

### File Structure for Implementation
```
/tasks/
  ├── prd-mdf-tools-installer.md      # Product Requirements Document
  ├── tasks-mdf-tools-installer.md    # Implementation task list
  └── ...

@docs/                               # Documentation under docs folder
  ├── mdf-tools-installer.md         # User guide
  └── troubleshooting-mdf.md          # Common issues
```

### Key Investigation Areas
```bash
# Examine existing patterns
grep -r "install" src/pyforge_cli/
grep -r "click.command" src/pyforge_cli/

# Core files to modify
# - src/pyforge_cli/main.py (new install command)
# - src/pyforge_cli/installers/ (new module)
# - src/pyforge_cli/config/ (configuration management)
# - tests/test_mdf_installer.py (comprehensive tests)
```

### Implementation Checkpoints
- [ ] **Phase 1**: Docker detection and management
- [ ] **Phase 2**: SQL Server container setup
- [ ] **Phase 3**: Configuration and validation
- [ ] **Phase 4**: Container lifecycle commands
- [ ] **Phase 5**: Error handling and platform support

---

## 📊 SUCCESS CRITERIA
- [ ] PRD document created and approved
- [ ] Task list generated with clear acceptance criteria
- [ ] All tasks completed with user approval at each step
- [ ] Interactive installation wizard works on all platforms
- [ ] SQL Server container starts and connects successfully
- [ ] Container management commands function properly
- [ ] Configuration persists and validates correctly
- [ ] Test coverage meets project standards
- [ ] Documentation updated (CLI help, docs site)

---

## 🔗 RELATED WORK
- **Related Issues**: MDF Converter feature (blocks this)
- **Depends On**: None
- **Blocks**: MDF to Parquet Converter implementation
- **Similar Features**: Existing converter architecture

---

## 📅 PRIORITIZATION
- **Business Impact**: High (enables MDF processing ecosystem)
- **Technical Complexity**: Medium (Docker integration, multi-platform)  
- **User Demand**: High (prerequisite for MDF conversion)
- **Implementation Timeline**: 1-2 weeks

---
**For Maintainers - PRD Workflow:**
- [ ] Issue reviewed and PRD requirements complete
- [ ] Technical feasibility confirmed
- [ ] PRD document creation approved
- [ ] Task generation authorized
- [ ] Implementation approach validated