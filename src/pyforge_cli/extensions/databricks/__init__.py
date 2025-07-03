"""
PyForge CLI Databricks Extension

This extension provides optimized data conversion capabilities for Databricks
environments with automatic detection of compute type and intelligent converter
selection.
"""

from .extension import DatabricksExtension
from .pyforge_databricks import PyForgeDatabricks

__all__ = ["DatabricksExtension", "PyForgeDatabricks"]
__version__ = "1.0.0"