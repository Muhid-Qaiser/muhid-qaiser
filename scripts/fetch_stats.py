#!/usr/bin/env python3
"""Collect the numbers the profile figures need, into data/stats.json.

Deliberately does NOT publish a lines-of-code total: this account is mostly
Jupyter notebooks, whose committed JSON carries base64 image outputs, so the
raw additions figure is an artefact of the file format rather than work done.
Repositories, regions and rebuilt-from-scratch counts are the honest signals.

Kept separate from rendering so the drawing scripts can be re-run offline.
"""
import json, os, re, sys, time, urllib.request, urllib.error
from collections import Counter
from pathlib import Path

LOGIN = os.environ.get("PROFILE_LOGIN", "Muhid-Qaiser")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
TZ_FALLBACK = 5  # PKT, used only when a commit date carries no UTC offset
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "stats.json"

if not TOKEN:
    sys.exit("Set GITHUB_TOKEN (locally: export GITHUB_TOKEN=$(gh auth token))")

HEADERS = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "muhid-profile",
           "Accept": "application/vnd.github+json"}

# Regions of the map, tested in order — first match wins, so the more specific
# vocabularies (agents, perception) are checked before the general ones.
REGIONS = [
    ("AGENTIC AI", r"agent|crewai|langchain|langgraph|\brag\b|_rag|-rag|tool|interviewer|"
               r"chatbot|prompt|multi-doc|multi_doc|ollama|mcp"),
    ("COMPUTER VISION", r"yolo|cnn|image|vision|visual|segmentation|detection|opencv|ocr|face|"
                   r"facial|emotion|pose|unet|resnet|teznet|oct|agrovq|bar_?code|"
                   r"attendance|homer|cat-dog|natural-image|digital_image|topological"),
    ("GENERATIVE AI", r"bert|gpt|transformer|translation|nlp|text|tts|speech|sentiment|spam|"
                 r"naive|token|deepseek|llm|urdu|moderation|audio|huffman"),
    ("PARALLEL COMPUTE", r"cuda|opencl|gpu|parallel|grpc|microservice|assembly|masm|x86|coal|"
                r"comparative_analysis"),
    ("MACHINE LEARNING", r"random-forest|decision-tree|k-nearest|knn|churn|salary|regression|lstm|"
                 r"prediction|auto-?encoder|genetic|search|astar|uniform|rating|deepdream|"
                 r"swish|ann[_-]|neural|machine-learning|specialization|classification"),
]
SCRATCH = re.compile(r"scratch|vanilla", re.I)


def rest(path, tries=6):
    for attempt in range(tries):
        req = urllib.request.Request(f"https://api.github.com{path}", headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                if r.status == 202:      # GitHub is still computing the stats
                    time.sleep(2 + attempt * 2)
                    continue
                return [] if r.status == 204 else json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (404, 409):     # empty repository, or renamed
                return []
            if attempt < tries - 1:
                time.sleep(2 + attempt * 3)
                continue
            raise
    return []


def search_count(query):
    """Total matches for a search. Search reads public data, so this works
    with the workflow's repo-scoped token, where user.pullRequests does not."""
    import urllib.parse
    try:
        body = rest(f"/search/issues?q={urllib.parse.quote(query)}&per_page=1")
        return body.get("total_count", 0) if isinstance(body, dict) else 0
    except Exception as exc:
        print(f"  ! search '{query}' failed: {exc}")
        return 0


def graphql(query, **variables):
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=payload,
                                 method="POST",
                                 headers={**HEADERS, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as r:
        body = json.load(r)
    errors = body.get("errors") or []
    data = body.get("data") or {}
    if errors and not data.get("user"):
        raise RuntimeError(errors)
    for e in errors:
        where = ".".join(str(p) for p in e.get("path", []))
        print(f"  ! skipped {where}: {e.get('message')}")
    return data


PROFILE_Q = """
query($login:String!) {
  user(login:$login) {
    createdAt
    followers { totalCount }
    following { totalCount }
    starredRepositories { totalCount }
    repositoriesContributedTo(
      contributionTypes:[COMMIT,ISSUE,PULL_REQUEST,REPOSITORY]) { totalCount }
    repositories(ownerAffiliations:OWNER, privacy:PUBLIC) { totalCount }
    repos: repositories(first:100, ownerAffiliations:OWNER, isFork:false,
                        privacy:PUBLIC, orderBy:{field:PUSHED_AT,direction:DESC}) {
      nodes {
        name description createdAt pushedAt stargazerCount
        primaryLanguage { name color }
        languages(first:10, orderBy:{field:SIZE,direction:DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def region_of(repo):
    hay = f"{repo['name']} {repo.get('description') or ''}".lower()
    for name, pattern in REGIONS:
        if re.search(pattern, hay):
            return name
    return "FOUNDATIONS"


print(f"· profile        {LOGIN}")
user = graphql(PROFILE_Q, login=LOGIN)["user"]
nodes = user["repos"]["nodes"]

languages, colors = Counter(), {}
for repo in nodes:
    for edge in repo["languages"]["edges"]:
        languages[edge["node"]["name"]] += edge["size"]
        colors[edge["node"]["name"]] = edge["node"].get("color")

print(f"· commits        walking {len(nodes)} repositories")
hours = [0] * 24
years = Counter()
repos, total_commits = [], 0

for i, repo in enumerate(nodes, 1):
    mine = 0
    for commit in rest(f"/repos/{LOGIN}/{repo['name']}/commits"
                       f"?author={LOGIN}&per_page=100") or []:
        date = ((commit.get("commit") or {}).get("author") or {}).get("date")
        if not date or len(date) < 19:
            continue
        mine += 1
        hour, tail = int(date[11:13]), date[19:]
        if tail and tail[0] in "+-":
            hour = (hour + (1 if tail[0] == "+" else -1) * int(tail[1:3])) % 24
        else:
            hour = (hour + TZ_FALLBACK) % 24
        hours[hour] += 1
        years[date[:4]] += 1

    total_commits += mine
    repos.append({
        "name": repo["name"],
        "description": repo.get("description") or "",
        "created": repo["createdAt"][:10],
        "pushed": repo["pushedAt"][:10],
        "stars": repo["stargazerCount"],
        "language": (repo.get("primaryLanguage") or {}).get("name") or "",
        "commits": mine,
        "region": region_of(repo),
        "scratch": bool(SCRATCH.search(f"{repo['name']} {repo.get('description') or ''}")),
    })
    if i % 20 == 0:
        print(f"    {i}/{len(nodes)}")

calendar = user["contributionsCollection"]["contributionCalendar"]
days = [(d["date"], d["contributionCount"])
        for w in calendar["weeks"] for d in w["contributionDays"]]
days.sort()

# Today may not be over yet, so an empty final day does not break a streak.
tail = days[:-1] if days and days[-1][1] == 0 else days
streak_current = 0
for _, count in reversed(tail):
    if not count:
        break
    streak_current += 1

streak_best = run = 0
for _, count in days:
    run = run + 1 if count else 0
    streak_best = max(streak_best, run)

active_days = sum(1 for _, c in days if c)
busiest = max(days, key=lambda d: d[1]) if days else ("", 0)
busiest = {"date": busiest[0], "count": busiest[1]}

by_region = Counter(r["region"] for r in repos)
stats = {
    "login": LOGIN,
    "since": user["createdAt"][:10],
    "repos": user["repositories"]["totalCount"],
    "repos_mapped": len(repos),
    "followers": user["followers"]["totalCount"],
    "stars": sum(r["stars"] for r in repos),
    "commits": total_commits,
    "contributions_year": calendar["totalContributions"],
    "streak_current": streak_current,
    "streak_best": streak_best,
    "active_days": active_days,
    "calendar_days": len(days),
    "busiest_day": busiest,
    "pull_requests": search_count(f"type:pr author:{LOGIN}"),
    "pull_requests_merged": search_count(f"type:pr author:{LOGIN} is:merged"),
    "issues": search_count(f"type:issue author:{LOGIN}"),
    "starred": (user.get("starredRepositories") or {}).get("totalCount", 0),
    "following": (user.get("following") or {}).get("totalCount", 0),
    "contributed_to": (user.get("repositoriesContributedTo") or {}).get("totalCount", 0),
    "year": {k: user["contributionsCollection"][v] for k, v in (
        ("commits", "totalCommitContributions"),
        ("pull_requests", "totalPullRequestContributions"),
        ("issues", "totalIssueContributions"),
        ("reviews", "totalPullRequestReviewContributions"),
        ("repositories", "totalRepositoryContributions"),
        ("private", "restrictedContributionsCount"),
    )},
    "scratch_builds": sum(1 for r in repos if r["scratch"]),
    "regions": [{"name": n, "count": c} for n, c in
                sorted(by_region.items(), key=lambda x: -x[1])],
    "hours": hours,
    "commits_by_year": dict(sorted(years.items())),
    "languages": [{"name": n, "size": s, "color": colors.get(n)}
                  for n, s in languages.most_common(10)],
    "repo_list": repos,
}

MONOTONIC = ("pull_requests", "pull_requests_merged", "issues")
if OUT.exists():
    try:
        prior = json.loads(OUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        prior = {}
    for key in MONOTONIC:
        was, now = prior.get(key, 0), stats.get(key, 0)
        if was > now:
            print(f"  · {key}: keeping {was} (this token only sees {now})")
            stats[key] = was

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(stats, indent=2), encoding="utf-8")
print(f"\nwrote {OUT}")
print(f"  {stats['repos']} repositories · {total_commits} commits · "
      f"{stats['scratch_builds']} rebuilt from scratch")
print(f"  streak: {streak_current} now, {streak_best} best · "
      f"{active_days}/{len(days)} active days")
for r in stats["regions"]:
    print(f"    {r['name']:14} {r['count']}")
