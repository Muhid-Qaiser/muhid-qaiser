#!/usr/bin/env python3
import os, json, urllib.request, html
from pathlib import Path

LOGIN = os.environ.get("PROFILE_LOGIN", "Muhid-Qaiser")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = Path("assets/telemetry.svg")

BG="#070b10"; PANEL="#0d131a"; BORDER="#26313d"; TEXT="#e8edf2"; MUTED="#8896a5"
CYAN="#67e8f9"; RED="#ff5a67"; CREAM="#f1d6b8"; GREEN="#63e6be"

query = r"""
query($login:String!) {
  user(login:$login) {
    followers { totalCount }
    repositories(ownerAffiliations:OWNER) { totalCount }
    sourceRepos: repositories(first:100, ownerAffiliations:OWNER, isFork:false, orderBy:{field:UPDATED_AT,direction:DESC}) {
      nodes {
        stargazerCount
        languages(first:12, orderBy:{field:SIZE,direction:DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}
"""

payload = json.dumps({"query": query, "variables": {"login": LOGIN}}).encode()
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "profile-telemetry"
    },
    method="POST",
)
with urllib.request.urlopen(req, timeout=30) as r:
    body = json.load(r)

if body.get("errors"):
    raise RuntimeError(body["errors"])

u = body["data"]["user"]
repos = u["sourceRepos"]["nodes"]
repo_count = u["repositories"]["totalCount"]
stars = sum(r["stargazerCount"] for r in repos)
followers = u["followers"]["totalCount"]
calendar = u["contributionsCollection"]["contributionCalendar"]
contribs = calendar["totalContributions"]

langs = {}
lang_colors = {}
for repo in repos:
    for e in repo["languages"]["edges"]:
        name = e["node"]["name"]
        langs[name] = langs.get(name, 0) + e["size"]
        lang_colors[name] = e["node"].get("color") or CYAN

top = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:6]
total = sum(v for _, v in top) or 1

# Build 52-week heatmap from latest weeks.
weeks = calendar["weeks"][-52:]
counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
mx = max(counts or [1])
def heat_color(c):
    if c == 0: return "#111820"
    ratio = c / mx
    if ratio < .25: return "#17353b"
    if ratio < .5: return "#1e5660"
    if ratio < .75: return "#2a8290"
    return CYAN

parts = [f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360">
<rect x="1" y="1" width="1198" height="358" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
<text x="38" y="47" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13" fill="{CYAN}">LIVE // GITHUB TELEMETRY</text>
<text x="38" y="78" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="26" font-weight="700" fill="{TEXT}">Signal, not badge clutter.</text>"""]

cards = [
    ("PUBLIC REPOS", str(repo_count), TEXT),
    ("STARS RECEIVED", str(stars), CREAM),
    ("FOLLOWERS", str(followers), CYAN),
    ("CONTRIBUTIONS / 12M", str(contribs), GREEN),
]
for i, (label, value, color) in enumerate(cards):
    x = 38 + i*280
    parts.append(f"""<rect x="{x}" y="104" width="264" height="80" rx="11" fill="{PANEL}" stroke="{BORDER}"/>
<text x="{x+20}" y="131" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10" fill="{MUTED}">{label}</text>
<text x="{x+20}" y="168" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="31" font-weight="800" fill="{color}">{html.escape(value)}</text>""")

parts.append(f"""<text x="38" y="221" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10" fill="{MUTED}">LANGUAGE SIGNAL</text>""")
x = 38
bar_w = 510
for name, val in top:
    w = max(2, bar_w * val / total)
    color = lang_colors.get(name) or CYAN
    parts.append(f'<rect x="{x:.1f}" y="236" width="{w:.1f}" height="13" rx="5" fill="{color}"/>')
    x += w

legend_x = 38
for name, val in top:
    pct = val / total * 100
    color = lang_colors.get(name) or CYAN
    parts.append(f'<circle cx="{legend_x+5}" cy="273" r="4" fill="{color}"/>')
    parts.append(f'<text x="{legend_x+15}" y="277" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10" fill="{MUTED}">{html.escape(name)} {pct:.0f}%</text>')
    legend_x += 145

parts.append(f'<text x="620" y="221" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10" fill="{MUTED}">52-WEEK ACTIVITY</text>')
cell=6; gap=3; start_x=620; start_y=235
for wi,w in enumerate(weeks):
    for di,d in enumerate(w["contributionDays"]):
        c=d["contributionCount"]
        parts.append(f'<rect x="{start_x + wi*(cell+gap)}" y="{start_y + di*(cell+gap)}" width="{cell}" height="{cell}" rx="1.5" fill="{heat_color(c)}"/>')

parts.append(f'<text x="38" y="334" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10" fill="{MUTED}">auto-generated from GitHub GraphQL • language share = bytes across visible non-fork repositories</text>')
parts.append("</svg>")
OUT.write_text("".join(parts), encoding="utf-8")
print(f"updated {OUT}")
