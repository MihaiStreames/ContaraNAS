import hashlib

from ContaraNAS.core.ui import (
    Grid,
    Modal,
    Stack,
    Stat,
    Table,
    TableColumn,
    Text,
)

from .helpers import format_bytes


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

    # Short path for display
    short_path = path.split("/")[-1] if "/" in path else path

    if not library_games:
        return Modal(
            id=modal_id,
            title=f"Library: {short_path}",
            size="lg",
            children=[Text(content="No games found in this library", variant="muted")],
        )

    # Library stats
    games_size = library.get("total_games_size", 0)
    drive_free = library.get("drive_free", 0)

    # Build game table - default sorted by size (largest first)
    columns = [
        TableColumn(key="name", label="Game", width="50%"),
        TableColumn(key="size", label="Size", align="right"),
        TableColumn(key="last_played", label="Last Played", align="right"),
    ]

    # Format game data for table, sorted by size descending
    table_data = []
    for game in sorted(library_games, key=lambda g: g.get("total_size", 0), reverse=True):
        last_played = game.get("last_played_date")
        if last_played:
            last_played_str = last_played if isinstance(last_played, str) else "—"
        else:
            last_played_str = "Never"

        table_data.append(
            {
                "name": game.get("name", "Unknown"),
                "size": format_bytes(game.get("total_size", 0)),
                "last_played": last_played_str,
            }
        )

    return Modal(
        id=modal_id,
        title=f"Library: {short_path}",
        size="lg",
        children=[
            Stack(
                direction="vertical",
                gap="4",
                children=[
                    # Summary stats
                    Grid(
                        columns=3,
                        gap="3",
                        children=[
                            Stat(label="Games", value=str(len(library_games))),
                            Stat(label="Total Size", value=format_bytes(games_size)),
                            Stat(label="Free Space", value=format_bytes(drive_free)),
                        ],
                    ),
                    # Games table
                    Table(
                        columns=columns,
                        data=table_data,
                        empty_message="No games in this library",
                    ),
                ],
            ),
        ],
    )
