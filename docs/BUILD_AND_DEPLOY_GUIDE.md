# PyForge CLI - Build and Deploy Guide

This comprehensive guide covers the complete process of building and deploying PyForge CLI to PyPI repositories.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Pre-Build Checklist](#pre-build-checklist)
4. [Building the Package](#building-the-package)
5. [Testing the Build](#testing-the-build)
6. [PyPI Account Setup](#pypi-account-setup)
7. [Deploying to Test PyPI](#deploying-to-test-pypi)
8. [Testing Installation from Test PyPI](#testing-installation-from-test-pypi)
9. [Deploying to Production PyPI](#deploying-to-production-pypi)
10. [Automated Deployment with GitHub Actions](#automated-deployment-with-github-actions)
11. [Troubleshooting](#troubleshooting)
12. [Post-Deployment](#post-deployment)

---

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Git**: For version control
- **Internet Connection**: For PyPI uploads
- **Terminal/Command Line**: Access to command line interface

### Required Tools
```bash
# Install build tools (choose one method)

# Method 1: Using pip
pip install build twine

# Method 2: Using uv (if available)
uv add --dev build twine

# Method 3: Using our requirements file
pip install -r requirements-dev.txt
```

---

## Development Environment Setup

### 1. Clone and Navigate to Project
```bash
git clone https://github.com/Py-Forge-Cli/PyForge-CLI.git
cd PyForge-CLI
```

### 2. Set Up Development Environment (Recommended)

#### Automated Setup (Easiest)
```bash
python scripts/setup_dev_environment.py
```

#### Or Use Make Commands
```bash
make setup-dev
```

#### Manual Setup
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Development Dependencies
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or install the package in development mode
pip install -e ".[dev]"
```

---

## Pre-Build Checklist

### ✅ Version Management
1. **Update Version Number** in `pyproject.toml`:
   ```toml
   [project]
   name = "pyforge-cli"
   version = "0.2.0"  # ← Update this
   ```

2. **Update CHANGELOG.md** with new features and fixes:
   ```markdown
   ## [0.2.0] - 2024-06-19
   ### Added
   - New feature descriptions
   
   ### Fixed
   - Bug fix descriptions
   ```

### ✅ Code Quality Checks
```bash
# Run linting
ruff check src tests

# Run type checking
mypy src

# Run tests
pytest tests/ --cov=pyforge_cli

# Run security scan
bandit -r src/
```

### ✅ Documentation Updates
1. **README.md** - Ensure installation instructions are current
2. **CHANGELOG.md** - Document all changes
3. **API Documentation** - Update any API changes

### ✅ Git Status Clean
```bash
# Ensure all changes are committed
git status
git add .
git commit -m "Prepare for release v0.2.0"
git push origin main
```

---

## Building the Package

### Method 1: Using Python Build (Recommended)
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source distribution and wheel
python -m build

# Expected output:
# Successfully built pyforge_cli-0.2.0.tar.gz and pyforge_cli-0.2.0-py3-none-any.whl
```

### Method 2: Using UV Build
```bash
# Clean previous builds
rm -rf dist/

# Build with uv
uv build

# Note: May require network access for dependencies
```

### Method 3: Manual Build Steps
```bash
# Build source distribution
python -m build --sdist

# Build wheel
python -m build --wheel
```

---

## Testing the Build

### 1. Validate Package Integrity
```bash
# Check package metadata and structure
twine check dist/*

# Expected output:
# Checking dist/pyforge_cli-0.2.0-py3-none-any.whl: PASSED
# Checking dist/pyforge_cli-0.2.0.tar.gz: PASSED
```

### 2. Inspect Package Contents
```bash
# List files in wheel
unzip -l dist/pyforge_cli-0.2.0-py3-none-any.whl

# Extract and inspect source distribution
tar -tzf dist/pyforge_cli-0.2.0.tar.gz | head -20
```

### 3. Test Local Installation
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from wheel
pip install dist/pyforge_cli-0.2.0-py3-none-any.whl

# Test CLI command
pyforge --help

# Clean up
deactivate
rm -rf test_env
```

---

## PyPI Account Setup

### 1. Create Accounts
1. **Test PyPI**: https://test.pypi.org/account/register/
2. **Production PyPI**: https://pypi.org/account/register/

### 2. Enable Two-Factor Authentication (Required)
1. Go to Account Settings
2. Enable 2FA using authenticator app
3. Generate recovery codes and store securely

### 3. Generate API Tokens

#### For Test PyPI:
1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `pyforge-cli-testpypi`
4. Scope: "Entire account" or specific project
5. Copy token (starts with `pypi-`)

#### For Production PyPI:
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `pyforge-cli-pypi`
4. Scope: "Entire account" or specific project
5. Copy token (starts with `pypi-`)

### 4. Configure Authentication

#### Option A: Using .pypirc File
```bash
# Create ~/.pypirc file
cat > ~/.pypirc << EOF
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

# Secure the file
chmod 600 ~/.pypirc
```

#### Option B: Environment Variables
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
```

---

## Deploying to Test PyPI

### 1. Upload to Test PyPI
```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Or specify files explicitly
twine upload --repository testpypi dist/pyforge_cli-0.2.0*
```

### 2. Expected Output
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading pyforge_cli-0.2.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 56.1/56.1 kB • 00:01
Uploading pyforge_cli-0.2.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 84.3/84.3 kB • 00:01

View at:
https://test.pypi.org/project/pyforge-cli/0.2.0/
```

### 3. Verify Upload
Visit: https://test.pypi.org/project/pyforge-cli/

---

## Testing Installation from Test PyPI

### 1. Create Clean Test Environment
```bash
# Create fresh virtual environment
python -m venv test_install
source test_install/bin/activate
```

### 2. Install from Test PyPI
```bash
# Install from Test PyPI (dependencies from regular PyPI)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyforge-cli

# Or install specific version
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyforge-cli==0.2.0
```

### 3. Test Installation
```bash
# Test CLI is available
pyforge --version
pyforge --help

# Test basic functionality
pyforge convert --help

# Run basic conversion test if you have test files
pyforge convert test.xlsx output/ --format parquet
```

### 4. Clean Up Test Environment
```bash
deactivate
rm -rf test_install
```

---

## Deploying to Production PyPI

### ⚠️ Pre-Production Checklist
- [ ] Tested on Test PyPI successfully
- [ ] All tests pass
- [ ] Documentation is complete
- [ ] Version number is correct
- [ ] CHANGELOG is updated
- [ ] No sensitive information in package

### 1. Upload to Production PyPI
```bash
# Upload to production PyPI
twine upload dist/*

# Or be explicit about files
twine upload dist/pyforge_cli-0.2.0*
```

### 2. Expected Output
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading pyforge_cli-0.2.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 56.1/56.1 kB • 00:02
Uploading pyforge_cli-0.2.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 84.3/84.3 kB • 00:01

View at:
https://pypi.org/project/pyforge-cli/0.2.0/
```

### 3. Verify Production Deployment
```bash
# Install from production PyPI
pip install pyforge-cli

# Test installation
pyforge --version
```

### 4. Create Git Tag
```bash
# Tag the release
git tag v0.2.0
git push origin v0.2.0

# Or create annotated tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

---

## Automated Deployment with GitHub Actions

### 1. Set Up Repository Secrets
In your GitHub repository:

1. Go to `Settings` → `Secrets and variables` → `Actions`
2. Add repository secrets:
   - `PYPI_API_TOKEN`: Your production PyPI token
   - `TEST_PYPI_API_TOKEN`: Your Test PyPI token

### 2. Configure Trusted Publishers (Recommended)

#### On PyPI:
1. Go to your project on PyPI
2. Go to `Manage` → `Publishing`
3. Add a "trusted publisher"
4. Configure:
   - **Owner**: Your GitHub username/organization
   - **Repository name**: Your repository name
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi` (optional but recommended)

#### On Test PyPI:
1. Go to your project on Test PyPI
2. Follow same steps as above
3. Environment name: `testpypi`

### 3. Automated Release Process
```bash
# Create and push a tag to trigger release
git tag v0.2.0
git push origin v0.2.0

# Or create release through GitHub UI
# This will automatically trigger the publish workflow
```

### 4. Monitor Workflow
1. Go to `Actions` tab in your repository
2. Watch the `Publish to PyPI` workflow
3. Check logs for any issues

---

## Troubleshooting

### Common Build Issues

#### 1. Import Errors During Build
**Problem**: Module not found during build
```bash
ModuleNotFoundError: No module named 'pyforge_cli'
```

**Solution**:
```bash
# Ensure package structure is correct
ls src/pyforge_cli/

# Check pyproject.toml configuration
grep -A 5 "\[tool.hatch.build.targets.wheel\]" pyproject.toml
```

#### 2. Version Conflicts
**Problem**: Version already exists on PyPI
```
ERROR: HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists.
```

**Solution**:
```bash
# Update version in pyproject.toml
# Rebuild and redeploy
```

#### 3. Authentication Issues
**Problem**: 403 Forbidden errors
```
ERROR: HTTPError: 403 Forbidden from https://upload.pypi.org/legacy/
```

**Solutions**:
```bash
# Check token validity
twine check dist/*

# Verify .pypirc file permissions
ls -la ~/.pypirc

# Test with environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-token-here
```

### Common Upload Issues

#### 1. Large File Upload Timeout
**Problem**: Upload times out for large packages
```bash
# Use slower, more reliable upload
twine upload --verbose dist/*
```

#### 2. Metadata Validation Errors
**Problem**: Invalid package metadata
```bash
# Validate before upload
twine check dist/*

# Check pyproject.toml syntax
python -m pyproject_metadata dist/pyforge_cli-0.2.0.tar.gz
```

#### 3. Network/Certificate Issues
**Problem**: SSL certificate errors
```bash
# Update certificates
pip install --upgrade certifi

# Or use specific CA bundle
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
```

### Build Tool Issues

#### 1. UV Build Network Issues
**Problem**: UV can't fetch dependencies
```bash
# Fall back to pip build
pip install build
python -m build
```

#### 2. Hatchling Build Issues
**Problem**: Build backend errors
```bash
# Try different build backend
pip install setuptools wheel
python setup.py sdist bdist_wheel
```

---

## Post-Deployment

### 1. Update Documentation
- [ ] Update README installation instructions
- [ ] Update version badges
- [ ] Update documentation website

### 2. Announce Release
- [ ] Create GitHub release with changelog
- [ ] Post on social media/forums
- [ ] Update package registries (if applicable)

### 3. Monitor Package
- [ ] Check PyPI package page
- [ ] Monitor download statistics
- [ ] Watch for user issues

### 4. Prepare Next Development Cycle
```bash
# Bump to next development version
# In pyproject.toml, change:
version = "0.2.1.dev0"

git add pyproject.toml
git commit -m "Bump version to 0.2.1.dev0"
git push origin main
```

---

## Quick Reference Commands

### Complete Build and Deploy Workflow
```bash
# 1. Prepare
git status && git pull origin main

# 2. Update version in pyproject.toml
# 3. Update CHANGELOG.md

# 4. Quality checks
pytest tests/ && ruff check src/ && mypy src/

# 5. Commit changes
git add . && git commit -m "Prepare release v0.2.0"

# 6. Build
rm -rf dist/ && python -m build

# 7. Test build
twine check dist/*

# 8. Upload to Test PyPI
twine upload --repository testpypi dist/*

# 9. Test installation
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyforge-cli

# 10. Upload to PyPI
twine upload dist/*

# 11. Tag release
git tag v0.2.0 && git push origin v0.2.0
```

### Environment Variables
```bash
# For automated deployment
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
export TWINE_REPOSITORY=pypi  # or testpypi
```

---

## Security Best Practices

1. **Never commit API tokens** to version control
2. **Use environment variables** for CI/CD
3. **Enable 2FA** on PyPI accounts
4. **Use trusted publishers** when possible
5. **Regularly rotate tokens**
6. **Scan dependencies** for vulnerabilities
7. **Sign releases** with GPG if possible

---

## Support and Resources

- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **GitHub Actions**: https://docs.github.com/en/actions
- **Project Issues**: https://github.com/Py-Forge-Cli/PyForge-CLI/issues

---

*This guide is maintained as part of the PyForge CLI project. For updates and corrections, please contribute to the repository.*