import argparse
import json
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from backend.ContaraNAS.core.utils import get_logger
from backend.ContaraNAS.modules import module_loader

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

    def install(self, module_path: str) -> bool:
        """Install a module from a zip file"""
        module_path = Path(module_path)

        if not module_path.exists():
            print(f"❌ Error: Module file not found: {module_path}")
            return False

        if not module_path.suffix == ".zip":
            print(f"❌ Error: Module must be a .zip file")
            return False

        print(f"📦 Installing module from {module_path.name}...")

        # Extract to temp directory
        temp_dir = self.community_dir / ".temp_install"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Extract zip
            with zipfile.ZipFile(module_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Read module.json
            module_json = temp_dir / "module.json"
            if not module_json.exists():
                print("❌ Error: module.json not found in package")
                return False

            with open(module_json) as f:
                metadata = json.load(f)

            module_id = metadata.get("name")
            if not module_id:
                print("❌ Error: 'name' field missing in module.json")
                return False

            print(f"📋 Module: {metadata.get('displayName', module_id)} v{metadata.get('version', '?')}")
            print(f"   Author: {metadata.get('author', 'Unknown')}")

            # Check if backend code exists
            backend_dir = temp_dir / "backend"
            if not backend_dir.exists():
                print("❌ Error: backend/ directory not found in package")
                return False

            # Validate platform compatibility
            if not self._check_platform_compatibility(metadata):
                return False

            # Install backend dependencies
            if not self._install_backend_dependencies(metadata):
                print("⚠️  Warning: Some dependencies failed to install")

            # Copy backend code to community directory
            target_dir = self.community_dir / module_id

            if target_dir.exists():
                print(f"⚠️  Module '{module_id}' already exists. Overwriting...")
                shutil.rmtree(target_dir)

            # Copy module.json
            shutil.copy2(module_json, target_dir.parent / (module_id + "_module.json"))

            # Copy backend directory as module root
            shutil.copytree(backend_dir, target_dir)

            # Copy module.json into the module directory
            shutil.copy2(module_json, target_dir / "module.json")

            print(f"✅ Backend installed to: {target_dir}")
            print(f"✅ Module '{module_id}' installed successfully!")
            print(f"\n🔄 Restart ContaraNAS to activate the module.")

            return True

        except Exception as e:
            print(f"❌ Installation failed: {e}")
            logger.error(f"Module installation failed: {e}", exc_info=True)
            return False

        finally:
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def uninstall(self, module_id: str) -> bool:
        """Uninstall a community module"""
        target_dir = self.community_dir / module_id

        if not target_dir.exists():
            print(f"❌ Error: Module '{module_id}' not found")
            return False

        print(f"🗑️  Uninstalling module: {module_id}")

        try:
            shutil.rmtree(target_dir)

            # Remove module.json if it exists
            module_json = self.community_dir.parent / (module_id + "_module.json")
            if module_json.exists():
                module_json.unlink()

            print(f"✅ Module '{module_id}' uninstalled successfully!")
            print(f"\n🔄 Restart ContaraNAS to complete removal.")

            return True

        except Exception as e:
            print(f"❌ Uninstallation failed: {e}")
            logger.error(f"Module uninstallation failed: {e}", exc_info=True)
            return False

    @staticmethod
    def list_modules() -> None:
        """List all installed modules"""

        print("\n📦 Installed Modules:\n")

        # Discover modules
        discovered = module_loader.discover()

        if not discovered:
            print("   No modules found.")
            return

        # Group by source
        builtin = []
        community = []

        for module_id, (metadata, _) in discovered.items():
            if metadata.source == "builtin":
                builtin.append(metadata)
            else:
                community.append(metadata)

        # Print builtin
        if builtin:
            print("Built-in Modules:")
            for metadata in builtin:
                print(f"  • {metadata.name} ({metadata.id}) - v{metadata.version}")

        # Print community
        if community:
            print("\nCommunity Modules:")
            for metadata in community:
                print(f"  • {metadata.name} ({metadata.id}) - v{metadata.version}")
                print(f"    Author: {metadata.author}")

        print()

    @staticmethod
    def _check_platform_compatibility(metadata: dict) -> bool:
        """Check if module is compatible with current platform"""
        supported_platforms = metadata.get("platforms", [])

        if not supported_platforms:
            return True  # No restrictions

        current_platform = platform.system().lower()

        if current_platform not in supported_platforms:
            print(f"❌ Error: Module not compatible with {current_platform}")
            print(f"   Supported platforms: {', '.join(supported_platforms)}")
            return False

        return True

    def _install_backend_dependencies(self, metadata: dict) -> bool:
        """Install Python dependencies for the module"""
        backend_config = metadata.get("backend", {})
        dependencies = backend_config.get("dependencies", {})
        platform_deps = backend_config.get("platform_dependencies", {})

        if not dependencies and not platform_deps:
            print("   No backend dependencies to install")
            return True

        print("\n📥 Installing backend dependencies...")

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
        print(f"   Installing {package}...", end=" ")

        try:
            result = subprocess.run(
                ["uv", "pip", "install", package],
                capture_output=True,
                text=True,
                check=True
            )
            print("✓")
            return True
        except subprocess.CalledProcessError as e:
            print("✗")
            logger.error(f"Failed to install {package}: {e.stderr}")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ContaraNAS Module Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a module")
    install_parser.add_argument("path", help="Path to module .zip file")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a module")
    uninstall_parser.add_argument("name", help="Module name/ID")

    # List command
    subparsers.add_parser("list", help="List installed modules")

    # Module subcommand (groups install/uninstall/list)
    module_parser = subparsers.add_parser("module", help="Module management commands")
    module_subparsers = module_parser.add_subparsers(dest="module_command")

    # module install
    mod_install = module_subparsers.add_parser("install", help="Install a module")
    mod_install.add_argument("path", help="Path to module .zip file")

    # module uninstall
    mod_uninstall = module_subparsers.add_parser("uninstall", help="Uninstall a module")
    mod_uninstall.add_argument("name", help="Module name/ID")

    # module list
    module_subparsers.add_parser("list", help="List installed modules")

    args = parser.parse_args()

    installer = ModuleInstaller()

    # Handle commands
    if args.command == "module":
        if args.module_command == "install":
            return 0 if installer.install(args.path) else 1
        elif args.module_command == "uninstall":
            return 0 if installer.uninstall(args.name) else 1
        elif args.module_command == "list":
            installer.list_modules()
            return 0
        else:
            module_parser.print_help()
            return 1
    elif args.command == "install":
        return 0 if installer.install(args.path) else 1
    elif args.command == "uninstall":
        return 0 if installer.uninstall(args.name) else 1
    elif args.command == "list":
        installer.list_modules()
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
