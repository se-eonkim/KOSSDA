# -*- coding: utf-8 -*-
"""
세 가설 실물 검증:
 ① female 'ㅋㅋ' → 조롱/하대 정서인가?
 ② LGBTQ+ '조용히' → 가시성 박탈(살아라/다녀라) vs 시끄럽다(해라/꺼져)?
 ③ male 공기패턴 → 몰려와서/우르르/잠재적/저지르고/범죄가 같은 댓글에 뭉쳐 이주남성 얘긴가?
"""
import json, re
BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def grp(d): return str(d.get("GRP","")).split("-")[-1]
single = [d for d in data
          if d.get("OFF") and "&" not in str(d.get("GRP",""))
          and (d.get("OFF_span") or "").strip()]

out = []
def W(s=""): out.append(s)

# ── ① female ㅋㅋ ───────────────────────────────
W("="*70); W("① female 'ㅋㅋ' 든 OFF_span (정서 확인)"); W("="*70)
fem = [d for d in single if grp(d)=="female" and "ㅋㅋ" in d["OFF_span"]]
W(f"female 단독 총 {sum(1 for d in single if grp(d)=='female')}개 중 ㅋㅋ 포함 {len(fem)}개\n")
for i,d in enumerate(fem[:25],1):
    W(f"#{i}  {d['OFF_span'].strip()}")

# ── ② LGBTQ+ 조용히 ───────────────────────────────
W(""); W("="*70); W("② LGBTQ+ '조용히' 든 OFF_span (가시성박탈 vs 시끄럽다)"); W("="*70)
lg = [d for d in single if grp(d)=="LGBTQ+" and "조용히" in d["OFF_span"]]
W(f"LGBTQ+ 단독 총 {sum(1 for d in single if grp(d)=='LGBTQ+')}개 중 '조용히' 포함 {len(lg)}개\n")
for i,d in enumerate(lg,1):
    # '조용히' 뒤 단어 추출
    m = re.search(r"조용히\s*(\S+)", d["OFF_span"])
    after = m.group(1) if m else "?"
    W(f"#{i}  [조용히+{after}]  {d['OFF_span'].strip()}")

# ── ③ male 공기 ───────────────────────────────
W(""); W("="*70); W("③ male: 이주남성 프레임 단어 공출현 (몰려/우르르/잠재적/저지르/범죄)"); W("="*70)
B_lex = ["몰려","우르르","잠재적","저지르","범죄"]
A_lex = ["한남"]
male = [d for d in single if grp(d)=="male"]
W(f"male 단독 총 {len(male)}개")
# B층 단어 1개라도 든 댓글
maleB = [d for d in male if any(w in d["OFF_span"] for w in B_lex)]
maleA = [d for d in male if any(w in d["OFF_span"] for w in A_lex)]
W(f"  B층(이주남성 단어 ≥1) 포함: {len(maleB)}개")
W(f"  A층(한남) 포함: {len(maleA)}개")
W(f"  B층 중 2개 이상 공출현: {sum(1 for d in maleB if sum(w in d['OFF_span'] for w in B_lex)>=2)}개\n")
W("[B층 단어 든 male OFF_span 전체]")
for i,d in enumerate(maleB,1):
    hit = [w for w in B_lex if w in d["OFF_span"]]
    W(f"#{i}  <{hit}>  TITLE: {d.get('title','')[:40]}")
    W(f"     {d['OFF_span'].strip()}")

with open(BASE + r"\03_analysis\language_kold\q3_qualcheck_result.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("DONE")
