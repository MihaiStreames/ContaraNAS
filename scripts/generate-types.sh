#!/bin/bash
# Generate TypeScript types from Python API schemas
#
# Usage: ./scripts/generate-types.sh
#
# This script:
# 1. Exports FastAPI's OpenAPI schema to JSON
# 2. Generates ui.ts, responses.ts, index.ts type aliases
# 3. Runs openapi-typescript to generate types.generated.ts
# 4. Runs tsc to verify all types compile correctly

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"

echo "==> Generating OpenAPI schema and type aliases..."
cd "$BACKEND_DIR"
uv run python "$SCRIPT_DIR/generate_api_types.py"

echo "==> Generating TypeScript types from OpenAPI..."
cd "$FRONTEND_DIR"
pnpm exec openapi-typescript openapi.json -o src/lib/api/types.generated.ts

echo "==> Verifying TypeScript compilation..."
pnpm exec tsc --noEmit src/lib/api/ui.ts src/lib/api/responses.ts src/lib/api/index.ts

echo "Types generated successfully"
