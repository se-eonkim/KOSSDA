"""Fig A·B 시각화 추출용 raw 데이터 → csv + txt."""
import csv
import re
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

# ========== Fig B: weat_results.csv 가공 ==========
EXP = {"수입": "경험 없음", "자생": "경험 있음", "입장": "—"}
src = list(csv.DictReader(open("weat_results.csv", encoding="utf-8-sig")))
figb = []
for r in src:
    figb.append({
        "target": r["target"], "group": r["group"], "experience": EXP[r["group"]],
        "klue_d": r["klue_d"], "klue_p_fdr": r["klue_p_fdr"],
        "sig": "Y" if float(r["klue_p_fdr"]) < 0.05 else "N",
        "ft_d": r["ft_d"], "ft_p": r["ft_p"],
        "ft_sig": "Y" if (r["ft_p"] and float(r["ft_p"]) < 0.05) else "N",
    })
figb.sort(key=lambda x: -float(x["klue_d"]))
with open("fig_b_data.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(figb[0].keys()))
    w.writeheader(); w.writerows(figb)

with open("fig_b_data.txt", "w", encoding="utf-8") as f:
    f.write("=== Fig B (dissociation 막대) raw ===\n")
    f.write("막대 높이=klue_d, 색=group, 유의=sig(FDR), robust=ft_sig\n\n")
    f.write(f"{'표적':9s}{'그룹':5s}{'경험':9s}{'d':>7s}{'p_FDR':>8s}{'유의':>5s}{'FT_d':>7s}{'FT유의':>7s}\n")
    for x in figb:
        f.write(f"{x['target']:9s}{x['group']:5s}{x['experience']:9s}{x['klue_d']:>7s}"
                f"{x['klue_p_fdr']:>8s}{x['sig']:>5s}{x['ft_d'] or '-':>7s}{x['ft_sig']:>7s}\n")
    f.write("\n핵심: 흑인(수입·경험없음) d=2.14 — KLUE·FastText 두 모델 유의. 여성 비유의(선택성).\n")

# ========== Fig A: MLM 토큰 추출 ==========
tok = AutoTokenizer.from_pretrained("klue/roberta-base")
mlm = AutoModelForMaskedLM.from_pretrained("klue/roberta-base"); mlm.eval()
MASK = tok.mask_token
SPECIAL = {"[PAD]", "[UNK]", "[CLS]", "[SEP]", MASK, ""}
HANGUL = re.compile(r"[가-힣]")
NEG = {"쓰레기", "바보", "싫어", "싫", "무섭", "무서운", "별로", "죄", "멍청", "한심",
       "역겹", "더럽", "나쁜", "최악", "거지", "병신", "테러리스트", "힘들", "범죄"}


def top_tokens(word, k=40, show=6):
    s = f"{word}은 정말 {MASK}다."
    inp = tok(s, return_tensors="pt")
    with torch.no_grad():
        probs = torch.softmax(mlm(**inp).logits[0], -1)
    mi = (inp["input_ids"][0] == tok.mask_token_id).nonzero()[0, 0]
    top = probs[mi].topk(k)
    out = []
    for p, t in zip(top.values.tolist(), top.indices.tolist()):
        d = tok.decode([t]).strip().lstrip("#")
        if d in SPECIAL or not HANGUL.search(d) or len(d) < 2:
            continue
        out.append((d, round(p, 3)))
        if len(out) == show:
            break
    return out


TARGETS = [("무슬림", "표적"), ("성소수자", "표적", "동성애자"), ("흑인", "표적"),
           ("조선족", "표적"), ("이주민", "표적"), ("페미", "표적", "페미니스트"),
           ("여성", "표적"), ("사람", "대조군"), ("학생", "대조군")]
figa = []
for row in TARGETS:
    label, role = row[0], row[1]
    word = row[2] if len(row) > 2 else label
    toks = top_tokens(word)
    neg = sum(1 for t, _ in toks if any(n in t for n in NEG)) / len(toks)
    figa.append({"target": label, "role": role, "probe_word": word,
                 "tokens": " ; ".join(f"{t}({p})" for t, p in toks),
                 "neg_rate": round(neg, 2)})
with open("fig_a_data.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(figa[0].keys()))
    w.writeheader(); w.writerows(figa)

with open("fig_a_data.txt", "w", encoding="utf-8") as f:
    f.write("=== Fig A (MLM 카드) raw ===\n")
    f.write("template: '{표적}은 정말 [MASK]다' / 상위 의미토큰(확률) / neg_rate=부정칩 비율\n\n")
    for x in figa:
        f.write(f"[{x['role']}] {x['target']} (neg={x['neg_rate']})\n   {x['tokens']}\n")

print("[saved] fig_b_data.csv/txt, fig_a_data.csv/txt")
