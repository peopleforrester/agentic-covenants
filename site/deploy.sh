#!/usr/bin/env bash
# ABOUTME: Publishes site/dist to the gh-pages branch from the local machine.
# ABOUTME: No CI minutes consumed; the build and the push both happen here.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

DIST="site/dist"
BRANCH="gh-pages"

echo "==> building"
python3 site/build.py

[ -f "$DIST/index.html" ] || { echo "deploy: no index.html in $DIST" >&2; exit 1; }
[ -f "$DIST/CNAME" ]      || { echo "deploy: no CNAME in $DIST" >&2; exit 1; }

# A worktree keeps the current checkout untouched, so a deploy can never
# disturb work in progress on staging.
# Fixed, gitignored path. An earlier version used mktemp inside the repo,
# which left a directory that `git add -A` staged as an embedded repository.
WORKTREE=".gh-pages-worktree"
cleanup() {
    # cd out first: the trap can fire while cwd is inside the worktree, and
    # deleting the directory under the shell makes every later command fail
    # with "Unable to read current working directory".
    cd "$ROOT" || return
    git worktree remove --force "$WORKTREE" 2>/dev/null || true
    rm -rf "$WORKTREE"
    git worktree prune
}
trap cleanup EXIT
cleanup

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git worktree add -q "$WORKTREE" "$BRANCH"
else
    echo "==> creating orphan $BRANCH"
    git worktree add -q --detach "$WORKTREE"
    git -C "$WORKTREE" checkout -q --orphan "$BRANCH"
    git -C "$WORKTREE" rm -rqf . 2>/dev/null || true
fi

# Replace wholesale: the build output is the complete published state, and a
# stale page left behind by a rename would still be served.
find "$WORKTREE" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a "$DIST"/. "$WORKTREE"/

SRC_SHA="$(git rev-parse --short HEAD)"

if [ -z "$(git -C "$WORKTREE" status --porcelain)" ]; then
    echo "==> no change to publish"
    exit 0
fi

git -C "$WORKTREE" add -A
git -C "$WORKTREE" commit -q -m "Publish site from $SRC_SHA"
git -C "$WORKTREE" push -q origin "$BRANCH"
echo "==> published $(git -C "$WORKTREE" rev-parse --short HEAD) to $BRANCH"
