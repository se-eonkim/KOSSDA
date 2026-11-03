[English](METHODOLOGY.md) | **한국어**

# 방법론 및 검증 과정

이 문서는 최종 결과물([`04_output/final_files/`](../04_output/final_files/))에 도달하기까지 각 해석 지점을 어떤 기준으로 검증했는지, 그리고 세운 가설 중 데이터로 기각된 것은 어떻게 처리했는지를 정리한다.

## 1. 해석 지점별 검증 기준

분석의 각 단계는 "그렇게 말해도 되는가"를 판단할 명시적 기준과 학술적 근거를 두고 진행했다. "타당"은 데이터가 실제로 뒷받침하는 서술, "비약"은 데이터가 뒷받침하지 않는 과잉 해석이다.

### KOSSDA ↔ KOLD 연결
- **비약:** 사회조사 수치와 KOLD 언어 수치를 직접 상관·인과로 연결 (표본·시점이 다른 자료를 그렇게 엮으면 허위상관)
- **타당:** 인식 층위(태도)와 언어화 층위(텍스트)를 명시적으로 분리하고, 같은 갈등 축이 층위마다 *다르게 프레임된다*는 대비로만 연결
- **근거:** Denzin, *The Research Act* (1978) — triangulation

### Co-targeting network 구성 (node=표적 집단, edge=공동 표적 빈도)
- **비약:** edge를 실제 사회적 관계·동맹으로 해석 / n=278(다중표적 댓글만)을 KOLD 전체처럼 일반화
- **타당:** edge = 같은 댓글 안에서의 co-occurrence, weight = 빈도로 명시. 최종 구현은 raw count 기반 가중 그래프 (`weight`), betweenness centrality는 `distance = 1/weight`로 계산 — PMI 정규화나 null model 대비 검정 없이 raw weight를 직접 사용했다는 점은 한계로 남김
- **근거:** co-occurrence 기반 연관 측정의 표준적 문제의식은 Church & Hanks (1990, PMI)

### Betweenness centrality 해석
- **비약:** "네트워크 내 매개중심성"이라는 그래프 속성을 곧장 "한국 사회의 구조축"으로 치환
- **타당:** "이 co-targeting network 안에서 여성이 betweenness·weighted degree 1위 → 서로 다른 갈등을 잇는 매개 위치"로 한정. 사회적 중심성이 아니라 *이 데이터셋 안에서의* 구조적 위치로 서술. 다만 이 순위는 거리 정의에 달려 있다. 비가중 경로에서는 잔여 범주 `others`가 1위(0.2018), 여성이 2위(0.1638)이며, 이름 있는 집단 중에서는 여전히 1위다
- **근거:** Borgatti (2005), "Centrality and Network Flow," *Social Networks* 27

### KOLD 대표성
- **비약:** keyword 기반(non-random) 수집 데이터를 "한국 사회 갈등 구조" 전체의 확률표본처럼 취급
- **타당:** "offense-prone 온라인 맥락의 언어화 구조"로 범위를 한정하고, 원 논문의 수집 방법을 인용해 대표성 한계를 선제적으로 명시
- **근거:** Jeong et al. (2022), "KOLD," *EMNLP 2022*

### AI/임베딩 분석의 control 설계
- **비약:** target–attribute cosine similarity 단독으로 "AI가 혐오를 배웠다"고 단정
- **타당:** 부정 대 긍정 attribute 대비를 permutation test로 유의성 검정한 뒤에만 해석. 빈칸 채우기(MLM)는 별도로 중립 명사를 대조군으로 사용해 template bias를 통제했다. [`m1_static_weat.py`](ai_model/m1_static_weat.py)는 `scipy.stats.false_discovery_control`로 다중비교 보정까지 적용. 보고한 `d`는 관측값을 순열 분포로 표준화한 값이다. FDR 보정은 KLUE-RoBERTa 분석에 적용했고, fastText 재현에서 원 p<.05인 표적은 흑인뿐이다(p=.0125)
- **근거:** Caliskan et al. (2017), *Science* 356(6334) — WEAT
- 정적/contextual 임베딩 중 정적을 채택하게 된 비교 과정은 [`ai_model/README.md`](ai_model/README.md) 참고. 처음에는 contextual KoSimCSE 표상에서 검정했으나 pooling·centering 4개 조건이 모두 비유의(p>0.49)여서 정적 임베딩으로 옮겼다. 이 결과는 연관의 부재가 아니라 표상과 probe 설계에 대한 민감성으로 해석한다

## 2. 반증 사례: "black 수입 프레임" 게이트

가설을 세우고 데이터로 확인 → 일부는 지지, 일부는 스스로 기각한 실제 사례.

**질문:** 흑인 표적 댓글은 국내에서의 직접 경험을 다루는가, 아니면 미국발 뉴스·영상 등 매개된 담론인가?

**절차:** 흑인(`race-black`) 표적 댓글 175개(단독 169 + 다중표적 6)의 기사·영상 제목을 국제뉴스 키워드로 분류. 코드: [`gate1_black_titles.py`](language_kold/gate1_black_titles.py).

| 검증 | 결과 |
|---|---|
| 제목이 넓은 국제뉴스 키워드 목록(`흑인` 자체와 BLM·미국·경찰·인종차별 등 포함)과 매칭 | 150/175 = 86% (44개는 `흑인`만으로 매칭) |
| 미매칭 25개 수동 검토 | 대부분도 국제 맥락 (영어 제목·노예무역 등) — 국내 흑인 갈등 맥락은 사실상 0건 |
| 수집 출처 = YouTube | 156/175 = 89% |

→ **조건부 유지:** 댓글은 주로 해외 맥락 콘텐츠에 달려 있어 매개된 담론 해석과 부합한다. 다만 작성자의 직접 경험이나 모델 속 연관의 출처를 측정한 것은 아니다.

**두 번째 가설(기각):** "BLM 발생 시기(2020-05\~06)에 흑인 관련 댓글이 집중됐을 것이다."

`date` 필드를 확인한 결과([`gate1_black_dates.py`](language_kold/gate1_black_dates.py) → [`gate1_dates_result.txt`](language_kold/gate1_dates_result.txt)), black(175개)뿐 아니라 islam(1,059개)·female(1,129개) 등 무관한 집단들도 전부 2020년 비중이 거의 없고(1.7%·0.7%·3.0%) 2021~2022년에 몰려 있었다. 즉 `date`는 댓글 작성 시점이 아니라 **크롤링/수집 시점**으로 추정되며, 시간축 근거로 쓸 수 없는 필드였다. 이 가설은 **폐기**하고, 시간축 대신 위 맥락 분석(86%/89%)만을 근거로 남겼다.

이 과정은 "그럴듯해 보이는 수치라도 필드의 실제 의미를 검증하지 않으면 근거로 쓸 수 없다"는 점을 보여준다 — `date` 필드의 의미에 대한 설명은 KOLD 원 논문에서 찾지 못했고, 직접 분포를 뜯어봐야 드러났다.

## 3. 한계 (자가 인지)

| 항목 | 한계 | 완화 |
|---|---|---|
| KOLD 대표성 | offense-prone keyword 기반 수집, 비확률 표본 | 빈도·순위 대신 구조·양식 중심 해석으로 제한 |
| 주석 신뢰도 | 원 데이터셋 inter-annotator agreement α = 0.55 | 원 라벨(표적 집단·공격 스팬)만 사용, 자체 재코딩 없음 |
| Co-targeting network | 다중표적 댓글만 사용, n=278 | centrality 해석을 "이 네트워크 내" 로 한정 |
| 중심성 정의 | 여성 1위는 `distance = 1/weight`와 weighted degree에서 성립하고, 비가중 BC에서는 성립하지 않음 | BC 값에 거리 정의를 함께 명시 |
| WEAT / 정적 임베딩 | 문장 수준 맥락 미반영, permutation test는 유의성만 검정 (인과 아님) | "학습된 연관"으로 서술, 모델의 "의견"이나 사회적 실재의 직접 증명으로 확대 해석하지 않음 |
