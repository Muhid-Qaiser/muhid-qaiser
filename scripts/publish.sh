#!/usr/bin/env bash
# Rebuild, verify, and only then commit and push.
#
# Twice now a merge has left conflict markers in data/stats.json, the build has
# refused to run on it, and a chained `git add && git commit && git push` has
# pushed the broken file regardless. Everything here is gated on the step
# before it, so a failed build cannot reach the remote.
set -euo pipefail

# Commit local work before merging: git refuses to merge over a dirty tree,
# and the nightly redraw means origin has usually moved.
git add -A
if ! git diff --cached --quiet; then
  git commit -q -F "${1:?usage: publish.sh <message-file>}"
fi

git fetch -q origin
if ! git merge-base --is-ancestor origin/master HEAD; then
  echo "· merging origin/master"
  git merge origin/master --no-edit || true          # generated files will conflict
fi

echo "· reconciling monotonic counts"
python - <<'PY'
import json, subprocess, pathlib
# Pull requests and issues only ever grow, but a merge resolves data/stats.json
# without knowing that, and the workflow's token reports 0 for them. Restore
# the highest value any recent commit recorded.
KEYS = ("pull_requests", "pull_requests_merged", "issues", "streak_best")
f = pathlib.Path("data/stats.json")
cur = json.loads(f.read_text(encoding="utf-8"))
revs = subprocess.run(["git", "log", "-25", "--format=%H", "--", str(f)],
                      capture_output=True, text=True).stdout.split()
best = dict.fromkeys(KEYS, 0)
for r in revs:
    blob = subprocess.run(["git", "show", f"{r}:{f.as_posix()}"],
                          capture_output=True, text=True).stdout
    try:
        old = json.loads(blob)
    except Exception:
        continue
    for k in KEYS:
        best[k] = max(best[k], int(old.get(k) or 0))
changed = [k for k in KEYS if best[k] > int(cur.get(k) or 0)]
for k in changed:
    print(f"  {k}: {cur.get(k)} -> {best[k]}")
    cur[k] = best[k]
if changed:
    f.write_text(json.dumps(cur, indent=2), encoding="utf-8")
else:
    print("  nothing to restore")
PY

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
if ! git diff --cached --quiet; then
  git commit -q --no-edit 2>/dev/null || git commit -q -m "Rebuild"
fi
git push -q origin master
echo "· pushed $(git rev-parse --short HEAD)"
