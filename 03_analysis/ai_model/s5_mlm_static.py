"""S5: 두 측정 빠른 비교 — (1) MLM fill-mask 정성, (2) static-성격 WEAT(input embedding)."""
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForMaskedLM, AutoTokenizer

from word_sets import TARGETS as TG, ATTR_UNPLEASANT, ATTR_PLEASANT

TARGETS = {k: [w for w in v if w not in ("재중동포", "성소수자")] for k, v in TG.items()}

MODEL_ID = "klue/roberta-base"
print(f"[load] {MODEL_ID}")
tok = AutoTokenizer.from_pretrained(MODEL_ID)
mlm = AutoModelForMaskedLM.from_pretrained(MODEL_ID)
mlm.eval()
MASK = tok.mask_token
print("[load] OK\n")

# ===== (1) MLM fill-mask 정성 =====
print("=" * 70)
print("(1) MLM fill-mask: '{표적}은/는 [MASK]다' → AI가 채우는 상위 토큰")
print("=" * 70)
TMPLS = ["{}은 {}다.", "{}은 정말 {}다.", "{}은 {}(이)다."]
reps = {"흑인": "흑인", "무슬림": "무슬림", "여성": "여성", "조선족": "조선족",
        "성소수자": "동성애자", "이주민": "이주민", "페미": "페미니스트"}
for grp, w in reps.items():
    print(f"\n[{grp}] ({w})")
    for tm in TMPLS:
        s = tm.format(w, MASK)
        inp = tok(s, return_tensors="pt")
        with torch.no_grad():
            logits = mlm(**inp).logits
        mi = (inp["input_ids"][0] == tok.mask_token_id).nonzero()[0, 0]
        top = logits[0, mi].topk(8).indices.tolist()
        toks = [tok.decode([t]).strip() for t in top]
        print(f"   {tm.format(w, '__'):26s} -> {toks}")

# ===== (2) static-성격 WEAT (input word embeddings) =====
print("\n" + "=" * 70)
print("(2) static-성격 WEAT: KLUE input embedding (contextual 이전 token 임베딩)")
print("=" * 70)
W = mlm.roberta.embeddings.word_embeddings.weight.detach()  # (V,H)


def vec(word):
    ids = tok(word, add_special_tokens=False)["input_ids"]
    return W[ids].mean(0, keepdim=True)


def mat(words):
    return torch.cat([vec(w) for w in words], 0)


def cos_mat(X, Y):
    return F.normalize(X, dim=1) @ F.normalize(Y, dim=1).T


A, B = mat(ATTR_UNPLEASANT), mat(ATTR_PLEASANT)


def s_of(v):
    return cos_mat(v, A).mean().item() - cos_mat(v, B).mean().item()


scores = {g: s_of(mat(ws)) for g, ws in TARGETS.items()}
allAB, nA = torch.cat([A, B], 0), A.shape[0]
rng = np.random.default_rng(0)


def perm_p(v):
    obs = s_of(v)
    null = []
    for _ in range(10000):
        idx = rng.permutation(allAB.shape[0])
        null.append(cos_mat(v, allAB[idx[:nA]]).mean().item() - cos_mat(v, allAB[idx[nA:]]).mean().item())
    null = np.array(null)
    return obs, (np.sum(null >= obs) + 1) / (len(null) + 1), (obs - null.mean()) / (null.std() + 1e-9)

print(f"  spread = {np.std(list(scores.values())):.4f}")
print(f"  {'표적':8s}{'s':>9s}{'p':>8s}{'d':>7s}")
for g in TARGETS:
    o, p, d = perm_p(mat(TARGETS[g]))
    print(f"  {g:8s}{o:9.3f}{p:8.3f}{d:7.2f}")
