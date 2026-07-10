"""KOSSDA 사회 축 공용 모듈 (Batch A).

핵심 사실(검증):
- handle 앞 4자리 = 조사연도 (기탁연도 아님). 사회통합 2014-2024(11), 인권의식 2020-2024(5).
- dta 라벨/값 라벨 인코딩 = cp949이나 pyreadstat가 latin1로 읽음 → fix()로 복원.
- 가중치: 비율/평균엔 '표준화(표본크기 기준)' 사용 — wt2 / wgt_s|wt_s / wt.
- 결측: 사회통합 갈등 배터리 {8,9}=모름/무응답 → NA. 인권의식 표적/경로 -1=비해당(접촉 안 함).
"""
import os, re, glob
import numpy as np
import pyreadstat

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "Data")
FOLDERS = {
    "sahoetonghap": os.path.join(DATA, "사회통합실태조사 2013~2024"),
    "ingwon": os.path.join(DATA, "인권의식실태조사 2019~2024"),
}

# ---- 인코딩 복원 ----
def fix(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin1").decode("cp949")
    except Exception:
        return s

def handle(path):
    return re.search(r"(\d{8})", os.path.basename(path)).group(1)

def survey_year(path):
    return int(handle(path)[:4])

def files(dataset):
    f = glob.glob(FOLDERS[dataset] + "/*.dta") + glob.glob(FOLDERS[dataset] + "/*.DTA")
    return sorted(set(f), key=handle)

def read(path, metadataonly=False):
    """dta 로드 + cp949 라벨 복원. (df, meta, labels) 반환. labels={col: 복원라벨}."""
    df, meta = pyreadstat.read_dta(path, metadataonly=metadataonly)
    labels = {c: fix(meta.column_names_to_labels.get(c) or "") for c in meta.column_names}
    vallabels = {c: {k: fix(v) for k, v in d.items()}
                 for c, d in (meta.variable_value_labels or {}).items()}
    return df, meta, labels, vallabels

# ---- 가중치: 표준화(표본크기 기준) 우선 ----
def weight_var(meta_cols):
    for cand in ("wt2", "wgt_s", "wt_s", "wt"):   # 표준화 → (인권 2020 단일)
        if cand in meta_cols:
            return cand
    return None

# ---- 표준키 ----
# 사회통합 갈등 정도 배터리: 라벨 '갈등 정도-<쌍>'의 쌍 텍스트 → 표준키
B2_PAIRS = {
    "빈곤층과": "poverty", "보수와 진보": "ideology", "근로자와": "labor",
    "수도권과": "region", "개발과": "develop", "젊은층": "age",
    "남자와 여자": "gender", "종교 간": "religion", "내국인과": "foreigner",
}
B2_NA = {8, 9}            # 모름/무응답
B2_VALID = (1, 2, 3, 4)   # 1 전혀~4 매우 심하다

# 인권의식 혐오표현 대상: 라벨 '혐오표현 대상N: <집단>'의 집단 텍스트 → 표준키 (index 매년 이동, 라벨로만 식별)
B3_TARGETS = {"여성": "female", "남성": "male", "이주민": "immigrant", "성소수자": "sexual_minority"}

def find_b2_pairs(labels):
    """{표준키: 변수명} — '갈등 정도-<쌍>' 라벨만(해소/원인/감정거리 제외)."""
    out = {}
    for c, l in labels.items():
        if "갈등 정도" in l and "-" in l:
            for token, key in B2_PAIRS.items():
                if token in l:
                    out[key] = c
    return out

def find_b3_targets(labels, want=None):
    """{표준키: 변수명} — '혐오표현 대상N: <집단>' 라벨로 식별. want=None이면 4대 표적."""
    keys = B3_TARGETS if want is None else {k: v for k, v in B3_TARGETS.items() if v in want}
    out = {}
    for c, l in labels.items():
        if "혐오표현 대상" in l and not c.endswith("t") and ":" in l:
            grp = l.split(":")[-1].strip()       # '대상6: 이주민(...)' → '이주민(...)'
            for token, key in keys.items():
                if grp.startswith(token):         # 이주민(...)·여성·남성·성소수자
                    out[key] = c
    return out

def find_by_label(labels, must_all=(), must_none=(), endswith=None):
    for c, l in labels.items():
        L = l.strip()
        if all(k in L for k in must_all) and not any(k in L for k in must_none):
            if endswith is None or L.endswith(endswith):
                return c
    return None

def b2_series(df, var):
    """갈등 배터리 1-4만 유효, {8,9}→NA."""
    s = df[var].where(df[var].isin(B2_VALID))
    return s
