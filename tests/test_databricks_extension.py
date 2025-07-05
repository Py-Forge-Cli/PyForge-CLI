"""
Comprehensive Test Suite for Databricks Extension

This module tests all components of the PyForge CLI Databricks extension.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import components to test
from pyforge_cli.extensions.databricks import DatabricksExtension, PyForgeDatabricks
from pyforge_cli.extensions.databricks.cache_manager import (
    CacheManager,
)
from pyforge_cli.extensions.databricks.classic_detector import ClassicDetector
from pyforge_cli.extensions.databricks.converter_selector import (
    ConverterRecommendation,
    ConverterSelector,
    ConverterType,
)
from pyforge_cli.extensions.databricks.environment import DatabricksEnvironment
from pyforge_cli.extensions.databricks.fallback_manager import (
    FallbackManager,
    FallbackReason,
)
from pyforge_cli.extensions.databricks.runtime_version import RuntimeVersionDetector
from pyforge_cli.extensions.databricks.serverless_detector import ServerlessDetector
from pyforge_cli.extensions.databricks.volume_operations import (
    VolumeOperations,
)

# Mark all tests in this module as databricks tests
pytestmark = pytest.mark.databricks


class TestDatabricksEnvironment:
    """Test DatabricksEnvironment class."""

    def test_is_databricks_environment_true(self):
        """Test Databricks environment detection when in Databricks."""
        with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x-scala2.12"}):
            env = DatabricksEnvironment()
            assert env.is_databricks_environment() is True

    def test_is_databricks_environment_false(self):
        """Test Databricks environment detection when not in Databricks."""
        with patch.dict(os.environ, {}, clear=True):
            env = DatabricksEnvironment()
            assert env.is_databricks_environment() is False

    def test_get_compute_type_serverless(self):
        """Test serverless compute detection."""
        with patch.dict(
            os.environ,
            {
                "DATABRICKS_RUNTIME_VERSION": "13.3.x-serverless-scala2.12",
                "DATABRICKS_SERVERLESS_COMPUTE": "true",
            },
        ):
            env = DatabricksEnvironment()
            assert env.get_compute_type() == "serverless"

    def test_get_compute_type_classic(self):
        """Test classic compute detection."""
        with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x-scala2.12"}):
            env = DatabricksEnvironment()
            assert env.get_compute_type() == "classic"

    def test_parse_runtime_version(self):
        """Test runtime version parsing."""
        env = DatabricksEnvironment()

        with patch.object(env, "get_runtime_version", return_value="13.3.x-scala2.12"):
            major, minor, is_lts = env.parse_runtime_version()
            assert major == 13
            assert minor == 3
            assert is_lts is True

    def test_get_environment_info(self):
        """Test comprehensive environment info."""
        with patch.dict(
            os.environ,
            {
                "DATABRICKS_RUNTIME_VERSION": "13.3.x-scala2.12",
                "SPARK_VERSION": "3.4.1",
            },
        ):
            env = DatabricksEnvironment()
            info = env.get_environment_info()

            assert info["is_databricks"] is True
            assert info["runtime_version"] == "13.3.x-scala2.12"
            assert info["spark_version"] == "3.4.1"
            assert "python_version" in info

    def test_cache_functionality(self):
        """Test environment caching."""
        env = DatabricksEnvironment()

        # First call should cache
        with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x-scala2.12"}):
            result1 = env.is_databricks_environment()

        # Second call should use cache even with different env
        with patch.dict(os.environ, {}, clear=True):
            result2 = env.is_databricks_environment()

        assert result1 == result2  # Cache should preserve first result

        # Clear cache and check again
        env.clear_cache()
        with patch.dict(os.environ, {}, clear=True):
            result3 = env.is_databricks_environment()

        assert result3 is False  # Should re-evaluate after cache clear


class TestServerlessDetector:
    """Test ServerlessDetector class."""

    def test_is_serverless_with_multiple_signals(self):
        """Test serverless detection with multiple positive signals."""
        with patch.dict(
            os.environ,
            {
                "DATABRICKS_RUNTIME_VERSION": "13.3.x-serverless-scala2.12",
                "DATABRICKS_SERVERLESS_COMPUTE": "true",
            },
        ):
            detector = ServerlessDetector()
            assert detector.is_serverless() is True

    def test_is_serverless_insufficient_signals(self):
        """Test serverless detection with insufficient signals."""
        with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x-scala2.12"}):
            detector = ServerlessDetector()
            assert detector.is_serverless() is False

    def test_get_serverless_features(self):
        """Test serverless feature detection."""
        detector = ServerlessDetector()

        with patch.object(detector, "is_serverless", return_value=True):
            with patch.object(detector, "_check_photon_enabled", return_value=True):
                features = detector.get_serverless_features()

                assert features["photon_acceleration"] is True
                assert features["auto_scaling"] is True
                assert features["instant_compute"] is True

    def test_get_serverless_limitations(self):
        """Test serverless limitations."""
        detector = ServerlessDetector()

        with patch.object(detector, "is_serverless", return_value=True):
            limitations = detector.get_serverless_limitations()

            assert len(limitations) > 0
            assert any("DBFS" in limit for limit in limitations)

    def test_detection_report(self):
        """Test comprehensive detection report."""
        with patch.dict(
            os.environ,
            {
                "DATABRICKS_RUNTIME_VERSION": "13.3.x-serverless-scala2.12",
                "DATABRICKS_SERVERLESS_COMPUTE": "true",
            },
        ):
            detector = ServerlessDetector()
            report = detector.get_detection_report()

            assert "is_serverless" in report
            assert "detection_methods" in report
            assert "features" in report
            assert "limitations" in report


class TestClassicDetector:
    """Test ClassicDetector class."""

    def test_is_classic_compute(self):
        """Test classic compute detection."""
        with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x-scala2.12"}):
            with patch("os.path.exists", return_value=True):
                detector = ClassicDetector()
                assert detector.is_classic_compute() is True

    def test_get_cluster_type(self):
        """Test cluster type detection."""
        detector = ClassicDetector()

        with patch.object(detector, "is_classic_compute", return_value=True):
            with patch.dict(os.environ, {"STANDARD_CLUSTER": "true"}):
                cluster_type = detector.get_cluster_type()
                assert cluster_type in [
                    "standard",
                    "high_concurrency",
                    "single_node",
                    "job",
                    "all_purpose",
                ]

    def test_get_node_info(self):
        """Test node information retrieval."""
        detector = ClassicDetector()

        with patch.dict(
            os.environ,
            {"DB_INSTANCE_TYPE": "i3.xlarge", "DB_DRIVER_INSTANCE_TYPE": "i3.xlarge"},
        ):
            node_info = detector.get_node_info()

            assert "node_type" in node_info
            assert "driver_node_type" in node_info
            assert node_info["driver_node_type"] == "i3.xlarge"

    def test_get_cluster_features(self):
        """Test cluster feature detection."""
        detector = ClassicDetector()

        with patch("os.path.exists", return_value=True):
            features = detector.get_cluster_features()

            assert isinstance(features, dict)
            assert "dbfs_access" in features
            assert "init_scripts" in features


class TestRuntimeVersionDetector:
    """Test RuntimeVersionDetector class."""

    def test_parse_version_standard(self):
        """Test parsing standard runtime version."""
        detector = RuntimeVersionDetector()

        info = detector.parse_version("13.3.x-scala2.12")
        assert info["major"] == 13
        assert info["minor"] == 3
        assert info["is_lts"] is True
        assert info["scala_version"] == "2.12"

    def test_parse_version_serverless(self):
        """Test parsing serverless runtime version."""
        detector = RuntimeVersionDetector()

        info = detector.parse_version("13.3.x-serverless-scala2.12")
        assert info["is_serverless"] is True
        assert info["variant"] == "serverless"

    def test_parse_version_ml(self):
        """Test parsing ML runtime version."""
        detector = RuntimeVersionDetector()

        info = detector.parse_version("13.3.x-ml-scala2.12")
        assert info["is_ml"] is True
        assert info["variant"] == "ml"

    def test_compare_versions(self):
        """Test version comparison."""
        detector = RuntimeVersionDetector()

        assert detector.compare_versions("13.3.x", "12.2.x") == 1
        assert detector.compare_versions("12.2.x", "13.3.x") == -1
        assert detector.compare_versions("13.3.x", "13.3.x") == 0

    def test_get_feature_availability(self):
        """Test feature availability detection."""
        detector = RuntimeVersionDetector()

        features = detector.get_feature_availability("13.3.x-scala2.12")
        assert features["unity_catalog"] is True
        assert features["serverless_compute"] is True
        assert features["photon"] is True

    def test_check_compatibility(self):
        """Test version compatibility check."""
        detector = RuntimeVersionDetector()

        with patch.object(
            detector, "get_runtime_version", return_value="13.3.x-scala2.12"
        ):
            assert detector.check_compatibility("12.0") is True
            assert detector.check_compatibility("14.0") is False


class TestCacheManager:
    """Test CacheManager class."""

    def test_cache_set_and_get(self):
        """Test basic cache operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=Path(tmpdir))

            # Set value
            cache.set("test_key", {"data": "value"}, ttl=60)

            # Get value
            result = cache.get("test_key")
            assert result == {"data": "value"}

    def test_cache_expiration(self):
        """Test cache TTL expiration."""
        cache = CacheManager(default_ttl=0)  # Immediate expiration

        cache.set("test_key", "value")

        # Value should be expired immediately
        import time

        time.sleep(0.1)

        result = cache.get("test_key")
        assert result is None

    def test_cache_with_generator(self):
        """Test cache with value generator."""
        cache = CacheManager()

        def generator():
            return {"generated": "value"}

        result = cache.get("new_key", generator=generator)
        assert result == {"generated": "value"}

        # Second call should use cache
        result2 = cache.get("new_key")
        assert result2 == {"generated": "value"}

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        cache = CacheManager()

        cache.set("test_key", "value")
        assert cache.get("test_key") == "value"

        cache.invalidate("test_key")
        assert cache.get("test_key") is None

    def test_cache_statistics(self):
        """Test cache statistics."""
        cache = CacheManager()

        # Generate some hits and misses
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_statistics()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["memory_entries"] == 1


class TestVolumeOperations:
    """Test VolumeOperations class."""

    def test_parse_volume_path_valid(self):
        """Test parsing valid Volume paths."""
        ops = VolumeOperations()

        info = ops.parse_volume_path("/Volumes/main/default/my_volume/data.csv")
        assert info is not None
        assert info.catalog == "main"
        assert info.schema == "default"
        assert info.volume == "my_volume"
        assert info.path == "data.csv"

    def test_parse_volume_path_invalid(self):
        """Test parsing invalid Volume paths."""
        ops = VolumeOperations()

        info = ops.parse_volume_path("/not/a/volume/path")
        assert info is None

    def test_parse_volume_path_variations(self):
        """Test parsing Volume path variations."""
        ops = VolumeOperations()

        # Without leading slash
        info = ops.parse_volume_path("Volumes/main/default/vol")
        assert info is not None

        # Lowercase
        info = ops.parse_volume_path("volumes/main/default/vol")
        assert info is not None

    @patch("pyspark.sql.SparkSession")
    def test_validate_volume_access(self, mock_spark):
        """Test Volume access validation."""
        ops = VolumeOperations()

        # Mock Spark catalog operations
        mock_session = MagicMock()
        mock_spark.builder.getOrCreate.return_value = mock_session
        mock_session.sql.return_value.collect.return_value = [
            Mock(catalog="main"),
            Mock(schema="default"),
            Mock(volume_name="my_volume"),
        ]

        valid, error = ops.validate_volume_access("/Volumes/main/default/my_volume")
        # Would need more mocking for full test


class TestConverterSelector:
    """Test ConverterSelector class."""

    def test_select_converter_small_file(self):
        """Test converter selection for small files."""
        selector = ConverterSelector()

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(b"test,data\n1,2\n")
            tmp.flush()

            try:
                recommendation = selector.select_converter(
                    Path(tmp.name), "parquet", {}
                )

                assert isinstance(recommendation, ConverterRecommendation)
                assert recommendation.converter_type in [
                    ConverterType.PANDAS,
                    ConverterType.NATIVE,
                ]
                assert recommendation.confidence > 0

            finally:
                os.unlink(tmp.name)

    def test_select_converter_large_file(self):
        """Test converter selection for large files."""
        selector = ConverterSelector()

        # Mock large file
        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = Mock(st_size=2 * 1024**3)  # 2GB

            with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x"}):
                recommendation = selector.select_converter(
                    Path("large_file.csv"), "parquet", {}
                )

                assert recommendation.converter_type == ConverterType.SPARK
                assert "Large file" in " ".join(recommendation.reasons)

    def test_file_characteristics_analysis(self):
        """Test file characteristics analysis."""
        selector = ConverterSelector()

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(b"col1,col2,col3\n1,2,3\n4,5,6\n")
            tmp.flush()

            try:
                chars = selector._analyze_file(Path(tmp.name))

                assert chars.format == "csv"
                assert chars.size_bytes > 0

            finally:
                os.unlink(tmp.name)


class TestFallbackManager:
    """Test FallbackManager class."""

    def test_register_converter(self):
        """Test converter registration."""
        manager = FallbackManager()

        def mock_converter(input_path, output_path, options):
            return True

        manager.register_converter(ConverterType.SPARK, mock_converter)
        assert ConverterType.SPARK in manager._converter_registry

    def test_execute_with_fallback_success(self):
        """Test successful conversion without fallback."""
        manager = FallbackManager()

        # Register successful converter
        manager.register_converter(ConverterType.SPARK, lambda i, o, opts: True)

        recommendation = ConverterRecommendation(
            converter_type=ConverterType.SPARK,
            confidence=0.9,
            reasons=["Test"],
            estimated_performance="fast",
            memory_requirement="low",
            fallback_options=[],
        )

        with patch.object(manager, "_is_converter_available", return_value=True):
            with patch.object(manager, "_initialize_converter", return_value=True):
                result = manager.execute_with_fallback(
                    Path("input.csv"), Path("output.parquet"), recommendation, {}
                )

        assert result.success is True
        assert result.final_converter == ConverterType.SPARK
        assert len(result.attempts) == 0

    def test_execute_with_fallback_failure_and_recovery(self):
        """Test fallback to alternative converter."""
        manager = FallbackManager()

        # Register failing and successful converters
        call_count = {"spark": 0, "pandas": 0}

        def failing_converter(i, o, opts):
            call_count["spark"] += 1
            raise Exception("Spark failed")

        def successful_converter(i, o, opts):
            call_count["pandas"] += 1
            return True

        manager.register_converter(ConverterType.SPARK, failing_converter)
        manager.register_converter(ConverterType.PANDAS, successful_converter)

        recommendation = ConverterRecommendation(
            converter_type=ConverterType.SPARK,
            confidence=0.9,
            reasons=["Test"],
            estimated_performance="fast",
            memory_requirement="low",
            fallback_options=[ConverterType.PANDAS],
        )

        with patch.object(manager, "_is_converter_available", return_value=True):
            with patch.object(manager, "_initialize_converter", return_value=True):
                result = manager.execute_with_fallback(
                    Path("input.csv"), Path("output.parquet"), recommendation, {}
                )

        assert result.success is True
        assert result.final_converter == ConverterType.PANDAS
        assert len(result.attempts) == 1
        assert result.attempts[0].converter_type == ConverterType.SPARK
        assert result.attempts[0].reason == FallbackReason.CONVERSION_ERROR


class TestPyForgeDatabricks:
    """Test PyForgeDatabricks API class."""

    @patch("pyspark.sql.SparkSession")
    def test_initialization(self, mock_spark):
        """Test PyForgeDatabricks initialization."""
        forge = PyForgeDatabricks(auto_init=False)

        assert forge is not None
        assert forge.environment is not None
        assert forge.converter_selector is not None

    @patch("pyspark.sql.SparkSession")
    def test_convert_basic(self, mock_spark):
        """Test basic conversion."""
        forge = PyForgeDatabricks(auto_init=False)

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(b"col1,col2\n1,2\n3,4\n")
            tmp.flush()

            try:
                # Mock converter execution
                with patch.object(
                    forge.fallback_manager, "execute_with_fallback"
                ) as mock_exec:
                    mock_exec.return_value = Mock(
                        success=True,
                        final_converter=ConverterType.PANDAS,
                        attempts=[],
                        warnings=[],
                        output_path=Path("output.parquet"),
                    )

                    result = forge.convert(tmp.name)

                    assert result["success"] is True
                    assert "output_path" in result
                    assert "duration_seconds" in result

            finally:
                os.unlink(tmp.name)

    def test_get_info(self):
        """Test file info retrieval."""
        forge = PyForgeDatabricks(auto_init=False)

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(b"test data\n")
            tmp.flush()

            try:
                info = forge.get_info(tmp.name)

                assert info["exists"] is True
                assert info["format"] == "csv"
                assert info["size"] > 0

            finally:
                os.unlink(tmp.name)

    def test_validate(self):
        """Test file validation."""
        forge = PyForgeDatabricks(auto_init=False)

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(b"col1,col2\n1,2\n")
            tmp.flush()

            try:
                validation = forge.validate(tmp.name)

                assert validation["is_valid"] is True
                assert len(validation["issues"]) == 0

            finally:
                os.unlink(tmp.name)

    def test_validate_empty_file(self):
        """Test validation of empty file."""
        forge = PyForgeDatabricks(auto_init=False)

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            # Empty file
            tmp.flush()

            try:
                validation = forge.validate(tmp.name)

                assert validation["is_valid"] is False
                assert "empty" in str(validation["issues"]).lower()

            finally:
                os.unlink(tmp.name)

    def test_get_statistics(self):
        """Test statistics retrieval."""
        forge = PyForgeDatabricks(auto_init=False)

        stats = forge.get_statistics()

        assert "total_conversions" in stats
        assert "successful_conversions" in stats
        assert "failed_conversions" in stats
        assert "success_rate" in stats


class TestDatabricksExtension:
    """Test DatabricksExtension class."""

    def test_extension_metadata(self):
        """Test extension metadata."""
        ext = DatabricksExtension()

        assert ext.name == "databricks"
        assert ext.version == "1.0.0"
        assert "Databricks" in ext.description

    def test_is_available(self):
        """Test extension availability."""
        ext = DatabricksExtension()

        # Should always be available (features vary by environment)
        assert ext.is_available() is True

    @patch("pyspark.sql.SparkSession")
    def test_initialize(self, mock_spark):
        """Test extension initialization."""
        ext = DatabricksExtension()

        result = ext.initialize()
        assert result is True
        assert ext.initialized is True

    def test_get_commands(self):
        """Test CLI command registration."""
        ext = DatabricksExtension()

        commands = ext.get_commands()
        assert "install-datasets" in commands
        assert "list-volumes" in commands
        assert "env-info" in commands
        assert "validate-volume" in commands

    def test_enhance_convert_command(self):
        """Test convert command enhancement."""
        ext = DatabricksExtension()
        ext.initialized = True

        options = {
            "input_file": "/path/to/file.csv",
            "file_size": 200 * 1024 * 1024,  # 200MB
        }

        with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x"}):
            enhanced = ext.enhance_convert_command(options)

            assert enhanced.get("use_spark") is True

    def test_hook_pre_conversion(self):
        """Test pre-conversion hook."""
        ext = DatabricksExtension()
        ext.initialized = True

        input_file = Path("test.csv")
        output_file = Path("test.parquet")
        options = {}

        with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x"}):
            result = ext.hook_pre_conversion(input_file, output_file, options)

            assert result is not None
            assert "databricks_environment" in result

    def test_hook_error_handling(self):
        """Test error handling hook."""
        ext = DatabricksExtension()
        ext.initialized = True

        # Test Spark error handling
        spark_error = Exception("SparkException: Some error")
        context = {}

        handled = ext.hook_error_handling(spark_error, context)
        assert handled is True
        assert context.get("fallback_to_pandas") is True

    def test_hook_environment_detection(self):
        """Test environment detection hook."""
        ext = DatabricksExtension()

        # Test non-Databricks environment
        with patch.dict(os.environ, {}, clear=True):
            env_info = ext.hook_environment_detection()
            assert isinstance(env_info, dict)
            # In non-Databricks environment, extension_active should not be set

        # Test Databricks environment
        with patch.dict(os.environ, {"DATABRICKS_RUNTIME_VERSION": "13.3.x"}):
            # Need to clear the cache and reinitialize to detect the new environment
            ext.environment.clear_cache()
            env_info = ext.hook_environment_detection()
            assert env_info.get("extension_active") is True


# Integration tests
class TestIntegration:
    """Integration tests for the complete extension."""

    @pytest.mark.integration
    @patch("pyspark.sql.SparkSession")
    def test_full_conversion_flow(self, mock_spark):
        """Test complete conversion flow."""
        # Initialize extension
        ext = DatabricksExtension()
        ext.initialize()

        # Get notebook API
        forge = ext.get_notebook_api()

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(b"id,name,value\n1,test,100\n2,example,200\n")
            tmp.flush()

            try:
                # Mock the actual conversion
                with patch.object(
                    forge.fallback_manager, "execute_with_fallback"
                ) as mock_exec:
                    mock_exec.return_value = Mock(
                        success=True,
                        final_converter=ConverterType.SPARK,
                        attempts=[],
                        warnings=[],
                        output_path=Path("output.parquet"),
                    )

                    # Perform conversion
                    result = forge.convert(tmp.name, format="parquet")

                    assert result["success"] is True
                    assert result["converter_used"] == "spark"

            finally:
                os.unlink(tmp.name)

    @pytest.mark.integration
    def test_environment_specific_behavior(self):
        """Test behavior changes based on environment."""
        ext = DatabricksExtension()

        # Test in non-Databricks environment
        with patch.dict(os.environ, {}, clear=True):
            ext.initialize()
            env_info = ext.hook_environment_detection()
            assert env_info.get("extension_active", False) is False

        # Test in Databricks serverless
        with patch.dict(
            os.environ,
            {
                "DATABRICKS_RUNTIME_VERSION": "13.3.x-serverless-scala2.12",
                "DATABRICKS_SERVERLESS_COMPUTE": "true",
            },
        ):
            ext = DatabricksExtension()  # Reinitialize
            ext.initialize()
            env_info = ext.hook_environment_detection()
            assert env_info.get("compute_type") == "serverless"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
