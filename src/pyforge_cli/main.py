"""Main CLI entry point for PyForge CLI."""

import logging
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .extensions import get_extension_manager
from .extensions.logging import configure_verbose_logging, setup_extension_logging
from .plugins import plugin_loader, registry

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="pyforge")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with detailed progress information",
)
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
        • XML (.xml, .xml.gz, .xml.bz2) to Parquet conversion with intelligent flattening
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

        # XML conversion
        pyforge convert data.xml --format parquet
        pyforge convert catalog.xml --flatten-strategy aggressive --array-handling expand
        pyforge convert api_response.xml --namespace-handling strip --preview-schema

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
    ctx.obj["verbose"] = verbose

    # Configure logging based on verbose flag
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.getLogger("pyforge_cli").setLevel(logging.DEBUG)
        console.print("[dim]Debug logging enabled[/dim]")
        # Also configure extension logging for verbose mode
        configure_verbose_logging()
    else:
        logging.basicConfig(
            level=logging.WARNING, format="%(name)s - %(levelname)s - %(message)s"
        )
        # Setup standard extension logging
        setup_extension_logging()

    # Load all available converters
    plugin_loader.load_all()

    # Initialize extension manager
    extension_manager = get_extension_manager()
    extension_manager.initialize()
    ctx.obj["extension_manager"] = extension_manager


@cli.command()
@click.argument(
    "input_file", type=click.Path(exists=True, path_type=Path), metavar="INPUT_FILE"
)
@click.argument(
    "output_file",
    type=click.Path(path_type=Path),
    required=False,
    metavar="[OUTPUT_FILE]",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["txt", "parquet"], case_sensitive=False),
    default="txt",
    help="Output format. Supported: txt (default), parquet",
)
@click.option(
    "--pages",
    "-p",
    "page_range",
    metavar="RANGE",
    help='Page range to convert (PDF only). Examples: "1-5", "1-", "-10", "3"',
)
@click.option(
    "--metadata",
    "-m",
    is_flag=True,
    help="Include page metadata and markers in output text (PDF only)",
)
@click.option(
    "--password",
    metavar="PASSWORD",
    help="Password for protected database files (MDB/ACCDB only)",
)
@click.option(
    "--tables",
    "-t",
    metavar="TABLE_LIST",
    help="Comma-separated list of tables to convert (database only)",
)
@click.option(
    "--compression",
    "-c",
    type=click.Choice(["snappy", "gzip", "none"], case_sensitive=False),
    default="snappy",
    help="Parquet compression format (default: snappy)",
)
@click.option(
    "--force", is_flag=True, help="Overwrite existing output file without confirmation"
)
@click.option(
    "--combine",
    is_flag=True,
    help="Force combination of matching sheets into single parquet (Excel only)",
)
@click.option(
    "--separate",
    is_flag=True,
    help="Keep all sheets as separate parquet files (Excel only)",
)
@click.option(
    "--flatten-strategy",
    type=click.Choice(["conservative", "moderate", "aggressive"], case_sensitive=False),
    default="conservative",
    help="XML flattening strategy (XML only): conservative, moderate, aggressive",
)
@click.option(
    "--array-handling",
    type=click.Choice(["expand", "concatenate", "json_string"], case_sensitive=False),
    default="expand",
    help="XML array handling mode (XML only): expand, concatenate, json_string",
)
@click.option(
    "--namespace-handling",
    type=click.Choice(["preserve", "strip", "prefix"], case_sensitive=False),
    default="preserve",
    help="XML namespace handling (XML only): preserve, strip, prefix",
)
@click.option(
    "--preview-schema",
    is_flag=True,
    help="Preview XML structure before conversion (XML only)",
)
@click.option(
    "--force-pyspark",
    is_flag=True,
    help="Force using PySpark for CSV conversion (requires PySpark)",
)
@click.pass_context
def convert(
    ctx,
    input_file,
    output_file,
    output_format,
    page_range,
    metadata,
    password,
    tables,
    compression,
    force,
    combine,
    separate,
    flatten_strategy,
    array_handling,
    namespace_handling,
    preview_schema,
    force_pyspark,
):
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

        # XML conversion examples
        cortexpy convert data.xml --format parquet
        cortexpy convert catalog.xml --flatten-strategy aggressive --array-handling expand
        cortexpy convert api_response.xml --namespace-handling strip --preview-schema

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

        XML CONVERSION:
        • Analyzes XML structure and detects arrays automatically
        • Flattens hierarchical data using configurable strategies
        • Handles namespaces and attributes intelligently
        • Creates single Parquet file with column-based output
        • All data converted to string format with proper handling

    \b
    NOTES:
        • Empty pages are automatically skipped
        • Text encoding is UTF-8
        • Progress is shown for files with multiple pages
        • Use --verbose flag for detailed conversion information
    """
    verbose = ctx.obj.get("verbose", False)
    extension_manager = ctx.obj.get("extension_manager")

    if verbose:
        console.print(f"[dim]Input file: {input_file}[/dim]")
        console.print(f"[dim]Output format: {output_format}[/dim]")

    # Determine output path
    input_ext = input_file.suffix.lower()
    is_database = input_ext in [".mdb", ".accdb", ".dbf"]
    is_excel = input_ext == ".xlsx"

    if not output_file:
        if (is_database or is_excel) and output_format == "parquet":
            # For database and Excel conversions, create output directory
            output_file = input_file.parent / f"{input_file.stem}_parquet"
        else:
            # Generate output file in same directory as input with new extension
            output_file = input_file.with_suffix(f".{output_format}")

        if verbose:
            if is_database or is_excel:
                console.print(
                    f"[dim]Auto-generated output directory: {output_file}[/dim]"
                )
            else:
                console.print(f"[dim]Auto-generated output file: {output_file}[/dim]")

    # Check if output path exists
    if output_file.exists() and not force:
        if is_database or is_excel:
            console.print(
                f"[yellow]Output directory {output_file} already exists. Use --force to overwrite.[/yellow]"
            )
        else:
            console.print(
                f"[yellow]Output file {output_file} already exists. Use --force to overwrite.[/yellow]"
            )
        return

    # Prepare conversion options
    options = {}

    # Get converter from registry
    converter = registry.get_converter(input_file)

    if not converter:
        console.print(
            f"[red]Error: Unsupported input format '{input_file.suffix}'[/red]"
        )

        # Show available formats
        formats = registry.list_supported_formats()
        if formats:
            console.print("[dim]Supported formats:[/dim]")
            for _name, format_info in formats.items():
                inputs = ", ".join(format_info["inputs"])
                console.print(f"[dim]  {inputs}[/dim]")
        return

    # PDF-specific options
    if page_range:
        options["page_range"] = page_range
    if metadata:
        options["include_metadata"] = True

    # Database-specific options
    if password:
        options["password"] = password
    if tables:
        options["tables"] = [t.strip() for t in tables.split(",")]
    if compression:
        options["compression"] = compression

    # Excel-specific options
    if combine:
        options["combine"] = True
    if separate:
        options["separate"] = True

    # XML-specific options
    if flatten_strategy:
        options["flatten_strategy"] = flatten_strategy
    if array_handling:
        options["array_handling"] = array_handling
    if namespace_handling:
        options["namespace_handling"] = namespace_handling
    if preview_schema:
        options["preview_schema"] = True

    # CSV-specific options
    if force_pyspark:
        options["force_pyspark"] = True

    # Pass verbose flag to converter
    options["verbose"] = verbose

    # Execute pre-conversion hooks from extensions
    if extension_manager:
        hook_results = extension_manager.execute_hook(
            "hook_pre_conversion",
            input_file=input_file,
            output_file=output_file,
            converter=converter,
            options=options,
        )
        if verbose and hook_results:
            console.print(
                f"[dim]Pre-conversion hooks executed: {len(hook_results)}[/dim]"
            )

    # Perform conversion
    try:
        success = converter.convert(input_file, output_file, **options)

        # Execute post-conversion hooks on success
        if success and extension_manager:
            hook_results = extension_manager.execute_hook(
                "hook_post_conversion",
                input_file=input_file,
                output_file=output_file,
                converter=converter,
                options=options,
                success=True,
            )
            if verbose and hook_results:
                console.print(
                    f"[dim]Post-conversion hooks executed: {len(hook_results)}[/dim]"
                )

        if not success:
            console.print("[red]Conversion failed![/red]")
            raise click.Abort()

    except Exception as e:
        # Execute error handling hooks
        if extension_manager:
            hook_results = extension_manager.execute_hook(
                "hook_error_handling",
                input_file=input_file,
                output_file=output_file,
                converter=converter,
                options=options,
                error=e,
            )
        raise


@cli.command()
@click.argument(
    "input_file", type=click.Path(exists=True, path_type=Path), metavar="INPUT_FILE"
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format: table (default) or json",
)
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
        console.print(
            f"[red]Error: Unsupported file format '{input_file.suffix}'[/red]"
        )
        return

    metadata = converter.get_metadata(input_file)

    if not metadata:
        console.print("[red]Could not extract metadata from file[/red]")
        return

    if output_format == "json":
        import json

        console.print(json.dumps(metadata, indent=2))
    else:
        # Display as table
        table = Table(title=f"File Information: {input_file.name}")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        for key, value in metadata.items():
            # Format the key for display
            display_key = key.replace("_", " ").title()

            # Format the value
            if key == "file_size":
                display_value = f"{value:,} bytes"
            elif key == "page_count":
                display_value = f"{value} pages"
            else:
                display_value = str(value) if value else "N/A"

            table.add_row(display_key, display_value)

        console.print(table)


@cli.command()
@click.pass_context
def list_extensions(ctx):
    """List all available extensions and their status.

    \b
    DESCRIPTION:
        Display information about all discovered PyForge CLI extensions,
        including their load status, version, and any errors encountered.

    \b
    OUTPUT:
        • Extension name and version
        • Load status (loaded, failed, disabled)
        • Load time for successful extensions
        • Error details for failed extensions
        • Dependencies information

    \b
    EXAMPLES:
        # List all extensions
        pyforge list-extensions

        # Use with verbose for more details
        pyforge --verbose list-extensions

    \b
    NOTES:
        • Extensions are discovered via Python entry points
        • Failed extensions show error details
        • Disabled extensions can be re-enabled
    """
    extension_manager = ctx.obj.get("extension_manager")
    if not extension_manager:
        console.print("[yellow]Extension system not initialized[/yellow]")
        return

    extension_info = extension_manager.get_extension_info()

    if not extension_info:
        console.print("[yellow]No extensions discovered[/yellow]")
        return

    table = Table(title="PyForge CLI Extensions")
    table.add_column("Extension", style="blue")
    table.add_column("Version", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Load Time", style="dim")
    table.add_column("Details", style="dim")

    for name, info in extension_info.items():
        # Format status with color
        status = info["state"]
        if status == "loaded":
            status_str = "[green][OK] Loaded[/green]"
        elif status == "failed":
            status_str = "[red][FAIL] Failed[/red]"
        elif status == "disabled":
            status_str = "[yellow]- Disabled[/yellow]"
        else:
            status_str = f"[dim]{status}[/dim]"

        # Format load time
        load_time_str = ""
        if info["load_time"]:
            load_time_str = f"{info['load_time']:.2f}s"

        # Format details
        details = []
        if info["description"]:
            details.append(
                info["description"][:50] + "..."
                if len(info["description"]) > 50
                else info["description"]
            )
        if info["error"]:
            details.append(f"[red]Error: {info['error']}[/red]")
        if not info["enabled"] and status == "loaded":
            details.append("[yellow]Disabled by user[/yellow]")

        details_str = "\n".join(details) if details else ""

        table.add_row(
            name, info["version"] or "Unknown", status_str, load_time_str, details_str
        )

    console.print(table)

    # Show summary
    loaded_count = sum(
        1 for info in extension_info.values() if info["state"] == "loaded"
    )
    failed_count = sum(
        1 for info in extension_info.values() if info["state"] == "failed"
    )

    console.print(
        f"\n[dim]Total: {len(extension_info)} extension(s) discovered, "
        f"{loaded_count} loaded, {failed_count} failed[/dim]"
    )

    if ctx.obj.get("verbose"):
        console.print("\n[dim]Entry points checked: pyforge_cli.extensions[/dim]")


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
        inputs = ", ".join(sorted(format_info["inputs"]))
        outputs = ", ".join(sorted(format_info["outputs"]))

        table.add_row(converter_name.title(), inputs, outputs)

    console.print(table)

    # Show loaded plugins
    loaded_plugins = plugin_loader.get_loaded_plugins()
    if loaded_plugins:
        console.print(f"\n[dim]Loaded plugins: {', '.join(loaded_plugins)}[/dim]")


@cli.command()
@click.argument(
    "input_file", type=click.Path(exists=True, path_type=Path), metavar="INPUT_FILE"
)
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
                echo "[OK] $file is valid"
            else
                echo "[FAIL] $file is invalid"
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
        [OK] document.pdf is a valid PDF file

        Invalid file:
        [FAIL] corrupted.pdf is not a valid PDF file

    \b
    NOTES:
        • Validation is fast and doesn't modify files
        • Use before batch processing to filter valid files
        • Supports all formats that have converters loaded
        • Returns appropriate exit codes for scripting
    """
    converter = registry.get_converter(input_file)

    if not converter:
        console.print(
            f"[red]Error: Unsupported file format '{input_file.suffix}'[/red]"
        )
        return

    is_valid = converter.validate_input(input_file)

    if is_valid:
        console.print(
            f"[green][OK] {input_file.name} is a valid {input_file.suffix.upper()} file[/green]"
        )
    else:
        console.print(
            f"[red][FAIL] {input_file.name} is not a valid {input_file.suffix.upper()} file[/red]"
        )
        raise click.Abort()


@cli.group()
def install():
    """Install prerequisites for specific file format converters.

    \b
    DESCRIPTION:
        Install and configure prerequisites needed for processing specific file formats.
        Each installer provides an interactive setup wizard to guide you through
        the installation process.

    \b
    AVAILABLE INSTALLERS:
        mdf-tools    Install Docker Desktop and SQL Server Express for MDF files

    \b
    EXAMPLES:
        # Install MDF processing tools
        pyforge install mdf-tools

        # Install with custom settings
        pyforge install mdf-tools --password "MySecure123!" --port 1433

    \b
    NOTES:
        • Installers are interactive and will guide you through each step
        • Most installers require administrator privileges for system changes
        • Configuration is saved to ~/.pyforge/ directory
        • Use corresponding management commands after installation
    """
    pass


@install.command("sample-datasets")
@click.argument(
    "path", type=click.Path(path_type=Path), required=False, metavar="[PATH]"
)
@click.option(
    "--version",
    "-v",
    metavar="VERSION",
    help="Specific release version to install (e.g., v1.0.0)",
)
@click.option(
    "--formats",
    "-f",
    metavar="FORMATS",
    help="Comma-separated list of formats to install (e.g., pdf,excel,xml)",
)
@click.option(
    "--sizes",
    "-s",
    metavar="SIZES",
    help="Comma-separated list of sizes to install: small,medium,large",
)
@click.option(
    "--list-releases", "-l", is_flag=True, help="List all available dataset releases"
)
@click.option(
    "--list-installed", is_flag=True, help="Show currently installed datasets"
)
@click.option("--force", is_flag=True, help="Force overwrite existing datasets")
@click.option("--uninstall", is_flag=True, help="Remove installed datasets")
@click.pass_context
def install_sample_datasets(
    ctx, path, version, formats, sizes, list_releases, list_installed, force, uninstall
):
    """Install curated sample datasets for testing PyForge CLI converters.

    \\b
    DESCRIPTION:
        Download and install curated test datasets from GitHub releases.
        Datasets cover all supported PyForge CLI formats with various sizes
        and edge cases for comprehensive testing.

    \\b
    ARGUMENTS:
        PATH            Target directory for datasets (default: ./sample-datasets)

    \\b
    SUPPORTED FORMATS:
        • PDF           Government documents and technical reports
        • Excel         Multi-sheet business and analytical workbooks
        • XML           RSS feeds, patents, and bibliographic data
        • Access        Sample business databases (.mdb/.accdb)
        • DBF           Geographic and census data files
        • MDF           SQL Server sample databases
        • CSV           Classic machine learning datasets

    \\b
    SIZE CATEGORIES:
        • Small         <100MB - Quick testing and typical use cases
        • Medium        100MB-1GB - Moderate performance testing
        • Large         >1GB - Heavy performance testing

    \\b
    EXAMPLES:
        # Install all datasets to default location
        pyforge install sample-datasets

        # Install to custom directory
        pyforge install sample-datasets /path/to/datasets

        # Install specific formats only
        pyforge install sample-datasets --formats pdf,excel,xml

        # Install small and medium datasets only
        pyforge install sample-datasets --sizes small,medium

        # Install specific version
        pyforge install sample-datasets --version v1.2.0

        # List available releases
        pyforge install sample-datasets --list-releases

        # Show installed datasets
        pyforge install sample-datasets --list-installed

        # Force reinstall over existing datasets
        pyforge install sample-datasets --force

        # Remove installed datasets
        pyforge install sample-datasets --uninstall --force

    \\b
    DATASET SOURCES:
        • Direct Downloads: Government and academic sources
        • Kaggle API: Public machine learning datasets
        • Manual Collection: Curated business samples

    \\b
    QUICK START AFTER INSTALLATION:
        # Test PDF conversion
        pyforge convert sample-datasets/pdf/small/*.pdf

        # Test Excel conversion
        pyforge convert sample-datasets/excel/small/*.xlsx

        # Test database conversion
        pyforge convert sample-datasets/access/small/*.mdb

        # Validate all formats
        find sample-datasets -name "*.*" -exec pyforge validate {} \\;

    \\b
    NOTES:
        • Downloads use GitHub Releases API with progress tracking
        • All files include SHA256 checksums for integrity verification
        • Manifest file provides complete dataset metadata
        • Archives are automatically extracted after download
        • Use --force to overwrite existing installations
    """
    from .installers.sample_datasets_installer import SampleDatasetsInstaller

    verbose = ctx.obj.get("verbose", False)

    # Initialize installer with custom path if provided
    installer = SampleDatasetsInstaller(target_dir=path)

    # Handle list operations
    if list_releases:
        installer.display_available_releases()
        return

    if list_installed:
        installer.list_installed_datasets()
        return

    # Handle uninstall
    if uninstall:
        success = installer.uninstall_datasets(force=force)
        if not success:
            raise click.Abort()
        return

    # Parse format and size filters
    format_list = None
    if formats:
        format_list = [f.strip().lower() for f in formats.split(",")]
        valid_formats = ["pdf", "excel", "xml", "access", "dbf", "mdf", "csv"]
        invalid_formats = [f for f in format_list if f not in valid_formats]
        if invalid_formats:
            console.print(f"[red]Invalid formats: {', '.join(invalid_formats)}[/red]")
            console.print(f"[dim]Valid formats: {', '.join(valid_formats)}[/dim]")
            raise click.Abort()

    size_list = None
    if sizes:
        size_list = [s.strip().lower() for s in sizes.split(",")]
        valid_sizes = ["small", "medium", "large"]
        invalid_sizes = [s for s in size_list if s not in valid_sizes]
        if invalid_sizes:
            console.print(f"[red]Invalid sizes: {', '.join(invalid_sizes)}[/red]")
            console.print(f"[dim]Valid sizes: {', '.join(valid_sizes)}[/dim]")
            raise click.Abort()

    if verbose:
        console.print(f"[dim]Target directory: {installer.target_dir}[/dim]")
        if version:
            console.print(f"[dim]Version: {version}[/dim]")
        if format_list:
            console.print(f"[dim]Formats: {', '.join(format_list)}[/dim]")
        if size_list:
            console.print(f"[dim]Sizes: {', '.join(size_list)}[/dim]")

    # Perform installation
    success = installer.install_datasets(
        version=version, formats=format_list, sizes=size_list, force=force
    )

    if not success:
        console.print("[red]Installation failed![/red]")
        raise click.Abort()


@install.command("mdf-tools")
@click.option(
    "--password",
    metavar="PASSWORD",
    help="Custom SQL Server password (default: PyForge@2024!)",
)
@click.option(
    "--port", type=int, metavar="PORT", help="Custom SQL Server port (default: 1433)"
)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Run in non-interactive mode (for automation/testing)",
)
def install_mdf_tools(password, port, non_interactive):
    """Install Docker Desktop and SQL Server Express for MDF processing.

    \b
    DESCRIPTION:
        Interactive installer that sets up all prerequisites needed for
        converting SQL Server MDF files to Parquet format. This includes:
        • Docker Desktop installation (if needed)
        • SQL Server Express container setup
        • Configuration file creation
        • Connection validation

    \b
    INSTALLATION PROCESS:
        1. Check system requirements and Docker status
        2. Guide through Docker Desktop installation if needed
        3. Pull and configure SQL Server Express container
        4. Test database connectivity
        5. Save configuration for MDF converter

    \b
    EXAMPLES:
        # Interactive installation with defaults
        pyforge install mdf-tools

        # Custom SQL Server password
        pyforge install mdf-tools --password "MySecure123!"

        # Custom port and password
        pyforge install mdf-tools --password "MySecure123!" --port 1433

    \b
    SYSTEM REQUIREMENTS:
        • Windows 10+, macOS 10.15+, or Ubuntu 18.04+
        • At least 4GB RAM available for SQL Server container
        • Internet connection for downloading Docker images
        • Administrator privileges may be required

    \b
    AFTER INSTALLATION:
        Use these commands to manage the SQL Server container:
        • pyforge mdf-tools status    - Check container status
        • pyforge mdf-tools start     - Start SQL Server
        • pyforge mdf-tools stop      - Stop SQL Server
        • pyforge mdf-tools logs      - View container logs
    """
    from .installers.mdf_tools_installer import MdfToolsInstaller

    installer = MdfToolsInstaller()
    installer.non_interactive = non_interactive
    success = installer.interactive_install(custom_password=password, custom_port=port)

    if not success:
        console.print(
            "[red]Installation failed. Please check the errors above and try again.[/red]"
        )
        raise click.Abort()


@cli.group("mdf-tools")
def mdf_tools():
    """Manage SQL Server Express container for MDF file processing.

    \b
    DESCRIPTION:
        Commands to manage the Docker container running SQL Server Express
        that is used for MDF file conversion. The container must be installed
        first using 'pyforge install mdf-tools'.

    \b
    CONTAINER LIFECYCLE:
        status      Check Docker and SQL Server status
        start       Start the SQL Server container
        stop        Stop the SQL Server container
        restart     Restart the SQL Server container
        logs        View SQL Server container logs
        config      Display current configuration
        test        Test SQL Server connectivity
        uninstall   Remove container and clean up

    \b
    EXAMPLES:
        # Check if everything is running
        pyforge mdf-tools status

        # Start SQL Server for MDF processing
        pyforge mdf-tools start

        # View recent container logs
        pyforge mdf-tools logs

        # Test database connection
        pyforge mdf-tools test

    \b
    TROUBLESHOOTING:
        If you encounter issues:
        1. Check status: pyforge mdf-tools status
        2. View logs: pyforge mdf-tools logs
        3. Restart: pyforge mdf-tools restart
        4. Reinstall: pyforge mdf-tools uninstall && pyforge install mdf-tools
    """
    pass


@mdf_tools.command()
def status():
    """Check Docker and SQL Server status.

    Shows the current status of:
    • Docker Desktop installation and daemon
    • SQL Server Express container existence and state
    • Database connectivity and responsiveness
    • Configuration file presence
    """
    from rich.table import Table

    from .installers.mdf_tools_installer import MdfToolsInstaller

    installer = MdfToolsInstaller()
    status_info = installer.get_status()

    # Create status table
    status_table = Table(title="MDF Tools Status")
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="bold")
    status_table.add_column("Details", style="dim")

    def format_status(is_ok: bool) -> str:
        return "[green][OK] OK[/green]" if is_ok else "[red][FAIL] FAIL[/red]"

    status_table.add_row(
        "Docker Installed",
        format_status(status_info["docker_installed"]),
        (
            "Docker command available"
            if status_info["docker_installed"]
            else "Run: pyforge install mdf-tools"
        ),
    )

    status_table.add_row(
        "Docker Running",
        format_status(status_info["docker_running"]),
        (
            "Docker daemon responsive"
            if status_info["docker_running"]
            else "Start Docker Desktop"
        ),
    )

    status_table.add_row(
        "SQL Container Exists",
        format_status(status_info["sql_container_exists"]),
        (
            "Container created"
            if status_info["sql_container_exists"]
            else "Run: pyforge install mdf-tools"
        ),
    )

    status_table.add_row(
        "SQL Container Running",
        format_status(status_info["sql_container_running"]),
        (
            "Container active"
            if status_info["sql_container_running"]
            else "Run: pyforge mdf-tools start"
        ),
    )

    status_table.add_row(
        "SQL Server Responding",
        format_status(status_info["sql_server_responding"]),
        (
            "Database accessible"
            if status_info["sql_server_responding"]
            else "Check container logs"
        ),
    )

    status_table.add_row(
        "Configuration File",
        format_status(status_info["config_exists"]),
        "Settings saved" if status_info["config_exists"] else "Run installation",
    )

    console.print(status_table)

    # Overall status
    all_ok = all(
        [
            status_info["docker_installed"],
            status_info["docker_running"],
            status_info["sql_container_exists"],
            status_info["sql_container_running"],
            status_info["sql_server_responding"],
        ]
    )

    if all_ok:
        console.print(
            "\n[bold green][OK] All systems operational - ready for MDF processing![/bold green]"
        )
    else:
        console.print(
            "\n[bold red][FAIL] System not ready - see status above for issues[/bold red]"
        )


@mdf_tools.command()
def start():
    """Start the SQL Server container."""
    from .installers.mdf_tools_installer import MdfToolsInstaller

    installer = MdfToolsInstaller()
    success = installer.start_container()

    if not success:
        raise click.Abort()


@mdf_tools.command()
def stop():
    """Stop the SQL Server container."""
    from .installers.mdf_tools_installer import MdfToolsInstaller

    installer = MdfToolsInstaller()
    success = installer.stop_container()

    if not success:
        raise click.Abort()


@mdf_tools.command()
def restart():
    """Restart the SQL Server container."""
    from .installers.mdf_tools_installer import MdfToolsInstaller

    installer = MdfToolsInstaller()
    success = installer.restart_container()

    if not success:
        raise click.Abort()


@mdf_tools.command()
@click.option(
    "--lines",
    "-n",
    type=int,
    default=50,
    help="Number of log lines to show (default: 50)",
)
def logs(lines):
    """View SQL Server container logs.

    \b
    EXAMPLES:
        # Show last 50 lines (default)
        pyforge mdf-tools logs

        # Show last 100 lines
        pyforge mdf-tools logs --lines 100

        # Show last 10 lines
        pyforge mdf-tools logs -n 10
    """
    from .installers.mdf_tools_installer import MdfToolsInstaller

    installer = MdfToolsInstaller()
    installer.show_logs(lines=lines)


@mdf_tools.command()
def config():
    """Display current configuration."""
    import json

    from .installers.mdf_tools_installer import MdfToolsInstaller

    installer = MdfToolsInstaller()

    if not installer.config_path.exists():
        console.print(
            "[red]Configuration file not found. Run 'pyforge install mdf-tools' first.[/red]"
        )
        return

    try:
        with open(installer.config_path, encoding="utf-8") as f:
            config = json.load(f)

        console.print(f"[bold]Configuration file:[/bold] {installer.config_path}")
        console.print(json.dumps(config, indent=2))

    except Exception as e:
        console.print(f"[red]Error reading configuration: {e}[/red]")


@mdf_tools.command()
def test():
    """Test SQL Server connectivity."""
    from .installers.mdf_tools_installer import DOCKER_AVAILABLE, MdfToolsInstaller

    installer = MdfToolsInstaller()

    console.print("[ANALYZE] Testing SQL Server connection...")

    if not DOCKER_AVAILABLE:
        console.print(
            "[red][FAIL] Docker SDK not available. Run 'pyforge install mdf-tools' first.[/red]"
        )
        return

    try:
        import docker

        installer.docker_client = docker.from_env()

        if installer._test_sql_connection():
            console.print("[green][OK] SQL Server connection successful![/green]")
        else:
            console.print("[red][FAIL] SQL Server connection failed[/red]")
            console.print("Try: pyforge mdf-tools restart")

    except Exception as e:
        console.print(f"[red][FAIL] Connection test failed: {e}[/red]")


@mdf_tools.command()
def uninstall():
    """Remove SQL Server container and clean up all data."""
    from .installers.mdf_tools_installer import MdfToolsInstaller

    installer = MdfToolsInstaller()
    success = installer.uninstall()

    if not success:
        raise click.Abort()


if __name__ == "__main__":
    cli()
