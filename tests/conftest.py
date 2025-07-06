"""
Pytest configuration for PyForge CLI tests.

This module configures pytest for the test suite, including:
- Custom markers for test categorization
- PySpark test setup and teardown
- Mock dbutils for Databricks testing
- Environment configuration for CI/CD
"""

import os
import sys
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure environment for tests
os.environ.setdefault("PYARROW_IGNORE_TIMEZONE", "1")
os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "pyspark: mark test as requiring PySpark")
    config.addinivalue_line("markers", "databricks: mark test as Databricks-specific")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow-running")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Auto-mark PySpark tests
        if "pyspark" in item.nodeid.lower():
            item.add_marker(pytest.mark.pyspark)

        # Auto-mark Databricks tests
        if "databricks" in item.nodeid.lower():
            item.add_marker(pytest.mark.databricks)

        # Auto-mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def spark_session():
    """Provide a Spark session for tests that need it."""
    try:
        from pyspark.sql import SparkSession

        spark = (
            SparkSession.builder.appName("PyForgeTest")
            .master("local[1]")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.adaptive.enabled", "false")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "false")
            .getOrCreate()
        )

        yield spark

        spark.stop()
    except ImportError:
        pytest.skip("PySpark not available")


@pytest.fixture
def mock_dbutils():
    """Provide mock dbutils for Databricks tests."""
    # Import or create mock dbutils
    try:
        from tests.utils.mock_dbutils import dbutils

        return dbutils
    except ImportError:
        # Create a simple mock
        class MockDBUtils:
            class widgets:
                @staticmethod
                def text(name, default_value="", label=""):
                    pass

                @staticmethod
                def get(name):
                    return ""

            class fs:
                @staticmethod
                def ls(path):
                    return []

                @staticmethod
                def mkdirs(path):
                    return True

        return MockDBUtils()


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Automatically set up test environment for all tests."""
    # Clear any problematic environment variables
    if "SPARK_HOME" in os.environ:
        monkeypatch.delenv("SPARK_HOME", raising=False)

    # Set test environment variables
    monkeypatch.setenv("PYARROW_IGNORE_TIMEZONE", "1")
    monkeypatch.setenv("SPARK_LOCAL_IP", "127.0.0.1")

    # For CI environment, set additional configs
    if os.environ.get("CI") == "true":
        monkeypatch.setenv("PYSPARK_PYTHON", sys.executable)
        monkeypatch.setenv("PYSPARK_DRIVER_PYTHON", sys.executable)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-pyspark", action="store_true", default=False, help="run PySpark tests"
    )
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_runtest_setup(item):
    """Skip tests based on markers and command line options."""
    # PySpark tests now run by default since issues are fixed
    # No longer skipping PySpark tests

    # Skip slow tests unless explicitly requested
    if "slow" in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("need --run-slow option to run")


# Import mock dbutils into pyspark namespace for tests
try:
    # Create mock pyspark.dbutils module
    import types

    import pyspark

    from tests.utils.mock_dbutils import dbutils

    pyspark.dbutils = types.ModuleType("pyspark.dbutils")
    pyspark.dbutils.DBUtils = lambda spark: dbutils
except ImportError:
    # PySpark or mock_dbutils not available, skip
    pass
