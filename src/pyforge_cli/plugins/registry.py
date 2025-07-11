"""Converter registry for managing format converters."""

from pathlib import Path
from typing import Dict, Optional, Set, Type

from ..converters.base import BaseConverter


class ConverterRegistry:
    """Registry for managing format converters."""

    def __init__(self):
        self._converters: Dict[str, Type[BaseConverter]] = {}
        self._input_formats: Dict[str, str] = {}  # extension -> converter_name
        self._output_formats: Dict[str, Set[str]] = (
            {}
        )  # converter_name -> output_extensions

    def register(self, name: str, converter_class: Type[BaseConverter]) -> None:
        """Register a converter class.

        Args:
            name: Unique name for the converter
            converter_class: Converter class to register
        """
        if not issubclass(converter_class, BaseConverter):
            raise ValueError(f"Converter {name} must inherit from BaseConverter")

        self._converters[name] = converter_class

        # Create temporary instance to get supported formats
        temp_instance = converter_class()

        # Map input formats to converter
        for input_ext in temp_instance.supported_inputs:
            self._input_formats[input_ext] = name

        # Map output formats
        self._output_formats[name] = temp_instance.supported_outputs

    def get_converter(self, input_path: Path) -> Optional[BaseConverter]:
        """Get appropriate converter for input file.

        Args:
            input_path: Path to input file

        Returns:
            BaseConverter instance or None if no suitable converter found
        """
        input_ext = input_path.suffix.lower()
        converter_name = self._input_formats.get(input_ext)

        if not converter_name:
            return None

        converter_class = self._converters.get(converter_name)
        if not converter_class:
            return None

        return converter_class()

    def get_converter_by_name(self, name: str) -> Optional[BaseConverter]:
        """Get converter by name.

        Args:
            name: Converter name

        Returns:
            BaseConverter instance or None if not found
        """
        converter_class = self._converters.get(name)
        if not converter_class:
            return None

        return converter_class()

    def list_supported_formats(self) -> Dict[str, Dict[str, Set[str]]]:
        """List all supported input and output formats.

        Returns:
            Dict mapping converter names to their supported formats
        """
        formats = {}

        for name, converter_class in self._converters.items():
            temp_instance = converter_class()
            formats[name] = {
                "inputs": temp_instance.supported_inputs,
                "outputs": temp_instance.supported_outputs,
            }

        return formats

    def supports_input(self, input_path: Path) -> bool:
        """Check if input format is supported.

        Args:
            input_path: Path to input file

        Returns:
            True if format is supported
        """
        input_ext = input_path.suffix.lower()
        return input_ext in self._input_formats

    def supports_conversion(self, input_path: Path, output_format: str) -> bool:
        """Check if conversion from input to output format is supported.

        Args:
            input_path: Path to input file
            output_format: Desired output format (without dot)

        Returns:
            True if conversion is supported
        """
        input_ext = input_path.suffix.lower()
        converter_name = self._input_formats.get(input_ext)

        if not converter_name:
            return False

        output_ext = f".{output_format.lower()}"
        supported_outputs = self._output_formats.get(converter_name, set())

        return output_ext in supported_outputs

    def get_available_outputs(self, input_path: Path) -> Set[str]:
        """Get available output formats for input file.

        Args:
            input_path: Path to input file

        Returns:
            Set of supported output extensions
        """
        input_ext = input_path.suffix.lower()
        converter_name = self._input_formats.get(input_ext)

        if not converter_name:
            return set()

        return self._output_formats.get(converter_name, set())

    def unregister(self, name: str) -> bool:
        """Unregister a converter.

        Args:
            name: Converter name to unregister

        Returns:
            True if successfully unregistered
        """
        if name not in self._converters:
            return False

        # Remove from converters
        del self._converters[name]

        # Remove input format mappings
        to_remove = [
            ext for ext, conv_name in self._input_formats.items() if conv_name == name
        ]
        for ext in to_remove:
            del self._input_formats[ext]

        # Remove output format mappings
        if name in self._output_formats:
            del self._output_formats[name]

        return True

    def clear(self) -> None:
        """Clear all registered converters."""
        self._converters.clear()
        self._input_formats.clear()
        self._output_formats.clear()


# Global registry instance
registry = ConverterRegistry()
