import os

from fastapi import APIRouter, HTTPException, Depends

from backend.core.utils import get_logger
from backend.modules.steam import SteamModule
from backend.modules.steam.manager.steam_game_manager import SteamGameManager

logger = get_logger(__name__)
router = APIRouter()


# Dependencies
def get_steam_module() -> SteamModule:
    """Dependency to get Steam module instance"""
    return SteamModule()


def get_steam_manager(steam_module: SteamModule = Depends(get_steam_module)) -> SteamGameManager:
    """Dependency to get Steam manager instance"""
    return SteamGameManager(steam_module.steam_path, steam_module.cache_dir)


@router.get("/tile-data")
async def get_steam_tile_data(steam_module: SteamModule = Depends(get_steam_module)):
    """Get quick data for the Steam dashboard tile"""
    try:
        return steam_module.get_tile_data()
    except Exception as e:
        logger.error(f"Error getting Steam tile data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/games")
async def get_steam_games(steam_manager: SteamGameManager = Depends(get_steam_manager)):
    """Get all Steam games"""
    try:
        steam_manager.load_games()
        games = steam_manager.serialize_games()
        return {"games": games, "count": len(games)}

    except Exception as e:
        logger.error(f"Error loading Steam games: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/games/{app_id}")
async def get_steam_game_details(app_id: str, steam_manager: SteamGameManager = Depends(get_steam_manager)):
    """Get detailed info for a specific Steam game"""
    try:
        steam_manager.load_games()

        # Find the game
        game = next((g for g in steam_manager.games if g.app_id == app_id), None)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        # Return detailed game data
        return {
            "app_id": game.app_id,
            "name": game.name,
            "location": game.library_path,
            "cover_image_url": game.cover_image_url,
            "store_page_url": game.store_page_url,
            "size_on_disk": game.size_on_disk,
            "dlc_size": game.dlc_size,
            "shader_cache_size": game.shader_cache_size,
            "workshop_content_size": game.workshop_content_size,
            "depots": game.depots
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting game details for {app_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_steam_cache(steam_manager: SteamGameManager = Depends(get_steam_manager)):
    """Force refresh of Steam game cache"""
    try:
        steam_manager.load_games()
        return {"message": "Steam cache refreshed", "game_count": len(steam_manager.games)}

    except Exception as e:
        logger.error(f"Error refreshing Steam cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cover/{app_id}")
async def get_game_cover(app_id: str):
    """Get game cover image path"""
    try:
        image_path = f"resources/images/steam/{app_id}.jpg"
        if os.path.exists(image_path):
            return {"image_path": image_path, "exists": True}
        else:
            return {"image_path": None, "exists": False}
    except Exception as e:
        logger.error(f"Error getting cover for {app_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
