"""
Tests for the Databricks environment detection module.
"""

from unittest.mock import MagicMock, patch

import pytest

from pyforge_cli.databricks.environment import (
    DatabricksEnvironment,
    detect_databricks_environment,
    is_running_in_databricks,
    is_running_in_serverless,
)

# Mark all tests in this module as databricks tests
pytestmark = pytest.mark.databricks


class TestDatabricksEnvironment:
    """Tests for the DatabricksEnvironment class."""

    def test_init_non_databricks(self):
        """Test initialization with non-Databricks environment."""
        env = DatabricksEnvironment({}, is_databricks=False)
        assert not env.is_databricks
        assert not env.is_serverless()
        assert env.version is None
        assert env.cluster_id is None
        assert env.workspace_id is None

    def test_init_databricks(self):
        """Test initialization with Databricks environment."""
        env_vars = {
            "DATABRICKS_RUNTIME_VERSION": "10.4",
            "DATABRICKS_CLUSTER_ID": "cluster-123",
            "DATABRICKS_WORKSPACE_ID": "workspace-456",
            "DATABRICKS_RUNTIME_EDITION": "serverless",
        }

        env = DatabricksEnvironment(env_vars, is_databricks=True, version="10.4")
        assert env.is_databricks
        assert env.is_serverless()
        assert env.version == "10.4"
        assert env.cluster_id == "cluster-123"
        assert env.workspace_id == "workspace-456"

    def test_init_databricks_non_serverless(self):
        """Test initialization with non-serverless Databricks environment."""
        env_vars = {
            "DATABRICKS_RUNTIME_VERSION": "10.4",
            "DATABRICKS_CLUSTER_ID": "cluster-123",
            "DATABRICKS_WORKSPACE_ID": "workspace-456",
            "DATABRICKS_RUNTIME_EDITION": "standard",
        }

        env = DatabricksEnvironment(env_vars, is_databricks=True, version="10.4")
        assert env.is_databricks
        assert not env.is_serverless()
        assert env.version == "10.4"
        assert env.cluster_id == "cluster-123"
        assert env.workspace_id == "workspace-456"

    def test_get_environment_info(self):
        """Test get_environment_info method."""
        env_vars = {
            "DATABRICKS_RUNTIME_VERSION": "10.4",
            "DATABRICKS_CLUSTER_ID": "cluster-123",
            "DATABRICKS_WORKSPACE_ID": "workspace-456",
            "DATABRICKS_RUNTIME_EDITION": "serverless",
            "UNRELATED_VAR": "should-not-be-included",
            "ANOTHER_DATABRICKS_VAR": "should-be-included",
        }

        env = DatabricksEnvironment(env_vars, is_databricks=True, version="10.4")
        info = env.get_environment_info()

        assert info["is_databricks"] is True
        assert info["is_serverless"] is True
        assert info["version"] == "10.4"
        assert info["cluster_id"] == "cluster-123"
        assert info["workspace_id"] == "workspace-456"
        assert "python_version" in info
        assert "env_vars" in info
        assert "DATABRICKS_RUNTIME_VERSION" in info["env_vars"]
        assert "ANOTHER_DATABRICKS_VAR" in info["env_vars"]
        assert "UNRELATED_VAR" not in info["env_vars"]


class TestDatabricksDetection:
    """Tests for Databricks detection functions."""

    @patch("os.environ", {})
    def test_detect_non_databricks(self):
        """Test detection in non-Databricks environment."""
        env = detect_databricks_environment()
        assert not env.is_databricks
        assert not env.is_serverless()

    @patch(
        "os.environ",
        {
            "DATABRICKS_RUNTIME_VERSION": "10.4",
            "DATABRICKS_CLUSTER_ID": "cluster-123",
            "DATABRICKS_WORKSPACE_ID": "workspace-456",
            "DATABRICKS_RUNTIME_EDITION": "serverless",
        },
    )
    def test_detect_databricks_serverless(self):
        """Test detection in Databricks serverless environment."""
        env = detect_databricks_environment()
        assert env.is_databricks
        assert env.is_serverless()
        assert env.version == "10.4"

    @patch(
        "os.environ",
        {
            "DATABRICKS_RUNTIME_VERSION": "10.4",
            "DATABRICKS_CLUSTER_ID": "cluster-123",
            "DATABRICKS_WORKSPACE_ID": "workspace-456",
            "DATABRICKS_RUNTIME_EDITION": "standard",
        },
    )
    def test_detect_databricks_standard(self):
        """Test detection in standard Databricks environment."""
        env = detect_databricks_environment()
        assert env.is_databricks
        assert not env.is_serverless()
        assert env.version == "10.4"

    @patch("os.environ", {"SPARK_HOME": "/opt/spark"})
    def test_detect_databricks_from_spark(self):
        """Test detection from Spark version."""
        # Mock the pyspark module
        mock_pyspark = MagicMock()
        mock_pyspark.version = "Databricks Runtime 10.4"

        with patch.dict("sys.modules", {"pyspark": mock_pyspark}):
            env = detect_databricks_environment()
            assert env.is_databricks

    @patch(
        "os.environ",
        {
            "DATABRICKS_RUNTIME_VERSION": "10.4",
            "DATABRICKS_RUNTIME_EDITION": "serverless",
        },
    )
    def test_is_running_in_databricks(self):
        """Test is_running_in_databricks function."""
        assert is_running_in_databricks() is True

    @patch(
        "os.environ",
        {
            "DATABRICKS_RUNTIME_VERSION": "10.4",
            "DATABRICKS_RUNTIME_EDITION": "serverless",
        },
    )
    def test_is_running_in_serverless(self):
        """Test is_running_in_serverless function."""
        assert is_running_in_serverless() is True

    @patch(
        "os.environ",
        {
            "DATABRICKS_RUNTIME_VERSION": "10.4",
            "DATABRICKS_RUNTIME_EDITION": "standard",
        },
    )
    def test_is_running_in_serverless_false(self):
        """Test is_running_in_serverless function with non-serverless environment."""
        assert is_running_in_serverless() is False
