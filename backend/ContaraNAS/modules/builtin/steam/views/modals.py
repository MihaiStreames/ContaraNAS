import hashlib

from ContaraNAS.core import settings
from ContaraNAS.core.ui import (
    Modal,
    Stack,
    Stat,
    Table,
    TableColumn,
    Text,
)

from .helpers import convert_date_to_string, format_bytes


def _get_image_path(app_id: int) -> str:
    """Get the file path for a cached game image"""
    return str(settings.cache_dir / "steam" / "images" / f"{app_id}.jpg")


def get_library_modal_id(library_path: str) -> str:
    """Generate a unique modal ID for a library path"""
    # Use a hash to create a safe ID from the path
    path_hash = hashlib.md5(library_path.encode()).hexdigest()[:8]
    return f"steam_library_{path_hash}"


def build_library_modal(library: dict, games: list[dict]) -> Modal:
    """Build a modal for a specific library showing its games"""
    path = library.get("path", "Unknown")
    modal_id = get_library_modal_id(path)

    # Filter games for this library
    library_games = [g for g in games if g.get("library_path") == path]

    if not library_games:
        return Modal(
            id=modal_id,
            title=path,  # Full path as title
            size="lg",
            children=[Text(content="No games found in this library", variant="muted")],
        )

    # Library stats
    games_size = library.get("total_games_size", 0)
    drive_free = library.get("drive_free", 0)

    # Build table columns with image support
    columns = [
        TableColumn(key="image", label="", render="image", sortable=False),
        TableColumn(key="name", label="Game"),
        TableColumn(key="size", label="Size"),
        TableColumn(key="last_played", label="Last Played"),
    ]

    # Build table data (use _sort suffix for sortable values)
    table_data = []
    for game in library_games:
        app_id = game.get("app_id", 0)
        game_size = game.get("total_size", 0)
        last_played = convert_date_to_string(game.get("last_played", 0))

        table_data.append(
            {
                "image": _get_image_path(app_id),
                "name": game.get("name", "Unknown"),
                "size": format_bytes(game_size),
                "size_sort": game_size,
                "last_played": last_played,
            }
        )

    return Modal(
        id=modal_id,
        title=path.upper(),
        size="lg",
        children=[
            Stack(
                direction="vertical",
                gap="4",
                children=[
                    # Summary stats
                    Stack(
                        direction="horizontal",
                        gap="6",
                        justify="around",
                        align="center",
                        grow=True,
                        children=[
                            Stat(label="Games", value=str(len(library_games))),
                            Stat(label="Total Size", value=format_bytes(games_size)),
                            Stat(label="Free Space", value=format_bytes(drive_free)),
                        ],
                    ),
                    # Games table with images, sortable by size (default)
                    Table(
                        columns=columns,
                        data=table_data,
                        empty_message="No games in this library",
                        sortable=True,
                        default_sort_key="size",
                        default_sort_desc=True,
                    ),
                ],
            ),
        ],
    )
