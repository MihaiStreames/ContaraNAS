"""
ContaraNAS CLI entry point

Usage:
    python -m ContaraNAS [command] [options]

Commands:
    server start              Start the API server
    module install <path>     Install a module
    module uninstall <name>   Uninstall a module
    module list               List installed modules
"""

from backend.ContaraNAS.cli import main


if __name__ == "__main__":
    main()
