"""
Example PyForge CLI Extension

This example demonstrates how to create a PyForge CLI extension that:
- Integrates with external APIs
- Provides custom commands
- Uses the hook system for pre/post processing
- Handles errors gracefully
- Supports environment-specific optimizations

This can be used as a template for creating your own extensions.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from pyforge_cli.extensions.base import BaseExtension


class ExampleExtension(BaseExtension):
    """
    Example extension demonstrating PyForge CLI extension capabilities.
    
    This extension shows how to:
    - Check for dependencies and environment conditions
    - Initialize and configure the extension
    - Add custom CLI commands
    - Use hooks to enhance conversion workflow
    - Handle errors and edge cases
    - Provide environment-specific optimizations
    """
    
    def __init__(self):
        """Initialize the example extension."""
        super().__init__()
        
        # Extension metadata
        self.name = "example"
        self.version = "1.0.0"
        self.description = "Example extension demonstrating PyForge CLI extension development"
        
        # Extension configuration
        self.config = {}
        self.api_client = None
        self.cache_dir = None
        
        # Set up logging
        self.logger = logging.getLogger(f"pyforge.extensions.{self.name}")
    
    def is_available(self) -> bool:
        """
        Check if extension dependencies are available.
        
        This method should verify that all required dependencies,
        environment conditions, and external services are available.
        """
        try:
            # Check for required Python packages
            import requests
            import json
            
            # Check for optional packages that enable additional features
            try:
                import pandas
                self.pandas_available = True
            except ImportError:
                self.pandas_available = False
                self.logger.debug("Pandas not available - some features will be limited")
            
            # Check environment conditions
            # Example: Check if we're in a supported environment
            if os.environ.get('EXAMPLE_DISABLE_EXTENSION'):
                self.logger.info("Extension disabled via environment variable")
                return False
            
            # Check for external service availability (optional)
            try:
                # This could be an API health check
                # For example: requests.get("https://api.example.com/health", timeout=1)
                pass
            except Exception as e:
                self.logger.debug(f"External service check failed: {e}")
                # Don't fail availability check for optional services
            
            return True
            
        except ImportError as e:
            self.logger.debug(f"Required dependency not available: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in availability check: {e}")
            return False
    
    def initialize(self) -> bool:
        """
        Initialize the extension.
        
        This method is called once when the extension is loaded.
        It should perform setup tasks like loading configuration,
        establishing connections, and preparing resources.
        """
        if not self.is_available():
            self.logger.warning("Extension not available - initialization skipped")
            return False
        
        try:
            # Load configuration
            self.config = self._load_config()
            self.logger.debug(f"Loaded configuration: {self.config}")
            
            # Set up cache directory
            self.cache_dir = self._setup_cache_directory()
            
            # Initialize API client (example)
            self.api_client = self._initialize_api_client()
            
            # Perform any other initialization tasks
            self._setup_monitoring()
            
            # Mark as initialized
            self.initialized = True
            self.logger.info(f"Extension {self.name} v{self.version} initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Extension initialization failed: {e}")
            return False
    
    def cleanup(self) -> None:
        """
        Clean up extension resources.
        
        This method is called when the extension is being unloaded
        or when the application is shutting down.
        """
        try:
            # Close API connections
            if self.api_client:
                # Example: self.api_client.close()
                self.api_client = None
            
            # Clean up temporary files
            if self.cache_dir and self.cache_dir.exists():
                # Example: shutil.rmtree(self.cache_dir)
                pass
            
            self.logger.info(f"Extension {self.name} cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        finally:
            super().cleanup()
    
    def get_commands(self) -> Dict[str, Any]:
        """
        Get additional CLI commands provided by this extension.
        
        Returns dictionary mapping command names to command functions.
        """
        return {
            'example-status': self.status_command,
            'example-config': self.config_command,
            'example-test': self.test_command
        }
    
    def enhance_convert_command(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance the convert command with extension-specific options.
        
        This method can add new options or modify existing ones
        for the convert command.
        """
        # Add example-specific options
        if self.initialized and self.config.get('auto_enhance', True):
            options.setdefault('example_metadata', True)
            options.setdefault('example_validation', True)
            
            # Add environment-specific optimizations
            env_info = self.hook_environment_detection()
            if env_info.get('high_memory_available'):
                options.setdefault('buffer_size', 'large')
        
        return options
    
    # Hook Methods
    
    def hook_pre_conversion(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Hook called before conversion starts.
        
        This is where you can:
        - Validate input files
        - Modify conversion options
        - Prepare external resources
        - Log conversion attempts
        """
        try:
            self.logger.info(f"Pre-conversion: {input_file} -> {output_file}")
            
            # Validate input file
            if not self._validate_input_file(input_file):
                self.logger.warning(f"Input file validation failed: {input_file}")
                return options
            
            # Add metadata about the conversion
            conversion_metadata = {
                'extension_name': self.name,
                'extension_version': self.version,
                'conversion_id': self._generate_conversion_id(),
                'timestamp': datetime.now().isoformat(),
                'input_file_size': input_file.stat().st_size if input_file.exists() else 0
            }
            
            options['conversion_metadata'] = conversion_metadata
            
            # Apply input-specific optimizations
            input_ext = input_file.suffix.lower()
            if input_ext == '.csv' and self.pandas_available:
                options['use_pandas_optimization'] = True
                self.logger.debug("Enabled pandas optimization for CSV file")
            
            # Check for cached results
            cache_key = self._get_cache_key(input_file, options)
            if self._has_cached_result(cache_key):
                options['use_cache'] = True
                options['cache_key'] = cache_key
                self.logger.debug(f"Found cached result for {cache_key}")
            
            return options
            
        except Exception as e:
            self.logger.error(f"Error in pre-conversion hook: {e}")
            return options  # Return original options on error
    
    def hook_post_conversion(self, input_file: Path, output_file: Path, options: Dict[str, Any], success: bool) -> None:
        """
        Hook called after conversion completes.
        
        This is where you can:
        - Process conversion results
        - Update caches
        - Send notifications
        - Log conversion results
        """
        try:
            conversion_metadata = options.get('conversion_metadata', {})
            conversion_id = conversion_metadata.get('conversion_id', 'unknown')
            
            status = "✅ SUCCESS" if success else "❌ FAILED"
            self.logger.info(f"Post-conversion [{conversion_id}]: {status}")
            
            if success:
                # Cache successful conversion metadata
                self._cache_conversion_result(input_file, output_file, options)
                
                # Validate output file
                if output_file.exists():
                    output_size = output_file.stat().st_size
                    self.logger.debug(f"Output file size: {output_size} bytes")
                    
                    # Optional: Send success notification
                    if self.config.get('send_notifications'):
                        self._send_notification('conversion_success', {
                            'input_file': str(input_file),
                            'output_file': str(output_file),
                            'output_size': output_size
                        })
                
                # Update usage statistics
                self._update_usage_stats('conversion_success')
                
            else:
                # Handle conversion failure
                self.logger.warning(f"Conversion failed for {input_file}")
                
                # Optional: Send failure notification
                if self.config.get('send_notifications'):
                    self._send_notification('conversion_failure', {
                        'input_file': str(input_file),
                        'error': 'Conversion failed'
                    })
                
                # Update usage statistics
                self._update_usage_stats('conversion_failure')
            
        except Exception as e:
            self.logger.error(f"Error in post-conversion hook: {e}")
    
    def hook_error_handling(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Hook called when an error occurs during conversion.
        
        Return True if the error was handled, False for default handling.
        """
        try:
            self.logger.error(f"Conversion error: {error}")
            
            # Log error details
            error_info = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save error details to cache for debugging
            self._save_error_log(error_info)
            
            # Check if this is a known error we can handle
            if self._is_recoverable_error(error):
                self.logger.info("Attempting error recovery...")
                return self._attempt_error_recovery(error, context)
            
            # For unknown errors, let default handling take over
            return False
            
        except Exception as e:
            self.logger.error(f"Error in error handling hook: {e}")
            return False
    
    def hook_environment_detection(self) -> Dict[str, Any]:
        """
        Hook for detecting environment-specific information.
        
        Returns environment information that can be used by other hooks
        and the core conversion system.
        """
        env_info = {}
        
        try:
            # Detect system resources
            import psutil
            env_info.update({
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'high_memory_available': psutil.virtual_memory().available > 4 * 1024**3  # 4GB
            })
        except ImportError:
            pass
        
        # Detect cloud environment
        if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
            env_info['cloud_provider'] = 'aws_lambda'
        elif os.environ.get('DATABRICKS_RUNTIME_VERSION'):
            env_info['cloud_provider'] = 'databricks'
        elif os.environ.get('GOOGLE_CLOUD_PROJECT'):
            env_info['cloud_provider'] = 'gcp'
        
        # Detect container environment
        if os.path.exists('/.dockerenv'):
            env_info['container'] = 'docker'
        elif os.environ.get('KUBERNETES_SERVICE_HOST'):
            env_info['container'] = 'kubernetes'
        
        self.logger.debug(f"Environment detection: {env_info}")
        return env_info
    
    def hook_performance_optimization(self, operation: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook for applying performance optimizations.
        
        This can modify options based on the operation type and
        environment conditions.
        """
        try:
            # Get environment information
            env_info = self.hook_environment_detection()
            
            if operation == 'convert':
                # Apply memory-based optimizations
                if env_info.get('high_memory_available'):
                    options['memory_optimization'] = 'high_memory'
                    options['chunk_size'] = 100000  # Larger chunks
                else:
                    options['memory_optimization'] = 'low_memory'
                    options['chunk_size'] = 10000   # Smaller chunks
                
                # Apply cloud-specific optimizations
                cloud_provider = env_info.get('cloud_provider')
                if cloud_provider == 'databricks':
                    options['use_spark'] = True
                elif cloud_provider == 'aws_lambda':
                    options['lambda_optimization'] = True
                    options['timeout_aware'] = True
                
                # Apply container-specific optimizations
                if env_info.get('container'):
                    options['container_optimization'] = True
            
            return options
            
        except Exception as e:
            self.logger.error(f"Error in performance optimization hook: {e}")
            return options
    
    # Custom CLI Commands
    
    def status_command(self) -> bool:
        """Show extension status and configuration."""
        print(f"Extension Status: {self.name} v{self.version}")
        print(f"Initialized: {self.initialized}")
        print(f"Available: {self.is_available()}")
        
        if self.config:
            print(f"Configuration: {json.dumps(self.config, indent=2)}")
        
        if self.cache_dir:
            print(f"Cache Directory: {self.cache_dir}")
            
        # Show usage statistics
        stats = self._get_usage_stats()
        if stats:
            print(f"Usage Statistics: {json.dumps(stats, indent=2)}")
        
        return True
    
    def config_command(self, action: str = 'show', key: str = None, value: str = None) -> bool:
        """Manage extension configuration."""
        if action == 'show':
            print(json.dumps(self.config, indent=2))
        elif action == 'set' and key and value:
            self.config[key] = value
            self._save_config()
            print(f"Set {key} = {value}")
        elif action == 'get' and key:
            print(self.config.get(key, 'Not set'))
        else:
            print("Usage: example-config [show|set|get] [key] [value]")
            return False
        
        return True
    
    def test_command(self) -> bool:
        """Run extension self-tests."""
        print(f"Running self-tests for {self.name} extension...")
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Dependency check
        tests_total += 1
        if self.is_available():
            print("✅ Dependencies available")
            tests_passed += 1
        else:
            print("❌ Dependencies missing")
        
        # Test 2: Initialization
        tests_total += 1
        if self.initialized:
            print("✅ Extension initialized")
            tests_passed += 1
        else:
            print("❌ Extension not initialized")
        
        # Test 3: Configuration
        tests_total += 1
        if self.config:
            print("✅ Configuration loaded")
            tests_passed += 1
        else:
            print("❌ No configuration found")
        
        # Test 4: Cache directory
        tests_total += 1
        if self.cache_dir and self.cache_dir.exists():
            print("✅ Cache directory accessible")
            tests_passed += 1
        else:
            print("❌ Cache directory not accessible")
        
        # Test 5: Hook functionality
        tests_total += 1
        try:
            env_info = self.hook_environment_detection()
            if env_info:
                print("✅ Environment detection working")
                tests_passed += 1
            else:
                print("⚠️ Environment detection returned no data")
        except Exception as e:
            print(f"❌ Environment detection failed: {e}")
        
        print(f"\nTest Results: {tests_passed}/{tests_total} passed")
        return tests_passed == tests_total
    
    # Private Helper Methods
    
    def _load_config(self) -> Dict[str, Any]:
        """Load extension configuration from file."""
        config_file = Path.home() / '.pyforge' / f'{self.name}.json'
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
        
        # Return default configuration
        return {
            'auto_enhance': True,
            'send_notifications': False,
            'cache_enabled': True,
            'debug_mode': False
        }
    
    def _save_config(self) -> None:
        """Save extension configuration to file."""
        config_file = Path.home() / '.pyforge' / f'{self.name}.json'
        config_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def _setup_cache_directory(self) -> Optional[Path]:
        """Set up cache directory for the extension."""
        cache_dir = Path.home() / '.pyforge' / 'cache' / self.name
        
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            return cache_dir
        except Exception as e:
            self.logger.error(f"Failed to create cache directory: {e}")
            return None
    
    def _initialize_api_client(self) -> Optional[Any]:
        """Initialize API client (example)."""
        # This is just an example - replace with actual API client initialization
        try:
            # Example: return SomeAPIClient(api_key=self.config.get('api_key'))
            return {"status": "mock_client_initialized"}
        except Exception as e:
            self.logger.error(f"Failed to initialize API client: {e}")
            return None
    
    def _setup_monitoring(self) -> None:
        """Set up monitoring and metrics collection."""
        # Example: Initialize metrics collection
        pass
    
    def _validate_input_file(self, input_file: Path) -> bool:
        """Validate input file before conversion."""
        try:
            if not input_file.exists():
                return False
            
            if input_file.stat().st_size == 0:
                self.logger.warning(f"Input file is empty: {input_file}")
                return False
            
            # Add more validation as needed
            return True
            
        except Exception as e:
            self.logger.error(f"Input file validation error: {e}")
            return False
    
    def _generate_conversion_id(self) -> str:
        """Generate unique conversion ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_cache_key(self, input_file: Path, options: Dict[str, Any]) -> str:
        """Generate cache key for conversion."""
        import hashlib
        
        # Create cache key from file path, size, and options
        key_data = f"{input_file}:{input_file.stat().st_size}:{hash(str(sorted(options.items())))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _has_cached_result(self, cache_key: str) -> bool:
        """Check if cached result exists."""
        if not self.cache_dir or not self.config.get('cache_enabled'):
            return False
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        return cache_file.exists()
    
    def _cache_conversion_result(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> None:
        """Cache conversion result metadata."""
        if not self.cache_dir or not self.config.get('cache_enabled'):
            return
        
        try:
            cache_key = self._get_cache_key(input_file, options)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            cache_data = {
                'input_file': str(input_file),
                'output_file': str(output_file),
                'options': options,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to cache conversion result: {e}")
    
    def _send_notification(self, event_type: str, data: Dict[str, Any]) -> None:
        """Send notification about conversion events."""
        # Example implementation - replace with actual notification system
        self.logger.info(f"Notification [{event_type}]: {data}")
    
    def _update_usage_stats(self, event: str) -> None:
        """Update usage statistics."""
        if not self.cache_dir:
            return
        
        try:
            stats_file = self.cache_dir / 'usage_stats.json'
            
            # Load existing stats
            if stats_file.exists():
                with open(stats_file) as f:
                    stats = json.load(f)
            else:
                stats = {}
            
            # Update stats
            stats[event] = stats.get(event, 0) + 1
            stats['last_updated'] = datetime.now().isoformat()
            
            # Save stats
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to update usage stats: {e}")
    
    def _get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        if not self.cache_dir:
            return {}
        
        try:
            stats_file = self.cache_dir / 'usage_stats.json'
            if stats_file.exists():
                with open(stats_file) as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load usage stats: {e}")
        
        return {}
    
    def _save_error_log(self, error_info: Dict[str, Any]) -> None:
        """Save error information for debugging."""
        if not self.cache_dir:
            return
        
        try:
            error_log_file = self.cache_dir / 'error_log.jsonl'
            
            with open(error_log_file, 'a') as f:
                f.write(json.dumps(error_info) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to save error log: {e}")
    
    def _is_recoverable_error(self, error: Exception) -> bool:
        """Check if error is recoverable."""
        # Example: Certain types of errors might be recoverable
        recoverable_errors = (
            ConnectionError,
            TimeoutError,
            # Add other recoverable error types
        )
        
        return isinstance(error, recoverable_errors)
    
    def _attempt_error_recovery(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from error."""
        try:
            if isinstance(error, ConnectionError):
                # Example: Retry with exponential backoff
                self.logger.info("Attempting connection error recovery...")
                # Implementation here
                return False  # Return True if recovery successful
            
            # Add other recovery strategies
            
        except Exception as e:
            self.logger.error(f"Error recovery failed: {e}")
        
        return False


# Example of how to create a specialized extension by inheriting from ExampleExtension
class CloudOptimizedExtension(ExampleExtension):
    """
    Example of a specialized extension that builds on the base example.
    
    This demonstrates how to extend existing extensions for specific use cases.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "cloud_optimized"
        self.version = "1.0.0"
        self.description = "Cloud-optimized version of example extension"
    
    def hook_performance_optimization(self, operation: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Apply cloud-specific performance optimizations."""
        # Call parent optimization first
        options = super().hook_performance_optimization(operation, options)
        
        # Add cloud-specific optimizations
        env_info = self.hook_environment_detection()
        cloud_provider = env_info.get('cloud_provider')
        
        if cloud_provider == 'aws_lambda':
            # AWS Lambda optimizations
            options.update({
                'lambda_memory_optimization': True,
                'concurrent_processing': False,  # Lambda has limited concurrency
                'timeout_buffer': 30  # Reserve 30 seconds for cleanup
            })
        elif cloud_provider == 'databricks':
            # Databricks optimizations
            options.update({
                'spark_optimization': True,
                'partition_optimization': True,
                'broadcast_joins': True
            })
        
        return options


# Export the main extension class
__all__ = ['ExampleExtension', 'CloudOptimizedExtension']