# CI/CD Test and Coverage Reporting Setup Guide

## Overview

This guide explains how to set up comprehensive test and code coverage reporting in GitHub Actions for the PyForge CLI project.

## Current Issues

1. **TestPyPI Publishing**: The publish step is failing (exit code 1) - likely due to authentication or version conflicts
2. **Test Reports**: The test-report.yml expects JUnit XML files but pytest isn't generating them
3. **Coverage Comments**: No automatic PR comments showing coverage changes

## Standard Practices for Test & Coverage Reports

### 1. Generate JUnit XML Reports

Update your pytest commands to generate JUnit XML:

```yaml
# In .github/workflows/ci-develop.yml and other workflows
- name: Run comprehensive test suite
  run: |
    pytest tests/ \
      --run-pyspark \
      --cov=pyforge_cli \
      --cov-report=term-missing \
      --cov-report=xml \
      --cov-report=html \
      --html=pytest_html_report.html \
      --self-contained-html \
      --junitxml=junit/test-results.xml \
      -v
```

### 2. Configure Coverage Settings

Add to `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
relative_files = true  # Critical for GitHub Actions
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### 3. Add PR Coverage Comments

Create `.github/workflows/coverage-comment.yml`:

```yaml
name: Coverage Comment

on:
  workflow_run:
    workflows: ["CI Develop Branch (Features)"]
    types:
      - completed

permissions:
  pull-requests: write
  contents: read
  actions: read

jobs:
  comment:
    if: github.event.workflow_run.event == 'pull_request' && github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    steps:
      - name: Download Coverage Report
        uses: actions/download-artifact@v4
        with:
          name: coverage-report
          run-id: ${{ github.event.workflow_run.id }}
          
      - name: Coverage Comment
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          MINIMUM_GREEN: 85
          MINIMUM_ORANGE: 70
          ANNOTATE_MISSING_LINES: true
          ANNOTATION_TYPE: warning
```

### 4. Enhanced Test Reporting

Update `.github/workflows/ci-develop.yml` to upload test artifacts properly:

```yaml
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results-${{ matrix.os }}
    path: |
      junit/
      pytest_html_report.html
      htmlcov/
      coverage.xml
```

### 5. Add Test Summary to PR

Create `.github/workflows/test-summary.yml`:

```yaml
name: Test Summary

on:
  workflow_run:
    workflows: ["CI Develop Branch (Features)"]
    types:
      - completed

permissions:
  checks: write
  pull-requests: write
  contents: read

jobs:
  test-summary:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.event == 'pull_request'
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          run-id: ${{ github.event.workflow_run.id }}
          path: artifacts
          
      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        with:
          check_name: 'Test Results'
          junit_files: 'artifacts/*/junit/*.xml'
          compare_to_earlier_commit: true
          
      - name: Find PR
        uses: actions/github-script@v7
        id: find-pr
        with:
          script: |
            const prs = await github.rest.pulls.list({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              head: `${context.repo.owner}:${context.payload.workflow_run.head_branch}`
            });
            return prs.data[0]?.number || null;
            
      - name: Comment Test Summary
        if: steps.find-pr.outputs.result
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const coverage = fs.readFileSync('artifacts/coverage.xml', 'utf8');
            // Parse and create summary...
            
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: ${{ steps.find-pr.outputs.result }},
              body: summaryText
            });
```

## Fix TestPyPI Publishing

The most common issues are:

1. **Version Already Exists**: Add to workflow:
```yaml
- name: Check if version exists
  run: |
    VERSION=$(python -c "import setuptools_scm; print(setuptools_scm.get_version())")
    if pip index versions -i https://test.pypi.org/simple/ pyforge-cli | grep -q $VERSION; then
      echo "Version $VERSION already exists on TestPyPI"
      echo "skip_publish=true" >> $GITHUB_ENV
    fi
    
- name: Publish to TestPyPI
  if: env.skip_publish != 'true'
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    repository-url: https://test.pypi.org/legacy/
```

2. **Authentication Issues**: The workflow uses OIDC (trusted publishing). Ensure:
   - You've configured trusted publishing on TestPyPI
   - The workflow has `id-token: write` permission
   - Project name matches exactly

## Best Practices

1. **Use Workflow Artifacts**: Store test results and coverage reports as artifacts
2. **PR Comments**: Update the same comment instead of creating new ones
3. **Status Checks**: Make test/coverage checks required for PR merging
4. **Badges**: Add coverage badges to README
5. **Thresholds**: Set minimum coverage requirements

## Example PR Comment Output

```
## Coverage Report 📊

Overall Coverage: **85.4%** (+2.1%) ✅

| File | Coverage | Change |
|------|----------|--------|
| main.py | 92.3% | +5.2% |
| converters/csv_converter.py | 88.1% | +1.5% |
| converters/pdf_converter.py | 78.9% | -0.3% |

<details>
<summary>Detailed Report</summary>

### New Uncovered Lines
- `main.py:142-145` - Error handling in convert function
- `converters/csv_converter.py:88` - Edge case for empty files

</details>

[View Full Report](link-to-htmlcov)
```

## Implementation Steps

1. **Fix JUnit generation**: Add `--junitxml` to pytest commands
2. **Update pyproject.toml**: Add coverage configuration
3. **Create coverage comment workflow**: For automatic PR comments
4. **Fix test-report.yml**: Ensure it finds the JUnit files
5. **Debug TestPyPI**: Add version checking and better error handling

## Resources

- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [GitHub Actions test reporting](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge)
- [Codecov documentation](https://docs.codecov.com/docs)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)