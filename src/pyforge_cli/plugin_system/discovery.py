"""
Plugin discovery and loading system for PyForge CLI.

This module implements the core plugin discovery mechanism using Python's entry points.
It supports Python 3.8-3.12 with appropriate compatibility handling.
"""

import sys
import time
import logging
from typing import Dict, List, Optional, Any, Type
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Handle different Python versions for importlib.metadata
if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    try:
        import importlib_metadata as metadata
    except ImportError:
        # For Python 3.8 and 3.9, importlib.metadata is available
        from importlib import metadata

from .exceptions import PluginLoadError, PluginInitializationError

logger = logging.getLogger(__name__)


class PluginDiscovery:
    """
    Discovers and loads PyForge extensions using entry points.
    
    This class handles the discovery, loading, and initialization of plugins
    with proper error handling and timeout protection.
    """
    
    # Entry point group names
    EXTENSIONS_GROUP = "pyforge.extensions"
    CONVERTERS_GROUP = "pyforge.converters"
    
    # Initialization timeout in seconds
    INIT_TIMEOUT = 5.0
    
    def __init__(self):
        """Initialize the plugin discovery system."""
        self.logger = logging.getLogger(__name__)
        self._extensions: Dict[str, Any] = {}
        self._converters: Dict[str, Type] = {}
        self._failed_plugins: Dict[str, str] = {}
        
    def discover_extensions(self) -> Dict[str, Any]:
        """
        Discover all available PyForge extensions.
        
        Returns:
            Dict mapping extension names to loaded extension instances
        """
        if self._extensions:
            return self._extensions
            
        self.logger.info("Discovering PyForge extensions...")
        start_time = time.time()
        
        try:
            # Get entry points for extensions
            entry_points = self._get_entry_points(self.EXTENSIONS_GROUP)
            
            for entry_point in entry_points:
                try:
                    # Load the extension class
                    extension_class = self._load_entry_point(entry_point)
                    
                    # Instantiate the extension
                    extension = extension_class()
                    
                    self._extensions[entry_point.name] = extension
                    self.logger.info(f"Loaded extension: {entry_point.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to load extension {entry_point.name}: {str(e)}"
                    self.logger.warning(error_msg)
                    self._failed_plugins[entry_point.name] = error_msg
                    
        except Exception as e:
            self.logger.error(f"Error discovering extensions: {e}")
            
        discovery_time = time.time() - start_time
        self.logger.info(f"Extension discovery completed in {discovery_time:.3f}s")
        self.logger.info(f"Loaded {len(self._extensions)} extensions, {len(self._failed_plugins)} failed")
        
        return self._extensions
    
    def discover_converters(self) -> Dict[str, Type]:
        """
        Discover all available converters including extension converters.
        
        Returns:
            Dict mapping converter names to converter classes
        """
        if self._converters:
            return self._converters
            
        self.logger.debug("Discovering PyForge converters...")
        
        try:
            # Get entry points for converters
            entry_points = self._get_entry_points(self.CONVERTERS_GROUP)
            
            for entry_point in entry_points:
                try:
                    # Load the converter class
                    converter_class = self._load_entry_point(entry_point)
                    
                    self._converters[entry_point.name] = converter_class
                    self.logger.debug(f"Registered converter: {entry_point.name}")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load converter {entry_point.name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error discovering converters: {e}")
            
        return self._converters
    
    def initialize_extensions(self) -> Dict[str, bool]:
        """
        Initialize all discovered extensions with timeout protection.
        
        Returns:
            Dict mapping extension names to initialization success status
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            for name, extension in self._extensions.items():
                try:
                    # Check if extension is available
                    if not extension.is_available():
                        self.logger.info(f"Extension {name} is not available in this environment")
                        results[name] = False
                        continue
                    
                    # Initialize with timeout
                    future = executor.submit(extension.initialize)
                    try:
                        success = future.result(timeout=self.INIT_TIMEOUT)
                        results[name] = success
                        if success:
                            self.logger.info(f"Extension {name} initialized successfully")
                        else:
                            self.logger.warning(f"Extension {name} initialization returned False")
                    except TimeoutError:
                        self.logger.error(f"Extension {name} initialization timed out after {self.INIT_TIMEOUT}s")
                        results[name] = False
                        
                except Exception as e:
                    self.logger.error(f"Error initializing extension {name}: {e}")
                    results[name] = False
                    
        return results
    
    def get_failed_plugins(self) -> Dict[str, str]:
        """Get information about plugins that failed to load."""
        return self._failed_plugins.copy()
    
    def _get_entry_points(self, group: str) -> List:
        """
        Get entry points for a specific group, handling Python version differences.
        
        Args:
            group: Entry point group name
            
        Returns:
            List of entry points
        """
        try:
            if sys.version_info >= (3, 10):
                # Python 3.10+ API
                return list(metadata.entry_points(group=group))
            else:
                # Python 3.8-3.9 API
                eps = metadata.entry_points()
                if hasattr(eps, 'select'):
                    # importlib_metadata 3.6+
                    return list(eps.select(group=group))
                else:
                    # Older importlib_metadata
                    return eps.get(group, [])
        except Exception as e:
            self.logger.error(f"Error getting entry points for group {group}: {e}")
            return []
    
    def _load_entry_point(self, entry_point) -> Any:
        """
        Load an entry point with proper error handling.
        
        Args:
            entry_point: Entry point to load
            
        Returns:
            Loaded object (class or function)
            
        Raises:
            PluginLoadError: If loading fails
        """
        try:
            return entry_point.load()
        except ImportError as e:
            raise PluginLoadError(f"Import error for {entry_point.name}: {e}")
        except Exception as e:
            raise PluginLoadError(f"Failed to load {entry_point.name}: {e}")


# Global plugin discovery instance
plugin_discovery = PluginDiscovery()