from enum import Enum


def get_enum_names(enum_class: type[Enum]) -> list[str]:
    """Get list of names from an Enum class."""
    return [member.name for member in enum_class]


def get_enum_values(enum_class: type[Enum]) -> list[str]:
    """Get list of values from an Enum class."""
    return [member.value for member in enum_class]
