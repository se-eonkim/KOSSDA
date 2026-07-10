# -*- coding: utf-8 -*-
"""GRP 값 실제 분포 — muslim/islam 코딩 확인용"""
import json
from collections import Counter

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

single = [d for d in data
          if d.get("OFF") and "&" not in str(d.get("GRP", ""))
          and (d.get("OFF_span") or "").strip()]

# 전체 GRP raw 분포
grp_raw = Counter(str(d.get("GRP", "")) for d in single)
# GRP_clean (마지막 - 뒤)
grp_clean = Counter(str(d.get("GRP","")).split("-")[-1] for d in single)

out = []
out.append("=== GRP raw (단독표적+OFF_span, 상위 40) ===")
for g, n in grp_raw.most_common(40):
    out.append(f"  {n:>5}  {g}")
out.append("")
out.append("=== GRP_clean (상위 40) ===")
for g, n in grp_clean.most_common(40):
    out.append(f"  {n:>5}  {g}")
out.append("")
# muslim/islam/religion 키워드 검색
out.append("=== 'muslim/islam/이슬람/religion' 포함 GRP ===")
for g, n in grp_raw.most_common():
    if any(k in g.lower() for k in ["muslim","islam","religion","이슬람"]):
        out.append(f"  {n:>5}  {g}")

with open(BASE + r"\03_analysis\language_kold\q3_grp_dist_result.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("DONE")
