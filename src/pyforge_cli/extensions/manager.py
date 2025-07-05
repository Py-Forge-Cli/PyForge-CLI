"""Extension lifecycle manager for PyForge CLI.

This module manages the complete lifecycle of extensions including discovery,
loading, initialization, and shutdown.
"""

import atexit
import logging
from typing import Dict, List, Optional

from pyforge_cli.extensions.base import BaseExtension
from pyforge_cli.extensions.discovery import ExtensionDiscovery
from pyforge_cli.extensions.loader import ExtensionLoader
from pyforge_cli.extensions.registry import ExtensionRegistry

logger = logging.getLogger(__name__)


class ExtensionManager:
    """Manages the lifecycle of PyForge CLI extensions."""

    def __init__(self):
        """Initialize the extension manager."""
        self.discovery = ExtensionDiscovery()
        self.loader = ExtensionLoader(self.discovery)
        self.registry = ExtensionRegistry()
        self._initialized = False
        self._shutting_down = False

        # Register cleanup on exit
        atexit.register(self.shutdown)

    def initialize(self, timeout: float = 30.0) -> None:
        """Initialize all extensions.

        Args:
            timeout: Maximum time to wait for each extension initialization
        """
        if self._initialized:
            logger.debug("Extension manager already initialized")
            return

        logger.info("Initializing extension manager...")

        try:
            # Discover extensions
            discovered = self.discovery.discover_extensions()

            # Register discovered extensions
            for name, entry_point in discovered.items():
                self.registry.register_discovered(name, entry_point)

            # Load extensions
            loaded_extensions = self.loader.load_all_extensions(timeout)

            # Register loaded extensions
            for name, extension in loaded_extensions.items():
                load_time = self.loader.get_loading_stats().get(name, 0.0)
                self.registry.register_loaded(
                    name=name, instance=extension, load_time=load_time
                )

            # Register failed extensions
            for name, error in self.loader.get_failed_extensions().items():
                self.registry.register_failed(name, error)

            self._initialized = True
            logger.info(
                f"Extension manager initialized with {len(loaded_extensions)} extension(s)"
            )

        except Exception as e:
            logger.error(f"Failed to initialize extension manager: {e}")
            raise

    def get_extension(self, name: str) -> Optional[BaseExtension]:
        """Get a specific extension by name.

        Args:
            name: Extension name

        Returns:
            Optional[BaseExtension]: The extension if loaded and enabled
        """
        return self.registry.get_extension(name)

    def get_all_extensions(self) -> List[BaseExtension]:
        """Get all enabled extensions.

        Returns:
            List[BaseExtension]: All enabled extension instances
        """
        return self.registry.get_enabled_extensions()

    def get_extensions_for_command(self, command: str) -> List[BaseExtension]:
        """Get extensions that provide additional commands.

        Args:
            command: The command name to filter by

        Returns:
            List[BaseExtension]: Extensions that provide the specified command
        """
        extensions = []
        for extension in self.get_all_extensions():
            commands = extension.get_commands()
            if commands and command in [cmd.name for cmd in commands]:
                extensions.append(extension)
        return extensions

    def execute_hook(self, hook_name: str, *args, **kwargs) -> Dict[str, any]:
        """Execute a hook on all enabled extensions.

        Args:
            hook_name: Name of the hook method to execute
            *args: Positional arguments for the hook
            **kwargs: Keyword arguments for the hook

        Returns:
            Dict[str, any]: Results from each extension that implements the hook
        """
        results = {}

        for extension in self.get_all_extensions():
            if hasattr(extension, hook_name):
                try:
                    logger.debug(
                        f"Executing hook {hook_name} on {extension.__class__.__name__}"
                    )
                    hook_method = getattr(extension, hook_name)
                    result = hook_method(*args, **kwargs)
                    results[extension.__class__.__name__] = result
                except Exception as e:
                    logger.error(
                        f"Error executing hook {hook_name} on {extension.__class__.__name__}: {e}"
                    )
                    results[extension.__class__.__name__] = {"error": str(e)}

        return results

    def enable_extension(self, name: str) -> bool:
        """Enable a specific extension.

        Args:
            name: Extension name

        Returns:
            bool: True if successfully enabled
        """
        return self.registry.enable_extension(name)

    def disable_extension(self, name: str) -> bool:
        """Disable a specific extension.

        Args:
            name: Extension name

        Returns:
            bool: True if successfully disabled
        """
        return self.registry.disable_extension(name)

    def reload_extension(self, name: str, timeout: float = 30.0) -> bool:
        """Reload a specific extension.

        Args:
            name: Extension name
            timeout: Maximum time for reloading

        Returns:
            bool: True if successfully reloaded
        """
        # First unregister the old instance
        self.registry.unregister(name)

        # Try to reload
        if self.loader.reload_extension(name, timeout):
            # Re-register if successful
            extension = self.loader.get_extension(name)
            if extension:
                load_time = self.loader.get_loading_stats().get(name, 0.0)
                self.registry.register_loaded(
                    name=name, instance=extension, load_time=load_time
                )
                return True

        return False

    def get_extension_info(self) -> Dict[str, Dict]:
        """Get information about all extensions.

        Returns:
            Dict with extension information including state, version, etc.
        """
        info = {}

        for name, metadata in self.registry.get_all_metadata().items():
            info[name] = {
                "state": metadata.state.value,
                "version": metadata.version,
                "description": metadata.description,
                "entry_point": metadata.entry_point,
                "load_time": metadata.load_time,
                "error": str(metadata.error) if metadata.error else None,
                "enabled": self.registry.is_enabled(name),
                "dependencies": metadata.dependencies,
            }

        return info

    def shutdown(self) -> None:
        """Shutdown all extensions and clean up resources."""
        if self._shutting_down:
            return

        self._shutting_down = True
        logger.info("Shutting down extension manager...")

        try:
            # Execute cleanup hooks
            self.execute_hook("hook_shutdown")

            # Clear the registry (which also calls cleanup on extensions)
            self.registry.clear()

            logger.info("Extension manager shutdown complete")
        except Exception as e:
            logger.error(f"Error during extension manager shutdown: {e}")
        finally:
            self._initialized = False
            self._shutting_down = False


# Global extension manager instance
_manager_instance: Optional[ExtensionManager] = None


def get_extension_manager() -> ExtensionManager:
    """Get the global extension manager instance.

    Returns:
        ExtensionManager: The global extension manager
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ExtensionManager()
    return _manager_instance
