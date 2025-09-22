#!/usr/bin/env bash
set -e

# Format with black
black ContaraNAS/

# Lint & sort imports with ruff
ruff check ContaraNAS/ --fix --unsafe-fixes