"""Base extension class for PyForge CLI extensions."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class BaseExtension(ABC):
    """Abstract base class for PyForge CLI extensions.

    This class defines the interface that all PyForge CLI extensions must implement.
    Extensions can add new functionality, provide environment-specific optimizations,
    or integrate with external services.

    Example:
        from pyforge_cli.extensions.base import BaseExtension

        class DatabricksExtension(BaseExtension):
            def __init__(self):
                super().__init__()
                self.name = "databricks"
                self.version = "1.0.0"
                self.description = "Databricks integration for PyForge CLI"

            def is_available(self) -> bool:
                try:
                    import databricks
                    return True
                except ImportError:
                    return False

            def initialize(self) -> bool:
                # Perform extension initialization
                return self.is_available()
    """

    def __init__(self):
        """Initialize the extension.

        Subclasses should call super().__init__() and set:
        - self.name: Unique extension name
        - self.version: Extension version
        - self.description: Human-readable description
        """
        self.name: str = ""
        self.version: str = "1.0.0"
        self.description: str = ""
        self.enabled: bool = True
        self.initialized: bool = False

    @abstractmethod
    def is_available(self) -> bool:
        """Check if extension dependencies are available.

        This method should check for required dependencies, environment
        conditions, or external services needed by the extension.

        Returns:
            bool: True if extension can be used, False otherwise
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the extension.

        This method is called once when the extension is loaded.
        It should perform any necessary setup, configuration loading,
        or connection establishment.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass

    def cleanup(self) -> None:
        """Clean up extension resources.

        This method is called when the extension is being unloaded
        or when the application is shutting down. Subclasses should
        override to perform cleanup operations.
        """
        self.initialized = False

    def get_commands(self) -> Dict[str, Any]:
        """Get additional CLI commands provided by this extension.

        Returns:
            Dict[str, Any]: Dictionary of command name to command function mappings
        """
        return {}

    def enhance_convert_command(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the convert command with extension-specific options.

        Args:
            options: Current conversion options

        Returns:
            Dict[str, Any]: Enhanced options with extension modifications
        """
        return options

    # Hook methods for extending core functionality
    def hook_pre_conversion(
        self, input_file: Path, output_file: Path, options: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Hook called before conversion starts.

        Args:
            input_file: Path to input file
            output_file: Path to output file
            options: Conversion options

        Returns:
            Optional[Dict[str, Any]]: Modified options or None to proceed unchanged
        """
        return None

    def hook_post_conversion(
        self,
        input_file: Path,
        output_file: Path,
        options: Dict[str, Any],
        success: bool,
    ) -> None:
        """Hook called after conversion completes.

        Args:
            input_file: Path to input file
            output_file: Path to output file
            options: Conversion options that were used
            success: Whether conversion was successful
        """
        pass

    def hook_error_handling(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Hook called when an error occurs during conversion.

        Args:
            error: The exception that occurred
            context: Context information about the error

        Returns:
            bool: True if error was handled, False to continue with default handling
        """
        return False

    def hook_environment_detection(self) -> Dict[str, Any]:
        """Hook for detecting environment-specific information.

        Returns:
            Dict[str, Any]: Environment information discovered by this extension
        """
        return {}

    def hook_performance_optimization(
        self, operation: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Hook for applying performance optimizations.

        Args:
            operation: The operation being performed (e.g., 'convert', 'validate')
            options: Current operation options

        Returns:
            Dict[str, Any]: Optimized options
        """
        return options

    def get_metadata(self) -> Dict[str, Any]:
        """Get extension metadata.

        Returns:
            Dict[str, Any]: Extension metadata including name, version, description, etc.
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled,
            "initialized": self.initialized,
            "available": self.is_available(),
        }

    def __str__(self) -> str:
        """String representation of the extension."""
        return f"{self.name} v{self.version}"

    def __repr__(self) -> str:
        """Developer representation of the extension."""
        return f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}', initialized={self.initialized})>"
