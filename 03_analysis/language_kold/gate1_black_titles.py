# -*- coding: utf-8 -*-
"""
게이트 1: black 표적 댓글의 기사/영상 제목(title) 분포
목적: black 댓글이 국제뉴스(BLM/미국 시위) 맥락인가, 국내 맥락인가 → S7 수입 프레임 생사
"""
import json
from collections import Counter

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# race-black 포함된 모든 댓글 (단독 + 다중표적)
black = [d for d in data if d.get("GRP") and "race-black" in d["GRP"]]

# 국제뉴스 vs 국내 맥락 자동 분류 키워드
intl_kw = ["BLM", "흑인", "미국", "조지", "플로이드", "Floyd", "시위", "인종차별",
           "인종 차별", "아프리카", "트럼프", "바이든", "NBA", "할리우드", "팝",
           "메이저리그", "월드컵", "올림픽", "美", "영국", "유럽", "프랑스",
           "경찰", "폭동", "약탈", "George", "조지아", "백인"]

out = []
out.append("=== 게이트 1: black 표적 댓글 title 분석 ===")
out.append(f"black 포함 댓글 총 {len(black)}개")
out.append("")

# source 분포
src = Counter(d.get("source") for d in black)
out.append(f"source 분포: {dict(src)}")
out.append("")

# title별 집계 (같은 기사에 여러 댓글)
title_counter = Counter(d.get("title", "") for d in black)
out.append(f"고유 title 수: {len(title_counter)}")
out.append("")

# 자동 분류
intl_titles, domestic_titles = [], []
for title, cnt in title_counter.most_common():
    matched = [kw for kw in intl_kw if kw in (title or "")]
    if matched:
        intl_titles.append((title, cnt, matched))
    else:
        domestic_titles.append((title, cnt))

n_intl_c = sum(c for _, c, _ in intl_titles)
n_dom_c = sum(c for _, c in domestic_titles)

out.append("=== 자동 분류 결과 (댓글 수 기준) ===")
out.append(f"국제뉴스 키워드 매칭: {n_intl_c}개 댓글 ({n_intl_c/len(black)*100:.1f}%)")
out.append(f"미매칭(국내/애매): {n_dom_c}개 댓글 ({n_dom_c/len(black)*100:.1f}%)")
out.append("")
out.append(f"고유 title: 국제매칭 {len(intl_titles)} / 미매칭 {len(domestic_titles)}")
out.append("")

out.append("=" * 70)
out.append("[국제뉴스 키워드 매칭 title]  형식: [댓글수] 제목  <매칭키워드>")
out.append("=" * 70)
for title, cnt, kws in intl_titles:
    out.append(f"[{cnt:2d}] {title}   <{','.join(kws)}>")
out.append("")

out.append("=" * 70)
out.append("[미매칭 title — 사용자 직접 판정 필요]")
out.append("=" * 70)
for title, cnt in domestic_titles:
    out.append(f"[{cnt:2d}] {title}")

with open(BASE + r"\03_analysis\language_kold\gate1_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE -> gate1_result.txt")
print(f"black {len(black)}개 | 국제매칭 {n_intl_c} ({n_intl_c/len(black)*100:.0f}%) | 미매칭 {n_dom_c}")
