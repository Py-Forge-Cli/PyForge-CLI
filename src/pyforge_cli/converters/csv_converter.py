"""
CSV to Parquet converter with automatic delimiter and encoding detection.
Converts all data to string format for consistency with PyForge CLI architecture.
"""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import chardet
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from rich.console import Console

from .base import BaseConverter
from .string_database_converter import StringTypeConverter


class CSVDialectDetector:
    """Detects CSV dialect (delimiter, quoting, etc.) from file content."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def detect_dialect(
        self, file_path: Path, encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        Auto-detect CSV dialect from file sample.

        Args:
            file_path: Path to CSV file
            encoding: File encoding to use

        Returns:
            Dictionary with detected dialect parameters
        """
        try:
            # Read sample from file
            with open(file_path, encoding=encoding, newline="") as f:
                # Read first 8KB for dialect detection
                sample = f.read(8192)

            if not sample.strip():
                raise ValueError("File appears to be empty")

            # Use CSV sniffer for automatic detection
            sniffer = csv.Sniffer()

            # Try to detect delimiter
            delimiter = self._detect_delimiter(sample, sniffer)

            # Try to detect quoting
            quoting, quote_char = self._detect_quoting(sample, delimiter)

            # Detect if first row is header
            has_header = self._detect_header(sample, delimiter)

            return {
                "delimiter": delimiter,
                "quotechar": quote_char,
                "quoting": quoting,
                "has_header": has_header,
                "lineterminator": "\n",
                "skipinitialspace": True,
            }

        except Exception as e:
            self.logger.warning(f"Dialect detection failed: {e}. Using defaults.")
            return self._get_default_dialect()

    def _detect_delimiter(self, sample: str, sniffer: csv.Sniffer) -> str:
        """Detect the delimiter character."""
        common_delimiters = [",", ";", "\t", "|", ":", " "]

        try:
            # Try CSV sniffer first
            dialect = sniffer.sniff(sample, delimiters=",;\t|")
            return dialect.delimiter
        except Exception:
            # Fallback: count occurrences of common delimiters
            delimiter_counts = {}
            lines = sample.split("\n")[:10]  # Check first 10 lines

            for delimiter in common_delimiters:
                if delimiter == "\t":
                    actual_delim = "\t"
                else:
                    actual_delim = delimiter

                # Count occurrences in each line
                counts = [line.count(actual_delim) for line in lines if line.strip()]
                if counts:
                    # Good delimiter should have consistent count across lines
                    avg_count = sum(counts) / len(counts)
                    consistency = 1.0 - (max(counts) - min(counts)) / (max(counts) + 1)
                    score = avg_count * consistency
                    delimiter_counts[delimiter] = score

            if delimiter_counts:
                best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
                return "\t" if best_delimiter == "\t" else best_delimiter

            # Final fallback
            return ","

    def _detect_quoting(self, sample: str, delimiter: str) -> Tuple[int, str]:
        """Detect quoting style and quote character."""
        quote_chars = ['"', "'"]

        for quote_char in quote_chars:
            if quote_char in sample:
                # Count quoted fields
                lines = sample.split("\n")[:5]
                quoted_fields = 0
                total_fields = 0

                for line in lines:
                    if line.strip():
                        fields = line.split(delimiter)
                        total_fields += len(fields)
                        for field in fields:
                            field = field.strip()
                            if field.startswith(quote_char) and field.endswith(
                                quote_char
                            ):
                                quoted_fields += 1

                # If significant portion is quoted, use QUOTE_MINIMAL
                if total_fields > 0 and quoted_fields / total_fields > 0.1:
                    return csv.QUOTE_MINIMAL, quote_char

        return csv.QUOTE_MINIMAL, '"'

    def _detect_header(self, sample: str, delimiter: str) -> bool:
        """Detect if first row contains headers."""
        lines = sample.split("\n")
        if len(lines) < 2:
            return False

        first_row = lines[0].strip()
        second_row = lines[1].strip()

        if not first_row or not second_row:
            return False

        try:
            # Split rows by delimiter
            first_fields = [
                field.strip().strip('"').strip("'")
                for field in first_row.split(delimiter)
            ]
            second_fields = [
                field.strip().strip('"').strip("'")
                for field in second_row.split(delimiter)
            ]

            if len(first_fields) != len(second_fields):
                return True  # Different field count suggests header

            # Check if first row looks like headers (non-numeric, descriptive)
            header_indicators = 0

            for field in first_fields:
                if field:
                    # Headers are typically non-numeric and descriptive
                    if not field.replace(".", "").replace("-", "").isdigit():
                        header_indicators += 1
                    # Common header patterns
                    if any(
                        word in field.lower()
                        for word in [
                            "id",
                            "name",
                            "date",
                            "time",
                            "count",
                            "total",
                            "amount",
                        ]
                    ):
                        header_indicators += 1

            # If most fields look like headers, assume it's a header row
            return header_indicators > len(first_fields) * 0.5

        except Exception:
            return True  # Default to assuming headers exist

    def _get_default_dialect(self) -> Dict[str, Any]:
        """Return default CSV dialect parameters."""
        return {
            "delimiter": ",",
            "quotechar": '"',
            "quoting": csv.QUOTE_MINIMAL,
            "has_header": True,
            "lineterminator": "\n",
            "skipinitialspace": True,
        }


class CSVEncodingDetector:
    """Detects character encoding of CSV files."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def detect_encoding(self, file_path: Path) -> Tuple[str, float]:
        """
        Auto-detect file encoding.

        Args:
            file_path: Path to CSV file

        Returns:
            Tuple of (encoding, confidence)
        """
        try:
            # Read sample of file for encoding detection
            with open(file_path, "rb") as f:
                # Read first 32KB for encoding detection
                raw_data = f.read(32768)

            if not raw_data:
                return "utf-8", 1.0

            # Use chardet for automatic detection
            detection = chardet.detect(raw_data)

            if detection and detection["encoding"]:
                encoding = detection["encoding"].lower()
                confidence = detection["confidence"]

                # Normalize common encoding names
                if encoding in ["ascii"]:
                    encoding = "utf-8"
                elif encoding in ["windows-1252", "cp1252"]:
                    encoding = "cp1252"
                elif encoding in ["iso-8859-1", "latin-1"]:
                    encoding = "latin-1"

                self.logger.debug(
                    f"Detected encoding: {encoding} (confidence: {confidence:.2f})"
                )
                return encoding, confidence

            # Fallback encodings to try
            fallback_encodings = ["utf-8", "cp1252", "latin-1", "utf-16"]

            for encoding in fallback_encodings:
                try:
                    raw_data.decode(encoding)
                    self.logger.debug(f"Fallback encoding successful: {encoding}")
                    return encoding, 0.8
                except UnicodeDecodeError:
                    continue

            # Final fallback
            return "utf-8", 0.5

        except Exception as e:
            self.logger.warning(f"Encoding detection failed: {e}. Using UTF-8.")
            return "utf-8", 0.5


class CSVConverter(BaseConverter):
    """
    CSV to Parquet converter with automatic delimiter and encoding detection.
    Converts all data to string format for consistency with PyForge CLI.
    """

    def __init__(self):
        super().__init__()
        self.supported_inputs = {".csv", ".tsv", ".txt"}
        self.supported_outputs = {".parquet"}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.console = Console()

        # Initialize detectors
        self.encoding_detector = CSVEncodingDetector()
        self.dialect_detector = CSVDialectDetector()
        self.string_converter = StringTypeConverter()

        # Conversion statistics
        self.stats = {
            "file_size": 0,
            "rows_processed": 0,
            "columns_detected": 0,
            "encoding_detected": "",
            "delimiter_detected": "",
            "has_header": False,
            "conversion_time": 0.0,
        }

    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """
        Convert CSV file to Parquet format.

        Args:
            input_path: Path to CSV file
            output_path: Path for output Parquet file
            **options: Conversion options (compression, force, etc.)

        Returns:
            True if conversion successful
        """
        import time

        start_time = time.time()

        try:
            self.logger.info(f"Starting CSV conversion: {input_path} -> {output_path}")

            # Validate input
            if not self.validate_input(input_path):
                self.logger.error(f"Invalid CSV file: {input_path}")
                return False

            # Get file size for progress tracking
            self.stats["file_size"] = input_path.stat().st_size

            # Detect encoding
            encoding, confidence = self.encoding_detector.detect_encoding(input_path)
            self.stats["encoding_detected"] = encoding

            if options.get("verbose"):
                self.console.print(
                    f"[dim]Detected encoding: {encoding} (confidence: {confidence:.2f})[/dim]"
                )

            # Detect CSV dialect
            dialect_params = self.dialect_detector.detect_dialect(input_path, encoding)
            self.stats["delimiter_detected"] = dialect_params["delimiter"]
            self.stats["has_header"] = dialect_params["has_header"]

            if options.get("verbose"):
                self.console.print(
                    f"[dim]Detected delimiter: '{dialect_params['delimiter']}', Headers: {dialect_params['has_header']}[/dim]"
                )

            # Read CSV file
            df = self._read_csv_file(
                input_path, encoding, dialect_params, options.get("verbose", False)
            )

            if df is None or df.empty:
                self.logger.warning("CSV file is empty or could not be read")
                return False

            self.stats["rows_processed"] = len(df)
            self.stats["columns_detected"] = len(df.columns)

            # Convert all data to strings
            if options.get("verbose"):
                self.console.print(
                    f"[dim]Converting {len(df)} rows to string format...[/dim]"
                )

            string_df = self.string_converter.convert_dataframe(df)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as Parquet
            self._save_parquet(string_df, output_path, **options)

            # Record timing
            self.stats["conversion_time"] = time.time() - start_time

            if options.get("verbose"):
                self._print_conversion_summary()

            self.logger.info(f"✓ CSV conversion completed: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"CSV conversion failed: {e}")
            if options.get("verbose"):
                self.console.print(f"[red]Error: {e}[/red]")
            return False

    def _read_csv_file(
        self,
        file_path: Path,
        encoding: str,
        dialect_params: Dict[str, Any],
        verbose: bool = False,
    ) -> Optional[pd.DataFrame]:
        """Read CSV file using detected parameters."""
        try:
            # Prepare pandas read_csv parameters
            read_params = {
                "sep": dialect_params["delimiter"],
                "encoding": encoding,
                "quotechar": dialect_params["quotechar"],
                "skipinitialspace": dialect_params["skipinitialspace"],
                "header": 0 if dialect_params["has_header"] else None,
                "dtype": str,  # Read everything as strings initially
                "na_filter": False,  # Don't convert to NaN, keep as strings
                "keep_default_na": False,  # Don't interpret 'NA', 'NULL' as NaN
            }

            # Handle tab delimiter
            if dialect_params["delimiter"] == "\t":
                read_params["sep"] = "\t"

            if verbose:
                self.console.print(
                    f"[dim]Reading CSV with parameters: {read_params}[/dim]"
                )

            # Read the CSV file
            df = pd.read_csv(file_path, **read_params)

            # If no headers detected, create generic column names
            if not dialect_params["has_header"]:
                df.columns = [f"Column_{i+1}" for i in range(len(df.columns))]

            # Clean column names (remove quotes, whitespace)
            df.columns = [str(col).strip().strip('"').strip("'") for col in df.columns]

            # Ensure no duplicate column names
            seen = set()
            new_columns = []
            for col in df.columns:
                if col in seen or not col:
                    counter = 1
                    new_col = (
                        f"{col}_duplicate_{counter}"
                        if col
                        else f"Column_{len(new_columns)+1}"
                    )
                    while new_col in seen:
                        counter += 1
                        new_col = (
                            f"{col}_duplicate_{counter}"
                            if col
                            else f"Column_{len(new_columns)+1}"
                        )
                    new_columns.append(new_col)
                    seen.add(new_col)
                else:
                    new_columns.append(col)
                    seen.add(col)

            df.columns = new_columns

            return df

        except Exception as e:
            self.logger.error(f"Failed to read CSV file: {e}")
            return None

    def _is_volume_path(self, path: Path) -> bool:
        """Check if a path is a Databricks Unity Catalog volume path."""
        return str(path).startswith("/Volumes/")

    def _save_parquet(
        self, df: pd.DataFrame, output_path: Path, **options: Any
    ) -> None:
        """Save DataFrame as Parquet with all string columns, handling volume paths safely."""
        try:
            compression = options.get("compression", "snappy")

            # Ensure all columns are strings
            for col in df.columns:
                df[col] = df[col].astype(str)

            # Create PyArrow schema with all string columns
            schema_fields = [(col, pa.string()) for col in df.columns]
            schema = pa.schema(schema_fields)

            # Convert to PyArrow table
            table = pa.Table.from_pandas(df, schema=schema)

            if self._is_volume_path(output_path):
                # Write to temporary file first, then copy to volume
                import shutil
                import tempfile

                with tempfile.NamedTemporaryFile(
                    suffix=".parquet", delete=False
                ) as tmp_file:
                    tmp_path = Path(tmp_file.name)

                    # Write Parquet file to temp location
                    pq.write_table(
                        table,
                        tmp_path,
                        compression=compression,
                        write_statistics=True,
                        use_dictionary=True,
                    )

                    # Copy to final destination
                    shutil.copy2(str(tmp_path), str(output_path))
                    tmp_path.unlink()  # Clean up temp file
            else:
                # Direct write for non-volume paths
                pq.write_table(
                    table,
                    output_path,
                    compression=compression,
                    write_statistics=True,
                    use_dictionary=True,
                )

        except Exception as e:
            self.logger.error(f"Failed to save Parquet file: {e}")
            raise

    def _print_conversion_summary(self) -> None:
        """Print summary of conversion process."""
        from rich.table import Table

        table = Table(title="CSV Conversion Summary")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("File Size", f"{self.stats['file_size']:,} bytes")
        table.add_row("Encoding Detected", self.stats["encoding_detected"])
        table.add_row("Delimiter Detected", repr(self.stats["delimiter_detected"]))
        table.add_row("Has Headers", str(self.stats["has_header"]))
        table.add_row("Rows Processed", f"{self.stats['rows_processed']:,}")
        table.add_row("Columns Detected", str(self.stats["columns_detected"]))
        table.add_row("Conversion Time", f"{self.stats['conversion_time']:.2f} seconds")

        # Add string conversion statistics
        conversion_summary = self.string_converter.get_conversion_summary()
        table.add_row(
            "Total Fields Converted",
            f"{conversion_summary['total_records'] * conversion_summary['total_fields']:,}",
        )
        table.add_row("Conversion Errors", str(conversion_summary["errors"]))
        table.add_row("Conversion Warnings", str(conversion_summary["warnings"]))

        self.console.print(table)

    def validate_input(self, input_path: Path) -> bool:
        """
        Validate if input file is a valid CSV.

        Args:
            input_path: Path to input file

        Returns:
            True if file can be processed
        """
        try:
            if not input_path.exists():
                return False

            if input_path.stat().st_size == 0:
                return False

            # Check file extension
            if input_path.suffix.lower() not in self.supported_inputs:
                return False

            # Try to detect encoding and read a small sample
            encoding, _ = self.encoding_detector.detect_encoding(input_path)

            with open(input_path, encoding=encoding, errors="ignore") as f:
                sample = f.read(1024)
                if not sample.strip():
                    return False

            return True

        except Exception as e:
            self.logger.debug(f"Validation failed for {input_path}: {e}")
            return False

    def get_metadata(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from CSV file.

        Args:
            input_path: Path to CSV file

        Returns:
            Dictionary with file metadata
        """
        try:
            if not self.validate_input(input_path):
                return None

            file_stat = input_path.stat()
            encoding, confidence = self.encoding_detector.detect_encoding(input_path)
            dialect_params = self.dialect_detector.detect_dialect(input_path, encoding)

            # Count rows quickly
            row_count = 0
            try:
                with open(input_path, encoding=encoding) as f:
                    row_count = sum(1 for _ in f)
                    if dialect_params["has_header"] and row_count > 0:
                        row_count -= 1  # Subtract header row
            except Exception:
                row_count = -1

            return {
                "file_name": input_path.name,
                "file_size": file_stat.st_size,
                "file_type": "CSV",
                "encoding": encoding,
                "encoding_confidence": confidence,
                "delimiter": dialect_params["delimiter"],
                "has_header": dialect_params["has_header"],
                "estimated_rows": row_count,
                "last_modified": file_stat.st_mtime,
            }

        except Exception as e:
            self.logger.debug(f"Failed to extract metadata from {input_path}: {e}")
            return None
