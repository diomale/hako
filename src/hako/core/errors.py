"""Exception types used by HAKO."""


class HakoError(Exception):
    """Base class for expected HAKO errors."""


class ConfigError(HakoError):
    """Raised when configuration is missing, invalid, or unreadable."""
