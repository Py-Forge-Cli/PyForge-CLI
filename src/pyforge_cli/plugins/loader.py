"""Plugin loader for discovering and loading converter plugins."""

import importlib
import pkgutil
from pathlib import Path
from typing import List, Optional

from ..converters.base import BaseConverter
from .registry import registry


class PluginLoader:
    """Loads converter plugins from various sources."""

    def __init__(self):
        self.loaded_plugins: List[str] = []

    def load_builtin_converters(self) -> None:
        """Load built-in converters from the converters package."""
        # Load PDF converter
        try:
            from ..converters.pdf_converter import PDFConverter

            registry.register("pdf", PDFConverter)
            self.loaded_plugins.append("pdf")
        except ImportError as e:
            print(f"Warning: Could not load PDF converter: {e}")

        # Load enhanced MDB converter (with fallback to basic)
        try:
            from ..converters.enhanced_mdb_converter import EnhancedMDBConverter

            registry.register("mdb", EnhancedMDBConverter)
            self.loaded_plugins.append("mdb")
            print("[OK] Loaded enhanced MDB converter with UCanAccess + pyodbc support")
        except ImportError as e:
            print(f"Warning: Enhanced MDB converter not available: {e}")
            # Fallback to basic MDB converter
            try:
                from ..converters import MDBConverter

                registry.register("mdb", MDBConverter)
                self.loaded_plugins.append("mdb")
                print("[OK] Loaded basic MDB converter (fallback)")
            except ImportError as e2:
                print(f"Warning: Could not load any MDB converter: {e2}")

        # Load DBF converter
        try:
            from ..converters import DBFConverter

            registry.register("dbf", DBFConverter)
            self.loaded_plugins.append("dbf")
        except ImportError as e:
            print(f"Warning: Could not load DBF converter: {e}")

        # Load Excel converter
        try:
            from ..converters.excel_converter import ExcelConverter

            registry.register("excel", ExcelConverter)
            self.loaded_plugins.append("excel")
        except ImportError as e:
            print(f"Warning: Could not load Excel converter: {e}")

        # Load CSV converter
        try:
            from ..converters.csv_converter import CSVConverter

            registry.register("csv", CSVConverter)
            self.loaded_plugins.append("csv")
        except ImportError as e:
            print(f"Warning: Could not load CSV converter: {e}")

        # Load XML converter
        try:
            from ..converters.xml import XmlConverter

            registry.register("xml", XmlConverter)
            self.loaded_plugins.append("xml")
        except ImportError as e:
            print(f"Warning: Could not load XML converter: {e}")

    def load_from_entry_points(self) -> None:
        """Load converters from setuptools entry points."""
        try:
            import pkg_resources

            for entry_point in pkg_resources.iter_entry_points(
                "cortexpy_cli.converters"
            ):
                try:
                    converter_class = entry_point.load()
                    if issubclass(converter_class, BaseConverter):
                        registry.register(entry_point.name, converter_class)
                        self.loaded_plugins.append(entry_point.name)
                except Exception as e:
                    print(f"Warning: Failed to load plugin {entry_point.name}: {e}")

        except ImportError:
            # pkg_resources not available, skip entry point loading
            pass

    def load_from_directory(self, plugin_dir: Path) -> None:
        """Load converters from a plugin directory.

        Args:
            plugin_dir: Directory containing converter plugins
        """
        if not plugin_dir.exists() or not plugin_dir.is_dir():
            return

        # Add plugin directory to Python path temporarily
        import sys

        sys.path.insert(0, str(plugin_dir))

        try:
            # Discover and load Python modules in the directory
            for module_info in pkgutil.iter_modules([str(plugin_dir)]):
                module_name = module_info.name

                try:
                    module = importlib.import_module(module_name)

                    # Look for converter classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseConverter)
                            and attr != BaseConverter
                        ):

                            converter_name = getattr(attr, "PLUGIN_NAME", module_name)
                            registry.register(converter_name, attr)
                            self.loaded_plugins.append(converter_name)

                except Exception as e:
                    print(f"Warning: Failed to load plugin module {module_name}: {e}")

        finally:
            # Remove plugin directory from Python path
            if str(plugin_dir) in sys.path:
                sys.path.remove(str(plugin_dir))

    def load_from_package(self, package_name: str) -> None:
        """Load converters from a Python package.

        Args:
            package_name: Name of the package containing converters
        """
        try:
            package = importlib.import_module(package_name)
            package_path = Path(package.__file__).parent

            # Look for converter modules in the package
            for module_info in pkgutil.iter_modules([str(package_path)]):
                module_name = f"{package_name}.{module_info.name}"

                try:
                    module = importlib.import_module(module_name)

                    # Look for converter classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseConverter)
                            and attr != BaseConverter
                        ):

                            converter_name = getattr(
                                attr, "PLUGIN_NAME", attr_name.lower()
                            )
                            registry.register(converter_name, attr)
                            self.loaded_plugins.append(converter_name)

                except Exception as e:
                    print(f"Warning: Failed to load converter from {module_name}: {e}")

        except ImportError as e:
            print(f"Warning: Could not import package {package_name}: {e}")

    def load_all(
        self,
        plugin_dirs: Optional[List[Path]] = None,
        packages: Optional[List[str]] = None,
    ) -> None:
        """Load converters from all available sources.

        Args:
            plugin_dirs: Additional directories to search for plugins
            packages: Additional packages to search for converters
        """
        # Load built-in converters
        self.load_builtin_converters()

        # Load from entry points
        self.load_from_entry_points()

        # Load from additional directories
        if plugin_dirs:
            for plugin_dir in plugin_dirs:
                self.load_from_directory(plugin_dir)

        # Load from additional packages
        if packages:
            for package in packages:
                self.load_from_package(package)

        # Load from user's home directory plugin folder
        home_plugins = Path.home() / ".cortexpy" / "plugins"
        if home_plugins.exists():
            self.load_from_directory(home_plugins)

    def get_loaded_plugins(self) -> List[str]:
        """Get list of successfully loaded plugin names.

        Returns:
            List of plugin names
        """
        return self.loaded_plugins.copy()

    def reload_plugins(self) -> None:
        """Reload all plugins (clear registry and reload)."""
        registry.clear()
        self.loaded_plugins.clear()
        self.load_all()


# Global plugin loader instance
plugin_loader = PluginLoader()
