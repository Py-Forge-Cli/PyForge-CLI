# Developer Notes

This directory contains internal development documentation, testing guides, and reference materials.

## Contents

- **SPARK_CONNECT_SETUP.md** - Guide for setting up Spark Connect for testing
- **requirements-integration.txt** - Dependencies for integration testing
- **requirements-serverless-test.txt** - Dependencies for serverless testing

## PyForge CLI Deployment

The main deployment script is now located at:
- **scripts/deploy_pyforge_to_databricks.py** - Deploys PyForge CLI wheel and notebooks to Databricks

### Usage
```bash
# Deploy from project root
python scripts/deploy_pyforge_to_databricks.py

# With options
python scripts/deploy_pyforge_to_databricks.py -u username -p profile -v
```

## Testing Organization

Test notebooks are organized in:
- **notebooks/testing/unit/** - Unit tests
- **notebooks/testing/integration/** - Integration tests  
- **notebooks/testing/functional/** - Functional tests
- **notebooks/testing/exploratory/** - Exploratory tests

The deployment script automatically uploads all organized notebooks to Databricks workspace.