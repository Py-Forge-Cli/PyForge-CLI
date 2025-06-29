# PyPI Trusted Publisher Setup Guide

## Issue Resolution

The automated PyPI deployment failed with:

```
Trusted publishing exchange failure: 
* `invalid-publisher`: valid token, but no corresponding publisher (All lookup strategies exhausted)
```

This error occurs because **trusted publisher configuration is missing in PyPI settings**.

## Quick Fix Applied

I've updated the workflow to support **hybrid authentication** - it can use either trusted publishing OR API tokens as fallback:

### Current Configuration
- **Default**: Uses API tokens (immediate fix)
- **Future**: Can switch to trusted publishing when configured

### Repository Variable Control
The workflow checks `vars.USE_TRUSTED_PUBLISHING`:
- **Not set or `!= 'true'`**: Uses API token authentication
- **Set to `'true'`**: Uses trusted publishing

## Setup Instructions

### Step 1: Immediate Fix (API Tokens)

**For TestPyPI**:
1. Go to https://test.pypi.org/manage/account/token/
2. Create new API token with scope: "Entire account"
3. Add to GitHub Secrets as `TEST_PYPI_API_TOKEN`

**For PyPI.org**:
1. Go to https://pypi.org/manage/account/token/
2. Create new API token with scope: "Entire account" 
3. Add to GitHub Secrets as `PYPI_API_TOKEN`

### Step 2: Long-term Solution (Trusted Publishing)

**Configure PyPI Test Trusted Publisher**:
1. Go to https://test.pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the form:
   ```
   PyPI Project Name: pyforge-cli
   Owner: Py-Forge-Cli
   Repository name: PyForge-CLI
   Workflow filename: publish.yml
   Environment name: testpypi
   ```
4. Save the configuration

**Configure PyPI.org Trusted Publisher**:
1. Go to https://pypi.org/manage/account/publishing/
2. Follow same steps as TestPyPI
3. Use environment name: `pypi`

**Activate Trusted Publishing**:
1. Go to repository Settings → Variables and secrets → Actions
2. Create repository variable: `USE_TRUSTED_PUBLISHING` = `true`
3. This switches the workflow to use trusted publishing

## Debugging Information from Failed Run

The GitHub Actions provided these debugging claims:
```
* sub: repo:Py-Forge-Cli/PyForge-CLI:environment:testpypi
* repository: Py-Forge-Cli/PyForge-CLI
* repository_owner: Py-Forge-Cli
* workflow_ref: Py-Forge-Cli/PyForge-CLI/.github/workflows/publish.yml@refs/heads/main
* ref: refs/heads/main
```

**Use these exact values when configuring trusted publishing.**

## Workflow Changes Made

### Enhanced publish.yml
```yaml
# Hybrid approach - supports both authentication methods
- name: Publish distribution 📦 to TestPyPI (Trusted Publishing)
  if: vars.USE_TRUSTED_PUBLISHING == 'true'
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    repository-url: https://test.pypi.org/legacy/
    skip-existing: true

- name: Publish distribution 📦 to TestPyPI (API Token Fallback)
  if: vars.USE_TRUSTED_PUBLISHING != 'true'
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    repository-url: https://test.pypi.org/legacy/
    skip-existing: true
    user: __token__
    password: ${{ secrets.TEST_PYPI_API_TOKEN }}
```

## Testing the Fix

### 1. Test with API Tokens (Immediate)
```bash
# After adding API tokens to GitHub secrets
git push origin main  # Should deploy to TestPyPI
```

### 2. Test with Trusted Publishing (Future)
```bash
# After configuring trusted publishing and setting repository variable
git push origin main  # Should use trusted publishing
```

### 3. Verify Deployment
```bash
# Check TestPyPI
pip install -i https://test.pypi.org/simple/ pyforge-cli

# Check version
python -c "import pyforge_cli; print(pyforge_cli.__version__)"
```

## Expected Version Patterns

Based on current Git state:
- **Development**: `1.0.6.dev20+ged3c6d1.d20250629`
- **After this fix**: `1.0.6.dev21+g[NEW_COMMIT]`

## Security Benefits of Trusted Publishing

### Current (API Tokens)
- ❌ Long-lived secrets stored in repository
- ❌ Manual token rotation required
- ❌ Broader access scope

### Future (Trusted Publishing)
- ✅ No secrets stored in repository
- ✅ Automatic token generation and expiration
- ✅ Scoped access per repository and workflow

## Migration Path

1. **Phase 1**: Use API tokens (implemented) ✅
2. **Phase 2**: Configure trusted publishing in PyPI
3. **Phase 3**: Set `USE_TRUSTED_PUBLISHING=true`
4. **Phase 4**: Remove API tokens from secrets
5. **Phase 5**: Pure trusted publishing workflow

## Troubleshooting

### Common Issues

**"Invalid credentials" with API tokens**:
- Verify token has correct scope (entire account)
- Check token hasn't expired
- Ensure correct secret name in GitHub

**"Publisher not found" with trusted publishing**:
- Verify exact repository details match debugging claims
- Check environment name matches workflow
- Ensure workflow filename is correct

**"Skip existing" warnings**:
- Normal behavior when version already exists
- Check setuptools-scm is generating unique versions
- Consider if commit created new development version

## Next Steps

1. **Immediate**: Add API tokens to GitHub secrets
2. **Test**: Trigger deployment with test commit
3. **Plan**: Schedule trusted publishing configuration
4. **Monitor**: Verify deployment success and version generation

The hybrid approach ensures we have immediate functionality while maintaining the path to enhanced security with trusted publishing.