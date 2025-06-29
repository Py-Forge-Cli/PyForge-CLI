"""Format converters package."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .base import BaseConverter
from .string_database_converter import StringTypeConverter, StringDatabaseConverter

# Database converters
from .mdb_converter import MDBConverter
from .dbf_converter import DBFConverter

# XML converter
from .xml import XmlConverter

# CSV converter
from .csv_converter import CSVConverter

# Conditionally import PySpark CSV converter
try:
    from .pyspark_csv_converter import PySparkCSVConverter
    HAS_PYSPARK_CONVERTER = True
except ImportError:
    HAS_PYSPARK_CONVERTER = False

# Conditionally import PDF converter (not yet implemented)
# try:
#     from .pdf_converter import PDFConverter
#     HAS_PDF_CONVERTER = True
# except ImportError:
#     HAS_PDF_CONVERTER = False

__all__ = [
    "BaseConverter", 
    "StringTypeConverter", 
    "StringDatabaseConverter",
    "MDBConverter",
    "DBFConverter",
    "CSVConverter",
    "XmlConverter",
    "get_csv_converter"
]

if HAS_PYSPARK_CONVERTER:
    __all__.append("PySparkCSVConverter")

# if HAS_PDF_CONVERTER:
#     __all__.append("PDFConverter")


def get_csv_converter(detect_environment: bool = True, force_pyspark: bool = False) -> BaseConverter:
    """
    Factory function to get the appropriate CSV converter.
    
    Args:
        detect_environment: Whether to detect Databricks environment
        force_pyspark: Whether to force using PySpark converter if available
        
    Returns:
        CSVConverter instance (either standard or PySpark-based)
    """
    logger = logging.getLogger(__name__)
    
    if not detect_environment and not force_pyspark:
        logger.debug("Using standard CSV converter (environment detection disabled)")
        return CSVConverter()
    
    if not HAS_PYSPARK_CONVERTER:
        logger.debug("PySpark converter not available, using standard CSV converter")
        return CSVConverter()
    
    try:
        # Create PySpark converter
        converter = PySparkCSVConverter()
        
        # Check if we should use it
        if converter.is_databricks or converter.pyspark_available and force_pyspark:
            logger.info("Using PySpark-based CSV converter")
            return converter
        else:
            logger.debug("Not in Databricks environment and force_pyspark not set")
            return CSVConverter()
    except Exception as e:
        logger.warning(f"Error initializing PySpark converter: {e}")
        logger.info("Falling back to standard CSV converter")
        return CSVConverter()
