from dataclasses import dataclass, field
from enum import Enum


class ThemeMode(str, Enum):
    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True)
class ColorShades:
    """5 shades of a color for depth effects"""

    darkest: str
    dark: str
    base: str
    light: str
    lightest: str


@dataclass(frozen=True)
class Shadows:
    """Shadow levels"""

    none: str = "none"
    sm: str = ""
    md: str = ""
    lg: str = ""
    inset: str = ""


@dataclass
class Theme:
    """Complete theme definition"""

    name: str
    mode: ThemeMode

    # Backgrounds
    bg_base: str  # Page background (darkest)
    bg_surface: str  # Cards (middle)
    bg_elevated: str  # Interactive elements (lightest)
    bg_input: str  # Input fields

    # Text
    text_primary: str
    text_secondary: str
    text_muted: str
    text_inverse: str

    # Borders
    border_default: str
    border_subtle: str

    # Color palettes
    primary: ColorShades
    success: ColorShades
    warning: ColorShades
    danger: ColorShades
    info: ColorShades
    neutral: ColorShades

    # Shadows
    shadows: Shadows = field(default_factory=Shadows)

    # Graph colors
    graph_primary: str = ""
    graph_secondary: str = ""
    graph_tertiary: str = ""
    graph_quaternary: str = ""
    graph_fill_opacity: float = 0.3
