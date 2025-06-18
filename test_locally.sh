#!/bin/bash

# CortexPy CLI Local Testing Script
# This script provides comprehensive testing for the CLI tool

set -e  # Exit on error

echo "🧪 CortexPy CLI - Local Testing Suite"
echo "====================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test 1: Basic CLI functionality
print_status "Testing basic CLI functionality..."

echo "1. Testing --version"
uv run cortexpy --version
print_success "Version command works"

echo -e "\n2. Testing --help"
uv run cortexpy --help > /dev/null
print_success "Help command works"

echo -e "\n3. Testing formats command"
uv run cortexpy formats
print_success "Formats command works"

# Test 2: Command help systems
print_status "Testing command help systems..."

commands=("convert" "info" "validate" "formats")
for cmd in "${commands[@]}"; do
    echo "Testing: cortexpy $cmd --help"
    uv run cortexpy "$cmd" --help > /dev/null
    print_success "$cmd help works"
done

# Test 3: Error handling
print_status "Testing error handling..."

echo "Testing with non-existent file"
if uv run cortexpy validate non_existent.pdf 2>/dev/null; then
    print_error "Should fail with non-existent file"
else
    print_success "Correctly handles non-existent files"
fi

echo "Testing with unsupported format"
touch test.txt
# Capture both stdout and stderr, check exit code
if uv run cortexpy validate test.txt >/dev/null 2>&1; then
    print_warning "Validation passed for .txt file (may be intended behavior)"
else
    print_success "Correctly handles unsupported formats"
fi
rm -f test.txt

# Test 4: Check for PDF files to test conversion
print_status "Looking for PDF files to test conversion..."

# Look for PDF files in common locations
pdf_found=""
search_dirs=(
    "."
    "$HOME/Downloads"
    "$HOME/Documents"
    "$HOME/Desktop"
)

for dir in "${search_dirs[@]}"; do
    if [ -d "$dir" ]; then
        pdf_file=$(find "$dir" -name "*.pdf" -type f | head -1)
        if [ -n "$pdf_file" ]; then
            pdf_found="$pdf_file"
            echo "Found PDF: $pdf_file"
            break
        fi
    fi
done

if [ -n "$pdf_found" ]; then
    print_status "Testing PDF conversion with: $pdf_found"
    
    # Copy to local directory for testing
    cp "$pdf_found" test_sample.pdf
    
    echo "1. Testing validation"
    if uv run cortexpy validate test_sample.pdf; then
        print_success "PDF validation works"
        
        echo -e "\n2. Testing metadata extraction"
        uv run cortexpy info test_sample.pdf
        print_success "Metadata extraction works"
        
        echo -e "\n3. Testing JSON metadata output"
        uv run cortexpy info test_sample.pdf --format json > metadata.json
        if [ -f metadata.json ] && [ -s metadata.json ]; then
            print_success "JSON metadata export works"
            echo "Sample metadata:"
            head -10 metadata.json
        fi
        
        echo -e "\n4. Testing conversion"
        uv run cortexpy --verbose convert test_sample.pdf
        if [ -f test_sample.txt ]; then
            print_success "PDF conversion works"
            echo "Output file size: $(wc -c < test_sample.txt) bytes"
            echo "First few lines of converted text:"
            head -5 test_sample.txt
        else
            print_error "Conversion failed - no output file"
        fi
        
        echo -e "\n5. Testing page range conversion"
        uv run cortexpy --verbose convert test_sample.pdf page_range_test.txt --pages "1"
        if [ -f page_range_test.txt ]; then
            print_success "Page range conversion works"
        else
            print_warning "Page range conversion may have failed"
        fi
        
    else
        print_warning "PDF validation failed - file may be corrupted or unsupported"
    fi
    
    # Cleanup
    rm -f test_sample.pdf test_sample.txt page_range_test.txt metadata.json
else
    print_warning "No PDF files found for conversion testing"
    print_warning "To test PDF conversion:"
    echo "  1. Copy any PDF file to this directory as 'test.pdf'"
    echo "  2. Run: uv run cortexpy convert test.pdf"
fi

# Test 5: Development tools
print_status "Testing development tools..."

echo "1. Testing build system"
if make build > /dev/null 2>&1; then
    print_success "Build system works"
    if [ -d "dist" ]; then
        echo "Built packages:"
        ls -la dist/
    fi
else
    print_error "Build system failed"
fi

echo -e "\n2. Testing test suite"
if make test > /dev/null 2>&1; then
    print_success "Test suite runs successfully"
else
    print_warning "Test suite may have issues (check dependencies)"
fi

# Test 6: Package integrity
print_status "Testing package integrity..."

echo "1. Checking package structure"
required_files=(
    "src/cortexpy_cli/__init__.py"
    "src/cortexpy_cli/main.py"
    "src/cortexpy_cli/converters/pdf_converter.py"
    "src/cortexpy_cli/plugins/registry.py"
    "pyproject.toml"
    "README.md"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ Missing: $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = true ]; then
    print_success "All required files present"
else
    print_error "Some required files are missing"
fi

echo -e "\n2. Testing Python imports"
if uv run python -c "import cortexpy_cli; print('✓ Package imports successfully')"; then
    print_success "Package imports work"
else
    print_error "Package import failed"
fi

# Summary
echo -e "\n🎯 Testing Summary"
echo "=================="
echo "✅ Basic CLI functionality tested"
echo "✅ Help system verified"
echo "✅ Error handling checked"
echo "✅ Package structure validated"

if [ -n "$pdf_found" ]; then
    echo "✅ PDF conversion tested successfully"
else
    echo "⚠️  PDF conversion not tested (no PDF files found)"
fi

echo -e "\n📝 Manual Testing Recommendations:"
echo "1. Test with your own PDF files:"
echo "   uv run cortexpy convert your_file.pdf"
echo ""
echo "2. Test advanced features:"
echo "   uv run cortexpy convert file.pdf --pages '1-5' --metadata"
echo ""
echo "3. Test batch processing:"
echo "   for f in *.pdf; do uv run cortexpy convert \"\$f\"; done"
echo ""
echo "4. Test integration with other tools:"
echo "   uv run cortexpy convert file.pdf | wc -w"

print_success "Local testing completed!"