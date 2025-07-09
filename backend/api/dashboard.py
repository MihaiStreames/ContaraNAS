import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.module_manager import ModuleManager
from backend.modules.steam import SteamModule

router = APIRouter()

# Global module manager
manager = ModuleManager()

# Register modules
manager.register(SteamModule())

# WebSocket connections for real-time updates
connections = []


@router.get("/modules")
async def get_dashboard():
    """Get dashboard data for all modules"""
    return manager.get_dashboard_data()


@router.post("/modules/{name}/enable")
async def enable_module(name: str):
    """Enable a module"""
    await manager.enable_module(name)
    return {"message": f"Module {name} enabled"}


@router.post("/modules/{name}/disable")
async def disable_module(name: str):
    """Disable a module"""
    await manager.disable_module(name)
    return {"message": f"Module {name} disabled"}


@router.get("/modules/{name}/details")
async def get_module_details(name: str):
    """Get detailed data for modal popup"""
    details = manager.get_module_details(name)
    if details:
        return details
    return {"error": "Module not found"}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            # Send dashboard updates every 2 seconds
            data = manager.get_dashboard_data()
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        connections.remove(websocket)
