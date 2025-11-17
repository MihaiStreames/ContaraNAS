from datetime import datetime

from nicegui import ui

from ContaraNAS.core.utils import get_cache_dir
from ContaraNAS.gui.utils import format_bytes
from ContaraNAS.modules.steam.constants import SORT_BY_LAST_PLAYED, SORT_BY_NAME, SORT_BY_SIZE


def sort_games(games: list[dict], sort_by: str) -> list[dict]:
    """Sort games based on the specified criteria"""
    if sort_by == SORT_BY_SIZE:
        return sorted(games, key=lambda g: g["total_size"], reverse=True)
    elif sort_by == SORT_BY_NAME:
        return sorted(games, key=lambda g: g["name"].lower())
    elif sort_by == SORT_BY_LAST_PLAYED:
        return sorted(
            games,
            key=lambda g: g["last_played"] if g["last_played"] > 0 else 0,
            reverse=True
        )
    return games


def get_game_image_path(app_id: int) -> str:
    """Get the path to a cached game image"""
    image_cache_dir = get_cache_dir() / "steam" / "images"
    image_path = image_cache_dir / f"{app_id}.jpg"

    if image_path.exists():
        return str(image_path)
    return ""


def format_last_played(timestamp: int) -> str:
    """Format last played timestamp to readable string"""
    if timestamp == 0:
        return "Never played"

    last_played_date = datetime.fromtimestamp(timestamp)
    now = datetime.now()

    # Calculate time difference
    diff = now - last_played_date

    if diff.days == 0:
        return "Today"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif diff.days < 365:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"


def render_game_row(game: dict) -> None:
    """Render a single game row in the modal"""
    with ui.row().classes("w-full items-center gap-3 p-2 hover:bg-gray-100 rounded"):
        # Game image on the left
        image_path = get_game_image_path(game["app_id"])
        if image_path:
            ui.image(image_path).classes("w-24 h-auto rounded")
        else:
            # Placeholder if no image
            with ui.element("div").classes("w-24 h-12 bg-gray-300 rounded flex items-center justify-center"):
                ui.label("No Image").classes("text-xs text-gray-500")

        # Game info in the middle (flex-grow)
        with ui.column().classes("flex-1 gap-0"):
            ui.label(game["name"]).classes("text-sm font-semibold")
            ui.label(format_last_played(game["last_played"])).classes("text-xs text-gray-500")

        # Size on the right
        ui.label(format_bytes(game["total_size"])).classes("text-sm font-bold min-w-fit")


def render_modal_content(games: list[dict], library_path: str, sort_by: str, on_sort_change) -> None:
    """Render the modal content with game list and sorting options"""
    with ui.column().classes("w-full gap-4"):
        # Header with library path and sort options
        with ui.row().classes("w-full justify-between items-center"):
            ui.label(f"Games in: {library_path}").classes("text-lg font-bold")

            # Sort dropdown
            with ui.row().classes("gap-2 items-center"):
                ui.label("Sort by:").classes("text-sm")
                ui.select(
                    options={
                        SORT_BY_SIZE: "Size",
                        SORT_BY_NAME: "Name",
                        SORT_BY_LAST_PLAYED: "Last Played"
                    },
                    value=sort_by,
                    on_change=lambda e: on_sort_change(e.value)
                ).classes("w-32")

        ui.separator()

        # Games list
        sorted_games = sort_games(games, sort_by)

        with ui.scroll_area().classes("w-full h-96"):
            with ui.column().classes("w-full gap-1"):
                for game in sorted_games:
                    render_game_row(game)

        # Footer with game count
        ui.separator()
        ui.label(f"Total: {len(games)} game{'s' if len(games) != 1 else ''}").classes("text-sm text-gray-500")
