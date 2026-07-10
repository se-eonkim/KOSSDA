"""S4: 약한 valence 신호 살리기 — CLS vs mean-pooling x raw vs centering.
표적간 분산(신호 세기) + 흑인 vs 자생 상대위치 + 흑인 단독 permutation."""
import numpy as np
import torch
import torch.nn.functional as F

from s2_env_model import model, tok
from word_sets import TARGETS, GROUP, ATTR_UNPLEASANT, ATTR_PLEASANT

# 과분할 단어 제거 (S3-a)
TARGETS = {k: [w for w in v if w not in ("재중동포", "성소수자")] for k, v in TARGETS.items()}


def embed(texts, pooling):
    inp = tok(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        out = model(**inp, return_dict=True)
    hs = out.last_hidden_state               # (B,T,H)
    if pooling == "cls":
        return hs[:, 0]
    mask = inp["attention_mask"].unsqueeze(-1).float()
    return (hs * mask).sum(1) / mask.sum(1)  # mean pooling


def cos_mat(X, Y):
    return F.normalize(X, dim=1) @ F.normalize(Y, dim=1).T


def run(pooling, centering):
    A = embed(ATTR_UNPLEASANT, pooling)
    B = embed(ATTR_PLEASANT, pooling)
    tgt = {g: embed(ws, pooling) for g, ws in TARGETS.items()}
    if centering:
        mu = torch.cat([A, B] + list(tgt.values()), 0).mean(0, keepdim=True)
        A, B = A - mu, B - mu
        tgt = {g: v - mu for g, v in tgt.items()}

    def s(v):
        return cos_mat(v, A).mean().item() - cos_mat(v, B).mean().item()

    scores = {g: s(v) for g, v in tgt.items()}
    spread = np.std(list(scores.values()))

    # 흑인 단독 SC-WEAT permutation (A∪B 재분할)
    allAB = torch.cat([A, B], 0)
    nA = A.shape[0]
    bv = tgt["흑인"]
    obs = s(bv)
    rng = np.random.default_rng(0)
    null = []
    for _ in range(10000):
        idx = rng.permutation(allAB.shape[0])
        Ap, Bp = allAB[idx[:nA]], allAB[idx[nA:]]
        null.append(cos_mat(bv, Ap).mean().item() - cos_mat(bv, Bp).mean().item())
    null = np.array(null)
    p = (np.sum(null >= obs) + 1) / (len(null) + 1)
    d = (obs - null.mean()) / (null.std() + 1e-9)
    return scores, spread, obs, p, d


print(f"{'pooling':8s}{'center':7s}{'spread':>8s}{'흑인s':>8s}{'흑인p':>8s}{'흑인d':>7s}  표적순위(부정쪽순)")
print("-" * 95)
for pooling in ("cls", "mean"):
    for centering in (False, True):
        sc, spread, obs, p, d = run(pooling, centering)
        order = " > ".join(f"{g}" for g, _ in sorted(sc.items(), key=lambda x: -x[1]))
        print(f"{pooling:8s}{str(centering):7s}{spread:8.4f}{obs:8.3f}{p:8.3f}{d:7.2f}  {order}")
