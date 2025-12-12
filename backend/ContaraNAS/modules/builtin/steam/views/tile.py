from ContaraNAS.core.ui import Alert
from ContaraNAS.core.ui import SegmentedProgress
from ContaraNAS.core.ui import SegmentedProgressSegment
from ContaraNAS.core.ui import Stack
from ContaraNAS.core.ui import Stat
from ContaraNAS.core.ui import Text
from ContaraNAS.core.ui import Tile

from .helpers import format_bytes
from .helpers import get_mountpoint


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
            content=[
                Alert(
                    message="Steam is not installed on this system",
                    variant="warning",
                )
            ],
            actions=[],
        )

    # Build library cards
    library_content = []

    for lib in libraries:
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

        # Build segments for the segmented progress bar (with sizes in labels)
        segments = []
        if games_size > 0:
            segments.append(
                SegmentedProgressSegment(
                    value=games_size,
                    color="var(--color-primary)",
                    label=f"Games ({format_bytes(games_size)})",
                )
            )
        if shader_size > 0:
            segments.append(
                SegmentedProgressSegment(
                    value=shader_size,
                    color="#9333ea",  # Purple
                    label=f"Shaders ({format_bytes(shader_size)})",
                )
            )
        if workshop_size > 0:
            segments.append(
                SegmentedProgressSegment(
                    value=workshop_size,
                    color="#14b8a6",  # Teal
                    label=f"Workshop ({format_bytes(workshop_size)})",
                )
            )
        if other_used > 0:
            segments.append(
                SegmentedProgressSegment(
                    value=other_used,
                    color="var(--text-muted)",
                    label=f"Other ({format_bytes(other_used)})",
                )
            )

        # Get mountpoint for display (e.g., "C:/" or "/home")
        mountpoint = get_mountpoint(path)

        action = open_library_actions.get(path)

        library_content.append(
            Stack(
                direction="vertical",
                gap="2",
                on_click=action,
                children=[
                    Stack(
                        direction="horizontal",
                        gap="2",
                        justify="between",
                        align="center",
                        children=[
                            Text(content=mountpoint),
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
                        show_legend=True,
                    ),
                    Text(
                        content=f"{format_bytes(drive_used)} / {format_bytes(drive_total)}",
                        variant="muted",
                    ),
                ],
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
        stats=stats,
        content=(
            [Stack(direction="vertical", gap="3", children=library_content)]
            if library_content
            else None
        ),
        actions=[],
    )
