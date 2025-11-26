import hashlib
import json

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response
from marketplace.server.config import config
from marketplace.server.models import ModuleDetail, ModuleResponse, ModuleVersion


router = APIRouter(prefix="/modules", tags=["modules"])


def load_registry() -> dict:
    """Load registry from JSON file"""
    if not config.REGISTRY_FILE.exists():
        return {"schema_version": 1, "modules": {}}

    with open(config.REGISTRY_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_module_from_registry(module_id: str) -> dict | None:
    """Get a single module from registry"""
    registry = load_registry()
    return registry.get("modules", {}).get(module_id)


def filter_versions_by_backend(versions: dict, backend_version: str) -> list[ModuleVersion]:
    """Filter and convert versions compatible with backend"""
    compatible = []

    for version_str, version_info in versions.items():
        min_version = version_info.get("min_backend_version", "0.0.0")

        if backend_version >= min_version:
            compatible.append(
                ModuleVersion(
                    version=version_str,
                    min_backend_version=min_version,
                    platforms=version_info.get("platforms", ["linux", "windows"]),
                    changelog=version_info.get("changelog", ""),
                    published_at=version_info.get("published_at", ""),
                    size_bytes=version_info.get("size_bytes", 0),
                    dependencies=version_info.get("dependencies", {}),
                )
            )

    # Sort by version descending
    compatible.sort(key=lambda v: v.version, reverse=True)
    return compatible


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: str,
    backend_version: str = Query(..., description="Backend version for compatibility filtering"),
):
    """Get detailed information about a specific module"""
    module_data = get_module_from_registry(module_id)

    if not module_data:
        raise HTTPException(status_code=404, detail="Module not found")

    compatible_versions = filter_versions_by_backend(
        module_data.get("versions", {}),
        backend_version,
    )

    if not compatible_versions:
        raise HTTPException(
            status_code=404,
            detail="No compatible versions found for this backend version",
        )

    module = ModuleDetail(
        id=module_id,
        display_name=module_data.get("display_name", module_id),
        description=module_data.get("description", ""),
        short_description=module_data.get("short_description", ""),
        author=module_data.get("author", "Unknown"),
        license=module_data.get("license", "Unknown"),
        repository=module_data.get("repository"),
        category=module_data.get("category", "other"),
        tags=module_data.get("tags", []),
        icon_url=f"/modules/{module_id}/icon" if module_data.get("has_icon") else None,
        versions=compatible_versions,
    )

    return ModuleResponse(module=module)


@router.get("/{module_id}/versions/{version}/download")
async def download_module(module_id: str, version: str):
    """Download a module zip file"""
    module_data = get_module_from_registry(module_id)

    if not module_data:
        raise HTTPException(status_code=404, detail="Module not found")

    if version not in module_data.get("versions", {}):
        raise HTTPException(status_code=404, detail="Version not found")

    zip_path = config.MODULES_DIR / module_id / f"{version}.zip"

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Module file not found")

    # Compute checksum
    content = zip_path.read_bytes()
    checksum = hashlib.sha256(content).hexdigest()

    return Response(
        content=content,
        media_type="application/zip",
        headers={
            "X-Checksum-SHA256": checksum,
            "Content-Disposition": f"attachment; filename={module_id}-{version}.zip",
        },
    )


@router.get("/{module_id}/icon")
async def get_module_icon(module_id: str):
    """Get module icon"""
    module_data = get_module_from_registry(module_id)

    if not module_data:
        raise HTTPException(status_code=404, detail="Module not found")

    # Check for icon in module directory
    module_dir = config.MODULES_DIR / module_id

    for ext in ["png", "jpg", "jpeg", "svg"]:
        icon_path = module_dir / f"icon.{ext}"
        if icon_path.exists():
            return FileResponse(icon_path)

    raise HTTPException(status_code=404, detail="Icon not found")
