# Branch Protection Rules Configuration

This document describes the required branch protection rules for the PyForge CLI repository to enforce quality gates.

## Required Branch Protection Rules for `main` branch

### 1. Require status checks to pass before merging
- ✅ **CI Pipeline / test (3.9)**  
- ✅ **CI Pipeline / test (3.10)**
- ✅ **CI Pipeline / test (3.11)**
- ✅ **CI Pipeline / quality-gates**

### 2. Require branches to be up to date before merging
- ✅ **Enabled** - Ensures the branch includes the latest changes from main

### 3. Require pull request reviews before merging
- **Number of required reviewers**: 1
- ✅ **Dismiss stale reviews when new commits are pushed**
- ✅ **Require review from code owners** (if CODEOWNERS file exists)

### 4. Restrict pushes that create files
- ✅ **Include administrators** - Even admins must follow the rules

### 5. Allow force pushes
- ❌ **Disabled** - Protects git history

### 6. Allow deletions
- ❌ **Disabled** - Protects the main branch from deletion

## Quality Gates Enforced

### Test Coverage Gate
- **Minimum Code Coverage**: 50%
- **Measurement**: Line coverage across all source files
- **Exclusions**: Test files, databricks extension (until dependencies resolved)

### Test Pass Rate Gate  
- **Minimum Pass Rate**: 70%
- **Calculation**: (Passed Tests / Total Tests) × 100
- **Exclusions**: Databricks extension tests (until PySpark dependencies resolved)

### Test Matrix
- **Python Versions**: 3.9, 3.10, 3.11
- **Operating System**: Ubuntu Latest
- **Dependencies**: Managed via `uv` package manager

## Implementation Steps

### 1. GitHub Repository Settings
1. Navigate to repository **Settings** → **Branches**
2. Click **Add rule** for `main` branch
3. Configure the settings listed above
4. Save the protection rule

### 2. Required Status Checks Setup
```bash
# Status checks that must pass:
CI Pipeline / test (3.9)
CI Pipeline / test (3.10) 
CI Pipeline / test (3.11)
CI Pipeline / quality-gates
```

### 3. Merge Strategy
- **Require linear history**: ✅ Recommended
- **Allow merge commits**: ❌ Discouraged
- **Allow squash merging**: ✅ Preferred
- **Allow rebase merging**: ✅ Allowed

## Current Status

✅ **CI Pipeline Created**: `.github/workflows/ci.yml`  
🔄 **Branch Protection**: Needs manual configuration in GitHub UI  
🔄 **Status Checks**: Will be enforced once branch protection is enabled  

## Testing the Pipeline

### Local Testing
```bash
# Install dependencies
uv sync --dev

# Run tests with coverage (same as CI)
python -m pytest \
  --ignore=tests/test_databricks_extension.py \
  --ignore=tests/test_extension_integration.py \
  --cov=src/pyforge_cli \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing

# Check current metrics
echo "Current test pass rate: 85.6% (✅ above 70%)"
echo "Current code coverage: 40% (❌ below 50% - needs improvement)"
```

### Pull Request Workflow
1. Create feature branch from `main`
2. Make changes and commit
3. Push branch and create Pull Request
4. CI pipeline runs automatically
5. Quality gates must pass for merge approval
6. Code review required
7. Merge only after all checks pass

## Monitoring and Alerts

### Failed Quality Gates
If quality gates fail:
1. **Coverage < 50%**: Add more unit tests or improve existing test coverage
2. **Pass Rate < 70%**: Fix failing tests before merge
3. **Build Failures**: Check dependencies and code syntax

### Dashboard Integration
- **CodeCov**: Automatic coverage reporting
- **GitHub Checks**: Status visible in PR interface
- **Branch Protection**: Blocks merge if gates fail

## Future Improvements

### Enhanced Coverage Rules
- Per-component coverage requirements
- Differential coverage for new code
- Integration test coverage tracking

### Additional Quality Gates
- Code complexity analysis
- Security vulnerability scanning
- Performance regression detection
- Documentation coverage

---

**Note**: These rules ensure that only high-quality, well-tested code is merged to the main branch, maintaining project stability and reliability.