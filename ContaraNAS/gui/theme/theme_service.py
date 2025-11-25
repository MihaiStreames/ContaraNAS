from collections.abc import Callable

from nicegui import ui

from ContaraNAS.core.utils import get_cache_dir, get_logger, load_json, save_json
from ContaraNAS.gui.theme.dark_theme import DARK_THEME
from ContaraNAS.gui.theme.light_theme import LIGHT_THEME
from ContaraNAS.gui.theme.theme import Theme, ThemeMode


logger = get_logger(__name__)

THEMES = {"light": LIGHT_THEME, "dark": DARK_THEME}


class ThemeService:
    """Manages current theme state and CSS injection"""

    _instance: "ThemeService | None" = None

    def __new__(cls) -> "ThemeService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._current: Theme = DARK_THEME
        self._listeners: list[Callable[[Theme], None]] = []
        self._cache_file = get_cache_dir() / "theme_preference.json"
        self._initialized = True
        self._load_preference()

    @property
    def current(self) -> Theme:
        return self._current

    @property
    def is_dark(self) -> bool:
        return self._current.mode == ThemeMode.DARK

    def set_theme(self, name: str) -> None:
        if name in THEMES:
            self._current = THEMES[name]
            self._save_preference()
            self._inject_css()
            for listener in self._listeners:
                listener(self._current)

    def toggle(self) -> None:
        self.set_theme("dark" if not self.is_dark else "light")

    def subscribe(self, callback: Callable[[Theme], None]) -> None:
        self._listeners.append(callback)

    def initialize(self) -> None:
        """Call this in setup_gui() to inject CSS"""
        self._inject_css()
        self._setup_nicegui_colors()

    def _inject_css(self) -> None:
        """Inject CSS custom properties"""
        t = self._current
        ui.add_css(f"""
        :root {{
            --bg-base: {t.bg_base};
            --bg-surface: {t.bg_surface};
            --bg-elevated: {t.bg_elevated};
            --text-primary: {t.text_primary};
            --text-secondary: {t.text_secondary};
            --text-muted: {t.text_muted};
            --border-default: {t.border_default};
            --shadow-sm: {t.shadows.sm};
            --shadow-md: {t.shadows.md};
            --shadow-lg: {t.shadows.lg};
            --shadow-inset: {t.shadows.inset};
        }}
        body {{ background-color: var(--bg-base); color: var(--text-primary); }}
        """)

    def _setup_nicegui_colors(self) -> None:
        t = self._current
        ui.colors(
            primary=t.primary.base,
            positive=t.success.base,
            negative=t.danger.base,
            warning=t.warning.base,
            info=t.info.base,
        )

    def _save_preference(self) -> None:
        try:
            save_json(self._cache_file, {"theme": self._current.mode.value})
        except Exception as e:
            logger.error(f"Failed to save theme: {e}")

    def _load_preference(self) -> None:
        try:
            data = load_json(self._cache_file)
            if data and data.get("theme") in THEMES:
                self._current = THEMES[data["theme"]]
        except Exception as e:
            logger.error(f"Failed to load theme: {e}")


# Global instance
theme = ThemeService()


def get_color(path: str) -> str:
    """Get color from current theme"""
    t = theme.current
    parts = path.split(".")

    if len(parts) == 1:
        return getattr(t, parts[0], "#000000")
    if len(parts) == 2:
        palette = getattr(t, parts[0], None)
        if palette:
            return getattr(palette, parts[1], "#000000")
    return "#000000"


def get_shadow(level: str = "md") -> str:
    """Get shadow CSS value: 'none', 'sm', 'md', 'lg', 'inset'"""
    return getattr(theme.current.shadows, level, "none")


def get_graph_color(key: str = "primary") -> str:
    """Get graph color: 'primary', 'secondary', 'tertiary', 'quaternary'"""
    return getattr(theme.current, f"graph_{key}", theme.current.graph_primary)


def get_graph_fill_opacity() -> float:
    return theme.current.graph_fill_opacity
