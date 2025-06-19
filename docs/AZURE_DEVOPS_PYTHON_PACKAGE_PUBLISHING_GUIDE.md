# Azure DevOps Python Package Publishing Guide
## Complete Setup Documentation for CortexPy CLI Tool

---

## Document Overview

This document provides step-by-step instructions for setting up Azure DevOps to publish the CortexPy CLI Python package with secure public access. The solution creates a public feed that allows anonymous installation of the cortexpy-cli package while maintaining security isolation from other organizational packages.

**Target Audience**: DevOps Engineers, System Administrators, Development Teams  
**Project**: CortexPy CLI Tool Package Publishing  
**Package Name**: cortexpy-cli  
**Last Updated**: June 2025  

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Azure DevOps Project Setup](#phase-1-azure-devops-project-setup)
4. [Phase 2: Artifacts Feed Configuration](#phase-2-artifacts-feed-configuration)
5. [Phase 3: Security and Permissions](#phase-3-security-and-permissions)
6. [Phase 4: Authentication Setup](#phase-4-authentication-setup)
7. [Phase 5: CI/CD Pipeline Implementation](#phase-5-cicd-pipeline-implementation)
8. [Phase 6: Package Publication](#phase-6-package-publication)
9. [Phase 7: Public Access Configuration](#phase-7-public-access-configuration)
10. [Phase 8: Testing and Validation](#phase-8-testing-and-validation)
11. [Maintenance and Monitoring](#maintenance-and-monitoring)
12. [Troubleshooting Guide](#troubleshooting-guide)
13. [Security Considerations](#security-considerations)
14. [Appendix](#appendix)

---

## Architecture Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                     Azure DevOps Organization                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐    ┌─────────────────────────────────┐   │
│  │   Private Project │    │        Public Project          │   │
│  │                   │    │                                 │   │
│  │ ┌───────────────┐ │    │ ┌─────────────────────────────┐ │   │
│  │ │Internal Feeds │ │    │ │     Public Feed             │ │   │
│  │ │• Secure       │ │    │ │• cortexpy-packages          │ │   │
│  │ │• Auth Required│ │    │ │• Anonymous Read Access      │ │   │
│  │ └───────────────┘ │    │ │• Authenticated Write Access │ │   │
│  └───────────────────┘    │ └─────────────────────────────┘ │   │
│                           └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌─────────────────────────┐
                        │    End Users            │
                        │• pip install cortexpy   │
                        │• No authentication      │
                        │• Public internet access │
                        └─────────────────────────┘
```

### Security Model
- **Package-Specific Access**: Only CortexPy packages are publicly accessible
- **Project Isolation**: Public feed is isolated in a separate public project
- **Dual Authentication**: Different access levels for read vs. write operations
- **Upstream Sources**: Controlled integration with PyPI and other package sources

---

## Prerequisites

### Organizational Requirements
- [ ] Azure DevOps Organization with appropriate licensing
- [ ] Organization-level permissions to create projects
- [ ] Artifacts feature enabled in the organization
- [ ] Network access to Azure DevOps (firewall/proxy configuration if needed)

### Technical Requirements
- [ ] Python 3.8+ development environment
- [ ] Git repository with Python package source code
- [ ] Build tools: `build`, `twine`, `wheel`
- [ ] Azure CLI (optional but recommended)

### Personnel Requirements
- [ ] DevOps Engineer with Azure DevOps administrative access
- [ ] Development team member familiar with Python packaging
- [ ] Project stakeholder for approval and testing

### Access Requirements
- [ ] Azure DevOps Organization Owner or Project Collection Administrator
- [ ] Ability to create Personal Access Tokens
- [ ] Network connectivity to Azure DevOps services

---

## Phase 1: Azure DevOps Project Setup

### Step 1.1: Create Public Project

**Responsible**: DevOps Engineer  
**Duration**: 15 minutes  

1. **Access Azure DevOps Organization**
   ```
   URL: https://dev.azure.com/[YOUR-ORGANIZATION-NAME]
   ```

2. **Create New Project**
   - Click "**+ New Project**" button
   - **Project Name**: `cortexpy-cli-public-packages`
   - **Description**: `Public distribution of CortexPy CLI Python package`
   - **Visibility**: **Public** ⚠️ **CRITICAL: Must be Public for anonymous access**
   - **Version Control**: Git
   - **Work Item Process**: Agile (or your organization's default)
   - Click "**Create**"

3. **Verify Project Settings**
   - Navigate to Project Settings → Overview
   - Confirm visibility is set to "Public"
   - Note the project URL for documentation

**Deliverable**: ✅ Public project created and accessible

### Step 1.2: Configure Project Permissions

**Responsible**: DevOps Engineer  
**Duration**: 10 minutes  

1. **Access Project Settings**
   - Go to Project Settings → Permissions

2. **Configure Team Permissions**
   ```
   Project Administrators:
   - Full control over project settings
   - Can modify feed permissions
   
   Contributors:
   - Can publish packages to feeds
   - Can create and modify pipelines
   
   Readers:
   - Can view project and packages
   - Default for authenticated users
   
   Anonymous Users:
   - Automatic read access to public feeds
   - Cannot modify or upload packages
   ```

3. **Add Specific Users/Groups**
   - Add development team members as Contributors
   - Add DevOps team as Project Administrators
   - Document access decisions

**Deliverable**: ✅ Project permissions configured

---

## Phase 2: Artifacts Feed Configuration

### Step 2.1: Create Public Feed

**Responsible**: DevOps Engineer  
**Duration**: 20 minutes  

1. **Navigate to Artifacts**
   - In your public project, select "**Artifacts**" from left navigation
   - If first time: Click "**Get started with Artifacts**"

2. **Create Feed**
   - Click "**Create Feed**" or "**+ New Feed**"
   - **Name**: `cortexpy-cli-packages`
   - **Description**: `Public feed for CortexPy CLI Python package`
   - **Visibility**: Inherits from project (Public)
   - **Scope**: 
     - ✅ **Project**: cortexpy-cli-public-packages (Recommended)
     - ❌ Organization (avoid for security isolation)
   - **Upstream Sources**: 
     - ✅ Check "Include packages from common public sources"
     - This allows fallback to PyPI for dependencies

3. **Configure Feed Settings**
   - Click "**Create**"
   - Note the feed URL: 
     ```
     https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
     ```

**Deliverable**: ✅ Public feed created with proper configuration

### Step 2.2: Configure Upstream Sources

**Responsible**: DevOps Engineer  
**Duration**: 15 minutes  

1. **Access Feed Settings**
   - Go to your feed → Settings (gear icon) → Upstream Sources

2. **Configure PyPI Upstream**
   ```yaml
   Name: PyPI
   Protocol: PyPI
   URL: https://pypi.org/simple/
   Priority: 1
   ```

3. **Test Upstream Configuration**
   - Search for a common package (e.g., `requests`)
   - Verify it appears in feed search results
   - Document any connectivity issues

**Deliverable**: ✅ Upstream sources configured and tested

---

## Phase 3: Security and Permissions

### Step 3.1: Configure Feed Permissions

**Responsible**: DevOps Engineer  
**Duration**: 25 minutes  

1. **Access Feed Permissions**
   - Go to Feed → Settings → Permissions

2. **Configure Security Groups**

   **Project Collection Build Service ([ORG])**
   ```
   Role: Contributor
   Purpose: Allow Azure Pipelines to publish packages
   ```

   **[Project] Build Service ([ORG])**
   ```
   Role: Contributor  
   Purpose: Allow project-specific pipelines to publish
   ```

   **Project Contributors**
   ```
   Role: Contributor
   Purpose: Allow team members to publish packages manually
   ```

   **Project Readers**
   ```
   Role: Reader
   Purpose: Allow authenticated users to view packages
   ```

   **Anonymous Users**
   ```
   Role: Reader (Automatic)
   Purpose: Public access to packages
   ```

3. **Create Custom Security Groups (Optional)**
   ```
   Package Publishers:
   - Members: Development team leads
   - Role: Contributor
   - Purpose: Controlled publishing access
   
   Package Managers:
   - Members: DevOps team, Project managers
   - Role: Owner
   - Purpose: Feed administration
   ```

**Deliverable**: ✅ Feed permissions configured with proper security model

### Step 3.2: Implement Package-Specific Security

**Responsible**: DevOps Engineer  
**Duration**: 30 minutes  

1. **Create Security Documentation**
   ```markdown
   # Package Security Model
   
   ## Feed Isolation Strategy
   - Public Feed: cortexpy-packages (anonymous read access)
   - Internal Feeds: organization-scoped (authentication required)
   
   ## Access Control Matrix
   | User Type | Read Access | Write Access | Admin Access |
   |-----------|-------------|--------------|--------------|
   | Anonymous | ✅ Public   | ❌           | ❌           |
   | Authenticated | ✅ All  | ❌           | ❌           |
   | Contributors | ✅ All   | ✅ Assigned  | ❌           |
   | Administrators | ✅ All | ✅ All       | ✅ All       |
   ```

2. **Implement Network Security (if applicable)**
   ```yaml
   Firewall Rules:
   - Allow outbound HTTPS to *.visualstudio.com
   - Allow outbound HTTPS to *.dev.azure.com
   - Allow outbound HTTPS to pkgs.dev.azure.com
   ```

3. **Configure Audit Logging**
   - Enable feed activity logging
   - Set up monitoring for unusual access patterns
   - Document log retention policies

**Deliverable**: ✅ Comprehensive security model implemented

---

## Phase 4: Authentication Setup

### Step 4.1: Create Service Accounts

**Responsible**: DevOps Engineer  
**Duration**: 20 minutes  

1. **Create Personal Access Tokens**

   **For CI/CD Pipeline**
   ```
   Name: cortexpy-cli-pipeline-publishing
   Scopes: 
   - Packaging (Read & Write)
   - Build (Read & Execute) - if using Azure Pipelines
   Expiration: 90 days (with renewal calendar reminder)
   ```

   **For Manual Publishing**
   ```
   Name: cortexpy-cli-manual-publishing  
   Scopes:
   - Packaging (Read & Write)
   Expiration: 30 days
   ```

2. **Secure Token Storage**
   - Store tokens in Azure Key Vault (recommended)
   - Or use Azure DevOps Library Variable Groups
   - Document token rotation procedures

3. **Create Service Connection (for pipelines)**
   - Go to Project Settings → Service Connections
   - Create "Python Package Index" connection
   - Configure with feed URL and authentication

**Deliverable**: ✅ Authentication tokens created and securely stored

### Step 4.2: Configure Local Development Access

**Responsible**: Development Team  
**Duration**: 15 minutes  

1. **Create .pypirc Configuration**
   ```ini
   # ~/.pypirc
   [distutils]
   index-servers = 
       cortexpy-cli-feed
       pypi
   
   [cortexpy-cli-feed]
   repository = https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/upload/
   username = [ANY_STRING]
   password = [PERSONAL_ACCESS_TOKEN]
   
   [pypi]
   # Remove or comment out to prevent accidental uploads to PyPI
   # repository = https://upload.pypi.org/legacy/
   # username = __token__
   # password = [PYPI_TOKEN]
   ```

2. **Configure pip.conf/pip.ini**
   ```ini
   # Linux/Mac: ~/.pip/pip.conf
   # Windows: %APPDATA%\pip\pip.ini
   [global]
   index-url = https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   extra-index-url = https://pypi.org/simple/
   ```

3. **Test Configuration**
   ```bash
   # Test authentication
   python -m twine upload --repository cortexpy-cli-feed --dry-run dist/*
   
   # Test installation
   pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   ```

**Deliverable**: ✅ Local development authentication configured and tested

---

## Phase 5: CI/CD Pipeline Implementation

### Step 5.1: Create Build Pipeline

**Responsible**: DevOps Engineer  
**Duration**: 45 minutes  

1. **Create azure-pipelines.yml**
   ```yaml
   # azure-pipelines.yml - Complete CI/CD Pipeline for Python Package Publishing
   
   trigger:
     branches:
       include:
       - main
       - release/*
     tags:
       include:
       - v*.*.*
   
   pr:
     branches:
       include:
       - main
   
   variables:
     pythonVersion: '3.10'
     feedName: 'cortexpy-cli-packages'
     projectName: 'cortexpy-cli-public-packages'
     packageName: 'cortexpy-cli'
   
   pool:
     vmImage: 'ubuntu-latest'
   
   stages:
   - stage: Build
     displayName: 'Build and Test Package'
     jobs:
     - job: BuildPackage
       displayName: 'Build Python Package'
       steps:
       - task: UsePythonVersion@0
         inputs:
           versionSpec: '$(pythonVersion)'
         displayName: 'Use Python $(pythonVersion)'
   
       - script: |
           python -m pip install --upgrade pip
           pip install build twine wheel setuptools hatchling
         displayName: 'Install build dependencies'
   
       - script: |
           pip install -e .
           pip install --dependency-groups dev
         displayName: 'Install package dependencies'
   
       - script: |
           python -m pytest tests/ -v --junitxml=test-results.xml --cov=cortexpy_cli --cov-report=xml
         displayName: 'Run tests'
         continueOnError: true
   
       - task: PublishTestResults@2
         inputs:
           testResultsFiles: 'test-results.xml'
           testRunTitle: 'Python Package Tests'
         condition: always()
   
       - task: PublishCodeCoverageResults@1
         inputs:
           codeCoverageTool: 'Cobertura'
           summaryFileLocation: 'coverage.xml'
         condition: always()
   
       - script: |
           python -m build --wheel --sdist
         displayName: 'Build package'
   
       - script: |
           python -m twine check dist/*
         displayName: 'Validate package'
   
       - task: PublishBuildArtifacts@1
         inputs:
           pathToPublish: 'dist'
           artifactName: 'python-packages'
         displayName: 'Publish build artifacts'
   
   - stage: Publish
     displayName: 'Publish to Feed'
     dependsOn: Build
     condition: and(succeeded(), or(eq(variables['Build.SourceBranch'], 'refs/heads/main'), startsWith(variables['Build.SourceBranch'], 'refs/tags/v')))
     jobs:
     - deployment: PublishPackage
       displayName: 'Publish to Azure Artifacts'
       environment: 'production'
       strategy:
         runOnce:
           deploy:
             steps:
             - task: UsePythonVersion@0
               inputs:
                 versionSpec: '$(pythonVersion)'
               displayName: 'Use Python $(pythonVersion)'
   
             - script: |
                 pip install twine
               displayName: 'Install twine'
   
             - task: TwineAuthenticate@1
               inputs:
                 artifactFeed: '$(projectName)/$(feedName)'
               displayName: 'Authenticate with Azure Artifacts'
   
             - task: DownloadBuildArtifacts@0
               inputs:
                 buildType: 'current'
                 artifactName: 'python-packages'
                 downloadPath: '$(System.ArtifactsDirectory)'
   
             - script: |
                 python -m twine upload -r $(feedName) --config-file $(PYPIRC_PATH) $(System.ArtifactsDirectory)/python-packages/*.whl $(System.ArtifactsDirectory)/python-packages/*.tar.gz
               displayName: 'Upload package to feed'
   
             - script: |
                 echo "Package published successfully!"
                 echo "Install with: pip install $(packageName) --index-url https://pkgs.dev.azure.com/$(System.TeamFoundationCollectionUri | Replace('https://dev.azure.com/',''))/$(projectName)/_packaging/$(feedName)/pypi/simple/"
               displayName: 'Display installation instructions'
   
   - stage: Validate
     displayName: 'Validate Publication'
     dependsOn: Publish
     jobs:
     - job: ValidateInstallation
       displayName: 'Test Package Installation'
       steps:
       - task: UsePythonVersion@0
         inputs:
           versionSpec: '$(pythonVersion)'
         displayName: 'Use Python $(pythonVersion)'
   
       - script: |
           pip install $(packageName) --index-url https://pkgs.dev.azure.com/$(System.TeamFoundationCollectionUri | Replace('https://dev.azure.com/',''))/$(projectName)/_packaging/$(feedName)/pypi/simple/
         displayName: 'Install published package'
   
       - script: |
           python -c "import $(packageName); print(f'Successfully imported $(packageName) version: {$(packageName).__version__}')"
         displayName: 'Validate package import'
   ```

2. **Configure Pipeline Variables**
   ```yaml
   # Library Variables (secure)
   Variables:
   - Group: cortexpy-cli-publishing
     Variables:
     - PYPI_TOKEN: [SECURE] # For fallback PyPI publishing
     - NOTIFICATION_EMAIL: devops@company.com
   ```

3. **Set Up Environments**
   - Create "production" environment
   - Configure approvals if required
   - Set up deployment gates

**Deliverable**: ✅ Complete CI/CD pipeline implemented and tested

### Step 5.2: Configure Branch Policies

**Responsible**: DevOps Engineer  
**Duration**: 15 minutes  

1. **Main Branch Protection**
   ```yaml
   Branch Policies for 'main':
   - Require pull request reviews: 1 reviewer minimum
   - Require status checks: Build pipeline must pass
   - Require branches to be up to date
   - Restrict pushes to main branch
   ```

2. **Release Branch Strategy**
   ```yaml
   Release Branches (release/*):
   - Automatic package publishing on merge to main
   - Semantic versioning enforcement
   - Tag creation automation
   ```

**Deliverable**: ✅ Branch policies configured for secure releases

---

## Phase 6: Package Publication

### Step 6.1: Prepare Python Package

**Responsible**: Development Team  
**Duration**: 30 minutes  

1. **Update Package Configuration**
   ```toml
   # pyproject.toml
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"
   
   [project]
   name = "cortexpy-cli"
   version = "0.1.0"
   description = "A powerful CLI tool for data format conversion and manipulation"
   readme = "README.md"
   requires-python = ">=3.8"
   license = {text = "MIT"}
   authors = [
       {name = "Your Organization", email = "devops@company.com"},
   ]
   keywords = ["cli", "data", "conversion", "pdf", "csv", "parquet"]
   classifiers = [
       "Development Status :: 3 - Alpha",
       "Intended Audience :: Developers",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
       "Programming Language :: Python :: 3",
       "Programming Language :: Python :: 3.8",
       "Programming Language :: Python :: 3.9",
       "Programming Language :: Python :: 3.10",
       "Programming Language :: Python :: 3.11",
       "Programming Language :: Python :: 3.12",
       "Topic :: Software Development :: Libraries :: Python Modules",
       "Topic :: Text Processing",
       "Topic :: Utilities",
   ]
   dependencies = [
       "click>=8.0.0",
       "rich>=13.0.0",
       "tqdm>=4.64.0",
       "PyMuPDF>=1.23.0",
       "pathlib-mate>=1.0.0",
       "pyarrow>=17.0.0",
       "pandas>=2.0.3",
       "chardet>=5.2.0",
       "pandas-access>=0.0.1",
       "dbfread>=2.0.7",
       "openpyxl>=3.1.5",
   ]
   
   [project.urls]
   Homepage = "https://dev.azure.com/[ORG]/cortexpy-cli-public-packages"
   Documentation = "https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_wiki"
   Repository = "https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_git/cortexpy-cli"
   Issues = "https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_workitems"
   
   [project.scripts]
   cortexpy = "cortexpy_cli.main:cli"
   
   [tool.hatch.build.targets.wheel]
   packages = ["src/cortexpy_cli"]
   ```

2. **Validate Package Structure**
   ```
   cortexpy-cli/
   ├── src/cortexpy_cli/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── converters/
   │   │   ├── __init__.py
   │   │   ├── base.py
   │   │   ├── dbf_converter.py
   │   │   ├── mdb_converter.py
   │   │   └── pdf_converter.py
   │   ├── detectors/
   │   │   ├── __init__.py
   │   │   └── database_detector.py
   │   ├── plugins/
   │   │   ├── __init__.py
   │   │   ├── loader.py
   │   │   └── registry.py
   │   └── readers/
   │       ├── __init__.py
   │       ├── dbf_reader.py
   │       └── mdb_reader.py
   ├── tests/
   ├── pyproject.toml
   ├── README.md
   ├── LICENSE
   └── Makefile
   ```

3. **Build Configuration Notes**
   - Uses Hatchling as build backend (modern replacement for setuptools)
   - Package sources are in `src/cortexpy_cli/` directory
   - Entry point is `cortexpy = "cortexpy_cli.main:cli"`
   - No MANIFEST.in needed with Hatchling (automatically includes necessary files)

**Deliverable**: ✅ Package configured for publication

### Step 6.2: Initial Manual Publication

**Responsible**: Development Team  
**Duration**: 20 minutes  

1. **Build and Test Locally**
   ```bash
   # Clean previous builds
   rm -rf dist/ build/ *.egg-info/
   
   # Build package
   python -m build
   
   # Validate package
   python -m twine check dist/*
   
   # Test installation locally
   pip install dist/*.whl
   python -c "import cortexpy_cli; print('CortexPy CLI installed successfully')"
   ```

2. **Publish to Azure Artifacts**
   ```bash
   # Upload to feed
   python -m twine upload --repository cortexpy-cli-feed dist/*
   
   # Verify upload
   # Check Azure DevOps Artifacts feed for new package
   ```

3. **Test Public Installation**
   ```bash
   # Test anonymous access
   pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   ```

**Deliverable**: ✅ Package successfully published and verified

---

## Phase 7: Public Access Configuration

### Step 7.1: Configure Public Access URLs

**Responsible**: DevOps Engineer  
**Duration**: 15 minutes  

1. **Document Public Access URLs**
   ```markdown
   # CortexPy CLI Package Installation
   
   ## Public Feed URLs
   - **Browse Packages**: https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_artifacts/feed/cortexpy-cli-packages
   - **Pip Index URL**: https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   
   ## Installation Instructions
   
   ### Standard Installation
   ```bash
   pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   ```
   
   ### Requirements.txt
   ```
   --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   cortexpy-cli==0.1.0
   ```
   
   ### With Version Constraints
   ```bash
   pip install "cortexpy-cli>=0.1.0,<1.0.0" --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   ```
   ```

2. **Create Package Badges**
   ```markdown
   # Package Status Badges
   ![Package Version](https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_apis/public/Packaging/Feeds/cortexpy-cli-packages/Packages/cortexpy-cli/Badge)
   ![Build Status](https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_apis/build/status/cortexpy-cli-build)
   ```

**Deliverable**: ✅ Public access URLs documented and tested

### Step 7.2: Create User Documentation

**Responsible**: Development Team + DevOps Engineer  
**Duration**: 45 minutes  

1. **Create Installation Guide**
   ```markdown
   # CortexPy CLI Installation Guide
   
   ## Quick Start
   
   CortexPy CLI is available through our public Azure Artifacts feed. No authentication required!
   
   ### Install Latest Version
   ```bash
   pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   ```
   
   ### Install Specific Version
   ```bash
   pip install cortexpy-cli==0.1.0 --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   ```
   
   ### Requirements.txt Integration
   Add to your requirements.txt:
   ```
   --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   cortexpy-cli>=0.1.0
   ```
   
   ## Usage Examples
   
   ### Basic PDF Conversion
   ```bash
   # Convert PDF to text
   cortexpy convert document.pdf
   
   # Convert with custom output
   cortexpy convert document.pdf output.txt
   
   # Convert specific pages
   cortexpy convert document.pdf --pages "1-10"
   ```
   
   ### File Information
   ```bash
   # Display file metadata
   cortexpy info document.pdf
   
   # Export as JSON
   cortexpy info document.pdf --format json
   ```
   
   ### Database Conversion (Future)
   ```bash
   # Convert MDB to Parquet (Coming Soon)
   cortexpy convert database.mdb --output-format parquet
   
   # Convert DBF to CSV (Coming Soon)  
   cortexpy convert data.dbf --output-format csv
   ```
   
   ## Verification
   
   ```bash
   # Test installation
   cortexpy --version
   
   # Show available commands
   cortexpy --help
   
   # List supported formats
   cortexpy formats
   ```
   
   ## Troubleshooting
   
   ### SSL/Certificate Issues
   ```bash
   pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/ --trusted-host pkgs.dev.azure.com
   ```
   
   ### Corporate Firewall
   Ensure your network allows HTTPS access to:
   - `*.dev.azure.com`
   - `pkgs.dev.azure.com`
   
   ### Version Conflicts
   ```bash
   pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/ --force-reinstall --no-deps
   ```
   ```

2. **Create API Documentation Links**
   ```markdown
   # CortexPy CLI Documentation
   
   - **User Guide**: https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_wiki
   - **Source Code**: https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_git/cortexpy-cli
   - **Issue Tracking**: https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_workitems
   - **Build Status**: https://dev.azure.com/[ORG]/cortexpy-cli-public-packages/_build
   ```

**Deliverable**: ✅ Comprehensive user documentation created

---

## Phase 8: Testing and Validation

### Step 8.1: End-to-End Testing

**Responsible**: DevOps Engineer + Development Team  
**Duration**: 60 minutes  

1. **Test Pipeline Flow**
   ```bash
   # Test complete CI/CD pipeline
   git checkout -b test-pipeline
   # Make minor change
   git commit -am "Test pipeline flow"
   git push origin test-pipeline
   # Create PR and merge
   # Verify package is published
   ```

2. **Test Anonymous Access**
   ```bash
   # Test from clean environment (no authentication)
   docker run --rm -it python:3.10 bash
   pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/
   cortexpy --version
   ```

3. **Test Various Environments**
   ```yaml
   Test Matrix:
   - Python Versions: [3.8, 3.9, 3.10, 3.11, 3.12]
   - Operating Systems: [Ubuntu, Windows, macOS]
   - Installation Methods: [pip, requirements.txt, Docker]
   - CLI Commands: [convert, info, formats, validate]
   ```

**Deliverable**: ✅ Comprehensive testing completed successfully

### Step 8.2: Load and Performance Testing

**Responsible**: DevOps Engineer  
**Duration**: 30 minutes  

1. **Test Concurrent Downloads**
   ```bash
   # Simulate multiple concurrent installations
   for i in {1..10}; do
     (pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/ --target /tmp/test$i) &
   done
   wait
   ```

2. **Monitor Feed Performance**
   - Check Azure DevOps Artifacts metrics
   - Monitor download times and success rates
   - Verify upstream source fallback works

**Deliverable**: ✅ Performance validated under load

---

## Maintenance and Monitoring

### Daily Tasks
- [ ] Monitor pipeline execution status
- [ ] Check for failed package installations
- [ ] Review download statistics

### Weekly Tasks
- [ ] Review Personal Access Token expiration dates
- [ ] Audit feed permissions and access logs
- [ ] Update documentation if needed

### Monthly Tasks
- [ ] Rotate Personal Access Tokens
- [ ] Review and clean up old package versions
- [ ] Audit security group memberships
- [ ] Performance and usage analysis

### Quarterly Tasks
- [ ] Security review of access patterns
- [ ] Update Azure DevOps organization settings
- [ ] Review and update disaster recovery procedures
- [ ] Update documentation and runbooks

### Monitoring Setup

```yaml
# Azure Monitor Alerts
Alerts:
  - Name: "Package Publication Failed"
    Condition: Pipeline failure in cortexpy-packages project
    Action: Email DevOps team
    
  - Name: "High Download Volume"
    Condition: >1000 downloads per hour
    Action: Review for potential issues
    
  - Name: "Authentication Failures"
    Condition: Multiple auth failures from same IP
    Action: Security team notification
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. "Package not found" errors
```
Problem: pip cannot find the package
Solution: 
- Verify feed URL is correct
- Check package name spelling
- Ensure package has been published successfully
- Check if upstream sources are properly configured
```

#### 2. Authentication failures during publishing
```
Problem: TwineAuthenticate task fails
Solution:
- Verify Personal Access Token hasn't expired
- Check token scopes include Packaging (Read & Write)
- Ensure Build Service has Contributor role on feed
- Verify project and feed names in pipeline configuration
```

#### 3. Public access not working
```
Problem: Anonymous users cannot install packages
Solution:
- Verify project visibility is set to "Public"
- Check feed is created in public project
- Confirm feed permissions allow anonymous read access
- Test with clean environment (no cached credentials)
```

#### 4. Upstream source conflicts
```
Problem: Wrong package version installed from PyPI instead of private feed
Solution:
- Adjust upstream source priorities
- Use explicit version constraints
- Configure pip.conf with correct index order
```

#### 5. SSL/Certificate issues
```
Problem: SSL certificate verification failures
Solution:
- Add --trusted-host pkgs.dev.azure.com to pip commands
- Configure corporate certificates if needed
- Check firewall/proxy configuration
```

### Diagnostic Commands

```bash
# Test feed connectivity
curl -I https://pkgs.dev.azure.com/[ORG]/cortexpy-public-packages/_packaging/cortexpy-packages/pypi/simple/

# Test package search
pip search cortexpy --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-public-packages/_packaging/cortexpy-packages/pypi/simple/

# Debug pip installation
pip install cortexpy --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-public-packages/_packaging/cortexpy-packages/pypi/simple/ -v

# Check Azure CLI connectivity
az artifacts universal download --organization https://dev.azure.com/[ORG] --project cortexpy-public-packages --scope project --feed cortexpy-packages --name cortexpy --version 1.8.0 --path ./test-download
```

---

## Security Considerations

### Data Protection
- **Package Content**: Ensure no sensitive data in published packages
- **Credentials**: Never commit authentication tokens to source code
- **Dependencies**: Regular security scanning of package dependencies

### Access Control
- **Principle of Least Privilege**: Users have minimum necessary permissions
- **Regular Audits**: Quarterly review of access permissions
- **Token Rotation**: Regular rotation of Personal Access Tokens

### Network Security
- **Firewall Rules**: Properly configured network access
- **SSL/TLS**: All communications encrypted in transit
- **Monitoring**: Log and monitor all access attempts

### Compliance
- **Audit Trails**: All actions logged and auditable
- **Data Retention**: Package retention policies defined
- **Change Management**: All changes properly documented

---

## Appendix

### A. Environment Variables Reference

```bash
# Azure DevOps Configuration
AZURE_DEVOPS_ORG="[YOUR-ORGANIZATION]"
AZURE_DEVOPS_PROJECT="cortexpy-cli-public-packages"
AZURE_ARTIFACTS_FEED="cortexpy-cli-packages"

# Authentication
AZURE_DEVOPS_PAT="[PERSONAL-ACCESS-TOKEN]"
SYSTEM_ACCESSTOKEN="[SYSTEM-ACCESS-TOKEN]" # For pipelines

# Feed URLs
FEED_URL="https://pkgs.dev.azure.com/${AZURE_DEVOPS_ORG}/${AZURE_DEVOPS_PROJECT}/_packaging/${AZURE_ARTIFACTS_FEED}/pypi/simple/"
UPLOAD_URL="https://pkgs.dev.azure.com/${AZURE_DEVOPS_ORG}/${AZURE_DEVOPS_PROJECT}/_packaging/${AZURE_ARTIFACTS_FEED}/pypi/upload/"
```

### B. Azure CLI Commands Reference

```bash
# Login and set defaults
az login
az devops configure --defaults organization=https://dev.azure.com/[ORG] project=cortexpy-cli-public-packages

# Artifacts management
az artifacts universal download --organization https://dev.azure.com/[ORG] --project cortexpy-cli-public-packages --scope project --feed cortexpy-cli-packages --name cortexpy-cli --version 0.1.0 --path ./download

# Pipeline management
az pipelines run --name cortexpy-cli-build-pipeline
az pipelines show --name cortexpy-cli-build-pipeline
```

### C. PowerShell Scripts for Windows Environments

```powershell
# Install-CortexPy-CLI.ps1
param(
    [string]$Version = "latest",
    [string]$IndexUrl = "https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/"
)

Write-Host "Installing CortexPy CLI..."
if ($Version -eq "latest") {
    pip install cortexpy-cli --index-url $IndexUrl
} else {
    pip install "cortexpy-cli==$Version" --index-url $IndexUrl
}

Write-Host "Verifying installation..."
cortexpy --version
Write-Host "CortexPy CLI installed successfully"
```

### D. Docker Integration Example

```dockerfile
# Dockerfile.cortexpy-cli
FROM python:3.10-slim

# Install CortexPy CLI from public feed
RUN pip install cortexpy-cli --index-url https://pkgs.dev.azure.com/[ORG]/cortexpy-cli-public-packages/_packaging/cortexpy-cli-packages/pypi/simple/

# Verify installation
RUN cortexpy --version

WORKDIR /app
COPY . .

# Set entry point to cortexpy command
ENTRYPOINT ["cortexpy"]
```

### E. Terraform Configuration for Automation

```hcl
# azure-devops.tf
terraform {
  required_providers {
    azuredevops = {
      source  = "microsoft/azuredevops"
      version = "~>0.1"
    }
  }
}

provider "azuredevops" {
  org_service_url = "https://dev.azure.com/[ORG]"
}

resource "azuredevops_project" "cortexpy_cli_public" {
  name               = "cortexpy-cli-public-packages"
  description        = "Public distribution of CortexPy CLI Python package"
  visibility         = "public"
  version_control    = "Git"
  work_item_template = "Agile"
}

resource "azuredevops_feed" "cortexpy_cli_feed" {
  name         = "cortexpy-cli-packages"
  project_id   = azuredevops_project.cortexpy_cli_public.id
  description  = "Public feed for CortexPy CLI Python package"
}
```

---

## Document Control

| Version | Date       | Author         | Changes                    |
|---------|------------|----------------|----------------------------|
| 1.0     | 2024-12-19 | DevOps Team    | Initial comprehensive guide |
| 2.0     | 2025-06-19 | DevOps Team    | Updated for CortexPy CLI tool |

**Document Owner**: DevOps Team  
**Review Cycle**: Quarterly  
**Next Review**: September 2025  

**Approval**:
- [ ] DevOps Lead
- [ ] Security Team
- [ ] Development Team Lead
- [ ] Project Manager

---

*This document contains sensitive configuration information. Distribute only to authorized personnel.*