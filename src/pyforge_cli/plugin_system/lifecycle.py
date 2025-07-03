"""
Extension lifecycle management for PyForge CLI.

This module provides comprehensive lifecycle management for extensions including
initialization order, dependency resolution, and cleanup procedures.
"""

import atexit
import logging
import time
from typing import Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from .registry import extension_registry, PluginState
from .exceptions import PluginInitializationError

logger = logging.getLogger(__name__)


class ExtensionLifecycleManager:
    """
    Manages the complete lifecycle of PyForge extensions.
    
    This class handles initialization ordering, dependency resolution,
    failure recovery, and cleanup procedures for all loaded extensions.
    """
    
    def __init__(self):
        """Initialize the lifecycle manager."""
        self.logger = logging.getLogger(__name__)
        self._initialization_order: List[str] = []
        self._cleanup_registered = False
        self._shutdown_in_progress = False
        
    def initialize_extensions(self, extensions: Dict[str, any], 
                            timeout: float = 30.0) -> Dict[str, bool]:
        """
        Initialize all discovered extensions with proper lifecycle management.
        
        Args:
            extensions: Dictionary of extension name to extension instance
            timeout: Maximum time to wait for all initializations
            
        Returns:
            Dictionary mapping extension names to initialization success status
        """
        if not extensions:
            self.logger.info("No extensions to initialize")
            return {}
        
        self.logger.info(f"Starting initialization of {len(extensions)} extensions")
        start_time = time.time()
        
        # Register cleanup handler if not already done
        if not self._cleanup_registered:
            atexit.register(self._cleanup_extensions)
            self._cleanup_registered = True
        
        # Initialize extensions with dependency ordering
        results = self._initialize_with_ordering(extensions, timeout)
        
        # Log initialization summary
        total_time = time.time() - start_time
        successful = sum(1 for success in results.values() if success)
        failed = len(results) - successful
        
        self.logger.info(
            f"Extension initialization completed in {total_time:.3f}s: "
            f"{successful} successful, {failed} failed"
        )
        
        return results
    
    def _initialize_with_ordering(self, extensions: Dict[str, any], 
                                timeout: float) -> Dict[str, bool]:
        """
        Initialize extensions with proper dependency ordering.
        
        Args:
            extensions: Dictionary of extension name to extension instance
            timeout: Timeout for initialization
            
        Returns:
            Dictionary of initialization results
        """
        results = {}
        remaining_extensions = extensions.copy()
        
        # Phase 1: Initialize extensions with no dependencies
        phase = 1
        while remaining_extensions and phase <= 3:  # Max 3 phases to prevent infinite loops
            self.logger.debug(f"Initialization phase {phase}")
            phase_results = self._initialize_phase(remaining_extensions, timeout / 3)
            
            # Update results and remove successful initializations
            results.update(phase_results)
            for name, success in phase_results.items():
                if success:
                    self._initialization_order.append(name)
                    remaining_extensions.pop(name, None)
            
            # If no progress was made, mark remaining as failed
            if not phase_results or not any(phase_results.values()):
                for name in remaining_extensions:
                    self.logger.error(f"Extension {name} failed to initialize after {phase} phases")
                    results[name] = False
                    extension_registry.update_state(
                        name, PluginState.FAILED, 
                        f"Failed to initialize after {phase} dependency resolution phases"
                    )
                break
            
            phase += 1
        
        return results
    
    def _initialize_phase(self, extensions: Dict[str, any], 
                         timeout: float) -> Dict[str, bool]:
        """
        Initialize a phase of extensions in parallel.
        
        Args:
            extensions: Extensions to initialize in this phase
            timeout: Per-extension timeout
            
        Returns:
            Dictionary of initialization results for this phase
        """
        results = {}
        
        # Use ThreadPoolExecutor for parallel initialization
        with ThreadPoolExecutor(max_workers=min(len(extensions), 4)) as executor:
            # Submit initialization tasks
            future_to_name = {
                executor.submit(self._initialize_single_extension, name, ext, timeout): name
                for name, ext in extensions.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_name, timeout=timeout * 2):
                name = future_to_name[future]
                try:
                    success = future.result()
                    results[name] = success
                    if success:
                        self.logger.info(f"Extension {name} initialized successfully")
                    else:
                        self.logger.warning(f"Extension {name} initialization returned False")
                except Exception as e:
                    self.logger.error(f"Extension {name} initialization failed: {e}")
                    results[name] = False
                    extension_registry.update_state(name, PluginState.FAILED, str(e))
        
        return results
    
    def _initialize_single_extension(self, name: str, extension: any, 
                                   timeout: float) -> bool:
        """
        Initialize a single extension with comprehensive error handling.
        
        Args:
            name: Extension name
            extension: Extension instance
            timeout: Initialization timeout
            
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            # Check if extension is available
            if not extension.is_available():
                self.logger.info(f"Extension {name} is not available in this environment")
                extension_registry.update_state(
                    name, PluginState.DISABLED, 
                    "Not available in this environment"
                )
                return False
            
            # Update state to loading
            extension_registry.update_state(name, PluginState.LOADING)
            
            # Initialize with timeout
            start_time = time.time()
            try:
                success = extension.initialize()
                init_time = time.time() - start_time
                
                if success:
                    self.logger.debug(f"Extension {name} initialized in {init_time:.3f}s")
                    extension_registry.update_state(name, PluginState.INITIALIZED)
                    return True
                else:
                    self.logger.warning(f"Extension {name} initialization returned False")
                    extension_registry.update_state(
                        name, PluginState.FAILED, 
                        "Initialization method returned False"
                    )
                    return False
                    
            except Exception as e:
                init_time = time.time() - start_time
                if init_time >= timeout:
                    error_msg = f"Initialization timeout ({timeout:.1f}s)"
                    self.logger.error(f"Extension {name} initialization timed out")
                else:
                    error_msg = f"Initialization error: {str(e)}"
                    self.logger.error(f"Extension {name} initialization failed: {e}")
                
                extension_registry.update_state(name, PluginState.FAILED, error_msg)
                return False
                
        except Exception as e:
            self.logger.error(f"Critical error initializing extension {name}: {e}")
            extension_registry.update_state(name, PluginState.FAILED, f"Critical error: {str(e)}")
            return False
    
    def shutdown_extensions(self) -> None:
        """
        Shutdown all initialized extensions in reverse order.
        
        This ensures proper cleanup and dependency resolution during shutdown.
        """
        if self._shutdown_in_progress:
            return
        
        self._shutdown_in_progress = True
        
        if not self._initialization_order:
            self.logger.debug("No extensions to shutdown")
            return
        
        self.logger.info(f"Shutting down {len(self._initialization_order)} extensions")
        
        # Shutdown in reverse initialization order
        for name in reversed(self._initialization_order):
            try:
                plugin_info = extension_registry.get_plugin_info(name)
                if plugin_info and plugin_info.extension:
                    # Check if extension has a shutdown method
                    if hasattr(plugin_info.extension, 'shutdown'):
                        self.logger.debug(f"Shutting down extension {name}")
                        plugin_info.extension.shutdown()
                    
                    # Update state
                    extension_registry.update_state(name, PluginState.DISABLED)
                    
            except Exception as e:
                self.logger.error(f"Error shutting down extension {name}: {e}")
        
        self.logger.info("Extension shutdown completed")
    
    def _cleanup_extensions(self) -> None:
        """Cleanup handler registered with atexit."""
        if not self._shutdown_in_progress:
            self.logger.debug("Performing cleanup on exit")
            self.shutdown_extensions()
    
    def get_initialization_order(self) -> List[str]:
        """Get the order in which extensions were successfully initialized."""
        return self._initialization_order.copy()
    
    def restart_failed_extensions(self) -> Dict[str, bool]:
        """
        Attempt to restart extensions that failed during initialization.
        
        Returns:
            Dictionary mapping extension names to restart success status
        """
        failed_plugins = extension_registry.get_failed_plugins()
        if not failed_plugins:
            self.logger.info("No failed extensions to restart")
            return {}
        
        self.logger.info(f"Attempting to restart {len(failed_plugins)} failed extensions")
        
        # Get extension instances for failed plugins
        extensions_to_restart = {}
        for name in failed_plugins:
            plugin_info = extension_registry.get_plugin_info(name)
            if plugin_info and plugin_info.extension:
                extensions_to_restart[name] = plugin_info.extension
        
        if not extensions_to_restart:
            self.logger.warning("No extension instances available for restart")
            return {}
        
        # Attempt restart
        return self._initialize_with_ordering(extensions_to_restart, 15.0)


# Global lifecycle manager instance
lifecycle_manager = ExtensionLifecycleManager()