# API Documentation

Learn how to use PyForge CLI as a Python library and extend it with custom plugins.

## Available APIs

<div class="grid cards" markdown>

-   :material-language-python: **Python API**

    ---

    Use PyForge CLI programmatically in your Python applications

    [:octicons-arrow-right-24: Python API](python-api.md)

-   :material-puzzle: **Plugin Development**

    ---

    Create custom converters and extend PyForge CLI

    [:octicons-arrow-right-24: Plugin Development](plugin-development.md)

</div>

## Quick Start

### Using as a Python Library

```python
from pyforge_cli.main import cli
from pyforge_cli.converters import PDFConverter, ExcelConverter

# Convert PDF to text
converter = PDFConverter()
result = converter.convert("document.pdf", "output.txt")

# Convert Excel to Parquet
excel_converter = ExcelConverter()
result = excel_converter.convert("data.xlsx", "output.parquet")
```

### Creating a Custom Plugin

```python
from pyforge_cli.converters.base import BaseConverter

class CustomConverter(BaseConverter):
    supported_formats = ['.custom']
    output_format = '.processed'
    
    def convert(self, input_path, output_path, **options):
        # Your conversion logic here
        pass
```

## API Features

- **Type Safety**: Full type hints for better development experience
- **Error Handling**: Comprehensive exception hierarchy
- **Progress Tracking**: Built-in progress reporting
- **Configuration**: Flexible configuration system
- **Extensibility**: Plugin architecture for custom formats

## Next Steps

- **[Python API](python-api.md)** - Detailed library documentation
- **[Plugin Development](plugin-development.md)** - Create custom converters