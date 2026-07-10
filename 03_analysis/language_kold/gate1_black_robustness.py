# -*- coding: utf-8 -*-
"""
게이트 1 보조: black criminalization 0.70 robustness
목적: 0.70이 black 댓글 몇 개·몇 개 토큰에 기반하는가 → 한계 슬라이드 분모
방법: 0329 노트북의 new_concept_map을 추출해 black OFF_span에 적용, frame 분포 재현
"""
import json, re
from collections import Counter, defaultdict

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"

# --- 1. 원 노트북에서 new_concept_map 추출 (exec) ---
nb_path = BASE + r"\03_analysis\language_kold\KOLD 분석\0329_offensivespan.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

concept_map = None
for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    if "new_concept_map" in src and "criminalization" in src and "{" in src:
        # new_concept_map = { ... } 정의 셀
        ns = {}
        exec(src, ns)
        concept_map = ns.get("new_concept_map")
        break

# --- 2. 데이터 로드 ---
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# black 단독 표적 (frame 계산은 원래 single 표적 기준)
black_single = [d for d in data
                if d.get("GRP") == "race-black"
                and (d.get("OFF_span") or "").strip()]

# --- 3. 토큰화 (노트북 로직 간략 재현) ---
def tokens(span):
    out = []
    for tok in str(span).split():
        tok = re.sub(r"[^0-9A-Za-z가-힣]", "", tok)
        if len(tok) > 1:
            out.append(tok)
    return out

# criminalization 토큰 집합
crim_tokens = {k for k, v in (concept_map or {}).items() if v == "criminalization"}

# --- 4. black frame 분포 + criminalization 댓글 추적 ---
concept_counter = Counter()
crim_comments = []   # criminalization 토큰이 든 댓글
for d in black_single:
    toks = tokens(d["OFF_span"])
    hit_crim = []
    for t in toks:
        if t in (concept_map or {}):
            c = concept_map[t]
            concept_counter[c] += 1
            if c == "criminalization":
                hit_crim.append(t)
    if hit_crim:
        crim_comments.append((d["title"], d["comment"], d["OFF_span"], hit_crim))

# row-normalize (other_or_generic 제외 — 노트북 plot 방식)
total_mapped = sum(v for k, v in concept_counter.items())
crim_n = concept_counter.get("criminalization", 0)

out = []
out.append("=== black criminalization 0.70 robustness ===")
out.append(f"criminalization 토큰 집합: {sorted(crim_tokens)}")
out.append("")
out.append(f"black 단독 표적 + OFF_span 있는 댓글: {len(black_single)}개")
out.append(f"매핑된 토큰 총량: {total_mapped}")
out.append(f"criminalization 토큰 발생: {crim_n}회")
out.append(f"criminalization 토큰이 든 댓글 수: {len(crim_comments)}개")
out.append("")
out.append("=== black frame 분포 (concept별 토큰수, row 정규화 전) ===")
for c, n in concept_counter.most_common():
    share = n / total_mapped * 100 if total_mapped else 0
    out.append(f"  {n:3d} ({share:4.1f}%)  {c}")
out.append("")
# other_or_generic 제외 정규화 (heatmap 방식)
filtered = {k: v for k, v in concept_counter.items() if k != "other_or_generic"}
ftot = sum(filtered.values())
out.append("=== other_or_generic 제외 정규화 (heatmap 0.70과 대조) ===")
for c, n in sorted(filtered.items(), key=lambda x: -x[1]):
    out.append(f"  {n/ftot:.2f}  {c}  ({n}/{ftot})")
out.append("")
out.append("=" * 70)
out.append("[criminalization 토큰이 든 black 댓글 전체]")
out.append("=" * 70)
for i, (title, comment, span, hits) in enumerate(crim_comments, 1):
    out.append(f"\n#{i}  <매칭: {hits}>")
    out.append(f"  TITLE: {title}")
    out.append(f"  COMMENT: {comment}")
    out.append(f"  OFF_span: {span}")

with open(BASE + r"\03_analysis\language_kold\gate1_robustness_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE -> gate1_robustness_result.txt")
print(f"black_single={len(black_single)} | crim toks={crim_n} | crim comments={len(crim_comments)} | total_mapped={total_mapped}")
print(f"crim share (with generic)={crim_n/total_mapped:.2f}" if total_mapped else "no tokens")
print(f"crim share (no generic)={crim_n/ftot:.2f}" if ftot else "")
