"""Fig B 베이스: dissociation 막대 (Figma 후보정용). weat_results.csv 직결."""
import csv
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 한글 폰트
for cand in ("Malgun Gothic", "AppleGothic", "NanumGothic"):
    if any(cand in f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False

rows = list(csv.DictReader(open("weat_results.csv", encoding="utf-8-sig")))
for r in rows:
    r["d"] = float(r["klue_d"])
    r["sig"] = float(r["klue_p_fdr"]) < 0.05
rows.sort(key=lambda r: r["d"])  # barh 아래→위

COLOR = {"수입": "#c0392b", "자생": "#2c7fb8", "입장": "#9b7fb8"}
labels, vals, colors, edges = [], [], [], []
for r in rows:
    labels.append(r["target"])
    vals.append(r["d"])
    if not r["sig"]:
        colors.append("#cfcfcf"); edges.append("#cfcfcf")
    else:
        c = COLOR[r["group"]]
        colors.append(c)
        edges.append("#7d1f14" if r["target"] == "흑인" else c)

fig, ax = plt.subplots(figsize=(8.2, 4.6))
bars = ax.barh(labels, vals, color=colors, edgecolor=edges,
               linewidth=[2.4 if l == "흑인" else 0 for l in labels], zorder=3)
for r, v in zip(rows, vals):
    ax.text(v + (0.04 if v >= 0 else -0.04), r["target"], f"{v:.2f}",
            va="center", ha="left" if v >= 0 else "right", fontsize=11,
            fontweight="bold" if r["target"] == "흑인" else "normal")

ax.axvline(0, color="#999", lw=0.8)
ax.set_xlim(-0.6, 2.5)
ax.set_xlabel("부정 연관 강도 (effect size d)", fontsize=11)
ax.set_title("경험한 적 없는데, 편견은 가장 강하다", fontsize=15, fontweight="bold", loc="left", pad=12)
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(length=0)
ax.grid(axis="x", color="#eee", zorder=0)

# 범례
from matplotlib.patches import Patch
leg = [Patch(fc="#c0392b", label="수입(경험 없음)"), Patch(fc="#2c7fb8", label="자생(경험 있음)"),
       Patch(fc="#9b7fb8", label="입장"), Patch(fc="#cfcfcf", label="비유의")]
ax.legend(handles=leg, loc="lower right", fontsize=9, frameon=False)

fig.text(0.01, 0.01, "KLUE 입력 임베딩 · FastText도 흑인 d=2.19 일치 · 탐색적, 이 모델에서",
         fontsize=8, color="#888")
fig.tight_layout()
fig.savefig("fig_b_base.png", dpi=200, bbox_inches="tight")
fig.savefig("fig_b_base.svg", bbox_inches="tight")
print("[saved] fig_b_base.png / fig_b_base.svg")
print("폰트:", plt.rcParams["font.family"])
