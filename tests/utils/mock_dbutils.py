"""
Mock dbutils module for local PySpark testing.

This module provides a mock implementation of Databricks utilities (dbutils)
that can be used for local testing without requiring a Databricks environment.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import shutil


class MockWidgets:
    """Mock implementation of dbutils.widgets."""
    
    def __init__(self):
        self._widgets = {}
    
    def text(self, name: str, default_value: str = "", label: str = "") -> None:
        """Create a text widget."""
        self._widgets[name] = default_value
    
    def dropdown(self, name: str, default_value: str, choices: List[str], label: str = "") -> None:
        """Create a dropdown widget."""
        if default_value not in choices:
            choices.insert(0, default_value)
        self._widgets[name] = default_value
    
    def combobox(self, name: str, default_value: str, choices: List[str], label: str = "") -> None:
        """Create a combobox widget."""
        self._widgets[name] = default_value
    
    def multiselect(self, name: str, default_value: str, choices: List[str], label: str = "") -> None:
        """Create a multiselect widget."""
        self._widgets[name] = default_value
    
    def get(self, name: str) -> str:
        """Get widget value."""
        return self._widgets.get(name, "")
    
    def remove(self, name: str) -> None:
        """Remove a widget."""
        self._widgets.pop(name, None)
    
    def removeAll(self) -> None:
        """Remove all widgets."""
        self._widgets.clear()


class MockFS:
    """Mock implementation of dbutils.fs."""
    
    def __init__(self):
        self._temp_dir = Path(tempfile.mkdtemp(prefix="mock_dbfs_"))
        # Create some mock volume paths
        self._volume_paths = {
            "/Volumes/cortex_dev_catalog/sandbox_testing/": self._temp_dir / "volumes" / "cortex_dev_catalog" / "sandbox_testing",
            "/Volumes/": self._temp_dir / "volumes",
        }
        for path in self._volume_paths.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def _normalize_path(self, path: str) -> Path:
        """Normalize a DBFS/Volume path to local filesystem path."""
        if path.startswith("dbfs:/"):
            path = path[5:]  # Remove dbfs: prefix
        if path.startswith("/Volumes/"):
            for volume_prefix, local_path in self._volume_paths.items():
                if path.startswith(volume_prefix):
                    relative_path = path[len(volume_prefix):].lstrip("/")
                    return local_path / relative_path
        # Default to temp directory
        return self._temp_dir / path.lstrip("/")
    
    def ls(self, path: str) -> List[Dict[str, Any]]:
        """List files in a directory."""
        local_path = self._normalize_path(path)
        if not local_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        result = []
        if local_path.is_dir():
            for item in local_path.iterdir():
                result.append({
                    "path": f"{path.rstrip('/')}/{item.name}",
                    "name": item.name,
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modificationTime": int(item.stat().st_mtime * 1000),
                    "isDir": item.is_dir(),
                    "isFile": item.is_file()
                })
        return result
    
    def mkdirs(self, path: str) -> bool:
        """Create directories."""
        local_path = self._normalize_path(path)
        local_path.mkdir(parents=True, exist_ok=True)
        return True
    
    def cp(self, source: str, destination: str, recurse: bool = False) -> bool:
        """Copy files."""
        src_path = self._normalize_path(source)
        dst_path = self._normalize_path(destination)
        
        if src_path.is_file():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        elif src_path.is_dir() and recurse:
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        return True
    
    def rm(self, path: str, recurse: bool = False) -> bool:
        """Remove files or directories."""
        local_path = self._normalize_path(path)
        if local_path.exists():
            if local_path.is_file():
                local_path.unlink()
            elif local_path.is_dir() and recurse:
                shutil.rmtree(local_path)
        return True
    
    def head(self, path: str, max_bytes: int = 65536) -> str:
        """Read the first few bytes of a file."""
        local_path = self._normalize_path(path)
        if local_path.is_file():
            with open(local_path, 'rb') as f:
                content = f.read(max_bytes)
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    return content.decode('utf-8', errors='replace')
        return ""
    
    def put(self, path: str, content: str, overwrite: bool = False) -> bool:
        """Write content to a file."""
        local_path = self._normalize_path(path)
        if local_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {path}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True


class MockLibrary:
    """Mock implementation of dbutils.library."""
    
    def __init__(self):
        self._installed_libraries = set()
    
    def restartPython(self) -> None:
        """Mock restart Python (no-op in testing)."""
        pass
    
    def install(self, library: str) -> None:
        """Mock install library."""
        self._installed_libraries.add(library)
    
    def list(self) -> List[Dict[str, str]]:
        """List installed libraries."""
        return [{"library": lib} for lib in self._installed_libraries]


class MockSecrets:
    """Mock implementation of dbutils.secrets."""
    
    def __init__(self):
        self._secrets = {}
    
    def get(self, scope: str, key: str) -> str:
        """Get a secret value."""
        return self._secrets.get(f"{scope}/{key}", f"mock-secret-{key}")
    
    def list(self, scope: str) -> List[Dict[str, str]]:
        """List secrets in a scope."""
        return [{"key": key.split("/")[-1]} for key in self._secrets.keys() if key.startswith(f"{scope}/")]


class MockDBUtils:
    """Mock implementation of Databricks utilities."""
    
    def __init__(self):
        self.widgets = MockWidgets()
        self.fs = MockFS()
        self.library = MockLibrary()
        self.secrets = MockSecrets()
    
    def notebook_exit(self, value: str = "") -> None:
        """Mock notebook exit."""
        pass


# Global instance for easy importing
dbutils = MockDBUtils()


def setup_mock_databricks_environment():
    """Set up mock Databricks environment variables for testing."""
    mock_env = {
        "DATABRICKS_RUNTIME_VERSION": "13.3.x-scala2.12",
        "SPARK_HOME": "/databricks/spark",
        "PYTHONPATH": "/databricks/spark/python:/databricks/spark/python/lib/py4j-0.10.9.7-src.zip",
        "PYSPARK_PYTHON": "/databricks/python/bin/python",
        "JAVA_HOME": "/usr/lib/jvm/zulu8-ca-amd64",
    }
    
    for key, value in mock_env.items():
        os.environ[key] = value
    
    return mock_env


def setup_mock_serverless_environment():
    """Set up mock Databricks Serverless environment variables for testing."""
    mock_env = setup_mock_databricks_environment()
    mock_env.update({
        "DATABRICKS_RUNTIME_VERSION": "13.3.x-serverless-scala2.12",
        "DATABRICKS_SERVERLESS_COMPUTE": "true",
    })
    
    for key, value in mock_env.items():
        os.environ[key] = value
    
    return mock_env


def cleanup_mock_environment():
    """Clean up mock environment variables."""
    mock_keys = [
        "DATABRICKS_RUNTIME_VERSION",
        "DATABRICKS_SERVERLESS_COMPUTE", 
        "SPARK_HOME",
        "PYTHONPATH",
        "PYSPARK_PYTHON",
        "JAVA_HOME",
    ]
    
    for key in mock_keys:
        os.environ.pop(key, None)


def create_sample_datasets(dbutils_fs: MockFS):
    """Create sample datasets in the mock filesystem for testing."""
    # Create sample CSV data
    csv_content = """id,name,age,city
1,John Doe,25,New York
2,Jane Smith,30,Los Angeles
3,Bob Johnson,35,Chicago"""
    
    # Create sample XML data
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="1">
        <title>Python Programming</title>
        <author>John Doe</author>
        <price>29.99</price>
    </book>
    <book id="2">
        <title>Data Science Handbook</title>
        <author>Jane Smith</author>
        <price>39.99</price>
    </book>
</catalog>"""
    
    # Create sample JSON data
    json_content = """[
    {"id": 1, "product": "Laptop", "price": 999.99},
    {"id": 2, "product": "Phone", "price": 699.99},
    {"id": 3, "product": "Tablet", "price": 399.99}
]"""
    
    # Create datasets in mock Volume
    base_path = "/Volumes/cortex_dev_catalog/sandbox_testing/sample-datasets"
    
    dbutils_fs.put(f"{base_path}/csv/employees.csv", csv_content, overwrite=True)
    dbutils_fs.put(f"{base_path}/xml/catalog.xml", xml_content, overwrite=True)
    dbutils_fs.put(f"{base_path}/json/products.json", json_content, overwrite=True)
    
    return {
        "csv_path": f"{base_path}/csv/employees.csv",
        "xml_path": f"{base_path}/xml/catalog.xml", 
        "json_path": f"{base_path}/json/products.json"
    }