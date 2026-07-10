# -*- coding: utf-8 -*-
"""
Gate 3: female co-target 원문 추출
질문 1: male-female(18개) — 비교 구문 있나? (S4 전환 증거)
질문 2: 이종 교차(islam/korean_chinese/LGBTQ+-female) — 명분 소환 vs 동시표적?
질문 3: feminist-female(46개) — 배경 확인
"""
import json
BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

multi = [d for d in data if "&" in str(d.get("GRP", ""))]

def parse_grps(s):
    return [p.split("-")[-1] for p in (x.strip() for x in s.split("&"))]

def has_pair(grps, a, b):
    return a in grps and b in grps

def extract(pair_a, pair_b, label):
    result = []
    for d in multi:
        grps = parse_grps(str(d["GRP"]))
        if has_pair(grps, pair_a, pair_b) or has_pair(grps, pair_b, pair_a):
            result.append(d)
    return result

out = []
def W(s=""): out.append(str(s))
def SEC(title): W(); W("="*68); W(f"  {title}"); W("="*68)

# ── 질문 1: male-female ───────────────────────────────────────────
cases = extract("male", "female", "male-female")
SEC(f"질문 1: male-female 공동표적 ({len(cases)}개) — 비교 구문 있나?")
W("  [읽기 포인트] '여자는 남자처럼/남자도 하는데' 류 비교 구문 있나?")
W("               female이 직접 공격받나, male이 비교 도구로 소환되나?\n")
for i, d in enumerate(cases, 1):
    grps = parse_grps(str(d["GRP"]))
    W(f"#{i:02d}  표적: {grps}")
    W(f"  제목: {str(d.get('title',''))[:60]}")
    W(f"  OFF_span: {str(d.get('OFF_span',''))}")
    W()

# ── 질문 2: 이종 교차 ─────────────────────────────────────────────
SEC("질문 2: 이종 교차 — 명분 소환 vs 동시표적?")
W("  [읽기 포인트] female이 '이슬람 오면 여성 위험' 같은 명분으로 등장하나?")
W("               아니면 그냥 같이 욕먹나?\n")

for other, label in [("islam","islam-female"), ("korean_chinese","조선족-female"),
                     ("LGBTQ+","LGBTQ-female"), ("feminist","feminist-female")]:
    cases2 = extract("female", other, label)
    W(f"--- {label} ({len(cases2)}개) ---")
    for i, d in enumerate(cases2[:20], 1):  # 최대 20개씩
        grps = parse_grps(str(d["GRP"]))
        W(f"  #{i:02d}  표적: {grps}")
        W(f"       제목: {str(d.get('title',''))[:55]}")
        W(f"       OFF_span: {str(d.get('OFF_span',''))}")
        W()
    if len(cases2) > 20:
        W(f"  ... {len(cases2)-20}개 생략\n")

result = "\n".join(out)
with open(BASE + r"\03_analysis\language_kold\gate3_cotarget_result.txt",
          "w", encoding="utf-8") as f:
    f.write(result)
print("DONE")
for label, n in [("male-female", len(extract("male","female",""))),
                 ("islam-female", len(extract("islam","female",""))),
                 ("korean_chinese-female", len(extract("korean_chinese","female",""))),
                 ("LGBTQ+-female", len(extract("LGBTQ+","female",""))),
                 ("feminist-female", len(extract("feminist","female",""))),]:
    print(f"  {label}: {n}개")
