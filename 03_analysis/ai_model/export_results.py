"""raw 결과 CSV 통합 export (시각화용). M1 KLUE + M3 FastText + M2 MLM 부정율."""
import csv
import gzip
import numpy as np
import torch
import torch.nn.functional as F
from scipy.stats import false_discovery_control
from transformers import AutoModelForMaskedLM, AutoTokenizer

from word_sets import TARGETS as TG, GROUP, ATTR_UNPLEASANT, ATTR_PLEASANT

TARGETS = {k: [w for w in v if w not in ("재중동포", "성소수자")] for k, v in TG.items()}
SEED = 42


def cos_np(X, Y):
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    Yn = Y / (np.linalg.norm(Y, axis=1, keepdims=True) + 1e-9)
    return Xn @ Yn.T


def weat(target_mat, A, B):
    allAB, nA = np.vstack([A, B]), A.shape[0]
    rng = np.random.default_rng(SEED)
    obs = cos_np(target_mat, A).mean() - cos_np(target_mat, B).mean()
    null = np.empty(10000)
    for i in range(10000):
        idx = rng.permutation(allAB.shape[0])
        null[i] = cos_np(target_mat, allAB[idx[:nA]]).mean() - cos_np(target_mat, allAB[idx[nA:]]).mean()
    p = (np.sum(null >= obs) + 1) / 10001
    d = (obs - null.mean()) / (null.std() + 1e-9)
    return float(obs), float(p), float(d)


# ===== M1: KLUE input embedding =====
print("[M1] KLUE input-emb ...")
tok = AutoTokenizer.from_pretrained("klue/roberta-base")
mlm = AutoModelForMaskedLM.from_pretrained("klue/roberta-base")
mlm.eval()
W = mlm.roberta.embeddings.word_embeddings.weight.detach().numpy()


def klue_mat(ws):
    return np.vstack([W[tok(w, add_special_tokens=False)["input_ids"]].mean(0) for w in ws])


A1, B1 = klue_mat(ATTR_UNPLEASANT), klue_mat(ATTR_PLEASANT)
klue = {g: weat(klue_mat(ws), A1, B1) for g, ws in TARGETS.items()}
fdr = false_discovery_control([klue[g][1] for g in TARGETS], method="bh")
klue_fdr = dict(zip(TARGETS, fdr))

# ===== M2: MLM 부정율 =====
print("[M2] MLM fill-mask ...")
MASK = tok.mask_token
NEG = {"쓰레기", "바보", "싫어", "싫", "무섭", "무서운", "무서", "별로", "죄", "멍청",
       "한심", "역겹", "더럽", "나쁜", "최악", "거지", "병신", "테러리스트", "힘들", "이상"}
REPS = {"흑인": "흑인", "무슬림": "무슬림", "여성": "여성", "조선족": "조선족",
        "성소수자": "동성애자", "이주민": "이주민", "페미": "페미니스트"}


def negrate(word):
    hit = tot = 0
    for tm in ("{}은 정말 {}다.", "{}은 {}다."):
        inp = tok(tm.format(word, MASK), return_tensors="pt")
        with torch.no_grad():
            lo = mlm(**inp).logits
        mi = (inp["input_ids"][0] == tok.mask_token_id).nonzero()[0, 0]
        for t in lo[0, mi].topk(10).indices.tolist():
            tot += 1
            if any(n in tok.decode([t]).strip() for n in NEG):
                hit += 1
    return hit / tot


mlm_neg = {g: negrate(w) for g, w in REPS.items()}

# ===== M3: FastText =====
print("[M3] FastText 추출 ...")
need = set(ATTR_UNPLEASANT) | set(ATTR_PLEASANT)
for ws in TARGETS.values():
    need |= set(ws)
vecs = {}
with gzip.open("fasttext/cc.ko.300.vec.gz", "rt", encoding="utf-8", errors="ignore") as f:
    f.readline()
    for line in f:
        sp = line.rstrip().split(" ")
        if sp[0] in need:
            vecs[sp[0]] = np.asarray(sp[1:], dtype=np.float32)
            if len(vecs) == len(need):
                break


def ft_mat(ws):
    v = [vecs[w] for w in ws if w in vecs]
    return np.vstack(v) if v else None


A3 = ft_mat([w for w in ATTR_UNPLEASANT if w in vecs])
B3 = ft_mat([w for w in ATTR_PLEASANT if w in vecs])
ft = {}
for g, ws in TARGETS.items():
    m = ft_mat(ws)
    ft[g] = weat(m, A3, B3) if m is not None else (None, None, None)

# ===== CSV =====
out = "weat_results.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    wtr = csv.writer(f)
    wtr.writerow(["target", "group", "klue_s", "klue_d", "klue_p", "klue_p_fdr",
                  "ft_s", "ft_d", "ft_p", "mlm_negrate"])
    for g in TARGETS:
        ks, kp, kd = klue[g]
        fs, fp, fd = ft[g]
        wtr.writerow([g, GROUP[g], round(ks, 4), round(kd, 3), round(kp, 4), round(klue_fdr[g], 4),
                      None if fs is None else round(fs, 4),
                      None if fd is None else round(fd, 3),
                      None if fp is None else round(fp, 4),
                      round(mlm_neg[g], 3)])
print(f"\n[saved] {out}")
