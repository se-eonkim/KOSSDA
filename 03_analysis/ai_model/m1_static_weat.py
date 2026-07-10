"""M1 메인: static WEAT (KLUE-RoBERTa input embedding). SC-WEAT + FDR 보정."""
import numpy as np
import torch
import torch.nn.functional as F
from scipy.stats import false_discovery_control
from transformers import AutoModelForMaskedLM, AutoTokenizer

from word_sets import TARGETS as TG, GROUP, ATTR_UNPLEASANT, ATTR_PLEASANT

TARGETS = {k: [w for w in v if w not in ("재중동포", "성소수자")] for k, v in TG.items()}

MODEL_ID = "klue/roberta-base"
print(f"[load] {MODEL_ID}")
tok = AutoTokenizer.from_pretrained(MODEL_ID)
mlm = AutoModelForMaskedLM.from_pretrained(MODEL_ID)
W = mlm.roberta.embeddings.word_embeddings.weight.detach()
print("[load] OK\n")


def vec(w):
    ids = tok(w, add_special_tokens=False)["input_ids"]
    return W[ids].mean(0, keepdim=True)


def mat(ws):
    return torch.cat([vec(w) for w in ws], 0)


def cos_mat(X, Y):
    return F.normalize(X, dim=1) @ F.normalize(Y, dim=1).T


A, B = mat(ATTR_UNPLEASANT), mat(ATTR_PLEASANT)
allAB, nA = torch.cat([A, B], 0), A.shape[0]
rng = np.random.default_rng(42)


def s_of(v):
    return cos_mat(v, A).mean().item() - cos_mat(v, B).mean().item()


def perm(v):
    obs = s_of(v)
    null = np.array([
        cos_mat(v, allAB[(idx := rng.permutation(allAB.shape[0]))[:nA]]).mean().item()
        - cos_mat(v, allAB[idx[nA:]]).mean().item()
        for _ in range(10000)
    ])
    p = (np.sum(null >= obs) + 1) / (len(null) + 1)
    d = (obs - null.mean()) / (null.std() + 1e-9)
    return obs, p, d


rows = []
for g in TARGETS:
    o, p, d = perm(mat(TARGETS[g]))
    rows.append((g, GROUP[g], o, d, p))

p_fdr = false_discovery_control([r[4] for r in rows], method="bh")

print(f"{'표적':9s}{'그룹':5s}{'s':>8s}{'d':>7s}{'p':>8s}{'p_FDR':>8s}{'유의':>6s}")
print("-" * 52)
for (g, grp, o, d, p), pf in zip(rows, p_fdr):
    sig = "***" if pf < .05 else ("." if p < .05 else "")
    print(f"{g:9s}{grp:5s}{o:8.3f}{d:7.2f}{p:8.3f}{pf:8.3f}{sig:>6s}")

# 그룹 평균 (dissociation 핵심)
print("\n[dissociation] 그룹 평균 d:")
for grp in ("수입", "자생", "입장"):
    ds = [d for (_, gg, _, d, _) in rows if gg == grp]
    print(f"  {grp}: mean d = {np.mean(ds):.2f}  (표적 {len(ds)}개)")
print("  핵심: 흑인(수입,경험0) vs 조선족(자생,경험有) 같은 수준이면 dissociation.")
