# Automated PyPI Deployment System

## Overview

PyForge CLI uses an automated deployment system with setuptools-scm for version management and PyPI trusted publishing for secure deployments.

## Key Features

- **Automatic Version Generation**: Versions are generated from Git commits and tags using setuptools-scm
- **Dual Deployment Pipeline**: Development versions to PyPI Test, production versions to PyPI.org
- **Trusted Publishing**: No API tokens required - uses PyPI's trusted publishing with GitHub Actions
- **Continuous Testing**: Every main branch commit creates a testable package

## Version Patterns

### Development Versions
- **Pattern**: `X.Y.Z.devN+gCOMMIT`
- **Example**: `1.0.7.dev1+gf9db985`
- **Trigger**: Commits to main branch
- **Deployment**: Automatic to PyPI Test

### Production Versions
- **Pattern**: `X.Y.Z`
- **Example**: `1.0.7`
- **Trigger**: Git tags
- **Deployment**: Automatic to PyPI.org

## Installation Commands

### Development Versions
```bash
# Install latest development version from PyPI Test
pip install -i https://test.pypi.org/simple/ pyforge-cli

# Install with fallback to PyPI for dependencies
pip install --index-url https://test.pypi.org/simple/ \
           --extra-index-url https://pypi.org/simple/ \
           pyforge-cli
```

### Production Versions
```bash
# Install latest stable version
pip install pyforge-cli

# Install specific version
pip install pyforge-cli==1.0.7
```

## Development Workflow

### For Contributors
1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Make changes**: Implement your feature
3. **Create PR**: Submit pull request to main branch
4. **Merge to main**: After approval, changes are merged
5. **Automatic deployment**: Package automatically deployed to PyPI Test
6. **Test installation**: `pip install -i https://test.pypi.org/simple/ pyforge-cli`

### For Maintainers
1. **Review PRs**: Ensure changes are ready for release
2. **Merge to main**: Development versions automatically deployed
3. **Create release**: When ready for production release
4. **Tag version**: `git tag 1.0.7 && git push origin 1.0.7`
5. **Automatic deployment**: Package automatically deployed to PyPI.org
6. **Create GitHub release**: Optional - add release notes

## Version Management

### Automatic Version Generation
- Uses setuptools-scm to generate versions from Git history
- No manual version management required
- Single source of truth for version information

### Version File
- Located at: `src/pyforge_cli/_version.py`
- Generated automatically during build
- Should not be edited manually
- Ignored by Git (in .gitignore)

### Version Import
```python
# In code
from pyforge_cli import __version__
print(f"Version: {__version__}")

# Command line
pyforge --version
```

## CI/CD Pipeline

### Workflow Triggers
- **Push to main**: Deploys development version to PyPI Test
- **Git tags**: Deploys production version to PyPI.org
- **Pull requests**: Runs tests only (no deployment)

### Build Process
1. **Test**: Run test suite and validation
2. **Build**: Create wheel and source distribution
3. **Validate**: Check package metadata with twine
4. **Deploy**: Upload to appropriate PyPI repository

### Security
- Uses PyPI trusted publishing (no API tokens)
- Environment protection for production deployments
- Scoped permissions per repository

## Troubleshooting

### Common Issues

#### Version Not Updating
**Problem**: Package shows old version after installation
**Solution**: 
```bash
# Clear pip cache
pip cache purge

# Force reinstall
pip install --force-reinstall pyforge-cli
```

#### Development Version Not Found
**Problem**: Cannot install from PyPI Test
**Solution**:
```bash
# Check if version exists on PyPI Test
pip index versions -i https://test.pypi.org/simple/ pyforge-cli

# Install with dependency fallback
pip install --index-url https://test.pypi.org/simple/ \
           --extra-index-url https://pypi.org/simple/ \
           pyforge-cli
```

#### Build Failures
**Problem**: Package build fails in CI
**Solution**:
- Ensure fetch-depth: 0 in checkout action
- Verify setuptools-scm is in build dependencies
- Check Git history is accessible

### Version Generation Issues

#### Wrong Version Number
**Problem**: setuptools-scm generates unexpected version
**Cause**: Missing Git tags or unclean working tree
**Solution**:
```bash
# Check current version
python -m setuptools_scm

# Check Git state
git status
git describe --tags

# Clean working tree if needed
git add . && git commit -m "clean up"
```

#### Missing Version File
**Problem**: `_version.py` not found
**Cause**: Package not built with setuptools-scm
**Solution**:
```bash
# Build package to generate version file
python -m build

# Or install in development mode
pip install -e .
```

## Configuration Files

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
dynamic = ["version"]

[tool.setuptools_scm]
version_file = "src/pyforge_cli/_version.py"
```

### GitHub Actions Workflow
- File: `.github/workflows/publish.yml`
- Environments: `testpypi`, `pypi`
- Permissions: `id-token: write`
- Trusted publishing configuration required in PyPI settings

## Deployment Monitoring

### GitHub Actions
- View deployment logs in Actions tab
- Monitor build and deployment status
- Check environment protection rules

### PyPI Metrics
- Package download statistics on PyPI
- Version usage analytics
- Distribution file validation

### Package Health
```bash
# Check package metadata
python -m pip show pyforge-cli

# Verify installation
python -c "import pyforge_cli; print(pyforge_cli.__version__)"

# Test CLI functionality
pyforge --help
```

## Migration Notes

### Changes from Previous System
- **Removed**: Manual version management in `pyproject.toml` and `__init__.py`
- **Added**: Dynamic version generation from Git
- **Replaced**: API token authentication with trusted publishing
- **Enhanced**: Automatic deployment for development versions

### Backward Compatibility
- All existing functionality preserved
- CLI interface unchanged
- Package import paths unchanged
- Version command works as before

## Future Enhancements

### Planned Features
- Automated changelog generation from conventional commits
- Pre-release deployment workflows (alpha, beta, rc)
- Integration with GitHub Releases for automated release notes
- Slack/Discord notifications for deployment events

### Configuration Options
- Custom version schemes
- Branch-specific deployment rules
- Extended environment protection
- Advanced deployment validation

## Support

### Getting Help
- Check this documentation first
- Review GitHub Actions logs for CI issues
- Open issues for deployment problems
- Contact maintainers for PyPI access

### Contributing
- Follow conventional commit messages
- Test changes on feature branches
- Verify version generation locally
- Update documentation for new features