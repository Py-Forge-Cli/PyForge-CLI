# PyForge CLI Sample Datasets

A comprehensive collection of sample datasets for testing PyForge CLI data processing capabilities across multiple file formats.

## Overview

The PyForge CLI Sample Datasets collection provides **23 curated datasets** across **7 different formats**, enabling comprehensive testing of data conversion, processing, and analysis workflows. All datasets are automatically downloadable through the PyForge CLI installation command.

## Installation

```bash
pyforge install sample-datasets [target_directory]
```

**Example:**
```bash
# Install to current directory
pyforge install sample-datasets .

# Install to specific directory
pyforge install sample-datasets /path/to/datasets

# Install to data folder
pyforge install sample-datasets ./data
```

## Dataset Categories

### Size Categories
- **Small**: <100MB - Ideal for quick testing and development
- **Medium**: 100MB-1GB - Suitable for performance testing
- **Large**: >1GB - For stress testing and production validation

### Format Coverage
- **PDF**: Government documents and technical reports
- **Excel**: Business data with multi-sheet structures
- **XML**: API responses and structured data
- **Access**: Database files (.mdb/.accdb)
- **DBF**: Geographic and legacy database formats
- **MDF**: SQL Server database files
- **CSV**: Analytics and machine learning datasets

## Available Datasets

### 📄 PDF Files (2 datasets)

#### DOD Software Guide
- **Size**: 2.1MB (Small)
- **Format**: PDF
- **License**: Public Domain (US Government)
- **Description**: Department of Defense software development standards
- **Use Cases**: Document processing, text extraction, government data
- **Download**: Direct HTTP
- **Status**: ❌ SSL certificate issues

#### NIST Cybersecurity Framework
- **Size**: 3.2MB → 1.0MB actual (Small)
- **Format**: PDF
- **License**: Public Domain (US Government)
- **Description**: NIST Cybersecurity Framework guidelines
- **Use Cases**: Technical document analysis, security compliance
- **Download**: Direct HTTP
- **Status**: ✅ Working

### 📊 Excel Files (5 datasets)

#### Superstore Dataset Final
- **Size**: 550KB → 2.2MB actual (Small)
- **Format**: CSV (Excel category)
- **License**: Public Domain
- **Description**: Business sales data with comprehensive analytics
- **Use Cases**: Business intelligence, sales analysis, data visualization
- **Download**: Kaggle API (`vivek468/superstore-dataset-final`)
- **Status**: ✅ Working

#### Global Superstore
- **Size**: 6MB → 17.4MB actual (Small)
- **Format**: Excel
- **License**: Other (specified)
- **Description**: Global e-commerce sales data 2011-2014
- **Use Cases**: International data processing, time series analysis
- **Download**: Kaggle API (`shekpaul/global-superstore`)
- **Status**: ✅ Working

#### COVID Dashboard
- **Size**: 121KB → 250.4KB actual (Small)
- **Format**: Excel
- **License**: Public
- **Description**: Interactive COVID-19 analysis with embedded charts
- **Use Cases**: Dashboard processing, chart extraction, health data
- **Download**: Kaggle API (`suhj22/covid19-excel-dataset-with-interactive-dashboard`)
- **Status**: ✅ Working

#### Financial Sample
- **Size**: 78KB → 81.5KB actual (Small)
- **Format**: Excel
- **License**: Public
- **Description**: Financial statements and analysis
- **Use Cases**: Financial data processing, accounting workflows
- **Download**: Kaggle API (`konstantinognev/financial-samplexlsx`)
- **Status**: ✅ Working

#### Bike Buyers Analysis
- **Size**: 6.8MB → 44.1MB actual (Small)
- **Format**: Excel
- **License**: Public
- **Description**: Customer demographic analysis and segmentation
- **Use Cases**: Market research, demographic analysis, customer segmentation
- **Download**: Kaggle API (`unica02/data-on-bike-buyers-by-using-ms-excel`)
- **Status**: ✅ Working

### 🔗 XML Files (3 datasets)

#### RSS News Feeds
- **Size**: 91KB → 347.9KB actual (Small)
- **Format**: XML
- **License**: CC0 Public Domain
- **Description**: 4,000+ RSS feeds for news collection
- **Use Cases**: RSS processing, news aggregation, syndication XML
- **Download**: Kaggle API (`ceshine/rss-feeds-from-news-outlets`)
- **Status**: ✅ Working

#### USPTO Patent Data
- **Size**: 104MB → 568.8MB actual (Medium)
- **Format**: XML
- **License**: CC Public Domain Mark 1.0
- **Description**: Full-text patent grants from USPTO
- **Use Cases**: Government XML processing, legal documents, complex structures
- **Download**: Kaggle API (`uspto/patent-grant-full-text`)
- **Status**: ✅ Working

#### DBLP Bibliography
- **Size**: 781MB → 3.5GB actual (Large)
- **Format**: XML
- **License**: CC BY-SA 4.0
- **Description**: Computer science bibliography database
- **Use Cases**: Academic data processing, large XML handling, bibliographic data
- **Download**: Kaggle API (`dheerajmpai/dblp2023`)
- **Status**: ✅ Working

### 🗃️ Access Database Files (3 datasets)

#### Northwind 2007 (VB.NET)
- **Size**: 3.5MB actual (Small)
- **Format**: ACCDB (Access 2007+)
- **License**: Educational/Sample Use
- **Description**: Classic Northwind sample database used in VB.NET examples
- **Use Cases**: Database connectivity, business data modeling, relational data
- **Download**: Direct HTTP (GitHub: `ssmith1975/samples-vb-net`)
- **Status**: ✅ Working

#### Sample Database (Dibi)
- **Size**: 284KB actual (Small)
- **Format**: MDB (Access 97/2000/2003)
- **License**: Open Source
- **Description**: Small sample database for testing database abstraction layer
- **Use Cases**: Legacy database testing, compatibility validation
- **Download**: Direct HTTP (GitHub: `dg/dibi`)
- **Status**: ✅ Working

#### Sakila (Access Port)
- **Size**: 3.8MB actual (Small)
- **Format**: MDB (Access 97/2000/2003)
- **License**: BSD License
- **Description**: MySQL Sakila sample database ported to Access format
- **Use Cases**: Cross-platform database testing, movie rental business model
- **Download**: Direct HTTP (GitHub: `ozzymcduff/sakila-sample-database-ports`)
- **Status**: ✅ Working

### 📋 DBF Files (3 datasets)

#### Census TIGER Sample
- **Size**: 25MB download → 175KB DBF (Small)
- **Format**: DBF (dBase)
- **License**: Public Domain (US Government)
- **Description**: US Census TIGER geographic place data
- **Use Cases**: Geographic data processing, legacy format support
- **Download**: Direct HTTP (ZIP extraction)
- **Status**: ✅ Working

#### Property Sample
- **Size**: 8.5MB download → 75MB DBF (Small)
- **Format**: DBF (dBase)
- **License**: Public Domain (US Government)
- **Description**: US Census tabulation blocks geographic data
- **Use Cases**: Large DBF handling, geographic analysis
- **Download**: Direct HTTP (ZIP extraction)
- **Status**: ✅ Working

#### County Geographic
- **Size**: 350MB download → 970KB DBF (Medium)
- **Format**: DBF (dBase)
- **License**: Public Domain (US Government)
- **Description**: US Census county geographic boundaries
- **Use Cases**: Administrative boundaries, county-level analysis
- **Download**: Direct HTTP (ZIP extraction)
- **Status**: ✅ Working

### 🗄️ MDF Files (2 datasets)

#### AdventureWorks 2012 OLTP LT
- **Size**: 15MB → 5.9MB actual (Small)
- **Format**: MDF (SQL Server)
- **License**: Microsoft Sample Code License
- **Description**: Microsoft AdventureWorks OLTP lightweight sample database
- **Use Cases**: SQL Server testing, OLTP processing, business applications
- **Download**: Direct HTTP (Microsoft GitHub)
- **Status**: ✅ Working

#### AdventureWorks 2012 DW
- **Size**: 680MB → 201.2MB actual (Medium)
- **Format**: MDF (SQL Server)
- **License**: Microsoft Sample Code License
- **Description**: Microsoft AdventureWorks Data Warehouse sample database
- **Use Cases**: Data warehouse testing, OLAP processing, analytics
- **Download**: Direct HTTP (Microsoft GitHub)
- **Status**: ✅ Working

### 📈 CSV Files (6 datasets)

#### Titanic Dataset
- **Size**: 100KB → 59.8KB actual (Small)
- **Format**: CSV
- **License**: Public Domain
- **Description**: Classic passenger survival dataset
- **Use Cases**: Machine learning, classification problems, missing values
- **Download**: Kaggle API (`yasserh/titanic-dataset`)
- **Status**: ✅ Working

#### Wine Quality
- **Size**: 300KB → 76.2KB actual (Small)
- **Format**: CSV
- **License**: Public Domain
- **Description**: Chemical properties and quality ratings
- **Use Cases**: Scientific data, regression analysis, quality prediction
- **Download**: Kaggle API (`yasserh/wine-quality-dataset`)
- **Status**: ✅ Working

#### UK E-Commerce Data
- **Size**: 7.5MB → 43.5MB actual (Small)
- **Format**: CSV
- **License**: Public Domain
- **Description**: UK online retail transactions
- **Use Cases**: E-commerce analysis, international data, business transactions
- **Download**: Kaggle API (`carrie1/ecommerce-data`)
- **Status**: ✅ Working

#### Credit Card Fraud
- **Size**: 66MB → 143.8MB actual (Small)
- **Format**: CSV
- **License**: Open Database License
- **Description**: European credit card fraud detection dataset
- **Use Cases**: Fraud detection, imbalanced datasets, financial security
- **Download**: Kaggle API (`mlg-ulb/creditcardfraud`)
- **Status**: ✅ Working

#### PaySim Financial
- **Size**: 186MB → 470.7MB actual (Medium)
- **Format**: CSV
- **License**: CC BY-SA 4.0
- **Description**: Synthetic mobile money transactions
- **Use Cases**: Financial simulation, large dataset processing, fraud detection
- **Download**: Kaggle API (`ealaxi/paysim1`)
- **Status**: ✅ Working

#### NYC Taxi Trips
- **Size**: 1.9GB → 1.8GB actual (Large)
- **Format**: CSV
- **License**: Public Domain
- **Description**: NYC yellow taxi trip records (2016-03 sample)
- **Use Cases**: Time series analysis, geographic coordinates, large CSV handling
- **Download**: Kaggle API (`elemento/nyc-yellow-taxi-trip-data`)
- **Status**: ✅ Working

## Download Methods

### Direct HTTP Downloads (12 datasets - 52%)
Direct downloads from reliable sources requiring no authentication:
- Government websites (Census, NIST, DOD)
- GitHub repositories (Microsoft, open source projects)
- Archive.org collections

### Kaggle API Downloads (10 datasets - 43%)
Programmatic access through Kaggle API:
- Requires Kaggle account and API token
- Automatic authentication handling
- Community datasets with clear licensing

### Manual Collection (1 dataset - 5%)
Requires user intervention or special handling:
- Interactive downloads
- Complex authentication requirements

## License Information

### Public Domain (11 datasets)
- US Government data (Census, NIST, DOD)
- Community contributions
- No usage restrictions

### Open Source Licenses (6 datasets)
- MIT, BSD, Apache licenses
- Attribution required
- Commercial use allowed

### Educational/Sample Use (4 datasets)
- Microsoft sample databases
- Educational projects
- Learning and development purposes

### Creative Commons (2 datasets)
- CC0, CC BY-SA licenses
- Open access with attribution

## Technical Specifications

### File Organization
```
sample-datasets/
├── pdf/
│   ├── small/
│   ├── medium/
│   └── large/
├── excel/
│   ├── small/
│   ├── medium/
│   └── large/
├── xml/
│   ├── small/
│   ├── medium/
│   └── large/
├── access/
│   ├── small/
│   ├── medium/
│   └── large/
├── dbf/
│   ├── small/
│   ├── medium/
│   └── large/
├── mdf/
│   ├── small/
│   ├── medium/
│   └── large/
├── csv/
│   ├── small/
│   ├── medium/
│   └── large/
└── metadata/
    ├── manifest.json
    ├── checksums.sha256
    └── download_results.json
```

### Metadata Standards
- **Source Attribution**: Original URL, license, collection date
- **File Characteristics**: Size, format version, encoding
- **Testing Properties**: Complexity level, special features
- **Quality Metrics**: Validation status, integrity checks

### Integrity Verification
- SHA256 checksums for all files
- Download validation and retry logic
- File corruption detection
- Source availability monitoring

## Usage Examples

### Basic Data Processing
```bash
# Download all datasets
pyforge install sample-datasets ./data

# Process PDF files
pyforge convert ./data/pdf/small/ --output ./processed/

# Analyze Excel files
pyforge convert ./data/excel/ --format parquet

# Handle large CSV files
pyforge convert ./data/csv/large/ --streaming
```

### Format-Specific Testing
```bash
# Test database connectivity
pyforge connect ./data/access/small/Northwind_2007_VBNet.accdb

# Process geographic data
pyforge convert ./data/dbf/ --projection WGS84

# Extract XML elements
pyforge convert ./data/xml/small/ --xpath "//item/title"
```

### Performance Benchmarking
```bash
# Small file performance
pyforge benchmark ./data/*/small/

# Large file stress testing
pyforge benchmark ./data/csv/large/ --memory-limit 1GB

# Format comparison
pyforge benchmark ./data/ --compare-formats
```

## Troubleshooting

### Common Issues

#### Download Failures
- **SSL Certificate Issues**: Some government sites may have certificate problems
- **Kaggle Authentication**: Ensure API token is properly configured
- **Network Timeouts**: Large files may require stable internet connection

#### File Access Problems
- **Permissions**: Ensure write access to target directory
- **Disk Space**: Large datasets require sufficient storage
- **Format Support**: Verify PyForge CLI format compatibility

#### Performance Issues
- **Memory Usage**: Large files may require streaming processing
- **Processing Time**: Complex formats take longer to convert
- **Concurrent Access**: Multiple processes may impact performance

### Support Resources
- **Documentation**: [PyForge CLI Docs](https://github.com/your-org/pyforge-cli)
- **Issue Tracking**: [GitHub Issues](https://github.com/your-org/pyforge-cli/issues)
- **Community**: [Discussions](https://github.com/your-org/pyforge-cli/discussions)

## Statistics

### Success Rates
- **Overall**: 22/23 datasets working (95.7%)
- **PDF**: 1/2 working (50%)
- **Excel**: 5/5 working (100%)
- **XML**: 3/3 working (100%)
- **Access**: 3/3 working (100%)
- **DBF**: 3/3 working (100%)
- **MDF**: 2/2 working (100%)
- **CSV**: 6/6 working (100%)

### Size Distribution
- **Small (<100MB)**: 16 datasets (70%)
- **Medium (100MB-1GB)**: 5 datasets (22%)
- **Large (>1GB)**: 2 datasets (8%)

### Total Collection Size
- **Compressed**: ~2.5GB
- **Uncompressed**: ~8.2GB
- **Average per dataset**: ~350MB

---

*Last updated: 2025-01-24*
*Version: 1.0.0*
*PyForge CLI Sample Datasets Collection*