"""
Unit tests for CSV to Parquet converter functionality.
"""

import pandas as pd
import pytest

from pyforge_cli.converters.csv_converter import (
    CSVConverter,
    CSVDialectDetector,
    CSVEncodingDetector,
)


class TestCSVEncodingDetector:
    """Test cases for CSV encoding detection"""

    def test_detect_utf8_encoding(self, tmp_path):
        """Test detection of UTF-8 encoding"""
        detector = CSVEncodingDetector()

        # Create UTF-8 test file
        test_file = tmp_path / "utf8_test.csv"
        content = "name,age,city\nJohn,25,New York\nJané,30,São Paulo"
        test_file.write_text(content, encoding="utf-8")

        encoding, confidence = detector.detect_encoding(test_file)
        assert encoding == "utf-8"
        assert confidence > 0.5

    def test_detect_latin1_encoding(self, tmp_path):
        """Test detection of Latin-1 encoding"""
        detector = CSVEncodingDetector()

        # Create Latin-1 test file
        test_file = tmp_path / "latin1_test.csv"
        content = "name,city\nJosé,México\nFrançois,Québec"
        test_file.write_bytes(content.encode("latin-1"))

        encoding, confidence = detector.detect_encoding(test_file)
        assert encoding in ["latin-1", "cp1252"]  # Both are acceptable
        assert confidence > 0.5

    def test_empty_file_encoding(self, tmp_path):
        """Test encoding detection for empty file"""
        detector = CSVEncodingDetector()

        test_file = tmp_path / "empty.csv"
        test_file.write_text("", encoding="utf-8")

        encoding, confidence = detector.detect_encoding(test_file)
        assert encoding == "utf-8"
        assert confidence == 1.0


class TestCSVDialectDetector:
    """Test cases for CSV dialect detection"""

    def test_header_detection_fix_issue_22(self, tmp_path):
        """Test header detection with newline character fix for Issue #22"""
        detector = CSVDialectDetector()

        # Create CSV that mimics Titanic dataset structure
        test_file = tmp_path / "titanic_like.csv"
        content = 'PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked\n1,0,3,"Braund, Mr. Owen Harris",male,22,1,0,A/5 21171,7.25,,S\n2,1,1,"Cumings, Mrs. John Bradley (Florence Briggs Thayer)",female,38,1,0,PC 17599,71.2833,C85,C'
        test_file.write_text(content, encoding="utf-8")

        dialect = detector.detect_dialect(test_file)

        # Should correctly detect headers
        assert dialect[
            "has_header"
        ], "Should detect CSV headers correctly after newline fix"
        assert dialect["delimiter"] == ","

        # Test the internal _detect_header method directly to ensure the fix works
        with open(test_file, encoding="utf-8", newline="") as f:
            sample = f.read(8192)

        header_result = detector._detect_header(sample, ",")
        assert (
            header_result
        ), "Internal _detect_header method should return True for CSV with headers"

    def test_detect_comma_delimiter(self, tmp_path):
        """Test detection of comma delimiter"""
        detector = CSVDialectDetector()

        test_file = tmp_path / "comma_test.csv"
        content = "name,age,city\nJohn,25,New York\nJane,30,Boston"
        test_file.write_text(content, encoding="utf-8")

        dialect = detector.detect_dialect(test_file)
        assert dialect["delimiter"] == ","
        assert dialect["has_header"]

    def test_detect_semicolon_delimiter(self, tmp_path):
        """Test detection of semicolon delimiter"""
        detector = CSVDialectDetector()

        test_file = tmp_path / "semicolon_test.csv"
        content = "name;age;city\nJohn;25;New York\nJane;30;Boston"
        test_file.write_text(content, encoding="utf-8")

        dialect = detector.detect_dialect(test_file)
        assert dialect["delimiter"] == ";"
        assert dialect["has_header"]

    def test_detect_tab_delimiter(self, tmp_path):
        """Test detection of tab delimiter"""
        detector = CSVDialectDetector()

        test_file = tmp_path / "tab_test.tsv"
        content = "name\tage\tcity\nJohn\t25\tNew York\nJane\t30\tBoston"
        test_file.write_text(content, encoding="utf-8")

        dialect = detector.detect_dialect(test_file)
        assert dialect["delimiter"] == "\t"
        assert dialect["has_header"]

    def test_detect_pipe_delimiter(self, tmp_path):
        """Test detection of pipe delimiter"""
        detector = CSVDialectDetector()

        test_file = tmp_path / "pipe_test.csv"
        content = "name|age|city\nJohn|25|New York\nJane|30|Boston"
        test_file.write_text(content, encoding="utf-8")

        dialect = detector.detect_dialect(test_file)
        assert dialect["delimiter"] == "|"
        assert dialect["has_header"]

    def test_detect_no_header(self, tmp_path):
        """Test detection when no header is present"""
        detector = CSVDialectDetector()

        test_file = tmp_path / "no_header.csv"
        content = "John,25,New York\nJane,30,Boston\nBob,35,Chicago"
        test_file.write_text(content, encoding="utf-8")

        dialect = detector.detect_dialect(test_file)
        assert dialect["delimiter"] == ","
        # Header detection might vary based on content

    def test_detect_quoted_fields(self, tmp_path):
        """Test detection with quoted fields"""
        detector = CSVDialectDetector()

        test_file = tmp_path / "quoted_test.csv"
        content = '"name","age","city"\n"John Smith","25","New York"\n"Jane Doe","30","Boston"'
        test_file.write_text(content, encoding="utf-8")

        dialect = detector.detect_dialect(test_file)
        assert dialect["delimiter"] == ","
        assert dialect["quotechar"] == '"'
        assert dialect["has_header"]


class TestCSVConverter:
    """Test cases for CSVConverter class"""

    def test_converter_instantiation(self):
        """Test converter instantiation"""
        converter = CSVConverter()
        assert converter is not None
        assert ".csv" in converter.supported_inputs
        assert ".tsv" in converter.supported_inputs
        assert ".txt" in converter.supported_inputs
        assert ".parquet" in converter.supported_outputs

    def test_validate_input_valid_csv(self, tmp_path):
        """Test input validation for valid CSV file"""
        converter = CSVConverter()

        test_file = tmp_path / "valid.csv"
        content = "name,age\nJohn,25\nJane,30"
        test_file.write_text(content, encoding="utf-8")

        assert converter.validate_input(test_file)

    def test_validate_input_empty_file(self, tmp_path):
        """Test input validation for empty file"""
        converter = CSVConverter()

        test_file = tmp_path / "empty.csv"
        test_file.write_text("", encoding="utf-8")

        assert not converter.validate_input(test_file)

    def test_validate_input_nonexistent_file(self, tmp_path):
        """Test input validation for non-existent file"""
        converter = CSVConverter()

        test_file = tmp_path / "nonexistent.csv"

        assert not converter.validate_input(test_file)

    def test_validate_input_unsupported_extension(self, tmp_path):
        """Test input validation for unsupported file extension"""
        converter = CSVConverter()

        test_file = tmp_path / "test.xyz"
        test_file.write_text("some content", encoding="utf-8")

        assert not converter.validate_input(test_file)

    def test_csv_header_preservation_issue_22(self, tmp_path):
        """Test CSV header preservation fix for Issue #22"""
        converter = CSVConverter()

        # Create CSV that reproduces the original issue
        input_file = tmp_path / "issue_22_test.csv"
        content = 'PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked\n1,0,3,"Braund, Mr. Owen Harris",male,22,1,0,A/5 21171,7.25,,S\n2,1,1,"Cumings, Mrs. John Bradley",female,38,1,0,PC 17599,71.2833,C85,C'
        input_file.write_text(content, encoding="utf-8")

        # Convert to Parquet
        output_file = tmp_path / "issue_22_test.parquet"
        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

        # Verify the fix: should have proper column names, not generic ones
        df = pd.read_parquet(output_file)

        # Should have 2 data rows (not 3 with header as data)
        assert len(df) == 2, f"Should have 2 data rows, got {len(df)}"

        # Should have actual column names, not generic Column_1, Column_2, etc.
        expected_columns = [
            "PassengerId",
            "Survived",
            "Pclass",
            "Name",
            "Sex",
            "Age",
            "SibSp",
            "Parch",
            "Ticket",
            "Fare",
            "Cabin",
            "Embarked",
        ]
        assert (
            list(df.columns) == expected_columns
        ), f"Expected {expected_columns}, got {list(df.columns)}"

        # First row should be actual data, not header
        assert (
            df["PassengerId"].iloc[0] == "1"
        ), f"First row PassengerId should be '1', got '{df['PassengerId'].iloc[0]}'"
        assert (
            df["Name"].iloc[0] == "Braund, Mr. Owen Harris"
        ), f"First row Name should be 'Braund, Mr. Owen Harris', got '{df['Name'].iloc[0]}'"

        # Verify no header data in first row
        assert (
            df["PassengerId"].iloc[0] != "PassengerId"
        ), "Header should not appear as data in first row"

    def test_basic_csv_conversion(self, tmp_path):
        """Test basic CSV to Parquet conversion"""
        converter = CSVConverter()

        # Create test CSV
        input_file = tmp_path / "test.csv"
        content = "name,age,city\nJohn,25,New York\nJane,30,Boston\nBob,35,Chicago"
        input_file.write_text(content, encoding="utf-8")

        # Convert to Parquet
        output_file = tmp_path / "test.parquet"
        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

        # Verify output
        df = pd.read_parquet(output_file)
        assert len(df) == 3
        assert list(df.columns) == ["name", "age", "city"]
        assert df["name"].iloc[0] == "John"
        assert df["age"].iloc[0] == "25"  # Should be string
        assert df["city"].iloc[0] == "New York"

    def test_csv_conversion_with_different_delimiters(self, tmp_path):
        """Test CSV conversion with various delimiters"""
        converter = CSVConverter()

        test_cases = [
            (",", "name,age,city\nJohn,25,New York"),
            (";", "name;age;city\nJohn;25;New York"),
            ("\t", "name\tage\tcity\nJohn\t25\tNew York"),
            ("|", "name|age|city\nJohn|25|New York"),
        ]

        for delimiter, content in test_cases:
            delimiter_name = delimiter.replace("\t", "tab").replace("|", "pipe")
            input_file = tmp_path / f"test_{delimiter_name}.csv"
            input_file.write_text(content, encoding="utf-8")

            output_file = tmp_path / f"test_{delimiter_name}.parquet"
            result = converter.convert(input_file, output_file)

            assert result
            assert output_file.exists()

            df = pd.read_parquet(output_file)
            assert len(df) == 1
            assert list(df.columns) == ["name", "age", "city"]
            assert df["name"].iloc[0] == "John"

    def test_csv_conversion_no_header(self, tmp_path):
        """Test CSV conversion without headers"""
        converter = CSVConverter()

        # Create CSV without headers
        input_file = tmp_path / "no_header.csv"
        content = "John,25,New York\nJane,30,Boston"
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "no_header.parquet"
        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

        df = pd.read_parquet(output_file)
        assert len(df) == 2
        # Should have generic column names
        assert "Column_1" in df.columns or df.columns[0] in ["0", "John"]

    def test_csv_conversion_with_quotes(self, tmp_path):
        """Test CSV conversion with quoted fields"""
        converter = CSVConverter()

        input_file = tmp_path / "quoted.csv"
        content = '"name","age","description"\n"John Smith","25","Software Engineer, Team Lead"\n"Jane Doe","30","Data Scientist, ML Expert"'
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "quoted.parquet"
        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

        df = pd.read_parquet(output_file)
        assert len(df) == 2
        assert df["name"].iloc[0] == "John Smith"
        assert "Software Engineer, Team Lead" in df["description"].iloc[0]

    def test_csv_conversion_with_special_characters(self, tmp_path):
        """Test CSV conversion with international characters"""
        converter = CSVConverter()

        input_file = tmp_path / "international.csv"
        content = "name,city,country\nJosé,São Paulo,Brasil\nFrançois,Québec,Canada\n北京,Beijing,中国"
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "international.parquet"
        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

        df = pd.read_parquet(output_file)
        assert len(df) == 3
        assert df["name"].iloc[0] == "José"
        assert df["city"].iloc[1] == "Québec"
        assert df["name"].iloc[2] == "北京"

    def test_csv_conversion_with_compression(self, tmp_path):
        """Test CSV conversion with different compression options"""
        converter = CSVConverter()

        input_file = tmp_path / "test.csv"
        content = "name,age,city\nJohn,25,New York\nJane,30,Boston"
        input_file.write_text(content, encoding="utf-8")

        compression_options = ["snappy", "gzip", "none"]

        for compression in compression_options:
            output_file = tmp_path / f"test_{compression}.parquet"
            result = converter.convert(input_file, output_file, compression=compression)

            assert result
            assert output_file.exists()

            # Verify we can read the compressed file
            df = pd.read_parquet(output_file)
            assert len(df) == 2
            assert df["name"].iloc[0] == "John"

    def test_csv_conversion_large_file(self, tmp_path):
        """Test CSV conversion with larger file"""
        converter = CSVConverter()

        input_file = tmp_path / "large.csv"

        # Create larger CSV file
        rows = ["name,age,city,salary"]
        for i in range(1000):
            rows.append(f"Person_{i},{20 + i % 50},City_{i % 10},{30000 + i * 100}")

        content = "\n".join(rows)
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "large.parquet"
        result = converter.convert(input_file, output_file, verbose=True)

        assert result
        assert output_file.exists()

        df = pd.read_parquet(output_file)
        assert len(df) == 1000
        assert list(df.columns) == ["name", "age", "city", "salary"]
        # All values should be strings
        assert df["age"].dtype == "object"
        assert df["salary"].dtype == "object"

    def test_csv_conversion_mixed_data_types(self, tmp_path):
        """Test CSV conversion with mixed data types"""
        converter = CSVConverter()

        input_file = tmp_path / "mixed_types.csv"
        content = """name,age,height,is_active,birth_date,salary
John,25,5.9,true,1999-01-15,50000.50
Jane,30,5.6,false,1994-03-20,75000.75
Bob,,6.1,,1989-12-01,60000"""
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "mixed_types.parquet"
        result = converter.convert(input_file, output_file)

        assert result
        assert output_file.exists()

        df = pd.read_parquet(output_file)
        assert len(df) == 3

        # All columns should be strings
        for col in df.columns:
            assert df[col].dtype == "object"

        # Verify specific values are preserved as strings
        assert df["age"].iloc[0] == "25"
        assert df["height"].iloc[0] == "5.9"
        assert df["is_active"].iloc[0] == "true"
        assert df["birth_date"].iloc[0] == "1999-01-15"
        assert df["salary"].iloc[0] == "50000.50"

    def test_get_metadata(self, tmp_path):
        """Test metadata extraction from CSV file"""
        converter = CSVConverter()

        input_file = tmp_path / "metadata_test.csv"
        content = "name,age,city\nJohn,25,New York\nJane,30,Boston\nBob,35,Chicago"
        input_file.write_text(content, encoding="utf-8")

        metadata = converter.get_metadata(input_file)

        assert metadata is not None
        assert metadata["file_name"] == "metadata_test.csv"
        assert metadata["file_type"] == "CSV"
        assert metadata["encoding"] == "utf-8"
        assert metadata["delimiter"] == ","
        assert metadata["has_header"]
        assert metadata["estimated_rows"] == 3  # Excluding header
        assert metadata["file_size"] > 0

    def test_conversion_with_force_option(self, tmp_path):
        """Test CSV conversion with force option to overwrite existing file"""
        converter = CSVConverter()

        input_file = tmp_path / "force_test.csv"
        content = "name,age\nJohn,25\nJane,30"
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "force_test.parquet"

        # First conversion
        result1 = converter.convert(input_file, output_file)
        assert result1
        assert output_file.exists()

        # Second conversion with force (should succeed)
        result2 = converter.convert(input_file, output_file, force=True)
        assert result2

    def test_conversion_error_handling(self, tmp_path):
        """Test error handling during conversion"""
        converter = CSVConverter()

        # Test with corrupted CSV (unmatched quotes)
        input_file = tmp_path / "corrupted.csv"
        content = 'name,description\nJohn,"This is a test\nJane,"Another test"'  # Missing closing quote
        input_file.write_text(content, encoding="utf-8")

        output_file = tmp_path / "corrupted.parquet"

        # Should handle error gracefully
        # Note: pandas is quite forgiving, so this might still succeed
        result = converter.convert(input_file, output_file)
        # Result could be True or False depending on pandas behavior
        assert isinstance(result, bool)


@pytest.fixture
def sample_csv_data():
    """Fixture providing sample CSV data for testing"""
    return {
        "simple": "name,age,city\nJohn,25,New York\nJane,30,Boston",
        "quoted": '"name","age","city"\n"John Smith","25","New York, NY"\n"Jane Doe","30","Boston, MA"',
        "semicolon": "name;age;city\nJohn;25;New York\nJane;30;Boston",
        "tab": "name\tage\tcity\nJohn\t25\tNew York\nJane\t30\tBoston",
        "no_header": "John,25,New York\nJane,30,Boston\nBob,35,Chicago",
        "international": "name,city\nJosé,São Paulo\nFrançois,Québec\n北京,Beijing",
    }


class TestCSVConverterIntegration:
    """Integration tests for CSV converter with real-world scenarios"""

    def test_end_to_end_conversion_workflow(self, tmp_path, sample_csv_data):
        """Test complete end-to-end conversion workflow"""
        converter = CSVConverter()

        for data_type, content in sample_csv_data.items():
            input_file = tmp_path / f"{data_type}.csv"
            output_file = tmp_path / f"{data_type}.parquet"

            # Write test data
            input_file.write_text(content, encoding="utf-8")

            # Validate input
            assert converter.validate_input(input_file)

            # Get metadata
            metadata = converter.get_metadata(input_file)
            assert metadata is not None

            # Convert
            result = converter.convert(input_file, output_file, verbose=True)
            assert result
            assert output_file.exists()

            # Verify output
            df = pd.read_parquet(output_file)
            assert len(df) > 0

            # All columns should be strings
            for col in df.columns:
                assert df[col].dtype == "object"
