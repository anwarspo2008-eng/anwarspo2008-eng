#!/usr/bin/env python3
"""Builds assets/profile.svg: matrix-style 1/0 rain, ASCII face, live GitHub stats.

Run locally:   GH_TOKEN=ghp_xxx GH_USER=yourname python generate.py
Preview fake:  python generate.py --mock
"""
import os, sys, json, random, html, datetime as dt, urllib.request

# ───────────────────────── EDIT THIS ─────────────────────────
USERNAME = os.environ.get("GH_USER", "anwarspo2008-eng")
NAME     = "Anwar"
INFO = [
    ("Role",     "Dev student | Apps dev"),
    ("Location", "Tetouan, Morocco"),
    ("Learning", "Android app dev"),
    ("Contact",  "anwarspo2008@gmail.com"),
]
STACK = [
    "PHP · MySQL · C · C# · Java",
    "HTML · CSS · JS · Git · GitHub",
    "raylib · CMake · Android Studio · .NET",
]
OUT_FILE = "assets/profile.svg"
GREEN, BRIGHT, WHITE, DIM = "#ffffff", "#ffffff", "#e6e6e6", "#777777"   # black & white theme
# ─────────────────────────────────────────────────────────────

def gql(query, variables=None):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-card"})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = json.load(r)
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]

def fetch_stats(user):
    u = gql("query($u:String!){user(login:$u){createdAt followers{totalCount}"
            " repositories(ownerAffiliations:OWNER,isFork:false){totalCount}}}", {"u": user})["user"]
    stars, langs, cursor = 0, {}, None
    while True:
        d = gql("""query($u:String!,$c:String){user(login:$u){repositories(first:100,after:$c,
                ownerAffiliations:OWNER,isFork:false){pageInfo{hasNextPage endCursor}
                nodes{stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){
                edges{size node{name}}}}}}}""", {"u": user, "c": cursor})["user"]["repositories"]
        for repo in d["nodes"]:
            stars += repo["stargazerCount"]
            for e in repo["languages"]["edges"]:
                langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        cursor = d["pageInfo"]["endCursor"]

    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    commits, days = 0, {}
    for y in range(int(u["createdAt"][:4]), now.year + 1):
        frm = f"{y}-01-01T00:00:00Z"
        to = now.strftime("%Y-%m-%dT%H:%M:%SZ") if y == now.year else f"{y}-12-31T23:59:59Z"
        c = gql("""query($u:String!,$f:DateTime!,$t:DateTime!){user(login:$u){
                contributionsCollection(from:$f,to:$t){totalCommitContributions
                contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}""",
                {"u": user, "f": frm, "t": to})["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"]
        for w in c["contributionCalendar"]["weeks"]:
            for day in w["contributionDays"]:
                days[day["date"]] = day["contributionCount"]
    cur, longest = streaks(days)
    return dict(repos=u["repositories"]["totalCount"], stars=stars, commits=commits,
                followers=u["followers"]["totalCount"], contributions=sum(days.values()),
                streak=cur, longest=longest, langs=langs)

def streaks(days):
    dates = sorted(days)
    longest = run = 0
    prev = None
    for d in dates:
        cur = dt.date.fromisoformat(d)
        if days[d] > 0:
            run = run + 1 if prev and (cur - prev).days == 1 else 1
            longest = max(longest, run)
            prev = cur
        elif prev is not None and (cur - prev).days >= 1:
            run, prev = 0, None
    today = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).date()
    cur = 0
    d = today
    if days.get(d.isoformat(), 0) == 0:
        d -= dt.timedelta(days=1)          # today may not have commits yet
    while days.get(d.isoformat(), 0) > 0:
        cur += 1
        d -= dt.timedelta(days=1)
    return cur, longest

def mock_stats():
    return dict(repos=24, stars=137, commits=1842, followers=58, contributions=2310,
                streak=47, longest=96,
                langs={"Python": 52000, "JavaScript": 31000, "PHP": 24000, "SQL": 15000,
                       "HTML": 9000, "CSS": 6000})

# ───────────────────────── rendering ─────────────────────────
def esc(s): return html.escape(str(s), quote=False)

def bar(pct, n=20):
    filled = max(1 if pct > 0 else 0, round(pct / 100 * n))
    return f'<tspan fill="{GREEN}">{"1" * filled}</tspan><tspan fill="{DIM}">{"0" * (n - filled)}</tspan>'

def render(s):
    random.seed(7)
    FS, LH, COLS = 14, 21, 46
    LX, RX, PW = 34, 484, 410
    W = RX + PW + 26

    def kv(label, value):
        dots = max(2, COLS - len(label) - len(str(value)) - 2)
        return (f'<tspan fill="{GREEN}">{esc(label)}</tspan> <tspan fill="{DIM}">{"." * dots}</tspan> '
                f'<tspan fill="{WHITE}">{esc(value)}</tspan>')
    def title(t):
        return f'<tspan fill="{BRIGHT}" font-weight="bold">── {esc(t)} {"─" * (COLS - len(t) - 4)}</tspan>'

    left = [f'<tspan fill="{BRIGHT}" font-weight="bold" class="glitch">{esc(USERNAME)}</tspan><tspan fill="{DIM}">@github</tspan>',
            f'<tspan fill="{DIM}">{"─" * COLS}</tspan>', kv("Name", NAME)]
    left += [kv(k, v) for k, v in INFO]
    left += ["", title("Stack")] + [f'<tspan fill="{WHITE}">{esc(x)}</tspan>' for x in STACK]

    right = [title("Stats"), kv("Public repos", s["repos"]), kv("Total stars ★", s["stars"]),
             kv("Total commits", f'{s["commits"]:,}'), kv("Followers", s["followers"]),
             kv("Longest streak", f'{s["longest"]} days'), "", title("Languages")]
    total = sum(s["langs"].values()) or 1
    for name, size in sorted(s["langs"].items(), key=lambda kv_: -kv_[1])[:6]:
        pct = size / total * 100
        right.append(f'<tspan fill="{GREEN}">{esc(name):<11}</tspan>{bar(pct, 20)}<tspan fill="{WHITE}"> {pct:4.1f}%</tspan>')
    if not s["langs"]:
        right.append(f'<tspan fill="{DIM}">no public code yet</tspan>')

    top = 46
    streak_y = top + (len(left) + 1) * LH + 14
    H = int(max(streak_y + 78, top + (len(right) + 1) * LH + 26))

    def block(rows, x, d0):
        return "".join(f'<text x="{x}" y="{top + (i + 1) * LH}" class="pl" style="animation-delay:{d0 + i * 0.1:.2f}s">{r}</text>'
                       for i, r in enumerate(rows) if r)

    # rain (white 0/1)
    rain, step, clen, cfs = [], 22, 22, 14
    for i in range(int(W / step)):
        x, dur = i * step + 6, random.uniform(5, 13)
        chars = "".join(f'<tspan x="{x}" dy="{cfs + 2}" fill-opacity="{0.06 + 0.7 * (j / clen) ** 2:.2f}">{random.choice("01")}</tspan>'
                        for j in range(clen))
        rain.append(f'<text x="{x}" y="{-clen * (cfs + 2)}" class="rain" style="animation-duration:{dur:.1f}s;animation-delay:-{random.uniform(0, dur):.1f}s">{chars}</text>')
    fall_to = H + clen * (cfs + 2)

    n = len(str(s["streak"]))
    streak = (f'<g class="pulse"><text x="{LX}" y="{streak_y}" font-size="13" fill="{DIM}">CURRENT COMMIT STREAK</text>'
              f'<text x="{LX}" y="{streak_y + 48}" font-size="48" font-weight="bold" fill="#fff" filter="url(#glow)">{s["streak"]}</text>'
              f'<text x="{LX + 30 * n + 14}" y="{streak_y + 48}" font-size="20" fill="{WHITE}">days</text>'
              f'<text x="{LX + 30 * n + 76}" y="{streak_y + 48}" font-size="26" fill="#fff" class="cursor">█</text></g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="'DejaVu Sans Mono',Menlo,Consolas,'Courier New',monospace" xml:space="preserve">
<defs>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<style>
  .rain {{ font-size:{cfs}px; fill:#fff; animation-name:fall; animation-timing-function:linear; animation-iteration-count:infinite; }}
  @keyframes fall {{ from {{ transform:translateY(0) }} to {{ transform:translateY({fall_to}px) }} }}
  .pl {{ font-size:{FS}px; white-space:pre; opacity:0; animation:fadein .5s forwards; }}
  @keyframes fadein {{ to {{ opacity:1 }} }}
  .pulse {{ animation:pulse 2.4s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity:.8 }} 50% {{ opacity:1 }} }}
  .glitch {{ animation:glitch 6s infinite; }}
  @keyframes glitch {{ 0%,95%,100% {{ opacity:1 }} 96% {{ opacity:.3 }} 98% {{ opacity:1 }} }}
  .cursor {{ animation:blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity:0 }} }}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="#000"/>
  <g opacity="0.5">{"".join(rain)}</g>
  <rect x="14" y="14" width="{RX - 14 - 22}" height="{H - 28}" rx="10" fill="#000" fill-opacity="0.78" stroke="#fff" stroke-opacity="0.25"/>
  <rect x="{RX - 20}" y="14" width="{PW + 36}" height="{H - 28}" rx="10" fill="#000" fill-opacity="0.78" stroke="#fff" stroke-opacity="0.25"/>
  {block(left, LX, 0.2)}
  {block(right, RX, 0.5)}
  {streak}
</g>
<rect width="{W}" height="{H}" rx="14" fill="none" stroke="#fff" stroke-opacity="0.3"/>
</svg>'''

if __name__ == "__main__":
    stats = mock_stats() if "--mock" in sys.argv else fetch_stats(USERNAME)
    out = "preview-sample.svg" if "--mock" in sys.argv else OUT_FILE
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(render(stats))
    print("wrote", out)
