#!/usr/bin/env python3
"""Simple test for CortexPy CLI with manual PDF testing."""

import subprocess
import sys
from pathlib import Path

def run_cmd(cmd):
    """Run command and show result."""
    print(f"$ {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Success")
        print(result.stdout[:300] + ("..." if len(result.stdout) > 300 else ""))
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error (exit {e.returncode})")
        if e.stderr:
            print(f"Error: {e.stderr[:200]}")
        return False

def main():
    print("🧪 CortexPy CLI Simple Test")
    print("=" * 30)
    
    # Basic functionality tests
    tests = [
        ["uv", "run", "cortexpy", "--version"],
        ["uv", "run", "cortexpy", "formats"],
    ]
    
    for cmd in tests:
        print()
        run_cmd(cmd)
    
    # Look for PDFs in common locations
    pdf_dirs = [
        Path.home() / "Downloads",
        Path.home() / "Documents", 
        Path.home() / "Desktop",
        Path(".")  # Current directory
    ]
    
    print(f"\n📁 Looking for PDF files...")
    test_pdf = None
    
    for pdf_dir in pdf_dirs:
        if pdf_dir.exists():
            pdfs = list(pdf_dir.glob("*.pdf"))
            if pdfs:
                test_pdf = pdfs[0]
                print(f"Found: {test_pdf}")
                break
    
    if test_pdf:
        print(f"\n🧪 Testing with: {test_pdf.name}")
        
        # Copy to local directory for testing
        local_pdf = Path("sample.pdf")
        import shutil
        shutil.copy2(test_pdf, local_pdf)
        
        # Test PDF commands
        print("\n1. Validating PDF:")
        run_cmd(["uv", "run", "cortexpy", "validate", "sample.pdf"])
        
        print("\n2. Getting metadata:")
        run_cmd(["uv", "run", "cortexpy", "info", "sample.pdf"])
        
        print("\n3. Converting to text:")
        run_cmd(["uv", "run", "cortexpy", "convert", "sample.pdf"])
        
        # Check output
        if Path("sample.txt").exists():
            size = Path("sample.txt").stat().st_size
            print(f"\n✅ Output created: sample.txt ({size:,} bytes)")
            
            # Show preview
            with open("sample.txt", "r", encoding="utf-8", errors="ignore") as f:
                preview = f.read(200)
                print(f"Preview: {preview}...")
        
        # Test page range
        print("\n4. Testing page range (first page only):")
        run_cmd(["uv", "run", "cortexpy", "convert", "sample.pdf", "page1.txt", "--pages", "1"])
        
        # Cleanup
        for f in ["sample.pdf", "sample.txt", "page1.txt"]:
            Path(f).unlink(missing_ok=True)
        
    else:
        print("\n❌ No PDF files found in common locations")
        print("\n💡 To test PDF conversion manually:")
        print("   1. Copy any PDF to this directory")
        print("   2. Run: uv run cortexpy convert your_file.pdf")
    
    print(f"\n🎯 Manual testing commands:")
    print(f"uv run cortexpy --help                     # Full help")
    print(f"uv run cortexpy convert --help             # Conversion help")
    print(f"uv run cortexpy convert file.pdf           # Convert PDF")
    print(f"uv run cortexpy info file.pdf              # Get metadata")
    print(f"uv run cortexpy validate file.pdf          # Validate file")
    
    # Test build system
    print(f"\n🏗️ Testing build system:")
    if run_cmd(["make", "build"]):
        print("✅ Build system works")
        if Path("dist").exists():
            files = list(Path("dist").glob("*"))
            print(f"Built files: {[f.name for f in files]}")

if __name__ == "__main__":
    main()