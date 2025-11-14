from nicegui import ui

from ContaraNAS.gui.utils import format_bytes


def calculate_drive_percentages(library: dict) -> dict[str, float]:
    """Calculate percentage breakdown of drive usage"""
    games_size = library["total_games_size"]
    shader_size = library["total_shader_size"]
    workshop_size = library["total_workshop_size"]
    total_steam_size = library["total_size"]

    drive_total = library["drive_total"]
    drive_used = library["drive_used"]

    if drive_total == 0:
        return {"games": 0, "shaders": 0, "workshop": 0, "non_steam": 0}

    # Calculate non-Steam files
    non_steam_size = max(0, drive_used - total_steam_size)

    return {
        "games": (games_size / drive_total) * 100,
        "shaders": (shader_size / drive_total) * 100,
        "workshop": (workshop_size / drive_total) * 100,
        "non_steam": (non_steam_size / drive_total) * 100,
        "games_size": games_size,
        "shader_size": shader_size,
        "workshop_size": workshop_size,
        "non_steam_size": non_steam_size,
    }


def generate_progress_bar_html(percentages: dict[str, float]) -> str:
    """Generate HTML for the segmented progress bar"""
    return f"""
    <div style="
        width: 100%;
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
        display: flex;
        position: relative;
    ">
        <div style="
            background-color: #1976d2;
            width: {percentages['games']}%;
            height: 100%;
        " title="Games: {format_bytes(int(percentages['games_size']))}"></div>
        <div style="
            background-color: #388e3c;
            width: {percentages['shaders']}%;
            height: 100%;
        " title="Shaders: {format_bytes(int(percentages['shader_size']))}"></div>
        <div style="
            background-color: #f57c00;
            width: {percentages['workshop']}%;
            height: 100%;
        " title="Workshop: {format_bytes(int(percentages['workshop_size']))}"></div>
        <div style="
            background-color: #fdd835;
            width: {percentages['non_steam']}%;
            height: 100%;
        " title="Non-Steam files: {format_bytes(int(percentages['non_steam_size']))}"></div>
    </div>
    """


def render_library_header(path: str, game_count: int) -> None:
    """Render the library header with path and game count"""
    with ui.row().classes("w-full justify-between items-center mb-1"):
        ui.label(f"{path}").classes("text-xs font-mono text-gray-600")
        ui.label(f"{game_count} games").classes("text-xs font-bold")


def render_progress_section(library: dict) -> None:
    """Render the progress bar section"""
    drive_total = library["drive_total"]
    total_steam_size = library["total_size"]

    if drive_total > 0:
        percentages = calculate_drive_percentages(library)

        with ui.row().classes("w-full items-center gap-2"):
            # Progress bar
            progress_html = generate_progress_bar_html(percentages)
            ui.html(progress_html, sanitize=False).classes("flex-1")

            # Total Steam size label
            ui.label(f"{format_bytes(total_steam_size)}").classes("text-xs font-bold min-w-fit")


def render_color_legend(library: dict) -> None:
    """Render the color legend showing breakdown of sizes"""
    games_size = library["total_games_size"]
    shader_size = library["total_shader_size"]
    workshop_size = library["total_workshop_size"]

    # Calculate non-Steam size
    drive_used = library["drive_used"]
    total_steam_size = library["total_size"]
    non_steam_size = max(0, drive_used - total_steam_size)

    with ui.row().classes("w-full gap-4 mt-1 text-xs"):
        ui.html(f'<span style="color: #1976d2;">■</span> Games: {format_bytes(games_size)}', sanitize=False)
        ui.html(f'<span style="color: #388e3c;">■</span> Shaders: {format_bytes(shader_size)}', sanitize=False)
        ui.html(f'<span style="color: #f57c00;">■</span> Workshop: {format_bytes(workshop_size)}', sanitize=False)
        if non_steam_size > 0:
            ui.html(f'<span style="color: #fdd835;">■</span> Other: {format_bytes(non_steam_size)}', sanitize=False)


def render_drive_info(library: dict) -> None:
    """Render drive usage information"""
    drive_total = library["drive_total"]
    drive_free = library["drive_free"]

    if drive_total > 0:
        free_percentage = (drive_free / drive_total) * 100
        ui.label(f"Drive: {format_bytes(drive_free)} free ({free_percentage:.1f}%)").classes(
            "text-xs text-gray-500"
        )
