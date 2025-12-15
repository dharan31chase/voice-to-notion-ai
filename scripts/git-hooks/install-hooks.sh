#!/bin/bash
# Install git hooks from scripts/git-hooks/ to .git/hooks/
# Run this after cloning the repo or when hooks are updated

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOKS_SOURCE="$REPO_ROOT/scripts/git-hooks"
HOOKS_TARGET="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."

# Install prepare-commit-msg hook
if [ -f "$HOOKS_SOURCE/prepare-commit-msg" ]; then
    cp "$HOOKS_SOURCE/prepare-commit-msg" "$HOOKS_TARGET/prepare-commit-msg"
    chmod +x "$HOOKS_TARGET/prepare-commit-msg"
    echo "✓ Installed prepare-commit-msg hook"
else
    echo "✗ prepare-commit-msg hook not found in $HOOKS_SOURCE"
    exit 1
fi

echo ""
echo "✅ Git hooks installed successfully"
echo ""
echo "Hook installed:"
echo "  - prepare-commit-msg: Auto-fills commit message template"
