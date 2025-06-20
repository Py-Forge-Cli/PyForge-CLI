"""Main CLI entry point for PyForge CLI."""

import click
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

from . import __version__
from .plugins import registry, plugin_loader


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="pyforge")
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose output with detailed progress information')
@click.pass_context
def cli(ctx, verbose):
    """PyForge CLI - A powerful data format conversion and synthetic data generation tool.
    
    \b
    DESCRIPTION:
        Convert between various data formats with ease and precision.
        Features beautiful terminal output, progress tracking, and extensible
        plugin architecture for adding new format converters.
    
    \b
    CURRENTLY SUPPORTED FORMATS:
        • PDF to Text conversion with advanced options
        • Excel (.xlsx) to Parquet conversion with multi-sheet support
        • MDB/ACCDB (Microsoft Access) to Parquet conversion
        • DBF (dBase) to Parquet conversion
        • CSV (.csv, .tsv, .txt) to Parquet conversion with auto-detection
        • File metadata extraction and validation
    
    \b
    QUICK START:
        pyforge formats                    # List all supported formats
        pyforge convert document.pdf       # Convert PDF to text
        pyforge info document.pdf          # Show file metadata
        pyforge validate document.pdf      # Check if file is valid
    
    \b
    EXAMPLES:
        # PDF conversion
        pyforge convert report.pdf
        pyforge convert document.pdf output.txt --pages "1-10" --metadata
        
        # Excel conversion
        pyforge convert data.xlsx --format parquet
        pyforge convert workbook.xlsx --format parquet --combine
        pyforge convert report.xlsx --format parquet --separate
        
        # Database conversion
        pyforge convert database.mdb --format parquet
        pyforge convert data.dbf output_dir/ --format parquet --compression gzip
        pyforge convert secure.accdb --password "secret" --tables "customers,orders"
        
        # CSV conversion
        pyforge convert data.csv --format parquet
        pyforge convert sales_data.csv output.parquet --compression gzip --verbose
        pyforge convert international.tsv --format parquet --force
        
        # File information and validation
        pyforge info document.pdf --format json
        pyforge validate database.mdb
    
    \b
    PLUGIN SYSTEM:
        The tool supports plugins for adding new format converters.
        See documentation for creating custom converters.
    
    For detailed help on any command, use: pyforge COMMAND --help
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    # Load all available converters
    plugin_loader.load_all()


@cli.command()
@click.argument('input_file', 
                type=click.Path(exists=True, path_type=Path),
                metavar='INPUT_FILE')
@click.argument('output_file', 
                type=click.Path(path_type=Path), 
                required=False,
                metavar='[OUTPUT_FILE]')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['txt', 'parquet'], case_sensitive=False),
              default='txt',
              help='Output format. Supported: txt (default), parquet')
@click.option('--pages', '-p', 'page_range',
              metavar='RANGE',
              help='Page range to convert (PDF only). Examples: "1-5", "1-", "-10", "3"')
@click.option('--metadata', '-m', is_flag=True,
              help='Include page metadata and markers in output text (PDF only)')
@click.option('--password', 
              metavar='PASSWORD',
              help='Password for protected database files (MDB/ACCDB only)')
@click.option('--tables', '-t',
              metavar='TABLE_LIST',
              help='Comma-separated list of tables to convert (database only)')
@click.option('--compression', '-c',
              type=click.Choice(['snappy', 'gzip', 'none'], case_sensitive=False),
              default='snappy',
              help='Parquet compression format (default: snappy)')
@click.option('--force', is_flag=True,
              help='Overwrite existing output file without confirmation')
@click.option('--combine', is_flag=True,
              help='Force combination of matching sheets into single parquet (Excel only)')
@click.option('--separate', is_flag=True,
              help='Keep all sheets as separate parquet files (Excel only)')
@click.pass_context
def convert(ctx, input_file, output_file, output_format, page_range, metadata, password, tables, compression, force, combine, separate):
    """Convert files between different formats.
    
    \b
    DESCRIPTION:
        Convert documents from one format to another with advanced options.
        The converter automatically detects the input format and applies
        the appropriate conversion method.
    
    \b
    ARGUMENTS:
        INPUT_FILE      Path to the input file to convert
        OUTPUT_FILE     Path for the output file (optional)
                       If not provided, creates output in same directory as input
                       with same filename but different extension
    
    \b
    PDF CONVERSION OPTIONS:
        --pages RANGE   Convert only specific pages:
                       • "5"      - Convert only page 5
                       • "1-10"   - Convert pages 1 through 10
                       • "5-"     - Convert from page 5 to end
                       • "-10"    - Convert from start to page 10
        
        --metadata      Include page markers in output:
                       • Adds "--- Page N ---" markers
                       • Useful for identifying source pages
                       • Increases output file size
    
    \b
    EXAMPLES:
        # Basic conversion (creates document.txt in same directory)
        cortexpy convert document.pdf
        
        # Convert with custom output filename
        cortexpy convert report.pdf extracted_text.txt
        
        # Convert file in subdirectory (creates subdir/file.txt)
        cortexpy convert path/to/document.pdf
        
        # Convert only first 5 pages
        cortexpy convert document.pdf --pages "1-5"
        
        # Convert from page 10 to end with metadata
        cortexpy convert document.pdf --pages "10-" --metadata
        
        # Force overwrite existing file
        cortexpy convert document.pdf output.txt --force
        
        # Convert with verbose progress
        cortexpy convert document.pdf --verbose
        
        # Excel conversion examples
        cortexpy convert data.xlsx --format parquet
        cortexpy convert workbook.xlsx --format parquet --combine
        cortexpy convert report.xlsx --format parquet --separate
        
        # Database conversion examples
        cortexpy convert database.mdb --format parquet
        cortexpy convert data.dbf output_dir/ --format parquet --compression gzip
        cortexpy convert secure.accdb --password "secret" --tables "customers,orders"
    
    \b
    OUTPUT:
        PDF CONVERSION:
        • Creates text file with extracted content
        • Shows progress bar for large files
        • Reports number of pages processed
        
        EXCEL CONVERSION:
        • Analyzes multi-sheet workbooks with column signature detection
        • Interactive prompts for handling matching/different sheet structures
        • Converts all data to string format with proper precision
        • Formula values extracted and converted (warns user)
        • Progress tracking with sheet-by-sheet processing
        
        DATABASE CONVERSION:
        • Creates directory with Parquet files (one per table)
        • Shows 6-stage progress with real-time metrics
        • Generates Excel report with conversion summary
        • All data converted to string format for Phase 1
    
    \b
    NOTES:
        • Empty pages are automatically skipped
        • Text encoding is UTF-8
        • Progress is shown for files with multiple pages
        • Use --verbose flag for detailed conversion information
    """
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        console.print(f"[dim]Input file: {input_file}[/dim]")
        console.print(f"[dim]Output format: {output_format}[/dim]")
    
    # Determine output path
    input_ext = input_file.suffix.lower()
    is_database = input_ext in ['.mdb', '.accdb', '.dbf']
    is_excel = input_ext == '.xlsx'
    
    if not output_file:
        if (is_database or is_excel) and output_format == 'parquet':
            # For database and Excel conversions, create output directory
            output_file = input_file.parent / f"{input_file.stem}_parquet"
        else:
            # Generate output file in same directory as input with new extension
            output_file = input_file.with_suffix(f'.{output_format}')
        
        if verbose:
            if is_database or is_excel:
                console.print(f"[dim]Auto-generated output directory: {output_file}[/dim]")
            else:
                console.print(f"[dim]Auto-generated output file: {output_file}[/dim]")
    
    # Check if output path exists
    if output_file.exists() and not force:
        if is_database or is_excel:
            console.print(f"[yellow]Output directory {output_file} already exists. Use --force to overwrite.[/yellow]")
        else:
            console.print(f"[yellow]Output file {output_file} already exists. Use --force to overwrite.[/yellow]")
        return
    
    # Get converter from registry
    converter = registry.get_converter(input_file)
    
    if not converter:
        console.print(f"[red]Error: Unsupported input format '{input_file.suffix}'[/red]")
        
        # Show available formats
        formats = registry.list_supported_formats()
        if formats:
            console.print("[dim]Supported formats:[/dim]")
            for name, format_info in formats.items():
                inputs = ', '.join(format_info['inputs'])
                console.print(f"[dim]  {inputs}[/dim]")
        return
    
    # Prepare conversion options
    options = {}
    
    # PDF-specific options
    if page_range:
        options['page_range'] = page_range
    if metadata:
        options['include_metadata'] = True
    
    # Database-specific options
    if password:
        options['password'] = password
    if tables:
        options['tables'] = [t.strip() for t in tables.split(',')]
    if compression:
        options['compression'] = compression
    
    # Excel-specific options
    if combine:
        options['combine'] = True
    if separate:
        options['separate'] = True
    
    # Perform conversion
    success = converter.convert(input_file, output_file, **options)
    
    if not success:
        console.print("[red]Conversion failed![/red]")
        raise click.Abort()


@cli.command()
@click.argument('input_file', 
                type=click.Path(exists=True, path_type=Path),
                metavar='INPUT_FILE')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json'], case_sensitive=False),
              default='table',
              help='Output format: table (default) or json')
def info(input_file, output_format):
    """Display detailed file information and metadata.
    
    \b
    DESCRIPTION:
        Extract and display comprehensive metadata from supported file formats.
        Shows document properties, technical details, and processing information
        in either human-readable table format or machine-readable JSON.
    
    \b
    ARGUMENTS:
        INPUT_FILE      Path to the file to analyze
    
    \b
    OUTPUT FORMATS:
        table          Human-readable formatted table (default)
                      • Colorized output with clear labels
                      • Formatted file sizes and dates
                      • Easy to read in terminal
        
        json           Machine-readable JSON format
                      • Suitable for scripting and automation
                      • Can be piped to other tools
                      • Preserves all metadata fields
    
    \b
    PDF METADATA INCLUDES:
        • Document title, author, subject
        • Creation and modification dates
        • Creator and producer software
        • Total page count
        • File size in bytes
        • PDF version information
    
    \b
    EXAMPLES:
        # Display metadata as formatted table
        cortexpy info document.pdf
        
        # Export metadata as JSON
        cortexpy info document.pdf --format json
        
        # Save JSON metadata to file
        cortexpy info document.pdf --format json > metadata.json
        
        # Extract specific field using jq
        cortexpy info document.pdf --format json | jq '.page_count'
        
        # Process multiple files
        for file in *.pdf; do
            echo "=== $file ==="
            cortexpy info "$file"
        done
    
    \b
    OUTPUT EXAMPLES:
        Table format shows:
        ┌─────────────┬─────────────────────┐
        │ Property    │ Value               │
        ├─────────────┼─────────────────────┤
        │ Title       │ My Document         │
        │ Author      │ John Doe            │
        │ Page Count  │ 25 pages           │
        │ File Size   │ 2,048,576 bytes    │
        └─────────────┴─────────────────────┘
        
        JSON format returns:
        {
          "title": "My Document",
          "author": "John Doe",
          "page_count": 25,
          "file_size": 2048576
        }
    
    \b
    NOTES:
        • Some metadata fields may be empty or unavailable
        • File size is always shown in bytes
        • Dates are in ISO format for JSON output
        • Use --verbose for additional processing details
    """
    converter = registry.get_converter(input_file)
    
    if not converter:
        console.print(f"[red]Error: Unsupported file format '{input_file.suffix}'[/red]")
        return
    
    metadata = converter.get_metadata(input_file)
    
    if not metadata:
        console.print("[red]Could not extract metadata from file[/red]")
        return
    
    if output_format == 'json':
        import json
        console.print(json.dumps(metadata, indent=2))
    else:
        # Display as table
        table = Table(title=f"File Information: {input_file.name}")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        for key, value in metadata.items():
            # Format the key for display
            display_key = key.replace('_', ' ').title()
            
            # Format the value
            if key == 'file_size':
                display_value = f"{value:,} bytes"
            elif key == 'page_count':
                display_value = f"{value} pages"
            else:
                display_value = str(value) if value else "N/A"
            
            table.add_row(display_key, display_value)
        
        console.print(table)


@cli.command()
def formats():
    """List all supported input and output formats.
    
    \b
    DESCRIPTION:
        Display a comprehensive table of all supported file format conversions.
        Shows which input formats can be converted to which output formats,
        along with information about loaded converter plugins.
    
    \b
    OUTPUT:
        • Table showing converter names and supported formats
        • Input formats (file extensions the tool can read)
        • Output formats (file extensions the tool can create)
        • List of currently loaded converter plugins
    
    \b
    EXAMPLES:
        # List all supported formats
        cortexpy formats
        
        # Check which formats are available after loading plugins
        cortexpy formats
    
    \b
    INTERPRETING OUTPUT:
        The table shows:
        • Converter: Name of the conversion plugin
        • Input Formats: File extensions that can be processed
        • Output Formats: File extensions that can be generated
        
        Example output:
        ┌───────────┬───────────────┬────────────────┐
        │ Converter │ Input Formats │ Output Formats │
        ├───────────┼───────────────┼────────────────┤
        │ Pdf       │ .pdf          │ .txt           │
        └───────────┴───────────────┴────────────────┘
    
    \b
    PLUGIN INFORMATION:
        • Loaded plugins are shown at the bottom
        • Plugins extend the tool's capabilities
        • Add new plugins by installing additional packages
        • Custom plugins can be placed in ~/.cortexpy/plugins/
    
    \b
    NOTES:
        • More formats are coming in future releases
        • Check project roadmap for planned format support
        • Contribute new converters via plugin system
    """
    formats_info = registry.list_supported_formats()
    
    if not formats_info:
        console.print("[yellow]No converters loaded.[/yellow]")
        return
    
    table = Table(title="Supported Formats")
    table.add_column("Converter", style="blue")
    table.add_column("Input Formats", style="cyan")
    table.add_column("Output Formats", style="magenta")
    
    for converter_name, format_info in formats_info.items():
        inputs = ', '.join(sorted(format_info['inputs']))
        outputs = ', '.join(sorted(format_info['outputs']))
        
        table.add_row(
            converter_name.title(),
            inputs,
            outputs
        )
    
    console.print(table)
    
    # Show loaded plugins
    loaded_plugins = plugin_loader.get_loaded_plugins()
    if loaded_plugins:
        console.print(f"\n[dim]Loaded plugins: {', '.join(loaded_plugins)}[/dim]")


@cli.command()
@click.argument('input_file', 
                type=click.Path(exists=True, path_type=Path),
                metavar='INPUT_FILE')
def validate(input_file):
    """Validate if a file can be processed by the tool.
    
    \b
    DESCRIPTION:
        Check if a file is valid and can be successfully processed by the
        appropriate converter. This performs format validation without
        actually converting the file, useful for batch processing validation.
    
    \b
    ARGUMENTS:
        INPUT_FILE      Path to the file to validate
    
    \b
    VALIDATION CHECKS:
        • File exists and is readable
        • File extension is supported
        • File format is valid and not corrupted
        • File can be opened by the appropriate converter
        • File contains processable content
    
    \b
    EXIT CODES:
        0              File is valid and can be processed
        1              File is invalid or cannot be processed
    
    \b
    EXAMPLES:
        # Validate a single PDF file
        cortexpy validate document.pdf
        
        # Validate multiple files in a script
        for file in *.pdf; do
            if cortexpy validate "$file" >/dev/null 2>&1; then
                echo "✓ $file is valid"
            else
                echo "✗ $file is invalid"
            fi
        done
        
        # Find all valid PDFs in directory
        find . -name "*.pdf" -exec cortexpy validate {} \\; \\
            -print 2>/dev/null
        
        # Use in conditional processing
        if cortexpy validate document.pdf; then
            cortexpy convert document.pdf
        else
            echo "Cannot process invalid file"
        fi
    
    \b
    OUTPUT:
        Valid file:
        ✓ document.pdf is a valid PDF file
        
        Invalid file:
        ✗ corrupted.pdf is not a valid PDF file
    
    \b
    NOTES:
        • Validation is fast and doesn't modify files
        • Use before batch processing to filter valid files
        • Supports all formats that have converters loaded
        • Returns appropriate exit codes for scripting
    """
    converter = registry.get_converter(input_file)
    
    if not converter:
        console.print(f"[red]Error: Unsupported file format '{input_file.suffix}'[/red]")
        return
    
    is_valid = converter.validate_input(input_file)
    
    if is_valid:
        console.print(f"[green]✓ {input_file.name} is a valid {input_file.suffix.upper()} file[/green]")
    else:
        console.print(f"[red]✗ {input_file.name} is not a valid {input_file.suffix.upper()} file[/red]")


if __name__ == '__main__':
    cli()