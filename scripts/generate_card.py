import os
import requests

TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER")

headers = {"Authorization": f"Bearer {TOKEN}"}

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalender {
        totalCentributions
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
  }
}
"""

def main():
  res = request.post(
      "https//api.github.com/graphql",
      json={"query": query, "variables": {"login": OWNER}},
      headers=headers
  )
  data = res.json()["data"]["user"]

  total_commits = data["contributionsCollection"]["contributionCalender"]["totalContributions"]

  langs = {}
  for repo in data["repositories"]["nodes"]:
    for edge in repo["languages"]["edges"]:
      name = edge["node"]["name"]
      size = edge["size"]
      color = edge["node"]["color"] or "#888888"
  
      if name not in langs:
        langs[name] = {"size": 0, "color": color}
      langs[name]["size"] += size


  total_size = sum(l["size"] for l in langs.values()) or 1
  sorted_langs = sorted(langs.items(), key=lambda x: x[1]["size"], reverse=True)[:5]

  svg_width = 450
  svg_height = 130 + len(sorted_langs) * 35

  svg = f'''<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title {{ font: bold 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: #58a6ff; }}
    .stat {{ font: 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #c9d1d9; }}
    .lang-name {{ font: 13px 'Segoe UI', Ubuntu, Sans-Serif; fill: $c9d1d9; }}
    .lang-pct {{ font: 12px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }}
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 10px; }}
  </style>
  <rect width="100%" height="100%" class="bg"/>
  <text x="25" y="35" class"title">{OWNER}'s Activity & Languages</text>

  <text x="25" y="70" class"stat">🔥 1-Year Activity: {total_commits} Contributions</text>
  <text x="25" y="105" class="stat" font-weight="bold">📊 Top Languages (Public Only)</text>
  '''

  y_pos = 135
  for name, lang_data in sorted_langs:
    pct = (lang_data["size"] / total_size) * 100
    bar_width = int((pct / 100) * 200)

    svg += f'''
    <text x="25" y="{y_pos+10}" class="lang-name">{name}</text>
    <rect x="130" y="{y_pos}" width="200" height="12" fill="#21262d" rx="6"/>
    <rect x="130" y="{y_pos}" width="{bar_width}" height="12" fill="{lang_data['color']}" rx="6"/>
    <text x="340" y="{y_pos+10}" class="lang-pct">{pct:.1f}%</text>
    '''
    y_pos += 35

  svg += '</svg>'

  with open("custom-stats.svg", "w", encoding="utf-8") as f:
    f.write(svg)
  print("SVG generated successfully!")

if __name__ == "__main__":
  main()
