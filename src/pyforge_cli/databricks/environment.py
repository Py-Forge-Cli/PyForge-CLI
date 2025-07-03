"""
Databricks environment detection module.
Provides utilities to detect and interact with Databricks environments.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class DatabricksEnvironment:
    """
    Class representing a Databricks environment.
    Provides information about the Databricks environment and its capabilities.
    """
    
    def __init__(self, env_vars: Dict[str, str], is_databricks: bool = False, version: str = None):
        """
        Initialize Databricks environment.
        
        Args:
            env_vars: Environment variables
            is_databricks: Whether running in Databricks
            version: Databricks runtime version
        """
        self.env_vars = env_vars
        self._is_databricks = is_databricks
        self._version = version
        self._is_serverless = None
        self._cluster_id = None
        self._workspace_id = None
        
        # Parse environment variables
        if is_databricks:
            self._parse_environment()
    
    def _parse_environment(self) -> None:
        """Parse Databricks environment variables."""
        # Get cluster ID
        self._cluster_id = self.env_vars.get('DATABRICKS_CLUSTER_ID')
        
        # Get workspace ID
        self._workspace_id = self.env_vars.get('DATABRICKS_WORKSPACE_ID')
        
        # Enhanced serverless detection based on actual V1 environment variables
        self._is_serverless = False
        
        # Method 1: Direct IS_SERVERLESS flag (most reliable for V1)
        if self.env_vars.get('IS_SERVERLESS', '').upper() == 'TRUE':
            self._is_serverless = True
            logger.debug("Serverless detected via IS_SERVERLESS=TRUE")
        
        # Method 2: Spark Connect mode (V1/V2 indicator)
        elif self.env_vars.get('SPARK_CONNECT_MODE_ENABLED') == '1':
            self._is_serverless = True
            logger.debug("Serverless detected via SPARK_CONNECT_MODE_ENABLED=1")
        
        # Method 3: Instance type pattern
        elif 'serverless' in self.env_vars.get('DB_INSTANCE_TYPE', '').lower():
            self._is_serverless = True
            logger.debug("Serverless detected via DB_INSTANCE_TYPE containing 'serverless'")
        
        # Method 4: POD_NAME pattern for Kubernetes serverless
        elif 'serverless' in self.env_vars.get('POD_NAME', '').lower():
            self._is_serverless = True
            logger.debug("Serverless detected via POD_NAME containing 'serverless'")
        
        # Method 5: Client runtime version pattern
        elif 'client.' in self.env_vars.get('DATABRICKS_RUNTIME_VERSION', ''):
            self._is_serverless = True
            logger.debug("Serverless detected via client runtime version")
        
        # Method 6: Legacy DATABRICKS_RUNTIME_EDITION check (for backwards compatibility)
        elif 'serverless' in self.env_vars.get('DATABRICKS_RUNTIME_EDITION', '').lower():
            self._is_serverless = True
            logger.debug("Serverless detected via DATABRICKS_RUNTIME_EDITION")
        
        # Log environment details with detection method
        logger.debug(f"Databricks environment detected: version={self._version}, serverless={self._is_serverless}")
    
    @property
    def is_databricks(self) -> bool:
        """Check if running in Databricks environment."""
        return self._is_databricks
    
    @property
    def version(self) -> Optional[str]:
        """Get Databricks runtime version."""
        return self._version
    
    def is_serverless(self) -> bool:
        """Check if running in Databricks serverless environment."""
        return self._is_databricks and self._is_serverless
    
    @property
    def cluster_id(self) -> Optional[str]:
        """Get Databricks cluster ID."""
        return self._cluster_id
    
    @property
    def workspace_id(self) -> Optional[str]:
        """Get Databricks workspace ID."""
        return self._workspace_id
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information."""
        return {
            'is_databricks': self._is_databricks,
            'version': self._version,
            'is_serverless': self._is_serverless,
            'cluster_id': self._cluster_id,
            'workspace_id': self._workspace_id,
            'python_version': sys.version,
            'env_vars': {k: v for k, v in self.env_vars.items() if 'DATABRICKS' in k}
        }


def detect_databricks_environment() -> DatabricksEnvironment:
    """
    Detect if running in Databricks environment.
    
    Returns:
        DatabricksEnvironment object with environment information
    """
    env_vars = dict(os.environ)
    
    # Enhanced Databricks detection with multiple checks
    is_databricks = False
    detection_reasons = []
    
    # Check 1: Direct serverless flag (strongest indicator for V1)
    if env_vars.get('IS_SERVERLESS', '').upper() == 'TRUE':
        is_databricks = True
        detection_reasons.append("IS_SERVERLESS=TRUE found")
    
    # Check 2: Databricks-specific environment variables
    elif any(k.startswith('DATABRICKS_') for k in env_vars):
        is_databricks = True
        detection_reasons.append("DATABRICKS_* environment variables found")
    
    # Check 3: Databricks-specific variables found in actual V1 environment
    databricks_specific_vars = [
        'DB_IS_DRIVER',           # Found in V1
        'DB_HOME',                # Found in V1
        'DB_INSTANCE_TYPE',       # Found in V1
        'DATABRICKS_RUNTIME_VERSION',  # Found in V1
        'SPARK_CONNECT_MODE_ENABLED',  # Serverless V1/V2 indicator
        'DATABRICKS_ROOT_VIRTUALENV_ENV'  # Found in V1
    ]
    if any(env_vars.get(var) for var in databricks_specific_vars):
        is_databricks = True
        detection_reasons.append("Databricks-specific variables found")
    
    # Check 4: Spark version check
    try:
        if not is_databricks and 'SPARK_HOME' in env_vars:
            import pyspark
            spark_version = getattr(pyspark, 'version', None)
            if spark_version and 'databricks' in spark_version.lower():
                is_databricks = True
                detection_reasons.append(f"Databricks Spark version detected: {spark_version}")
    except ImportError:
        pass
    
    # Check 5: Try to detect from active Spark session
    try:
        if not is_databricks:
            import pyspark
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                spark_version = spark.version
                if 'databricks' in spark_version.lower():
                    is_databricks = True
                    detection_reasons.append(f"Active Spark session with Databricks version: {spark_version}")
    except (ImportError, AttributeError, Exception):
        pass
    
    # Get Databricks version
    version = None
    if is_databricks:
        version = env_vars.get('DATABRICKS_RUNTIME_VERSION')
        
        # Try to get version from Spark if not in env vars
        if not version:
            try:
                import pyspark
                from pyspark.sql import SparkSession
                spark = SparkSession.getActiveSession()
                if spark:
                    version = spark.version
                else:
                    # Try to create a session to get version
                    sc = pyspark.SparkContext.getOrCreate()
                    version = sc.version
            except (ImportError, AttributeError, Exception):
                pass
    
    # Log detection results for debugging
    if is_databricks:
        logger.debug(f"Databricks environment detected. Reasons: {detection_reasons}")
    else:
        logger.debug("No Databricks environment detected")
    
    return DatabricksEnvironment(env_vars, is_databricks, version)


def is_running_in_databricks() -> bool:
    """
    Simple check if running in Databricks environment.
    
    Returns:
        True if running in Databricks
    """
    return detect_databricks_environment().is_databricks


def is_running_in_serverless() -> bool:
    """
    Check if running in Databricks serverless environment.
    
    Returns:
        True if running in Databricks serverless
    """
    return detect_databricks_environment().is_serverless()
