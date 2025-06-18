#!/usr/bin/env python3
"""Test script to verify output file path behavior."""

import tempfile
import shutil
from pathlib import Path
import subprocess

def test_output_path_behavior():
    """Test that output files are created in the same directory as input files."""
    
    print("🧪 Testing Output Path Behavior")
    print("=" * 40)
    
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create subdirectories
        subdir1 = temp_path / "documents"
        subdir2 = temp_path / "pdfs" / "work"
        subdir1.mkdir(parents=True)
        subdir2.mkdir(parents=True)
        
        print(f"📁 Created test directory: {temp_path}")
        
        # Look for an existing PDF to use for testing
        pdf_locations = [
            Path.home() / "Downloads",
            Path.home() / "Documents",
            Path("."),
        ]
        
        test_pdf = None
        for location in pdf_locations:
            if location.exists():
                pdfs = list(location.glob("*.pdf"))
                if pdfs:
                    test_pdf = pdfs[0]
                    break
        
        if not test_pdf:
            print("❌ No PDF files found for testing")
            print("💡 Copy a PDF file to this directory to test")
            return
        
        print(f"📄 Using test PDF: {test_pdf.name}")
        
        # Test 1: File in root directory
        print("\n🧪 Test 1: File in root directory")
        root_pdf = temp_path / "test_root.pdf"
        shutil.copy2(test_pdf, root_pdf)
        
        # Run conversion without specifying output path
        result = subprocess.run([
            "uv", "run", "cortexpy", "convert", str(root_pdf)
        ], capture_output=True, text=True, cwd=".")
        
        expected_output = root_pdf.with_suffix(".txt")
        if expected_output.exists():
            print(f"✅ Created: {expected_output}")
            print(f"   Size: {expected_output.stat().st_size:,} bytes")
        else:
            print(f"❌ Expected output not found: {expected_output}")
        
        # Test 2: File in subdirectory
        print("\n🧪 Test 2: File in subdirectory")
        sub_pdf = subdir1 / "test_subdir.pdf"
        shutil.copy2(test_pdf, sub_pdf)
        
        result = subprocess.run([
            "uv", "run", "cortexpy", "convert", str(sub_pdf)
        ], capture_output=True, text=True, cwd=".")
        
        expected_output = sub_pdf.with_suffix(".txt")
        if expected_output.exists():
            print(f"✅ Created: {expected_output}")
            print(f"   Relative to test dir: {expected_output.relative_to(temp_path)}")
        else:
            print(f"❌ Expected output not found: {expected_output}")
        
        # Test 3: File in nested subdirectory
        print("\n🧪 Test 3: File in nested subdirectory")
        nested_pdf = subdir2 / "test_nested.pdf"
        shutil.copy2(test_pdf, nested_pdf)
        
        result = subprocess.run([
            "uv", "run", "cortexpy", "convert", str(nested_pdf)
        ], capture_output=True, text=True, cwd=".")
        
        expected_output = nested_pdf.with_suffix(".txt")
        if expected_output.exists():
            print(f"✅ Created: {expected_output}")
            print(f"   Relative to test dir: {expected_output.relative_to(temp_path)}")
        else:
            print(f"❌ Expected output not found: {expected_output}")
        
        # Test 4: With verbose mode to see auto-generated path
        print("\n🧪 Test 4: Verbose mode (shows auto-generated path)")
        verbose_pdf = temp_path / "test_verbose.pdf"
        shutil.copy2(test_pdf, verbose_pdf)
        
        result = subprocess.run([
            "uv", "run", "cortexpy", "--verbose", "convert", str(verbose_pdf)
        ], capture_output=True, text=True, cwd=".")
        
        print("Verbose output:")
        print(result.stdout)
        
        expected_output = verbose_pdf.with_suffix(".txt")
        if expected_output.exists():
            print(f"✅ Created: {expected_output}")
        
        # Test 5: Compare with explicit output path
        print("\n🧪 Test 5: Explicit vs auto-generated paths")
        explicit_pdf = temp_path / "test_explicit.pdf"
        shutil.copy2(test_pdf, explicit_pdf)
        
        # Convert with explicit output path in different directory
        explicit_output = temp_path / "output" / "custom_name.txt"
        explicit_output.parent.mkdir(exist_ok=True)
        
        result = subprocess.run([
            "uv", "run", "cortexpy", "convert", str(explicit_pdf), str(explicit_output)
        ], capture_output=True, text=True, cwd=".")
        
        if explicit_output.exists():
            print(f"✅ Explicit output created: {explicit_output}")
            print(f"   Different directory: {explicit_output.parent != explicit_pdf.parent}")
        
        # Show directory structure
        print(f"\n📁 Final directory structure:")
        for item in temp_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(temp_path)
                size = item.stat().st_size
                print(f"   {rel_path} ({size:,} bytes)")

def test_edge_cases():
    """Test edge cases for output path generation."""
    print(f"\n🧪 Testing Edge Cases")
    print("=" * 30)
    
    # Test with files that have no extension
    print("Edge case testing would require actual file manipulation")
    print("Manual tests to try:")
    print("1. Files with no extension")
    print("2. Files with multiple dots in name")
    print("3. Files with spaces in path")
    print("4. Files with unicode characters")

if __name__ == "__main__":
    test_output_path_behavior()
    test_edge_cases()
    
    print(f"\n✅ Output Path Testing Complete!")
    print(f"\n💡 Manual verification:")
    print(f"   uv run cortexpy convert /path/to/your/file.pdf")
    print(f"   # Should create: /path/to/your/file.txt")