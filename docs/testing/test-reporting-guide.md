# Test Reporting Infrastructure Guide

## Overview

PyForge CLI uses a comprehensive test reporting system in GitHub Actions that provides:
- Detailed test results with pass/fail status
- Code coverage reports
- HTML test reports for debugging
- Test summaries in PR checks
- Historical test tracking

## Features

### 1. Multiple Report Formats

The CI workflow generates multiple test report formats:

- **JUnit XML**: For GitHub Actions integration
- **HTML Reports**: Self-contained HTML reports for viewing test details
- **JSON Reports**: Machine-readable test results
- **Coverage Reports**: XML and HTML coverage reports
- **GitHub Job Summaries**: Markdown summaries in workflow runs

### 2. Test Reporting Actions

#### Primary Test Reporting
- **mikepenz/action-junit-report@v4**: Publishes test results as PR checks
  - Shows detailed test results with annotations
  - Includes both passed and failed tests
  - Creates separate checks for each OS/Python version combination

#### Cross-Workflow Reporting
- **EnricoMi/publish-unit-test-result-action@v2**: Aggregates results across workflow runs
- **test-summary/action@v2**: Creates comprehensive test summaries

### 3. Artifacts

All test artifacts are uploaded and retained for 30 days:
- JUnit XML files
- HTML test reports
- JSON test reports
- HTML coverage reports
- XML coverage data

## Viewing Test Results

### 1. PR Checks
- Each PR shows test results as GitHub checks
- Click on "Details" to see individual test results
- Failed tests show with file annotations

### 2. Job Summaries
- Go to Actions → Select workflow run
- View "Summary" tab for test statistics
- Includes total tests, passed, failed, skipped counts

### 3. Artifacts
- Download HTML reports from workflow artifacts
- Open `pytest_html_report.html` for detailed test results
- View `htmlcov/index.html` for coverage details

### 4. Codecov Integration
- Coverage reports are sent to Codecov
- View coverage trends and PR coverage changes

## Configuration Details

### pytest Configuration

```bash
pytest tests/ \
  --cov=pyforge_cli \
  --cov-report=xml \
  --cov-report=html:htmlcov \
  --junit-xml=junit/test-results-${{ matrix.os }}-${{ matrix.python-version }}.xml \
  --html=pytest_html_report.html \
  --self-contained-html \
  --json-report \
  --json-report-file=test-report.json \
  -v
```

### Required Dependencies

```bash
pip install pytest-html pytest-json-report
```

## Best Practices

### 1. Always Run Reporting Steps
Use `if: success() || failure()` or `if: always()` to ensure reports are generated even when tests fail.

### 2. Unique Artifact Names
Include OS and Python version in artifact names to avoid conflicts:
```yaml
name: test-results-${{ matrix.os }}-${{ matrix.python-version }}
```

### 3. Memory Management
For large test suites, increase Node.js memory:
```yaml
env:
  NODE_OPTIONS: "--max_old_space_size=4096"
```

### 4. Security Considerations
- Test report workflow has limited permissions
- Only reads artifacts from trusted workflow runs
- Uses `permissions` to limit access scope

## Troubleshooting

### Missing Test Reports
1. Check if pytest generated the report files
2. Verify artifact upload paths match generated files
3. Ensure `if: always()` is used for upload steps

### Out of Memory Errors
1. Add NODE_OPTIONS environment variable
2. Consider splitting tests into smaller groups
3. Use pytest-xdist for parallel execution

### Permissions Errors
1. Ensure workflow has `checks: write` permission
2. For cross-repo PRs, use the separate test-report workflow
3. Check GitHub token permissions

## Adding New Report Types

To add a new test reporting format:

1. Install the pytest plugin:
   ```yaml
   pip install pytest-[plugin-name]
   ```

2. Add pytest arguments:
   ```yaml
   pytest --[plugin-args]
   ```

3. Upload artifacts:
   ```yaml
   - name: Upload [Report Type]
     uses: actions/upload-artifact@v4
     if: always()
     with:
       name: [report-name]-${{ matrix.os }}-${{ matrix.python-version }}
       path: [report-path]
   ```

## Extending Test Reporting

### Custom Test Summaries
Add Python scripts to parse test results and create custom summaries:

```python
import json
with open('test-report.json', 'r') as f:
    data = json.load(f)
    # Process and format test data
```

### Integration with External Services
- Send test results to external dashboards
- Integrate with test management tools
- Create custom notifications

## Security Considerations

- Test reports may contain sensitive information
- Artifacts are public in public repositories
- Use artifact retention policies appropriately
- Consider encrypting sensitive test data