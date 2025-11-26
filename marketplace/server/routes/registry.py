import hashlib
import json

from fastapi import APIRouter, Query
from marketplace.server.config import config
from marketplace.server.models import ModuleSummary, RegistryResponse


router = APIRouter(tags=["registry"])


def load_registry() -> dict:
    """Load registry from JSON file"""
    if not config.REGISTRY_FILE.exists():
        return {"schema_version": 1, "modules": {}}

    with config.REGISTRY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def compute_checksum(data: dict) -> str:
    """Compute SHA256 checksum of modules data"""
    content = json.dumps(data, sort_keys=True).encode()
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def filter_by_backend_version(registry: dict, backend_version: str) -> dict[str, ModuleSummary]:
    """Filter modules compatible with the given backend version"""
    # Simple version comparison for now
    # Could use packaging library for proper semver

    filtered = {}

    for module_id, module_data in registry.get("modules", {}).items():
        compatible_versions = []

        for version_str, version_info in module_data.get("versions", {}).items():
            min_version = version_info.get("min_backend_version", "0.0.0")

            # Simple string comparison - works for x.y.z format
            if backend_version >= min_version:
                compatible_versions.append(version_str)

        if compatible_versions:
            # Sort versions descending
            compatible_versions.sort(reverse=True)

            filtered[module_id] = ModuleSummary(
                id=module_id,
                display_name=module_data.get("display_name", module_id),
                short_description=module_data.get("short_description", ""),
                author=module_data.get("author", "Unknown"),
                category=module_data.get("category", "other"),
                tags=module_data.get("tags", []),
                icon_url=f"/modules/{module_id}/icon" if module_data.get("has_icon") else None,
                latest_version=compatible_versions[0],
                versions=compatible_versions,
            )

    return filtered


@router.get("/registry", response_model=RegistryResponse)
async def get_registry(
    backend_version: str = Query(..., description="Backend version for compatibility filtering"),
):
    """Get the module registry filtered by backend version"""
    registry = load_registry()
    filtered_modules = filter_by_backend_version(registry, backend_version)

    checksum = compute_checksum(
        {"modules": {k: v.model_dump() for k, v in filtered_modules.items()}}
    )

    return RegistryResponse(
        checksum=checksum,
        modules=filtered_modules,
    )
