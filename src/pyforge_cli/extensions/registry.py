"""Extension registry for PyForge CLI.

This module provides a thread-safe registry to track and manage loaded extensions,
their states, and metadata.
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set

from pyforge_cli.extensions.base import BaseExtension

logger = logging.getLogger(__name__)


class ExtensionState(Enum):
    """States an extension can be in."""
    DISCOVERED = "discovered"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"
    DISABLED = "disabled"
    UNLOADED = "unloaded"


@dataclass
class ExtensionMetadata:
    """Metadata about an extension."""
    name: str
    entry_point: str
    state: ExtensionState
    version: Optional[str] = None
    description: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    load_time: Optional[float] = None
    error: Optional[Exception] = None
    loaded_at: Optional[datetime] = None
    instance: Optional[BaseExtension] = None


class ExtensionRegistry:
    """Thread-safe registry for PyForge CLI extensions."""
    
    def __init__(self):
        """Initialize the extension registry."""
        self._extensions: Dict[str, ExtensionMetadata] = {}
        self._lock = threading.RLock()
        self._enabled_extensions: Set[str] = set()
        self._disabled_extensions: Set[str] = set()
    
    def register_discovered(self, name: str, entry_point: str) -> None:
        """Register a discovered extension.
        
        Args:
            name: Extension name
            entry_point: Entry point specification
        """
        with self._lock:
            if name not in self._extensions:
                self._extensions[name] = ExtensionMetadata(
                    name=name,
                    entry_point=entry_point,
                    state=ExtensionState.DISCOVERED
                )
                logger.debug(f"Registered discovered extension: {name}")
    
    def update_state(self, name: str, state: ExtensionState, error: Optional[Exception] = None) -> None:
        """Update the state of an extension.
        
        Args:
            name: Extension name
            state: New state
            error: Optional error if state is FAILED
        """
        with self._lock:
            if name in self._extensions:
                self._extensions[name].state = state
                if error:
                    self._extensions[name].error = error
                logger.debug(f"Updated extension {name} state to {state.value}")
            else:
                logger.warning(f"Attempted to update state for unknown extension: {name}")
    
    def register_loaded(
        self, 
        name: str, 
        instance: BaseExtension,
        load_time: float,
        version: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """Register a successfully loaded extension.
        
        Args:
            name: Extension name
            instance: The loaded extension instance
            load_time: Time taken to load in seconds
            version: Optional version string
            description: Optional description
        """
        with self._lock:
            if name in self._extensions:
                metadata = self._extensions[name]
                metadata.state = ExtensionState.LOADED
                metadata.instance = instance
                metadata.load_time = load_time
                metadata.loaded_at = datetime.now()
                metadata.version = version or getattr(instance, '__version__', None)
                metadata.description = description or getattr(instance, '__doc__', '').strip()
                
                # Automatically enable loaded extensions
                self._enabled_extensions.add(name)
                logger.info(f"Registered loaded extension: {name} (v{metadata.version})")
            else:
                # Create new entry if not discovered first
                self._extensions[name] = ExtensionMetadata(
                    name=name,
                    entry_point="unknown",
                    state=ExtensionState.LOADED,
                    instance=instance,
                    load_time=load_time,
                    loaded_at=datetime.now(),
                    version=version,
                    description=description
                )
                self._enabled_extensions.add(name)
    
    def register_failed(self, name: str, error: Exception) -> None:
        """Register a failed extension.
        
        Args:
            name: Extension name
            error: The error that occurred
        """
        with self._lock:
            if name in self._extensions:
                self._extensions[name].state = ExtensionState.FAILED
                self._extensions[name].error = error
            else:
                self._extensions[name] = ExtensionMetadata(
                    name=name,
                    entry_point="unknown",
                    state=ExtensionState.FAILED,
                    error=error
                )
            logger.warning(f"Registered failed extension: {name} - {error}")
    
    def get_extension(self, name: str) -> Optional[BaseExtension]:
        """Get a loaded extension instance.
        
        Args:
            name: Extension name
            
        Returns:
            Optional[BaseExtension]: The extension instance if loaded and enabled
        """
        with self._lock:
            if name in self._extensions and name in self._enabled_extensions:
                metadata = self._extensions[name]
                if metadata.state == ExtensionState.LOADED:
                    return metadata.instance
            return None
    
    def get_metadata(self, name: str) -> Optional[ExtensionMetadata]:
        """Get metadata for an extension.
        
        Args:
            name: Extension name
            
        Returns:
            Optional[ExtensionMetadata]: Extension metadata if registered
        """
        with self._lock:
            return self._extensions.get(name)
    
    def get_all_metadata(self) -> Dict[str, ExtensionMetadata]:
        """Get metadata for all registered extensions.
        
        Returns:
            Dict[str, ExtensionMetadata]: All extension metadata
        """
        with self._lock:
            return self._extensions.copy()
    
    def get_extensions_by_state(self, state: ExtensionState) -> List[str]:
        """Get extensions in a specific state.
        
        Args:
            state: The state to filter by
            
        Returns:
            List[str]: Extension names in the specified state
        """
        with self._lock:
            return [
                name for name, metadata in self._extensions.items()
                if metadata.state == state
            ]
    
    def enable_extension(self, name: str) -> bool:
        """Enable an extension.
        
        Args:
            name: Extension name
            
        Returns:
            bool: True if the extension was enabled
        """
        with self._lock:
            if name in self._extensions:
                metadata = self._extensions[name]
                if metadata.state in (ExtensionState.LOADED, ExtensionState.DISABLED):
                    self._enabled_extensions.add(name)
                    self._disabled_extensions.discard(name)
                    if metadata.state == ExtensionState.DISABLED:
                        metadata.state = ExtensionState.LOADED
                    logger.info(f"Enabled extension: {name}")
                    return True
            return False
    
    def disable_extension(self, name: str) -> bool:
        """Disable an extension.
        
        Args:
            name: Extension name
            
        Returns:
            bool: True if the extension was disabled
        """
        with self._lock:
            if name in self._extensions:
                self._enabled_extensions.discard(name)
                self._disabled_extensions.add(name)
                if self._extensions[name].state == ExtensionState.LOADED:
                    self._extensions[name].state = ExtensionState.DISABLED
                logger.info(f"Disabled extension: {name}")
                return True
            return False
    
    def is_enabled(self, name: str) -> bool:
        """Check if an extension is enabled.
        
        Args:
            name: Extension name
            
        Returns:
            bool: True if the extension is enabled
        """
        with self._lock:
            return name in self._enabled_extensions
    
    def get_enabled_extensions(self) -> List[BaseExtension]:
        """Get all enabled extension instances.
        
        Returns:
            List[BaseExtension]: Enabled extension instances
        """
        with self._lock:
            extensions = []
            for name in self._enabled_extensions:
                if name in self._extensions:
                    metadata = self._extensions[name]
                    if metadata.state == ExtensionState.LOADED and metadata.instance:
                        extensions.append(metadata.instance)
            return extensions
    
    def unregister(self, name: str) -> bool:
        """Unregister an extension completely.
        
        Args:
            name: Extension name
            
        Returns:
            bool: True if the extension was unregistered
        """
        with self._lock:
            if name in self._extensions:
                # Clean up the instance if it exists
                metadata = self._extensions[name]
                if metadata.instance:
                    try:
                        metadata.instance.cleanup()
                    except Exception as e:
                        logger.warning(f"Error during cleanup of {name}: {e}")
                
                # Remove from all tracking
                del self._extensions[name]
                self._enabled_extensions.discard(name)
                self._disabled_extensions.discard(name)
                logger.info(f"Unregistered extension: {name}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all registered extensions."""
        with self._lock:
            # Clean up all instances
            for metadata in self._extensions.values():
                if metadata.instance:
                    try:
                        metadata.instance.cleanup()
                    except Exception as e:
                        logger.warning(f"Error during cleanup of {metadata.name}: {e}")
            
            self._extensions.clear()
            self._enabled_extensions.clear()
            self._disabled_extensions.clear()
            logger.info("Cleared extension registry")