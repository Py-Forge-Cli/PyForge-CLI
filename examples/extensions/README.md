# PyForge CLI Extension Examples

This directory contains example extensions and templates for developing PyForge CLI extensions.

## Files Overview

### Templates
- **`extension_template.py`** - Complete template for creating new extensions
- **`pyproject.toml.template`** - Template for package configuration

### Examples
- **`example_extension.py`** - Comprehensive example showing all extension features
- **`simple_extension.py`** - Minimal extension example
- **`databricks_extension_example.py`** - Example Databricks integration

### Project Templates
- **`extension_project_template/`** - Complete project structure template

## Quick Start

### 1. Copy the Template
```bash
cp extension_template.py my_extension.py
```

### 2. Customize the Extension
1. Replace `TemplateExtension` with your extension class name
2. Update metadata (name, version, description)
3. Implement required methods
4. Add your custom functionality

### 3. Create Package Structure
```
my-extension/
├── pyproject.toml
├── README.md
├── src/
│   └── my_extension/
│       ├── __init__.py
│       └── extension.py
├── tests/
│   └── test_extension.py
└── examples/
    └── usage.py
```

### 4. Configure Entry Points
Add to your `pyproject.toml`:
```toml
[project.entry-points."pyforge.extensions"]
my_extension = "my_extension.extension:MyExtension"
```

### 5. Test Your Extension
```bash
pip install -e .
pyforge --list-extensions
```

## Extension Categories

### Infrastructure Extensions
- Cloud provider integrations (AWS, Azure, GCP)
- Container platform integrations (Docker, Kubernetes)
- CI/CD pipeline integrations

### Environment Extensions
- Databricks integration
- Jupyter notebook integration
- Apache Spark optimization

### Format Extensions
- New input format support
- Custom output format handlers
- Format validation and metadata

### Workflow Extensions
- Pre/post-processing pipelines
- Data quality validation
- Notification systems

## Best Practices

1. **Follow the Template**: Use the provided template as starting point
2. **Error Handling**: Always handle errors gracefully
3. **Logging**: Use structured logging for debugging
4. **Testing**: Write comprehensive tests
5. **Documentation**: Provide clear documentation and examples
6. **Dependencies**: Minimize required dependencies
7. **Performance**: Consider performance impact of hooks
8. **Compatibility**: Support multiple Python versions

## Resources

- [Extension Developer Guide](../../docs/api/extension-developer-guide.md)
- [PyForge CLI Documentation](../../docs/)
- [Testing Guidelines](../../docs/testing/)

## Contributing

Submit your extension examples via pull request to help other developers!