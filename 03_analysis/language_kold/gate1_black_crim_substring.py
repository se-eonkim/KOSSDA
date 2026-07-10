# -*- coding: utf-8 -*-
"""
black criminalization robustness — substring 직접 카운트
OFF_span이 긴 구라 공백 split이 부정확 → 부분문자열로 범죄 어휘 탐지
"""
import json
from collections import Counter

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

black = [d for d in data if d.get("GRP") == "race-black" and (d.get("OFF_span") or "").strip()]

# criminalization 관련 어휘 (넓게)
crim_lex = ["범죄", "흉기", "강간", "성추행", "사기", "폭력", "도둑", "약탈",
            "살인", "강도", "범죄자", "감옥", "수감", "체포", "테러", "총", "칼"]
# 비교: disgust/dehumanization 등 다른 대표 프레임도 같이
other_lex = {
    "disgust": ["역겹", "혐오", "더럽", "싫"],
    "dehumanization": ["짐승", "동물", "원숭이", "노예"],
    "intelligence": ["멍청", "무식", "아이큐", "지능", "iq"],
}

out = []
out.append("=== black criminalization substring robustness ===")
out.append(f"black 단독 + OFF_span 있는 댓글: {len(black)}개")
out.append("")

# 댓글 단위: criminalization 어휘 1개라도 포함하면 카운트
crim_hit_comments = []
lex_counter = Counter()
for d in black:
    span = d["OFF_span"]
    hits = [w for w in crim_lex if w in span]
    if hits:
        crim_hit_comments.append((d["title"], d["comment"], span, hits))
        for w in hits:
            lex_counter[w] += 1

out.append(f"criminalization 어휘 포함 댓글: {len(crim_hit_comments)}개 / {len(black)} = {len(crim_hit_comments)/len(black)*100:.1f}%")
out.append(f"어휘별 등장 댓글 수: {dict(lex_counter.most_common())}")
out.append("")

for name, lex in other_lex.items():
    hit = sum(1 for d in black if any(w in d["OFF_span"] for w in lex))
    out.append(f"  [비교] {name} 어휘 포함 댓글: {hit}개 ({hit/len(black)*100:.1f}%)")
out.append("")

out.append("=" * 70)
out.append("[criminalization 어휘가 든 black 댓글 전체]")
out.append("=" * 70)
for i, (title, comment, span, hits) in enumerate(crim_hit_comments, 1):
    out.append(f"\n#{i}  <{hits}>")
    out.append(f"  TITLE: {title}")
    out.append(f"  OFF_span: {span}")

with open(BASE + r"\03_analysis\language_kold\gate1_crim_substring_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE")
print(f"black={len(black)} | crim 어휘 포함 댓글={len(crim_hit_comments)} ({len(crim_hit_comments)/len(black)*100:.0f}%)")
print(f"어휘별: {dict(lex_counter.most_common())}")
