# PyPI Automated Deployment Best Practices

## Overview

This document outlines comprehensive best practices for automated Python package deployment to PyPI Test and PyPI.org, including version management strategies, CI/CD workflows, and real-world examples from successful Python libraries.

## Table of Contents

1. [Automated Deployment Architecture](#automated-deployment-architecture)
2. [Version Numbering Strategies](#version-numbering-strategies)
3. [Development vs Production Deployment](#development-vs-production-deployment)  
4. [CI/CD Workflow Implementation](#cicd-workflow-implementation)
5. [Version Management Tools](#version-management-tools)
6. [Git Tag Integration](#git-tag-integration)
7. [Real-World Examples](#real-world-examples)
8. [Security Best Practices](#security-best-practices)
9. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)

## Automated Deployment Architecture

### Core Principles

1. **Separation of Build and Publish**: Always separate the building of distribution packages from the publishing step to ensure atomic uploads and prevent partial deployments.

2. **Test Before Production**: Deploy to TestPyPI first, test installation, then promote to production PyPI.

3. **Trusted Publishing**: Use PyPI's trusted publishing implementation with GitHub Actions for enhanced security without manual API token management.

### Recommended Workflow Structure

```yaml
name: Publish Python Package

on:
  push:
    branches: [main]
  release:
    types: [published]

permissions:
  contents: read
  id-token: write  # Required for trusted publishing

jobs:
  build:
    name: Build distribution
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Critical for setuptools-scm
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Install build dependencies
        run: python3 -m pip install build --user
      - name: Build distributions
        run: python3 -m build
      - name: Store distributions
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

  publish-to-testpypi:
    name: Publish to TestPyPI
    needs: [build]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment:
      name: testpypi
      url: https://test.pypi.org/p/YOUR-PACKAGE
    permissions:
      id-token: write
    steps:
      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  publish-to-pypi:
    name: Publish to PyPI
    needs: [build]
    runs-on: ubuntu-latest
    if: github.event_name == 'release' && github.event.action == 'published'
    environment:
      name: pypi
      url: https://pypi.org/p/YOUR-PACKAGE
    permissions:
      id-token: write
    steps:
      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

## Version Numbering Strategies

### Semantic Versioning (SemVer)

Follow the `MAJOR.MINOR.PATCH` format where:
- **MAJOR**: Breaking changes that are not backward compatible
- **MINOR**: New features that are backward compatible
- **PATCH**: Bug fixes that are backward compatible

### PEP 440 Compliance

All Python packages must comply with PEP 440 for version identifiers:

- **Final releases**: `1.2.3`
- **Pre-releases**: `1.2.3a1`, `1.2.3b2`, `1.2.3rc1`
- **Post-releases**: `1.2.3.post1` (for minor corrections)
- **Development releases**: `1.2.3.dev0`
- **Local versions**: `1.2.3+local.version`

### Development Version Patterns

For continuous deployment to TestPyPI:

1. **Time-based**: `1.2.3.dev20231201120000`
2. **Commit-based**: `1.2.3.dev+g1234567`
3. **Build-based**: `1.2.3.dev123`

## Development vs Production Deployment

### Strategy 1: Branch-Based Deployment

```yaml
# Deploy dev versions on every main branch commit
on:
  push:
    branches: [main]
  # Deploy production versions on releases
  release:
    types: [published]
```

### Strategy 2: Tag-Based Deployment

```yaml
# Deploy dev versions on commits
on:
  push:
    branches: [main]
  # Deploy production on version tags
  push:
    tags: ['v*']
```

### Version Patterns by Environment

| Environment | Trigger | Version Pattern | Example |
|-------------|---------|----------------|---------|
| TestPyPI | Every commit to main | `X.Y.Z.devN+commit` | `1.2.3.dev45+g1a2b3c4` |
| PyPI | GitHub Release | `X.Y.Z` | `1.2.3` |
| PyPI | Pre-release tag | `X.Y.ZrcN` | `1.2.3rc1` |

## CI/CD Workflow Implementation

### Complete GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]
  release:
    types: [published]

env:
  PYTHON_VERSION: "3.11"

jobs:
  test:
    name: Test Suite
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[test]
      - name: Run tests
        run: pytest
      - name: Run linting
        run: |
          black --check .
          isort --check-only .
          flake8

  build:
    name: Build Package
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install build dependencies
        run: python -m pip install build twine
      - name: Build package
        run: python -m build
      - name: Check package
        run: twine check dist/*
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: distributions
          path: dist/

  publish-dev:
    name: Publish Development Version
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: testpypi
    permissions:
      id-token: write
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: distributions
          path: dist/
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  publish-release:
    name: Publish Release
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'release' && github.event.action == 'published'
    environment: pypi
    permissions:
      id-token: write
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: distributions
          path: dist/
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

## Version Management Tools

### 1. setuptools-scm (Recommended)

**Advantages:**
- Automatic version extraction from Git tags
- No manual version management required
- Supports development versions
- Integrates seamlessly with setuptools

**Configuration:**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
dynamic = ["version"]

[tool.setuptools_scm]
version_file = "src/mypackage/_version.py"
```

**Usage:**
```bash
# Check current version
python -m setuptools_scm

# Build with automatic versioning
python -m build
```

### 2. python-semantic-release

**Advantages:**
- Fully automated releases based on commit messages
- Changelog generation
- Git tag creation
- Multi-file version updates

**Configuration:**

```toml
# pyproject.toml
[tool.semantic_release]
version_variables = [
    "src/mypackage/__init__.py:__version__",
    "pyproject.toml:version"
]
build_command = "python -m pip install build && python -m build"
major_on_zero = false
```

**GitHub Actions Integration:**

```yaml
- name: Python Semantic Release
  uses: python-semantic-release/python-semantic-release@v8.3.0
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    root_options: "-vv"
```

### 3. bump2version/bump-my-version

**Advantages:**
- Simple command-line interface
- Multi-file version updates
- Custom version part definitions
- VCS integration

**Configuration:**

```ini
# .bumpversion.cfg
[bumpversion]
current_version = 0.1.0
commit = True
tag = True

[bumpversion:file:setup.py]
[bumpversion:file:mypackage/__init__.py]
```

**Usage:**
```bash
bump2version patch  # 0.1.0 -> 0.1.1
bump2version minor  # 0.1.1 -> 0.2.0
bump2version major  # 0.2.0 -> 1.0.0
```

## Git Tag Integration

### setuptools-scm with GitHub Actions

Critical requirements for setuptools-scm in CI/CD:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Essential: fetches complete history including tags
```

### Version Calculation Rules

1. **On tagged commit**: Returns exact tag version (e.g., `1.2.3`)
2. **After tagged commit**: Returns tag + development info (e.g., `1.2.4.dev2+g1a2b3c4`)
3. **No tags**: Returns `0.1.dev0+g1a2b3c4`

### Tag Naming Conventions

```bash
# Recommended patterns
git tag v1.2.3      # Production release
git tag v1.2.3rc1   # Release candidate
git tag v1.2.3a1    # Alpha release
git tag v1.2.3b1    # Beta release
```

## Real-World Examples

### Example 1: Tryceratops (Linting Tool)

**Features:**
- python-semantic-release for automation
- Poetry for building
- Multi-file version updates
- GitHub Actions integration

**Configuration:**
```toml
[tool.semantic_release]
version_variable = [
    "src/tryceratops/__init__.py:__version__",
    "pyproject.toml:version"
]
build_command = "pip install poetry && poetry build"
major_on_zero = false
```

### Example 2: FastAPI (Web Framework)

**Features:**
- setuptools-scm for versioning
- Comprehensive test matrix
- Multiple Python version support
- Documentation deployment

**Workflow Pattern:**
```yaml
name: Test and Deploy
on:
  push:
    tags: ['*']
  push:
    branches: [master]
```

### Example 3: Requests (HTTP Library)

**Features:**
- Manual release process with automation
- Extensive testing before deployment
- Multiple environment deployment
- Security-focused approach

## Security Best Practices

### 1. Trusted Publishing (Recommended)

Configure trusted publishing in PyPI settings:
- No API tokens required
- Scoped to specific repositories
- Automatic token generation and expiration

### 2. API Token Management

If using API tokens:
```yaml
environment:
  name: pypi
  url: https://pypi.org/project/YOUR-PACKAGE
```

- Store tokens as GitHub repository secrets
- Use scoped tokens (project-specific)
- Regularly rotate tokens
- Use different tokens for TestPyPI and PyPI

### 3. Environment Protection

```yaml
environment:
  name: pypi
  protection_rules:
    - type: required_reviewers
      reviewers: ["maintainer1", "maintainer2"]
    - type: wait_timer
      minutes: 5
```

## Common Pitfalls and Solutions

### 1. Version Conflicts

**Problem:** Version already exists on PyPI
**Solution:** 
- Use development versions for TestPyPI
- Implement proper version bumping
- Never reuse version numbers

### 2. Incomplete Git History

**Problem:** setuptools-scm returns `0.1.dev0`
**Solution:**
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Fetch complete history
```

### 3. TestPyPI Size Limits

**Problem:** Frequent uploads exceed TestPyPI limits
**Solution:**
- Clean up old versions regularly
- Use local PyPI server for testing
- Implement smarter deployment triggers

### 4. Dependency Resolution

**Problem:** TestPyPI packages can't install dependencies
**Solution:**
```bash
# Install with fallback to PyPI
pip install --index-url https://test.pypi.org/simple/ \
           --extra-index-url https://pypi.org/simple/ \
           your-package
```

### 5. Build Reproducibility

**Problem:** Different builds produce different artifacts
**Solution:**
- Pin build dependencies
- Use consistent build environments
- Implement artifact validation

## Implementation Checklist

### Initial Setup
- [ ] Configure trusted publishing or API tokens
- [ ] Set up repository secrets
- [ ] Create environment protection rules
- [ ] Configure branch protection

### Workflow Configuration
- [ ] Implement build job with artifact storage
- [ ] Configure TestPyPI deployment on main branch commits
- [ ] Configure PyPI deployment on releases
- [ ] Add comprehensive test suite
- [ ] Implement version management strategy

### Version Management
- [ ] Choose and configure version management tool
- [ ] Set up automatic version detection
- [ ] Configure multi-file version updates
- [ ] Test version calculation locally

### Testing and Validation
- [ ] Test installation from TestPyPI
- [ ] Validate package metadata
- [ ] Check dependency resolution
- [ ] Verify distribution completeness

### Monitoring and Maintenance
- [ ] Set up deployment notifications
- [ ] Monitor package download statistics
- [ ] Regularly audit and rotate secrets
- [ ] Keep dependencies updated

## Conclusion

Automated PyPI deployment requires careful planning and implementation of security, versioning, and CI/CD best practices. The strategies outlined in this document provide a comprehensive foundation for implementing reliable, secure, and maintainable package deployment pipelines.

Key success factors:
1. Use trusted publishing for security
2. Implement proper version management
3. Test thoroughly before production deployment
4. Follow semantic versioning principles
5. Monitor and maintain deployment pipelines

By following these best practices and learning from successful real-world implementations, teams can create robust automated deployment systems that enhance productivity while maintaining security and reliability.