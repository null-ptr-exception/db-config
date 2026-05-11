#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BRANCH="catalog"
# Generate catalog
python3 "$REPO_ROOT/scripts/generate_catalog.py"

# Set up a temporary worktree for the orphan branch
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

# Check if the branch exists on the remote
if git ls-remote --exit-code origin "refs/heads/$BRANCH" >/dev/null 2>&1; then
    git fetch origin "$BRANCH"
    git worktree add "$WORK_DIR" "origin/$BRANCH" --detach
    cd "$WORK_DIR"
    git checkout -B "$BRANCH"
else
    git worktree add --detach "$WORK_DIR"
    cd "$WORK_DIR"
    git checkout --orphan "$BRANCH"
    git rm -rf . >/dev/null 2>&1 || true
fi

# Copy generated catalog files
cp "$REPO_ROOT"/output/*.yaml "$WORK_DIR/"

# Commit and push if there are changes
git add *.yaml
if git diff --cached --quiet; then
    echo "No changes to catalog, skipping commit."
else
    git commit -m "chore: update database catalog"
    git push origin "$BRANCH"
    echo "Pushed updated catalog to '$BRANCH' branch."
fi

# Cleanup worktree
cd "$REPO_ROOT"
git worktree remove "$WORK_DIR" --force 2>/dev/null || true
