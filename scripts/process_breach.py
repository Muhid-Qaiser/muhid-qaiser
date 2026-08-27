#!/usr/bin/env python3
import os, json, hashlib
from pathlib import Path

STATE = Path("data/breach.json")
OUT = Path("assets/breach.svg")
RESULT = Path("breach-result.md")

BG="#070b10"; PANEL="#0d131a"; BORDER="#26313d"; TEXT="#e8edf2"; MUTED="#8896a5"
CYAN="#67e8f9"; RED="#ff5a67"; CREAM="#f1d6b8"; GREEN="#63e6be"

title = os.environ.get("ISSUE_TITLE", "")
issue = os.environ.get("ISSUE_NUMBER", "0")
actor = os.environ.get("ISSUE_ACTOR", "visitor")

vectors = {
  "[BREACH] PROMPT_INJECTION": ("PROMPT_INJECTION", 0.44),
  "[BREACH] TOOL_HIJACK": ("TOOL_HIJACK", 0.29),
  "[BREACH] ARTIFACT_POISONING": ("ARTIFACT_POISONING", 0.36),
}
if title not in vectors:
    print("Not a recognized profile game issue; nothing to do.")
    raise SystemExit(0)

vector, breach_probability = vectors[title]
s = json.loads(STATE.read_text())
seed = hashlib.sha256(f"{issue}:{vector}".encode()).digest()[0] / 255
breached = seed < breach_probability

s["attempts"] += 1
s["vectors"][vector] = s["vectors"].get(vector, 0) + 1
s["last_vector"] = vector
if breached:
    s["attacker"] += 1
    s["last_result"] = "BYPASS DETECTED"
else:
    s["guard"] += 1
    s["last_result"] = "ATTACK BLOCKED"

STATE.write_text(json.dumps(s, indent=2))

attacker=s["attacker"]; guard=s["guard"]; attempts=s["attempts"]
last=s["last_result"]; vec=s["last_vector"]
svg=f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="270" viewBox="0 0 1200 270">
<defs><pattern id="bg3" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#111c25" opacity=".45"/></pattern></defs>
<rect x="1" y="1" width="1198" height="268" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
<rect x="1" y="1" width="1198" height="268" rx="18" fill="url(#bg3)"/>
<text x="38" y="48" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13" fill="{RED}">PLAY // BREACH AGENT-01</text>
<text x="38" y="82" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="28" font-weight="700" fill="{TEXT}">Can the guard hold?</text>
<circle cx="1012" cy="43" r="5" fill="{GREEN}"/><text x="1025" y="48" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" fill="{GREEN}">SIMULATION ONLINE</text>
<rect x="38" y="112" width="250" height="105" rx="12" fill="{PANEL}" stroke="{BORDER}"/>
<text x="58" y="139" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" fill="{MUTED}">ATTACKER WINS</text><text x="58" y="188" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="46" font-weight="800" fill="{RED}">{attacker:02d}</text>
<rect x="305" y="112" width="250" height="105" rx="12" fill="{PANEL}" stroke="{BORDER}"/>
<text x="325" y="139" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" fill="{MUTED}">GUARD BLOCKS</text><text x="325" y="188" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="46" font-weight="800" fill="{GREEN}">{guard:02d}</text>
<rect x="572" y="112" width="250" height="105" rx="12" fill="{PANEL}" stroke="{BORDER}"/>
<text x="592" y="139" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" fill="{MUTED}">TOTAL ATTEMPTS</text><text x="592" y="188" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="46" font-weight="800" fill="{CREAM}">{attempts:02d}</text>
<rect x="839" y="112" width="323" height="105" rx="12" fill="#0c1218" stroke="{BORDER}"/>
<text x="859" y="139" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" fill="{MUTED}">LAST EVENT</text>
<text x="859" y="165" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12" fill="{CYAN}">{vec}</text>
<text x="859" y="190" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12" fill="{TEXT}">{last}</text>
<text x="38" y="248" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" fill="{MUTED}">choose an attack vector below  /  GitHub resolves the mini-simulation  /  scoreboard updates automatically</text>
</svg>"""
OUT.write_text(svg, encoding="utf-8")

headline = "🔴 BYPASS DETECTED" if breached else "🟢 ATTACK BLOCKED"
RESULT.write_text(
    f"### {headline}\n\n"
    f"`vector` **{vector}**  \n"
    f"`operator` **@{actor}**  \n"
    f"`attempt` **#{s['attempts']}**\n\n"
    f"The profile scoreboard has been updated automatically. This is a lightweight GitHub profile mini-game, not a real security assessment.\n"
)
print(last)
