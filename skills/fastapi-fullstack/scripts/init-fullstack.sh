#!/bin/bash
# init-fullstack.sh — scaffold the official FastAPI full-stack template
# Usage: bash init-fullstack.sh <project-name>
set -euo pipefail

# ── Argument validation ─────────────────────────────────────────────────────
if [ -z "${1:-}" ]; then
  echo "❌ Usage: bash init-fullstack.sh <project-name>"
  echo "   Example: bash init-fullstack.sh my-saas-app"
  exit 1
fi

PROJECT_NAME="$1"

# Convert project-name to python_package_name (hyphens → underscores, lowercase)
PACKAGE_NAME="${PROJECT_NAME//-/_}"
PACKAGE_NAME="${PACKAGE_NAME,,}"

# ── Prerequisite checks ──────────────────────────────────────────────────────
echo "🔍 Checking prerequisites..."

missing=()

if ! command -v git &>/dev/null; then
  missing+=("git (sudo apt install git)")
fi

if ! command -v uv &>/dev/null; then
  missing+=("uv (curl -LsSf https://astral.sh/uv/install.sh | sh)")
fi

if ! command -v bun &>/dev/null && ! command -v node &>/dev/null; then
  missing+=("bun (curl -fsSL https://bun.sh/install | bash) or node")
fi

if [ ${#missing[@]} -gt 0 ]; then
  echo "❌ Missing prerequisites:"
  for tool in "${missing[@]}"; do
    echo "   - $tool"
  done
  exit 1
fi

echo "✅ All prerequisites found"

# ── Clone template ───────────────────────────────────────────────────────────
echo "📦 Cloning full-stack-fastapi-template into $PROJECT_NAME/..."
git clone https://github.com/fastapi/full-stack-fastapi-template "$PROJECT_NAME"

cd "$PROJECT_NAME"

# Remove upstream git history and start fresh
rm -rf .git
git init
echo "✅ Fresh git repo initialised"

# ── Rename project ───────────────────────────────────────────────────────────
echo "✏️  Renaming project to '$PROJECT_NAME'..."

# pyproject.toml: name field
if [ -f "backend/pyproject.toml" ]; then
  sed -i "s/^name = \"app\"/name = \"$PACKAGE_NAME\"/" backend/pyproject.toml
fi

# Replace 'app' package name throughout backend Python files
if [ -d "backend/app" ]; then
  mv backend/app "backend/$PACKAGE_NAME"
  # Update all Python import statements
  find "backend/$PACKAGE_NAME" -name "*.py" -exec sed -i "s/from app\./from $PACKAGE_NAME./g; s/import app\./import $PACKAGE_NAME./g" {} +
  # Update alembic env.py if it exists
  if [ -f "backend/alembic/env.py" ]; then
    sed -i "s/from app\./from $PACKAGE_NAME./g; s/import app\./import $PACKAGE_NAME./g" backend/alembic/env.py
  fi
  echo "   Backend package: app → $PACKAGE_NAME"
fi

# Docker Compose: replace service/container references to 'app' with project name
for compose_file in compose.yml compose.override.yml; do
  if [ -f "$compose_file" ]; then
    sed -i "s/full-stack-fastapi-template/$PROJECT_NAME/g" "$compose_file"
    echo "   Updated $compose_file"
  fi
done

# ── Generate .env from .env.example ─────────────────────────────────────────
echo ""
echo "🔑 Generating .env..."

if [ ! -f ".env.example" ]; then
  echo "⚠️  .env.example not found — skipping .env generation"
else
  cp .env.example .env

  # Auto-generate secret key
  SECRET_KEY=$(openssl rand -hex 32)
  sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
  echo "   SECRET_KEY auto-generated"

  # Prompt for sensitive values
  echo ""
  read -rp "   POSTGRES_PASSWORD: " POSTGRES_PASSWORD
  sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env

  read -rp "   FIRST_SUPERUSER (email): " FIRST_SUPERUSER
  sed -i "s/^FIRST_SUPERUSER=.*/FIRST_SUPERUSER=$FIRST_SUPERUSER/" .env

  read -rsp "   FIRST_SUPERUSER_PASSWORD: " FIRST_SUPERUSER_PASSWORD
  echo ""
  sed -i "s/^FIRST_SUPERUSER_PASSWORD=.*/FIRST_SUPERUSER_PASSWORD=$FIRST_SUPERUSER_PASSWORD/" .env

  echo "✅ .env written"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "✅ Project '$PROJECT_NAME' scaffolded successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  uv sync                        # install Python backend deps"
echo "  cd frontend && bun install && cd ..  # install frontend deps"
echo "  docker compose up -d           # start the full stack"
echo ""
echo "Access points:"
echo "  Frontend:         http://localhost:5173"
echo "  Backend API docs: http://localhost:8000/docs"
echo "  Adminer (DB UI):  http://localhost:8080"
