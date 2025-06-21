# XML to Parquet Conversion

Convert XML files to efficient Parquet format with intelligent structure analysis and configurable flattening strategies for analytics use cases.

## Features

### Core Capabilities
- **Automatic Structure Detection**: Analyzes XML hierarchy, namespaces, and array patterns
- **Intelligent Flattening**: Converts nested XML to tabular format with multiple strategies
- **Array Handling**: Detects and processes repeated elements (arrays) correctly  
- **Attribute Support**: Extracts XML attributes as separate columns
- **Namespace Handling**: Configurable namespace processing (preserve, strip, prefix)
- **Schema Preview**: Optional preview of detected structure before conversion

### Supported Input Formats
- `.xml` - Standard XML files
- `.xml.gz` - Gzip compressed XML
- `.xml.bz2` - Bzip2 compressed XML

### Output Format
- `.parquet` - Apache Parquet with Snappy compression (default)

## Basic Usage

### Simple Conversion
```bash
# Convert XML to Parquet
pyforge convert data.xml output.parquet

# Auto-generate output filename
pyforge convert data.xml
# Creates: data.parquet
```

### Schema Information
```bash
# View XML structure information
pyforge info data.xml

# Validate XML file
pyforge validate data.xml
```

## Command Options

### Flattening Strategies
Control how nested XML structures are flattened:

```bash
# Conservative (default) - Minimal flattening, preserve structure
pyforge convert data.xml output.parquet --flatten-strategy conservative

# Moderate - Balance between structure and usability  
pyforge convert data.xml output.parquet --flatten-strategy moderate

# Aggressive - Maximum flattening for analytics
pyforge convert data.xml output.parquet --flatten-strategy aggressive
```

### Array Handling
Control how repeated XML elements (arrays) are processed:

```bash
# Expand (default) - Create multiple rows for array elements
pyforge convert data.xml output.parquet --array-handling expand

# Concatenate - Join array values with delimiter
pyforge convert data.xml output.parquet --array-handling concatenate

# JSON String - Store arrays as JSON strings
pyforge convert data.xml output.parquet --array-handling json_string
```

### Namespace Handling
Control how XML namespaces are processed:

```bash
# Preserve (default) - Keep namespace prefixes in column names
pyforge convert data.xml output.parquet --namespace-handling preserve

# Strip - Remove all namespace information
pyforge convert data.xml output.parquet --namespace-handling strip

# Prefix - Convert namespaces to column prefixes
pyforge convert data.xml output.parquet --namespace-handling prefix
```

### Schema Preview
Preview the detected XML structure before conversion:

```bash
# Show schema preview and ask for confirmation
pyforge convert data.xml output.parquet --preview-schema
```

## Examples

### Example 1: Simple XML
**Input XML** (`customer.xml`):
```xml
<?xml version="1.0"?>
<customer>
    <id>1001</id>
    <name>John Doe</name>
    <email>john@example.com</email>
    <active>true</active>
</customer>
```

**Command:**
```bash
pyforge convert customer.xml customer.parquet
```

**Result:** Single row with columns:
- `customer_id`: "1001"
- `customer_name`: "John Doe" 
- `customer_email`: "john@example.com"
- `customer_active`: "true"

### Example 2: XML with Arrays
**Input XML** (`orders.xml`):
```xml
<?xml version="1.0"?>
<orders>
    <order id="1001" status="shipped">
        <item>Laptop</item>
        <item>Mouse</item>
        <total currency="USD">999.99</total>
    </order>
    <order id="1002" status="pending">
        <item>Keyboard</item>
        <total currency="EUR">49.99</total>
    </order>
</orders>
```

**Command:**
```bash
pyforge convert orders.xml orders.parquet
```

**Result:** Two rows (one per order) with columns:
- `orders_order@id`: "1001", "1002"
- `orders_order@status`: "shipped", "pending"  
- `orders_order_item`: "Laptop; Mouse", "Keyboard"
- `orders_order_total`: "999.99", "49.99"
- `orders_order_total@currency`: "USD", "EUR"

### Example 3: Complex Nested XML
**Input XML** (`catalog.xml`):
```xml
<?xml version="1.0"?>
<catalog xmlns:prod="http://example.com/products">
    <prod:book id="1">
        <title>XML Guide</title>
        <author>
            <name>John Smith</name>
            <email>john@example.com</email>
        </author>
        <tags>
            <tag>XML</tag>
            <tag>Programming</tag>
        </tags>
    </prod:book>
</catalog>
```

**Commands:**
```bash
# Conservative flattening (preserves structure)
pyforge convert catalog.xml catalog_conservative.parquet --flatten-strategy conservative

# Aggressive flattening (maximum columns)  
pyforge convert catalog.xml catalog_aggressive.parquet --flatten-strategy aggressive

# Strip namespaces
pyforge convert catalog.xml catalog_clean.parquet --namespace-handling strip
```

## Column Naming Convention

The converter uses a hierarchical naming convention for columns:

### Elements
- **Pattern**: `parent_element_child_element`
- **Example**: XML path `/catalog/book/title` → Column `catalog_book_title`

### Attributes  
- **Pattern**: `element_name@attribute_name`
- **Example**: `<book id="1">` → Column `catalog_book@id`

### Arrays
- **Pattern**: Same as elements, but may contain multiple values
- **Example**: Multiple `<tag>` elements → Column `catalog_book_tags_tag`

### Namespace Handling
- **Preserve**: `{http://example.com}book_title` → `{http://example.com}book_title`
- **Strip**: `{http://example.com}book_title` → `book_title`  
- **Prefix**: `{http://example.com}book_title` → `com_book_title`

## Performance Considerations

### File Size Guidelines
- **Small files** (< 10MB): Fast in-memory processing
- **Medium files** (10MB - 100MB): Efficient processing with progress tracking
- **Large files** (> 100MB): Use streaming mode (future feature)

### Memory Usage
- Conservative strategy: Lower memory usage, preserves structure
- Aggressive strategy: Higher memory usage, maximum flattening
- Array expansion: Can significantly increase row count

### Optimization Tips
```bash
# For large files with many arrays, use concatenate mode
pyforge convert large.xml output.parquet --array-handling concatenate

# For memory-constrained environments, use conservative flattening
pyforge convert data.xml output.parquet --flatten-strategy conservative
```

## Output Analysis

After conversion, you can analyze the Parquet files with standard tools:

### Python/Pandas
```python
import pandas as pd
df = pd.read_parquet('output.parquet')
print(df.info())
print(df.head())
```

### DuckDB
```sql
SELECT * FROM 'output.parquet' LIMIT 10;
```

### Apache Spark
```python
df = spark.read.parquet('output.parquet')
df.show()
```

## Common Use Cases

### 1. Data Migration
Convert XML exports from legacy systems to modern analytics formats:
```bash
pyforge convert legacy_export.xml modern_data.parquet --flatten-strategy aggressive
```

### 2. API Response Processing
Process XML API responses for data analysis:
```bash
pyforge convert api_response.xml analysis_data.parquet --array-handling expand
```

### 3. Configuration Analysis
Analyze XML configuration files:
```bash
pyforge convert config.xml config_analysis.parquet --namespace-handling strip
```

### 4. Log Processing
Convert structured XML logs to tabular format:
```bash
pyforge convert logs.xml log_analysis.parquet --flatten-strategy moderate
```

## Troubleshooting

### Common Issues

**Issue**: "Invalid XML file" error
```bash
# Solution: Validate XML first
pyforge validate data.xml
```

**Issue**: Too many columns created
```bash
# Solution: Use conservative flattening
pyforge convert data.xml output.parquet --flatten-strategy conservative
```

**Issue**: Array data looks wrong
```bash
# Solution: Try different array handling
pyforge convert data.xml output.parquet --array-handling concatenate
```

**Issue**: Namespace prefixes too long
```bash
# Solution: Strip namespaces
pyforge convert data.xml output.parquet --namespace-handling strip
```

### Getting Help

```bash
# View detailed help
pyforge convert --help

# Check supported formats
pyforge formats

# View file information
pyforge info data.xml
```

## Implementation Details

### Architecture
The XML converter consists of three main components:

1. **XmlStructureAnalyzer**: Analyzes XML schema, detects arrays and namespaces
2. **XmlFlattener**: Flattens hierarchical data using configurable strategies  
3. **XmlConverter**: Orchestrates the conversion process and CLI integration

### Data Type Handling
- **Phase 1**: All data converted to strings for maximum compatibility
- **Future**: Type inference and preservation planned

### String Conversion
All XML data is converted to strings following these rules:
- Text content: Extracted as-is
- Attributes: Converted to strings
- Arrays: Joined with "; " delimiter (concatenate mode)
- Null/empty: Empty strings

## Limitations

### Current Limitations
- All data types converted to strings (Phase 1 implementation)
- Large file streaming not yet implemented
- Some complex nested arrays may not flatten optimally
- DTD and entity resolution not supported

### Future Enhancements
- Data type inference and preservation
- Streaming mode for very large files
- Advanced array expansion strategies
- Custom flattening rules
- XPath-based filtering

## Contributing

The XML converter is part of the PyForge CLI project. Contributions are welcome:

1. **Bug Reports**: File issues with sample XML files
2. **Feature Requests**: Suggest improvements or new flattening strategies
3. **Code Contributions**: Follow the existing converter patterns

See the project repository for contribution guidelines.