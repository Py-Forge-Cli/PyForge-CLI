"""
Databricks Runtime Version Detection and Parsing Module

This module provides comprehensive runtime version detection, parsing,
and compatibility checking for Databricks environments.
"""

import logging
import os
import re
from functools import lru_cache
from typing import Any, Dict, List, Optional

from packaging import version


class RuntimeVersionDetector:
    """
    Detects and parses Databricks runtime versions with detailed feature mapping.

    Provides version parsing, comparison, and feature availability based on
    runtime version.
    """

    def __init__(self):
        """Initialize the runtime version detector."""
        self.logger = logging.getLogger("pyforge.extensions.databricks.runtime")

        # Version patterns
        self.VERSION_PATTERN = re.compile(
            r"^(\d+)\.(\d+)(?:\.(\d+))?(?:\.(x|dev|beta))?"
            r"(?:-([\w-]+))?"  # Variant (ml, gpu, serverless, etc.)
            r"(?:-scala(\d+\.\d+))?"  # Scala version
            r"(?:-(.+))?$"  # Additional tags
        )

        # Known LTS versions
        self.LTS_VERSIONS = {
            "11.3": "2023-06",
            "12.2": "2023-12",
            "13.3": "2024-06",
            "14.3": "2024-12",  # Projected
        }

        # Feature availability by version
        self.FEATURE_MATRIX = {
            "unity_catalog": 11.3,
            "serverless_compute": 13.0,
            "photon": 9.0,
            "delta_sharing": 10.0,
            "spark_connect": 13.0,
            "mlflow_2": 11.0,
            "automl": 10.0,
            "feature_store": 10.0,
            "model_serving": 11.0,
        }

        # Runtime variants
        self.RUNTIME_VARIANTS = {
            "ml": "Machine Learning",
            "gpu": "GPU-accelerated",
            "serverless": "Serverless Compute",
            "photon": "Photon-accelerated",
            "hls": "Healthcare & Life Sciences",
            "genomics": "Genomics",
        }

    def get_runtime_version(self) -> Optional[str]:
        """
        Get the raw runtime version string.

        Returns:
            Optional[str]: Runtime version or None
        """
        return os.environ.get("DATABRICKS_RUNTIME_VERSION")

    def parse_version(self, version_string: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse runtime version into structured components.

        Args:
            version_string: Version to parse (defaults to current runtime)

        Returns:
            Dict[str, Any]: Parsed version components
        """
        if version_string is None:
            version_string = self.get_runtime_version()

        if not version_string:
            return self._empty_version_info()

        # Try to match the version pattern
        match = self.VERSION_PATTERN.match(version_string)

        if not match:
            self.logger.warning(f"Could not parse version: {version_string}")
            return self._empty_version_info()

        groups = match.groups()

        # Extract components
        major = int(groups[0])
        minor = int(groups[1])
        patch = int(groups[2]) if groups[2] else 0
        stage = groups[3] if groups[3] else "release"
        variant = groups[4] if groups[4] else None
        scala_version = groups[5] if groups[5] else None
        tags = groups[6].split("-") if groups[6] else []

        # Determine variant from tags if not explicit
        if not variant and tags:
            for tag in tags:
                if tag in self.RUNTIME_VARIANTS:
                    variant = tag
                    break

        # Build structured version info
        version_info = {
            "raw": version_string,
            "major": major,
            "minor": minor,
            "patch": patch,
            "stage": stage,
            "variant": variant,
            "variant_name": (
                self.RUNTIME_VARIANTS.get(variant, variant) if variant else None
            ),
            "scala_version": scala_version,
            "tags": tags,
            "numeric_version": f"{major}.{minor}.{patch}",
            "is_lts": self.is_lts_version(major, minor),
            "lts_release_date": self.LTS_VERSIONS.get(f"{major}.{minor}"),
            "is_serverless": variant == "serverless" or "serverless" in tags,
            "is_ml": variant == "ml" or "ml" in tags,
            "is_gpu": variant == "gpu" or "gpu" in tags,
            "is_photon": variant == "photon" or "photon" in tags,
        }

        return version_info

    def is_lts_version(self, major: int, minor: int) -> bool:
        """
        Check if a version is LTS (Long Term Support).

        Args:
            major: Major version number
            minor: Minor version number

        Returns:
            bool: True if LTS version
        """
        version_key = f"{major}.{minor}"
        return version_key in self.LTS_VERSIONS

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two runtime versions.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        try:
            # Extract numeric versions for comparison
            v1_info = self.parse_version(version1)
            v2_info = self.parse_version(version2)

            v1_numeric = v1_info["numeric_version"]
            v2_numeric = v2_info["numeric_version"]

            if version.parse(v1_numeric) < version.parse(v2_numeric):
                return -1
            elif version.parse(v1_numeric) > version.parse(v2_numeric):
                return 1
            else:
                return 0

        except Exception as e:
            self.logger.error(f"Error comparing versions: {e}")
            return 0

    def get_feature_availability(
        self, runtime_version: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Get feature availability for a runtime version.

        Args:
            runtime_version: Version to check (defaults to current)

        Returns:
            Dict[str, bool]: Feature availability map
        """
        version_info = self.parse_version(runtime_version)

        if not version_info["major"]:
            # No valid version, assume no features
            return dict.fromkeys(self.FEATURE_MATRIX, False)

        numeric_version = float(f"{version_info['major']}.{version_info['minor']}")

        features = {}
        for feature, min_version in self.FEATURE_MATRIX.items():
            features[feature] = numeric_version >= min_version

        # Special cases for variants
        if version_info["is_serverless"]:
            features["serverless_compute"] = True
            features["unity_catalog"] = True  # Always in serverless
            features["photon"] = True  # Always in serverless

        if version_info["is_ml"]:
            features["mlflow_2"] = True
            features["automl"] = version_info["major"] >= 10
            features["feature_store"] = version_info["major"] >= 10

        return features

    def get_spark_version_mapping(self) -> Dict[str, str]:
        """
        Get Spark version for runtime versions.

        Returns:
            Dict[str, str]: Runtime to Spark version mapping
        """
        return {
            "14.3": "3.5.0",
            "14.2": "3.5.0",
            "14.1": "3.5.0",
            "14.0": "3.5.0",
            "13.3": "3.4.1",
            "13.2": "3.4.1",
            "13.1": "3.4.0",
            "13.0": "3.4.0",
            "12.2": "3.3.2",
            "12.1": "3.3.1",
            "12.0": "3.3.1",
            "11.3": "3.3.0",
            "11.2": "3.3.0",
            "11.1": "3.3.0",
            "11.0": "3.3.0",
            "10.4": "3.2.1",
            "10.3": "3.2.1",
            "10.2": "3.2.0",
            "10.1": "3.2.0",
            "10.0": "3.2.0",
        }

    def get_expected_spark_version(
        self, runtime_version: Optional[str] = None
    ) -> Optional[str]:
        """
        Get expected Spark version for a runtime.

        Args:
            runtime_version: Runtime version to check

        Returns:
            Optional[str]: Expected Spark version
        """
        version_info = self.parse_version(runtime_version)
        if not version_info["major"]:
            return None

        mapping = self.get_spark_version_mapping()
        version_key = f"{version_info['major']}.{version_info['minor']}"

        return mapping.get(version_key)

    def check_compatibility(self, required_version: str) -> bool:
        """
        Check if current runtime meets minimum version requirement.

        Args:
            required_version: Minimum required version (e.g., "13.0")

        Returns:
            bool: True if current version meets requirement
        """
        current = self.get_runtime_version()
        if not current:
            return False

        return self.compare_versions(current, required_version) >= 0

    def get_deprecation_warnings(self) -> List[str]:
        """
        Get deprecation warnings for current runtime.

        Returns:
            List[str]: List of deprecation warnings
        """
        warnings = []
        version_info = self.parse_version()

        if not version_info["major"]:
            return warnings

        # Check for old runtime versions
        if version_info["major"] < 11:
            warnings.append(
                f"Runtime {version_info['numeric_version']} is deprecated. "
                "Please upgrade to 11.3 LTS or newer."
            )

        # Check for non-LTS versions older than 6 months
        if not version_info["is_lts"] and version_info["major"] < 13:
            warnings.append(
                f"Non-LTS runtime {version_info['numeric_version']} may be deprecated soon. "
                "Consider using an LTS version for stability."
            )

        # Check for old ML runtime
        if version_info["is_ml"] and version_info["major"] < 12:
            warnings.append(
                "ML runtime older than 12.x has outdated ML libraries. "
                "Please upgrade for latest features."
            )

        return warnings

    def get_runtime_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations based on current runtime.

        Returns:
            Dict[str, Any]: Runtime recommendations
        """
        version_info = self.parse_version()
        recommendations = {
            "current_version": version_info["raw"],
            "recommendations": [],
        }

        if not version_info["major"]:
            recommendations["recommendations"].append(
                {"type": "error", "message": "No Databricks runtime detected"}
            )
            return recommendations

        # LTS recommendation
        if not version_info["is_lts"]:
            latest_lts = "13.3 LTS"
            recommendations["recommendations"].append(
                {
                    "type": "stability",
                    "message": f"Consider using {latest_lts} for long-term stability",
                }
            )

        # Serverless recommendation
        if not version_info["is_serverless"] and version_info["major"] >= 13:
            recommendations["recommendations"].append(
                {
                    "type": "performance",
                    "message": "Serverless compute available for instant startup and auto-scaling",
                }
            )

        # ML runtime recommendation
        if not version_info["is_ml"] and self._detect_ml_workload():
            recommendations["recommendations"].append(
                {
                    "type": "feature",
                    "message": "Consider ML runtime for optimized machine learning libraries",
                }
            )

        # GPU runtime recommendation
        if not version_info["is_gpu"] and self._detect_gpu_available():
            recommendations["recommendations"].append(
                {
                    "type": "performance",
                    "message": "GPU runtime available for accelerated computation",
                }
            )

        return recommendations

    @lru_cache(maxsize=1)
    def get_full_version_report(self) -> Dict[str, Any]:
        """
        Get comprehensive version report.

        Returns:
            Dict[str, Any]: Full version analysis
        """
        version_info = self.parse_version()

        return {
            "version_info": version_info,
            "features": self.get_feature_availability(),
            "expected_spark_version": self.get_expected_spark_version(),
            "actual_spark_version": os.environ.get("SPARK_VERSION"),
            "deprecation_warnings": self.get_deprecation_warnings(),
            "recommendations": self.get_runtime_recommendations(),
            "environment": {
                "python_version": self._get_python_version(),
                "scala_version": version_info.get("scala_version"),
                "java_version": self._get_java_version(),
            },
        }

    # Private helper methods

    def _empty_version_info(self) -> Dict[str, Any]:
        """Return empty version info structure."""
        return {
            "raw": None,
            "major": None,
            "minor": None,
            "patch": None,
            "stage": None,
            "variant": None,
            "variant_name": None,
            "scala_version": None,
            "tags": [],
            "numeric_version": None,
            "is_lts": False,
            "lts_release_date": None,
            "is_serverless": False,
            "is_ml": False,
            "is_gpu": False,
            "is_photon": False,
        }

    def _detect_ml_workload(self) -> bool:
        """Detect if ML libraries are being used."""
        ml_indicators = ["MLFLOW_", "DATABRICKS_AUTOML", "FEATURE_STORE"]

        for var in os.environ:
            if any(indicator in var for indicator in ml_indicators):
                return True

        # Check for ML library imports
        try:
            import mlflow  # noqa: F401

            return True
        except ImportError:
            pass

        return False

    def _detect_gpu_available(self) -> bool:
        """Detect if GPUs are available."""
        # Check CUDA
        if os.path.exists("/usr/local/cuda"):
            return True

        # Check nvidia-smi
        try:
            import subprocess

            result = subprocess.run(
                ["nvidia-smi", "-L"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            pass

        return False

    def _get_python_version(self) -> str:
        """Get Python version."""
        import sys

        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def _get_java_version(self) -> Optional[str]:
        """Get Java version if available."""
        try:
            import subprocess

            result = subprocess.run(
                ["java", "-version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Parse version from stderr (Java outputs version to stderr)
                output = result.stderr
                version_match = re.search(r'version "(\d+\.\d+\.\d+)', output)
                if version_match:
                    return version_match.group(1)
        except Exception:
            pass

        return None
