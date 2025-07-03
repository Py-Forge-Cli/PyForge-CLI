"""PyForge CLI Extensions package.

This package provides the extension system for PyForge CLI, allowing developers
to create plugins that extend the functionality of the CLI tool.

The extension system supports:
- Plugin discovery through Python entry points
- Lifecycle management (initialization, cleanup)
- Hook system for extending core functionality
- Environment detection and adaptation
- Graceful error handling and fallback behavior

Example:
    from pyforge_cli.extensions.base import BaseExtension
    
    class MyExtension(BaseExtension):
        def is_available(self) -> bool:
            return True
            
        def initialize(self) -> bool:
            return True
"""

from .base import BaseExtension

__all__ = ['BaseExtension']