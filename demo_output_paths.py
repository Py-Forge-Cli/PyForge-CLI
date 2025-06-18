#!/usr/bin/env python3
"""Demonstrate the output path behavior of CortexPy CLI."""

import subprocess
import tempfile
import shutil
from pathlib import Path

def demo_output_paths():
    """Demonstrate how output paths are generated."""
    
    print("📁 CortexPy CLI Output Path Demonstration")
    print("=" * 50)
    
    # Find a test PDF
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
        print("❌ No PDF files found for demonstration")
        print("💡 Copy a PDF file to this directory to see the demo")
        return
    
    print(f"📄 Using test PDF: {test_pdf.name}\n")
    
    # Create demo directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        demo_root = Path(temp_dir) / "demo"
        demo_root.mkdir()
        
        print("📁 Demo directory structure:")
        print(f"   {demo_root}/")
        
        # Scenario 1: File in root directory
        print("\n🔍 Scenario 1: File in root directory")
        file1 = demo_root / "document.pdf"
        shutil.copy2(test_pdf, file1)
        print(f"   Input:  {file1.relative_to(demo_root)}")
        
        result = subprocess.run([
            "uv", "run", "cortexpy", "convert", str(file1)
        ], capture_output=True, text=True, cwd=".")
        
        output1 = file1.with_suffix(".txt")
        if output1.exists():
            print(f"   Output: {output1.relative_to(demo_root)} ✅")
            print(f"   Same directory: {output1.parent == file1.parent}")
        
        # Scenario 2: File in subdirectory
        print("\n🔍 Scenario 2: File in subdirectory")
        subdir = demo_root / "reports" / "2024"
        subdir.mkdir(parents=True)
        file2 = subdir / "quarterly_report.pdf"
        shutil.copy2(test_pdf, file2)
        print(f"   Input:  {file2.relative_to(demo_root)}")
        
        result = subprocess.run([
            "uv", "run", "cortexpy", "convert", str(file2)
        ], capture_output=True, text=True, cwd=".")
        
        output2 = file2.with_suffix(".txt")
        if output2.exists():
            print(f"   Output: {output2.relative_to(demo_root)} ✅")
            print(f"   Same directory: {output2.parent == file2.parent}")
        
        # Scenario 3: Explicit output path
        print("\n🔍 Scenario 3: Explicit output path")
        file3 = demo_root / "input.pdf"
        shutil.copy2(test_pdf, file3)
        explicit_dir = demo_root / "outputs"
        explicit_dir.mkdir()
        explicit_output = explicit_dir / "custom_name.txt"
        
        print(f"   Input:  {file3.relative_to(demo_root)}")
        print(f"   Explicit output: {explicit_output.relative_to(demo_root)}")
        
        result = subprocess.run([
            "uv", "run", "cortexpy", "convert", str(file3), str(explicit_output)
        ], capture_output=True, text=True, cwd=".")
        
        if explicit_output.exists():
            print(f"   Created: {explicit_output.relative_to(demo_root)} ✅")
            print(f"   Different directory: {explicit_output.parent != file3.parent}")
        
        # Scenario 4: Complex filename
        print("\n🔍 Scenario 4: Complex filename with spaces and dots")
        complex_file = demo_root / "My Document v2.1 - Final.pdf"
        shutil.copy2(test_pdf, complex_file)
        print(f"   Input:  {complex_file.relative_to(demo_root)}")
        
        result = subprocess.run([
            "uv", "run", "cortexpy", "convert", str(complex_file)
        ], capture_output=True, text=True, cwd=".")
        
        complex_output = complex_file.with_suffix(".txt")
        if complex_output.exists():
            print(f"   Output: {complex_output.relative_to(demo_root)} ✅")
            print(f"   Preserves filename: {complex_output.stem == complex_file.stem}")
        
        # Show final directory structure
        print(f"\n📁 Final directory structure:")
        for item in sorted(demo_root.rglob("*")):
            if item.is_file():
                rel_path = item.relative_to(demo_root)
                size = item.stat().st_size
                file_type = "📄 PDF" if item.suffix == ".pdf" else "📝 TXT"
                print(f"   {rel_path} {file_type} ({size:,} bytes)")
    
    print(f"\n✅ Demonstration complete!")
    print(f"\n📋 Key behaviors:")
    print(f"   • Output files are created in the same directory as input files")
    print(f"   • Original filename is preserved with new extension")
    print(f"   • Complex filenames with spaces and dots are handled correctly")
    print(f"   • Explicit output paths override the default behavior")
    print(f"   • Use --verbose to see the auto-generated output path")

if __name__ == "__main__":
    demo_output_paths()