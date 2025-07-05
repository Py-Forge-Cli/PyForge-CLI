"""
Databricks Serverless Compute Detection Module

This module provides specialized detection logic for Databricks serverless compute
environments, including advanced detection methods and feature capability checks.
"""

import logging
import os
from typing import Any, Dict, List


class ServerlessDetector:
    """
    Specialized detector for Databricks serverless compute environments.

    This class provides multiple detection methods to reliably identify
    serverless compute environments and their specific capabilities.
    """

    def __init__(self):
        """Initialize the serverless detector."""
        self.logger = logging.getLogger("pyforge.extensions.databricks.serverless")

        # Known serverless indicators
        self.SERVERLESS_MARKERS = [
            "serverless",
            "photon",
            "spark-connect",
            "unity-only",
        ]

        # Serverless-specific paths
        self.SERVERLESS_PATHS = [
            "/databricks/serverless",
            "/databricks/spark-connect",
            "/opt/spark-serverless",
        ]

        # Serverless environment variables
        self.SERVERLESS_ENV_VARS = {
            "DATABRICKS_SERVERLESS_COMPUTE": ["true", "1", "yes"],
            "IS_SERVERLESS_COMPUTE": ["true", "1", "yes"],
            "SERVERLESS_COMPUTE_ENABLED": ["true", "1", "yes"],
            "PHOTON_ENABLED": ["true", "1", "yes"],
            "SPARK_CONNECT_MODE": ["true", "1", "yes"],
            "DATABRICKS_COMPUTE_TYPE": ["serverless", "sql-serverless"],
        }

        # Serverless Spark configurations
        self.SERVERLESS_SPARK_CONFIGS = {
            "spark.databricks.service.serverless.enabled": "true",
            "spark.databricks.photon.enabled": "true",
            "spark.databricks.unityCatalog.enforced": "true",
            "spark.databricks.service.sparkConnect.enabled": "true",
            "spark.databricks.compute.serverless": "true",
        }

    def is_serverless(self) -> bool:
        """
        Determine if running in serverless compute with high confidence.

        Uses multiple detection methods and requires at least 2 positive
        signals for confident detection.

        Returns:
            bool: True if serverless compute detected
        """
        detection_signals = []

        # Method 1: Runtime version check
        if self._check_runtime_version():
            detection_signals.append("runtime_version")
            self.logger.debug("Serverless detected via runtime version")

        # Method 2: Environment variables
        if self._check_environment_variables():
            detection_signals.append("env_vars")
            self.logger.debug("Serverless detected via environment variables")

        # Method 3: File system markers
        if self._check_filesystem_markers():
            detection_signals.append("filesystem")
            self.logger.debug("Serverless detected via filesystem markers")

        # Method 4: Spark configuration
        if self._check_spark_configuration():
            detection_signals.append("spark_config")
            self.logger.debug("Serverless detected via Spark configuration")

        # Method 5: Process characteristics
        if self._check_process_characteristics():
            detection_signals.append("process")
            self.logger.debug("Serverless detected via process characteristics")

        # Require at least 2 positive signals for confident detection
        is_serverless = len(detection_signals) >= 2

        if is_serverless:
            self.logger.info(
                f"Serverless compute confirmed with signals: {detection_signals}"
            )
        else:
            self.logger.info(
                f"Not serverless compute. Signals found: {detection_signals}"
            )

        return is_serverless

    def get_serverless_features(self) -> Dict[str, bool]:
        """
        Get detailed serverless compute features and capabilities.

        Returns:
            Dict[str, bool]: Dictionary of feature availability
        """
        if not self.is_serverless():
            return {
                "photon_acceleration": False,
                "auto_scaling": False,
                "spark_connect": False,
                "unity_catalog_only": False,
                "serverless_sql": False,
                "instant_compute": False,
            }

        features = {
            "photon_acceleration": self._check_photon_enabled(),
            "auto_scaling": True,  # Always true for serverless
            "spark_connect": self._check_spark_connect(),
            "unity_catalog_only": self._check_unity_catalog_enforced(),
            "serverless_sql": self._check_serverless_sql(),
            "instant_compute": True,  # Always true for serverless
        }

        self.logger.debug(f"Serverless features: {features}")

        return features

    def get_serverless_limitations(self) -> List[str]:
        """
        Get list of limitations in serverless compute.

        Returns:
            List[str]: List of limitation descriptions
        """
        if not self.is_serverless():
            return []

        limitations = [
            "DBFS access is restricted - use Unity Catalog Volumes",
            "Some Spark configurations cannot be modified",
            "Direct cluster access is not available",
            "Custom libraries must be installed via Unity Catalog",
            "Init scripts are not supported",
            "Some RDD operations are restricted",
        ]

        # Check for specific limitations
        if not self._check_dbfs_access():
            limitations.append("DBFS is completely disabled")

        return limitations

    # Private detection methods

    def _check_runtime_version(self) -> bool:
        """Check runtime version for serverless markers."""
        runtime_version = os.environ.get("DATABRICKS_RUNTIME_VERSION", "").lower()

        if not runtime_version:
            return False

        # Check for serverless markers in version string
        for marker in self.SERVERLESS_MARKERS:
            if marker in runtime_version:
                return True

        return False

    def _check_environment_variables(self) -> bool:
        """Check environment variables for serverless indicators."""
        for env_var, valid_values in self.SERVERLESS_ENV_VARS.items():
            value = os.environ.get(env_var, "").lower()
            if value in valid_values:
                self.logger.debug(f"Found serverless indicator: {env_var}={value}")
                return True

        return False

    def _check_filesystem_markers(self) -> bool:
        """Check for serverless-specific filesystem markers."""
        for path in self.SERVERLESS_PATHS:
            if os.path.exists(path):
                self.logger.debug(f"Found serverless path: {path}")
                return True

        # Check for absence of classic compute paths
        classic_paths = ["/databricks/driver", "/databricks/executor"]
        missing_classic = sum(1 for p in classic_paths if not os.path.exists(p))

        if missing_classic >= len(classic_paths):
            self.logger.debug("Classic compute paths missing - likely serverless")
            return True

        return False

    def _check_spark_configuration(self) -> bool:
        """Check Spark configuration for serverless settings."""
        try:
            from pyspark.sql import SparkSession

            spark = SparkSession.builder.getOrCreate()

            matches = 0
            for config_key, expected_value in self.SERVERLESS_SPARK_CONFIGS.items():
                try:
                    actual_value = spark.conf.get(config_key, "").lower()
                    if actual_value == expected_value.lower():
                        matches += 1
                        self.logger.debug(
                            f"Spark config match: {config_key}={actual_value}"
                        )
                except Exception:
                    continue

            # Consider serverless if at least 3 configs match
            return matches >= 3

        except Exception as e:
            self.logger.debug(f"Could not check Spark configuration: {e}")
            return False

    def _check_process_characteristics(self) -> bool:
        """Check process characteristics for serverless patterns."""
        try:
            # Check for Spark Connect process
            import psutil

            current_process = psutil.Process()

            # Look for Spark Connect in process tree
            for proc in current_process.children(recursive=True):
                if "spark-connect" in proc.name().lower():
                    return True

            # Check for serverless-specific process patterns
            cmdline = " ".join(current_process.cmdline())
            if any(
                marker in cmdline.lower() for marker in ["serverless", "spark-connect"]
            ):
                return True

        except Exception:
            pass

        return False

    def _check_photon_enabled(self) -> bool:
        """Check if Photon acceleration is enabled."""
        # Check environment
        if os.environ.get("PHOTON_ENABLED", "").lower() in ["true", "1", "yes"]:
            return True

        # Check Spark config
        try:
            from pyspark.sql import SparkSession

            spark = SparkSession.builder.getOrCreate()
            photon_enabled = spark.conf.get("spark.databricks.photon.enabled", "false")
            return photon_enabled.lower() == "true"
        except Exception:
            return False

    def _check_spark_connect(self) -> bool:
        """Check if Spark Connect is enabled."""
        # Environment check
        if os.environ.get("SPARK_CONNECT_MODE", "").lower() in ["true", "1", "yes"]:
            return True

        # Check for Spark Connect server
        try:
            spark_connect_url = os.environ.get("SPARK_CONNECT_URL")
            if spark_connect_url:
                return True
        except Exception:
            pass

        return False

    def _check_unity_catalog_enforced(self) -> bool:
        """Check if Unity Catalog is enforced (no DBFS access)."""
        try:
            from pyspark.sql import SparkSession

            spark = SparkSession.builder.getOrCreate()
            enforced = spark.conf.get("spark.databricks.unityCatalog.enforced", "false")
            return enforced.lower() == "true"
        except Exception:
            # In serverless, Unity Catalog is always enforced
            return self.is_serverless()

    def _check_serverless_sql(self) -> bool:
        """Check if running on serverless SQL compute."""
        compute_type = os.environ.get("DATABRICKS_COMPUTE_TYPE", "").lower()
        return "sql" in compute_type and "serverless" in compute_type

    def _check_dbfs_access(self) -> bool:
        """Check if DBFS access is available."""
        try:
            # Try to access DBFS root
            dbfs_path = "/dbfs"
            if os.path.exists(dbfs_path) and os.access(dbfs_path, os.R_OK):
                return True
        except Exception:
            pass

        return False

    def get_detection_report(self) -> Dict[str, Any]:
        """
        Generate a detailed detection report.

        Returns:
            Dict[str, Any]: Comprehensive detection results
        """
        report = {
            "is_serverless": self.is_serverless(),
            "detection_methods": {
                "runtime_version": self._check_runtime_version(),
                "environment_variables": self._check_environment_variables(),
                "filesystem_markers": self._check_filesystem_markers(),
                "spark_configuration": self._check_spark_configuration(),
                "process_characteristics": self._check_process_characteristics(),
            },
            "features": self.get_serverless_features(),
            "limitations": self.get_serverless_limitations(),
            "environment_details": {
                "runtime_version": os.environ.get(
                    "DATABRICKS_RUNTIME_VERSION", "Not found"
                ),
                "compute_type": os.environ.get("DATABRICKS_COMPUTE_TYPE", "Not found"),
                "has_dbfs_access": self._check_dbfs_access(),
            },
        }

        return report
