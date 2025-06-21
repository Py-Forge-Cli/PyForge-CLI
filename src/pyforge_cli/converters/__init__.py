"""Format converters package."""

from .base import BaseConverter
from .string_database_converter import StringTypeConverter, StringDatabaseConverter

# Database converters
from .mdb_converter import MDBConverter
from .dbf_converter import DBFConverter

# XML converter
from .xml import XmlConverter

# Conditionally import PDF converter (requires fitz)
try:
    from .pdf_converter import PDFConverter
    __all__ = [
        "BaseConverter", 
        "StringTypeConverter", 
        "StringDatabaseConverter",
        "MDBConverter",
        "DBFConverter", 
        "PDFConverter",
        "XmlConverter"
    ]
except ImportError:
    __all__ = [
        "BaseConverter", 
        "StringTypeConverter", 
        "StringDatabaseConverter",
        "MDBConverter",
        "DBFConverter",
        "XmlConverter"
    ]