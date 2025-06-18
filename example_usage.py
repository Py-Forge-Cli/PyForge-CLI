#!/usr/bin/env python3
"""Example usage of CortexPy CLI programmatically."""

from pathlib import Path
from cortexpy_cli.converters import PDFConverter
from cortexpy_cli.plugins import registry, plugin_loader


def main():
    """Demonstrate CortexPy CLI usage."""
    
    # Load all available converters
    plugin_loader.load_all()
    
    print("🚀 CortexPy CLI - Example Usage")
    print("=" * 40)
    
    # Show available formats
    print("\n📋 Available Formats:")
    formats = registry.list_supported_formats()
    for name, format_info in formats.items():
        inputs = ', '.join(format_info['inputs'])
        outputs = ', '.join(format_info['outputs'])
        print(f"  {name.title()}: {inputs} -> {outputs}")
    
    # Example: Check if we can convert a PDF
    example_pdf = Path("example.pdf")
    if registry.supports_input(example_pdf):
        print(f"\n✅ Can process {example_pdf.suffix} files")
        
        available_outputs = registry.get_available_outputs(example_pdf)
        print(f"   Available outputs: {', '.join(available_outputs)}")
        
        # Get converter
        converter = registry.get_converter(example_pdf)
        if converter:
            print(f"   Using converter: {type(converter).__name__}")
    else:
        print(f"\n❌ Cannot process {example_pdf.suffix} files")
    
    # Show plugin system status
    loaded_plugins = plugin_loader.get_loaded_plugins()
    print(f"\n🔌 Loaded Plugins: {', '.join(loaded_plugins) if loaded_plugins else 'None'}")
    
    print("\n💡 To use the CLI:")
    print("   cortexpy --help")
    print("   cortexpy formats")
    print("   cortexpy convert document.pdf")
    print("   cortexpy info document.pdf")


if __name__ == "__main__":
    main()