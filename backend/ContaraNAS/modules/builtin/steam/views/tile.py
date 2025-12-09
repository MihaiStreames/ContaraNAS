"""Tile view for the Steam module"""

from ContaraNAS.core.ui import Alert, Badge, Button, Stat, Tile

from .helpers import format_bytes


def build_tile(
    status: str,
    total_games: int,
    total_libraries: int,
    total_size: int,
    open_games_action,
    open_libraries_action,
) -> Tile:
    """Build the dashboard tile UI component"""
    if status == "steam_not_found":
        return Tile(
            icon="Gamepad2",
            title="Steam",
            badge=Badge(text="Not Found", variant="warning"),
            content=[
                Alert(
                    message="Steam is not installed on this system",
                    variant="warning",
                )
            ],
            actions=[],
        )

    stats = [
        Stat(label="Games", value=str(total_games)),
        Stat(label="Libraries", value=str(total_libraries)),
    ]

    if total_size > 0:
        stats.append(Stat(label="Total Size", value=format_bytes(total_size)))

    return Tile(
        icon="Gamepad2",
        title="Steam",
        badge=Badge(text="Ready", variant="success") if status == "ready" else None,
        stats=stats,
        actions=[
            Button(label="Games", variant="secondary", on_click=open_games_action),
            Button(label="Libraries", variant="ghost", on_click=open_libraries_action),
        ],
    )
