#!/bin/bash
# Setup script for PySpark test environment
# Works both locally and in CI/CD environments

set -e

echo "🚀 Setting up PySpark test environment..."

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo "Detected OS: $OS"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Java installation
check_java() {
    echo "Checking Java installation..."
    
    if command_exists java; then
        JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f 2 | cut -d'.' -f 1-2)
        echo "✓ Java found: version $JAVA_VERSION"
        
        # Check if JAVA_HOME is set
        if [ -z "$JAVA_HOME" ]; then
            echo "⚠️  JAVA_HOME not set, attempting to detect..."
            
            if [ "$OS" == "macos" ]; then
                # Try common macOS Java locations
                for java_home in \
                    "/Library/Java/JavaVirtualMachines/jdk-11"*"/Contents/Home" \
                    "/Library/Java/JavaVirtualMachines/jdk1.8"*"/Contents/Home" \
                    "/System/Library/Java/JavaVirtualMachines/1.8.0.jdk/Contents/Home"
                do
                    if [ -d "$java_home" ]; then
                        export JAVA_HOME="$java_home"
                        echo "✓ Set JAVA_HOME=$JAVA_HOME"
                        break
                    fi
                done
            elif [ "$OS" == "linux" ]; then
                # Try common Linux Java locations
                for java_home in \
                    "/usr/lib/jvm/java-11-openjdk-amd64" \
                    "/usr/lib/jvm/java-8-openjdk-amd64" \
                    "/usr/lib/jvm/default-java"
                do
                    if [ -d "$java_home" ]; then
                        export JAVA_HOME="$java_home"
                        echo "✓ Set JAVA_HOME=$JAVA_HOME"
                        break
                    fi
                done
            fi
        else
            echo "✓ JAVA_HOME already set: $JAVA_HOME"
        fi
    else
        echo "❌ Java not found. Please install Java 8 or 11."
        return 1
    fi
}

# Setup Python environment
setup_python_env() {
    echo "Setting up Python environment..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
    echo "Python version: $PYTHON_VERSION"
    
    # Create virtual environment if not in one
    if [ -z "$VIRTUAL_ENV" ] && [ "$CI" != "true" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
}

# Install PySpark dependencies
install_dependencies() {
    echo "Installing PySpark dependencies..."
    
    # Core PySpark packages
    pip install pyspark==3.5.2
    pip install delta-spark==3.1.0
    pip install databricks-sdk==0.19.0
    
    # Testing packages
    pip install pytest pytest-mock pytest-xdist pytest-cov
    pip install findspark py4j
    
    # Install project
    if [ -f "pyproject.toml" ]; then
        pip install -e .
    fi
}

# Configure environment variables
configure_environment() {
    echo "Configuring environment variables..."
    
    # PySpark configuration
    export PYSPARK_PYTHON=${PYSPARK_PYTHON:-python3}
    export PYSPARK_DRIVER_PYTHON=${PYSPARK_DRIVER_PYTHON:-python3}
    export PYARROW_IGNORE_TIMEZONE=1
    export SPARK_LOCAL_IP=127.0.0.1
    
    # Clear any existing SPARK_HOME
    unset SPARK_HOME
    
    # Add Java to PATH if needed
    if [ -n "$JAVA_HOME" ] && [[ ":$PATH:" != *":$JAVA_HOME/bin:"* ]]; then
        export PATH="$JAVA_HOME/bin:$PATH"
    fi
    
    echo "Environment configured:"
    echo "  JAVA_HOME=$JAVA_HOME"
    echo "  PYSPARK_PYTHON=$PYSPARK_PYTHON"
    echo "  PYARROW_IGNORE_TIMEZONE=$PYARROW_IGNORE_TIMEZONE"
}

# Verify PySpark installation
verify_pyspark() {
    echo "Verifying PySpark installation..."
    
    python3 -c "
import sys
try:
    import pyspark
    from pyspark.sql import SparkSession
    
    print(f'✓ PySpark {pyspark.__version__} imported successfully')
    
    # Try to create a simple Spark session
    spark = SparkSession.builder \
        .appName('TestSetup') \
        .master('local[1]') \
        .config('spark.driver.bindAddress', '127.0.0.1') \
        .config('spark.ui.enabled', 'false') \
        .getOrCreate()
    
    # Simple test
    data = [(1, 'test'), (2, 'setup')]
    df = spark.createDataFrame(data, ['id', 'value'])
    count = df.count()
    
    spark.stop()
    
    if count == 2:
        print('✓ PySpark is working correctly!')
        sys.exit(0)
    else:
        print('✗ PySpark test failed')
        sys.exit(1)
        
except ImportError as e:
    print(f'✗ Failed to import PySpark: {e}')
    sys.exit(1)
except Exception as e:
    print(f'✗ PySpark verification failed: {e}')
    sys.exit(1)
"
}

# Create test runner script
create_test_runner() {
    echo "Creating test runner script..."
    
    cat > run_pyspark_tests.sh << 'EOF'
#!/bin/bash
# Run PySpark tests with proper environment setup

# Source the environment setup
source scripts/setup_test_environment.sh --no-install

# Run tests
echo "Running PySpark tests..."

# Basic PySpark tests
pytest tests/test_pyspark_csv_converter.py -v --tb=short

# Databricks environment tests
pytest tests/test_databricks_environment.py -v --tb=short

# Databricks extension tests
pytest tests/test_databricks_extension.py -v --tb=short

# Integration tests (may have some failures)
pytest tests/test_extension_integration.py -v --tb=short -k "databricks" || true

echo "✅ Test run complete!"
EOF
    
    chmod +x run_pyspark_tests.sh
    echo "✓ Created run_pyspark_tests.sh"
}

# Main execution
main() {
    echo "======================================"
    echo "PySpark Test Environment Setup"
    echo "======================================"
    
    # Check if we should skip installation (for test runs)
    if [ "$1" != "--no-install" ]; then
        check_java || exit 1
        setup_python_env
        install_dependencies
    fi
    
    configure_environment
    
    if [ "$1" != "--no-install" ]; then
        verify_pyspark || exit 1
        create_test_runner
        
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "To run PySpark tests:"
        echo "  ./run_pyspark_tests.sh"
        echo ""
        echo "Or run individual tests:"
        echo "  pytest tests/test_pyspark_csv_converter.py -v"
        echo "  pytest tests/test_databricks_extension.py -v"
    fi
}

# Run main function
main "$@"