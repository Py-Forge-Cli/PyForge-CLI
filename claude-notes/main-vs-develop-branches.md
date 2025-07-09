# Main vs Develop Branch Strategy - PyForge CLI

## Overview

This document explains the branch management strategy for the PyForge-CLI project, specifically the differences and purposes of the `main` and `develop` branches.

## Current Branch Status

### Main Branch

The `main` branch represents the stable, production-ready version of the codebase.

**Latest commit:**

- `a6f54e5` - Update CI workflow to run tests only on Python 3.10

### Develop Branch

The `develop` branch contains ongoing development work and feature integrations.

**Recent Pull Requests Merged:**

#### PR #36: Fix missing get_metadata implementations and test failures (Issue #35)

**Merged:** July 6, 2025
**Impact:** 22 files changed, +2,135 lines, -119 lines

**Key Changes:**

- Fixed all 9 failing tests related to missing `get_metadata` implementations
- Added comprehensive metadata extraction for all converter types:
  - **Excel**: Fixed document properties handling for openpyxl limitations
  - **MDB**: Fixed mock test issues and connection handling
  - **XML**: Enhanced namespace detection, depth calculation, and encoding detection
  - **DBF**: Added complete metadata implementation with file stats
  - **CSV**: Enhanced metadata with encoding detection
  - **PDF**: Improved metadata extraction
- Enabled PySpark tests by default (removed skip logic)
- Test results improved from 373 passed/9 failed to 381 passed/0 failed
- Code coverage increased from 48% to 49%

#### PR #33: Databricks Extension V2 with Python 3.10 compatibility

**Merged:** July 5, 2025
**Impact:** 209 files changed, +40,593 lines, -6,011 lines (Major feature addition)

**Key Changes:**

- **Databricks Extension Architecture:**
  - Complete Databricks extension with Spark converters
  - Environment detection for Classic vs Serverless
  - Volume operations with fallback mechanisms
  - Cache management for improved performance
  - 53 new tests for Databricks functionality

- **Spark Converters Added:**
  - `SparkCSVConverter`: Optimized CSV processing with Spark
  - `SparkExcelConverter`: Large Excel file processing
  - `SparkXMLConverter`: Distributed XML processing
  - Delta Lake support for output formats
  - Streaming support for large datasets

- **Python Compatibility:**
  - Fixed all test failures for Python 3.10 compatibility
  - Updated mocking patterns and assertions
  - Configured for Databricks Runtime 14.3 LTS
  - PySpark 3.5.0 compatibility

- **Documentation:**
  - Added comprehensive Databricks deployment guide
  - Extension developer guide and API reference
  - Performance benchmarks documentation
  - Testing guide for Databricks extensions

## Branch Purposes

### Main Branch

- **Stability**: Contains only thoroughly tested and reviewed code
- **Releases**: All official releases (v1.0.x) are tagged from this branch
- **CI/CD**: Has simplified CI running only on Python 3.10
- **PyPI Deployment**: Code deployed to PyPI comes from this branch

### Develop Branch

- **Active Development**: Where new features and fixes are integrated
- **Extended Testing**: More comprehensive CI/CD testing
- **Pre-release Features**: Contains unreleased improvements
- **Integration Testing**: Where features are tested together before release

## Key Differences

### CI/CD Configuration

- **Main**: Simplified CI workflow (`ci.yml`) - tests only on Python 3.10
- **Develop**: Enhanced CI workflow (`ci-develop.yml`) - comprehensive testing and reporting

### Testing Strategy

- **Main**: Focused on stability with minimal test matrix
- **Develop**: Full test matrix across multiple Python versions and OS platforms

### Code Quality

- **Main**: Production-ready code only
- **Develop**: May contain experimental features being tested

## Workflow

### Standard Development Flow

1. Create feature branch from `develop`
2. Implement feature/fix
3. Create PR to merge feature branch → `develop`
4. Test integration on `develop`
5. When ready for release, create PR to merge `develop` → `main`
6. Tag release on `main`
7. Deploy to PyPI from `main`

### Hotfix Flow

1. Create hotfix branch from `main`
2. Implement critical fix
3. Create PR to merge hotfix → `main`
4. Tag patch release
5. Merge `main` back to `develop` to include hotfix

## Current Development Focus

### In Develop (Not Yet Released)

1. **Databricks Extension V2** (PR #33)
   - Complete Spark-based converter suite
   - Environment detection and adaptation
   - Volume operations and caching
   - 209 files changed, massive feature addition

2. **Metadata Extraction Fixes** (PR #36)
   - All converters now have working `get_metadata` methods
   - Fixed 9 failing tests
   - Improved error handling for malformed files
   - Better library compatibility

3. **Windows Compatibility**
   - Full Windows support with UTF-8 encoding fixes
   - ASCII-only characters for cross-platform compatibility

4. **Enhanced Testing**
   - Improved test coverage (46% → 49%)
   - PySpark tests enabled by default
   - Comprehensive test reporting

5. **Code Quality**
   - Black formatting applied across codebase
   - Linting improvements
   - Better error messages and logging

### Released in Main

- Stable v1.0.x releases
- Core PyForge CLI functionality
- Basic converter implementations

## Feature Comparison

### Available in Main

- Basic file conversion (CSV, XML, Excel, PDF, MDB, DBF)
- Standard CLI commands
- PyPI package distribution
- Basic testing suite

### Additional in Develop

- **Databricks Extension** with Spark converters
- **Enhanced metadata extraction** for all file types
- **Improved test coverage** and reporting
- **Better error handling** and user feedback
- **Performance optimizations** for large files
- **Extended documentation** and guides

## Best Practices

1. **Always develop on feature branches** created from `develop`
2. **Never commit directly to `main`** - use PR workflow
3. **Keep branches synchronized** - merge `main` to `develop` after releases
4. **Run full tests locally** before creating PRs
5. **Update documentation** as part of feature development

## Commands Reference

```bash
# Work with develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Keep develop updated with main
git checkout develop
git merge origin/main

# View branch differences
git log --oneline origin/main..origin/develop  # Commits in develop not in main
git log --oneline origin/develop..origin/main  # Commits in main not in develop

# View PR details
gh pr list --state closed --base develop
gh pr view <PR-number> --json files,additions,deletions
```

## Next Release Planning

The next release from `develop` to `main` will include:

1. **Major Feature**: Databricks Extension V2
2. **Bug Fixes**: All metadata extraction issues resolved
3. **Improvements**: Better test coverage and Windows compatibility
4. **Documentation**: Comprehensive guides for Databricks deployment

This represents a significant enhancement to PyForge CLI's capabilities, especially for enterprise users working with Databricks environments.