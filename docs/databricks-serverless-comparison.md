# Databricks Serverless Environment Comparison

## Overview
This document compares the Python library environments between Databricks Serverless V1 and V2, providing insights for dependency management and compatibility.

## Environment Specifications

| Aspect | V1 | V2 |
|--------|----|----|
| **Python Version** | 3.10.12 | 3.11.10 |
| **pip Version** | 22.3.1 | 24.2 |
| **setuptools** | 65.5.1 | 75.1.0 |
| **Primary Focus** | Core Data Science | AI/ML + Cloud Integration |

## Major Version Changes

### Critical Breaking Changes

#### PyArrow (Major Breaking Change)
- **V1**: `pyarrow==8.0.0`
- **V2**: `pyarrow==14.0.1`
- **Impact**: Major version jump with potential breaking changes in DataFrame serialization

#### Python Version
- **V1**: Python 3.10.12
- **V2**: Python 3.11.10
- **Impact**: Language features, performance improvements, but potential compatibility issues

### Core Data Science Libraries

| Library | V1 | V2 | Change |
|---------|----|----|--------|
| numpy | 1.23.5 | 1.23.5 | ✅ Same |
| pandas | 1.5.3 | 1.5.3 | ✅ Same |
| scipy | 1.10.0 | 1.11.1 | 🔄 Minor |
| matplotlib | 3.7.0 | 3.7.2 | 🔄 Patch |
| scikit-learn | 1.1.1 | 1.3.0 | 🔄 Minor |

### Cloud Libraries

#### AWS
| Library | V1 | V2 | Change |
|---------|----|----|--------|
| boto3 | 1.24.28 | 1.34.39 | 🔄 Major |
| botocore | 1.27.28 | 1.34.39 | 🔄 Major |

#### Azure (New in V2)
- `azure-core==1.31.0`
- `azure-storage-blob==12.19.1`
- `azure-storage-file-datalake==12.14.0`
- `azure-identity==1.15.0`
- `azure-keyvault-secrets==4.7.0`

#### Google Cloud (New in V2)
- `google-cloud-storage==2.18.2`
- `google-cloud-core==2.4.1`
- `google-auth==2.28.1`

### Machine Learning & AI

#### Traditional ML
| Library | V1 | V2 | Change |
|---------|----|----|--------|
| mlflow | 2.3.1 | 2.11.4 (skinny) | 🔄 Major |
| xgboost | 1.6.2 | 1.7.6 | 🔄 Minor |
| lightgbm | 3.3.2 | 4.1.0 | 🔄 Major |

#### Deep Learning (New in V2)
- `tensorflow==2.15.0`
- `torch==2.1.2`
- `torchvision==0.16.2`
- `torchaudio==2.1.2`

#### LLM & AI (New in V2)
- `transformers==4.36.2`
- `tokenizers==0.15.0`
- `accelerate==0.25.0`
- `openai==1.6.1`
- `anthropic==0.8.1`
- `langchain==0.1.0`
- `sentence-transformers==2.2.2`

### Development Tools

| Library | V1 | V2 | Change |
|---------|----|----|--------|
| black | 22.6.0 | 23.12.1 | 🔄 Major |
| ipython | 8.12.0 | 8.25.0 | 🔄 Minor |
| ipykernel | 6.25.0 | 6.28.0 | 🔄 Minor |

#### New Development Tools in V2
- `mypy==1.8.0` (type checking)
- `pylsp-mypy==0.6.8`

## Usage Examples

### Using V1 Constraints
```bash
# Install with V1 constraints (Python 3.10 required)
pip install -c constraints-databricks-serverless-v1.txt pandas pyarrow

# For PyForge CLI with V1 compatibility
pip install -c constraints-databricks-serverless-v1.txt pyforge-cli
```

### Using V2 Constraints
```bash
# Install with V2 constraints (Python 3.11 required)
pip install -c constraints-databricks-serverless-v2.txt pandas pyarrow

# For AI/ML workloads
pip install -c constraints-databricks-serverless-v2.txt transformers torch
```

## Migration Considerations

### Upgrading from V1 to V2

#### ✅ Safe Migrations
- Core data science libraries (numpy, pandas) remain the same
- Basic file I/O operations should work unchanged
- Most data processing workflows will be compatible

#### ⚠️ Requires Testing
- **PyArrow operations**: Test DataFrame serialization/deserialization
- **Cloud integrations**: Updated boto3 may have API changes
- **ML pipelines**: MLflow and XGBoost version changes
- **Custom code**: Python 3.11 language changes

#### 🚨 Breaking Changes
- **PyArrow 8.0.0 → 14.0.1**: Schema evolution, metadata handling
- **Python 3.10 → 3.11**: Language syntax, removed modules
- **MLflow**: Potential API changes from 2.3.1 → 2.11.4

### PyForge CLI Compatibility

#### Current Status (V1 Compatible)
```toml
# pyproject.toml constraints for V1
requires-python = ">=3.8,<3.11"
dependencies = [
    "pandas==1.5.3",
    "pyarrow==8.0.0",
    "numpy==1.23.5",
    # ... other V1 compatible versions
]
```

#### V2 Migration Strategy
1. **Create separate V2 branch** for testing
2. **Update Python requirement** to `>=3.11`
3. **Test PyArrow compatibility** thoroughly
4. **Update CI/CD** to test both environments
5. **Gradual rollout** with feature flags

## Recommendations

### For New Projects
- **Use V2** if you need AI/ML capabilities or cloud integrations
- **Use V1** for stable data processing workloads

### For Existing Projects
- **Stay on V1** unless you need V2-specific features
- **Plan migration carefully** with comprehensive testing
- **Consider dual compatibility** during transition period

### For PyForge CLI
1. **Maintain V1 compatibility** in main branch
2. **Create V2 experimental branch** for testing
3. **Use constraints files** for environment-specific builds
4. **Update CI/CD** to test both environments

## Environment-Specific Installation

### V1 Environment Setup
```bash
# Create V1 compatible environment
python3.10 -m venv venv-v1
source venv-v1/bin/activate
pip install -c constraints-databricks-serverless-v1.txt -r requirements.txt
```

### V2 Environment Setup
```bash
# Create V2 compatible environment
python3.11 -m venv venv-v2
source venv-v2/bin/activate
pip install -c constraints-databricks-serverless-v2.txt -r requirements.txt
```

## Testing Matrix

### Recommended Test Strategy
```yaml
strategy:
  matrix:
    databricks-env: [v1, v2]
    python-version: ["3.10.12", "3.11.10"]
    exclude:
      - databricks-env: v1
        python-version: "3.11.10"
      - databricks-env: v2
        python-version: "3.10.12"
```

## Conclusion

V2 represents a significant expansion of capabilities, particularly in AI/ML and cloud integration. However, the PyArrow version jump and Python version change require careful migration planning. For stable data processing workloads, V1 remains a solid choice, while V2 opens up modern AI/ML capabilities.

The provided constraints files enable precise dependency management for both environments, ensuring compatibility and reproducible builds.