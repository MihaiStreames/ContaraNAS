"""Modal views for the Steam module"""

from ContaraNAS.core.ui import (
    Grid,
    Modal,
    Progress,
    Stack,
    Stat,
    StatCard,
    Table,
    TableColumn,
    Text,
)

from .helpers import format_bytes


def build_games_modal(games: list[dict]) -> Modal:
    """Build the games list modal"""
    if not games:
        return Modal(
            id="steam_games",
            title="Steam Games",
            size="lg",
            children=[Text(content="No games found", variant="muted")],
        )

    # Summary stats
    total_size = sum(g.get("total_size", 0) for g in games)
    sum(1 for g in games if g.get("install_state") in ["downloading", "updating"])
    installed = sum(1 for g in games if g.get("install_state") == "installed")

    # Build game table
    columns = [
        TableColumn(key="name", label="Game", width="40%"),
        TableColumn(key="size", label="Size", align="right"),
        TableColumn(key="status", label="Status", align="center"),
    ]

    # Format game data for table
    table_data = []
    for game in sorted(games, key=lambda g: g.get("name", "")):
        state = game.get("install_state", "unknown")

        table_data.append(
            {
                "name": game.get("name", "Unknown"),
                "size": format_bytes(game.get("total_size", 0)),
                "status": state.capitalize(),
            }
        )

    return Modal(
        id="steam_games",
        title=f"Steam Games ({len(games)})",
        size="lg",
        children=[
            Stack(
                direction="vertical",
                gap="4",
                children=[
                    Grid(
                        columns=3,
                        gap="4",
                        children=[
                            StatCard(label="Total Games", value=str(len(games)), icon="Gamepad2"),
                            StatCard(
                                label="Installed",
                                value=str(installed),
                                icon="CheckCircle",
                                color="success",
                            ),
                            StatCard(
                                label="Total Size",
                                value=format_bytes(total_size),
                                icon="HardDrive",
                            ),
                        ],
                    ),
                    Table(columns=columns, data=table_data, empty_message="No games installed"),
                ],
            ),
        ],
    )


def build_libraries_modal(libraries: list[dict]) -> Modal:
    """Build the libraries list modal"""
    if not libraries:
        return Modal(
            id="steam_libraries",
            title="Steam Libraries",
            size="md",
            children=[Text(content="No libraries found", variant="muted")],
        )

    library_cards = []
    for lib in libraries:
        path = lib.get("path", "Unknown")
        game_count = lib.get("game_count", 0)
        total_size = lib.get("total_size", 0)
        drive_total = lib.get("drive_total", 0)
        drive_used = lib.get("drive_used", 0)
        drive_free = lib.get("drive_free", 0)

        usage_percent = (drive_used / drive_total * 100) if drive_total > 0 else 0
        color = "success" if usage_percent < 70 else "warning" if usage_percent < 90 else "error"

        library_cards.append(
            Stack(
                direction="vertical",
                gap="2",
                children=[
                    Text(content=path, variant="body"),
                    Grid(
                        columns=3,
                        gap="2",
                        children=[
                            Stat(label="Games", value=str(game_count)),
                            Stat(label="Steam Size", value=format_bytes(total_size)),
                            Stat(label="Free Space", value=format_bytes(drive_free)),
                        ],
                    ),
                    Progress(
                        value=usage_percent,
                        max=100,
                        label="Drive Usage",
                        sublabel=f"{format_bytes(drive_used)} / {format_bytes(drive_total)}",
                        color=color,
                    ),
                ],
            )
        )

    return Modal(
        id="steam_libraries",
        title=f"Steam Libraries ({len(libraries)})",
        size="md",
        children=[Stack(direction="vertical", gap="4", children=library_cards)],
    )
