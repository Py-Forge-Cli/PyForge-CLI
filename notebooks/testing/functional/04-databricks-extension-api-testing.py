# Databricks notebook source
# dbutils is globally available in Databricks notebooks
# type: ignore
# MAGIC %md
# MAGIC # PyForge CLI Databricks Extension - API Testing
# MAGIC
# MAGIC This notebook tests the PyForge CLI Databricks Extension API functionality using Python methods (not CLI commands).
# MAGIC
# MAGIC ## Test Pattern:
# MAGIC 1. Configure widgets for dynamic testing
# MAGIC 2. Install PyForge from Unity Catalog Volume
# MAGIC 3. Download ALL available sample datasets
# MAGIC 4. Display dataset information with sizes
# MAGIC 5. Select smallest file of each type for testing
# MAGIC 6. Test PyForgeDatabricks API methods (convert, info, validate)
# MAGIC 7. Display comprehensive results

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Install PyForge from Unity Catalog Volume

# COMMAND ----------

# Create widgets for configuration first (they persist across restarts)
dbutils.widgets.text("username", "usa-sdandey@deloitte.com", "Databricks Username")
dbutils.widgets.text("wheel_version", "1.0.9.dev53", "PyForge Wheel Version")
dbutils.widgets.text("sample_datasets_path", "/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/", "Sample Datasets Path")
dbutils.widgets.text("conversion_output_path", "", "Conversion Output Path (leave empty for auto)")
dbutils.widgets.dropdown("verbose", "yes", ["yes", "no"], "Verbose Output")
dbutils.widgets.dropdown("force_download", "no", ["yes", "no"], "Force Download Datasets")

# Get widget values for installation
username = dbutils.widgets.get("username")
wheel_version = dbutils.widgets.get("wheel_version")

# Construct wheel path
wheel_path = f"/Volumes/cortex_dev_catalog/sandbox_testing/pkgs/{username}/pyforge_cli-{wheel_version}-py3-none-any.whl"
print(f"Installing PyForge from: {wheel_path}")

# Install the wheel with proper flags for Databricks Serverless
%pip install {wheel_path} --no-cache-dir --quiet --index-url https://pypi.org/simple/ --trusted-host pypi.org

print("✓ PyForge installation complete")

# COMMAND ----------

# Restart Python to ensure clean imports
dbutils.library.restartPython()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Configuration Display

# COMMAND ----------

# Get widget values after restart
username = dbutils.widgets.get("username")
wheel_version = dbutils.widgets.get("wheel_version")
sample_datasets_path = dbutils.widgets.get("sample_datasets_path")
conversion_output_path = dbutils.widgets.get("conversion_output_path")
verbose = dbutils.widgets.get("verbose") == "yes"
force_download = dbutils.widgets.get("force_download") == "yes"

# Display configuration
print("=" * 60)
print("PyForge Databricks Extension API Testing")
print("=" * 60)
print(f"Username: {username}")
print(f"Wheel Version: {wheel_version}")
print(f"Sample Datasets Path: {sample_datasets_path}")
print(f"Conversion Output Path: {conversion_output_path or 'Auto-generated'}")
print(f"Verbose Output: {verbose}")
print(f"Force Download: {force_download}")
print("=" * 60)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Import and Initialize PyForge API

# COMMAND ----------

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Import PyForge
try:
    import pyforge_cli
    print(f"✓ PyForge CLI version: {pyforge_cli.__version__}")
except ImportError as e:
    print(f"✗ Failed to import pyforge_cli: {e}")
    raise

# Import Databricks Extension
try:
    from pyforge_cli.extensions.databricks import PyForgeDatabricks
    print("✓ Databricks extension imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Databricks extension: {e}")
    raise

# Import Sample Datasets Installer
try:
    from pyforge_cli.installers.sample_datasets_installer import SampleDatasetsInstaller
    print("✓ Sample datasets installer imported successfully")
except ImportError as e:
    print(f"✗ Failed to import sample datasets installer: {e}")
    raise

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Environment Information

# COMMAND ----------

# Initialize PyForgeDatabricks with existing Spark session
# In Databricks notebooks, 'spark' is automatically available
try:
    # Use the global spark variable if available
    forge = PyForgeDatabricks(spark_session=spark)
    print("✓ Initialized with existing Databricks spark session")
except NameError:
    # Fallback if spark variable not available
    forge = PyForgeDatabricks()
    print("✓ Initialized with auto-detected spark session")

# Get environment information
env_info = forge.get_environment_info()

print("Environment Information:")
print(json.dumps(env_info, indent=2))

print(f"\n✓ Running in Databricks: {env_info.get('is_databricks', False)}")
print(f"✓ Compute Type: {env_info.get('compute_type', 'Unknown')}")
print(f"✓ Runtime Version: {env_info.get('runtime_version', 'Unknown')}")
print(f"✓ Is Serverless: {env_info.get('is_serverless', False)}")
print(f"✓ Serverless Version: {env_info.get('serverless_version', 'N/A')}")
print(f"✓ Spark Connect Enabled: {env_info.get('spark_connect_enabled', False)}")

# COMMAND ----------

# Display key environment variables for debugging
import os

print("\n=== Key Environment Variables ===")
key_env_vars = [
    'IS_SERVERLESS',
    'SPARK_ENV_LOADED', 
    'DATABRICKS_RUNTIME_VERSION',
    'SPARK_CONNECT_MODE_ENABLED',
    'POD_NAME',
    'DB_INSTANCE_TYPE'
]

for var in key_env_vars:
    value = os.environ.get(var, 'Not set')
    print(f"{var}: {value}")

# Optionally display all environment variables (commented out for brevity)
# print("\n=== All Environment Variables ===")
# env_vars = dict(os.environ)
# for key, value in sorted(env_vars.items()):
#     print(f"{key}: {value}")

# Debug: Check converter registration
print("\n\n=== Converter Registration Debug ===")
print(f"Converters initialized: {forge._converters_initialized}")
print(f"Registered converters: {list(forge.fallback_manager._converter_registry.keys())}")
print(f"Spark session available: {forge.spark is not None}")
if forge.spark:
    print(f"Spark version: {forge.spark.version}")
    # Note: sparkContext.appName not available in Databricks Serverless (Spark Connect mode)

print(f"\nConverter availability:")
for converter_type in forge.fallback_manager._converter_registry.keys():
    available = forge.fallback_manager._is_converter_available(converter_type)
    print(f"  - {converter_type.value}: {'Available' if available else 'Not Available'}")

# Test if serverless limitations are detected
serverless_features = env_info.get('serverless_features', {})
if serverless_features:
    print(f"\n=== Serverless Features ===")
    for feature, enabled in serverless_features.items():
        print(f"  - {feature}: {enabled}")

# COMMAND ----------

# Debug cell - Check converter selector and fallback chain
from pyforge_cli.extensions.databricks.converter_selector import ConverterType
from pathlib import Path

print("DEBUG - Converter Selector Test:")
test_input = Path("/tmp/test.csv")
test_output_format = "parquet"
test_options = {}

try:
    recommendation = forge.converter_selector.select_converter(
        test_input, test_output_format, test_options
    )
    print(f"\nRecommended converter: {recommendation.converter_type.value}")
    print(f"Confidence: {recommendation.confidence:.2f}")
    print(f"Reasons: {recommendation.reasons}")
    print(f"Fallback options: {[c.value for c in recommendation.fallback_options]}")
except Exception as e:
    print(f"Error in converter selection: {e}")
    import traceback
    traceback.print_exc()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Download ALL Available Sample Datasets

# COMMAND ----------

# Helper function for file validation
def validate_file_exists(file_path: str) -> bool:
    """Validate that a file exists using dbutils.fs."""
    try:
        # Use dbutils.fs for all paths in Databricks
        dbutils.fs.ls(file_path)
        return True
    except Exception:
        return False

# COMMAND ----------

# Check if datasets already exist
datasets_exist = False
try:
    # For Volume paths, we need to check with dbutils
    if sample_datasets_path.startswith('/Volumes/'):
        try:
            files = dbutils.fs.ls(sample_datasets_path)
            # Check if there are actual data files (not just directories)
            for file_info in files:
                if file_info.name in ['csv/', 'excel/', 'xml/', 'access/', 'dbf/', 'pdf/']:
                    datasets_exist = True
                    break
        except:
            datasets_exist = False
    else:
        # For local paths, still use dbutils.fs in Databricks
        try:
            files = dbutils.fs.ls(sample_datasets_path)
            datasets_exist = len(files) > 0
        except:
            datasets_exist = False
except:
    datasets_exist = False

print("Dataset Status:")
print(f"  Path: {sample_datasets_path}")
print(f"  Exists: {datasets_exist}")
print(f"  Force Download: {force_download}")
print("=" * 60)

# Handle force download
if force_download and datasets_exist:
    print("Force download enabled. Removing existing datasets...")
    try:
        if sample_datasets_path.startswith('/Volumes/'):
            # Use dbutils for Volume paths
            dbutils.fs.rm(sample_datasets_path, recurse=True)
            print("✓ Removed existing datasets from Volume")
        else:
            # Use shutil for local paths
            import shutil
            shutil.rmtree(sample_datasets_path)
            print("✓ Removed existing datasets from local path")
        datasets_exist = False
    except Exception as e:
        print(f"✗ Error removing existing datasets: {e}")

# Download datasets if needed
if not datasets_exist or force_download:
    print("\nDownloading sample datasets...")
    print("=" * 60)
    
    # Initialize the sample datasets installer
    installer = SampleDatasetsInstaller(target_dir=Path(sample_datasets_path))
    
    # First, check available releases
    print("Checking available releases...")
    releases = installer.list_available_releases()
    print(f"Found {len(releases)} releases")
    
    if releases:
        # Show latest release info
        latest = releases[0]
        print(f"\nLatest release: {latest.get('tag_name', 'Unknown')}")
        assets = latest.get('assets', [])
        zip_assets = [a for a in assets if a['name'].endswith('.zip')]
        print(f"ZIP assets in latest release: {len(zip_assets)}")
        
        if zip_assets:
            for asset in zip_assets[:5]:  # Show first 5
                print(f"  - {asset['name']} ({asset['size'] / (1024*1024):.1f} MB)")
    
    # Install all datasets (no format or size filters)
    print("\nInstalling datasets...")
    try:
        install_result = installer.install_datasets(
            version="v1.0.5",  # Use v1.0.5 which has all the datasets
            formats=None,      # Download all formats
            sizes=None,        # All sizes
            force=True         # Force overwrite if exists
        )
        
        if install_result:
            print("✓ Sample datasets installed successfully")
        else:
            print("✗ Failed to install sample datasets")
            print("Note: The installer may have created minimal datasets locally.")
    except Exception as e:
        print(f"✗ Error during installation: {e}")
        print("Creating minimal datasets locally instead...")
        
        # Create minimal datasets as fallback
        try:
            if sample_datasets_path.startswith('/Volumes/'):
                # For Volume paths, use dbutils.fs operations
                print("Creating minimal datasets in Databricks Volume...")
                
                # Create CSV content
                csv_content = """id,name,category,value,date
1,Sample Item 1,Category A,100.50,2023-01-01
2,Sample Item 2,Category B,250.75,2023-01-02
3,Sample Item 3,Category A,175.25,2023-01-03
4,Sample Item 4,Category C,90.00,2023-01-04
5,Sample Item 5,Category B,320.80,2023-01-05"""
                
                # Create XML content - Enhanced with more data for better testing
                xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <books>
        <book id="1" category="fiction">
            <title>The Great Adventure</title>
            <author>John Smith</author>
            <price currency="USD">29.99</price>
            <publication_date>2023-01-01</publication_date>
            <pages>324</pages>
            <description>An exciting tale of discovery and friendship.</description>
        </book>
        <book id="2" category="science">
            <title>Understanding Quantum Physics</title>
            <author>Dr. Jane Wilson</author>
            <price currency="USD">49.95</price>
            <publication_date>2023-02-15</publication_date>
            <pages>485</pages>
            <description>A comprehensive guide to quantum mechanics.</description>
        </book>
        <book id="3" category="history">
            <title>Ancient Civilizations</title>
            <author>Prof. Robert Brown</author>
            <price currency="USD">39.50</price>
            <publication_date>2023-03-10</publication_date>
            <pages>256</pages>
            <description>Exploring the mysteries of ancient cultures.</description>
        </book>
        <book id="4" category="technology">
            <title>Machine Learning Fundamentals</title>
            <author>Sarah Davis</author>
            <price currency="USD">55.00</price>
            <publication_date>2023-04-20</publication_date>
            <pages>612</pages>
            <description>A practical approach to machine learning algorithms.</description>
        </book>
        <book id="5" category="fiction">
            <title>Space Odyssey 2024</title>
            <author>Michael Chen</author>
            <price currency="USD">34.99</price>
            <publication_date>2023-05-05</publication_date>
            <pages>398</pages>
            <description>A thrilling journey through the cosmos.</description>
        </book>
    </books>
    <metadata>
        <total_books>5</total_books>
        <last_updated>2023-06-01</last_updated>
        <version>1.0</version>
    </metadata>
</catalog>"""
                
                # Write CSV file to Volume
                csv_path = f"{sample_datasets_path.rstrip('/')}/csv/small/sample_data.csv"
                dbutils.fs.put(csv_path, csv_content, overwrite=True)
                print(f"✓ Created CSV: {csv_path}")
                
                # Write XML file to Volume
                xml_path = f"{sample_datasets_path.rstrip('/')}/xml/small/sample_data.xml"
                dbutils.fs.put(xml_path, xml_content, overwrite=True)
                print(f"✓ Created XML: {xml_path}")
                
                # Also create a larger XML file for performance testing
                large_xml_content = xml_content
                # Duplicate the books section multiple times to make it larger
                books_section = xml_content[xml_content.find('<books>'):xml_content.find('</books>') + 8]
                large_books = ""
                for i in range(20):  # Create 100 books (5 * 20)
                    # Modify book IDs to make them unique
                    id_offset = i * 5 + 1
                    modified_books = books_section.replace('<book id="', f'<book id="{id_offset}')
                    large_books += modified_books.replace('<books>', '').replace('</books>', '')
                
                large_xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <books>
{large_books}
    </books>
    <metadata>
        <total_books>100</total_books>
        <last_updated>2023-06-01</last_updated>
        <version>1.0</version>
    </metadata>
</catalog>"""
                
                large_xml_path = f"{sample_datasets_path.rstrip('/')}/xml/large/books_catalog.xml"
                dbutils.fs.put(large_xml_path, large_xml_content, overwrite=True)
                print(f"✓ Created large XML: {large_xml_path}")
                
                print("✓ Created minimal and large sample datasets in Volume")
                
            else:
                # For local paths, use standard file operations
                print("Creating minimal datasets locally...")
                
                # Create directory structure
                csv_dir = Path(sample_datasets_path) / "csv" / "small"
                csv_dir.mkdir(parents=True, exist_ok=True)
                
                # Create a simple CSV sample
                sample_csv = csv_dir / "sample_data.csv"
                csv_content = """id,name,category,value,date
1,Sample Item 1,Category A,100.50,2023-01-01
2,Sample Item 2,Category B,250.75,2023-01-02
3,Sample Item 3,Category A,175.25,2023-01-03
4,Sample Item 4,Category C,90.00,2023-01-04
5,Sample Item 5,Category B,320.80,2023-01-05"""
                
                with open(sample_csv, "w", encoding="utf-8") as f:
                    f.write(csv_content)
                
                # Create XML directory and sample
                xml_dir = Path(sample_datasets_path) / "xml" / "small"
                xml_dir.mkdir(parents=True, exist_ok=True)
                
                sample_xml = xml_dir / "sample_data.xml"
                xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<data>
    <items>
        <item id="1">
            <name>Sample Item 1</name>
            <category>Category A</category>
            <value>100.50</value>
            <date>2023-01-01</date>
        </item>
        <item id="2">
            <name>Sample Item 2</name>
            <category>Category B</category>
            <value>250.75</value>
            <date>2023-01-02</date>
        </item>
    </items>
</data>"""
                
                with open(sample_xml, "w", encoding="utf-8") as f:
                    f.write(xml_content)
                
                print("✓ Created minimal sample datasets locally")
        except Exception as e2:
            print(f"✗ Failed to create minimal datasets: {e2}")
else:
    print("\nDatasets already exist. Skipping download.")
    print("To force re-download, set 'Force Download Datasets' to 'yes'")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5b. Alternative: Download Sample Datasets Using CLI (if installer fails)

# COMMAND ----------

# Alternative approach using subprocess if the installer has issues
import subprocess

# Check if we need to use the CLI approach using dbutils
try:
    # Check if directory exists and has content
    files = dbutils.fs.ls(sample_datasets_path)
    has_content = len(files) > 0
except:
    has_content = False

if not has_content:
    print("Attempting to download sample datasets using PyForge CLI...")
    try:
        # Run pyforge install sample-datasets command
        result = subprocess.run(
            ["pyforge", "install", "sample-datasets", "--path", sample_datasets_path, "--force"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Sample datasets downloaded successfully via CLI")
            print(result.stdout)
        else:
            print("✗ CLI download failed")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"✗ Could not run PyForge CLI: {e}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Discover and Display All Downloaded Datasets

# COMMAND ----------

def discover_datasets(base_path: str) -> Dict[str, List[Dict[str, any]]]:
    """Discover all datasets and organize by file type."""
    datasets_by_type = {}
    
    try:
        # Check if path exists
        try:
            dbutils.fs.ls(base_path)
        except Exception as e:
            print(f"Cannot access path {base_path}: {e}")
            return datasets_by_type
            
        # Use dbutils.fs to recursively walk through Volume directories
        def walk_directory(path: str, relative_base: str = ""):
            try:
                items = dbutils.fs.ls(path)
                for item in items:
                    item_name = item.name.rstrip('/')  # Remove trailing slash from dirs
                    item_path = item.path
                    
                    if item.isDir():
                        # Recursively walk subdirectories
                        new_relative = os.path.join(relative_base, item_name) if relative_base else item_name
                        walk_directory(item_path, new_relative)
                    else:
                        # Process file
                        if item_name.startswith('.') or item_name in ['manifest.json', 'checksums.sha256', 'README.md']:
                            continue
                            
                        file_ext = os.path.splitext(item_name)[1].lower().lstrip('.')
                        
                        if file_ext:  # Only process files with extensions
                            if file_ext not in datasets_by_type:
                                datasets_by_type[file_ext] = []
                            
                            relative_path = os.path.join(relative_base, item_name) if relative_base else item_name
                            
                            datasets_by_type[file_ext].append({
                                'name': item_name,
                                'path': item_path,
                                'size_bytes': item.size,
                                'size_mb': item.size / (1024 * 1024),
                                'relative_path': relative_path
                            })
            except Exception as e:
                print(f"Error walking directory {path}: {e}")
        
        # Start walking from base path
        walk_directory(base_path)
        
        # Sort each type by size
        for file_type in datasets_by_type:
            datasets_by_type[file_type].sort(key=lambda x: x['size_bytes'])
            
    except Exception as e:
        print(f"Error discovering datasets: {e}")
    
    return datasets_by_type

# Discover all datasets
print("Discovering all downloaded datasets...")
datasets_by_type = discover_datasets(sample_datasets_path)

# Display summary
print(f"\nFound datasets for {len(datasets_by_type)} file types:")
print("=" * 80)
print(f"{'File Type':<10} {'Count':<8} {'Total Size (MB)':<15} {'Smallest (MB)':<15} {'Largest (MB)':<15}")
print("-" * 80)

for file_type, files in sorted(datasets_by_type.items()):
    total_size = sum(f['size_mb'] for f in files)
    smallest = files[0]['size_mb'] if files else 0
    largest = files[-1]['size_mb'] if files else 0
    
    print(f"{file_type:<10} {len(files):<8} {total_size:<15.2f} {smallest:<15.2f} {largest:<15.2f}")

print("=" * 80)

# Display all files with sizes if verbose
if verbose:
    print("\nDetailed file listing:")
    for file_type, files in sorted(datasets_by_type.items()):
        print(f"\n{file_type.upper()} Files ({len(files)} total):")
        print("-" * 60)
        for file in files:
            print(f"  {file['relative_path']:<40} {file['size_mb']:>10.2f} MB")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Select Smallest File of Each Type for Testing

# COMMAND ----------

# Hard-coded smallest files of each type based on actual dataset analysis
# Use proper Volume path construction (no os.path.join for Volume paths)
def build_volume_path(base_path: str, *parts: str) -> str:
    """Build Volume path by joining with forward slashes."""
    path = base_path.rstrip('/')
    for part in parts:
        path += '/' + part.strip('/')
    return path

# Define test files with primary and fallback options
test_files_config = {
    'csv': [
        {
            'name': 'titanic-dataset.csv',
            'path': build_volume_path(sample_datasets_path, 'csv/small/titanic-dataset.csv'),
            'size_bytes': 61440,
            'size_mb': 0.06
        },
        {
            'name': 'sample_data.csv',
            'path': build_volume_path(sample_datasets_path, 'csv/small/sample_data.csv'),
            'size_bytes': 400,
            'size_mb': 0.0004
        }
    ],
    'xlsx': [
        {
            'name': 'financial-sample.xlsx', 
            'path': build_volume_path(sample_datasets_path, 'excel/small/financial-sample.xlsx'),
            'size_bytes': 83968,
            'size_mb': 0.08
        }
    ],
    'xml': [
        {
            'name': 'books_catalog.xml',
            'path': build_volume_path(sample_datasets_path, 'xml/large/books_catalog.xml'),
            'size_bytes': 15000,  # Estimated size for large XML
            'size_mb': 0.015
        },
        {
            'name': 'sample_data.xml',
            'path': build_volume_path(sample_datasets_path, 'xml/small/sample_data.xml'),
            'size_bytes': 2000,  # Estimated size for enhanced XML
            'size_mb': 0.002
        }
    ],
    'mdb': [
        {
            'name': 'sample_dibi.mdb',
            'path': build_volume_path(sample_datasets_path, 'access/small/sample_dibi.mdb'),
            'size_bytes': 290816,
            'size_mb': 0.28
        }
    ],
    'accdb': [
        {
            'name': 'Northwind_2007_VBNet.accdb',
            'path': build_volume_path(sample_datasets_path, 'access/small/Northwind_2007_VBNet.accdb'),
            'size_bytes': 3670016,
            'size_mb': 3.5
        }
    ],
    'dbf': [
        {
            'name': 'tl_2024_01_place.dbf',
            'path': build_volume_path(sample_datasets_path, 'dbf/small/tl_2024_01_place.dbf'),
            'size_bytes': 179200,
            'size_mb': 0.17
        }
    ],
    'pdf': [
        {
            'name': 'NIST-CSWP-04162018.pdf',
            'path': build_volume_path(sample_datasets_path, 'pdf/small/NIST-CSWP-04162018.pdf'),
            'size_bytes': 1048576,
            'size_mb': 1.0
        }
    ]
}

# Function to find the first available file for each type
def find_available_test_files():
    """Find the first available file for each type from the config."""
    test_files = {}
    
    for file_type, candidates in test_files_config.items():
        for candidate in candidates:
            file_path = candidate['path']
            if validate_file_exists(file_path):
                test_files[file_type] = candidate
                print(f"✓ Found {file_type.upper()}: {candidate['name']} ({candidate['size_mb']:.3f} MB)")
                break
        else:
            print(f"✗ No {file_type.upper()} files found from candidates")
    
    return test_files

# Find available test files
print("\nDiscovering available test files...")
print("=" * 60)
test_files = find_available_test_files()

if not test_files:
    print("\n⚠️  No test files found! This might indicate:")
    print("  1. Sample datasets failed to download/install")
    print("  2. File paths are incorrect")
    print("  3. Minimal dataset creation failed")
    print("\nLet's create them manually...")
    
    # Force creation of minimal datasets
    try:
        if sample_datasets_path.startswith('/Volumes/'):
            # Create the essential test files
            csv_content = """id,name,category,value,date
1,Sample Item 1,Category A,100.50,2023-01-01
2,Sample Item 2,Category B,250.75,2023-01-02"""
            
            xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <books>
        <book id="1" category="fiction">
            <title>Test Book</title>
            <author>Test Author</author>
            <price>29.99</price>
        </book>
    </books>
</catalog>"""
            
            # Create CSV
            csv_path = f"{sample_datasets_path.rstrip('/')}/csv/small/sample_data.csv"
            dbutils.fs.put(csv_path, csv_content, overwrite=True)
            
            # Create XML  
            xml_path = f"{sample_datasets_path.rstrip('/')}/xml/small/sample_data.xml"
            dbutils.fs.put(xml_path, xml_content, overwrite=True)
            
            # Update test_files with created files
            test_files = {
                'csv': {
                    'name': 'sample_data.csv',
                    'path': csv_path,
                    'size_bytes': len(csv_content),
                    'size_mb': len(csv_content) / (1024*1024)
                },
                'xml': {
                    'name': 'sample_data.xml', 
                    'path': xml_path,
                    'size_bytes': len(xml_content),
                    'size_mb': len(xml_content) / (1024*1024)
                }
            }
            print("✓ Created minimal test files manually")
            
    except Exception as e:
        print(f"✗ Failed to create minimal test files: {e}")

print(f"\nFound {len(test_files)} test file types for conversion testing")

print("Selected test files (smallest of each type):")
print("=" * 60)
print(f"{'Type':<10} {'File Name':<35} {'Size':<10}")
print("-" * 60)

for file_type, file_info in sorted(test_files.items()):
    print(f"{file_type:<10} {file_info['name']:<35} {file_info['size_mb']:<10.2f} MB")

print("=" * 60)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 8. Test PyForge API: get_info()

# COMMAND ----------

print("Testing PyForge API: get_info()")
print("=" * 60)

info_results = {}

for file_type, file_info in test_files.items():
    print(f"\nTesting {file_type.upper()} file: {file_info['name']}")
    print("-" * 40)
    
    try:
        # Get file information using PyForge API
        file_path = file_info['path']
        info = forge.get_info(file_path)
        info_results[file_type] = info
        
        # Display key information
        print(f"✓ File exists: {info.get('exists', False)}")
        print(f"  Format: {info.get('format', 'Unknown')}")
        print(f"  Size: {info.get('size', 0) / (1024*1024):.2f} MB")
        
        # Format-specific information
        if 'sheets' in info:
            print(f"  Sheets: {info['sheets']}")
        if 'encoding' in info:
            print(f"  Encoding: {info['encoding']}")
        if 'delimiter' in info:
            print(f"  Delimiter: {repr(info['delimiter'])}")
        if 'columns' in info:
            print(f"  Columns: {len(info['columns'])}")
            
    except Exception as e:
        print(f"✗ Error getting info: {e}")
        info_results[file_type] = {'error': str(e)}

# COMMAND ----------
# MAGIC %md
# MAGIC ## 9. Test PyForge API: validate()

# COMMAND ----------

print("Testing PyForge API: validate()")
print("=" * 60)

validation_results = {}

for file_type, file_info in test_files.items():
    print(f"\nValidating {file_type.upper()} file: {file_info['name']}")
    print("-" * 40)
    
    try:
        # Validate file using PyForge API
        file_path = file_info['path']
        validation = forge.validate(file_path)
        validation_results[file_type] = validation
        
        # Display validation results
        print(f"✓ Valid: {validation.get('is_valid', False)}")
        
        if validation.get('issues'):
            print(f"  Issues: {validation['issues']}")
        if validation.get('warnings'):
            print(f"  Warnings: {validation['warnings']}")
            
    except Exception as e:
        print(f"✗ Error validating: {e}")
        validation_results[file_type] = {'error': str(e)}

# COMMAND ----------
# MAGIC %md
# MAGIC ## 10. Test PyForge API: convert()
# MAGIC ### Setting up output directory for all conversions

# COMMAND ----------

# Create output directory using configuration
if conversion_output_path.strip():
    # User provided custom output path
    output_dir = conversion_output_path.rstrip('/')
    print(f"Using custom output path: {output_dir}")
else:
    # Auto-generate output path based on sample datasets path
    if sample_datasets_path.startswith('/Volumes/'):
        # For Volume paths, create output in the same volume with /tmp suffix
        base_volume = sample_datasets_path.rstrip('/') 
        output_dir = f"{base_volume}/tmp/pyforge_conversions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        # For local paths, use /tmp
        output_dir = f"/tmp/pyforge_api_test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Auto-generated output path: {output_dir}")

print(f"Conversion output directory: {output_dir}")

# Create the output directory
try:
    if output_dir.startswith('/Volumes/'):
        # Use dbutils for Volume paths - just ensure parent exists, directories auto-create
        print(f"Will create Volume output directory: {output_dir}")
    else:
        # For local paths, create directory
        import os
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created local output directory: {output_dir}")
    # Ensure the directory exists for Volume paths
    if output_dir.startswith('/Volumes/'):
        try:
            dbutils.fs.mkdirs(output_dir)
            print(f"✓ Created Volume output directory: {output_dir}")
        except Exception as create_error:
            print(f"Note: Directory will be created during conversion: {create_error}")
except Exception as e:
    print(f"Note: Output directory creation will be handled during conversion: {e}")

print("=" * 60)

# Initialize results dictionary
conversion_results = {}

# Helper function to validate conversion results
def validate_conversion_result(result, output_path, file_type):
    """Validate that conversion was successful and output file exists."""
    if not result.get('success'):
        return False, f"Conversion failed: {result.get('error', 'Unknown error')}"
    
    # Check if output file exists
    actual_output = result.get('output_path', output_path)
    
    try:
        if actual_output.startswith('/Volumes/'):
            # Use dbutils for Volume paths
            try:
                file_info = dbutils.fs.ls(actual_output)
                if file_info:
                    return True, f"✓ Output file verified: {actual_output}"
                else:
                    return False, f"✗ Output file not found: {actual_output}"
            except Exception as e:
                return False, f"✗ Error checking output file: {e}"
        else:
            # Still use dbutils for all paths in Databricks
            try:
                file_info = dbutils.fs.ls(actual_output)
                if file_info:
                    size = file_info[0].size if hasattr(file_info[0], 'size') else 'unknown'
                    return True, f"✓ Output file verified: {actual_output} ({size} bytes)"
                else:
                    return False, f"✗ Output file not found: {actual_output}"
            except Exception as e:
                return False, f"✗ Error checking output file: {e}"
    except Exception as e:
        return False, f"✗ Error validating output: {e}"

# Helper function to display conversion results
def display_conversion_results(result, output_path, file_path, duration, file_type):
    """Display standardized conversion results with validation."""
    # Validate conversion result
    is_valid, validation_msg = validate_conversion_result(result, output_path, file_type)
    
    # Display results
    if result.get('success'):
        print(f"✓ Conversion successful")
        print(f"  Input: {file_path}")
        print(f"  Output: {result.get('output_path', output_path)}")
        print(f"  Converter: {result.get('converter_used', 'Unknown')}")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Rows: {result.get('rows_processed', 'Unknown')}")
        print(f"  Validation: {validation_msg}")
        
        # Try to get output file size
        try:
            actual_output = result.get('output_path', output_path)
            if actual_output.startswith('/Volumes/'):
                # Get size from dbutils for Volume files
                try:
                    file_info = dbutils.fs.ls(actual_output)
                    if file_info and hasattr(file_info[0], 'size'):
                        size_bytes = file_info[0].size
                        print(f"  Output size: {size_bytes / (1024*1024):.2f} MB")
                    elif file_info:
                        print(f"  Output size: File exists (size unknown)")
                except Exception as size_error:
                    print(f"  Output size: Could not determine ({size_error})")
            else:
                # Still use dbutils for all paths in Databricks
                try:
                    file_info = dbutils.fs.ls(actual_output)
                    if file_info and hasattr(file_info[0], 'size'):
                        size_bytes = file_info[0].size
                        print(f"  Output size: {size_bytes / (1024*1024):.2f} MB")
                    else:
                        print(f"  Output size: File exists (size unknown)")
                except Exception as size_error:
                    print(f"  Output size: Could not determine ({size_error})")
        except Exception as e:
            print(f"  Output size: Error getting size ({e})")
            
        # Additional metadata if available
        if result.get('warnings'):
            print(f"  Warnings: {result['warnings']}")
    else:
        print(f"✗ Conversion failed")
        print(f"  Input: {file_path}")
        print(f"  Expected output: {output_path}")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Validation: {validation_msg}")
        
        # Show fallback attempts if available
        if result.get('fallback_history'):
            print(f"  Fallback attempts: {len(result['fallback_history'])}")
            for i, attempt in enumerate(result['fallback_history'][:3], 1):  # Show first 3
                print(f"    {i}. {attempt.get('converter', 'Unknown')}: {attempt.get('error', 'Unknown error')}")
    
    return is_valid


# COMMAND ----------
# MAGIC %md
# MAGIC ### 10a. Convert CSV to Parquet

# COMMAND ----------

print("Testing CSV to Parquet conversion")
print("=" * 60)

file_type = 'csv'
file_info = test_files[file_type]
target_format = 'parquet'

print(f"Input file: {file_info['name']} ({file_info['size_mb']:.2f} MB)")
print(f"Target format: {target_format}")
print("-" * 40)

try:
    # Prepare paths
    file_path = file_info['path']
    output_filename = f"{Path(file_info['name']).stem}.{target_format}"
    output_path = f"{output_dir}/{output_filename}"
    
    # Convert using PyForge API
    start_time = datetime.now()
    result = forge.convert(
        input_path=file_path,
        output_path=output_path,
        format=target_format
    )
    duration = (datetime.now() - start_time).total_seconds()
    
    conversion_results[file_type] = result
    
    # Display results using helper function
    is_valid = display_conversion_results(result, output_path, file_path, duration, file_type)
        
except Exception as e:
    print(f"✗ Error during conversion: {e}")
    conversion_results[file_type] = {'error': str(e)}

# COMMAND ----------
# MAGIC %md
# MAGIC ### 10b. Convert Excel to Parquet

# COMMAND ----------

print("Testing Excel to Parquet conversion")
print("=" * 60)

file_type = 'xlsx'
if file_type not in test_files:
    print(f"⚠️  No {file_type.upper()} test file available, skipping conversion test")
else:
    file_info = test_files[file_type]
    target_format = 'parquet'

    print(f"Input file: {file_info['name']} ({file_info['size_mb']:.2f} MB)")
    print(f"Target format: {target_format}")
    print("-" * 40)

    try:
        # Prepare paths
        file_path = file_info['path']
        output_filename = f"{Path(file_info['name']).stem}.{target_format}"
        output_path = f"{output_dir}/{output_filename}"
        
        # Convert using PyForge API
        start_time = datetime.now()
        result = forge.convert(
            input_path=file_path,
            output_path=output_path,
            format=target_format
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        conversion_results[file_type] = result
        
        # Display results using helper function
        is_valid = display_conversion_results(result, output_path, file_path, duration, file_type)
        
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        conversion_results[file_type] = {'error': str(e)}

# COMMAND ----------
# MAGIC %md
# MAGIC ### 10c. Convert XML to Parquet

# COMMAND ----------

print("Testing XML to Parquet conversion")
print("=" * 60)

file_type = 'xml'
if file_type not in test_files:
    print(f"⚠️  No {file_type.upper()} test file available, skipping conversion test")
else:
    file_info = test_files[file_type]
    target_format = 'parquet'

    print(f"Input file: {file_info['name']} ({file_info['size_mb']:.2f} MB)")
    print(f"Target format: {target_format}")
    print("-" * 40)

    try:
        # Prepare paths
        file_path = file_info['path']
        output_filename = f"{Path(file_info['name']).stem}.{target_format}"
        output_path = f"{output_dir}/{output_filename}"
        
        # Convert using PyForge API
        start_time = datetime.now()
        result = forge.convert(
            input_path=file_path,
            output_path=output_path,
            format=target_format
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        conversion_results[file_type] = result
        
        # Display results using helper function
        is_valid = display_conversion_results(result, output_path, file_path, duration, file_type)
        
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        conversion_results[file_type] = {'error': str(e)}

# COMMAND ----------
# MAGIC %md
# MAGIC ### 10d. Convert MDB/Access to Parquet

# COMMAND ----------

print("Testing MDB/Access to Parquet conversion")
print("=" * 60)

# Test both MDB and ACCDB formats
for file_type in ['mdb', 'accdb']:
    if file_type in test_files:
        file_info = test_files[file_type]
        target_format = 'parquet'
        
        print(f"\nTesting {file_type.upper()} file: {file_info['name']} ({file_info['size_mb']:.2f} MB)")
        print(f"Target format: {target_format}")
        print("-" * 40)
        
        try:
            # Prepare paths
            file_path = file_info['path']
            output_filename = f"{Path(file_info['name']).stem}.{target_format}"
            output_path = f"{output_dir}/{output_filename}"
            
            # Convert using PyForge API
            start_time = datetime.now()
            result = forge.convert(
                input_path=file_path,
                output_path=output_path,
                format=target_format
            )
            duration = (datetime.now() - start_time).total_seconds()
            
            conversion_results[file_type] = result
            
            # Display results using helper function
            is_valid = display_conversion_results(result, output_path, file_path, duration, file_type)
                
        except Exception as e:
            print(f"✗ Error during conversion: {e}")
            conversion_results[file_type] = {'error': str(e)}

# COMMAND ----------
# MAGIC %md
# MAGIC ### 10e. Convert DBF to Parquet

# COMMAND ----------

print("Testing DBF to Parquet conversion")
print("=" * 60)

file_type = 'dbf'
if file_type not in test_files:
    print(f"⚠️  No {file_type.upper()} test file available, skipping conversion test")
else:
    file_info = test_files[file_type]
    target_format = 'parquet'

    print(f"Input file: {file_info['name']} ({file_info['size_mb']:.2f} MB)")
    print(f"Target format: {target_format}")
    print("-" * 40)

    try:
        # Prepare paths
        file_path = file_info['path']
        output_filename = f"{Path(file_info['name']).stem}.{target_format}"
        output_path = f"{output_dir}/{output_filename}"
        
        # Convert using PyForge API
        start_time = datetime.now()
        result = forge.convert(
            input_path=file_path,
            output_path=output_path,
            format=target_format
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        conversion_results[file_type] = result
        
        # Display results using helper function
        is_valid = display_conversion_results(result, output_path, file_path, duration, file_type)
        
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        conversion_results[file_type] = {'error': str(e)}

# COMMAND ----------
# MAGIC %md
# MAGIC ### 10f. Convert PDF to Parquet

# COMMAND ----------

print("Testing PDF to Parquet conversion")
print("=" * 60)

file_type = 'pdf'
if file_type not in test_files:
    print(f"⚠️  No {file_type.upper()} test file available, skipping conversion test")
else:
    file_info = test_files[file_type]
    target_format = 'parquet'

    print(f"Input file: {file_info['name']} ({file_info['size_mb']:.2f} MB)")
    print(f"Target format: {target_format}")
    print("-" * 40)

    try:
        # Prepare paths
        file_path = file_info['path']
        output_filename = f"{Path(file_info['name']).stem}.{target_format}"
        output_path = f"{output_dir}/{output_filename}"
        
        # Convert using PyForge API
        start_time = datetime.now()
        result = forge.convert(
            input_path=file_path,
            output_path=output_path,
            format=target_format
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        conversion_results[file_type] = result
        
        # Display results using helper function
        is_valid = display_conversion_results(result, output_path, file_path, duration, file_type)
        
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        conversion_results[file_type] = {'error': str(e)}

# COMMAND ----------
# MAGIC %md
# MAGIC ## 11. Summary Results

# COMMAND ----------

print("=" * 80)
print("API TESTING SUMMARY")
print("=" * 80)

# Dataset summary
total_files = sum(len(files) for files in datasets_by_type.values())
total_size = sum(f['size_mb'] for files in datasets_by_type.values() for f in files)

print(f"\nDatasets Downloaded:")
print(f"  Total files: {total_files}")
print(f"  Total size: {total_size:.2f} MB")
print(f"  File types: {len(datasets_by_type)}")

# API test summary
print(f"\nAPI Tests Performed:")
print(f"  Files tested: {len(test_files)}")

# Info API results
info_success = sum(1 for r in info_results.values() if 'error' not in r)
print(f"\nget_info() Results:")
print(f"  Successful: {info_success}/{len(info_results)}")

# Validation API results
valid_success = sum(1 for r in validation_results.values() if r.get('is_valid', False))
print(f"\nvalidate() Results:")
print(f"  Valid files: {valid_success}/{len(validation_results)}")

# Conversion API results
convert_success = sum(1 for r in conversion_results.values() if r.get('success', False))
print(f"\nconvert() Results:")
print(f"  Successful: {convert_success}/{len(conversion_results)}")

# Detailed results by file type
print("\nDetailed Results by File Type:")
print("-" * 80)
print(f"{'Type':<10} {'Info':<10} {'Valid':<10} {'Convert':<10} {'Notes':<30}")
print("-" * 80)

for file_type in sorted(test_files.keys()):
    info_ok = '✓' if 'error' not in info_results.get(file_type, {}) else '✗'
    valid_ok = '✓' if validation_results.get(file_type, {}).get('is_valid', False) else '✗'
    convert_ok = '✓' if conversion_results.get(file_type, {}).get('success', False) else '✗'
    
    # Gather notes
    notes = []
    if 'error' in info_results.get(file_type, {}):
        notes.append("Info error")
    if conversion_results.get(file_type, {}).get('converter_used'):
        notes.append(f"Used {conversion_results[file_type]['converter_used']}")
    
    print(f"{file_type:<10} {info_ok:<10} {valid_ok:<10} {convert_ok:<10} {', '.join(notes):<30}")

print("=" * 80)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 12. Cleanup (Optional)

# COMMAND ----------

# Clean up output directory if needed
cleanup = False  # Set to True to cleanup

if cleanup:
    print("Cleaning up test outputs...")
    try:
        # Use dbutils for cleanup if it's a DBFS path
        if output_dir.startswith("/tmp/") or output_dir.startswith("dbfs:/"):
            dbutils.fs.rm(output_dir, recurse=True)
            print(f"✓ Removed output directory: {output_dir}")
        else:
            # For local directories, use shutil
            shutil.rmtree(output_dir)
            print(f"✓ Removed output directory: {output_dir}")
    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
else:
    print(f"Test outputs preserved in: {output_dir}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Test Complete
# MAGIC
# MAGIC The PyForge Databricks Extension API testing is complete. Review the results above to verify:
# MAGIC
# MAGIC 1. ✓ All sample datasets were downloaded
# MAGIC 2. ✓ Dataset information was displayed with sizes
# MAGIC 3. ✓ Smallest file of each type was selected for testing
# MAGIC 4. ✓ PyForge API methods (get_info, validate, convert) were tested
# MAGIC 5. ✓ Comprehensive results were displayed
# MAGIC
# MAGIC Next steps:
# MAGIC - Review any failed conversions for specific file type issues
# MAGIC - Test with larger files for performance benchmarking
# MAGIC - Verify converter selection matches expectations