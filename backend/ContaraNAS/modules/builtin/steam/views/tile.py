"""Tile view for the Steam module"""

from ContaraNAS.core.ui import (
    Alert,
    Badge,
    Button,
    SegmentedProgress,
    SegmentedProgressSegment,
    Stack,
    Stat,
    Text,
    Tile,
)

from .helpers import format_bytes


def build_tile(
    status: str,
    total_games: int,
    total_libraries: int,
    total_size: int,
    libraries: list[dict],
    open_library_actions: dict,  # {library_path: action}
) -> Tile:
    """Build the dashboard tile UI component with inline libraries"""
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

    # Build library cards for inline display (max 2 visible, rest scrollable)
    library_content = []

    for lib in libraries[:2]:  # Show first 2 inline
        path = lib.get("path", "Unknown")
        game_count = lib.get("game_count", 0)
        games_size = lib.get("total_games_size", 0)
        shader_size = lib.get("total_shader_size", 0)
        workshop_size = lib.get("total_workshop_size", 0)
        drive_total = lib.get("drive_total", 0)
        drive_used = lib.get("drive_used", 0)

        # Calculate "other" usage (non-Steam files on the drive)
        steam_total = games_size + shader_size + workshop_size
        other_used = drive_used - steam_total if drive_used > steam_total else 0

        # Build segments for the segmented progress bar
        segments = []
        if games_size > 0:
            segments.append(
                SegmentedProgressSegment(
                    value=games_size, color="var(--color-primary)", label="Games"
                )
            )
        if shader_size > 0:
            segments.append(
                SegmentedProgressSegment(
                    value=shader_size,
                    color="#9333ea",
                    label="Shaders",  # Purple
                )
            )
        if workshop_size > 0:
            segments.append(
                SegmentedProgressSegment(
                    value=workshop_size,
                    color="#14b8a6",
                    label="Workshop",  # Teal
                )
            )
        if other_used > 0:
            segments.append(
                SegmentedProgressSegment(value=other_used, color="var(--text-muted)", label="Other")
            )

        # Get a short display name for the path
        short_path = path.split("/")[-1] if "/" in path else path
        if len(short_path) > 20:
            short_path = "..." + short_path[-17:]

        action = open_library_actions.get(path)

        library_content.append(
            Stack(
                direction="vertical",
                gap="1",
                children=[
                    Stack(
                        direction="horizontal",
                        gap="2",
                        justify="between",
                        align="center",
                        children=[
                            Button(
                                label=short_path,
                                variant="ghost",
                                size="sm",
                                on_click=action,
                            ),
                            Text(
                                content=f"{game_count} games",
                                variant="muted",
                            ),
                        ],
                    ),
                    SegmentedProgress(
                        segments=segments,
                        max=drive_total,
                        size="sm",
                    ),
                    Text(
                        content=f"{format_bytes(drive_used)} / {format_bytes(drive_total)}",
                        variant="muted",
                    ),
                ],
            )
        )

    # Add "more libraries" indicator if there are more than 2
    if len(libraries) > 2:
        library_content.append(
            Text(
                content=f"+ {len(libraries) - 2} more libraries",
                variant="muted",
            )
        )

    # Header stats
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
        content=[Stack(direction="vertical", gap="3", children=library_content)]
        if library_content
        else None,
        actions=[],
    )
