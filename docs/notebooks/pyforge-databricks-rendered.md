# PyForge Databricks: Advanced Volume Integration and Serverless Optimization

This notebook demonstrates PyForge Databricks, an advanced integration that extends PyForge Core with Databricks-specific features including Unity Catalog Volume support, serverless compute optimization, and distributed processing capabilities.

## Introduction

PyForge Databricks builds upon PyForge Core to provide seamless integration with Databricks environments. This guide covers:

- Databricks SDK integration for Volume operations
- Serverless compute detection and optimization
- Direct Volume-to-Volume file conversions
- Format-specific routing for optimal performance
- Batch processing with distributed computing
- Delta Lake integration

### Key Enhancements:
- **Unity Catalog Volumes**: Direct read/write operations on Volume paths
- **Serverless Optimization**: Automatic detection and optimization for serverless compute
- **Distributed Processing**: Leverage Spark for supported formats (CSV, JSON, XML)
- **Delta Lake Integration**: Native support for Delta format conversions
- **Databricks SDK**: Full integration with workspace APIs

### Architecture:
- **Intelligent Routing**: Automatically selects optimal processing engine
- **Volume-Native**: Works directly with `/Volumes/` paths
- **Memory Efficient**: Streaming for large files, distributed for supported formats
- **Environment Aware**: Adapts to serverless vs. classic compute

---

## 1. Installation and Environment Setup

Install both PyForge Core and PyForge Databricks packages.

```python
# Install PyForge packages
%pip install pyforge-core pyforge-databricks --quiet

# Restart Python kernel for clean imports
dbutils.library.restartPython()
```

```python
# Import required libraries
import os
import sys
from datetime import datetime
from pathlib import Path
import json

# Databricks SDK
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import catalog

# PyForge imports
from pyforge_core import PyForgeCore
from pyforge_databricks import PyForgeDatabricks

# Spark imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp, count, sum as spark_sum

print("🚀 PyForge Databricks Integration loaded!")
print(f"📍 Python version: {sys.version.split()[0]}")
print(f"🏢 Databricks Runtime: {spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion')}")
```

---

## 2. Environment Detection and Validation

PyForge Databricks automatically detects your environment and optimizes accordingly.

```python
# Initialize PyForge Databricks
forge = PyForgeDatabricks()

# Get detailed environment information
env_info = forge.env.get_environment_info()

print("🔍 Environment Detection Results:")
print("=" * 60)

# Display environment details
env_details = [
    ("Databricks Environment", env_info['is_databricks'], "✅" if env_info['is_databricks'] else "❌"),
    ("Serverless Compute", env_info['is_serverless'], "⚡" if env_info['is_serverless'] else "🖥️"),
    ("Environment Version", env_info['environment_version'], f"v{env_info['environment_version']}"),
    ("Python Version", env_info['python_version'], "🐍"),
    ("Spark Version", env_info['spark_version'], "✨"),
    ("Cluster Type", env_info['cluster_type'], "🏢")
]

for label, value, icon in env_details:
    print(f"{icon} {label:25}: {value}")

# Validate SDK connection
print("\n🔌 Validating Databricks SDK connection...")
try:
    current_user = forge.w.current_user.me()
    print(f"✅ Connected as: {current_user.display_name}")
    print(f"📧 Email: {current_user.user_name}")
    sdk_connected = True
except Exception as e:
    print(f"❌ SDK connection failed: {str(e)}")
    print("   Note: Some features may be limited without SDK access")
    sdk_connected = False
```

---

## 3. Unity Catalog Volume Setup

Configure Unity Catalog paths and verify Volume access.

```python
# Configure your Unity Catalog settings
CATALOG = "main"          # Replace with your catalog
SCHEMA = "default"        # Replace with your schema
BRONZE_VOLUME = "bronze"  # Raw data volume
SILVER_VOLUME = "silver"  # Processed data volume
GOLD_VOLUME = "gold"      # Curated data volume

# Construct Volume paths
bronze_path = f"/Volumes/{CATALOG}/{SCHEMA}/{BRONZE_VOLUME}"
silver_path = f"/Volumes/{CATALOG}/{SCHEMA}/{SILVER_VOLUME}"
gold_path = f"/Volumes/{CATALOG}/{SCHEMA}/{GOLD_VOLUME}"

print("📁 Unity Catalog Volume Configuration:")
print("=" * 60)
print(f"📦 Catalog: {CATALOG}")
print(f"📋 Schema: {SCHEMA}")
print(f"\nVolume Paths:")
print(f"  🥉 Bronze (Raw): {bronze_path}")
print(f"  🥈 Silver (Processed): {silver_path}")
print(f"  🥇 Gold (Curated): {gold_path}")

# List available volumes
if sdk_connected:
    print("\n📂 Available Volumes:")
    try:
        volumes = forge.w.volumes.list(catalog_name=CATALOG, schema_name=SCHEMA)
        for vol in volumes:
            vol_type = "📁" if vol.volume_type == "MANAGED" else "🔗"
            print(f"  {vol_type} {vol.name} ({vol.volume_type})")
    except Exception as e:
        print(f"  ⚠️ Could not list volumes: {str(e)}")
else:
    print("\n⚠️ SDK not connected - skipping volume listing")
```

---

## 4. Installing Sample Datasets to Volumes

Create sample datasets directly in Unity Catalog Volumes for testing.

```python
print("📦 Installing Sample Datasets to Volumes...")
print("=" * 60)

# Sample dataset 1: Customer data (CSV)
customer_csv = """customer_id,name,email,country,registration_date,total_purchases
1001,Alice Johnson,alice@email.com,USA,2023-01-15,5430.50
1002,Bob Smith,bob@email.com,Canada,2023-02-20,3250.75
1003,Charlie Davis,charlie@email.com,UK,2023-03-10,7890.25
1004,Diana Prince,diana@email.com,USA,2023-04-05,12500.00
1005,Eve Wilson,eve@email.com,Australia,2023-05-12,4567.80"""

# Sample dataset 2: Product catalog (JSON)
product_json = {
    "catalog_version": "2024.1",
    "last_updated": "2024-01-15",
    "products": [
        {
            "id": "P001",
            "name": "Laptop Pro Max",
            "category": "Electronics",
            "price": 1299.99,
            "specs": {
                "cpu": "M3 Pro",
                "ram": "32GB",
                "storage": "1TB SSD"
            },
            "tags": ["premium", "professional", "portable"]
        },
        {
            "id": "P002",
            "name": "Wireless Headphones",
            "category": "Audio",
            "price": 349.99,
            "features": ["noise-canceling", "30hr battery", "bluetooth 5.3"]
        }
    ]
}

# Sample dataset 3: Sales transactions (XML)
sales_xml = """<?xml version="1.0" encoding="UTF-8"?>
<transactions>
    <transaction id="T001">
        <date>2024-01-15</date>
        <customer_id>1001</customer_id>
        <items>
            <item>
                <product_id>P001</product_id>
                <quantity>1</quantity>
                <price>1299.99</price>
            </item>
        </items>
        <total>1299.99</total>
    </transaction>
    <transaction id="T002">
        <date>2024-01-16</date>
        <customer_id>1002</customer_id>
        <items>
            <item>
                <product_id>P002</product_id>
                <quantity>2</quantity>
                <price>349.99</price>
            </item>
        </items>
        <total>699.98</total>
    </transaction>
</transactions>"""

# Write sample files to Bronze Volume
sample_files = [
    (f"{bronze_path}/customers.csv", customer_csv),
    (f"{bronze_path}/products.json", json.dumps(product_json, indent=2)),
    (f"{bronze_path}/transactions.xml", sales_xml)
]

for file_path, content in sample_files:
    try:
        forge.volume_handler.write_file(file_path, content.encode('utf-8'))
        print(f"✅ Created: {Path(file_path).name}")
    except Exception as e:
        print(f"❌ Failed to create {Path(file_path).name}: {str(e)}")

print("\n📊 Sample datasets installed in Bronze Volume")
```

---

## 5. Basic Volume-to-Volume Conversions

Use the simplified `forge.convert()` API for Volume operations.

### Convert CSV to Parquet using automatic Volume detection

```python
print("🔄 Converting Customer CSV to Parquet...")
print("=" * 60)

# Input and output paths
input_csv = f"{bronze_path}/customers.csv"
output_parquet = f"{silver_path}/customers.parquet"

print(f"📄 Input: {input_csv}")
print(f"📦 Output: {output_parquet}")

# Perform conversion - PyForge automatically detects Volume paths
result = forge.convert(
    input_path=input_csv,
    output_path=output_parquet,
    format_options={
        'compression': 'snappy',
        'schema_inference': True
    }
)

print(f"\n✅ Conversion successful!")
print(f"⏱️  Duration: {result['duration']:.2f}s")
print(f"📊 Rows processed: {result['row_count']}")
print(f"🔧 Processing engine: {result['processing_engine']}")

# Read and display the converted data
df = spark.read.parquet(output_parquet)
print(f"\n📋 Schema of converted data:")
df.printSchema()
display(df)
```

### Auto-generate output paths

```python
print("🔄 Converting with Auto-Generated Output Paths...")
print("=" * 60)

# Convert JSON without specifying output path
json_input = f"{bronze_path}/products.json"

print(f"📄 Converting: {json_input}")
print("📍 Output path will be auto-generated in the same volume")

result = forge.convert(
    input_path=json_input,
    output_format="parquet",
    json_options={
        'flatten_nested': True,
        'normalize_arrays': True
    }
)

print(f"\n✅ Conversion successful!")
print(f"📦 Output: {result['output_path']}")
print(f"⏱️  Duration: {result['duration']:.2f}s")

# Display the flattened structure
df = spark.read.parquet(result['output_path'])
display(df)
```

---

## 6. Format-Specific Processing Strategies

PyForge Databricks automatically selects the optimal processing strategy based on file format and environment.

```python
print("🎯 Processing Strategy Analysis:")
print("=" * 60)

# Test different file formats
test_scenarios = [
    {
        'file': 'data.csv',
        'format': 'CSV',
        'size': 'Large (1GB+)',
        'expected_strategy': 'Databricks Native (Spark)'
    },
    {
        'file': 'report.xlsx',
        'format': 'Excel',
        'size': 'Medium (100MB)',
        'expected_strategy': 'Hybrid (PyForge + Spark)'
    },
    {
        'file': 'config.json',
        'format': 'JSON',
        'size': 'Small (10MB)',
        'expected_strategy': 'Databricks Native (Spark)'
    },
    {
        'file': 'document.pdf',
        'format': 'PDF',
        'size': 'Any',
        'expected_strategy': 'PyForge Converter'
    }
]

for scenario in test_scenarios:
    file_ext = Path(scenario['file']).suffix
    strategy = forge.processor.get_processing_strategy(file_ext)
    
    print(f"\n📄 {scenario['file']}")
    print(f"   Format: {scenario['format']}")
    print(f"   Size: {scenario['size']}")
    print(f"   Strategy: {strategy}")
    print(f"   Expected: {scenario['expected_strategy']}")
    
    # Show optimization details
    if forge.env.is_serverless and 'Native' in scenario['expected_strategy']:
        print("   ⚡ Serverless Optimizations:")
        print("      • Photon acceleration")
        print("      • Adaptive query execution")
        print("      • Dynamic resource scaling")
```

---

## 7. Advanced XML Processing with Hierarchical Flattening

Process complex XML structures with automatic flattening.

```python
print("🌳 Processing Hierarchical XML Data...")
print("=" * 60)

xml_input = f"{bronze_path}/transactions.xml"
xml_output = f"{silver_path}/transactions_flat.parquet"

print("📄 Converting XML with structure flattening...")
print(f"   Input: {xml_input}")
print(f"   Output: {xml_output}")

# Perform conversion with XML-specific options
result = forge.convert(
    input_path=xml_input,
    output_path=xml_output,
    xml_options={
        'flatten_nested': True,
        'array_detection': True,
        'preserve_attributes': True,
        'root_tag': 'transaction'
    }
)

print(f"\n✅ XML conversion successful!")
print(f"🔧 Processing details:")
print(f"   • Nested structures flattened")
print(f"   • Arrays detected and normalized")
print(f"   • XML attributes preserved as columns")

# Display the flattened result
df = spark.read.parquet(xml_output)
print(f"\n📊 Flattened structure ({df.count()} rows, {len(df.columns)} columns):")
display(df)
```

---

## 8. Excel Multi-Sheet Processing

Handle complex Excel files with multiple sheets and different structures.

```python
# Create a complex Excel file with multiple sheets
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample data for multiple sheets
dates = pd.date_range('2024-01-01', periods=30, freq='D')

# Sheet 1: Daily Sales
daily_sales = pd.DataFrame({
    'date': dates,
    'revenue': np.random.randint(5000, 15000, size=30),
    'transactions': np.random.randint(50, 200, size=30),
    'region': np.random.choice(['North', 'South', 'East', 'West'], size=30)
})

# Sheet 2: Product Performance  
products = ['Product A', 'Product B', 'Product C', 'Product D']
product_performance = pd.DataFrame({
    'date': dates,
    'product': np.random.choice(products, size=30),
    'units_sold': np.random.randint(10, 100, size=30),
    'revenue': np.random.randint(1000, 5000, size=30)
})

# Sheet 3: Customer Metrics (different structure)
customer_metrics = pd.DataFrame({
    'metric_date': dates[::5],  # Every 5 days
    'new_customers': np.random.randint(5, 50, size=6),
    'churn_rate': np.random.uniform(0.01, 0.05, size=6),
    'satisfaction_score': np.random.uniform(4.0, 5.0, size=6)
})

# Save to Excel file in Bronze Volume
excel_path = f"/tmp/analytics_report.xlsx"
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    daily_sales.to_excel(writer, sheet_name='Daily_Sales', index=False)
    product_performance.to_excel(writer, sheet_name='Product_Performance', index=False)
    customer_metrics.to_excel(writer, sheet_name='Customer_Metrics', index=False)

# Upload to Volume
with open(excel_path, 'rb') as f:
    excel_content = f.read()
    
excel_volume_path = f"{bronze_path}/analytics_report.xlsx"
forge.volume_handler.write_file(excel_volume_path, excel_content)

print("✅ Created multi-sheet Excel file with 3 sheets")
```

### Convert Excel with intelligent sheet handling

```python
print("📊 Converting Multi-Sheet Excel File...")
print("=" * 60)

excel_output = f"{silver_path}/analytics_combined.parquet"

# Get information about the Excel file
excel_info = forge.get_info(excel_volume_path)
print(f"📋 Excel File Information:")
print(f"   Sheets: {excel_info.get('sheet_count', 0)}")
print(f"   Sheet names: {excel_info.get('sheet_names', [])}")

# Convert with sheet combination
result = forge.convert(
    input_path=excel_volume_path,
    output_path=excel_output,
    excel_options={
        'combine_sheets': True,
        'sheet_matching_strategy': 'column_signature',
        'include_sheet_name': True
    }
)

print(f"\n✅ Excel conversion completed!")
print(f"📊 Processing summary:")
print(f"   Sheets processed: {result['sheets_processed']}")
print(f"   Total rows: {result['row_count']}")
print(f"   Matching strategy: Column signature analysis")

# Display combined data
df = spark.read.parquet(excel_output)
print(f"\n📋 Combined data structure:")
display(df.groupBy("sheet_name").count().orderBy("sheet_name"))
```

---

## 9. Batch Processing with Parallel Execution

Process multiple files efficiently using PyForge Databricks batch capabilities.

```python
# Create sample files for batch processing
print("📦 Creating Sample Files for Batch Processing...")
print("=" * 60)

# Generate monthly sales data files
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun']
batch_files = []

for i, month in enumerate(months):
    # Create CSV data for each month
    month_data = f"""date,store_id,product_category,sales_amount,units_sold
2024-{i+1:02d}-01,S001,Electronics,{5000+i*500},25
2024-{i+1:02d}-02,S002,Clothing,{3000+i*300},40
2024-{i+1:02d}-03,S003,Food,{4000+i*400},100
2024-{i+1:02d}-04,S001,Electronics,{5500+i*550},28
2024-{i+1:02d}-05,S002,Clothing,{3200+i*320},45"""
    
    file_path = f"{bronze_path}/sales_{month}_2024.csv"
    forge.volume_handler.write_file(file_path, month_data.encode('utf-8'))
    batch_files.append(file_path)
    print(f"✅ Created: sales_{month}_2024.csv")

print(f"\n📊 Total files created: {len(batch_files)}")
```

```python
# Batch convert all files with progress tracking
print("🔄 Batch Converting Files to Parquet...")
print("=" * 60)

from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def convert_file(input_path):
    """Convert a single file"""
    output_path = input_path.replace('.csv', '.parquet').replace(bronze_path, silver_path)
    
    start_time = time.time()
    try:
        result = forge.convert(
            input_path=input_path,
            output_path=output_path,
            format_options={'compression': 'snappy'}
        )
        
        return {
            'file': Path(input_path).name,
            'status': 'success',
            'duration': time.time() - start_time,
            'rows': result.get('row_count', 0),
            'output': output_path
        }
    except Exception as e:
        return {
            'file': Path(input_path).name,
            'status': 'failed',
            'error': str(e),
            'duration': time.time() - start_time
        }

# Process files in parallel
batch_start = time.time()
results = []

with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit all conversion tasks
    future_to_file = {executor.submit(convert_file, f): f for f in batch_files}
    
    # Process completed conversions
    for future in as_completed(future_to_file):
        result = future.result()
        results.append(result)
        
        if result['status'] == 'success':
            print(f"✅ {result['file']} → Converted in {result['duration']:.2f}s")
        else:
            print(f"❌ {result['file']} → Failed: {result['error']}")

# Summary statistics
batch_duration = time.time() - batch_start
success_count = sum(1 for r in results if r['status'] == 'success')
total_rows = sum(r.get('rows', 0) for r in results if r['status'] == 'success')

print(f"\n📊 Batch Processing Summary:")
print(f"   Total files: {len(batch_files)}")
print(f"   Successful: {success_count}")
print(f"   Failed: {len(batch_files) - success_count}")
print(f"   Total duration: {batch_duration:.2f}s")
print(f"   Average time per file: {batch_duration/len(batch_files):.2f}s")
print(f"   Total rows processed: {total_rows}")
```

### Combine all converted files into a single dataset

```python
print("🔗 Combining Batch Results into Single Dataset...")
print("=" * 60)

# Read all parquet files
parquet_pattern = f"{silver_path}/sales_*_2024.parquet"
combined_df = spark.read.parquet(parquet_pattern)

print(f"📊 Combined dataset statistics:")
print(f"   Total rows: {combined_df.count()}")
print(f"   Total columns: {len(combined_df.columns)}")

# Analyze the combined data
sales_summary = combined_df.groupBy("product_category").agg(
    spark_sum("sales_amount").alias("total_sales"),
    spark_sum("units_sold").alias("total_units"),
    count("*").alias("transaction_count")
).orderBy("total_sales", ascending=False)

print("\n💰 Sales Summary by Category:")
display(sales_summary)

# Save combined dataset with partitioning
final_output = f"{gold_path}/sales_2024_combined"
combined_df.write.mode("overwrite").partitionBy("product_category").parquet(final_output)

print(f"\n✅ Combined dataset saved to Gold layer: {final_output}")
```

---

## 10. Delta Lake Integration

Convert data directly to Delta Lake format for versioning and time travel.

```python
# Convert to Delta Lake format
print("🔺 Converting to Delta Lake Format...")
print("=" * 60)

# Source data
source_parquet = f"{silver_path}/customers.parquet"
delta_table_path = f"{gold_path}/customers_delta"

print(f"📄 Source: {source_parquet}")
print(f"🔺 Target Delta: {delta_table_path}")

# Convert to Delta with optimization
result = forge.convert(
    input_path=source_parquet,
    output_path=delta_table_path,
    output_format="delta",
    delta_options={
        'mode': 'overwrite',
        'optimizeWrite': True,
        'autoCompact': True
    }
)

print(f"\n✅ Delta conversion successful!")
print(f"⏱️  Duration: {result['duration']:.2f}s")

# Create Delta table and show history
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS customers_delta
    USING DELTA
    LOCATION '{delta_table_path}'
""")

print("\n📊 Delta Table Information:")
display(spark.sql("DESCRIBE DETAIL customers_delta"))

# Perform an update to create version history
spark.sql("""
    UPDATE customers_delta 
    SET total_purchases = total_purchases * 1.1 
    WHERE country = 'USA'
""")

print("\n📜 Delta Table History:")
display(spark.sql("DESCRIBE HISTORY customers_delta"))
```

---

## 11. Performance Monitoring and Optimization

Monitor conversion performance and resource utilization.

```python
print("📊 Performance Monitoring Dashboard")
print("=" * 60)

# Get conversion statistics
stats = forge.get_conversion_statistics()

if stats:
    print("\n📈 Conversion Statistics:")
    print(f"   Total conversions: {stats['total_conversions']}")
    print(f"   Successful: {stats['successful']}")
    print(f"   Failed: {stats['failed']}")
    print(f"   Average duration: {stats['avg_duration']:.2f}s")
    print(f"   Total data processed: {stats['total_bytes_processed'] / (1024**3):.2f} GB")

# Check serverless optimizations
if forge.env.is_serverless:
    print("\n⚡ Serverless Optimizations Active:")
    optimizations = [
        ("Photon Acceleration", "2-10x faster processing"),
        ("Adaptive Query Execution", "Dynamic optimization"),
        ("Auto-scaling", "Resources scale with workload"),
        ("Columnar Caching", "Faster repeated queries"),
        ("Dynamic File Pruning", "Reduced I/O operations")
    ]
    
    for opt, benefit in optimizations:
        print(f"   ✅ {opt}: {benefit}")
    
    # Show key Spark configurations
    print("\n🔧 Spark Configuration:")
    configs = [
        "spark.databricks.compute.type",
        "spark.databricks.photon.enabled",
        "spark.sql.adaptive.enabled",
        "spark.sql.adaptive.coalescePartitions.enabled",
        "spark.sql.adaptive.skewJoin.enabled"
    ]
    
    for config in configs:
        try:
            value = spark.conf.get(config)
            print(f"   {config}: {value}")
        except:
            print(f"   {config}: Not set")

# Memory usage guidelines
print("\n💾 Memory Usage Guidelines by Format:")
memory_guide = {
    'CSV': {'factor': 2, 'note': 'String parsing overhead'},
    'JSON': {'factor': 3, 'note': 'Nested structure parsing'},
    'XML': {'factor': 4, 'note': 'DOM tree construction'},
    'Excel': {'factor': 2.5, 'note': 'Per-sheet memory allocation'},
    'Parquet': {'factor': 0.5, 'note': 'Columnar compression'},
    'PDF': {'factor': 1.5, 'note': 'Text extraction buffers'}
}

for format_type, info in memory_guide.items():
    print(f"   {format_type}: ~{info['factor']}x file size ({info['note']})")
```

---

## 12. Production Best Practices

Guidelines for using PyForge Databricks in production environments.

```python
print("📚 Production Best Practices")
print("=" * 60)

best_practices = {
    "🗂️ Volume Organization": [
        "Follow medallion architecture (Bronze → Silver → Gold)",
        "Use descriptive naming: include date, source, version",
        "Implement retention policies for each layer",
        "Regular cleanup of temporary conversion files"
    ],
    
    "⚡ Performance Optimization": [
        "Use forge.convert() for automatic optimization",
        "Batch similar files for parallel processing",
        "Enable compression for Parquet/Delta outputs",
        "Monitor cluster utilization during large jobs"
    ],
    
    "🔒 Security & Governance": [
        "Leverage Unity Catalog for fine-grained access control",
        "Audit all conversion operations",
        "Encrypt sensitive data at rest and in transit",
        "Use service principals for automated workflows"
    ],
    
    "🛠️ Error Handling": [
        "Implement comprehensive try-except blocks",
        "Log all conversion attempts and failures",
        "Set up alerts for failed conversions",
        "Maintain fallback strategies for critical pipelines"
    ],
    
    "📈 Monitoring": [
        "Track conversion metrics (duration, volume, success rate)",
        "Monitor Volume storage usage and costs",
        "Set up dashboards for pipeline health",
        "Regular performance baseline updates"
    ]
}

for category, practices in best_practices.items():
    print(f"\n{category}:")
    for practice in practices:
        print(f"  • {practice}")
```

---

## Summary

You've learned how to use PyForge Databricks for advanced data processing:

✅ **Environment Detection**: Automatic optimization for serverless compute  
✅ **Volume Integration**: Direct operations on Unity Catalog Volumes  
✅ **Smart Routing**: Optimal processing engine selection by format  
✅ **Batch Processing**: Parallel execution for multiple files  
✅ **Delta Lake**: Native support for versioned data  
✅ **Performance**: Monitoring and optimization strategies  
✅ **Production Ready**: Best practices and integration patterns  

### Key Advantages:
- **Unified API**: Simple `forge.convert()` works everywhere
- **Auto-optimization**: Detects and uses best processing engine
- **Volume-native**: No local downloads required
- **Serverless-ready**: Scales automatically with workload

### Next Steps:
1. Install in your environment: `pip install pyforge-core pyforge-databricks`
2. Configure Unity Catalog Volumes
3. Start with simple conversions
4. Build production pipelines
5. Monitor and optimize performance

```python
# Display package versions
print("📦 Package Information:")
print("=" * 60)
print(f"pyforge-core version: {PyForgeCore.__version__}")
print(f"pyforge-databricks version: {PyForgeDatabricks.__version__}")
print(f"Databricks SDK version: {forge.w.version}")
print(f"Python version: {sys.version.split()[0]}")
print(f"Spark version: {spark.version}")

print("\n🎉 Happy converting with PyForge Databricks!")
```

## How to Use This Notebook

1. **Import to Databricks**: Copy the notebook content and create a new notebook in your Databricks workspace
2. **Configure Unity Catalog**: Update the CATALOG, SCHEMA, and VOLUME names to match your environment
3. **Run Sequentially**: Execute cells in order for the complete experience
4. **Customize**: Adapt examples to your specific use cases and data formats