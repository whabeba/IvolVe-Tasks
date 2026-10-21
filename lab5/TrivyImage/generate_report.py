import json
import os
import sys
import base64
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────
V1_FILE    = "trivy-report.json"
V2_FILE    = "trivy-report-v2.json"
OUTPUT     = "vulnerability-report.html"

COLORS = {
    "CRITICAL": "#D72638",
    "HIGH":     "#F4511E",
    "MEDIUM":   "#FFA500",
    "LOW":      "#4CAF50",
    "UNKNOWN":  "#9E9E9E",
}
SEV_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]

# ── Helpers ───────────────────────────────────────────────────────────────────
def parse(path):
    if not os.path.exists(path):
        return None, {}, []
    with open(path) as f:
        data = json.load(f)
    counts = {s: 0 for s in SEV_ORDER}
    vulns  = []
    for result in data.get("Results", []):
        for v in result.get("Vulnerabilities") or []:
            sev = v.get("Severity", "UNKNOWN").upper()
            counts[sev] = counts.get(sev, 0) + 1
            if sev in ("CRITICAL", "HIGH"):
                vulns.append({
                    "cve":       v.get("VulnerabilityID", "N/A"),
                    "package":   v.get("PkgName", "N/A"),
                    "installed": v.get("InstalledVersion", "N/A"),
                    "fixed":     v.get("FixedVersion") or "No fix",
                    "severity":  sev,
                    "title":     (v.get("Title") or v.get("Description", ""))[:80] or "—",
                })
    vulns.sort(key=lambda x: 0 if x["severity"] == "CRITICAL" else 1)
    name = data.get("ArtifactName", os.path.basename(path))
    return name, counts, vulns

def fig_to_b64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# ── Parse both versions ───────────────────────────────────────────────────────
name1, counts1, vulns1 = parse(V1_FILE)
name2, counts2, vulns2 = parse(V2_FILE)

if not name1:
    print(f"[ERROR] {V1_FILE} not found.")
    sys.exit(1)

has_v2    = name2 is not None
total1    = sum(counts1.values())
total2    = sum(counts2.values()) if has_v2 else 0

print(f"[INFO] v1 ({name1}): {total1:,} vulnerabilities")
for s in SEV_ORDER:
    print(f"       {s}: {counts1[s]}")
if has_v2:
    print(f"[INFO] v2 ({name2}): {total2:,} vulnerabilities")
    for s in SEV_ORDER:
        print(f"       {s}: {counts2[s]}")

os.makedirs("screenshots", exist_ok=True)

# ── Chart 1 — Bar chart (v1 only OR side-by-side) ────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(SEV_ORDER))
w = 0.35 if has_v2 else 0.5

bars1 = ax.bar(x - (w/2 if has_v2 else 0),
               [counts1[s] for s in SEV_ORDER],
               width=w, color=[COLORS[s] for s in SEV_ORDER],
               label=name1, edgecolor="white")

if has_v2:
    bars2 = ax.bar(x + w/2,
                   [counts2[s] for s in SEV_ORDER],
                   width=w, color=[COLORS[s] for s in SEV_ORDER],
                   alpha=0.5, label=name2, edgecolor="white", hatch="//")
    for bar, val in zip(bars2, [counts2[s] for s in SEV_ORDER]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                f"{val:,}", ha="center", va="bottom", fontsize=9, color="#555")

for bar, val in zip(bars1, [counts1[s] for s in SEV_ORDER]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
            f"{val:,}", ha="center", va="bottom", fontsize=9, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(SEV_ORDER, fontsize=11)
ax.set_title("Vulnerability Count by Severity" + (" — v1 vs v2" if has_v2 else ""), fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Count", fontsize=11)
ax.set_facecolor("#F9F9F9")
fig.patch.set_facecolor("#FFFFFF")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linestyle="--", alpha=0.4)
ax.set_axisbelow(True)
if has_v2:
    ax.legend(fontsize=10)
plt.tight_layout()
bar_b64 = fig_to_b64(fig)
fig.savefig("screenshots/bar_chart.png", dpi=150, bbox_inches="tight")
plt.close()
print("[INFO] Saved: screenshots/bar_chart.png")

# ── Chart 2 — Pie chart v1 ────────────────────────────────────────────────────
def make_pie(counts, title, filename=None):
    nz = {k: v for k, v in counts.items() if v > 0}
    fig, ax = plt.subplots(figsize=(6, 6))
    _, texts, autotexts = ax.pie(
        nz.values(), labels=nz.keys(),
        colors=[COLORS[k] for k in nz],
        autopct="%1.1f%%", startangle=140, pctdistance=0.82,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for t in texts:    t.set_fontsize(11); t.set_fontweight("bold")
    for a in autotexts: a.set_fontsize(9);  a.set_color("white"); a.set_fontweight("bold")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=16)
    plt.tight_layout()
    b64 = fig_to_b64(fig)
    if filename:
        fig.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"[INFO] Saved: {filename}")
    plt.close()
    return b64

pie1_b64 = make_pie(counts1, f"v1 Distribution\n{name1}", "screenshots/pie_chart.png")
pie2_b64 = make_pie(counts2, f"v2 Distribution\n{name2}", "screenshots/pie_chart_v2.png") if has_v2 else None

# ── Chart 3 — Comparison bar (CRITICAL + HIGH only) ──────────────────────────
comp_b64 = None
if has_v2:
    cats    = ["CRITICAL", "HIGH"]
    v1_vals = [counts1[c] for c in cats]
    v2_vals = [counts2[c] for c in cats]
    x2 = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=(7, 5))
    b1 = ax.bar(x2 - 0.2, v1_vals, width=0.35, color=["#D72638","#F4511E"], label=name1, edgecolor="white")
    b2 = ax.bar(x2 + 0.2, v2_vals, width=0.35, color=["#D72638","#F4511E"], alpha=0.45, label=name2, edgecolor="white", hatch="//")
    for bar, val in zip(list(b1)+list(b2), v1_vals+v2_vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+4,
                f"{val:,}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_xticks(x2); ax.set_xticklabels(cats, fontsize=12)
    ax.set_title("HIGH & CRITICAL: v1 vs v2", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_facecolor("#F9F9F9"); fig.patch.set_facecolor("#FFFFFF")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4); ax.set_axisbelow(True)
    ax.legend(fontsize=10)
    plt.tight_layout()
    comp_b64 = fig_to_b64(fig)
    fig.savefig("screenshots/comparison_chart.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[INFO] Saved: screenshots/comparison_chart.png")

# ── HTML helpers ──────────────────────────────────────────────────────────────
SEV_BADGE = {
    "CRITICAL": '<span style="background:#D72638;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700">CRITICAL</span>',
    "HIGH":     '<span style="background:#F4511E;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700">HIGH</span>',
}

def card(bg, label, val):
    return (f'<div style="background:{bg};color:#fff;border-radius:8px;padding:16px 22px;'
            f'text-align:center;min-width:110px">'
            f'<div style="font-size:26px;font-weight:800">{val:,}</div>'
            f'<div style="font-size:11px;margin-top:4px;opacity:.9">{label}</div></div>')

def cards_row(counts):
    return "".join(card(COLORS[s], s, counts[s]) for s in SEV_ORDER)

def vuln_rows(vulns, limit=20):
    html = ""
    for v in vulns[:limit]:
        badge = SEV_BADGE.get(v["severity"], v["severity"])
        html += (f'<tr><td><code style="font-size:11px">{v["cve"]}</code></td>'
                 f'<td>{v["package"]}</td><td>{v["installed"]}</td>'
                 f'<td>{v["fixed"]}</td><td>{badge}</td>'
                 f'<td style="font-size:11px;color:#555">{v["title"]}</td></tr>')
    return html

# ── Comparison summary section ────────────────────────────────────────────────
compare_section = ""
if has_v2:
    rows = ""
    for s in SEV_ORDER:
        diff  = counts2[s] - counts1[s]
        arrow = f'<span style="color:#4CAF50;font-weight:700">▼ {abs(diff):,}</span>' if diff < 0 else \
                (f'<span style="color:#D72638;font-weight:700">▲ {diff:,}</span>' if diff > 0 else
                 '<span style="color:#999">—</span>')
        rows += (f'<tr><td><span style="background:{COLORS[s]};color:#fff;padding:2px 8px;'
                 f'border-radius:4px;font-size:11px;font-weight:700">{s}</span></td>'
                 f'<td style="text-align:center">{counts1[s]:,}</td>'
                 f'<td style="text-align:center">{counts2[s]:,}</td>'
                 f'<td style="text-align:center">{arrow}</td></tr>')

    total_diff = total2 - total1
    total_arrow = f'<span style="color:#4CAF50;font-weight:700">▼ {abs(total_diff):,}</span>' if total_diff < 0 else \
                  f'<span style="color:#D72638;font-weight:700">▲ {total_diff:,}</span>'

    compare_section = f"""
  <h2>📊 Remediation Comparison: v1 vs v2</h2>
  <div style="display:flex;gap:24px;flex-wrap:wrap;margin-bottom:24px">
    <img src="data:image/png;base64,{comp_b64}" alt="Comparison" style="border-radius:8px;border:1px solid #e5e7eb;background:#fff;height:300px"/>
  </div>
  <table style="max-width:520px">
    <thead><tr><th>Severity</th><th>v1 ({name1})</th><th>v2 ({name2})</th><th>Change</th></tr></thead>
    <tbody>
      {rows}
      <tr style="font-weight:700;background:#f7f8fa">
        <td>TOTAL</td>
        <td style="text-align:center">{total1:,}</td>
        <td style="text-align:center">{total2:,}</td>
        <td style="text-align:center">{total_arrow}</td>
      </tr>
    </tbody>
  </table>

  <h2>v2 Severity Distribution</h2>
  <div style="display:flex;gap:24px;flex-wrap:wrap">
    <img src="data:image/png;base64,{pie1_b64}" alt="v1 Pie" style="border-radius:8px;border:1px solid #e5e7eb;background:#fff;height:280px"/>
    <img src="data:image/png;base64,{pie2_b64}" alt="v2 Pie" style="border-radius:8px;border:1px solid #e5e7eb;background:#fff;height:280px"/>
  </div>

  <h2>Top 20 HIGH &amp; CRITICAL — v2 ({name2})</h2>
  <table>
    <thead><tr><th>CVE ID</th><th>Package</th><th>Installed</th><th>Fixed Version</th><th>Severity</th><th>Description</th></tr></thead>
    <tbody>{vuln_rows(vulns2)}</tbody>
  </table>
"""

# ── Full HTML ─────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Trivy Vulnerability Report</title>
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,"Segoe UI",system-ui,sans-serif;background:#f0f2f5;color:#1f2328}}
  .page{{max-width:1100px;margin:0 auto;padding:32px 24px}}
  h1{{font-size:24px;font-weight:800}}
  h2{{font-size:17px;font-weight:700;margin:32px 0 14px;border-left:4px solid #3b82d4;padding-left:10px}}
  .subtitle{{color:#57606a;font-size:13px;margin-top:4px}}
  .cards{{display:flex;gap:14px;flex-wrap:wrap;margin:20px 0}}
  table{{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
  th{{background:#2c3e50;color:#fff;text-align:left;padding:10px 12px;font-size:12px;text-transform:uppercase;letter-spacing:.05em}}
  td{{padding:9px 12px;font-size:12px;border-bottom:1px solid #f0f2f5;vertical-align:middle}}
  tr:hover td{{background:#f7f8fa}}
  .tag{{background:#e8f0fe;color:#3b82d4;border-radius:4px;padding:3px 10px;font-size:12px;font-weight:600}}
  footer{{text-align:center;margin-top:48px;padding-top:16px;border-top:1px solid #e5e7eb;font-size:12px;color:#57606a}}
</style>
</head>
<body>
<div class="page">

  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
    <div>
      <h1>🔍 Trivy Vulnerability Report</h1>
      <p class="subtitle">Image: <strong>{name1}</strong> &nbsp;|&nbsp; Total: <strong>{total1:,}</strong> vulnerabilities</p>
    </div>
    <span class="tag">trivy scan</span>
  </div>

  <h2>v1 Summary — {name1}</h2>
  <div class="cards">{cards_row(counts1)}</div>

  <h2>v1 Charts</h2>
  <div style="display:flex;gap:24px;flex-wrap:wrap;margin-bottom:8px">
    <img src="data:image/png;base64,{bar_b64}" alt="Bar" style="border-radius:8px;border:1px solid #e5e7eb;background:#fff;height:300px"/>
    <img src="data:image/png;base64,{pie1_b64}" alt="Pie" style="border-radius:8px;border:1px solid #e5e7eb;background:#fff;height:300px"/>
  </div>

  <h2>Top 20 HIGH &amp; CRITICAL — v1 ({name1})</h2>
  <table>
    <thead><tr><th>CVE ID</th><th>Package</th><th>Installed</th><th>Fixed Version</th><th>Severity</th><th>Description</th></tr></thead>
    <tbody>{vuln_rows(vulns1)}</tbody>
  </table>

  {compare_section}

  <footer>Made with IBM Bob &nbsp;·&nbsp; Powered by <a href="https://trivy.dev" style="color:#3b82d4">Trivy</a></footer>
</div>
</body>
</html>"""

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n[DONE] Report saved: {OUTPUT}")
print(f"       Open with: explorer.exe {OUTPUT}")
