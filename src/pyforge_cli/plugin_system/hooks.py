"""
Extension hooks system for PyForge CLI.

This module provides a comprehensive hooks system that allows extensions
to modify and enhance the conversion process at various points.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
from enum import Enum

from .registry import extension_registry

logger = logging.getLogger(__name__)


class HookType(Enum):
    """Types of hooks available in the conversion process."""
    PRE_CONVERSION = "pre_conversion"
    POST_CONVERSION = "post_conversion"
    PARAMETER_ENHANCEMENT = "parameter_enhancement"
    ERROR_HANDLING = "error_handling"
    CONVERTER_SELECTION = "converter_selection"


class HookResult:
    """Result of a hook execution."""
    
    def __init__(self, success: bool = True, data: Any = None, 
                 message: str = "", stop_processing: bool = False):
        """
        Initialize hook result.
        
        Args:
            success: Whether the hook executed successfully
            data: Modified data or result from the hook
            message: Optional message or error description
            stop_processing: Whether to stop further hook processing
        """
        self.success = success
        self.data = data
        self.message = message
        self.stop_processing = stop_processing


class ExtensionHooksManager:
    """
    Manages extension hooks throughout the conversion process.
    
    This class provides a centralized way to execute hooks at various
    points in the conversion pipeline, allowing extensions to modify
    parameters, handle errors, and enhance functionality.
    """
    
    def __init__(self):
        """Initialize the hooks manager."""
        self.logger = logging.getLogger(__name__)
        self._hook_cache: Dict[HookType, List[Callable]] = {}
        self._last_cache_update = 0
    
    def execute_pre_conversion_hooks(self, input_file: Path, output_file: Path, 
                                   options: Dict[str, Any]) -> HookResult:
        """
        Execute pre-conversion hooks.
        
        These hooks are called before any conversion begins and can modify
        conversion parameters or perform pre-processing.
        
        Args:
            input_file: Input file path
            output_file: Output file path
            options: Conversion options dictionary
            
        Returns:
            HookResult with potentially modified options
        """
        self.logger.debug("Executing pre-conversion hooks")
        
        hook_data = {
            'input_file': input_file,
            'output_file': output_file,
            'options': options.copy()
        }
        
        result = self._execute_hooks(HookType.PRE_CONVERSION, hook_data)
        
        if result.success and result.data and 'options' in result.data:
            # Return just the options for backwards compatibility
            result.data = result.data['options']
        
        return result
    
    def execute_post_conversion_hooks(self, input_file: Path, output_file: Path, 
                                    conversion_result: bool, 
                                    metadata: Optional[Dict[str, Any]] = None) -> HookResult:
        """
        Execute post-conversion hooks.
        
        These hooks are called after conversion completes and can perform
        post-processing, cleanup, or additional operations.
        
        Args:
            input_file: Input file path
            output_file: Output file path
            conversion_result: Whether conversion was successful
            metadata: Optional metadata from the conversion
            
        Returns:
            HookResult with any additional processing results
        """
        self.logger.debug("Executing post-conversion hooks")
        
        hook_data = {
            'input_file': input_file,
            'output_file': output_file,
            'conversion_result': conversion_result,
            'metadata': metadata or {}
        }
        
        return self._execute_hooks(HookType.POST_CONVERSION, hook_data)
    
    def execute_parameter_enhancement_hooks(self, input_file: Path, 
                                          options: Dict[str, Any]) -> HookResult:
        """
        Execute parameter enhancement hooks.
        
        These hooks can modify or add to the conversion options based on
        the input file type, content, or extension-specific logic.
        
        Args:
            input_file: Input file path
            options: Current conversion options
            
        Returns:
            HookResult with potentially enhanced options
        """
        self.logger.debug("Executing parameter enhancement hooks")
        
        hook_data = {
            'input_file': input_file,
            'options': options.copy()
        }
        
        result = self._execute_hooks(HookType.PARAMETER_ENHANCEMENT, hook_data)
        
        if result.success and result.data and 'options' in result.data:
            result.data = result.data['options']
        
        return result
    
    def execute_error_handling_hooks(self, input_file: Path, output_file: Path, 
                                   error: Exception, 
                                   context: Dict[str, Any]) -> HookResult:
        """
        Execute error handling hooks.
        
        These hooks are called when an error occurs during conversion
        and can provide recovery mechanisms or enhanced error reporting.
        
        Args:
            input_file: Input file path
            output_file: Output file path
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            HookResult indicating if error was handled
        """
        self.logger.debug("Executing error handling hooks")
        
        hook_data = {
            'input_file': input_file,
            'output_file': output_file,
            'error': error,
            'context': context
        }
        
        return self._execute_hooks(HookType.ERROR_HANDLING, hook_data)
    
    def execute_converter_selection_hooks(self, input_file: Path, 
                                        available_converters: List[str]) -> HookResult:
        """
        Execute converter selection hooks.
        
        These hooks can influence which converter is selected for a file
        based on extension-specific logic or enhanced file detection.
        
        Args:
            input_file: Input file path
            available_converters: List of available converter names
            
        Returns:
            HookResult with potentially modified converter selection
        """
        self.logger.debug("Executing converter selection hooks")
        
        hook_data = {
            'input_file': input_file,
            'available_converters': available_converters.copy()
        }
        
        result = self._execute_hooks(HookType.CONVERTER_SELECTION, hook_data)
        
        if result.success and result.data and 'selected_converter' in result.data:
            result.data = result.data['selected_converter']
        
        return result
    
    def _execute_hooks(self, hook_type: HookType, data: Dict[str, Any]) -> HookResult:
        """
        Execute all hooks of a specific type.
        
        Args:
            hook_type: Type of hook to execute
            data: Data to pass to hooks
            
        Returns:
            Combined result from all hooks
        """
        hooks = self._get_hooks_for_type(hook_type)
        
        if not hooks:
            self.logger.debug(f"No hooks registered for {hook_type.value}")
            return HookResult(success=True, data=data)
        
        current_data = data.copy()
        messages = []
        
        for hook_func in hooks:
            try:
                self.logger.debug(f"Executing {hook_type.value} hook: {hook_func.__name__}")
                
                # Execute the hook
                hook_result = hook_func(current_data)
                
                # Handle different return types
                if isinstance(hook_result, HookResult):
                    result = hook_result
                elif isinstance(hook_result, dict):
                    result = HookResult(success=True, data=hook_result)
                elif isinstance(hook_result, bool):
                    result = HookResult(success=hook_result, data=current_data)
                else:
                    result = HookResult(success=True, data=hook_result)
                
                if not result.success:
                    self.logger.warning(f"Hook {hook_func.__name__} failed: {result.message}")
                    messages.append(f"{hook_func.__name__}: {result.message}")
                    
                    if result.stop_processing:
                        return HookResult(
                            success=False, 
                            data=current_data,
                            message="; ".join(messages)
                        )
                    continue
                
                # Update current data with hook result
                if result.data is not None:
                    if isinstance(result.data, dict):
                        current_data.update(result.data)
                    else:
                        current_data = result.data
                
                if result.message:
                    messages.append(f"{hook_func.__name__}: {result.message}")
                
                if result.stop_processing:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error executing {hook_type.value} hook {hook_func.__name__}: {e}")
                messages.append(f"{hook_func.__name__}: Error - {str(e)}")
                continue
        
        return HookResult(
            success=True,
            data=current_data,
            message="; ".join(messages) if messages else ""
        )
    
    def _get_hooks_for_type(self, hook_type: HookType) -> List[Callable]:
        """
        Get all registered hooks for a specific type.
        
        Args:
            hook_type: Type of hook to retrieve
            
        Returns:
            List of callable hook functions
        """
        # Check if we need to refresh the cache
        current_plugins = extension_registry.get_all_plugins()
        
        if not current_plugins or len(current_plugins) != self._last_cache_update:
            self._refresh_hook_cache()
            self._last_cache_update = len(current_plugins)
        
        return self._hook_cache.get(hook_type, [])
    
    def _refresh_hook_cache(self) -> None:
        """Refresh the cache of available hooks from all extensions."""
        self.logger.debug("Refreshing hook cache")
        
        self._hook_cache.clear()
        
        # Get all enabled extensions
        enabled_extensions = extension_registry.get_enabled_extensions()
        
        for name, extension in enabled_extensions.items():
            try:
                # Check for each hook type
                for hook_type in HookType:
                    method_name = f"hook_{hook_type.value}"
                    
                    if hasattr(extension, method_name):
                        hook_method = getattr(extension, method_name)
                        if callable(hook_method):
                            if hook_type not in self._hook_cache:
                                self._hook_cache[hook_type] = []
                            
                            self._hook_cache[hook_type].append(hook_method)
                            self.logger.debug(f"Registered {hook_type.value} hook from {name}")
                
            except Exception as e:
                self.logger.error(f"Error registering hooks from extension {name}: {e}")
    
    def get_hook_statistics(self) -> Dict[str, int]:
        """
        Get statistics about registered hooks.
        
        Returns:
            Dictionary with hook counts by type
        """
        stats = {}
        
        for hook_type in HookType:
            hooks = self._get_hooks_for_type(hook_type)
            stats[hook_type.value] = len(hooks)
        
        stats['total'] = sum(stats.values())
        return stats
    
    def clear_cache(self) -> None:
        """Clear the hook cache to force refresh."""
        self._hook_cache.clear()
        self._last_cache_update = 0


# Global hooks manager instance
hooks_manager = ExtensionHooksManager()