"""Base converter class for all format converters."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class BaseConverter(ABC):
    """Abstract base class for all format converters."""

    def __init__(self):
        self.supported_inputs = set()
        self.supported_outputs = set()

    @abstractmethod
    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """Convert input file to output format.

        Args:
            input_path: Path to input file
            output_path: Path to output file
            **options: Additional conversion options

        Returns:
            bool: True if conversion successful, False otherwise
        """
        pass

    @abstractmethod
    def validate_input(self, input_path: Path) -> bool:
        """Validate if input file can be processed.

        Args:
            input_path: Path to input file

        Returns:
            bool: True if file can be processed
        """
        pass

    def get_output_extension(self, output_format: str) -> str:
        """Get appropriate file extension for output format.

        Args:
            output_format: Target output format

        Returns:
            str: File extension (including dot)
        """
        format_extensions = {
            "txt": ".txt",
            "csv": ".csv",
            "json": ".json",
            "parquet": ".parquet",
            "xlsx": ".xlsx",
        }
        return format_extensions.get(output_format.lower(), f".{output_format.lower()}")

    def get_metadata(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from input file.

        Args:
            input_path: Path to input file

        Returns:
            Optional[Dict[str, Any]]: File metadata or None
        """
        return None
