**English** | [한국어](README.ko.md)

# The Structure and Persistence of Hate across Social Perception, Online Discourse, and Model Representations

*Original Korean title: 혐오는 어떻게 남아 재생산되는가? 사회에서 언어로, 언어에서 AI로 (How Does Hate Persist and Reproduce? From Society to Language, and from Language to AI)*

Single-authored | 2026.04–2026.06 | **Excellence Award** at KOSSDA Data Fair 2026 (among 261 entries from 77 universities)

> **Q.** How does hate persist and reproduce?
>
> **A. (the entry's argument)** Hate is not an outburst of emotion. It is a *structure* in which targets and forms of expression repeat. That structure appears as a "grammar" in language, and AI learns it and writes it again, reproducing it.
>
> Anger cools. The grammar remains. And the machine says it again.

Hate is usually understood as "individual emotion". This project questions that premise. Using three kinds of secondary public data (social surveys, a text corpus, and language models), I traced how hate is **perceived** in society, what **structure** it repeats in online language, and what **learned representation** it leaves in AI models. What the project actually examined is **structural mechanism**: how targets are repeatedly tied together (network structure), how attacks fall into a small set of patterns (language structure), and what trace remains in model representations (embedding structure), measured at each layer.

The result that shaped my later work is at the model layer: the same association was significant in static embeddings and was not detected in contextual representations. Conclusions about a model depend on the representation and probe used to read it.

- **Final outputs (in Korean):** [submission PDF](04_output/final_files/2026공모전_출품작PDF_김세언.pdf) · [slides](04_output/final_files/2026공모전_출품작PPT_김세언.pptx) · [summary](04_output/final_files/2026공모전_출품작요약문_김세언.pdf)
- **Methodology (validation criteria and falsification):** [`03_analysis/METHODOLOGY.md`](03_analysis/METHODOLOGY.md)

---

## Why Three Layers: Society, Language, AI

I do not connect the figures from the three datasets through direct correlation or causation. Linking sources with different samples and periods that way would be a methodological overreach. The design instead rests on a contrast: the same conflict axis is framed differently at each layer. This is a contrastive triangulation that extends Denzin's (1978) concept from convergence alone to convergence (axis) plus divergence (frame).

| Layer | What it looks at | Data | Methods |
|---|---|---|---|
| **Society** | Perception of conflict and experience of hate speech (attitudes) | KOSSDA Social Integration Survey (2014–24), Human Rights Awareness Survey (2020–24) | Descriptive statistics |
| **Language** | How that conflict is structured in language | [KOLD](https://github.com/boychaboy/KOLD) (Jeong et al. 2022) | Log-odds distinctive terms, co-targeting network, betweenness centrality |
| **AI** | What association the models hold | KLUE-RoBERTa, fastText (cc.ko.300) | SC-WEAT, MLM fill-mask probing |

The layers complement rather than replace one another. The surveys set a baseline that hate is present. The language analysis shows that it is **patterned rather than formless**. The model analysis shows that an association can be present in a system that has neither **emotion nor experience**.

---

## Key Findings

**1. Society: hate is present**

Averaged across the 2014–2024 surveys, a majority rated eight of nine conflict axes as serious (the gender axis was 49.1%). Averaged across the 2020–2024 surveys, 57% reported encountering hate speech in the past year, and 70.3% of those encounters happened online. This is the reason for analyzing online text.

**2. Language: what looked formless turned out to be regular**

I extracted distinctive terms for eight KOLD target groups using [log-odds ratios with a Dirichlet prior](https://languagelog.ldc.upenn.edu/myl/Monroe.pdf) (Monroe et al. 2008). Read through my interpretive grouping, attacks fall into a small set of patterns: **threat and expulsion, pathologization, contamination and infection, ascribed deficiency and crime, mockery, and commands to be silent**. Some forms recur across targets: `나라로` ("back to your country") for Muslims and Korean-Chinese people, and contamination framing for Chinese people and LGBTQ+ people. Laughter creates distance; demands for silence control visibility.

**3. Structure: being attacked often is different from standing where hostilities meet**

I built a co-targeting network from comments that attack several groups at once (node = target, edge = co-targeting frequency) and computed [betweenness centrality](http://www.analytictech.com/borgatti/papers/centflow.pdf) on the weighted graph (distance = 1/weight). In this network, **female has the highest BC (0.567) and male has BC = 0**. Male targets are attacked often on their own, yet they do not sit between conflicts over religion, ethnicity, ideology, and sexual orientation. Being attacked often and standing where different hostilities meet are different axes. See the [methodology](03_analysis/METHODOLOGY.md) for how far this reading extends.

**4. Models: an association can be present without emotion or experience**

I measured the association between target groups and negative versus positive word sets using SC-WEAT, based on [WEAT](https://www.science.org/doi/10.1126/science.aal4230) (Caliskan et al. 2017), with permutation testing and FDR correction. **Six target groups showed significant negative-valence associations.** Black targets showed the strongest association, in both KLUE-RoBERTa input embeddings (d=2.14) and the fastText replication (d=2.19). Yet no Black-specific slur appeared among the distinctive terms in KOLD, and the Black population in Korea is very small. Official statistics do not count residents by race; as a rough proxy, [foreign residents from Africa numbered 19,916 in 2018](https://unbiasthenews.org/heard-but-not-seen-being-black-in-south-korea/) (Ministry of Justice data), about 0.04% of [a population of roughly 52 million](https://www.koreatimes.co.kr/southkorea/others/20261028/foreign-resident-population-in-korea-hits-record-266-mil-as-intl-student-numbers-surge). I read this as prejudice arriving through text rather than direct contact. In the fill-mask probe (`"○○은 ___다"`), negative words were clearly more common for target groups than for neutral-noun controls (0.29 vs 0.13).

**5. Static-contextual dissociation: the same test, a different answer**

I ran the same test on static embeddings and on contextual sentence representations (KoSimCSE, CLS or mean pooling, with or without centering). All four contextual configurations were non-significant (Black d=-0.50 to 0.00, p>0.49, [`s4_signal_result.txt`](03_analysis/ai_model/s4_signal_result.txt)), while the static embeddings showed the signal above. This does not mean contextual models hold no such association. Whether the association appears depends on the representation and probe; that dependence is itself an observation. May et al. (2019, SEAT) also report mixed results on sentence encoders, suggesting that the test's assumptions may not hold in general. I did not test the cause here. Code: [`03_analysis/ai_model/`](03_analysis/ai_model/), with an index in its README.

---

## Validation Case: Re-examining the Timeline Hypothesis

I used the `date` field to check whether comments targeting Black people cluster around the BLM period (2020-05 to 06) ([`gate1_black_dates.py`](03_analysis/language_kold/gate1_black_dates.py), [`gate1_dates_result.txt`](03_analysis/language_kold/gate1_dates_result.txt)). Unrelated targets (Muslims, women) also had very few comments in 2020 and concentrated in 2021 and 2022, which suggests that `date` likely reflects crawl time rather than posting time. I did not use this timeline hypothesis as evidence.

I relied on a context analysis instead ([`gate1_black_titles.py`](03_analysis/language_kold/gate1_black_titles.py)). Of the 175 comments targeting Black people, 86% had titles matching a broad international-news keyword list, and 89% came from YouTube. This is consistent with a mediated-discourse reading, but it does not measure commenters' direct experience.

> See [`METHODOLOGY.md`](03_analysis/METHODOLOGY.md) for all validation criteria and other cases.

---

## Research Trajectory

The language layer (KOLD analysis) began in a Korean–Italian–Sinhala cross-linguistic research collaboration at the University of Tübingen: [kold-hate-speech-analysis](https://github.com/se-eonkim/kold-hate-speech-analysis). I carried forward two observations from that study (female as a bridging node, and the hypothesis of an imported frame on Black targets) and changed the following:

- **Method:** from qualitative concept-taxonomy coding to significance testing with log-odds ratios (Monroe et al. 2008, Dirichlet prior)
- **Scope:** from a single language layer to three layers, adding a social-survey baseline (KOSSDA) and a model layer (SC-WEAT, MLM)

The static-contextual dissociation led to my next question: whether information decoded from a representation is actually used by a model.

---

## Methods Used

- **Embedding-based bias probing:** SC-WEAT, permutation test, FDR correction
- **Static vs. contextual representation dissociation:** the same test on contextual embeddings (KoSimCSE, four pooling and centering configurations; p>0.49) and static embeddings (KLUE-RoBERTa input embeddings, fastText; d≈2.1 for Black targets)
- **Masked language model probing:** KLUE-RoBERTa fill-mask
- **Distributional semantics:** log-odds ratio with an informative Dirichlet prior (Monroe et al. 2008, "Fightin' Words")
- **Graph-based structural analysis:** weighted co-occurrence network, betweenness centrality (NetworkX)
- **Link to negated-fact probing:** cited in the discussion: Kassner & Schütze (2020) found that pretrained language models do not distinguish negated from non-negated cloze questions
- **Dataset bias awareness:** KOLD's keyword-based, non-random collection and its inter-annotator agreement of α=0.55 shaped the design, which focuses on structure and patterns rather than frequency

---

## Limitations

- **KOLD representativeness:** collected with offense-prone keywords, so it is not a random sample. Frequency and rank do not represent the population, and the analysis centers on structure and patterns, which are relatively less sensitive to this bias.
- **Network sample:** the co-targeting network uses multi-target comments only (n=278).
- **Language patterns:** the log-odds analysis uses whitespace tokenization.
- **SC-WEAT / static embeddings:** no sentence-level context. The results are "learned associations", not the model's opinion or proof of a social fact.
- See [`03_analysis/METHODOLOGY.md`](03_analysis/METHODOLOGY.md) for validation criteria and the falsification process, including a hypothesis I set and then rejected with the data.

---

## Repository Structure

```
01_data/                Notes on data sources
03_analysis/
  society_kossda/       KOSSDA survey preprocessing and analysis code
  language_kold/        KOLD distinctive-term and co-targeting network analysis
  ai_model/             SC-WEAT and MLM model analysis (code index in README.md)
  METHODOLOGY.md        Validation criteria and falsification cases
04_output/final_files/  Final submitted slides, PDF, and summary (in Korean)
```

## Data Sources

- Social Integration Survey (2014–2024) and Human Rights Awareness Survey (2020–2024): Korea Institute of Public Administration and National Human Rights Commission of Korea, provided by the Korea Social Science Data Archive (KOSSDA). [Citation format](03_analysis/society_kossda/meta/citation.md)
- KOLD: Jeong et al. (2022), [Korean Offensive Language Dataset](https://github.com/boychaboy/KOLD), 40,429 Korean comments from NAVER News and YouTube
- WEAT lexicon: Mukherjee et al. (2023), [WEATHub](https://huggingface.co/datasets/iamshnoo/WEATHub); original WEAT definition by Caliskan et al. (2017, *Science*). Details in [`lexicon/SOURCE.md`](03_analysis/ai_model/lexicon/SOURCE.md)
- KLUE-RoBERTa (Park et al. 2021) and fastText cc.ko.300 (Bojanowski et al. 2017): Hugging Face and fasttext.cc

See slide 11 of the [submission PDF](04_output/final_files/2026공모전_출품작PDF_김세언.pdf) for the full reference list.

### fastText model (excluded through gitignore because of its size)

To reproduce [`03_analysis/ai_model/m3_fasttext_weat.py`](03_analysis/ai_model/m3_fasttext_weat.py), download the pretrained Korean fastText vectors (cc.ko.300, gzip text format, about 1.2 GB) and place them at `03_analysis/ai_model/fasttext/cc.ko.300.vec.gz`.

- Download: <https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.ko.300.vec.gz> (official distribution: <https://fasttext.cc/docs/en/crawl-vectors.html>)
- Source: Bojanowski et al. (2017), *Enriching Word Vectors with Subword Information*
