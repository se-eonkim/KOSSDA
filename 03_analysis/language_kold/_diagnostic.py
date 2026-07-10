# -*- coding: utf-8 -*-
"""데이터 구조 진단 — 인코딩 안전하게 결과를 파일로 출력"""
import json
from collections import Counter

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

out = []
out.append(f"총 항목 수: {len(data)}")
out.append(f"키: {list(data[0].keys())}")
out.append("")

# GRP 필드 분포 (gold label로 추정)
grp = Counter(d.get("GRP") for d in data)
out.append(f"=== GRP 고유값 개수: {len(grp)} ===")
for k, v in grp.most_common():
    out.append(f"{v:6d}  {repr(k)}")
out.append("")

# OFF, TGT 필드 값 분포
out.append("=== TGT 분포 ===")
for k, v in Counter(d.get("TGT") for d in data).most_common():
    out.append(f"{v:6d}  {repr(k)}")
out.append("")
out.append("=== OFF 분포 ===")
for k, v in Counter(d.get("OFF") for d in data).most_common():
    out.append(f"{v:6d}  {repr(k)}")
out.append("")

# source 분포
out.append("=== source 분포 ===")
for k, v in Counter(d.get("source") for d in data).most_common():
    out.append(f"{v:6d}  {repr(k)}")
out.append("")

with open(BASE + r"\03_analysis\language_kold\_diag_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE -> _diag_out.txt")
