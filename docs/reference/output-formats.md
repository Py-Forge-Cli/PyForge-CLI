# Output Formats Reference

*This section is under development.*

Comprehensive guide to all output formats supported by PyForge CLI.

## Coming Soon

Detailed output format specifications will be available in a future release.

## Current Output Formats

### Text (.txt)
- **Used for**: PDF conversion
- **Encoding**: UTF-8
- **Features**: Preserves line breaks and basic formatting

### Parquet (.parquet)
- **Used for**: Excel, MDB/ACCDB, DBF conversion
- **Compression**: SNAPPY (default), GZIP, LZ4, ZSTD
- **Features**: Column-oriented, highly compressed, fast read/write

## Format Details

For detailed information about each output format, see:

- [PDF to Text Converter](../converters/pdf-to-text.md)
- [Excel to Parquet Converter](../converters/excel-to-parquet.md)
- [Database Files Converter](../converters/database-files.md)
- [DBF Files Converter](../converters/dbf-files.md)

## Next Steps

- [CLI Reference](cli-reference.md) - Complete command documentation
- [Converters](../converters/index.md) - Format-specific conversion guides