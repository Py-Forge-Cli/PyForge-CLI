# PyForge Documentation

This directory contains comprehensive documentation for PyForge packages, including Databricks integration guides and notebook examples.

## 📁 Structure

```
docs/
├── notebooks/                    # Interactive notebook guides
│   ├── pyforge-core-databricks-guide.md         # PyForge Core in Databricks
│   └── pyforge-databricks-volume-guide.md       # PyForge Databricks with Volumes
└── README.md                     # This file
```

## 📓 Notebook Guides

### 1. PyForge Core Databricks Guide
**File**: `notebooks/pyforge-core-databricks-guide.md`

A comprehensive walkthrough of using PyForge CLI in Databricks environments:

- **Target Audience**: Data specialists new to PyForge
- **Prerequisites**: Basic Databricks knowledge
- **Content**:
  - Installation and setup using `pip install pyforge-cli`
  - Sample dataset installation using CLI commands
  - Basic file conversions (CSV, JSON, XML, Excel, PDF) using %sh magic
  - Multi-table database detection and extraction
  - Batch processing with shell scripts
  - Performance optimization
  - Best practices

**Key Features Demonstrated**:
- CLI-only approach with %sh magic commands
- Automatic multi-table database detection
- Format-specific conversions
- File validation using CLI
- Error handling and logging

### 2. PyForge Databricks Volume Guide  
**File**: `notebooks/pyforge-databricks-volume-guide.md`

Guide for using PyForge CLI with Unity Catalog Volume integration:

- **Target Audience**: Data engineers working with Unity Catalog
- **Prerequisites**: Unity Catalog access, Volume permissions
- **Content**:
  - PyForge CLI installation (`pip install pyforge-cli`)
  - Unity Catalog Volume operations using CLI
  - Direct Volume-to-Volume file conversions using shell commands
  - Volume-to-Volume conversions
  - Delta Lake integration
  - Advanced batch processing
  - Production patterns

**Key Features Demonstrated**:
- Direct Volume file operations
- Serverless environment detection
- Distributed processing strategies
- Delta Lake format support
- Performance monitoring

## 🚀 Getting Started

### For Data Specialists (PyForge Core)

1. **Start Here**: [PyForge Core Databricks Guide](notebooks/pyforge-core-databricks-guide.md)
2. **Installation**: `%pip install pyforge-core`
3. **First Steps**: Follow the notebook to install sample datasets and try basic conversions
4. **Use Cases**: File format conversions, data preparation, reporting

### For Data Engineers (PyForge Databricks)

1. **Start Here**: [PyForge Databricks Volume Guide](notebooks/pyforge-databricks-volume-guide.md)  
2. **Installation**: `%pip install pyforge-core pyforge-databricks`
3. **Prerequisites**: Configure Unity Catalog Volumes
4. **Use Cases**: Production pipelines, automated workflows, large-scale processing

## 📖 How to Use These Notebooks

### Option 1: Import to Databricks
1. Copy the markdown content from the guide you want to use
2. Create a new notebook in Databricks
3. Paste the content and run the cells sequentially
4. Customize paths and parameters for your environment

### Option 2: View as HTML (GitHub Pages)
The notebooks are formatted in Databricks-compatible markdown and can be viewed as HTML documentation:

- View rendered notebooks at: `https://yourusername.github.io/pyforge-cli/docs/notebooks/`
- Each guide includes complete code examples and explanations
- Copy-paste code blocks directly into your Databricks notebooks

## 🔧 Customization

### Environment Variables
Update these variables in the notebooks to match your setup:

```python
# For Volume operations
CATALOG = "your_catalog"      # Your Unity Catalog name
SCHEMA = "your_schema"        # Your schema name  
BRONZE_VOLUME = "bronze"      # Raw data volume
SILVER_VOLUME = "silver"      # Processed data volume
GOLD_VOLUME = "gold"          # Curated data volume
```

### File Paths
The guides use these path patterns:
- `/Volumes/catalog/schema/volume/file.ext` - Unity Catalog Volumes
- `/tmp/pyforge_samples/` - Local temporary files for testing
- `dbfs:/FileStore/shared_uploads/` - DBFS paths

## 🎯 Key API Changes

The updated API uses a unified `forge.convert()` method that automatically:
- Detects Volume vs local paths
- Selects optimal processing engine
- Handles format-specific options
- Provides consistent interface

**Before**:
```python
forge.convert_from_volume(input_path, output_path, options)
```

**After**:
```python
forge.convert(input_path, output_path, **options)
```

## 📊 Supported Formats

| Format | Extensions | Processing Engine | Notes |
|--------|------------|-------------------|-------|
| CSV | `.csv`, `.tsv` | Databricks Native | Distributed processing |
| JSON | `.json` | Databricks Native | Nested structure flattening |
| XML | `.xml` | Databricks Native | Hierarchical flattening |
| Excel | `.xlsx` | Hybrid | PyForge analysis + Spark output |
| PDF | `.pdf` | PyForge | Text extraction |
| Access | `.mdb`, `.accdb` | PyForge | Database conversion |
| DBF | `.dbf` | PyForge | Legacy format support |
| Parquet | `.parquet` | Databricks Native | Optimal for analytics |
| Delta | Delta tables | Databricks Native | Versioning and ACID |

## 🔗 Related Resources

- [PyForge Core Repository](https://github.com/PyForge/pyforge-core)
- [PyForge Databricks Repository](https://github.com/PyForge/pyforge-databricks)  
- [Unity Catalog Volumes Documentation](https://docs.databricks.com/data-governance/unity-catalog/volumes.html)
- [Databricks SDK Documentation](https://databricks-sdk-py.readthedocs.io/)

## 🤝 Contributing

To contribute to these documentation guides:

1. **Feedback**: Open issues for improvements or corrections
2. **Examples**: Submit additional use cases and examples
3. **Updates**: Keep documentation current with package releases
4. **Testing**: Verify notebooks work in different Databricks environments

## 📝 License

These documentation files are provided under the same license as the PyForge packages (MIT License).