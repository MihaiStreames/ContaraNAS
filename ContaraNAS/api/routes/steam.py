from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Query, status

from ContaraNAS.api.schemas import (
    SteamGameResponse,
    SteamLibraryGamesResponse,
    SteamLibraryResponse,
    SteamOverviewResponse,
)
from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.steam.constants import (
    SORT_BY_LAST_PLAYED,
    SORT_BY_NAME,
    SORT_BY_SIZE,
)

if TYPE_CHECKING:
    from ContaraNAS.core.module_manager import ModuleManager

logger = get_logger(__name__)


def create_steam_router(module_manager: "ModuleManager") -> APIRouter:
    """Create the Steam router with the module manager dependency"""

    router = APIRouter(prefix="/steam", tags=["steam"])

    def _get_steam_controller():
        """Helper to get the steam controller, raising if unavailable"""
        module = module_manager.modules.get("steam")

        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Steam module not found",
            )

        if not module.enable_flag:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Steam module is not enabled",
            )

        if not module.controller:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Steam controller not initialized",
            )

        return module.controller

    @router.get("/overview", response_model=SteamOverviewResponse)
    async def get_steam_overview() -> SteamOverviewResponse:
        """Get overview of all Steam libraries"""
        controller = _get_steam_controller()

        try:
            tile_data = await controller.get_tile_data()

            libraries = [
                SteamLibraryResponse(**lib) for lib in tile_data.get("libraries", [])
            ]

            return SteamOverviewResponse(
                libraries=libraries,
                total_games=tile_data.get("total_games", 0),
                total_libraries=tile_data.get("total_libraries", 0),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting Steam overview: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting Steam overview: {e!s}",
            ) from e

    @router.get("/libraries", response_model=list[SteamLibraryResponse])
    async def get_libraries() -> list[SteamLibraryResponse]:
        """Get list of all Steam libraries"""
        controller = _get_steam_controller()

        try:
            tile_data = await controller.get_tile_data()
            return [SteamLibraryResponse(**lib) for lib in tile_data.get("libraries", [])]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting Steam libraries: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting Steam libraries: {e!s}",
            ) from e

    @router.get("/libraries/{library_index}/games", response_model=SteamLibraryGamesResponse)
    async def get_library_games(
            library_index: int,
            sort_by: str = Query(
                default=SORT_BY_SIZE,
                description="Sort games by: size, name, or last_played",
            ),
            sort_desc: bool = Query(default=True, description="Sort in descending order"),
            limit: int = Query(default=0, ge=0, description="Limit number of results (0 = no limit)"),
            offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    ) -> SteamLibraryGamesResponse:
        """Get all games in a specific library by index"""
        controller = _get_steam_controller()

        try:
            library_paths = controller.library_service.get_library_paths()

            if library_index < 0 or library_index >= len(library_paths):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Library index {library_index} not found. Available: 0-{len(library_paths) - 1}",
                )

            library_path = library_paths[library_index]
            games_data = await controller.get_library_games(str(library_path))

            # Sort games
            games = _sort_games(games_data, sort_by, sort_desc)

            # Apply pagination
            if limit > 0:
                games = games[offset: offset + limit]
            elif offset > 0:
                games = games[offset:]

            game_responses = [SteamGameResponse(**game) for game in games]

            return SteamLibraryGamesResponse(
                library_path=str(library_path),
                games=game_responses,
                game_count=len(game_responses),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting library games: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting library games: {e!s}",
            ) from e

    @router.get("/games", response_model=list[SteamGameResponse])
    async def get_all_games(
            sort_by: str = Query(
                default=SORT_BY_SIZE,
                description="Sort games by: size, name, or last_played",
            ),
            sort_desc: bool = Query(default=True, description="Sort in descending order"),
            limit: int = Query(default=0, ge=0, description="Limit number of results (0 = no limit)"),
            offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    ) -> list[SteamGameResponse]:
        """Get all games across all libraries"""
        controller = _get_steam_controller()

        try:
            all_games = []

            for library_path in controller.library_service.get_library_paths():
                games_data = await controller.get_library_games(str(library_path))
                all_games.extend(games_data)

            # Sort games
            all_games = _sort_games(all_games, sort_by, sort_desc)

            # Apply pagination
            if limit > 0:
                all_games = all_games[offset: offset + limit]
            elif offset > 0:
                all_games = all_games[offset:]

            return [SteamGameResponse(**game) for game in all_games]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting all games: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting all games: {e!s}",
            ) from e

    @router.get("/games/{app_id}", response_model=SteamGameResponse)
    async def get_game_by_id(app_id: int) -> SteamGameResponse:
        """Get a specific game by its Steam App ID"""
        controller = _get_steam_controller()

        try:
            for library_path in controller.library_service.get_library_paths():
                games_data = await controller.get_library_games(str(library_path))

                for game in games_data:
                    if game["app_id"] == app_id:
                        return SteamGameResponse(**game)

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with App ID {app_id} not found",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting game {app_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting game: {e!s}",
            ) from e

    @router.get("/games/search/{query}", response_model=list[SteamGameResponse])
    async def search_games(
            query: str,
            limit: int = Query(default=20, ge=1, le=100, description="Maximum results to return"),
    ) -> list[SteamGameResponse]:
        """Search for games by name"""
        controller = _get_steam_controller()

        try:
            query_lower = query.lower()
            matching_games = []

            for library_path in controller.library_service.get_library_paths():
                games_data = await controller.get_library_games(str(library_path))

                for game in games_data:
                    if query_lower in game["name"].lower():
                        matching_games.append(game)

                        if len(matching_games) >= limit:
                            break

                if len(matching_games) >= limit:
                    break

            return [SteamGameResponse(**game) for game in matching_games]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error searching games: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching games: {e!s}",
            ) from e

    @router.get("/stats")
    async def get_steam_stats() -> dict:
        """Get Steam library statistics"""
        controller = _get_steam_controller()

        try:
            tile_data = await controller.get_tile_data()
            libraries = tile_data.get("libraries", [])

            total_games_size = sum(lib.get("total_games_size", 0) for lib in libraries)
            total_shader_size = sum(lib.get("total_shader_size", 0) for lib in libraries)
            total_workshop_size = sum(lib.get("total_workshop_size", 0) for lib in libraries)
            total_size = sum(lib.get("total_size", 0) for lib in libraries)
            total_drive_space = sum(lib.get("drive_total", 0) for lib in libraries)
            total_drive_free = sum(lib.get("drive_free", 0) for lib in libraries)

            return {
                "total_libraries": len(libraries),
                "total_games": tile_data.get("total_games", 0),
                "total_games_size_bytes": total_games_size,
                "total_games_size_gb": total_games_size / (1024 ** 3),
                "total_shader_size_bytes": total_shader_size,
                "total_shader_size_gb": total_shader_size / (1024 ** 3),
                "total_workshop_size_bytes": total_workshop_size,
                "total_workshop_size_gb": total_workshop_size / (1024 ** 3),
                "total_size_bytes": total_size,
                "total_size_gb": total_size / (1024 ** 3),
                "total_drive_space_bytes": total_drive_space,
                "total_drive_space_gb": total_drive_space / (1024 ** 3),
                "total_drive_free_bytes": total_drive_free,
                "total_drive_free_gb": total_drive_free / (1024 ** 3),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting Steam stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting Steam stats: {e!s}",
            ) from e

    @router.get("/largest-games", response_model=list[SteamGameResponse])
    async def get_largest_games(
            limit: int = Query(default=10, ge=1, le=50, description="Number of games to return"),
    ) -> list[SteamGameResponse]:
        """Get the largest games across all libraries"""
        controller = _get_steam_controller()

        try:
            all_games = []

            for library_path in controller.library_service.get_library_paths():
                games_data = await controller.get_library_games(str(library_path))
                all_games.extend(games_data)

            # Sort by total size descending
            all_games.sort(key=lambda g: g.get("total_size", 0), reverse=True)

            return [SteamGameResponse(**game) for game in all_games[:limit]]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting largest games: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting largest games: {e!s}",
            ) from e

    @router.get("/recently-played", response_model=list[SteamGameResponse])
    async def get_recently_played(
            limit: int = Query(default=10, ge=1, le=50, description="Number of games to return"),
    ) -> list[SteamGameResponse]:
        """Get recently played games"""
        controller = _get_steam_controller()

        try:
            all_games = []

            for library_path in controller.library_service.get_library_paths():
                games_data = await controller.get_library_games(str(library_path))
                # Only include games that have been played
                all_games.extend([g for g in games_data if g.get("last_played", 0) > 0])

            # Sort by last played descending
            all_games.sort(key=lambda g: g.get("last_played", 0), reverse=True)

            return [SteamGameResponse(**game) for game in all_games[:limit]]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting recently played games: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting recently played games: {e!s}",
            ) from e

    return router


def _sort_games(games: list[dict], sort_by: str, descending: bool) -> list[dict]:
    """Sort games by the specified field"""
    sort_key_map = {
        SORT_BY_SIZE: lambda g: g.get("total_size", 0),
        SORT_BY_NAME: lambda g: g.get("name", "").lower(),
        SORT_BY_LAST_PLAYED: lambda g: g.get("last_played", 0),
    }

    sort_key = sort_key_map.get(sort_by, sort_key_map[SORT_BY_SIZE])

    # For name sorting, ascending is typically preferred
    if sort_by == SORT_BY_NAME:
        descending = not descending

    return sorted(games, key=sort_key, reverse=descending)
