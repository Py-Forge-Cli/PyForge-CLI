"""Extension discovery mechanism for PyForge CLI.

This module handles the discovery of PyForge extensions using Python entry points.
Extensions are discovered dynamically at runtime, allowing for a pluggable architecture.
"""

import logging
from typing import Dict, List, Optional, Tuple, Type
from importlib.metadata import entry_points
import importlib
import sys

from pyforge_cli.extensions.base import BaseExtension

logger = logging.getLogger(__name__)


class ExtensionDiscovery:
    """Discovers and manages PyForge CLI extensions."""
    
    ENTRY_POINT_GROUP = "pyforge_cli.extensions"
    
    def __init__(self):
        """Initialize the extension discovery mechanism."""
        self._discovered_extensions: Dict[str, Tuple[str, Optional[Exception]]] = {}
        self._entry_points_cache = None
    
    def discover_extensions(self) -> Dict[str, str]:
        """Discover all available extensions via entry points.
        
        Returns:
            Dict[str, str]: Mapping of extension names to their entry point values.
                           The value is in the format 'module:class'.
        """
        logger.info("Discovering PyForge CLI extensions...")
        
        try:
            # Get entry points for our group
            if sys.version_info >= (3, 10):
                # Python 3.10+ API
                eps = entry_points(group=self.ENTRY_POINT_GROUP)
                discovered = {ep.name: ep.value for ep in eps}
            else:
                # Python 3.8-3.9 API
                eps = entry_points()
                if self.ENTRY_POINT_GROUP in eps:
                    discovered = {
                        ep.name: ep.value 
                        for ep in eps[self.ENTRY_POINT_GROUP]
                    }
                else:
                    discovered = {}
            
            # Cache the discovered extensions
            for name, entry_point in discovered.items():
                self._discovered_extensions[name] = (entry_point, None)
                logger.debug(f"Discovered extension: {name} -> {entry_point}")
            
            logger.info(f"Found {len(discovered)} extension(s)")
            return discovered
            
        except Exception as e:
            logger.error(f"Error discovering extensions: {e}")
            return {}
    
    def load_extension_class(self, name: str, entry_point: str) -> Optional[Type[BaseExtension]]:
        """Load an extension class from its entry point.
        
        Args:
            name: The extension name
            entry_point: The entry point value (e.g., 'module.path:ClassName')
        
        Returns:
            Optional[Type[BaseExtension]]: The extension class if loaded successfully
        """
        try:
            # Parse the entry point
            if ':' not in entry_point:
                raise ValueError(f"Invalid entry point format: {entry_point}")
            
            module_path, class_name = entry_point.split(':', 1)
            
            # Import the module
            logger.debug(f"Loading extension {name} from {module_path}:{class_name}")
            module = importlib.import_module(module_path)
            
            # Get the class
            extension_class = getattr(module, class_name)
            
            # Validate it's a BaseExtension subclass
            if not issubclass(extension_class, BaseExtension):
                raise TypeError(
                    f"Extension {name} class {class_name} must inherit from BaseExtension"
                )
            
            return extension_class
            
        except ImportError as e:
            logger.warning(f"Failed to import extension {name}: {e}")
            self._discovered_extensions[name] = (entry_point, e)
            return None
        except Exception as e:
            logger.error(f"Error loading extension {name}: {e}")
            self._discovered_extensions[name] = (entry_point, e)
            return None
    
    def get_discovered_extensions(self) -> Dict[str, Tuple[str, Optional[Exception]]]:
        """Get all discovered extensions with their load status.
        
        Returns:
            Dict mapping extension names to tuples of (entry_point, error).
            If error is None, the extension was discovered successfully.
        """
        return self._discovered_extensions.copy()
    
    def is_extension_available(self, name: str) -> bool:
        """Check if an extension was discovered successfully.
        
        Args:
            name: The extension name
            
        Returns:
            bool: True if the extension was discovered without errors
        """
        if name not in self._discovered_extensions:
            return False
        
        _, error = self._discovered_extensions[name]
        return error is None