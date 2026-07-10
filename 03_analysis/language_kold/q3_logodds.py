# -*- coding: utf-8 -*-
"""
Log-odds ratio (Monroe 2008, Dirichlet prior) — 그룹별 특징 어휘
타겟 그룹 vs. 전체 나머지 댓글 비교
공백 split + 2글자 이상 필터 (형태소 없이도 개념은 충분히 드러남)
"""
import json, math, re
from collections import Counter

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ── 단독 표적 + OFF_span 있는 것만 ──────────────────────────
single = [d for d in data
          if d.get("OFF") and
             "&" not in str(d.get("GRP", "")) and
             (d.get("OFF_span") or "").strip()]

def tokenize(text):
    tokens = re.split(r"\s+", text.strip())
    return [t for t in tokens if len(t) >= 2]

def get_grp(d):
    grp = str(d.get("GRP", ""))
    return grp.split("-")[-1] if "-" in grp else grp

# ── 그룹별 vocab 구축 ────────────────────────────────────────
from collections import defaultdict
grp_counts = defaultdict(Counter)
for d in single:
    g = get_grp(d)
    for tok in tokenize(d["OFF_span"]):
        grp_counts[g][tok] += 1

target_groups = ["black", "feminist", "islam", "korean_chinese", "female", "male", "LGBTQ+", "chinese"]

# ── Monroe log-odds with Dirichlet prior ────────────────────
def log_odds_vs_rest(target_grp, grp_counts, alpha=0.01, top_n=15):
    fg = grp_counts[target_grp]
    # background = 나머지 모든 그룹 합산
    bg = Counter()
    for g, c in grp_counts.items():
        if g != target_grp:
            bg.update(c)

    vocab = set(fg) | set(bg)
    n_fg = sum(fg.values())
    n_bg = sum(bg.values())

    scores = {}
    for w in vocab:
        f1 = fg.get(w, 0) + alpha
        f2 = bg.get(w, 0) + alpha
        # log-odds
        lo = math.log(f1 / (n_fg + alpha * len(vocab) - f1)) \
           - math.log(f2 / (n_bg + alpha * len(vocab) - f2))
        # variance (Monroe 식)
        var = 1/f1 + 1/f2
        z = lo / math.sqrt(var)
        scores[w] = (z, lo, fg.get(w, 0))

    # z-score 기준 정렬, fg 최소 3회 이상
    ranked = sorted([(w, s) for w, s in scores.items() if s[2] >= 3],
                    key=lambda x: -x[1][0])
    return ranked[:top_n]

out = []
out.append("=" * 65)
out.append("  Log-odds ratio: 그룹별 특징 어휘 (vs. 나머지 전체)")
out.append("  Monroe 2008 / Dirichlet prior α=0.01 / min freq 3")
out.append("=" * 65)

for grp in target_groups:
    if grp not in grp_counts:
        out.append(f"\n[{grp}] — 데이터 없음")
        continue
    n = sum(grp_counts[grp].values())
    n_doc = sum(1 for d in single if get_grp(d) == grp)
    ranked = log_odds_vs_rest(grp, grp_counts)
    out.append(f"\n[{grp}]  (OFF_span 토큰 수={n}, 댓글 수={n_doc})")
    out.append(f"  {'순위':<4}  {'토큰':<12}  {'z-score':>8}  {'raw_freq':>8}")
    out.append(f"  {'-'*40}")
    for rank, (w, (z, lo, freq)) in enumerate(ranked, 1):
        out.append(f"  {rank:<4}  {w:<12}  {z:>8.2f}  {freq:>8}")

result = "\n".join(out)
with open(BASE + r"\03_analysis\language_kold\q3_logodds_result.txt", "w", encoding="utf-8") as f:
    f.write(result)

print("DONE -> q3_logodds_result.txt")
