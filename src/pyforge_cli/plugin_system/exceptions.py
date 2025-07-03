"""Plugin system exceptions."""


class PluginError(Exception):
    """Base exception for plugin system errors."""
    pass


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""
    pass


class PluginInitializationError(PluginError):
    """Raised when a plugin fails to initialize."""
    pass