#!/usr/bin/env bash
# Rebuild, verify, and only then commit and push.
#
# Twice now a merge has left conflict markers in data/stats.json, the build has
# refused to run on it, and a chained `git add && git commit && git push` has
# pushed the broken file regardless. Everything here is gated on the step
# before it, so a failed build cannot reach the remote.
set -euo pipefail

git fetch -q origin
if ! git merge-base --is-ancestor origin/master HEAD; then
  echo "· merging origin/master"
  git merge origin/master --no-edit || true          # conflicts expected in generated files
fi

echo "· rebuilding"
rm -rf scripts/__pycache__
python scripts/build_profile.py > /dev/null

echo "· verifying"
python - <<'PY'
import json, sys, xml.etree.ElementTree as E
json.load(open("data/stats.json"))                    # raises on conflict markers
svg = open("assets/profile.svg", encoding="utf-8").read()
E.fromstring(svg)
assert "<<<<<<<" not in svg, "conflict markers in assets/profile.svg"
print(f"  stats.json parses; profile.svg valid, {len(svg)/1024:.0f} KB")
PY

git add -A
if git diff --cached --quiet; then
  echo "· nothing to commit"
else
  git commit -q -F "${1:?usage: publish.sh <message-file>}"
fi
git push -q origin master
echo "· pushed $(git rev-parse --short HEAD)"
