#!/usr/bin/env python3
"""Quick test script for CortexPy CLI functionality."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Success")
        if result.stdout.strip():
            print("Output:")
            print(result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""))
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        if e.stderr:
            print("Error:", e.stderr[:200])
        return False

def main():
    print("🧪 CortexPy CLI Quick Test")
    print("=" * 30)
    
    # Test 1: Basic commands
    tests = [
        (["uv", "run", "cortexpy", "--version"], "Version check"),
        (["uv", "run", "cortexpy", "formats"], "List formats"),
        (["uv", "run", "cortexpy", "--help"], "Main help"),
        (["uv", "run", "cortexpy", "convert", "--help"], "Convert help"),
        (["uv", "run", "cortexpy", "info", "--help"], "Info help"),
    ]
    
    passed = 0
    total = len(tests)
    
    for cmd, desc in tests:
        if run_command(cmd, desc):
            passed += 1
    
    print(f"\n📊 Basic Tests: {passed}/{total} passed")
    
    # Test 2: Error handling
    print("\n🚨 Testing Error Handling:")
    
    # Test with non-existent file (should fail)
    print("\n🔍 Testing with non-existent file (should fail)")
    try:
        result = subprocess.run(
            ["uv", "run", "cortexpy", "validate", "nonexistent.pdf"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("✅ Correctly failed for non-existent file")
        else:
            print("❌ Should have failed for non-existent file")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Look for PDF files
    print("\n📁 Looking for PDF files to test...")
    pdf_files = list(Path.home().glob("**/*.pdf"))[:5]  # Limit to first 5 found
    
    if pdf_files:
        test_pdf = pdf_files[0]
        print(f"Found PDF: {test_pdf}")
        
        # Copy to local directory
        local_pdf = Path("test.pdf")
        import shutil
        shutil.copy2(test_pdf, local_pdf)
        
        # Test PDF operations
        pdf_tests = [
            (["uv", "run", "cortexpy", "validate", "test.pdf"], "Validate PDF"),
            (["uv", "run", "cortexpy", "info", "test.pdf"], "Extract metadata"),
            (["uv", "run", "cortexpy", "info", "test.pdf", "--format", "json"], "JSON metadata"),
            (["uv", "run", "cortexpy", "convert", "test.pdf"], "Convert to text"),
        ]
        
        pdf_passed = 0
        for cmd, desc in pdf_tests:
            if run_command(cmd, desc):
                pdf_passed += 1
        
        print(f"\n📊 PDF Tests: {pdf_passed}/{len(pdf_tests)} passed")
        
        # Check if conversion produced output
        if Path("test.txt").exists():
            size = Path("test.txt").stat().st_size
            print(f"✅ Conversion output: test.txt ({size} bytes)")
            
            # Show first few lines
            with open("test.txt", "r", encoding="utf-8") as f:
                content = f.read(300)
                print(f"Preview: {content[:200]}...")
        
        # Cleanup
        for f in ["test.pdf", "test.txt"]:
            if Path(f).exists():
                Path(f).unlink()
    else:
        print("❌ No PDF files found for testing")
        print("💡 To test PDF features:")
        print("   1. Copy any PDF to this directory as 'test.pdf'")
        print("   2. Run: uv run cortexpy convert test.pdf")
    
    # Test 4: Package integrity
    print("\n📦 Testing Package Integrity:")
    try:
        # Test import
        result = subprocess.run(
            ["uv", "run", "python", "-c", "import cortexpy_cli; print('✅ Import successful')"],
            capture_output=True, text=True, check=True
        )
        print(result.stdout.strip())
        
        # Test programmatic usage
        result = subprocess.run(
            ["uv", "run", "python", "example_usage.py"],
            capture_output=True, text=True, check=True
        )
        print("✅ Example usage script works")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Package integrity test failed: {e}")
    
    print("\n🎯 Quick Test Complete!")
    print("\n💡 For more comprehensive testing:")
    print("   ./test_locally.sh")
    print("\n💡 Manual testing ideas:")
    print("   uv run cortexpy convert your_file.pdf")
    print("   uv run cortexpy info your_file.pdf --format json")
    print("   uv run cortexpy --verbose convert your_file.pdf --pages '1-3'")

if __name__ == "__main__":
    main()