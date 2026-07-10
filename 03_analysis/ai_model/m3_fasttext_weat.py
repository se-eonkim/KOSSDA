"""M3 robustness: 진짜 FastText 한국어(cc.ko.300)로 static WEAT 재현."""
import gzip
import numpy as np

from word_sets import TARGETS as TG, GROUP, ATTR_UNPLEASANT, ATTR_PLEASANT

TARGETS = {k: [w for w in v if w not in ("재중동포", "성소수자")] for k, v in TG.items()}
need = set(ATTR_UNPLEASANT) | set(ATTR_PLEASANT)
for ws in TARGETS.values():
    need |= set(ws)

print(f"[load] FastText에서 필요 단어 {len(need)}개 추출...")
vecs = {}
with gzip.open("fasttext/cc.ko.300.vec.gz", "rt", encoding="utf-8", errors="ignore") as f:
    f.readline()
    for line in f:
        sp = line.rstrip().split(" ")
        if sp[0] in need:
            vecs[sp[0]] = np.asarray(sp[1:], dtype=np.float32)
            if len(vecs) == len(need):
                break
miss = need - set(vecs)
print(f"[load] 찾음 {len(vecs)} / 누락 {sorted(miss)}\n")


def mat(ws):
    v = [vecs[w] for w in ws if w in vecs]
    return np.vstack(v) if v else None


def cos_mat(X, Y):
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    Yn = Y / (np.linalg.norm(Y, axis=1, keepdims=True) + 1e-9)
    return Xn @ Yn.T


A = mat([w for w in ATTR_UNPLEASANT if w in vecs])
B = mat([w for w in ATTR_PLEASANT if w in vecs])
allAB, nA = np.vstack([A, B]), A.shape[0]
rng = np.random.default_rng(42)


def s_of(v):
    return cos_mat(v, A).mean() - cos_mat(v, B).mean()


def perm(v):
    obs = s_of(v)
    null = np.empty(10000)
    for i in range(10000):
        idx = rng.permutation(allAB.shape[0])
        null[i] = cos_mat(v, allAB[idx[:nA]]).mean() - cos_mat(v, allAB[idx[nA:]]).mean()
    p = (np.sum(null >= obs) + 1) / (len(null) + 1)
    d = (obs - null.mean()) / (null.std() + 1e-9)
    return obs, p, d


print(f"{'표적':9s}{'그룹':5s}{'s':>8s}{'d':>7s}{'p':>8s}{'유의':>6s}  (cc.ko.300)")
print("-" * 52)
for g in TARGETS:
    m = mat(TARGETS[g])
    if m is None:
        print(f"{g:9s}{GROUP[g]:5s}  (단어 전부 누락)")
        continue
    o, p, d = perm(m)
    print(f"{g:9s}{GROUP[g]:5s}{o:8.3f}{d:7.2f}{p:8.3f}{'***' if p < .05 else '':>6s}")
print("\n→ KLUE input-emb 결과(흑인 유의)와 방향 일치하면 robustness 봉인.")
