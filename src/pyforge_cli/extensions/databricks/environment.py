"""
Databricks Environment Detection Module

This module provides comprehensive environment detection for Databricks runtime,
including serverless vs classic compute detection, runtime version parsing,
and Unity Catalog availability.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, Tuple
from functools import lru_cache
from datetime import datetime, timedelta
from pathlib import Path


class DatabricksEnvironment:
    """
    Detects and manages Databricks environment information.
    
    This class provides methods to detect the Databricks runtime environment,
    determine compute type (serverless vs classic), parse runtime versions,
    and cache environment information for performance.
    """
    
    def __init__(self):
        """Initialize the Databricks environment detector."""
        self.logger = logging.getLogger("pyforge.extensions.databricks.environment")
        self._cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)  # Cache for 5 minutes
        
        # Environment variable names
        self.RUNTIME_VERSION_VAR = "DATABRICKS_RUNTIME_VERSION"
        self.SPARK_VERSION_VAR = "SPARK_VERSION"
        self.SERVERLESS_MARKER = "serverless"
        
        # File system markers
        self.DATABRICKS_ROOT = "/databricks"
        self.DRIVER_LOGS_PATH = "/databricks/driver/logs"
        self.SPARK_CONF_DIR = "/databricks/spark/conf"
        
    def is_databricks_environment(self) -> bool:
        """
        Check if running in any Databricks environment.
        
        Returns:
            bool: True if running in Databricks, False otherwise
        """
        # Check cache first
        cache_key = "is_databricks"
        if self._check_cache(cache_key):
            return self._cache[cache_key]
        
        is_databricks = False
        
        # Method 1: Check for Databricks runtime version
        if os.environ.get(self.RUNTIME_VERSION_VAR):
            is_databricks = True
            self.logger.debug(f"Detected Databricks via {self.RUNTIME_VERSION_VAR}")
        
        # Method 2: Check for Databricks-specific paths
        elif os.path.exists(self.DATABRICKS_ROOT):
            is_databricks = True
            self.logger.debug(f"Detected Databricks via {self.DATABRICKS_ROOT}")
        
        # Method 3: Check for Databricks-specific environment patterns
        elif self._check_databricks_env_patterns():
            is_databricks = True
            self.logger.debug("Detected Databricks via environment patterns")
        
        # Cache the result
        self._set_cache(cache_key, is_databricks)
        
        return is_databricks
    
    def get_compute_type(self) -> str:
        """
        Determine the Databricks compute type.
        
        Returns:
            str: "serverless", "classic", or "unknown"
        """
        if not self.is_databricks_environment():
            return "unknown"
        
        # Check cache
        cache_key = "compute_type"
        if self._check_cache(cache_key):
            return self._cache[cache_key]
        
        compute_type = "unknown"
        
        # Method 1: Check runtime version for serverless marker
        runtime_version = self.get_runtime_version()
        if runtime_version and self.SERVERLESS_MARKER in runtime_version.lower():
            compute_type = "serverless"
            self.logger.info("Detected serverless compute from runtime version")
        
        # Method 2: Check environment variables
        elif self._is_serverless_by_env():
            compute_type = "serverless"
            self.logger.info("Detected serverless compute from environment")
        
        # Method 3: Check Spark configuration
        elif self._is_serverless_by_spark_conf():
            compute_type = "serverless"
            self.logger.info("Detected serverless compute from Spark config")
        
        # Default to classic if Databricks but not serverless
        elif self.is_databricks_environment():
            compute_type = "classic"
            self.logger.info("Detected classic compute (non-serverless Databricks)")
        
        # Cache the result
        self._set_cache(cache_key, compute_type)
        
        return compute_type
    
    def get_runtime_version(self) -> Optional[str]:
        """
        Get the Databricks runtime version.
        
        Returns:
            Optional[str]: Runtime version string or None
        """
        # Check cache
        cache_key = "runtime_version"
        if self._check_cache(cache_key):
            return self._cache[cache_key]
        
        runtime_version = os.environ.get(self.RUNTIME_VERSION_VAR)
        
        if runtime_version:
            self.logger.debug(f"Runtime version: {runtime_version}")
        else:
            self.logger.debug("No runtime version found")
        
        # Cache the result
        self._set_cache(cache_key, runtime_version)
        
        return runtime_version
    
    def parse_runtime_version(self) -> Tuple[Optional[int], Optional[int], bool]:
        """
        Parse the runtime version into components.
        
        Returns:
            Tuple[Optional[int], Optional[int], bool]: (major, minor, is_lts)
        """
        runtime_version = self.get_runtime_version()
        if not runtime_version:
            return None, None, False
        
        # Example formats:
        # "13.3.x-scala2.12" (LTS)
        # "14.0.x-scala2.12" (standard)
        # "13.3.x-serverless-scala2.12" (serverless)
        
        try:
            # Extract numeric version
            version_parts = runtime_version.split("-")[0].split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            # Check if LTS (Long Term Support)
            is_lts = major in [11, 12, 13]  # Known LTS versions
            
            return major, minor, is_lts
            
        except (ValueError, IndexError) as e:
            self.logger.warning(f"Failed to parse runtime version '{runtime_version}': {e}")
            return None, None, False
    
    def get_spark_version(self) -> Optional[str]:
        """
        Get the Spark version.
        
        Returns:
            Optional[str]: Spark version string or None
        """
        # Check cache
        cache_key = "spark_version"
        if self._check_cache(cache_key):
            return self._cache[cache_key]
        
        spark_version = os.environ.get(self.SPARK_VERSION_VAR)
        
        # Try to get from SparkContext if available
        if not spark_version:
            try:
                from pyspark import SparkContext
                sc = SparkContext.getOrCreate()
                spark_version = sc.version
            except Exception:
                pass
        
        # Cache the result
        self._set_cache(cache_key, spark_version)
        
        return spark_version
    
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get comprehensive environment information.
        
        Returns:
            Dict[str, Any]: Dictionary containing all environment details
        """
        # Check cache
        cache_key = "environment_info"
        if self._check_cache(cache_key):
            return self._cache[cache_key]
        
        # Gather all information
        runtime_version = self.get_runtime_version()
        major, minor, is_lts = self.parse_runtime_version()
        
        info = {
            "is_databricks": self.is_databricks_environment(),
            "compute_type": self.get_compute_type(),
            "runtime_version": runtime_version,
            "runtime_major": major,
            "runtime_minor": minor,
            "is_lts": is_lts,
            "spark_version": self.get_spark_version(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "has_unity_catalog": self._check_unity_catalog(),
            "has_pyspark": self._check_pyspark_availability(),
            "detected_at": datetime.now().isoformat()
        }
        
        # Add serverless-specific info
        if info["compute_type"] == "serverless":
            info.update({
                "serverless_features": {
                    "auto_scaling": True,
                    "photon_enabled": True,
                    "unity_catalog_only": True,
                    "spark_connect": True
                }
            })
        
        # Cache the result
        self._set_cache(cache_key, info)
        
        return info
    
    def clear_cache(self):
        """Clear all cached environment information."""
        self._cache.clear()
        self._cache_expiry.clear()
        self.logger.debug("Environment cache cleared")
    
    # Private helper methods
    
    def _check_cache(self, key: str) -> bool:
        """Check if cached value exists and is not expired."""
        if key not in self._cache:
            return False
        
        if key in self._cache_expiry:
            if datetime.now() > self._cache_expiry[key]:
                # Expired
                del self._cache[key]
                del self._cache_expiry[key]
                return False
        
        return True
    
    def _set_cache(self, key: str, value: Any):
        """Set a cached value with expiration."""
        self._cache[key] = value
        self._cache_expiry[key] = datetime.now() + self._cache_ttl
    
    def _check_databricks_env_patterns(self) -> bool:
        """Check for Databricks-specific environment variable patterns."""
        databricks_env_patterns = [
            "DATABRICKS_",
            "DB_",
            "SPARK_LOCAL_IP",
            "SPARK_PUBLIC_DNS"
        ]
        
        for var in os.environ:
            for pattern in databricks_env_patterns:
                if var.startswith(pattern):
                    return True
        
        return False
    
    def _is_serverless_by_env(self) -> bool:
        """Check environment variables for serverless indicators."""
        serverless_env_vars = [
            "DATABRICKS_SERVERLESS_COMPUTE",
            "IS_SERVERLESS_COMPUTE",
            "SERVERLESS_COMPUTE_ENABLED"
        ]
        
        for var in serverless_env_vars:
            if os.environ.get(var, "").lower() in ["true", "1", "yes"]:
                return True
        
        return False
    
    def _is_serverless_by_spark_conf(self) -> bool:
        """Check Spark configuration for serverless indicators."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Check for serverless-specific configurations
            serverless_configs = [
                "spark.databricks.service.serverless.enabled",
                "spark.databricks.photon.enabled",
                "spark.databricks.unityCatalog.enabled"
            ]
            
            for config in serverless_configs:
                try:
                    value = spark.conf.get(config, "false")
                    if value.lower() == "true":
                        return True
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Could not check Spark config: {e}")
        
        return False
    
    def _check_unity_catalog(self) -> bool:
        """Check if Unity Catalog is available."""
        try:
            # Method 1: Check environment variable
            if os.environ.get("DATABRICKS_UNITY_CATALOG_ENABLED", "").lower() == "true":
                return True
            
            # Method 2: Try to access catalog
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Try to list catalogs
            spark.sql("SHOW CATALOGS").collect()
            return True
            
        except Exception:
            return False
    
    def _check_pyspark_availability(self) -> bool:
        """Check if PySpark is available and functional."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            # Try a simple operation
            spark.range(1).collect()
            return True
        except Exception:
            return False
    
    @lru_cache(maxsize=1)
    def _get_cluster_tags(self) -> Dict[str, str]:
        """Get cluster tags if available (cached)."""
        tags = {}
        
        try:
            # Try to read cluster tags from Spark config
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Cluster tags are prefixed with spark.databricks.clusterUsageTags
            for key, value in spark.sparkContext.getConf().getAll():
                if key.startswith("spark.databricks.clusterUsageTags"):
                    tag_name = key.split(".")[-1]
                    tags[tag_name] = value
                    
        except Exception as e:
            self.logger.debug(f"Could not retrieve cluster tags: {e}")
        
        return tags
    
    def __repr__(self) -> str:
        """String representation of the environment."""
        if not self.is_databricks_environment():
            return "DatabricksEnvironment(is_databricks=False)"
        
        info = self.get_environment_info()
        return (
            f"DatabricksEnvironment("
            f"compute_type='{info['compute_type']}', "
            f"runtime='{info['runtime_version']}', "
            f"spark='{info['spark_version']}')"
        )