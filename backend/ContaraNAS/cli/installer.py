import json
from pathlib import Path
import platform
import shutil
import subprocess
import zipfile

from backend.ContaraNAS.core.utils import get_logger
from backend.ContaraNAS.modules import module_loader
import click


logger = get_logger(__name__)


class ModuleInstaller:
    """Handles module installation and removal"""

    def __init__(self):
        # Find the modules directory
        contaranas_dir = Path(__file__).parent.parent
        self.modules_dir = contaranas_dir / "modules"
        self.community_dir = self.modules_dir / "community"

        # Ensure community directory exists
        self.community_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_input(module_path: Path) -> str | None:
        """Validate module path"""
        if not module_path.exists():
            return f"❌ Error: Module file not found: {module_path}"

        if module_path.suffix != ".zip":
            return "❌ Error: Module must be a .zip file"

        return None

    def _perform_installation(self, module_path: Path, temp_dir: Path) -> bool:
        """Perform the actual installation"""
        # Extract zip
        with zipfile.ZipFile(module_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Load and validate metadata
        metadata = self._load_metadata(temp_dir)
        if not metadata:
            return False

        module_id = metadata["name"]

        # Display module info
        self._display_module_info(metadata)

        # Validate backend structure
        if not self._validate_backend_structure(temp_dir):
            return False

        # Check platform compatibility
        if not self._check_platform_compatibility(metadata):
            return False

        # Install dependencies
        if not self._install_dependencies(metadata):
            click.secho("⚠️  Warning: Some dependencies failed to install", fg="yellow")

        # Install the module
        target_dir = self.community_dir / module_id

        if target_dir.exists():
            click.secho(
                f"⚠️  Module '{module_id}' already exists. Overwriting...", fg="yellow"
            )
            shutil.rmtree(target_dir)

        # Copy backend directory as module root
        backend_dir = temp_dir / "backend"
        shutil.copytree(backend_dir, target_dir)

        # Copy module.json into the module directory
        module_json = temp_dir / "module.json"
        shutil.copy2(module_json, target_dir / "module.json")

        click.secho(f"✅ Backend installed to: {target_dir}", fg="green")
        click.secho(f"✅ Module '{module_id}' installed successfully!", fg="green", bold=True)
        click.echo()
        click.secho("🔄 Restart ContaraNAS to activate the module.", fg="cyan")

        return True

    def install(self, module_path: str) -> bool:
        """Install a module from a zip file"""
        module_path = Path(module_path)

        # Validate input
        validation_error = self._validate_input(module_path)
        if validation_error:
            click.secho(validation_error, fg="red")
            return False

        click.echo(f"📦 Installing module from {module_path.name}...")

        # Extract to temp directory
        temp_dir = self.community_dir / ".temp_install"
        temp_dir.mkdir(exist_ok=True)

        try:
            return self._perform_installation(module_path, temp_dir)
        except Exception as e:
            click.secho(f"❌ Installation failed: {e}", fg="red")
            logger.error(f"Module installation failed: {e}", exc_info=True)
            return False
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def uninstall(self, module_id: str) -> bool:
        """Uninstall a community module"""
        target_dir = self.community_dir / module_id

        if not target_dir.exists():
            click.secho(f"❌ Error: Module '{module_id}' not found", fg="red")
            return False

        click.echo(f"🗑️  Uninstalling module: {module_id}")

        try:
            shutil.rmtree(target_dir)

            click.secho(f"✅ Module '{module_id}' uninstalled successfully!", fg="green", bold=True)
            click.echo()
            click.secho("🔄 Restart ContaraNAS to complete removal.", fg="cyan")

            return True

        except Exception as e:
            click.secho(f"❌ Uninstallation failed: {e}", fg="red")
            logger.error(f"Module uninstallation failed: {e}", exc_info=True)
            return False

    def list_modules(self, source_filter: str = "all") -> None:
        """List all installed modules"""
        click.echo()
        click.secho("📦 Installed Modules:", bold=True)
        click.echo()

        # Discover modules
        discovered = module_loader.discover()

        if not discovered:
            click.secho("   No modules found.", fg="yellow")
            return

        # Group by source
        builtin = []
        community = []

        for metadata, _ in discovered.values():
            if metadata.source == "builtin":
                builtin.append(metadata)
            else:
                community.append(metadata)

        # Print based on filter
        if source_filter in ("all", "builtin") and builtin:
            click.secho("Built-in Modules:", fg="cyan", bold=True)
            for metadata in builtin:
                self._print_module_entry(metadata)
            click.echo()

        if source_filter in ("all", "community") and community:
            click.secho("Community Modules:", fg="magenta", bold=True)
            for metadata in community:
                self._print_module_entry(metadata)
            click.echo()

        if source_filter == "all":
            total = len(builtin) + len(community)
            click.secho(
                f"Total: {total} modules ({len(builtin)} builtin, {len(community)} community)",
                fg="white",
            )

    @staticmethod
    def _load_metadata(temp_dir: Path) -> dict | None:
        """Load and validate module.json"""
        module_json = temp_dir / "module.json"

        if not module_json.exists():
            click.secho("❌ Error: module.json not found in package", fg="red")
            return None

        try:
            with Path(module_json).open() as f:
                metadata = json.load(f)

            if "name" not in metadata:
                click.secho("❌ Error: 'name' field missing in module.json", fg="red")
                return None

            return metadata

        except json.JSONDecodeError as e:
            click.secho(f"❌ Error: Invalid module.json: {e}", fg="red")
            return None

    @staticmethod
    def _display_module_info(metadata: dict) -> None:
        """Display module information"""
        click.secho(
            f"📋 Module: {metadata.get('displayName', metadata['name'])} "
            f"v{metadata.get('version', '?')}",
            fg="cyan",
        )
        click.echo(f"   Author: {metadata.get('author', 'Unknown')}")
        click.echo(f"   Description: {metadata.get('description', 'No description')}")

    @staticmethod
    def _validate_backend_structure(temp_dir: Path) -> bool:
        """Validate that the module has required backend structure"""
        backend_dir = temp_dir / "backend"

        if not backend_dir.exists():
            click.secho("❌ Error: backend/ directory not found in package", fg="red")
            return False

        init_file = backend_dir / "__init__.py"
        if not init_file.exists():
            click.secho("❌ Error: backend/__init__.py not found in package", fg="red")
            return False

        return True

    @staticmethod
    def _check_platform_compatibility(metadata: dict) -> bool:
        """Check if module is compatible with current platform"""
        supported_platforms = metadata.get("platforms", [])

        if not supported_platforms:
            return True  # No restrictions

        current_platform = platform.system().lower()

        if current_platform not in supported_platforms:
            click.secho(f"❌ Error: Module not compatible with {current_platform}", fg="red")
            click.secho(f"   Supported platforms: {', '.join(supported_platforms)}", fg="yellow")
            return False

        return True

    def _install_dependencies(self, metadata: dict) -> bool:
        """Install Python dependencies for the module"""
        backend_config = metadata.get("backend", {})
        dependencies = backend_config.get("dependencies", {})
        platform_deps = backend_config.get("platform_dependencies", {})

        if not dependencies and not platform_deps:
            click.echo("   No backend dependencies to install")
            return True

        click.echo()
        click.secho("📥 Installing backend dependencies...", fg="cyan")

        success = True

        # Install common dependencies
        for package, version_spec in dependencies.items():
            spec = f"{package}{version_spec}" if version_spec else package
            if not self._install_package(spec):
                success = False

        # Install platform-specific dependencies
        current_platform = platform.system().lower()
        if current_platform in platform_deps:
            for package in platform_deps[current_platform]:
                if not self._install_package(package):
                    success = False

        return success

    @staticmethod
    def _install_package(package: str) -> bool:
        """Install a Python package with uv"""
        click.echo(f"   Installing {package}...", nl=False)

        try:
            subprocess.run(
                ["uv", "pip", "install", package],
                capture_output=True,
                text=True,
                check=True,
            )
            click.secho(" ✓", fg="green")
            return True
        except subprocess.CalledProcessError as e:
            click.secho(" ✗", fg="red")
            logger.error(f"Failed to install {package}: {e.stderr}")
            return False

    @staticmethod
    def _print_module_entry(metadata) -> None:
        """Print a single module entry"""
        click.echo(f"  • {click.style(metadata.name, fg='white', bold=True)} ", nl=False)
        click.echo(f"({click.style(metadata.id, fg='bright_black')}) ", nl=False)
        click.echo(f"- v{metadata.version}")
        click.echo(f"    {metadata.description}")
        if metadata.source == "community":
            click.echo(f"    Author: {click.style(metadata.author, fg='bright_black')}")
