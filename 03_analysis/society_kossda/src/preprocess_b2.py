"""Batch B — 사회통합 갈등 배터리 하모나이즈 → build/b2_year_pair.csv, b2_pair_summary.csv
가중: 표준화(wt2). 결측 {8,9}→NA. 변수명·쌍수(8↔9) 라벨로 식별."""
import os, sys, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

PAIR_ORDER = ["poverty", "ideology", "labor", "region", "develop", "age", "gender", "religion", "foreigner"]
BUILD = os.path.join(C.BASE, "build")
os.makedirs(BUILD, exist_ok=True)

def wstat(x, w):
    """가중 통계: (mean, pct_high(3+4), pct_top(4), n_valid, na_rate)."""
    valid = x.notna()
    n_valid = int(valid.sum())
    na_rate = round(100 * (1 - n_valid / len(x)), 1)
    xv, wv = x[valid].astype(float), w[valid].astype(float)
    W = wv.sum()
    mean = float((wv * xv).sum() / W)
    hi = float((wv * (xv >= 3)).sum() / W) * 100
    top = float((wv * (xv == 4)).sum() / W) * 100
    return round(mean, 3), round(hi, 1), round(top, 1), n_valid, na_rate

rows = []
for f in C.files("sahoetonghap"):
    yr = C.survey_year(f)
    df, meta, lab, vl = C.read(f)
    pairs = C.find_b2_pairs(lab)
    wv = C.weight_var(meta.column_names)
    w = df[wv]
    for key in PAIR_ORDER:
        if key not in pairs:
            continue
        s = C.b2_series(df, pairs[key])
        mean, hi, top, n, na = wstat(s, w)
        rows.append([yr, key, pairs[key], mean, hi, top, n, na])

with open(os.path.join(BUILD, "b2_year_pair.csv"), "w", encoding="utf-8-sig", newline="") as fp:
    wr = csv.writer(fp)
    wr.writerow(["survey_year", "pair_key", "src_var", "mean", "pct_high", "pct_top", "n", "na_rate"])
    wr.writerows(rows)

# ---- 쌍 요약 (연도값들로) ----
summ = []
for key in PAIR_ORDER:
    yrs = [r for r in rows if r[1] == key]
    if not yrs:
        continue
    highs = [r[4] for r in yrs]
    means = [r[3] for r in yrs]
    summ.append([key, round(float(np.mean(means)), 3), round(float(np.mean(highs)), 1),
                 min(highs), max(highs), round(float(np.std(highs, ddof=1)), 2),
                 len(yrs), f"{min(r[0] for r in yrs)}-{max(r[0] for r in yrs)}"])

with open(os.path.join(BUILD, "b2_pair_summary.csv"), "w", encoding="utf-8-sig", newline="") as fp:
    wr = csv.writer(fp)
    wr.writerow(["pair_key", "mean_allyr", "pct_high_allyr", "high_min", "high_max",
                 "high_sd", "n_years", "year_range"])
    wr.writerows(summ)

print("rows:", len(rows), "| summary pairs:", len(summ))
print("\n-- summary (pct_high, allyr/min/max/sd, n) --")
for s in summ:
    print(f"  {s[0]:10} high={s[2]:5} ({s[3]}-{s[4]}) sd={s[5]:4} n={s[6]} {s[7]}")
