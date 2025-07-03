"""
Base extension interface for PyForge CLI.

All PyForge extensions must inherit from this base class and implement
the required abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import click


class BaseExtension(ABC):
    """
    Base class for PyForge extensions.
    
    Extensions provide additional functionality to PyForge CLI through
    a well-defined interface. They can add new commands, enhance existing
    commands, and provide new converters.
    """
    
    def __init__(self):
        """Initialize the extension with default metadata."""
        self.name = self.__class__.__name__.lower().replace('extension', '')
        self.version = "1.0.0"
        self.description = self.__doc__ or "PyForge extension"
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if extension dependencies are available and can be used.
        
        This method should check for required dependencies, environment
        variables, or system conditions needed for the extension to work.
        
        Returns:
            bool: True if the extension can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the extension.
        
        This method is called once when the extension is loaded.
        It should perform any necessary setup, such as configuring
        libraries or establishing connections.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    def get_commands(self) -> List[click.Command]:
        """
        Return additional CLI commands provided by this extension.
        
        Extensions can add new commands to the PyForge CLI by returning
        a list of Click command objects.
        
        Returns:
            List[click.Command]: List of additional CLI commands
        """
        return []
    
    def get_converters(self) -> Dict[str, Any]:
        """
        Return additional converters provided by this extension.
        
        Extensions can register new file format converters by returning
        a dictionary mapping format names to converter classes.
        
        Returns:
            Dict[str, Any]: Dictionary of format name to converter class
        """
        return {}
    
    def enhance_convert_command(self, ctx: click.Context, **kwargs) -> Dict[str, Any]:
        """
        Enhance the convert command with extension-specific options.
        
        This hook is called before the convert command executes, allowing
        extensions to modify parameters or add functionality.
        
        Args:
            ctx: Click context object
            **kwargs: Current command parameters
            
        Returns:
            Dict[str, Any]: Modified parameters
        """
        return kwargs
    
    def post_conversion_hook(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook called after conversion completion.
        
        Extensions can use this to perform post-processing, logging,
        or cleanup after a conversion completes.
        
        Args:
            result: Conversion result dictionary
            
        Returns:
            Dict[str, Any]: Modified result dictionary
        """
        return result
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this extension.
        
        Returns:
            Dict[str, Any]: Extension metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "available": self.is_available()
        }
    
    # Hook methods for the new hooks system
    def hook_pre_conversion(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Pre-conversion hook.
        
        Called before conversion begins. Can modify conversion parameters
        or perform pre-processing operations.
        
        Args:
            data: Dictionary containing input_file, output_file, and options
            
        Returns:
            Optional[Dict[str, Any]]: Modified data or None to leave unchanged
        """
        return None
    
    def hook_post_conversion(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Post-conversion hook.
        
        Called after conversion completes. Can perform post-processing,
        cleanup, or additional operations.
        
        Args:
            data: Dictionary containing input_file, output_file, conversion_result, and metadata
            
        Returns:
            Optional[Dict[str, Any]]: Additional data or None
        """
        return None
    
    def hook_parameter_enhancement(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parameter enhancement hook.
        
        Called to enhance or modify conversion parameters based on
        extension-specific logic.
        
        Args:
            data: Dictionary containing input_file and options
            
        Returns:
            Optional[Dict[str, Any]]: Modified data with enhanced options or None
        """
        return None
    
    def hook_error_handling(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Error handling hook.
        
        Called when an error occurs during conversion. Can provide
        recovery mechanisms or enhanced error reporting.
        
        Args:
            data: Dictionary containing input_file, output_file, error, and context
            
        Returns:
            Optional[Dict[str, Any]]: Recovery data or None
        """
        return None
    
    def hook_converter_selection(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Converter selection hook.
        
        Called to influence which converter is selected for a file.
        Can provide enhanced file detection or format-specific logic.
        
        Args:
            data: Dictionary containing input_file and available_converters
            
        Returns:
            Optional[Dict[str, Any]]: Data with selected_converter or None
        """
        return None
    
    def shutdown(self) -> None:
        """
        Shutdown hook called during cleanup.
        
        Extensions can override this to perform cleanup operations
        when the application is shutting down.
        """
        pass