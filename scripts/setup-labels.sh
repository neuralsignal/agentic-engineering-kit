#!/bin/bash
# Creates GitHub labels required by the dark factory workflows.
# Usage: ./setup-labels.sh --repo owner/repo
#
# Requires: gh CLI authenticated with repo access.

set -euo pipefail

REPO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 --repo owner/repo"
      echo ""
      echo "Creates GitHub labels required by the dark factory workflows."
      echo "Existing labels with the same name are updated (color/description overwritten)."
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

# Format: "name|color|description"  (pipe-delimited because label names contain colons)
LABELS=(
  "type:bug|#d73a4a|Bug report"
  "type:feat|#0075ca|Feature request"
  "type:chore|#e4e669|Maintenance / improvement"
  "priority:1|#b60205|Urgent -- implement immediately"
  "priority:2|#fbca04|Normal priority (default)"
  "priority:3|#0e8a16|Backlog"
  "claude:implement|#7057ff|Trigger Claude to implement this issue"
  "status:triaged|#c5def5|Issue has been triaged"
  "status:in-progress|#f9d0c4|Claude is working on this"
  "status:pr-created|#bfd4f2|PR created, awaiting review"
  "status:blocked|#e99695|Implementation blocked"
  "source:dep-audit|#d4c5f9|Created by dependency audit agent"
  "source:security-scan|#f9d0c4|Created by security scan agent"
  "source:code-quality|#c2e0c6|Created by code quality check"
  "source:test-coverage|#bfdadc|Created by test coverage analysis"
  "source:docs-freshness|#fef2c0|Created by docs freshness check"
  "source:workflow-upgrade|#ededed|Created by workflow upgrade check"
  "status:pr-draft|#d4c5f9|Draft PR created, CI pending"
  "autofix:1|#c5def5|First auto-fix attempt"
  "autofix:2|#fef2c0|Second auto-fix attempt"
  "autofix:3|#e99695|Third (final) auto-fix attempt"
)

echo "Creating/updating labels on $REPO..."
echo ""

for entry in "${LABELS[@]}"; do
  IFS='|' read -r name color description <<< "$entry"
  # gh label create updates existing labels with --force
  if gh label create "$name" --repo "$REPO" --color "${color#\#}" --description "$description" --force 2>/dev/null; then
    echo "  ✓ $name"
  else
    echo "  ✗ $name (failed)"
  fi
done

echo ""
echo "Done. Labels created/updated on $REPO."
