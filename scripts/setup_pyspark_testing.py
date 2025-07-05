#!/usr/bin/env python3
"""
Setup script for PySpark local testing environment.

This script installs the necessary dependencies and configures the environment
for running PySpark and Databricks extension tests locally.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def check_java_installation():
    """Check if Java is installed and accessible."""
    print("Checking Java installation...")
    
    try:
        result = run_command(["java", "-version"], check=False)
        if result.returncode == 0:
            print("✓ Java is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠ Java not found in PATH")
    return False


def suggest_java_installation():
    """Suggest Java installation commands based on the platform."""
    system = platform.system().lower()
    
    print("\nJava 8 or 11 is required for PySpark. Installation suggestions:")
    
    if system == "darwin":  # macOS
        print("For macOS:")
        print("  brew install openjdk@11")
        print("  # Or download from: https://adoptium.net/")
        
    elif system == "linux":
        print("For Ubuntu/Debian:")
        print("  sudo apt-get update")
        print("  sudo apt-get install openjdk-11-jdk")
        print("\nFor CentOS/RHEL:")
        print("  sudo yum install java-11-openjdk-devel")
        
    elif system == "windows":
        print("For Windows:")
        print("  Download and install from: https://adoptium.net/")
        print("  Or use chocolatey: choco install openjdk11")
    
    print("\nAfter installation, make sure JAVA_HOME is set:")
    print("  export JAVA_HOME=/path/to/java")
    print("  export PATH=$JAVA_HOME/bin:$PATH")


def install_pyspark_dependencies():
    """Install PySpark testing dependencies."""
    print("Installing PySpark testing dependencies...")
    
    # Install using the dependency group
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    
    # Try to install with dependency groups (newer pip)
    try:
        result = run_command(cmd + ["-e", ".[test-pyspark]"], check=False)
        if result.returncode == 0:
            print("✓ Installed with dependency groups")
            return True
    except:
        pass
    
    # Fallback: install individual packages
    print("Installing individual packages...")
    packages = [
        "pyspark==3.5.2",
        "delta-spark==3.1.0", 
        "databricks-sdk==0.19.0",
        "pytest>=8.3.5",
        "pytest-mock>=3.10.0",
        "pytest-cov>=5.0.0",
        "pytest-xdist>=3.0.0",
        "findspark>=2.0.1",
        "py4j>=0.10.9.7",
    ]
    
    for package in packages:
        try:
            result = run_command(cmd + [package], check=False)
            if result.returncode == 0:
                print(f"✓ Installed {package}")
            else:
                print(f"⚠ Failed to install {package}: {result.stderr}")
        except Exception as e:
            print(f"⚠ Error installing {package}: {e}")


def verify_pyspark_installation():
    """Verify that PySpark can be imported and used."""
    print("Verifying PySpark installation...")
    
    try:
        # Test basic PySpark import
        import pyspark
        print(f"✓ PySpark {pyspark.__version__} imported successfully")
        
        # Test SparkSession creation
        from pyspark.sql import SparkSession
        
        # Set minimal config for testing
        os.environ["JAVA_HOME"] = os.environ.get("JAVA_HOME", "/usr/lib/jvm/default-java")
        
        spark = SparkSession.builder \
            .appName("PySpark-Test") \
            .master("local[1]") \
            .config("spark.sql.adaptive.enabled", "false") \
            .getOrCreate()
        
        # Test basic operation
        data = [(1, "test"), (2, "data")]
        df = spark.createDataFrame(data, ["id", "value"])
        count = df.count()
        
        spark.stop()
        
        if count == 2:
            print("✓ PySpark basic functionality verified")
            return True
        else:
            print("⚠ PySpark test failed: unexpected row count")
            return False
            
    except ImportError as e:
        print(f"⚠ PySpark import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠ PySpark verification failed: {e}")
        return False


def verify_delta_lake():
    """Verify Delta Lake installation."""
    print("Verifying Delta Lake installation...")
    
    try:
        import delta
        print(f"✓ Delta Lake imported successfully")
        return True
    except ImportError as e:
        print(f"⚠ Delta Lake import failed: {e}")
        return False


def setup_environment_variables():
    """Set up environment variables for PySpark testing."""
    print("Setting up environment variables...")
    
    # Create a setup script
    script_content = """# PySpark Environment Setup
# Add this to your shell profile (.bashrc, .zshrc, etc.)

# Java (adjust path as needed)
export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/default-java}

# PySpark
export PYSPARK_PYTHON=${PYSPARK_PYTHON:-python3}
export PYSPARK_DRIVER_PYTHON=${PYSPARK_DRIVER_PYTHON:-python3}

# Reduce Spark logging (optional)
export SPARK_LOCAL_IP=127.0.0.1

# Add to PATH
export PATH=$JAVA_HOME/bin:$PATH
"""
    
    env_file = Path("pyspark_env_setup.sh")
    with open(env_file, "w") as f:
        f.write(script_content)
    
    print(f"✓ Environment setup script created: {env_file}")
    print("  Run: source pyspark_env_setup.sh")
    print("  Or add the contents to your shell profile")


def create_test_runner_script():
    """Create a script to run PySpark tests."""
    script_content = """#!/usr/bin/env python3
\"\"\"
Run PySpark tests for PyForge CLI.
\"\"\"

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
"""
    
    script_file = Path("run_pyspark_tests.py")
    with open(script_file, "w") as f:
        f.write(script_content)
    
    # Make executable
    script_file.chmod(0o755)
    
    print(f"✓ Test runner script created: {script_file}")
    print("  Run: python run_pyspark_tests.py")


def main():
    """Main setup function."""
    print("🚀 Setting up PySpark testing environment for PyForge CLI\n")
    
    # Check prerequisites
    java_ok = check_java_installation()
    if not java_ok:
        suggest_java_installation()
        print("\nPlease install Java and try again.")
        return 1
    
    # Install dependencies
    install_pyspark_dependencies()
    
    # Verify installation
    pyspark_ok = verify_pyspark_installation()
    delta_ok = verify_delta_lake()
    
    # Create helper scripts
    setup_environment_variables()
    create_test_runner_script()
    
    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    print(f"Java:           {'✓' if java_ok else '✗'}")
    print(f"PySpark:        {'✓' if pyspark_ok else '✗'}")
    print(f"Delta Lake:     {'✓' if delta_ok else '✗'}")
    
    if pyspark_ok:
        print("\n✅ PySpark testing environment is ready!")
        print("\nNext steps:")
        print("1. Run: source pyspark_env_setup.sh")
        print("2. Run: python run_pyspark_tests.py")
        print("3. Or run individual tests: pytest tests/test_pyspark_csv_converter.py -v")
        return 0
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())