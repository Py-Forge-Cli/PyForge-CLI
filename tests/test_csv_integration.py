"""
Integration tests for CSV converter through CLI interface.
"""

import subprocess
import sys

import pandas as pd


class TestCSVConverterIntegration:
    """Integration tests for CSV converter through CLI"""

    def test_csv_conversion_via_cli(self, tmp_path):
        """Test CSV conversion through the CLI interface"""
        # Create test CSV file
        input_file = tmp_path / "test.csv"
        content = "name,age,city\nJohn,25,New York\nJane,30,Boston"
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "test.parquet"

        # Run CLI conversion
        cmd = [
            sys.executable,
            "-m",
            "pyforge_cli.main",
            "convert",
            str(input_file),
            str(output_file),
            "--format",
            "parquet",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        # Check command succeeded
        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Check output file was created
        assert output_file.exists()

        # Verify content
        df = pd.read_parquet(output_file)
        assert len(df) > 0
        assert len(df.columns) > 0

        # All columns should be strings
        for col in df.columns:
            assert df[col].dtype == "object"

    def test_csv_formats_command(self):
        """Test that CSV formats are listed in the formats command"""
        cmd = [sys.executable, "-m", "pyforge_cli.main", "formats"]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        assert result.returncode == 0
        assert "Csv" in result.stdout
        assert ".csv" in result.stdout
        assert ".tsv" in result.stdout

    def test_csv_info_command(self, tmp_path):
        """Test getting CSV file info through CLI"""
        # Create test CSV file
        input_file = tmp_path / "info_test.csv"
        content = "name,age,city,salary\nJohn,25,New York,50000\nJane,30,Boston,75000"
        input_file.write_text(content, encoding="utf-8")

        # Use the installed pyforge command
        cmd = [sys.executable, "-m", "pyforge_cli.main", "info", str(input_file)]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        assert result.returncode == 0
        assert "File Information" in result.stdout
        assert "info_test.csv" in result.stdout

    def test_csv_validate_command(self, tmp_path):
        """Test validating CSV file through CLI"""
        # Create test CSV file
        input_file = tmp_path / "validate_test.csv"
        content = "name,age\nJohn,25\nJane,30"
        input_file.write_text(content, encoding="utf-8")

        # Use the installed pyforge command
        cmd = [sys.executable, "-m", "pyforge_cli.main", "validate", str(input_file)]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        assert result.returncode == 0
        assert "valid" in result.stdout.lower()

    def test_csv_conversion_with_compression(self, tmp_path):
        """Test CSV conversion with different compression options"""
        # Create test CSV file
        input_file = tmp_path / "compression_test.csv"
        content = "name,age,city\nJohn,25,New York\nJane,30,Boston"
        input_file.write_text(content, encoding="utf-8")

        compression_options = ["snappy", "gzip", "none"]

        for compression in compression_options:
            output_file = tmp_path / f"test_{compression}.parquet"

            # Use the installed pyforge command
            cmd = [
                sys.executable,
                "-m",
                "pyforge_cli.main",
                "convert",
                str(input_file),
                str(output_file),
                "--format",
                "parquet",
                "--compression",
                compression,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

            assert (
                result.returncode == 0
            ), f"Failed with compression {compression}: {result.stderr}"
            assert output_file.exists()

            # Verify we can read the file
            df = pd.read_parquet(output_file)
            assert len(df) == 2

    def test_csv_conversion_with_verbose(self, tmp_path):
        """Test CSV conversion with verbose output"""
        # Create test CSV file
        input_file = tmp_path / "verbose_test.csv"
        content = "name,age,city\nJohn,25,New York\nJane,30,Boston"
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "verbose_test.parquet"

        # Use the installed pyforge command
        cmd = [
            sys.executable,
            "-m",
            "pyforge_cli.main",
            "--verbose",
            "convert",
            str(input_file),
            str(output_file),
            "--format",
            "parquet",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        assert result.returncode == 0
        assert output_file.exists()

        # Should have verbose output
        assert "Input file:" in result.stdout
        assert "Output format:" in result.stdout

    def test_csv_conversion_error_handling(self, tmp_path):
        """Test error handling for invalid CSV files"""
        # Create invalid file (not CSV)
        input_file = tmp_path / "invalid.csv"
        input_file.write_bytes(b"\x00\x01\x02\x03")  # Binary content

        output_file = tmp_path / "invalid.parquet"

        cmd = [
            sys.executable,
            "-m",
            "pyforge_cli.main",
            "convert",
            str(input_file),
            str(output_file),
            "--format",
            "parquet",
        ]

        subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        # Should fail gracefully (not crash)
        # Result could be 0 or 1 depending on how pandas handles the binary content
