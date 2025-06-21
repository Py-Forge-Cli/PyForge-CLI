# CLI Reference

<div align="center">
  <img src="../assets/icon_pyforge_forge.svg" alt="PyForge CLI" width="80" height="80">
</div>

Complete command-line interface documentation for PyForge CLI.

## Quick Navigation

<div class="grid cards" markdown>

-   :material-console: **CLI Commands**

    ---

    Complete command reference with examples

    [:octicons-arrow-right-24: CLI Reference](cli-reference.md)

-   :material-table: **Options Matrix**

    ---

    All options organized by converter type

    [:octicons-arrow-right-24: Options Matrix](options.md)

-   :material-file-export: **Output Formats**

    ---

    Detailed information about output formats

    [:octicons-arrow-right-24: Output Formats](output-formats.md)

</div>

## Command Overview

PyForge CLI provides these main commands:

| Command | Purpose | Example |
|---------|---------|---------|
| `convert` | Convert files between formats | `pyforge convert file.pdf` |
| `info` | Display file information | `pyforge info file.xlsx` |
| `validate` | Validate file compatibility | `pyforge validate file.mdb` |
| `formats` | List supported formats | `pyforge formats` |

## Global Options

These options work with all commands:

| Option | Description | Example |
|--------|-------------|---------|
| `--help` | Show help message | `pyforge --help` |
| `--version` | Show version information | `pyforge --version` |
| `--verbose` | Enable verbose output | `pyforge convert file.pdf --verbose` |

## Quick Reference Card

### Basic Conversions

```bash
# PDF to Text
pyforge convert document.pdf

# Excel to Parquet
pyforge convert spreadsheet.xlsx

# Access Database to Parquet
pyforge convert database.mdb

# DBF to Parquet
pyforge convert legacy.dbf
```

### File Information

```bash
# Get file details
pyforge info filename.ext

# Validate file
pyforge validate filename.ext

# List supported formats
pyforge formats
```

### Common Options

```bash
# With custom output
pyforge convert input.pdf output.txt

# Force overwrite
pyforge convert input.xlsx --force

# Verbose mode
pyforge convert input.mdb --verbose
```

## Command Structure

All PyForge CLI commands follow this structure:

```
pyforge <command> <input_file> [output_file] [options]
```

Where:
- `<command>`: One of convert, info, validate, formats
- `<input_file>`: Path to input file (required for most commands)
- `[output_file]`: Optional output file path
- `[options]`: Command-specific options

## Next Steps

- **[CLI Reference](cli-reference.md)** - Detailed command documentation
- **[Options Matrix](options.md)** - All options by converter
- **[Output Formats](output-formats.md)** - Output format specifications