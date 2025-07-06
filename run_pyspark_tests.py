#!/usr/bin/env python3
"""
Run PySpark tests for PyForge CLI.
"""

import sys
import subprocess
from pathlib import Path

def main():
    # Set up environment
    import os
    os.environ.setdefault("JAVA_HOME", "/usr/lib/jvm/default-java")
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Run PySpark-specific tests
    pyspark_test_files = [
        "tests/test_pyspark_csv_converter.py",
        "tests/test_databricks_extension.py", 
        "tests/test_databricks_environment.py",
        "tests/test_extension_integration.py",
    ]
    
    # Filter to existing files
    existing_tests = [f for f in pyspark_test_files if Path(f).exists()]
    
    if not existing_tests:
        print("No PySpark test files found")
        return 1
    
    # Run tests
    cmd = [
        sys.executable, "-m", "pytest",
        "--override-ini=addopts=",  # Clear default options
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
    ] + existing_tests
    
    print(f"Running command: {' '.join(cmd)}")
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())
