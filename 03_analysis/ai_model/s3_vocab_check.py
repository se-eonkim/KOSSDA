"""S3: vocab 토크나이즈 체크 + bare vs template 입력형식 결정."""
import numpy as np
import torch
import torch.nn.functional as F

from s2_env_model import encode, tok
from word_sets import TARGETS, GROUP, ATTR_UNPLEASANT, ATTR_PLEASANT

TEMPLATES = ["그 사람은 {}이다.", "나는 {}을 잘 안다.", "{}에 대한 이야기다.", "여기 {}가 있다."]


def _cos_mat(X, Y):
    """(n,d),(m,d) -> (n,m) 모든 쌍 cos."""
    return F.normalize(X, dim=1) @ F.normalize(Y, dim=1).T


def s_score(wv, A_emb, B_emb):
    """SC-WEAT association: mean cos(w,Unpleasant) - mean cos(w,Pleasant)."""
    a = _cos_mat(wv, A_emb).mean().item()
    b = _cos_mat(wv, B_emb).mean().item()
    return a - b


print("=" * 60)
print("S3-a. 토크나이즈 (subword 개수 / UNK)")
print("=" * 60)
unk = tok.unk_token
for grp, words in TARGETS.items():
    for w in words:
        toks = tok.tokenize(w)
        flag = " <<UNK" if unk in toks else (" <과분할" if len(toks) >= 4 else "")
        print(f"  {grp:7s} {w:8s} -> {len(toks)} {toks}{flag}")

# 임베딩 준비
A_emb = encode(ATTR_UNPLEASANT)
B_emb = encode(ATTR_PLEASANT)

print()
print("=" * 60)
print("S3-b. bare sanity (동의어 응집 / Pleasant 변별)")
print("=" * 60)
for grp, words in TARGETS.items():
    emb = encode(words)
    # 동의어 내부 평균 pairwise cos
    if len(words) > 1:
        sims = [F.cosine_similarity(emb[i:i+1], emb[j:j+1]).item()
                for i in range(len(words)) for j in range(i+1, len(words))]
        coh = np.mean(sims)
    else:
        coh = float("nan")
    pl = F.cosine_similarity(emb, B_emb.mean(0, keepdim=True)).mean().item()
    print(f"  {grp:7s} 응집={coh:.3f}  vs긍정={pl:.3f}")

print()
print("=" * 60)
print("S3-c/d. bare vs template s(w) (입력형식 결정)")
print("=" * 60)
print(f"  {'표적':8s} {'그룹':4s} {'s_bare':>8s} {'s_tmpl':>8s}")
bare_s, tmpl_s = [], []
for grp, words in TARGETS.items():
    sb = s_score(encode(words), A_emb, B_emb)
    # template: 단어별 여러 문장 평균 임베딩 -> 다시 표적 평균
    tvecs = []
    for w in words:
        sents = [t.format(w) for t in TEMPLATES]
        tvecs.append(encode(sents).mean(0, keepdim=True))
    st = s_score(torch.cat(tvecs, 0), A_emb, B_emb)
    bare_s.append(sb)
    tmpl_s.append(st)
    print(f"  {grp:8s} {GROUP[grp]:4s} {sb:8.3f} {st:8.3f}")

r = np.corrcoef(bare_s, tmpl_s)[0, 1]
print(f"\n  bare vs template 상관 r = {r:.3f}  ({'일치(robust)' if r > 0.7 else 'unstable->template 채택'})")
print(f"  s>0 (부정쪽) 표적 수: bare={sum(x>0 for x in bare_s)} tmpl={sum(x>0 for x in tmpl_s)} / {len(bare_s)}")
