"""
Databricks Extension for PyForge CLI

This module implements the main extension class that integrates with PyForge CLI's
plugin system, providing Databricks-specific optimizations and features.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pyforge_cli.extensions.base import BaseExtension

from .converter_selector import ConverterSelector
from .environment import DatabricksEnvironment
from .fallback_manager import FallbackManager
from .pyforge_databricks import PyForgeDatabricks
from .volume_operations import VolumeOperations


class DatabricksExtension(BaseExtension):
    """
    Databricks extension for PyForge CLI.

    Provides:
    - Automatic Databricks environment detection
    - Serverless and classic compute optimization
    - Unity Catalog Volume integration
    - Spark-based converters for large files
    - Intelligent converter selection with fallback
    """

    def __init__(self):
        """Initialize the Databricks extension."""
        super().__init__()

        # Extension metadata
        self.name = "databricks"
        self.version = "1.0.0"
        self.description = (
            "Databricks integration with Unity Catalog and PySpark optimization"
        )

        # Core components
        self.environment = DatabricksEnvironment()
        self.converter_selector = ConverterSelector()
        self.fallback_manager = FallbackManager()
        self.volume_ops = VolumeOperations()

        # Notebook API
        self._notebook_api: Optional[PyForgeDatabricks] = None

        # Configuration
        self.config = self._load_config()

        # Set up logging
        self.logger = logging.getLogger(f"pyforge.extensions.{self.name}")

    def is_available(self) -> bool:
        """
        Check if extension can run in current environment.

        Returns:
            bool: True if in Databricks environment
        """
        # Always available, but features vary by environment
        return True

    def initialize(self) -> bool:
        """
        Initialize the extension.

        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info(f"Initializing {self.name} extension v{self.version}")

            # Check environment
            if self.environment.is_databricks_environment():
                env_info = self.environment.get_environment_info()
                self.logger.info(
                    f"Databricks environment detected: "
                    f"{env_info['compute_type']} "
                    f"(Runtime: {env_info['runtime_version']})"
                )

                # Check for required features
                if not env_info.get("has_pyspark"):
                    self.logger.warning(
                        "PySpark not available - some features disabled"
                    )
            else:
                self.logger.info(
                    "Non-Databricks environment - running in compatibility mode"
                )

            # Initialize components
            self._register_converters()

            self.initialized = True
            self.logger.info(f"{self.name} extension initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Extension initialization failed: {e}", exc_info=True)
            return False

    def cleanup(self) -> None:
        """Clean up extension resources."""
        try:
            # Stop any streaming queries
            if hasattr(self, "_streaming_support"):
                self._streaming_support.stop_all_streams()

            # Clear caches
            self.environment.clear_cache()

            self.logger.info(f"{self.name} extension cleaned up")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        finally:
            super().cleanup()

    def get_commands(self) -> Dict[str, Any]:
        """
        Get additional CLI commands provided by this extension.

        Returns:
            Dict[str, Any]: Command implementations
        """
        return {
            "install-datasets": self._install_datasets_command,
            "list-volumes": self._list_volumes_command,
            "env-info": self._env_info_command,
            "validate-volume": self._validate_volume_command,
        }

    def enhance_convert_command(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance convert command with Databricks-specific options.

        Args:
            options: Current conversion options

        Returns:
            Dict[str, Any]: Enhanced options
        """
        if not self.initialized:
            return options

        # Add Databricks-specific options
        env_info = self.environment.get_environment_info()

        if env_info["is_databricks"]:
            # Enable Spark optimization for large files
            if options.get("file_size", 0) > 100 * 1024 * 1024:  # 100MB
                options.setdefault("use_spark", True)

            # Serverless-specific optimizations
            if env_info["compute_type"] == "serverless":
                options.setdefault("adaptive_execution", True)
                options.setdefault(
                    "photon_enabled",
                    env_info.get("serverless_features", {}).get(
                        "photon_acceleration", False
                    ),
                )

            # Unity Catalog Volume detection
            input_path = options.get("input_file", "")
            if isinstance(input_path, (str, Path)) and str(input_path).startswith(
                "/Volumes"
            ):
                options["is_volume_path"] = True
                options["volume_info"] = self.volume_ops.parse_volume_path(
                    str(input_path)
                )

        return options

    # Hook implementations

    def hook_pre_conversion(
        self, input_file: Path, output_file: Path, options: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Pre-conversion hook for Databricks optimizations.

        Args:
            input_file: Input file path
            output_file: Output file path
            options: Conversion options

        Returns:
            Optional[Dict[str, Any]]: Modified options
        """
        try:
            if not self.initialized:
                return options

            # Skip if not in Databricks
            if not self.environment.is_databricks_environment():
                return options

            self.logger.debug(f"Pre-conversion hook: {input_file} -> {output_file}")

            # Validate Volume paths
            if str(input_file).startswith("/Volumes"):
                valid, error = self.volume_ops.validate_volume_access(str(input_file))
                if not valid:
                    self.logger.error(f"Volume validation failed: {error}")
                    # Don't fail - let core handle it

            # Get converter recommendation
            recommendation = self.converter_selector.select_converter(
                input_file, output_file.suffix.lstrip("."), options
            )

            # Add recommendation to options
            options["databricks_converter"] = recommendation.converter_type.value
            options["databricks_confidence"] = recommendation.confidence
            options["databricks_reasons"] = recommendation.reasons

            # Add environment context
            options["databricks_environment"] = self.environment.get_environment_info()

            return options

        except Exception as e:
            self.logger.error(f"Error in pre-conversion hook: {e}")
            return options  # Don't break conversion

    def hook_post_conversion(
        self,
        input_file: Path,
        output_file: Path,
        options: Dict[str, Any],
        success: bool,
    ) -> None:
        """
        Post-conversion hook for logging and cleanup.

        Args:
            input_file: Input file path
            output_file: Output file path
            options: Conversion options used
            success: Whether conversion was successful
        """
        try:
            if not self.initialized:
                return

            status = "SUCCESS" if success else "FAILED"
            self.logger.info(
                f"Post-conversion [{status}]: {input_file} -> {output_file}"
            )

            # Log Databricks-specific information
            if "databricks_converter" in options:
                self.logger.info(
                    f"Used {options['databricks_converter']} converter "
                    f"(confidence: {options.get('databricks_confidence', 'N/A')})"
                )

            # Update statistics if available
            if hasattr(self, "_conversion_stats"):
                self._conversion_stats["total"] += 1
                if success:
                    self._conversion_stats["successful"] += 1
                else:
                    self._conversion_stats["failed"] += 1

        except Exception as e:
            self.logger.error(f"Error in post-conversion hook: {e}")

    def hook_error_handling(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Handle Databricks-specific errors.

        Args:
            error: The exception that occurred
            context: Error context

        Returns:
            bool: True if error was handled
        """
        try:
            error_type = type(error).__name__
            error_msg = str(error).lower()

            # Handle Spark-specific errors
            if "spark" in error_msg or "pyspark" in error_type.lower():
                self.logger.info("Handling Spark error - attempting fallback to pandas")
                context["fallback_to_pandas"] = True
                return True

            # Handle Volume access errors
            if "volume" in error_msg or "/volumes" in error_msg:
                self.logger.info("Handling Volume access error")
                context["volume_error"] = True
                # Could attempt to copy to local first
                return False  # Let default handling continue

            # Handle memory errors in Spark
            if (
                isinstance(error, MemoryError)
                and self.environment.is_databricks_environment()
            ):
                self.logger.info(
                    "Memory error in Databricks - suggesting streaming mode"
                )
                context["suggest_streaming"] = True
                return False

        except Exception as e:
            self.logger.error(f"Error in error handling hook: {e}")

        return False

    def hook_environment_detection(self) -> Dict[str, Any]:
        """
        Detect Databricks environment details.

        Returns:
            Dict[str, Any]: Environment information
        """
        env_info = {}

        try:
            if self.environment.is_databricks_environment():
                env_info = self.environment.get_environment_info()

                # Add extension-specific info
                env_info["extension_active"] = True
                env_info["extension_version"] = self.version

                # Check for specific capabilities
                if env_info.get("has_unity_catalog"):
                    # Test Volume access
                    test_volume = "/Volumes/main/default"
                    if os.path.exists(test_volume):
                        env_info["volume_access"] = True

        except Exception as e:
            self.logger.error(f"Error in environment detection: {e}")

        return env_info

    def hook_performance_optimization(
        self, operation: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply Databricks-specific performance optimizations.

        Args:
            operation: Operation being performed
            options: Current options

        Returns:
            Dict[str, Any]: Optimized options
        """
        try:
            if (
                operation != "convert"
                or not self.environment.is_databricks_environment()
            ):
                return options

            env_info = self.environment.get_environment_info()

            # Serverless optimizations
            if env_info["compute_type"] == "serverless":
                options.update(
                    {
                        "spark.sql.adaptive.enabled": "true",
                        "spark.sql.adaptive.coalescePartitions.enabled": "true",
                        "spark.databricks.photon.enabled": "true",
                    }
                )

            # File size based optimizations
            file_size = options.get("file_size", 0)

            if file_size > 1024 * 1024 * 1024:  # 1GB
                options["use_streaming"] = True
                options["batch_size"] = 10000
            elif file_size > 100 * 1024 * 1024:  # 100MB
                options["use_spark"] = True
                options["repartition"] = True

        except Exception as e:
            self.logger.error(f"Error in performance optimization: {e}")

        return options

    # Command implementations

    def _install_datasets_command(
        self, volume_path: Optional[str] = None, **kwargs
    ) -> bool:
        """Install sample datasets to Unity Catalog Volume."""
        try:
            if not volume_path:
                print("Please specify a Volume path with --volume-path")
                return False

            # Validate Volume path
            valid, error = self.volume_ops.validate_volume_access(volume_path)
            if not valid:
                print(f"Invalid Volume path: {error}")
                return False

            print(f"Installing sample datasets to {volume_path}...")

            # Create PyForgeDatabricks instance for the operation
            forge = PyForgeDatabricks()
            result = forge.install_sample_datasets(volume_path)

            if result["success"]:
                print("[OK] Sample datasets installed successfully")
            else:
                print(
                    f"[FAIL] Installation failed: {result.get('error', 'Unknown error')}"
                )

            return result["success"]

        except Exception as e:
            print(f"Error installing datasets: {e}")
            return False

    def _list_volumes_command(self, **kwargs) -> bool:
        """List available Unity Catalog Volumes."""
        try:
            if not self.environment.is_databricks_environment():
                print("This command is only available in Databricks environments")
                return False

            print("Listing Unity Catalog Volumes...")

            # This would query the catalog - placeholder for now
            print("Volume listing not yet implemented")

            return True

        except Exception as e:
            print(f"Error listing volumes: {e}")
            return False

    def _env_info_command(self, **kwargs) -> bool:
        """Display environment information."""
        try:
            env_info = self.environment.get_environment_info()

            print("PyForge Databricks Environment Information")
            print("=" * 50)

            if env_info["is_databricks"]:
                print("[OK] Running in Databricks")
                print(f"   Compute Type: {env_info['compute_type']}")
                print(f"   Runtime Version: {env_info['runtime_version']}")
                print(f"   Spark Version: {env_info['spark_version']}")
                print(f"   Python Version: {env_info['python_version']}")
                print(
                    f"   Unity Catalog: {'[OK]' if env_info['has_unity_catalog'] else '[FAIL]'}"
                )
                print(
                    f"   PySpark Available: {'[OK]' if env_info['has_pyspark'] else '[FAIL]'}"
                )

                if env_info["compute_type"] == "serverless":
                    print("\nServerless Features:")
                    features = env_info.get("serverless_features", {})
                    for feature, enabled in features.items():
                        status = "[OK]" if enabled else "[FAIL]"
                        print(f"   {feature}: {status}")
            else:
                print("[FAIL] Not running in Databricks")
                print("   Running in local/standard environment")

            return True

        except Exception as e:
            print(f"Error getting environment info: {e}")
            return False

    def _validate_volume_command(self, volume_path: str, **kwargs) -> bool:
        """Validate access to a Unity Catalog Volume."""
        try:
            if not volume_path:
                print("Please specify a Volume path to validate")
                return False

            print(f"Validating Volume: {volume_path}")

            valid, error = self.volume_ops.validate_volume_access(volume_path)

            if valid:
                print("[OK] Volume is accessible")

                # Get Volume metadata
                volume_info = self.volume_ops.get_volume_metadata(volume_path)
                if volume_info:
                    print("\nVolume Details:")
                    print(f"   Catalog: {volume_info.catalog}")
                    print(f"   Schema: {volume_info.schema}")
                    print(f"   Volume: {volume_info.volume}")
                    if volume_info.is_managed is not None:
                        print(
                            f"   Type: {'Managed' if volume_info.is_managed else 'External'}"
                        )
            else:
                print(f"[FAIL] Volume validation failed: {error}")

            return valid

        except Exception as e:
            print(f"Error validating volume: {e}")
            return False

    # Private helper methods

    def _load_config(self) -> Dict[str, Any]:
        """Load extension configuration."""
        default_config = {
            "auto_detect_environment": True,
            "enable_spark_optimization": True,
            "enable_streaming": True,
            "default_output_format": "parquet",
            "spark_memory_fraction": 0.8,
            "adaptive_execution": True,
        }

        # Could load from file or environment
        return default_config

    def _register_converters(self):
        """Register Spark converters with fallback manager."""
        # This is handled by PyForgeDatabricks when needed
        pass

    def get_notebook_api(self) -> PyForgeDatabricks:
        """
        Get the notebook API instance.

        Returns:
            PyForgeDatabricks: Notebook API instance
        """
        if self._notebook_api is None:
            self._notebook_api = PyForgeDatabricks(auto_init=True)
        return self._notebook_api
