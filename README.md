# 혐오는 어떻게 남아 재생산되는가?
### 사회에서 언어로, 언어에서 AI로

KOSSDA 대학생 데이터 시각화 공모전 2026 출품작.

> **Q. 혐오는 어떻게 남아 재생산되는가?**
> **A. 혐오는 감정의 분출이 아니라 표적·표현 방식이 반복되는 *구조*다 — 그 구조가 언어에서 '문법'으로 드러나고, AI가 그 구조를 그대로 학습해 다시 써내며 재생산한다.**

혐오는 흔히 "개인의 감정"으로 이해된다. 이 프로젝트는 그 전제를 뒤집는다 — 혐오가 사회에서 어떻게 **인식**되고, 온라인 언어에서 어떤 **구조**로 반복되며, AI 모델에는 어떤 **학습된 표상**으로 남는지를 사회조사·텍스트 코퍼스·언어모델 세 종류의 2차 공개 데이터로 추적했다. 이 프로젝트가 실제로 파고든 것은 감정의 서사가 아니라 **구조 메커니즘**이다 — 표적이 어떻게 반복 결합되고(네트워크 구조), 공격이 어떻게 소수의 양식으로 수렴하며(언어 구조), 그 구조가 모델 표상에 어떻게 흔적을 남기는가(임베딩 구조)를 각 층위에서 수치로 짚었다.

- **최종 결과물:** [출품작 PDF](04_output/final_files/2026공모전_출품작PDF_김세언.pdf) · [PPT](04_output/final_files/2026공모전_출품작PPT_김세언.pptx) · [요약문](04_output/final_files/2026공모전_출품작요약문_김세언.pdf)
- **방법론 상세 (검증 기준·반증 과정):** [`03_analysis/METHODOLOGY.md`](03_analysis/METHODOLOGY.md)

---

## 왜 사회 → 언어 → AI 세 층위인가

세 데이터의 수치를 직접 상관·인과로 잇지 않는다 (표본·시점이 다른 자료를 그렇게 엮는 것은 방법론적 비약이다). 대신 **같은 갈등 축이 층위마다 다른 형태로 프레임된다는 대비**를 근거로 삼는 대비형 삼각측량(triangulation) 구조를 취한다 — Denzin(1978)의 삼각측량 개념을 "수렴"이 아니라 "수렴(축)+발산(프레임)"으로 확장한 것.

| 층위 | 보는 것 | 데이터 | 방법론 |
|---|---|---|---|
| **사회** | 갈등·혐오표현의 인식·경험 (태도) | KOSSDA 사회통합실태조사(2014–24), 인권의식실태조사(2020–24) | 기술통계 |
| **언어** | 그 갈등이 언어로 구조화되는 방식 | [KOLD](https://github.com/boychaboy/KOLD) (Jeong et al. 2022) | log-odds 변별어, co-targeting network, betweenness centrality |
| **AI** | 그 언어적 구조가 모델에 남긴 표상 | KLUE-RoBERTa, fastText(cc.ko.300) | WEAT, MLM fill-mask probing |

각 층위는 서로를 대체하지 않고 검증한다: 사회조사가 "혐오가 실재한다"는 기준선을 세우면, 언어 분석이 그 실재가 **무정형이 아니라 규칙(문법)** 임을 보이고, 모델 분석이 그 문법이 **경험·감정 없이도 학습된 연관**으로 전이될 수 있음을 보인다.

---

## 핵심 발견

**1. 사회 — 혐오는 실재한다**
사람들은 한국 사회의 여러 갈등 축을 과반이 심각하게 인식했고, 절반 이상(57%)이 지난 1년 내 혐오표현을 접촉했다. 그중 70.3%가 온라인에서 발생했다 — 온라인 텍스트를 분석 대상으로 삼는 근거.

**2. 언어 — 무정형이 아니라 규칙이었다**
KOLD 8개 표적 집단의 변별어를 [log-odds ratio + Dirichlet prior](https://languagelog.ldc.upenn.edu/myl/Monroe.pdf)(Monroe et al. 2008)로 추출한 결과, 공격 표현은 **위협·추방 / 병리화 / 오염·감염 / 자질 결함·범죄 / 조롱 / 침묵 명령** 등 소수의 양식으로 수렴했다. 일부 문법소는 표적을 가로질러 재사용됐다 (`나라로`: 무슬림 + 조선족 / `오염` 프레임: 중국인 + 성소수자).

**3. 구조 — 여성이 매개 허브였다**
한 댓글이 여러 집단을 동시에 공격하는 패턴을 co-targeting network(노드=표적, 엣지=공동 표적 빈도)로 구성하고 [betweenness centrality](http://www.analytictech.com/borgatti/papers/centflow.pdf)(가중 그래프, distance=1/weight)를 계산했다. **여성 BC=0.567**로 최고, **남성 BC=0**. 남성은 단독으로 많이 공격받지만 서로 다른 갈등(종교·민족·이념·성소수자)을 잇는 매개 지위에는 있지 않았다 — "많이 공격받는 것"과 "서로 다른 혐오가 만나는 자리에 있는 것"은 다른 축이다.

**4. AI — 경험·감정 없이도 학습된 연관으로 남는다**
[WEAT](https://www.science.org/doi/10.1126/science.aal4230)(Caliskan et al. 2017) effect size로 표적 집단과 부정/긍정 어휘 집합 사이 연관을 측정한 결과, 6개 표적 모두 대조군(d=0.13) 기준을 초과했다. 특히 **흑인 d=2.14로 최댓값** — 한국어 KOLD 코퍼스의 변별어 분석에서 흑인 자생 비하어는 거의 발견되지 않고 한국 내 인구 비율도 0.1% 미만인데도, 모델 내부 표상에서는 가장 강한 부정 연관을 보였다. 직접 경험이 없는 편견이 텍스트를 통해 임베딩 공간에 그대로 이식된 사례로 해석했다. MLM 빈칸 채우기(`"○○은 ___다"`)에서도 표적 집단에 부정어가 유의하게 쏠렸다.

같은 측정을 contextual sentence embedding(KoSimCSE, CLS/mean pooling × centering 조합 4종)으로도 시도했으나 모두 비유의했다(흑인 d=-0.50\~0.00, p>0.49, [`s4_signal_result.txt`](03_analysis/ai_model/s4_signal_result.txt)). 정적 임베딩에서만 신호가 나타난 것은 문장 표상 공간의 anisotropy가 valence 신호를 누르는 현상과 일치한다(May et al. 2019, SEAT). 표상 방식에 따라 같은 편향이 보이거나 안 보인다는 것 자체가 하나의 관찰이다. 코드: [`03_analysis/ai_model/`](03_analysis/ai_model/) (탐색 s2\~s5 → 본분석 m1\~m3 순서로 인덱스 정리됨).

---

## 검증 사례: 시간축 가설 재검토

흑인 표적 댓글이 BLM 발생 시기(2020-05\~06)에 몰려 있는지 `date` 필드로 확인했다([`gate1_black_dates.py`](03_analysis/language_kold/gate1_black_dates.py) → [`gate1_dates_result.txt`](03_analysis/language_kold/gate1_dates_result.txt)). 그런데 무관한 다른 표적(무슬림·여성) 댓글까지 전부 2020년 비중이 낮고 2021-07\~08·2022-01\~02에 몰려 있어, `date`가 댓글 작성 시점이 아니라 수집(크롤링) 시점일 가능성이 드러났다. 이 시간축 가설은 근거로 쓰지 않았다.

대신 흑인 표적 댓글 175개 중 86%가 국제뉴스(BLM·미국 인종 이슈) 제목에, 89%가 YouTube 출처에 달려 있다는 맥락 분석으로 "매개된 담론" 해석의 근거를 대체했다([`gate1_black_titles.py`](03_analysis/language_kold/gate1_black_titles.py)).

> 검증 기준 전체와 다른 사례는 [`METHODOLOGY.md`](03_analysis/METHODOLOGY.md) 참고.

---

## Research Trajectory

이 프로젝트의 언어 축(KOLD 분석)은 튀빙겐 대학교(University of Tübingen)에서 진행한 한국어·이탈리아어·신할라어 비교 혐오표현 연구(cross-linguistic collaboration)에서 시작됐다 — [kold-hate-speech-analysis](https://github.com/se-eonkim/kold-hate-speech-analysis). 그 연구의 두 관찰(여성 = 매개 허브, 흑인 표적 = 수입된 프레임)을 이어받아 이 프로젝트에서 바뀐 부분:

- **방법론:** 정성적 concept taxonomy 프레임 코딩 → log-odds ratio(Monroe et al. 2008, Dirichlet prior) 기반 통계적 유의성 검정
- **범위:** 언어 축 단일 분석 → 사회조사(KOSSDA) 기준선 + AI 모델(WEAT/MLM) 층위를 더한 3층 구조

---

## 방법론 키워드

이 프로젝트에서 다룬 방법론은 아래 방향의 리서치와 맞닿아 있다:

- **Embedding-based bias probing** — WEAT (word/sentence embedding association test), permutation test + FDR 다중비교보정
- **Static vs. contextual representation dissociation** — 동일한 WEAT를 contextual embedding(KoSimCSE, pooling×centering 4조합)에서 먼저 시도해 신호 소실(p>0.49)을 확인한 뒤, 정적 임베딩(KLUE-RoBERTa input embedding·fastText)에서 유의 신호(d≈2.1)를 확인했다(May et al. 2019, SEAT의 anisotropy 관찰과 일치)
- **Masked language model probing** — KLUE-RoBERTa fill-mask
- **Distributional semantics** — log-odds ratio with informative Dirichlet prior (Monroe et al. 2008, "Fightin' Words")
- **Graph-based structural analysis** — weighted co-occurrence network, betweenness centrality (NetworkX)
- **Negated-fact probing과의 연결** — Kassner & Schütze(2020)의 "부정해도 연관이 강화된다"는 발견을 결론의 함의로 인용
- **Dataset bias 인지** — KOLD의 keyword 기반(non-random) 수집, inter-annotator agreement α=0.55를 분석 설계(빈도 대신 구조·양식 중심)에 반영

---

## 한계

- **KOLD 대표성:** offense-prone keyword 기반 수집으로 무작위 표본이 아님 → 빈도·순위는 모집단을 대표하지 않는다고 명시하고, 상대적으로 편향에 둔감한 구조·양식 분석을 중심으로 삼음
- **네트워크 표본:** co-targeting network는 다중 표적 댓글만 사용 (n=278)
- **WEAT/정적 임베딩:** 문장 수준 맥락을 반영하지 못함. 분석 결과는 "학습된 연관"이지 모델의 의견이나 실제 사회적 사실의 증명이 아님
- 검증 기준과 반증 과정(예: 하나의 가설을 세웠다가 데이터로 기각한 사례)은 [`03_analysis/METHODOLOGY.md`](03_analysis/METHODOLOGY.md)에 정리

---

## 폴더 구조

```
01_data/                데이터 출처 메모
03_analysis/
  society_kossda/        KOSSDA 사회조사 전처리·분석 코드
  language_kold/          KOLD 변별어·co-targeting network 분석
  ai_model/                WEAT/MLM 기반 AI 모델 편향 분석 (README.md에 코드 인덱스)
  METHODOLOGY.md           검증 기준 + 반증 사례
04_output/final_files/  출품 최종 PPT·PDF·요약문
```

## 데이터 출처

- 사회통합실태조사(2014–2024), 인권의식실태조사(2020–2024) — 한국행정연구원 / 국가인권위원회, 한국사회과학자료원(KOSSDA) 제공. [인용 서식](03_analysis/society_kossda/meta/citation.md)
- KOLD — Jeong et al. (2022), [Korean Offensive Language Dataset](https://github.com/boychaboy/KOLD), NAVER 뉴스·YouTube 한국어 댓글 40,429개
- WEAT lexicon — Mukherjee et al. (2023) [WEATHub](https://huggingface.co/datasets/iamshnoo/WEATHub); 원 WEAT 정의 Caliskan et al. (2017, *Science*). 상세는 [`lexicon/SOURCE.md`](03_analysis/ai_model/lexicon/SOURCE.md)
- KLUE-RoBERTa (Park et al. 2021) / fastText cc.ko.300 (Bojanowski et al. 2017) — Hugging Face / fasttext.cc

전체 참고문헌은 [출품작 PDF 11페이지](04_output/final_files/2026공모전_출품작PDF_김세언.pdf) 참고.

### fastText 모델 (용량 문제로 gitignore됨)

[`03_analysis/ai_model/m3_fasttext_weat.py`](03_analysis/ai_model/m3_fasttext_weat.py)를 재현하려면 fastText 한국어 사전학습 벡터(cc.ko.300, gzip 텍스트 포맷, 약 1.2GB)를 아래에서 받아 `03_analysis/ai_model/fasttext/cc.ko.300.vec.gz` 경로에 두면 된다.

- 다운로드: <https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.ko.300.vec.gz> (공식 배포처: <https://fasttext.cc/docs/en/crawl-vectors.html>)
- 출처: Bojanowski et al. (2017), *Enriching Word Vectors with Subword Information*
