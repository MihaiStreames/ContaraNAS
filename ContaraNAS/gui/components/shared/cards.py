from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from nicegui import ui


@contextmanager
def module_card(
    width: str = "w-72",
    min_height: str = "min-h-[180px]",
    padding: str = "p-4",
) -> Generator[ui.card]:
    """Base card container for module tiles

    Usage::

        with module_card(
            width="w-96", min_height="min-h-[240px]", padding="p-6"
        ) as card:
            ui.label("Content goes here")
    """
    with ui.card().classes(f"{width} {min_height} {padding}") as card:
        yield card


@contextmanager
def card_header(
    title: str,
    status_text: str | None = None,
    status_color: str = "grey",
) -> Generator[dict[str, Any]]:
    """Standard card header with title and optional status badge

    Usage::

        with card_header("My Module", "Running", "positive") as refs:
            pass  # Header is rendered
        # Later: refs["badge"].set_text("Stopped")
    """
    refs: dict[str, Any] = {}

    with ui.row().classes("w-full items-center justify-between mb-4"):
        refs["title"] = ui.label(title).classes("text-lg font-bold")

        if status_text:
            refs["badge"] = ui.badge(status_text, color=status_color)

    yield refs


@contextmanager
def card_footer_buttons(
    on_enable: Callable | None = None,
    on_disable: Callable | None = None,
    enabled: bool = False,
) -> Generator[dict[str, ui.button]]:
    """Standard enable/disable button footer for module cards"""
    refs: dict[str, ui.button] = {}

    with ui.row().classes("w-full justify-end gap-2"):
        refs["enable"] = ui.button(
            "Enable",
            icon="play_arrow",
            on_click=on_enable,
        ).props("size=sm color=positive")

        refs["disable"] = ui.button(
            "Disable",
            icon="stop",
            on_click=on_disable,
        ).props("size=sm color=warning")

        # Set initial visibility
        refs["enable"].set_visibility(not enabled)
        refs["disable"].set_visibility(enabled)

    yield refs


@contextmanager
def clickable_section(
    on_click: Callable,
    hover_bg: str = "hover:bg-gray-50",
) -> Generator[ui.column]:
    """Clickable container section for interactive list items

    Usage::

        with clickable_section(lambda: open_modal(item_id)):
            ui.label(item.name)
            ui.label(item.description)
    """
    with (
        ui.column()
        .classes(f"w-full mb-3 p-2 border rounded cursor-pointer {hover_bg}")
        .on("click", on_click)
    ) as container:
        yield container


@contextmanager
def bordered_section(
    padding: str = "p-3",
    margin: str = "mb-3",
) -> Generator[ui.column]:
    """Bordered container for grouping related content

    Usage::

        with bordered_section():
            ui.label("Section Title").classes("font-bold")
            ui.label("Section content...")
    """
    with ui.column().classes(f"w-full border border-black rounded {padding} {margin}") as section:
        yield section


@contextmanager
def info_section(
    title: str | None = None,
    collapsible: bool = False,
) -> Generator[ui.column]:
    """Information section with optional title and collapse

    Usage::

        with info_section("Details", collapsible=True):
            ui.label("Detailed information...")
    """
    if collapsible and title:
        with ui.expansion(title).classes("w-full"):
            with ui.column().classes("w-full") as content:
                yield content
    else:
        with ui.column().classes("w-full") as section:
            if title:
                ui.label(title).classes("text-sm font-semibold mb-2")
            yield section


@contextmanager
def tab_container(
    tabs: list[str],
    default_tab: str | None = None,
) -> Generator[dict[str, Any]]:
    """Tabbed container component

    Usage::

        with tab_container(["CPU", "Memory", "Disks"]) as refs:
            with refs["panels"]:
                with ui.tab_panel(refs["tabs"]["CPU"]):
                    render_cpu_content()
    """
    refs: dict[str, Any] = {"tabs": {}, "panels": None, "tabs_element": None}

    default = default_tab or tabs[0] if tabs else None

    with ui.tabs().classes("w-full") as tabs_element:
        refs["tabs_element"] = tabs_element
        for tab_name in tabs:
            refs["tabs"][tab_name] = ui.tab(tab_name)

    # Set default tab
    default_tab_ref = refs["tabs"].get(default) if default else None

    with ui.tab_panels(tabs_element, value=default_tab_ref).classes("w-full") as panels:
        refs["panels"] = panels
        yield refs
