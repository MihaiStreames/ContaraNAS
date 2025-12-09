#!/usr/bin/env bash
set -euo pipefail

# Get the project root (parent of scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Cleaning project caches in $PROJECT_ROOT..."

# Python caches
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true

# Tool caches
find "$PROJECT_ROOT" -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Build artifacts
find "$PROJECT_ROOT" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

# Node caches
find "$PROJECT_ROOT" -type d -name ".svelte-kit" -exec rm -rf {} + 2>/dev/null || true

echo "Done."
