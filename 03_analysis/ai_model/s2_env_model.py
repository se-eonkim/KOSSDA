"""S2: KoSimCSE 로드 + sanity 인코딩. encode()는 S3/S4 재사용."""
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

MODEL_ID = "BM-K/KoSimCSE-roberta-multitask"

print(f"[load] {MODEL_ID}")
tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModel.from_pretrained(MODEL_ID)
model.eval()
print("[load] OK")


def encode(texts):
    """문장/단어 리스트 -> CLS 임베딩 (KoSimCSE 표준)."""
    inp = tok(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        out = model(**inp, return_dict=False)
    return out[0][:, 0]  # [CLS]


if __name__ == "__main__":
    emb = encode(["오늘 날씨가 참 좋다", "날씨가 화창하고 맑다", "주식 시장이 폭락했다"])
    sim = F.cosine_similarity(emb[0:1], emb[1:2]).item()
    dif = F.cosine_similarity(emb[0:1], emb[2:3]).item()
    print(f"[sanity] 유사쌍 cos = {sim:.3f}  (높아야)")
    print(f"[sanity] 비유사 cos = {dif:.3f}  (낮아야)")
    print(f"[sanity] 판정: {'OK' if sim > dif else 'FAIL'}  (유사 > 비유사)")
