# -*- coding: utf-8 -*-
"""
게이트 1 보조: black 표적 댓글의 날짜 분포
목적: BLM 시기(2020.5~6) 집중도 확인 → "수입" 시간축 증거
비교군: islam(수입 프레임 2), female(자생 프레임) 와 월별 분포 대조
"""
import json
from collections import Counter

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def ym(d):
    # date 형식 'YYYY-MM-DD' → 'YYYY-MM'
    return (d.get("date") or "")[:7]

def subset(key):
    return [d for d in data if d.get("GRP") and key in d["GRP"]]

black = subset("race-black")
islam = subset("religion-islam")
female = subset("gender-female")

out = []
out.append("=== 게이트 1 보조: 월별 날짜 분포 ===")
out.append("수집기간: 2020-03 ~ 2022-03 / BLM 정점: 2020-05~06")
out.append("")

for name, grp in [("black", black), ("islam", islam), ("female", female)]:
    months = Counter(ym(d) for d in grp)
    total = len(grp)
    # 2020 상반기(BLM 시기) 비율
    blm_window = sum(c for m, c in months.items() if m in ("2020-05", "2020-06", "2020-07"))
    y2020 = sum(c for m, c in months.items() if m.startswith("2020"))
    out.append(f"--- {name} (n={total}) ---")
    out.append(f"  2020-05~07(BLM±): {blm_window}개 ({blm_window/total*100:.1f}%)")
    out.append(f"  2020년 전체: {y2020}개 ({y2020/total*100:.1f}%)")
    out.append(f"  월별(상위 12): " )
    for m, c in months.most_common(12):
        bar = "#" * c
        out.append(f"    {m}: {c:3d} {bar}")
    out.append("")

with open(BASE + r"\03_analysis\language_kold\gate1_dates_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE -> gate1_dates_result.txt")
# 콘솔엔 핵심 수치만 (한글 깨짐 회피용 영문)
for name, grp in [("black", black), ("islam", islam), ("female", female)]:
    months = Counter(ym(d) for d in grp)
    blm = sum(c for m, c in months.items() if m in ("2020-05","2020-06","2020-07"))
    y20 = sum(c for m, c in months.items() if m.startswith("2020"))
    print(f"{name}: n={len(grp)} | 2020-05~07={blm} ({blm/len(grp)*100:.0f}%) | 2020={y20} ({y20/len(grp)*100:.0f}%)")
