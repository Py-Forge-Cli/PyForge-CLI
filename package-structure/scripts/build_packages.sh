#!/bin/bash
# Build script for PyForge modular packages

set -e  # Exit on error

echo "🔨 Building PyForge packages..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Function to build a package
build_package() {
    local package_name=$1
    local package_dir="$ROOT_DIR/$package_name"
    
    echo -e "${BLUE}Building $package_name...${NC}"
    
    if [ ! -d "$package_dir" ]; then
        echo -e "${RED}Error: Package directory $package_dir not found${NC}"
        return 1
    fi
    
    cd "$package_dir"
    
    # Clean previous builds
    rm -rf dist/ build/ *.egg-info/
    
    # Build the package
    python -m build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $package_name built successfully${NC}"
        echo "   Distribution files in: $package_dir/dist/"
    else
        echo -e "${RED}❌ Failed to build $package_name${NC}"
        return 1
    fi
}

# Function to run tests
run_tests() {
    local package_name=$1
    local package_dir="$ROOT_DIR/$package_name"
    
    echo -e "${BLUE}Running tests for $package_name...${NC}"
    
    cd "$package_dir"
    
    if [ -d "tests" ]; then
        python -m pytest tests/ -v
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ All tests passed for $package_name${NC}"
        else
            echo -e "${RED}❌ Some tests failed for $package_name${NC}"
            return 1
        fi
    else
        echo "   No tests directory found, skipping tests"
    fi
}

# Main build process
main() {
    echo "📦 PyForge Package Builder"
    echo "========================="
    echo ""
    
    # Check if build tool is installed
    if ! command -v python -m build &> /dev/null; then
        echo -e "${RED}Error: 'build' package not installed${NC}"
        echo "Please install it with: pip install build"
        exit 1
    fi
    
    # Build pyforge-core first (dependency for pyforge-databricks)
    echo "1. Building pyforge-core..."
    build_package "pyforge-core"
    
    # Optional: Run tests for pyforge-core
    if [ "$1" == "--test" ]; then
        run_tests "pyforge-core"
    fi
    
    echo ""
    echo "2. Building pyforge-databricks..."
    build_package "pyforge-databricks"
    
    # Optional: Run tests for pyforge-databricks
    if [ "$1" == "--test" ]; then
        run_tests "pyforge-databricks"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Build complete!${NC}"
    echo ""
    echo "Distribution files created:"
    echo "  - $ROOT_DIR/pyforge-core/dist/"
    echo "  - $ROOT_DIR/pyforge-databricks/dist/"
    echo ""
    echo "To install locally for testing:"
    echo "  pip install $ROOT_DIR/pyforge-core/dist/*.whl"
    echo "  pip install $ROOT_DIR/pyforge-databricks/dist/*.whl"
    echo ""
    echo "To publish to PyPI:"
    echo "  python -m twine upload $ROOT_DIR/pyforge-core/dist/*"
    echo "  python -m twine upload $ROOT_DIR/pyforge-databricks/dist/*"
}

# Run main function
main "$@"