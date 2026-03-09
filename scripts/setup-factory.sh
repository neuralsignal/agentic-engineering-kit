#!/bin/bash
# Sets up the dark factory for a repository.
# Runs setup-labels.sh, creates the Factory Dashboard issue, and checks secrets.
#
# Usage: ./setup-factory.sh --repo owner/repo
#
# Requires: gh CLI authenticated with repo access.

set -euo pipefail

REPO=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 --repo owner/repo"
      echo ""
      echo "Sets up the dark factory for a repository:"
      echo "  1. Creates/updates labels (via setup-labels.sh)"
      echo "  2. Creates [Factory Dashboard] issue if it doesn't exist"
      echo "  3. Checks that required secrets are configured"
      echo "  4. Checks workflow permissions (advisory)"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ -z "$REPO" ]; then
  echo "Error: --repo is required"
  echo "Usage: $0 --repo owner/repo"
  exit 1
fi

echo "=== Dark Factory Setup for $REPO ==="
echo ""

# Step 1: Create labels
echo "--- Step 1: Labels ---"
"$SCRIPT_DIR/setup-labels.sh" --repo "$REPO"
echo ""

# Step 2: Create Factory Dashboard issue if it doesn't exist
echo "--- Step 2: Factory Dashboard ---"
DASHBOARD=$(gh issue list --repo "$REPO" \
  --search "[Factory Dashboard]" \
  --state open \
  --json number \
  --jq '.[0].number' 2>/dev/null || true)

if [ -n "$DASHBOARD" ]; then
  echo "  Factory Dashboard already exists: issue #$DASHBOARD"
else
  DASHBOARD_URL=$(gh issue create \
    --repo "$REPO" \
    --title "[Factory Dashboard]" \
    --body "Status aggregation point for dark factory assessment agents. The factory-orchestrator workflow posts periodic status summaries as comments on this issue.")
  echo "  Created Factory Dashboard: $DASHBOARD_URL"
fi
echo ""

# Step 3: Check secrets
echo "--- Step 3: Secrets ---"
SECRETS=$(gh secret list --repo "$REPO" --json name --jq '.[].name' 2>/dev/null || true)

if echo "$SECRETS" | grep -q "CLAUDE_CODE_OAUTH_TOKEN"; then
  echo "  CLAUDE_CODE_OAUTH_TOKEN: set"
else
  echo "  CLAUDE_CODE_OAUTH_TOKEN: NOT SET"
  echo "    Run: claude /install-github-app"
  echo "    Then add the token as a repo secret named CLAUDE_CODE_OAUTH_TOKEN"
fi

if echo "$SECRETS" | grep -q "FACTORY_PAT"; then
  echo "  FACTORY_PAT: set"
else
  echo "  FACTORY_PAT: NOT SET"
  echo "    Create a fine-grained PAT with read/write for: actions, commit statuses, issues, pull requests"
  echo "    Scoped to: $REPO"
  echo "    If label operations fail on public repos, use a classic PAT with public_repo scope instead"
  echo "    Add as repo secret named FACTORY_PAT"
fi
echo ""

# Step 4: Check workflow permissions (advisory)
echo "--- Step 4: Workflow Permissions (advisory) ---"
echo "  Verify manually at: https://github.com/$REPO/settings/actions"
echo "  Required:"
echo "    - Workflow permissions: Read and write"
echo "    - Allow GitHub Actions to create and approve pull requests: enabled"
echo ""

echo "=== Setup complete ==="
