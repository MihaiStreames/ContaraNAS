from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dashboard import router as dashboard_router
from core.utils import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="NAS Manager API",
    version="1.0.0",
    description="Backend API for NAS Manager"
)

# CORS for Tauri app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "Healthy",
        "version": "1.0.0",
        "api": "NAS Manager"
    }


# Include routers
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting NAS Manager API server...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
