"""Batch C — 인권의식 하모나이즈 → build/b3_year_target.csv, b3_year_target_full.csv, b3_year_context.csv
가중: 표준화(wgt_s/wt_s/wt). 표적/경로 -1=비해당(접촉 안 함). 게이트·심각성 역방향(1매우~4전혀).
경로 버그 수정: 유튜브=라벨'인터넷 방송'으로 식별(TV 충돌 회피), 분모=접촉자 통일."""
import os, sys, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

BUILD = os.path.join(C.BASE, "build")
os.makedirs(BUILD, exist_ok=True)
TARGET_ORDER = ["female", "male", "immigrant", "sexual_minority"]

def wmean_ind(ind, w):
    """가중 비율(%) — ind: 0/1 bool Series, w: weight (같은 인덱스)."""
    W = w.sum()
    return float((w * ind.astype(float)).sum() / W) * 100 if W > 0 else float("nan")

def wmean(x, w):
    W = w.sum()
    return float((w * x.astype(float)).sum() / W) if W > 0 else float("nan")

trows, frows, crows = [], [], []
for f in C.files("ingwon"):
    yr = C.survey_year(f)
    df, meta, lab, vl = C.read(f)
    wv = C.weight_var(meta.column_names)
    w = df[wv]

    # ---- 표적 (4키 + 전체15) ----
    tg = C.find_b3_targets(lab)
    for key in TARGET_ORDER:
        v = tg.get(key)
        if not v:
            continue
        s = df[v]
        contacted = s.isin([0, 1])            # 접촉자
        n_total = len(df)
        n_contact = int(contacted.sum())
        pct_contact = wmean_ind((s == 1)[contacted], w[contacted])
        pct_total = wmean_ind(s == 1, w)      # -1·0 모두 분모, 1만 분자
        trows.append([yr, key, v, round(pct_contact, 1), round(pct_total, 1), n_contact, n_total])

    # 전체 표적(라벨의 집단명)
    for c, l in lab.items():
        if "혐오표현 대상" in l and not c.endswith("t") and ":" in l:
            grp = l.split(":")[-1].strip()
            if grp in ("기타",) or grp == "":
                continue
            s = df[c]; contacted = s.isin([0, 1])
            if contacted.sum() == 0:
                continue
            frows.append([yr, grp, c, round(wmean_ind((s == 1)[contacted], w[contacted]), 1),
                          round(wmean_ind(s == 1, w), 1), int(contacted.sum()), len(df)])

    # ---- 맥락 (경험률·강도·심각성·경로) ----
    gate = C.find_by_label(lab, must_all=["혐오표현", "들어"], must_none=["대상", "경로"])
    g = df[gate].where(df[gate].isin([1, 2, 3, 4]))
    gv = g.notna()
    exp_top1 = wmean_ind((g == 1)[gv], w[gv])
    exp_top12 = wmean_ind(g.isin([1, 2])[gv], w[gv])
    exp_any = wmean_ind(g.isin([1, 2, 3])[gv], w[gv])
    exp_mean = wmean((5 - g)[gv], w[gv])      # 매우자주=4 ... 전혀=1

    # 표적폭: 접촉자 중 4표적 합
    tvars = [tg[k] for k in TARGET_ORDER if k in tg]
    M = df[tvars].apply(lambda s: (s == 1).astype(int))
    contacted_any = df[tvars[0]].isin([0, 1])
    breadth = wmean(M.sum(axis=1)[contacted_any], w[contacted_any])

    # 심각성 q26 (2021+)
    sev = C.find_by_label(lab, must_all=["혐오표현", "심각"])
    if sev:
        sv = df[sev].where(df[sev].isin([1, 2, 3, 4])); svv = sv.notna()
        sev_pct = round(wmean_ind(sv.isin([1, 2])[svv], w[svv]), 1)
    else:
        sev_pct = ""

    # 경로 (접촉자 분모): 포털/커뮤니티, 온라인any(포털+메신저+SNS+인터넷방송)
    def chan(kw):
        return next((c for c, l in lab.items()
                     if "혐오표현 접촉 경로" in l and kw in l and not c.endswith("t")), None)
    portal = chan("포털")
    online_kws = ["포털", "메신저", "사회관계망", "인터넷 방송"]   # ⚠ 'TV' 안 씀(유튜브 충돌)
    online_vars = [chan(k) for k in online_kws]; online_vars = [v for v in online_vars if v]
    if portal:
        base = df[portal].isin([0, 1])
        portal_pct = round(wmean_ind((df[portal] == 1)[base], w[base]), 1)
        any_online = (df[online_vars] == 1).any(axis=1)
        online_pct = round(wmean_ind(any_online[base], w[base]), 1)
    else:
        portal_pct = online_pct = ""

    crows.append([yr, round(exp_top1, 1), round(exp_top12, 1), round(exp_any, 1),
                  round(exp_mean, 3), round(breadth, 3), sev_pct, portal_pct, online_pct])

def dump(path, header, rows):
    with open(os.path.join(BUILD, path), "w", encoding="utf-8-sig", newline="") as fp:
        wr = csv.writer(fp); wr.writerow(header); wr.writerows(rows)

dump("b3_year_target.csv", ["survey_year", "target_key", "src_var", "pct_contact", "pct_total", "n_contact", "n_total"], trows)
dump("b3_year_target_full.csv", ["survey_year", "target_label", "src_var", "pct_contact", "pct_total", "n_contact", "n_total"], frows)
dump("b3_year_context.csv", ["survey_year", "exp_top1", "exp_top1_2", "exp_any", "exp_mean", "breadth", "severe_pct", "portal_pct", "online_any_pct"], crows)

print("target rows:", len(trows), "| full:", len(frows), "| context:", len(crows))
print("\n-- context (가중) --")
print("yr   top1  top12  any  mean  breadth  severe portal onlineAny")
for r in crows:
    print(f"{r[0]} {r[1]:5} {r[2]:5} {r[3]:5} {r[4]:5} {r[5]:6} {str(r[6]):>5} {str(r[7]):>5} {str(r[8]):>6}")
print("\n-- 표적 (접촉자 기준 %) --")
for r in trows:
    print(f"  {r[0]} {r[1]:16} {r[3]:5}  (전체 {r[4]})")
