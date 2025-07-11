"""
Unit tests for string database converter functionality.
"""

from datetime import date, datetime, time
from decimal import Decimal

import numpy as np
import pandas as pd
from cortexpy_cli.converters.string_database_converter import (
    ConversionStats,
    StringTypeConverter,
)


class TestStringTypeConverter:
    """Test cases for StringTypeConverter class"""

    def test_instantiation(self):
        """Test converter instantiation"""
        converter = StringTypeConverter()
        assert converter is not None
        assert isinstance(converter.stats, ConversionStats)

    def test_basic_type_conversions(self):
        """Test basic data type conversions"""
        converter = StringTypeConverter()

        test_cases = [
            # Numbers
            (42, "42"),
            (123.4, "123.4"),
            (123.45678, "123.45678"),
            (Decimal("999.12345"), "999.12345"),
            (-45.67, "-45.67"),
            (1000000, "1000000"),
            (0, "0"),
            (0.0, "0.0"),
            # Dates
            (datetime(2024, 3, 15, 14, 30, 0), "2024-03-15 14:30:00"),
            (date(2024, 3, 15), "2024-03-15"),
            (time(14, 30, 0), "14:30:00"),
            # Booleans
            (True, "true"),
            (False, "false"),
            # Special values
            (None, ""),
            ("", ""),
            ("Hello World", "Hello World"),
        ]

        for input_val, expected in test_cases:
            result = converter.convert_value(input_val)
            assert (
                result == expected
            ), f"Failed for {input_val}: got {result}, expected {expected}"

    def test_special_numeric_values(self):
        """Test special numeric values"""
        converter = StringTypeConverter()

        # Infinity
        assert converter.convert_value(float("inf")) == "Infinity"
        assert converter.convert_value(float("-inf")) == "-Infinity"

        # NaN
        assert converter.convert_value(float("nan")) == ""
        assert converter.convert_value(np.nan) == ""

    def test_binary_conversion(self):
        """Test binary data conversion"""
        converter = StringTypeConverter()

        binary_data = b"Hello, World!"
        result = converter.convert_value(binary_data)

        # Should be valid base64
        import base64

        decoded = base64.b64decode(result)
        assert decoded == binary_data

    def test_dataframe_conversion(self):
        """Test DataFrame conversion"""
        converter = StringTypeConverter()

        # Create test DataFrame with mixed types
        test_data = {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "salary": [50000.50, 60000.75, 70000.00],
            "is_active": [True, False, True],
            "hire_date": [
                datetime(2020, 1, 15),
                datetime(2019, 6, 20),
                datetime(2021, 3, 10),
            ],
        }

        df = pd.DataFrame(test_data)
        string_df = converter.convert_dataframe(df)

        # Check all columns are strings
        assert all(dtype == "object" for dtype in string_df.dtypes)

        # Check specific conversions
        assert string_df.loc[0, "id"] == "1"
        assert string_df.loc[0, "salary"] == "50000.5"
        assert string_df.loc[0, "is_active"] == "true"
        assert string_df.loc[0, "hire_date"] == "2020-01-15 00:00:00"

    def test_error_handling(self):
        """Test error handling for problematic values"""
        converter = StringTypeConverter()

        # Test with object that can't be converted
        class BadObject:
            def __str__(self):
                raise ValueError("Cannot convert")

            def __repr__(self):
                raise ValueError("Cannot represent")

        bad_obj = BadObject()
        result = converter.convert_value(bad_obj)
        assert result == "[CONVERSION_ERROR]"

        # Check error was recorded
        summary = converter.get_conversion_summary()
        assert summary["errors"] > 0

    def test_conversion_statistics(self):
        """Test conversion statistics tracking"""
        converter = StringTypeConverter()

        # Convert various types
        test_values = [42, "text", True, None, 3.14, datetime.now()]
        for val in test_values:
            converter.convert_value(val)

        summary = converter.get_conversion_summary()
        assert summary["conversions_by_type"]
        assert len(summary["conversions_by_type"]) > 0
        assert isinstance(summary["errors"], int)
        assert isinstance(summary["warnings"], int)


class TestStringDatabaseConverter:
    """Test cases for StringDatabaseConverter base class"""

    def test_instantiation(self):
        """Test base converter instantiation"""
        # StringDatabaseConverter is abstract, so we test with a concrete subclass
        from cortexpy_cli.converters.mdb_converter import MDBConverter

        converter = MDBConverter()
        assert converter is not None
        assert hasattr(converter, "string_converter")
        assert isinstance(converter.string_converter, StringTypeConverter)

    def test_supported_formats(self):
        """Test supported formats method"""
        from cortexpy_cli.converters.dbf_converter import DBFConverter
        from cortexpy_cli.converters.mdb_converter import MDBConverter

        mdb_converter = MDBConverter()
        dbf_converter = DBFConverter()

        assert ".mdb" in mdb_converter.get_supported_formats()
        assert ".accdb" in mdb_converter.get_supported_formats()
        assert ".dbf" in dbf_converter.get_supported_formats()

    def test_conversion_report(self):
        """Test conversion report generation"""
        from cortexpy_cli.converters.mdb_converter import MDBConverter

        converter = MDBConverter()

        # Initial report should show no conversions
        report = converter.get_conversion_report()
        assert report["status"] == "no_conversions"


class TestConversionStats:
    """Test ConversionStats dataclass"""

    def test_instantiation(self):
        """Test ConversionStats instantiation"""
        stats = ConversionStats()
        assert stats.total_records == 0
        assert stats.total_fields == 0
        assert isinstance(stats.conversions_by_type, dict)
        assert isinstance(stats.errors, list)
        assert isinstance(stats.warnings, list)

    def test_with_data(self):
        """Test ConversionStats with data"""
        stats = ConversionStats(
            total_records=100,
            total_fields=5,
            conversions_by_type={"string": 50, "integer": 30},
            errors=["Error 1"],
            warnings=["Warning 1"],
        )

        assert stats.total_records == 100
        assert stats.total_fields == 5
        assert stats.conversions_by_type["string"] == 50
        assert len(stats.errors) == 1
        assert len(stats.warnings) == 1
