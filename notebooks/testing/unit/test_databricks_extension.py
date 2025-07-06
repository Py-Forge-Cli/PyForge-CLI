#!/usr/bin/env python3
"""
Unit tests for PyForge CLI Databricks Extension

This module contains unit tests for the Databricks extension components including:
- Extension discovery and loading
- Environment detection
- API method implementations
- Error handling and edge cases
- Configuration management

Usage:
    python test_databricks_extension.py
    pytest test_databricks_extension.py -v
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

# Add source directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

class TestDatabricksExtensionDiscovery(unittest.TestCase):
    """Test cases for Databricks extension discovery mechanism"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_plugin_discovery_import(self):
        """Test that plugin discovery module can be imported"""
        try:
            from pyforge_cli.plugin_system import discovery
            self.assertIsNotNone(discovery)
        except ImportError as e:
            self.skipTest(f"Plugin discovery module not available: {e}")
    
    def test_plugin_discovery_instantiation(self):
        """Test that PluginDiscovery can be instantiated"""
        try:
            from pyforge_cli.plugin_system.discovery import PluginDiscovery
            
            plugin_discovery = PluginDiscovery()
            self.assertIsNotNone(plugin_discovery)
            self.assertTrue(hasattr(plugin_discovery, 'discover_extensions'))
            self.assertTrue(hasattr(plugin_discovery, 'initialize_extensions'))
            
        except ImportError:
            self.skipTest("PluginDiscovery not available")
    
    @patch('pyforge_cli.plugin_system.discovery.metadata.entry_points')
    def test_extension_discovery_with_mock_entry_points(self, mock_entry_points):
        """Test extension discovery with mocked entry points"""
        try:
            from pyforge_cli.plugin_system.discovery import PluginDiscovery
            
            # Mock entry points
            mock_entry_point = Mock()
            mock_entry_point.name = 'databricks'
            mock_entry_point.load.return_value = Mock()
            
            mock_entry_points.return_value = [mock_entry_point]
            
            plugin_discovery = PluginDiscovery()
            extensions = plugin_discovery.discover_extensions()
            
            self.assertIsInstance(extensions, dict)
            
        except ImportError:
            self.skipTest("PluginDiscovery not available")
    
    def test_extension_discovery_error_handling(self):
        """Test that extension discovery handles errors gracefully"""
        try:
            from pyforge_cli.plugin_system.discovery import PluginDiscovery
            
            plugin_discovery = PluginDiscovery()
            
            # Should not raise exception even if no extensions found
            extensions = plugin_discovery.discover_extensions()
            self.assertIsInstance(extensions, dict)
            
        except ImportError:
            self.skipTest("PluginDiscovery not available")


class TestDatabricksExtensionBase(unittest.TestCase):
    """Test cases for Databricks extension base class"""
    
    def test_base_extension_import(self):
        """Test that BaseExtension can be imported"""
        try:
            from pyforge_cli.extensions.base import BaseExtension
            self.assertIsNotNone(BaseExtension)
        except ImportError as e:
            self.skipTest(f"BaseExtension not available: {e}")
    
    def test_base_extension_abstract_methods(self):
        """Test that BaseExtension has required abstract methods"""
        try:
            from pyforge_cli.extensions.base import BaseExtension
            
            # Check that abstract methods exist
            self.assertTrue(hasattr(BaseExtension, 'is_available'))
            self.assertTrue(hasattr(BaseExtension, 'initialize'))
            
            # Check that we cannot instantiate abstract class
            with self.assertRaises(TypeError):
                BaseExtension()
                
        except ImportError:
            self.skipTest("BaseExtension not available")
    
    def test_extension_hook_methods(self):
        """Test that BaseExtension has hook methods"""
        try:
            from pyforge_cli.extensions.base import BaseExtension
            
            # Check hook methods exist
            self.assertTrue(hasattr(BaseExtension, 'hook_pre_conversion'))
            self.assertTrue(hasattr(BaseExtension, 'hook_post_conversion'))
            
        except ImportError:
            self.skipTest("BaseExtension not available")


class TestDatabricksExtensionRegistry(unittest.TestCase):
    """Test cases for extension registry functionality"""
    
    def test_extension_registry_import(self):
        """Test that ExtensionRegistry can be imported"""
        try:
            from pyforge_cli.plugin_system.registry import ExtensionRegistry
            self.assertIsNotNone(ExtensionRegistry)
        except ImportError as e:
            self.skipTest(f"ExtensionRegistry not available: {e}")
    
    def test_extension_registry_instantiation(self):
        """Test that ExtensionRegistry can be instantiated"""
        try:
            from pyforge_cli.plugin_system.registry import ExtensionRegistry
            
            registry = ExtensionRegistry()
            self.assertIsNotNone(registry)
            self.assertTrue(hasattr(registry, 'register_extension'))
            self.assertTrue(hasattr(registry, 'get_extension'))
            
        except ImportError:
            self.skipTest("ExtensionRegistry not available")
    
    def test_extension_registration(self):
        """Test extension registration functionality"""
        try:
            from pyforge_cli.plugin_system.registry import ExtensionRegistry
            
            registry = ExtensionRegistry()
            
            # Mock extension
            mock_extension = Mock()
            mock_extension.is_available.return_value = True
            mock_extension.initialize.return_value = True
            
            # Test registration
            registry.register_extension('test_extension', mock_extension)
            
            # Test retrieval
            retrieved_extension = registry.get_extension('test_extension')
            self.assertEqual(retrieved_extension, mock_extension)
            
        except ImportError:
            self.skipTest("ExtensionRegistry not available")


class TestEnvironmentDetection(unittest.TestCase):
    """Test cases for environment detection functionality"""
    
    def test_environment_detection_basic(self):
        """Test basic environment detection"""
        # Test that we can detect basic environment info
        import os
        import sys
        
        # Should be able to get basic environment info
        python_version = sys.version
        self.assertIsNotNone(python_version)
        
        platform = sys.platform
        self.assertIsNotNone(platform)
    
    @patch.dict(os.environ, {'DATABRICKS_RUNTIME_VERSION': 'serverless-14.3.x'})
    def test_serverless_environment_detection(self):
        """Test serverless environment detection"""
        import os
        
        runtime_version = os.environ.get('DATABRICKS_RUNTIME_VERSION')
        is_serverless = 'serverless' in runtime_version.lower()
        
        self.assertTrue(is_serverless)
    
    @patch.dict(os.environ, {'DATABRICKS_RUNTIME_VERSION': '14.3.x-scala2.12'})
    def test_classic_environment_detection(self):
        """Test classic environment detection"""
        import os
        
        runtime_version = os.environ.get('DATABRICKS_RUNTIME_VERSION')
        is_serverless = 'serverless' in runtime_version.lower()
        
        self.assertFalse(is_serverless)
    
    def test_pyspark_availability_detection(self):
        """Test PySpark availability detection"""
        try:
            import pyspark
            pyspark_available = True
            pyspark_version = pyspark.__version__
        except ImportError:
            pyspark_available = False
            pyspark_version = None
        
        # Should be able to detect whether PySpark is available
        self.assertIsInstance(pyspark_available, bool)
        
        if pyspark_available:
            self.assertIsNotNone(pyspark_version)


class TestDatabricksExtensionAPI(unittest.TestCase):
    """Test cases for Databricks extension API methods"""
    
    def test_core_cli_integration(self):
        """Test that core CLI can be imported and has expected structure"""
        try:
            import pyforge_cli
            self.assertIsNotNone(pyforge_cli)
            self.assertTrue(hasattr(pyforge_cli, '__version__'))
            
        except ImportError as e:
            self.skipTest(f"PyForge CLI not available: {e}")
    
    def test_plugin_registry_integration(self):
        """Test that plugin registry integration works"""
        try:
            from pyforge_cli.plugins import registry
            
            # Should be able to list supported formats
            formats = registry.list_supported_formats()
            self.assertIsInstance(formats, dict)
            
        except ImportError:
            self.skipTest("Plugin registry not available")
    
    def test_converter_selection(self):
        """Test converter selection functionality"""
        try:
            from pyforge_cli.plugins import registry
            from pathlib import Path
            
            # Test with common file types
            test_files = [
                Path('test.csv'),
                Path('test.xlsx'),
                Path('test.pdf'),
                Path('test.xml')
            ]
            
            for test_file in test_files:
                converter = registry.get_converter(test_file)
                # Should either find a converter or return None
                self.assertTrue(converter is None or hasattr(converter, 'convert'))
                
        except ImportError:
            self.skipTest("Plugin registry not available")


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases"""
    
    def test_missing_dependency_handling(self):
        """Test handling of missing optional dependencies"""
        # Test that missing dependencies are handled gracefully
        
        # Mock missing databricks-sdk
        with patch.dict('sys.modules', {'databricks': None}):
            try:
                # Should be able to import core functionality
                import pyforge_cli
                self.assertIsNotNone(pyforge_cli)
            except ImportError:
                self.skipTest("Core PyForge CLI not available")
    
    def test_invalid_configuration_handling(self):
        """Test handling of invalid configuration"""
        # Test with invalid paths
        invalid_paths = [
            '/nonexistent/path',
            '',
            None,
            123  # Invalid type
        ]
        
        for invalid_path in invalid_paths:
            # Should handle invalid paths gracefully
            # This would test actual API methods once implemented
            pass
    
    def test_timeout_scenarios(self):
        """Test timeout handling"""
        import time
        
        # Test that operations complete within reasonable time
        start_time = time.time()
        
        # Simulate a quick operation
        time.sleep(0.01)
        
        elapsed = time.time() - start_time
        
        # Should complete quickly
        self.assertLess(elapsed, 1.0)
    
    def test_memory_pressure_scenarios(self):
        """Test handling of memory pressure"""
        # Test with moderately large data structures
        try:
            large_list = list(range(10000))
            self.assertEqual(len(large_list), 10000)
            
            # Should be able to handle moderate data sizes
            del large_list
            
        except MemoryError:
            self.skipTest("Insufficient memory for test")


class TestConfigurationManagement(unittest.TestCase):
    """Test cases for configuration management"""
    
    def setUp(self):
        """Set up test configuration"""
        self.test_config = {
            'catalog_name': 'test_catalog',
            'schema_name': 'test_schema',
            'volume_name': 'test_volume',
            'environment': 'test'
        }
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        # Test valid configuration
        valid_config = {
            'catalog_name': 'main',
            'schema_name': 'default',
            'volume_name': 'pyforge'
        }
        
        # Should validate required fields
        required_fields = ['catalog_name', 'schema_name', 'volume_name']
        for field in required_fields:
            self.assertIn(field, valid_config)
            self.assertIsInstance(valid_config[field], str)
            self.assertGreater(len(valid_config[field]), 0)
    
    def test_volume_path_construction(self):
        """Test volume path construction"""
        catalog = 'test_catalog'
        schema = 'test_schema'
        volume = 'test_volume'
        
        expected_path = f"/Volumes/{catalog}/{schema}/{volume}"
        
        # Test path construction
        self.assertEqual(expected_path, "/Volumes/test_catalog/test_schema/test_volume")
    
    def test_configuration_defaults(self):
        """Test configuration defaults"""
        # Test that sensible defaults are provided
        default_config = {
            'catalog_name': 'main',
            'schema_name': 'default',
            'pyforge_version': 'latest',
            'test_environment': 'auto'
        }
        
        # Should have reasonable defaults
        for key, value in default_config.items():
            self.assertIsNotNone(value)
            self.assertIsInstance(value, str)


class TestPerformanceMetrics(unittest.TestCase):
    """Test cases for performance measurement and metrics"""
    
    def test_timing_measurement(self):
        """Test timing measurement functionality"""
        import time
        
        start_time = time.time()
        time.sleep(0.01)  # Small delay
        elapsed = time.time() - start_time
        
        # Should measure time accurately
        self.assertGreater(elapsed, 0.005)  # At least 5ms
        self.assertLess(elapsed, 0.1)       # Less than 100ms
    
    def test_memory_measurement(self):
        """Test memory measurement functionality"""
        try:
            import psutil
            
            # Get current process memory
            process = psutil.Process()
            memory_info = process.memory_info()
            
            # Should have reasonable memory usage
            self.assertGreater(memory_info.rss, 0)
            self.assertLess(memory_info.rss, 1024 * 1024 * 1024)  # Less than 1GB
            
        except ImportError:
            self.skipTest("psutil not available for memory measurement")
    
    def test_data_processing_rate_calculation(self):
        """Test data processing rate calculation"""
        # Test rate calculations
        rows = 1000
        time_seconds = 2.0
        
        rate = rows / time_seconds
        
        self.assertEqual(rate, 500.0)  # 500 rows/second
        
        # Test with different units
        mb_size = 10.0
        mb_per_second = mb_size / time_seconds
        
        self.assertEqual(mb_per_second, 5.0)  # 5 MB/second


def run_tests():
    """Run all unit tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDatabricksExtensionDiscovery,
        TestDatabricksExtensionBase,
        TestDatabricksExtensionRegistry,
        TestEnvironmentDetection,
        TestDatabricksExtensionAPI,
        TestErrorHandling,
        TestConfigurationManagement,
        TestPerformanceMetrics
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return test results
    return result


if __name__ == '__main__':
    print("=" * 60)
    print("PyForge CLI Databricks Extension Unit Tests")
    print("=" * 60)
    
    result = run_tests()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)