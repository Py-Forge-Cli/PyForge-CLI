"""
Databricks Classic Compute Detection Module

This module provides detection logic for Databricks classic compute clusters,
including cluster type identification, runtime capabilities, and resource detection.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path


class ClassicDetector:
    """
    Detector for Databricks classic compute clusters.
    
    Identifies classic compute environments and their specific characteristics
    such as cluster type, node configuration, and available features.
    """
    
    def __init__(self):
        """Initialize the classic compute detector."""
        self.logger = logging.getLogger("pyforge.extensions.databricks.classic")
        
        # Classic compute paths
        self.CLASSIC_PATHS = {
            "driver": "/databricks/driver",
            "spark": "/databricks/spark",
            "logs": "/databricks/driver/logs",
            "dbfs": "/dbfs",
            "local_disk": "/local_disk0"
        }
        
        # Cluster type indicators
        self.CLUSTER_TYPE_MARKERS = {
            "standard": ["STANDARD_", "WORKER_ENV_"],
            "high_concurrency": ["HIGH_CONCURRENCY", "SHARED_"],
            "single_node": ["SINGLE_NODE", "DRIVER_ONLY"],
            "job": ["JOB_CLUSTER", "AUTOMATED_"],
            "all_purpose": ["INTERACTIVE", "ALL_PURPOSE"]
        }
        
        # Node type patterns
        self.NODE_PATTERNS = {
            "memory_optimized": ["r5", "r6", "m5", "m6"],
            "compute_optimized": ["c5", "c6"],
            "storage_optimized": ["i3", "d2", "d3"],
            "gpu_enabled": ["p3", "p4", "g4", "g5"],
            "general_purpose": ["m4", "m5d", "m6i"]
        }
    
    def is_classic_compute(self) -> bool:
        """
        Determine if running in classic compute environment.
        
        Returns:
            bool: True if classic compute detected
        """
        # Must be in Databricks but not serverless
        if not self._is_databricks():
            return False
        
        if self._is_serverless():
            return False
        
        # Positive signals for classic compute
        classic_signals = []
        
        # Check for classic paths
        if self._check_classic_paths():
            classic_signals.append("paths")
        
        # Check for driver/executor model
        if self._check_driver_executor_model():
            classic_signals.append("driver_executor")
        
        # Check for DBFS access
        if self._check_dbfs_access():
            classic_signals.append("dbfs")
        
        # Check for init scripts
        if self._check_init_scripts():
            classic_signals.append("init_scripts")
        
        is_classic = len(classic_signals) >= 2
        
        if is_classic:
            self.logger.info(f"Classic compute confirmed with signals: {classic_signals}")
        
        return is_classic
    
    def get_cluster_type(self) -> str:
        """
        Identify the specific type of classic cluster.
        
        Returns:
            str: Cluster type (standard, high_concurrency, single_node, job, all_purpose)
        """
        if not self.is_classic_compute():
            return "unknown"
        
        # Check environment variables for cluster type
        for cluster_type, markers in self.CLUSTER_TYPE_MARKERS.items():
            for marker in markers:
                if any(marker in var for var in os.environ):
                    self.logger.debug(f"Detected {cluster_type} cluster via environment")
                    return cluster_type
        
        # Check Spark configuration
        cluster_type_from_spark = self._get_cluster_type_from_spark()
        if cluster_type_from_spark:
            return cluster_type_from_spark
        
        # Check for single node
        if self._is_single_node():
            return "single_node"
        
        # Default to standard
        return "standard"
    
    def get_node_info(self) -> Dict[str, Any]:
        """
        Get information about cluster nodes.
        
        Returns:
            Dict[str, Any]: Node configuration details
        """
        node_info = {
            "node_type": self._detect_node_type(),
            "node_count": self._get_node_count(),
            "driver_node_type": self._get_driver_node_type(),
            "worker_node_type": self._get_worker_node_type(),
            "has_gpus": self._has_gpu_nodes(),
            "local_storage": self._get_local_storage_info()
        }
        
        # Add instance details if available
        instance_info = self._get_instance_metadata()
        if instance_info:
            node_info["instance_metadata"] = instance_info
        
        return node_info
    
    def get_cluster_features(self) -> Dict[str, bool]:
        """
        Get available features in the classic cluster.
        
        Returns:
            Dict[str, bool]: Feature availability
        """
        features = {
            "dbfs_access": self._check_dbfs_access(),
            "init_scripts": self._check_init_scripts(),
            "cluster_libraries": self._check_cluster_libraries(),
            "spark_ui": self._check_spark_ui_access(),
            "ganglia_metrics": self._check_ganglia_metrics(),
            "custom_tags": self._check_custom_tags(),
            "autoscaling": self._check_autoscaling(),
            "spot_instances": self._check_spot_instances(),
            "table_acls": self._check_table_acls(),
            "credential_passthrough": self._check_credential_passthrough()
        }
        
        return features
    
    def get_cluster_resources(self) -> Dict[str, Any]:
        """
        Get cluster resource information.
        
        Returns:
            Dict[str, Any]: Resource details
        """
        resources = {
            "total_cores": self._get_total_cores(),
            "total_memory": self._get_total_memory(),
            "executors": self._get_executor_count(),
            "spark_version": self._get_spark_version(),
            "scala_version": self._get_scala_version(),
            "python_version": self._get_python_version()
        }
        
        # Add resource utilization if available
        utilization = self._get_resource_utilization()
        if utilization:
            resources["utilization"] = utilization
        
        return resources
    
    # Private helper methods
    
    def _is_databricks(self) -> bool:
        """Check if running in Databricks."""
        return bool(os.environ.get("DATABRICKS_RUNTIME_VERSION"))
    
    def _is_serverless(self) -> bool:
        """Check if running in serverless (to exclude)."""
        runtime = os.environ.get("DATABRICKS_RUNTIME_VERSION", "").lower()
        return "serverless" in runtime
    
    def _check_classic_paths(self) -> bool:
        """Check for classic compute filesystem paths."""
        required_paths = ["driver", "spark"]
        found_paths = []
        
        for name, path in self.CLASSIC_PATHS.items():
            if os.path.exists(path):
                found_paths.append(name)
        
        # Classic compute should have at least driver and spark paths
        return all(req in found_paths for req in required_paths)
    
    def _check_driver_executor_model(self) -> bool:
        """Check for driver/executor execution model."""
        # Check for driver-specific environment
        if os.environ.get("IS_DRIVER") == "TRUE":
            return True
        
        # Check for executor environment variables
        executor_vars = ["SPARK_EXECUTOR_ID", "EXECUTOR_ID", "SPARK_EXECUTOR_CORES"]
        if any(var in os.environ for var in executor_vars):
            return True
        
        # Check Spark configuration
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Check for executor instances
            executor_instances = spark.conf.get("spark.executor.instances", "0")
            if int(executor_instances) > 0:
                return True
        except Exception:
            pass
        
        return False
    
    def _check_dbfs_access(self) -> bool:
        """Check if DBFS is accessible."""
        dbfs_path = "/dbfs"
        try:
            if os.path.exists(dbfs_path):
                # Try to list DBFS root
                os.listdir(dbfs_path)
                return True
        except Exception:
            pass
        
        return False
    
    def _check_init_scripts(self) -> bool:
        """Check if init scripts are supported."""
        init_script_paths = [
            "/databricks/init_scripts",
            "/databricks/scripts/init"
        ]
        
        return any(os.path.exists(path) for path in init_script_paths)
    
    def _get_cluster_type_from_spark(self) -> Optional[str]:
        """Get cluster type from Spark configuration."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Check for high concurrency
            if spark.conf.get("spark.databricks.cluster.profile", "") == "serverless":
                return "high_concurrency"
            
            # Check for job cluster
            if spark.conf.get("spark.databricks.job.id", ""):
                return "job"
            
        except Exception:
            pass
        
        return None
    
    def _is_single_node(self) -> bool:
        """Check if running on single node cluster."""
        try:
            # Check environment variable
            if os.environ.get("SINGLE_NODE") == "TRUE":
                return True
            
            # Check Spark configuration
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Single node has 0 executors
            executors = spark.conf.get("spark.executor.instances", "1")
            return int(executors) == 0
            
        except Exception:
            return False
    
    def _detect_node_type(self) -> str:
        """Detect the node type category."""
        instance_type = os.environ.get("DB_INSTANCE_TYPE", "").lower()
        
        if not instance_type:
            return "unknown"
        
        for category, patterns in self.NODE_PATTERNS.items():
            if any(pattern in instance_type for pattern in patterns):
                return category
        
        return "general_purpose"
    
    def _get_node_count(self) -> int:
        """Get total number of nodes in cluster."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Get executor count
            executors = int(spark.conf.get("spark.executor.instances", "0"))
            
            # Add 1 for driver
            return executors + 1
            
        except Exception:
            return 1  # At least driver node
    
    def _get_driver_node_type(self) -> Optional[str]:
        """Get driver node instance type."""
        return os.environ.get("DB_DRIVER_INSTANCE_TYPE") or os.environ.get("DB_INSTANCE_TYPE")
    
    def _get_worker_node_type(self) -> Optional[str]:
        """Get worker node instance type."""
        return os.environ.get("DB_WORKER_INSTANCE_TYPE") or os.environ.get("DB_INSTANCE_TYPE")
    
    def _has_gpu_nodes(self) -> bool:
        """Check if cluster has GPU nodes."""
        instance_type = (self._get_driver_node_type() or "").lower()
        
        # Check for GPU instance types
        gpu_patterns = ["p2", "p3", "p4", "g3", "g4", "g5"]
        if any(pattern in instance_type for pattern in gpu_patterns):
            return True
        
        # Check CUDA availability
        return os.path.exists("/usr/local/cuda")
    
    def _get_local_storage_info(self) -> Dict[str, Any]:
        """Get local storage information."""
        storage_info = {}
        
        try:
            import shutil
            
            # Check local disk
            if os.path.exists("/local_disk0"):
                usage = shutil.disk_usage("/local_disk0")
                storage_info["local_disk"] = {
                    "total_gb": round(usage.total / (1024**3), 2),
                    "available_gb": round(usage.free / (1024**3), 2)
                }
            
            # Check for NVMe
            if any(os.path.exists(f"/dev/nvme{i}n1") for i in range(4)):
                storage_info["has_nvme"] = True
                
        except Exception:
            pass
        
        return storage_info
    
    def _get_instance_metadata(self) -> Optional[Dict[str, Any]]:
        """Get cloud instance metadata if available."""
        metadata = {}
        
        # AWS instance metadata
        aws_metadata_url = "http://169.254.169.254/latest/meta-data/"
        try:
            import urllib.request
            response = urllib.request.urlopen(aws_metadata_url + "instance-type", timeout=1)
            metadata["aws_instance_type"] = response.read().decode()
            metadata["cloud_provider"] = "aws"
        except Exception:
            pass
        
        # Azure instance metadata
        azure_metadata_url = "http://169.254.169.254/metadata/instance"
        try:
            import urllib.request
            req = urllib.request.Request(
                azure_metadata_url,
                headers={"Metadata": "true"}
            )
            response = urllib.request.urlopen(req, timeout=1)
            azure_data = json.loads(response.read().decode())
            metadata["azure_vm_size"] = azure_data.get("compute", {}).get("vmSize")
            metadata["cloud_provider"] = "azure"
        except Exception:
            pass
        
        return metadata if metadata else None
    
    def _check_cluster_libraries(self) -> bool:
        """Check if cluster libraries are supported."""
        lib_paths = [
            "/databricks/python/lib",
            "/databricks/jars",
            "/databricks/R/lib"
        ]
        return any(os.path.exists(path) for path in lib_paths)
    
    def _check_spark_ui_access(self) -> bool:
        """Check if Spark UI is accessible."""
        return os.environ.get("SPARK_UI_ENABLED", "true").lower() == "true"
    
    def _check_ganglia_metrics(self) -> bool:
        """Check if Ganglia metrics are available."""
        return os.path.exists("/databricks/spark/scripts/ganglia")
    
    def _check_custom_tags(self) -> bool:
        """Check if custom cluster tags are available."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Look for custom tags in Spark conf
            for key, _ in spark.sparkContext.getConf().getAll():
                if key.startswith("spark.databricks.clusterUsageTags"):
                    return True
        except Exception:
            pass
        
        return False
    
    def _check_autoscaling(self) -> bool:
        """Check if autoscaling is enabled."""
        return os.environ.get("ENABLE_AUTOSCALING", "false").lower() == "true"
    
    def _check_spot_instances(self) -> bool:
        """Check if using spot/preemptible instances."""
        spot_vars = ["DB_IS_SPOT_CLUSTER", "USE_SPOT_INSTANCES"]
        return any(os.environ.get(var, "false").lower() == "true" for var in spot_vars)
    
    def _check_table_acls(self) -> bool:
        """Check if table ACLs are enabled."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            return spark.conf.get("spark.databricks.acl.enabled", "false").lower() == "true"
        except Exception:
            return False
    
    def _check_credential_passthrough(self) -> bool:
        """Check if credential passthrough is enabled."""
        return os.environ.get("CREDENTIAL_PASSTHROUGH_ENABLED", "false").lower() == "true"
    
    def _get_total_cores(self) -> int:
        """Get total CPU cores in cluster."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            executor_cores = int(spark.conf.get("spark.executor.cores", "4"))
            executor_instances = int(spark.conf.get("spark.executor.instances", "0"))
            driver_cores = int(spark.conf.get("spark.driver.cores", "4"))
            
            return driver_cores + (executor_cores * executor_instances)
            
        except Exception:
            return os.cpu_count() or 4
    
    def _get_total_memory(self) -> str:
        """Get total memory in cluster."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            executor_memory = spark.conf.get("spark.executor.memory", "4g")
            executor_instances = int(spark.conf.get("spark.executor.instances", "0"))
            driver_memory = spark.conf.get("spark.driver.memory", "4g")
            
            # Simple concatenation for display
            if executor_instances > 0:
                return f"Driver: {driver_memory}, Executors: {executor_instances}x{executor_memory}"
            else:
                return f"Driver: {driver_memory}"
                
        except Exception:
            return "Unknown"
    
    def _get_executor_count(self) -> int:
        """Get number of executors."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            return int(spark.conf.get("spark.executor.instances", "0"))
        except Exception:
            return 0
    
    def _get_spark_version(self) -> Optional[str]:
        """Get Spark version."""
        return os.environ.get("SPARK_VERSION")
    
    def _get_scala_version(self) -> Optional[str]:
        """Get Scala version."""
        runtime = os.environ.get("DATABRICKS_RUNTIME_VERSION", "")
        if "scala2.12" in runtime:
            return "2.12"
        elif "scala2.11" in runtime:
            return "2.11"
        return None
    
    def _get_python_version(self) -> str:
        """Get Python version."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_resource_utilization(self) -> Optional[Dict[str, float]]:
        """Get current resource utilization."""
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent
            }
        except Exception:
            return None
    
    def get_detection_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive detection report.
        
        Returns:
            Dict[str, Any]: Complete cluster information
        """
        if not self.is_classic_compute():
            return {"is_classic": False}
        
        return {
            "is_classic": True,
            "cluster_type": self.get_cluster_type(),
            "node_info": self.get_node_info(),
            "features": self.get_cluster_features(),
            "resources": self.get_cluster_resources(),
            "runtime_version": os.environ.get("DATABRICKS_RUNTIME_VERSION"),
            "cluster_id": os.environ.get("DB_CLUSTER_ID")
        }