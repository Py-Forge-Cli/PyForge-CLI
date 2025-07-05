# PyForge CLI Branching Strategy

## Overview

PyForge CLI uses a simplified two-branch strategy optimized for Python package development and PyPI publishing. This strategy balances rapid development with stable releases.

## Branch Structure

```
main (stable, bug fixes only)
│
├── hotfix/critical-bug-fix (→ main)
│
develop (features, active development)
│
├── feature/new-converter-support (→ develop)
├── feature/enhanced-cli-options (→ develop)
└── bugfix/minor-issue-fix (→ develop)
```

## Branch Responsibilities

### `main` Branch
- **Purpose**: Stable, production-ready code with bug fixes only
- **Version Pattern**: `1.0.x` (patch releases)
- **Merges From**: Hotfix branches, critical bug fixes
- **Deployment**: Patch dev versions to TestPyPI, tagged releases to PyPI
- **Protection**: Requires PR reviews, all status checks must pass

### `develop` Branch  
- **Purpose**: Active development, new features, and improvements
- **Version Pattern**: `1.x.0`, `x.0.0` (minor/major releases)
- **Merges From**: Feature branches, enhancement branches
- **Deployment**: Feature dev versions to TestPyPI, tagged releases to PyPI
- **Protection**: Requires status checks, allows maintainer pushes

### Feature Branches
- **Naming**: `feature/description` or `feature/issue-number`
- **Source**: Created from `develop`
- **Merge Target**: `develop`
- **Lifespan**: Short-lived (1-5 days)

### Hotfix Branches
- **Naming**: `hotfix/description` or `hotfix/issue-number`
- **Source**: Created from `main`
- **Merge Target**: `main` (then merge main → develop)
- **Lifespan**: Very short-lived (hours to 1 day)

## Version Strategy

### Semantic Versioning
We follow [Semantic Versioning](https://semver.org/) with PEP-440 compliance:

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes (rare)
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Development Versions
Using `setuptools-scm` for automatic versioning:

- **main branch**: `1.0.6.dev4` (patch dev versions)
- **develop branch**: `1.1.0.dev12` (feature dev versions)
- **Tagged releases**: `1.0.6`, `1.1.0`

### Version Examples
```
1.0.5        # Current stable release
1.0.6.dev3   # Development version on main (bug fixes)
1.1.0.dev8   # Development version on develop (new features)
1.0.6        # Next patch release from main
1.1.0        # Next minor release from develop
```

## Workflow Process

### For Bug Fixes (main branch)
1. **Create hotfix branch**: `git checkout -b hotfix/fix-csv-encoding main`
2. **Implement fix**: Make minimal changes to fix the issue
3. **Test thoroughly**: Ensure fix doesn't break existing functionality
4. **Create PR**: Target `main` branch
5. **Merge**: After review and CI passes
6. **Merge main → develop**: Keep develop up to date

### For New Features (develop branch)
1. **Create feature branch**: `git checkout -b feature/add-json-support develop`
2. **Implement feature**: Add new functionality with tests
3. **Test comprehensively**: Full test suite including integration tests
4. **Create PR**: Target `develop` branch
5. **Merge**: After review and CI passes

### For Releases

#### Patch Release (from main)
1. **Tag release**: `git tag v1.0.6`
2. **Push tag**: `git push origin v1.0.6`
3. **Automatic deployment**: GitHub Actions publishes to PyPI

#### Feature Release (from develop)
1. **Merge develop → main**: Create PR from develop to main
2. **Tag release**: `git tag v1.1.0`
3. **Push tag**: `git push origin v1.1.0`
4. **Automatic deployment**: GitHub Actions publishes to PyPI

## CI/CD Pipeline

### Branch-Specific Testing

#### Main Branch (`ci-main.yml`)
- **Focus**: Stability and regression testing
- **Tests**: Core functionality, exclude slow tests
- **Matrix**: Python 3.9, 3.10, 3.11
- **Deployment**: Dev versions to TestPyPI

#### Develop Branch (`ci-develop.yml`)
- **Focus**: Comprehensive testing including new features
- **Tests**: Full test suite, integration tests, PySpark tests
- **Matrix**: Python 3.9, 3.10, 3.11 × Ubuntu, Windows, macOS
- **Deployment**: Dev versions to TestPyPI

#### Release (`release.yml`)
- **Trigger**: Git tags matching `v*`
- **Tests**: Full test suite across all platforms
- **Deployment**: Production PyPI + GitHub Release

### Deployment Strategy

| Branch | TestPyPI | PyPI | Version Pattern |
|--------|----------|------|----------------|
| main | ✅ (dev) | ✅ (tagged) | 1.0.x.devN → 1.0.x |
| develop | ✅ (dev) | ✅ (tagged) | 1.x.0.devN → 1.x.0 |
| feature | ❌ | ❌ | N/A |
| hotfix | ❌ | ❌ | N/A |

## Branch Protection Rules

### Main Branch
- ✅ Require pull request reviews (1 reviewer)
- ✅ Dismiss stale reviews when new commits are pushed
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators in restrictions
- ✅ Allow force pushes: No
- ✅ Allow deletions: No

### Develop Branch
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Allow force pushes: No
- ✅ Allow deletions: No
- ⚠️ Allow maintainer pushes (for quick fixes)

## Release Schedule

### Patch Releases
- **Frequency**: As needed for critical bugs
- **Source**: main branch
- **Timeline**: Same day as bug fix
- **Scope**: Bug fixes only

### Feature Releases  
- **Frequency**: Weekly/bi-weekly
- **Source**: develop branch
- **Timeline**: Every 1-2 weeks
- **Scope**: New features, improvements

### Major Releases
- **Frequency**: Quarterly/as needed
- **Source**: develop branch
- **Timeline**: 3-6 months
- **Scope**: Breaking changes, major features

## Best Practices

### Code Quality
- **All branches**: Must pass linting (ruff), formatting (black), type checking (mypy)
- **Tests required**: All new features must include tests
- **Coverage**: Maintain >80% code coverage
- **Security**: Pass security checks (bandit, safety)

### Documentation
- **Features**: Update README.md and docs/ for new features
- **Breaking changes**: Update CHANGELOG.md with migration notes
- **API changes**: Update docstrings and type hints

### Review Process
- **Patch fixes**: 1 reviewer required
- **New features**: 1 reviewer required + discussion for significant changes
- **Breaking changes**: Team discussion + documentation

## Migration Guide

### From Single Branch
If you're currently using only `main`:
1. Create `develop` branch from `main`
2. Set up branch protection rules
3. Update CI workflows
4. Start using feature branches

### From GitFlow
If you're using traditional GitFlow:
1. Keep `main` and `develop` branches
2. Remove `release/*` branches (handled by tagging)
3. Convert `hotfix/*` to direct fixes on `main`
4. Update CI workflows for simplified approach

## Troubleshooting

### Common Issues

**Q: Version number isn't incrementing**
A: Check that setuptools-scm is installed and you have proper git history

**Q: TestPyPI deployment fails**
A: Ensure the version doesn't already exist, use `skip-existing: true`

**Q: CI fails on develop but passes on main**
A: Develop runs more comprehensive tests; check integration test logs

**Q: Release deployment fails**
A: Verify PyPI trusted publisher is configured correctly

### Commands Reference

```bash
# Check current version
python -c "import setuptools_scm; print(setuptools_scm.get_version())"

# Create feature branch
git checkout develop
git checkout -b feature/new-feature

# Create hotfix branch
git checkout main
git checkout -b hotfix/critical-fix

# Merge feature to develop
git checkout develop
git merge --no-ff feature/new-feature

# Release patch version
git checkout main
git tag v1.0.6
git push origin v1.0.6

# Release feature version
git checkout main
git merge --no-ff develop
git tag v1.1.0
git push origin v1.1.0
```

---

This branching strategy provides a balance between rapid development and stable releases, optimized for PyForge CLI's needs as a Python package distributed via PyPI.