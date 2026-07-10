"""S1 산출물: WEAT 단어 세트. attribute는 WEATHub lexicon json에서 로드(재현성)."""
import json
import os

_LEX = os.path.join(os.path.dirname(__file__), "lexicon")


def _load(fname):
    with open(os.path.join(_LEX, fname), encoding="utf-8") as f:
        return json.load(f)


# --- Attribute (출처: Caliskan 2017 + WEATHub ko_human/weat1) ---
_w1 = _load("ko_human_weat1.json")
ATTR_UNPLEASANT = _w1["attr2"]["examples"]   # A: 부정(valence) — 25
ATTR_PLEASANT = _w1["attr1"]["examples"]     # B: 긍정 baseline — 25

# robustness 대체 자 (출처: WEATHub ko_new/weat11)
_w11 = _load("ko_new_weat11.json")
ATTR_OFFENSIVE = _w11["targ1"]["examples"]   # OffensiveWords

# --- Target sets (중립 지시어, vocab 체크에서 거름) ---
TARGETS = {
    "흑인":     ["흑인", "흑인들"],
    "무슬림":   ["무슬림", "이슬람교도", "이슬람"],
    "여성":     ["여성", "여자", "여성들", "여자들"],
    "조선족":   ["조선족", "중국동포", "재중동포"],
    "성소수자": ["성소수자", "동성애자", "게이", "레즈비언", "퀴어"],
    "이주민":   ["이주민", "이민자", "외국인노동자", "외국인"],
    "페미":     ["페미니스트", "페미"],
}
GROUP = {  # 자생/수입/입장
    "흑인": "수입", "무슬림": "수입",
    "여성": "자생", "조선족": "자생", "성소수자": "자생", "이주민": "자생",
    "페미": "입장",
}

if __name__ == "__main__":
    print(f"A Unpleasant: {len(ATTR_UNPLEASANT)}  B Pleasant: {len(ATTR_PLEASANT)}  Offensive: {len(ATTR_OFFENSIVE)}")
    print(f"표적 {len(TARGETS)}개, 단어 총 {sum(len(v) for v in TARGETS.values())}개")
