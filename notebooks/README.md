# Notebooks Directory

This directory contains Jupyter notebooks organized by purpose and testing type.

## Structure

```
notebooks/
├── testing/
│   ├── unit/                    # Test individual functions/modules
│   │   └── 01-csv-testing-notebook.py
│   ├── integration/             # Test component interactions
│   │   ├── 01-pyforge-integration-testing.py
│   │   ├── 02-pyforge-v1-testing.py
│   │   └── 03-enhanced-pyforge-testing.py
│   ├── functional/              # Test complete user workflows
│   │   └── 01-test-cli-end-to-end.ipynb
│   └── exploratory/            # Performance analysis and debugging
├── documentation/               # Tutorial and example notebooks
└── reports/                    # Generated test reports
```

## Naming Convention

Notebooks follow the pattern: `[sequence]-[test-type]-[component]-[description].ipynb`

Examples:
- `01-unit-cli-argument-parsing.ipynb`
- `02-integration-cli-workflow-end-to-end.ipynb`
- `03-functional-user-scenario-project-creation.ipynb`

## Usage

- **Unit Testing**: Focus on individual functions and modules
- **Integration Testing**: Test how components work together
- **Functional Testing**: End-to-end user scenarios and workflows
- **Exploratory**: Performance analysis, debugging, and investigation

## Deployment

All notebooks in this directory are automatically deployed to Databricks using:

```bash
python scripts/deploy_pyforge_to_databricks.py
```

This will:
1. Upload all `.py` and `.ipynb` files to Databricks workspace
2. Preserve the directory structure (unit/, integration/, functional/, exploratory/)
3. Set appropriate formats (JUPYTER for .ipynb, SOURCE for .py files)

## Best Practices

1. Use sequential numbering for execution order
2. Include setup/teardown cells
3. Use markdown cells for documentation
4. Keep notebooks focused on specific scenarios
5. Use ASCII-only text to avoid encoding issues
6. Clean outputs before committing to version control