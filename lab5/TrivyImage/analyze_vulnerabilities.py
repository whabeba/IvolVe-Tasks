import json
import matplotlib.pyplot as plt
import os
import sys

# ── Load report ──────────────────────────────────────────────────────────────
REPORT_FILE = "trivy-report.json"

if not os.path.exists(REPORT_FILE):
    print(f"[ERROR] {REPORT_FILE} not found. Run trivy scan first.")
    sys.exit(1)

with open(REPORT_FILE) as f:
    data = json.load(f)

# ── Parse vulnerabilities ─────────────────────────────────────────────────────
severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
top_vulns = []

results = data.get("Results", [])
for result in results:
    for vuln in result.get("Vulnerabilities") or []:
        sev = vuln.get("Severity", "UNKNOWN").upper()
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["UNKNOWN"] += 1

        if sev in ("CRITICAL", "HIGH"):
            top_vulns.append({
                "CVE":       vuln.get("VulnerabilityID", "N/A"),
                "Package":   vuln.get("PkgName", "N/A"),
                "Installed": vuln.get("InstalledVersion", "N/A"),
                "Fixed":     vuln.get("FixedVersion", "N/A"),
                "Severity":  sev,
            })

# sort: CRITICAL first, then HIGH
top_vulns.sort(key=lambda x: (0 if x["Severity"] == "CRITICAL" else 1))
top_10 = top_vulns[:10]

total = sum(severity_counts.values())
print(f"[INFO] Total vulnerabilities found: {total}")
for k, v in severity_counts.items():
    print(f"       {k}: {v}")

os.makedirs("screenshots", exist_ok=True)

# ── Color palette ─────────────────────────────────────────────────────────────
COLORS = {
    "CRITICAL": "#D72638",
    "HIGH":     "#F4511E",
    "MEDIUM":   "#FFA500",
    "LOW":      "#4CAF50",
    "UNKNOWN":  "#9E9E9E",
}

# ── Chart 1 — Bar Chart ───────────────────────────────────────────────────────
labels = list(severity_counts.keys())
values = list(severity_counts.values())
colors = [COLORS[l] for l in labels]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor="white", linewidth=0.8)

for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            str(val), ha="center", va="bottom", fontsize=12, fontweight="bold", color="#333")

ax.set_title("Vulnerability Count by Severity", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Severity Level", fontsize=12)
ax.set_ylabel("Number of Vulnerabilities", fontsize=12)
ax.set_facecolor("#F9F9F9")
fig.patch.set_facecolor("#FFFFFF")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("screenshots/bar_chart.png", dpi=150)
plt.close()
print("[INFO] Saved: screenshots/bar_chart.png")

# ── Chart 2 — Pie Chart ───────────────────────────────────────────────────────
non_zero = {k: v for k, v in severity_counts.items() if v > 0}

fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    non_zero.values(),
    labels=non_zero.keys(),
    colors=[COLORS[k] for k in non_zero],
    autopct="%1.1f%%",
    startangle=140,
    pctdistance=0.82,
    wedgeprops={"edgecolor": "white", "linewidth": 2},
)

for text in texts:
    text.set_fontsize(12)
    text.set_fontweight("bold")
for autotext in autotexts:
    autotext.set_fontsize(10)
    autotext.set_color("white")
    autotext.set_fontweight("bold")

ax.set_title("Vulnerability Distribution by Severity", fontsize=16, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("screenshots/pie_chart.png", dpi=150)
plt.close()
print("[INFO] Saved: screenshots/pie_chart.png")

# ── Chart 3 — Top 10 HIGH & CRITICAL CVEs Table ───────────────────────────────
if top_10:
    fig, ax = plt.subplots(figsize=(14, max(3, len(top_10) * 0.6 + 1.5)))
    ax.axis("off")

    col_labels = ["CVE ID", "Package", "Installed Ver.", "Fixed Ver.", "Severity"]
    table_data = [
        [v["CVE"], v["Package"], v["Installed"], v["Fixed"] or "No fix", v["Severity"]]
        for v in top_10
    ]

    tbl = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.6)

    # header row styling
    for j in range(len(col_labels)):
        tbl[0, j].set_facecolor("#2C3E50")
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    # data rows styling
    for i, row in enumerate(table_data, start=1):
        sev = row[4]
        row_color = "#FDECEA" if sev == "CRITICAL" else "#FFF3E0"
        for j in range(len(col_labels)):
            tbl[i, j].set_facecolor(row_color)
        tbl[i, 4].set_facecolor(COLORS.get(sev, "#9E9E9E"))
        tbl[i, 4].set_text_props(color="white", fontweight="bold")

    ax.set_title("Top 10 HIGH & CRITICAL Vulnerabilities", fontsize=14,
                 fontweight="bold", pad=10)
    plt.tight_layout()
    plt.savefig("screenshots/top10_cves.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[INFO] Saved: screenshots/top10_cves.png")
else:
    print("[INFO] No HIGH or CRITICAL vulnerabilities found — skipping table chart.")

print("\n[DONE] All charts saved to screenshots/")
print("       Add them to your README:")
print("       ![Bar Chart](screenshots/bar_chart.png)")
print("       ![Pie Chart](screenshots/pie_chart.png)")
print("       ![Top CVEs](screenshots/top10_cves.png)")
