# XML Converter Quick Reference

## Basic Commands

```bash
# Simple conversion
pyforge convert data.xml output.parquet

# View XML structure
pyforge info data.xml

# Validate XML
pyforge validate data.xml

# Check supported formats  
pyforge formats
```

## Conversion Options

| Option | Values | Description |
|--------|--------|-------------|
| `--flatten-strategy` | `conservative`, `moderate`, `aggressive` | How aggressively to flatten nested structures |
| `--array-handling` | `expand`, `concatenate`, `json_string` | How to handle repeated elements |
| `--namespace-handling` | `preserve`, `strip`, `prefix` | How to process XML namespaces |
| `--preview-schema` | flag | Show structure preview before conversion |

## Flattening Strategies

### Conservative (Default)
- Minimal flattening
- Preserves XML structure  
- Good for: Configuration files, simple XML

### Moderate  
- Balanced approach
- Creates logical records
- Good for: API responses, structured data

### Aggressive
- Maximum flattening
- Creates most columns
- Good for: Analytics, data warehousing

## Array Handling

### Expand (Default)
- Creates multiple rows for arrays
- Best for: Relational analysis

### Concatenate  
- Joins values with "; " delimiter
- Best for: Preserving all data in single row

### JSON String
- Stores arrays as JSON strings
- Best for: Complex nested structures

## Column Naming

| XML Structure | Column Name |
|---------------|-------------|
| `<root><name>John</name></root>` | `root_name` |
| `<book id="1">Title</book>` | `book` (text), `book@id` (attribute) |
| `<ns:element xmlns:ns="...">` | Depends on namespace handling |

## Common Patterns

```bash
# Data migration
pyforge convert legacy.xml modern.parquet --flatten-strategy aggressive

# API processing  
pyforge convert response.xml data.parquet --array-handling expand

# Configuration analysis
pyforge convert config.xml analysis.parquet --namespace-handling strip

# Preview before converting
pyforge convert complex.xml output.parquet --preview-schema
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Too many columns | Use `--flatten-strategy conservative` |
| Array data incorrect | Try `--array-handling concatenate` |
| Namespace issues | Use `--namespace-handling strip` |
| Invalid XML error | Run `pyforge validate file.xml` first |

## File Support

- ✅ `.xml` - Standard XML files
- ✅ `.xml.gz` - Gzip compressed  
- ✅ `.xml.bz2` - Bzip2 compressed
- ✅ Various encodings (UTF-8, UTF-16, etc.)

## Output Analysis

```python
# Python/Pandas
import pandas as pd
df = pd.read_parquet('output.parquet')
print(df.head())

# DuckDB
SELECT * FROM 'output.parquet';

# Spark
df = spark.read.parquet('output.parquet')
```