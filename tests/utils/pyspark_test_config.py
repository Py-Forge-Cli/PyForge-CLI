"""
PySpark test configuration and utilities for local testing.

This module provides utilities to set up and configure PySpark for local testing
of the Databricks extension functionality.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import pytest
from unittest.mock import patch


def setup_java_home():
    """Set up JAVA_HOME for PySpark if not already set."""
    if "JAVA_HOME" not in os.environ:
        # Try to find Java installation
        possible_java_homes = [
            "/usr/lib/jvm/default-java",
            "/usr/lib/jvm/java-11-openjdk-amd64",
            "/usr/lib/jvm/java-8-openjdk-amd64",
            "/Library/Java/JavaVirtualMachines/adoptopenjdk-11.jdk/Contents/Home",
            "/Library/Java/JavaVirtualMachines/adoptopenjdk-8.jdk/Contents/Home",
            "/System/Library/Java/JavaVirtualMachines/1.8.0.jdk/Contents/Home",
        ]
        
        for java_home in possible_java_homes:
            if Path(java_home).exists():
                os.environ["JAVA_HOME"] = java_home
                break
        else:
            # If no Java found, use a placeholder (tests will skip)
            os.environ["JAVA_HOME"] = "/usr/lib/jvm/default-java"


def create_spark_session(app_name: str = "PyForgeTest", **spark_config):
    """Create a Spark session for testing."""
    try:
        # Set up Java
        setup_java_home()
        
        # Import PySpark (will be skipped if not available)
        from pyspark.sql import SparkSession
        from pyspark.conf import SparkConf
        
        # Base configuration for local testing
        config = {
            "spark.master": "local[2]",
            "spark.app.name": app_name,
            "spark.sql.adaptive.enabled": "false",
            "spark.sql.adaptive.coalescePartitions.enabled": "false",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            "spark.sql.warehouse.dir": str(Path(tempfile.gettempdir()) / "spark-warehouse"),
            "spark.driver.host": "localhost",
            "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
            "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            # Reduce logging
            "spark.sql.adaptive.logLevel": "WARN",
        }
        
        # Add custom config
        config.update(spark_config)
        
        # Create Spark configuration
        conf = SparkConf()
        for key, value in config.items():
            conf.set(key, value)
        
        # Create Spark session
        spark = SparkSession.builder.config(conf=conf).getOrCreate()
        
        # Set log level to reduce noise
        spark.sparkContext.setLogLevel("WARN")
        
        return spark
    
    except ImportError:
        pytest.skip("PySpark not available")
    except Exception as e:
        pytest.skip(f"Failed to create Spark session: {e}")


def cleanup_spark_session(spark):
    """Clean up Spark session after testing."""
    if spark:
        try:
            spark.stop()
        except:
            pass


class SparkTestCase:
    """Base class for Spark test cases."""
    
    @pytest.fixture(scope="class")
    def spark_session(self):
        """Provide a Spark session for testing."""
        spark = create_spark_session()
        yield spark
        cleanup_spark_session(spark)
    
    @pytest.fixture
    def temp_dir(self):
        """Provide a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)


def mock_databricks_imports():
    """Mock Databricks-specific imports for local testing."""
    
    # Mock dbutils
    mock_dbutils_module = """
from tests.utils.mock_dbutils import dbutils
"""
    
    # Create mock modules
    mock_modules = {
        'pyspark.dbutils': type(sys)('pyspark.dbutils'),
        'databricks.feature_store': type(sys)('databricks.feature_store'),
        'databricks.sdk': type(sys)('databricks.sdk'),
    }
    
    # Add dbutils to pyspark module
    from tests.utils.mock_dbutils import dbutils
    mock_modules['pyspark.dbutils'].dbutils = dbutils
    
    return mock_modules


def requires_pyspark(func):
    """Decorator to skip tests if PySpark is not available."""
    def wrapper(*args, **kwargs):
        try:
            import pyspark
            return func(*args, **kwargs)
        except ImportError:
            pytest.skip("PySpark not available")
    return wrapper


def requires_java(func):
    """Decorator to skip tests if Java is not available."""
    def wrapper(*args, **kwargs):
        setup_java_home()
        java_home = os.environ.get("JAVA_HOME", "")
        if not java_home or not Path(java_home).exists():
            pytest.skip("Java not available")
        return func(*args, **kwargs)
    return wrapper


def requires_delta(func):
    """Decorator to skip tests if Delta Lake is not available."""
    def wrapper(*args, **kwargs):
        try:
            import delta
            return func(*args, **kwargs)
        except ImportError:
            pytest.skip("Delta Lake not available")
    return wrapper


# Environment setup for PySpark tests
def setup_pyspark_test_environment():
    """Set up environment for PySpark testing."""
    
    # Set up Java
    setup_java_home()
    
    # Set PySpark Python executable
    if "PYSPARK_PYTHON" not in os.environ:
        os.environ["PYSPARK_PYTHON"] = sys.executable
    
    # Reduce Spark logging
    import logging
    logging.getLogger("py4j").setLevel(logging.WARNING)
    logging.getLogger("pyspark").setLevel(logging.WARNING)
    
    # Mock Databricks imports
    mock_modules = mock_databricks_imports()
    
    # Patch sys.modules
    for module_name, mock_module in mock_modules.items():
        sys.modules[module_name] = mock_module


# Pytest configuration
def pytest_configure():
    """Configure pytest for PySpark tests."""
    # Add custom markers
    pytest.mark.pyspark = pytest.mark.skipif(
        not _pyspark_available(), 
        reason="PySpark not available"
    )
    pytest.mark.databricks = pytest.mark.skipif(
        not _pyspark_available(), 
        reason="Databricks dependencies not available"
    )


def _pyspark_available():
    """Check if PySpark is available."""
    try:
        import pyspark
        return True
    except ImportError:
        return False


# Sample data generators for testing
def create_sample_dataframe(spark, data_type="mixed"):
    """Create sample DataFrames for testing."""
    if data_type == "mixed":
        data = [
            (1, "John Doe", 25, 50000.50, True),
            (2, "Jane Smith", 30, 60000.75, False),
            (3, "Bob Johnson", 35, 70000.00, True),
        ]
        columns = ["id", "name", "age", "salary", "is_active"]
    elif data_type == "numeric":
        data = [(i, i * 10, i * 100.5) for i in range(1, 101)]
        columns = ["id", "value", "amount"]
    elif data_type == "large":
        data = [(i, f"User_{i}", i % 100) for i in range(1, 10001)]
        columns = ["id", "username", "group_id"]
    else:
        raise ValueError(f"Unknown data type: {data_type}")
    
    return spark.createDataFrame(data, columns)


def assert_dataframes_equal(df1, df2, check_schema=True):
    """Assert that two DataFrames are equal."""
    if check_schema:
        assert df1.schema == df2.schema, f"Schemas differ: {df1.schema} vs {df2.schema}"
    
    # Convert to pandas for easier comparison
    pd1 = df1.toPandas().sort_values(by=df1.columns[0]).reset_index(drop=True)
    pd2 = df2.toPandas().sort_values(by=df2.columns[0]).reset_index(drop=True)
    
    assert pd1.equals(pd2), f"DataFrames differ:\n{pd1}\nvs\n{pd2}"