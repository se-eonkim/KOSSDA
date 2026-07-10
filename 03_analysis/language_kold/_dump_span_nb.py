# -*- coding: utf-8 -*-
"""0329 노트북 전체(코드+마크다운)를 UTF-8 텍스트로 덤프 — frame 파이프라인 정독용"""
import json
BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
nb = json.load(open(BASE + r"\03_analysis\language_kold\KOLD 분석\0329_offensivespan.ipynb", encoding="utf-8"))
out = []
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"])
    if not src.strip():
        continue
    tag = "MD" if c["cell_type"] == "markdown" else "CODE"
    out.append(f"\n{'='*60}\n[{tag} CELL {i}]\n{'='*60}\n{src}")
open(BASE + r"\03_analysis\language_kold\_span_full.txt", "w", encoding="utf-8").write("\n".join(out))
print("DONE -> _span_full.txt", len(nb["cells"]), "cells")
