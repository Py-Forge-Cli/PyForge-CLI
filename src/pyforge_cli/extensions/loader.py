"""Extension loader for PyForge CLI.

This module handles the loading and initialization of discovered extensions,
with proper error handling and dependency checking.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, Optional, Type

from pyforge_cli.extensions.base import BaseExtension
from pyforge_cli.extensions.discovery import ExtensionDiscovery

logger = logging.getLogger(__name__)


class ExtensionLoadError(Exception):
    """Raised when an extension fails to load."""

    pass


class ExtensionLoader:
    """Loads and initializes PyForge CLI extensions."""

    DEFAULT_TIMEOUT = 30.0  # 30 seconds timeout for extension initialization

    def __init__(self, discovery: Optional[ExtensionDiscovery] = None):
        """Initialize the extension loader.

        Args:
            discovery: Optional ExtensionDiscovery instance. If not provided,
                      a new instance will be created.
        """
        self.discovery = discovery or ExtensionDiscovery()
        self._loaded_extensions: Dict[str, BaseExtension] = {}
        self._failed_extensions: Dict[str, Exception] = {}
        self._loading_times: Dict[str, float] = {}

    def load_all_extensions(
        self, timeout: float = DEFAULT_TIMEOUT
    ) -> Dict[str, BaseExtension]:
        """Discover and load all available extensions.

        Args:
            timeout: Maximum time in seconds to wait for each extension to initialize

        Returns:
            Dict[str, BaseExtension]: Successfully loaded extensions
        """
        logger.info("Loading PyForge CLI extensions...")
        start_time = time.time()

        # Discover extensions
        discovered = self.discovery.discover_extensions()

        if not discovered:
            logger.info("No extensions found")
            return {}

        # Load each extension
        for name, entry_point in discovered.items():
            try:
                extension = self._load_single_extension(name, entry_point, timeout)
                if extension:
                    self._loaded_extensions[name] = extension
            except Exception as e:
                logger.error(f"Failed to load extension {name}: {e}")
                self._failed_extensions[name] = e

        total_time = time.time() - start_time
        logger.info(
            f"Loaded {len(self._loaded_extensions)} extension(s) in {total_time:.2f}s "
            f"({len(self._failed_extensions)} failed)"
        )

        return self._loaded_extensions.copy()

    def _load_single_extension(
        self, name: str, entry_point: str, timeout: float
    ) -> Optional[BaseExtension]:
        """Load a single extension with timeout protection.

        Args:
            name: Extension name
            entry_point: Entry point specification
            timeout: Maximum initialization time

        Returns:
            Optional[BaseExtension]: The loaded extension instance
        """
        logger.debug(f"Loading extension: {name}")
        start_time = time.time()

        try:
            # Load the extension class
            extension_class = self.discovery.load_extension_class(name, entry_point)
            if not extension_class:
                raise ExtensionLoadError(f"Failed to load extension class for {name}")

            # Check if extension is available (dependencies satisfied)
            if not extension_class.is_available():
                logger.info(f"Extension {name} is not available (missing dependencies)")
                self._failed_extensions[name] = ExtensionLoadError(
                    "Dependencies not satisfied"
                )
                return None

            # Initialize the extension with timeout
            extension = self._initialize_with_timeout(extension_class, name, timeout)

            # Record loading time
            self._loading_times[name] = time.time() - start_time
            logger.info(
                f"Successfully loaded extension: {name} ({self._loading_times[name]:.2f}s)"
            )

            return extension

        except TimeoutError:
            error = ExtensionLoadError(
                f"Extension {name} initialization timed out after {timeout}s"
            )
            self._failed_extensions[name] = error
            logger.error(str(error))
            return None
        except Exception as e:
            self._failed_extensions[name] = e
            logger.error(f"Error loading extension {name}: {e}")
            return None

    def _initialize_with_timeout(
        self, extension_class: Type[BaseExtension], name: str, timeout: float
    ) -> BaseExtension:
        """Initialize an extension with a timeout.

        Args:
            extension_class: The extension class to instantiate
            name: Extension name for logging
            timeout: Maximum time allowed for initialization

        Returns:
            BaseExtension: The initialized extension

        Raises:
            TimeoutError: If initialization exceeds timeout
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(extension_class)
            try:
                extension = future.result(timeout=timeout)

                # Initialize the extension
                future = executor.submit(extension.initialize)
                future.result(timeout=timeout)

                return extension
            except TimeoutError:
                logger.error(f"Extension {name} initialization timed out")
                raise

    def get_loaded_extensions(self) -> Dict[str, BaseExtension]:
        """Get all successfully loaded extensions.

        Returns:
            Dict[str, BaseExtension]: Loaded extensions
        """
        return self._loaded_extensions.copy()

    def get_failed_extensions(self) -> Dict[str, Exception]:
        """Get extensions that failed to load.

        Returns:
            Dict[str, Exception]: Failed extensions with their errors
        """
        return self._failed_extensions.copy()

    def get_extension(self, name: str) -> Optional[BaseExtension]:
        """Get a specific loaded extension by name.

        Args:
            name: The extension name

        Returns:
            Optional[BaseExtension]: The extension if loaded, None otherwise
        """
        return self._loaded_extensions.get(name)

    def is_extension_loaded(self, name: str) -> bool:
        """Check if an extension is loaded.

        Args:
            name: The extension name

        Returns:
            bool: True if the extension is loaded
        """
        return name in self._loaded_extensions

    def get_loading_stats(self) -> Dict[str, float]:
        """Get loading time statistics for extensions.

        Returns:
            Dict[str, float]: Extension names to loading times in seconds
        """
        return self._loading_times.copy()

    def reload_extension(self, name: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
        """Reload a specific extension.

        Args:
            name: The extension name to reload
            timeout: Maximum time for reloading

        Returns:
            bool: True if successfully reloaded
        """
        logger.info(f"Reloading extension: {name}")

        # Clean up existing extension if loaded
        if name in self._loaded_extensions:
            try:
                self._loaded_extensions[name].cleanup()
            except Exception as e:
                logger.warning(f"Error during cleanup of {name}: {e}")
            del self._loaded_extensions[name]

        # Clear any previous failure
        if name in self._failed_extensions:
            del self._failed_extensions[name]

        # Try to reload from discovery
        discovered = self.discovery.discover_extensions()
        if name not in discovered:
            logger.error(f"Extension {name} not found in discovery")
            return False

        # Load the extension
        extension = self._load_single_extension(name, discovered[name], timeout)
        if extension:
            self._loaded_extensions[name] = extension
            return True

        return False
