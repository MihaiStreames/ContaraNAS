"""
ContaraNAS CLI entry point

Usage:
    python -m ContaraNAS module install <path>
    python -m ContaraNAS module uninstall <name>
    python -m ContaraNAS module list
"""

import sys

from backend.ContaraNAS.cli.module_commands import main

if __name__ == "__main__":
    sys.exit(main())
