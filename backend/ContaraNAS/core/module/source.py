from enum import Enum


class ModuleSource(Enum):
    """Source/origin of a module"""

    BUILTIN = "builtin"
    COMMUNITY = "community"
    LOCAL = "local"
