# AI 모델 편향 분석 — 코드 인덱스

파일명이 실행 순서(탐색 s1~s5 → 본분석 m1~m3)를 따른다. 본분석(m1~m3) 결과가 최종 결과물에 쓰였고, 탐색(s2~s5)은 그 결과에 도달하기까지의 방법 선택 과정(특히 contextual embedding이 실패한 이유)을 남긴 기록이다.

## 본분석 (m1~m3)

| 파일 | 역할 | 출력 |
|---|---|---|
| [`word_sets.py`](word_sets.py) | WEAT target/attribute 단어 세트 정의 (attribute는 [WEATHub lexicon](lexicon/) json에서 로드) | — |
| [`m1_static_weat.py`](m1_static_weat.py) | **메인.** KLUE-RoBERTa input embedding(static) 기반 SC-WEAT + permutation test + FDR 보정 | [`weat_results.csv`](weat_results.csv) |
| [`m2_mlm_probe.py`](m2_mlm_probe.py) | MLM fill-mask (`"○○은 ___다"`) + 중립명사 대조군으로 template bias 통제 | — |
| [`m2_inspect.py`](m2_inspect.py) | m2 결과에서 의미 토큰만 정제 추출 | [`m2_inspect_result.txt`](m2_inspect_result.txt) |
| [`m3_fasttext_weat.py`](m3_fasttext_weat.py) | fastText(cc.ko.300)로 m1 재현 — 서로 다른 두 모델에서 같은 방향 결과가 나오는지 확인하는 robustness 체크 | — |
| [`export_results.py`](export_results.py) | m1(KLUE)+m3(FastText)+m2(MLM) 결과를 시각화용 CSV로 통합 | — |

## 탐색 — static vs. contextual 방법 선택 과정 (s2~s5)

WEAT를 처음에 contextual sentence embedding(KoSimCSE)으로 시도했으나 신호가 죽는 것을 확인하고, 정적 임베딩(m1)으로 전환하게 된 과정이다. [README의 static/contextual dissociation 발견](../../README.md#핵심-발견)의 근거 코드.

| 파일 | 역할 | 출력 |
|---|---|---|
| [`s2_env_model.py`](s2_env_model.py) | KoSimCSE 로드 + sanity check. `encode()`를 s3/s4가 재사용 | — |
| [`s3_vocab_check.py`](s3_vocab_check.py) | 토크나이즈 체크, bare 단어 vs template 문장 입력형식 비교 | [`s3_vocab_result.txt`](s3_vocab_result.txt) |
| [`s4_signal_test.py`](s4_signal_test.py) | CLS vs mean-pooling × raw vs centering 4조합에서 신호 세기 비교 — **전부 비유의(p>0.49)로 확인된 지점** | [`s4_signal_result.txt`](s4_signal_result.txt) |
| [`s5_mlm_static.py`](s5_mlm_static.py) | MLM fill-mask와 static-성격 WEAT(input embedding)를 나란히 비교 — m1으로 이어지는 전환점 | [`s5_result.txt`](s5_result.txt) |

## Figure 재현

- [`fig_export_data.py`](fig_export_data.py), [`fig_b_dissociation.py`](fig_b_dissociation.py) — 발표 자료용 dissociation 막대 그래프(Fig B) 소스
