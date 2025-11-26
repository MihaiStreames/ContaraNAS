from pydantic import BaseModel


class ModuleVersion(BaseModel):
    """A specific version of a module"""

    version: str
    min_backend_version: str
    platforms: list[str]
    changelog: str
    published_at: str
    size_bytes: int
    dependencies: dict[str, dict | list] = {}


class ModuleSummary(BaseModel):
    """Module info for registry listing"""

    id: str
    display_name: str
    short_description: str
    author: str
    category: str
    tags: list[str]
    icon_url: str | None
    latest_version: str
    versions: list[str]


class ModuleDetail(BaseModel):
    """Full module information"""

    id: str
    display_name: str
    description: str
    short_description: str
    author: str
    license: str
    repository: str | None
    category: str
    tags: list[str]
    icon_url: str | None
    versions: list[ModuleVersion]


class RegistryResponse(BaseModel):
    """Response for GET /registry"""

    checksum: str
    modules: dict[str, ModuleSummary]


class ModuleResponse(BaseModel):
    """Response for GET /modules/{id}"""

    module: ModuleDetail
