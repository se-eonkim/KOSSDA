# WEAT lexicon 출처 (2026-06-21 수집)

원천: **WEATHub** — Mukherjee et al., "Global Voices, Local Biases: Socio-Cultural Prejudices across Languages", EMNLP 2023.
- repo: https://github.com/iamshnoo/weathub
- data: https://huggingface.co/datasets/iamshnoo/WEATHub
- paper: https://aclanthology.org/2023.emnlp-main.981/
- 원 WEAT 카테고리 정의: Caliskan, Bryson & Narayanan 2017 (Science).
- 한국어 = `ko_human`(원어민 번역) / `ko_new`(신규 차원). 본 파일들은 raw.githubusercontent main 브랜치에서 직접 다운로드.

## 저장 파일 ↔ 용도
| 파일 | 카테고리 | 본 분석에서 역할 |
|---|---|---|
| ko_human_weat1.json | Flowers/Insects, **Pleasant/Unpleasant** | ★ Attribute A(Unpleasant)/B(Pleasant) 출처 |
| ko_human_weat2.json | Instruments/Weapons, **Pleasant/Unpleasant** | A/B 동일 확인(교차검증) |
| ko_new_weat11.json | (gender), **OffensiveWords**/RespectfulWords | robustness 대체 자 A' |
| ko_new_weat13.json | **LGBTQ+/이성애**, Prejudice/Pride | 표적 차용 후보(성소수자) |
| ko_new_weat13b.json | LGBTQ+/이성애, Unpleasant/Pleasant | 〃 |
| ko_new_weat15.json | **이주민/비이주민**, Disrespectful/Respectful | 표적 차용 후보(이주민) |

## ⚠️ 주의
- A/B(Unpleasant/Pleasant) = valence(부정/긍정)지 "혐오" 아님 → 설계문서 §0 CLAIM 규율.
- 흑인(race) target은 한국어 WEATHub에 **없음** → KOLD 기반 자체 구성 필요.
- weat1·weat2의 attr1/attr2는 동일 25단어(원본 표준).
