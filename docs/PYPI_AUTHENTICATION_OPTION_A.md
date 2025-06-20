# PyPI Authentication - Option A: Using .pypirc File

This guide covers **Option A** for PyPI authentication using the `.pypirc` configuration file method. This is the recommended approach for local development and manual deployments.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Configuration Examples](#configuration-examples)
5. [Security Considerations](#security-considerations)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

### What is .pypirc?
The `.pypirc` file is a configuration file that stores PyPI repository information and authentication credentials. It allows you to:

- Store multiple repository configurations (Test PyPI, Production PyPI, private repositories)
- Securely store API tokens locally
- Avoid typing credentials repeatedly
- Switch between repositories easily

### When to Use Option A
✅ **Recommended for:**
- Local development environments
- Manual package uploads
- Personal projects
- Learning and testing

❌ **Not recommended for:**
- CI/CD pipelines (use environment variables instead)
- Shared development machines
- Production automation (use trusted publishers)

---

## Prerequisites

### Required Accounts
1. **Test PyPI Account**: https://test.pypi.org/account/register/
2. **Production PyPI Account**: https://pypi.org/account/register/

### Required Tools
```bash
# Ensure you have twine installed
uv add --dev twine --native-tls

# Or with pip
pip install twine
```

### 2FA Setup (Required)
Both PyPI and Test PyPI require two-factor authentication:
1. Install an authenticator app (Google Authenticator, Authy, etc.)
2. Enable 2FA in account settings
3. Save recovery codes securely

---

## Step-by-Step Setup

### Step 1: Generate API Tokens

#### For Test PyPI:
1. Go to https://test.pypi.org/manage/account/token/
2. Click **"Add API token"**
3. Configure token:
   - **Token name**: `pyforge-cli-testpypi`
   - **Scope**: Choose "Entire account" or specific project
4. Click **"Add token"**
5. **Copy the token** (starts with `pypi-`) - you won't see it again!

#### For Production PyPI:
1. Go to https://pypi.org/manage/account/token/
2. Click **"Add API token"**
3. Configure token:
   - **Token name**: `pyforge-cli-pypi`
   - **Scope**: Choose "Entire account" or specific project
4. Click **"Add token"**
5. **Copy the token** (starts with `pypi-`) - you won't see it again!

### Step 2: Create .pypirc File

#### Method 1: Using Command Line (Recommended)
```bash
# Create the .pypirc file with proper configuration
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
EOF
```

#### Method 2: Using Text Editor
```bash
# Open file in your preferred editor
nano ~/.pypirc
# or
vim ~/.pypirc
# or
code ~/.pypirc
```

Then add the configuration content (see examples below).

### Step 3: Replace Token Placeholders
Edit the file and replace the placeholder tokens:

```bash
# Edit the file
nano ~/.pypirc

# Replace these placeholders with your actual tokens:
# pypi-YOUR_PRODUCTION_TOKEN_HERE  → your actual production token
# pypi-YOUR_TEST_TOKEN_HERE        → your actual test token
```

### Step 4: Secure the File
```bash
# Set restrictive permissions (important for security)
chmod 600 ~/.pypirc

# Verify permissions
ls -la ~/.pypirc
# Should show: -rw------- (read/write for owner only)
```

### Step 5: Verify Configuration
```bash
# Test configuration with twine
twine check dist/*

# If you get authentication errors, the tokens might be incorrect
```

---

## Configuration Examples

### Basic Configuration
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJGE1YzZhNDQzLWJkNGYtNGVhOC1iNzMwLWY1OTk5MzQzYzNlZgACKlsKJGYxZjYxZWQ2LWUzNDMtNGFiOC05NmM2LTEwNmQwOTgzMGM2NRIEcHlwaQAGIAEgASgC

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZyIkZTliNzQzYjktOWY0Ni00MGJhLWFhNWMtMGE5N2QwNzMzNTMzAAIqWwokNjQxMGVhODMtZGUzMS00YjY5LWI4YjgtOTMwNzZhYTI5ZDc3EgR0ZXN0AAABAAEBKAM
```

### Configuration with Multiple Repositories
```ini
[distutils]
index-servers =
    pypi
    testpypi
    private-repo

[pypi]
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN

[private-repo]
repository = https://private.pypi.example.com/simple/
username = your-username
password = your-password
```

### Configuration with Custom Repository Names
```ini
[distutils]
index-servers =
    production
    testing
    staging

[production]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN

[testing]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN

[staging]
repository = https://staging.pypi.example.com/legacy/
username = __token__
password = pypi-YOUR_STAGING_TOKEN
```

---

## Security Considerations

### File Permissions
```bash
# CRITICAL: Always set restrictive permissions
chmod 600 ~/.pypirc

# Verify nobody else can read your tokens
ls -la ~/.pypirc
# Must show: -rw------- (600 permissions)
```

### Token Security
```bash
# ✅ DO:
- Use API tokens (never passwords)
- Set restrictive token scopes
- Rotate tokens regularly
- Keep tokens private

# ❌ DON'T:
- Commit .pypirc to version control
- Share tokens in chat/email
- Use overly broad token scopes
- Leave tokens unchanged for years
```

### Backup Strategy
```bash
# Create a secure backup of your configuration
cp ~/.pypirc ~/.pypirc.backup
chmod 600 ~/.pypirc.backup

# Store backup in secure location (not in version control)
```

### Git Protection
```bash
# Add to global gitignore to prevent accidental commits
echo ".pypirc" >> ~/.gitignore_global
git config --global core.excludesfile ~/.gitignore_global

# Also add to project .gitignore
echo ".pypirc" >> .gitignore
```

---

## Usage Examples

### Basic Upload Commands
```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to Production PyPI
twine upload --repository pypi dist/*
# or simply:
twine upload dist/*
```

### Specific File Uploads
```bash
# Upload only wheel to Test PyPI
twine upload --repository testpypi dist/pyforge_cli-0.2.0-py3-none-any.whl

# Upload only source distribution to PyPI
twine upload --repository pypi dist/pyforge_cli-0.2.0.tar.gz

# Upload specific version files
twine upload --repository testpypi dist/pyforge_cli-0.2.0*
```

### Interactive vs Non-Interactive
```bash
# Non-interactive (uses .pypirc automatically)
twine upload --repository testpypi dist/*

# Interactive mode (will prompt for credentials if .pypirc missing)
twine upload --repository testpypi dist/* --interactive

# Skip existing files (useful for re-uploads)
twine upload --repository testpypi dist/* --skip-existing
```

### Verbose Output
```bash
# Get detailed upload information
twine upload --repository testpypi dist/* --verbose

# Check uploads without actually uploading
twine check dist/*
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Permission Denied Errors
```bash
# Problem: Permission denied when reading .pypirc
# Solution: Fix file permissions
chmod 600 ~/.pypirc
```

#### 2. Authentication Failures
```bash
# Problem: 403 Forbidden errors
# Cause: Invalid or expired tokens

# Solution 1: Verify token format
cat ~/.pypirc | grep password
# Tokens should start with "pypi-"

# Solution 2: Regenerate tokens
# Go to PyPI → Account → API tokens → Regenerate
```

#### 3. Repository Not Found
```bash
# Problem: Repository 'testpypi' not found
# Cause: Typo in repository name or missing section

# Solution: Check repository names
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Or fix .pypirc configuration
```

#### 4. File Not Found Errors
```bash
# Problem: .pypirc file not found
# Solution: Check file location and existence
ls -la ~/.pypirc

# Create if missing
touch ~/.pypirc
chmod 600 ~/.pypirc
```

#### 5. Token Scope Issues
```bash
# Problem: Insufficient permissions
# Cause: Token scope too restrictive

# Solution: Check token scope on PyPI
# Regenerate with broader scope if needed
```

### Debug Commands
```bash
# Test configuration
twine check dist/*

# Show configuration (without passwords)
python -c "
import configparser
config = configparser.ConfigParser()
config.read('~/.pypirc')
for section in config.sections():
    print(f'[{section}]')
    for key, value in config.items(section):
        if 'password' not in key.lower():
            print(f'{key} = {value}')
    print()
"

# Test repository connectivity
curl -I https://upload.pypi.org/legacy/
curl -I https://test.pypi.org/legacy/
```

### Configuration Validation
```bash
# Create validation script
cat > validate_pypirc.py << 'EOF'
#!/usr/bin/env python3
import configparser
import os
from pathlib import Path

def validate_pypirc():
    pypirc_path = Path.home() / '.pypirc'
    
    if not pypirc_path.exists():
        print("❌ .pypirc file not found")
        return False
    
    # Check permissions
    stat = pypirc_path.stat()
    if oct(stat.st_mode)[-3:] != '600':
        print(f"⚠️  .pypirc permissions: {oct(stat.st_mode)[-3:]} (should be 600)")
    else:
        print("✅ .pypirc permissions correct")
    
    # Parse configuration
    config = configparser.ConfigParser()
    try:
        config.read(pypirc_path)
    except Exception as e:
        print(f"❌ Error parsing .pypirc: {e}")
        return False
    
    # Check sections
    required_sections = ['pypi', 'testpypi']
    for section in required_sections:
        if section in config:
            print(f"✅ [{section}] section found")
            
            # Check credentials
            if 'username' in config[section] and 'password' in config[section]:
                username = config[section]['username']
                password = config[section]['password']
                
                if username == '__token__' and password.startswith('pypi-'):
                    print(f"✅ [{section}] credentials look valid")
                else:
                    print(f"⚠️  [{section}] credentials format may be incorrect")
            else:
                print(f"❌ [{section}] missing username or password")
        else:
            print(f"❌ [{section}] section not found")
    
    print("✅ .pypirc validation complete")
    return True

if __name__ == "__main__":
    validate_pypirc()
EOF

python validate_pypirc.py
```

---

## Best Practices

### Security Best Practices
1. **Use API tokens, never passwords**
2. **Set minimum required token scopes**
3. **Rotate tokens every 6 months**
4. **Use different tokens for different projects**
5. **Never commit .pypirc to version control**
6. **Set proper file permissions (600)**
7. **Keep backup of configuration**

### Operational Best Practices
```bash
# Test on Test PyPI first
twine upload --repository testpypi dist/*

# Verify upload before production
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyforge-cli

# Then upload to production
twine upload dist/*
```

### Token Management
```bash
# Regular token rotation (every 6 months)
# 1. Generate new tokens on PyPI
# 2. Update .pypirc
# 3. Test uploads
# 4. Revoke old tokens

# Token naming convention
# Format: {project-name}-{environment}-{date}
# Example: pyforge-cli-prod-2024-06
```

### Multi-Project Setup
```bash
# For multiple projects, use project-specific sections
[distutils]
index-servers =
    pypi
    testpypi
    project1-pypi
    project1-testpypi

[project1-pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-PROJECT1_PRODUCTION_TOKEN

[project1-testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-PROJECT1_TEST_TOKEN
```

---

## Migration and Maintenance

### Updating Tokens
```bash
# When tokens need updating:
# 1. Generate new token on PyPI
# 2. Update .pypirc
# 3. Test with check command
twine check dist/*

# 4. Test upload to Test PyPI
twine upload --repository testpypi dist/* --skip-existing

# 5. Revoke old token on PyPI
```

### Moving to Environment Variables (CI/CD)
```bash
# For CI/CD, extract from .pypirc:
grep "password.*pypi-" ~/.pypirc

# Set as environment variables:
export TWINE_PASSWORD=pypi-your-token-here
export TWINE_USERNAME=__token__
```

### Backup and Recovery
```bash
# Create encrypted backup
gpg --symmetric --cipher-algo AES256 ~/.pypirc
# Creates ~/.pypirc.gpg

# Restore from backup
gpg --decrypt ~/.pypirc.gpg > ~/.pypirc
chmod 600 ~/.pypirc
```

---

## Quick Reference

### Essential Commands
```bash
# Create .pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = pypi, testpypi
[pypi]
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN
EOF

# Secure file
chmod 600 ~/.pypirc

# Test upload
twine upload --repository testpypi dist/*

# Production upload
twine upload dist/*
```

### File Locations
- **Configuration**: `~/.pypirc`
- **Backup**: `~/.pypirc.backup`
- **Permissions**: `600` (read/write owner only)

### Repository URLs
- **Production PyPI**: `https://upload.pypi.org/legacy/`
- **Test PyPI**: `https://test.pypi.org/legacy/`

---

*This guide covers Option A authentication for PyForge CLI deployment. For automated deployment scenarios, consider using environment variables or trusted publishers instead.*