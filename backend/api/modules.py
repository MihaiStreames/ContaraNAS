from fastapi import APIRouter, HTTPException

from backend.core.utils import get_logger
from backend.modules.steam import SteamModule

logger = get_logger(__name__)
router = APIRouter()

# Registry of available modules
AVAILABLE_MODULES = {
    'steam': SteamModule,
}


@router.get("/")
async def get_available_modules():
    """Get list of available modules with their tile data"""
    modules = []

    for module_name, module_class in AVAILABLE_MODULES.items():
        try:
            module_instance = module_class()

            module_info = module_instance.get_module_info()
            tile_data = module_instance.get_tile_data()

            modules.append({
                **module_info,
                "tile_data": tile_data
            })

        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            # Add a basic error module entry
            modules.append({
                "name": module_name,
                "title": module_name.capitalize(),
                "description": f"Error loading module: {str(e)}",
                "tile_data": {},
                "error": True
            })

    return {"modules": modules}


@router.get("/{module_name}")
async def get_module_info(module_name: str):
    """Get detailed info for a specific module"""
    if module_name not in AVAILABLE_MODULES:
        raise HTTPException(status_code=404, detail="Module not found")

    try:
        module_class = AVAILABLE_MODULES[module_name]
        module_instance = module_class()

        return {
            **module_instance.get_module_info(),
            "tile_data": module_instance.get_tile_data()
        }

    except Exception as e:
        logger.error(f"Error getting info for module {module_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
