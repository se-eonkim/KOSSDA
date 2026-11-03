**English** | [한국어](METHODOLOGY.ko.md)

# Methodology and Validation

This document records how I tested each interpretive step on the way to the [final outputs](../04_output/final_files/), and what I did with hypotheses the data rejected.

## 1. Validation Criteria at Each Interpretive Step

Each step of the analysis had an explicit criterion and a scholarly basis for deciding whether a claim could actually be made. "Warranted" marks what the data supports. "Overreach" marks an interpretation it does not support.

### Linking the KOSSDA and KOLD analyses
- **Overreach:** linking survey figures and KOLD language figures through direct correlation or causation. The samples and periods differ, so such a link would be spurious.
- **Warranted:** keeping the perception layer (attitudes) and the language layer (text) explicitly separate, and connecting them only through a contrast: the same conflict axis is *framed differently* at each layer.
- **Basis:** Denzin, *The Research Act* (1978), on triangulation.

### Co-targeting network construction (node = target group, edge = co-targeting frequency)
- **Overreach:** reading an edge as a real social relationship or alliance, or generalizing n=278 (multi-target comments only) to all of KOLD.
- **Warranted:** defining an edge as co-occurrence within one comment and its weight as frequency. The final graph uses raw counts (`weight`), and betweenness centrality is computed with `distance = 1/weight`. I did not apply PMI normalization or a null-model test, and I keep this as a stated limitation.
- **Basis:** Church & Hanks (1990, PMI) for the standard problem of measuring association from co-occurrence.

### Interpreting betweenness centrality
- **Overreach:** converting a graph property, betweenness within this network, directly into "the structural axis of Korean society".
- **Warranted:** limiting the claim to this network: female ranks first in betweenness and weighted degree, which places it between otherwise separate conflicts. This describes a structural position *within this dataset*, not social centrality. The rank depends on the distance definition. With unweighted paths, the residual `others` category ranks first (0.2018) and female second (0.1638), still first among named groups.
- **Basis:** Borgatti (2005), "Centrality and Network Flow," *Social Networks* 27.

### KOLD representativeness
- **Overreach:** treating keyword-based, non-random data as a probability sample of "the structure of conflict in Korean society".
- **Warranted:** limiting the scope to "language structure in offense-prone online contexts", and stating the representativeness limit up front by citing the original collection method.
- **Basis:** Jeong et al. (2022), "KOLD," *EMNLP 2022*.

### Control design in the AI and embedding analysis
- **Overreach:** concluding "the AI learned hate" from target–attribute cosine similarity alone.
- **Warranted:** interpreting an association only after a permutation test of the unpleasant-versus-pleasant attribute contrast. The fill-mask probe separately uses neutral nouns as a control for template bias. [`m1_static_weat.py`](ai_model/m1_static_weat.py) also applies Benjamini-Hochberg correction through `scipy.stats.false_discovery_control`. The reported `d` is the observed score standardized against the permutation null. FDR correction covers the KLUE-RoBERTa analysis; in the fastText replication, Black was the only target with raw p<.05 (p=.0125).
- **Basis:** Caliskan et al. (2017), *Science* 356(6334), on WEAT.
- See [`ai_model/README.md`](ai_model/README.md) for the comparison that led to the static embedding analysis. I first ran the test on contextual KoSimCSE representations. All four pooling and centering configurations were non-significant (p>0.49), so I moved to static embeddings. I read this as sensitivity to representation and probe design, not as absence of the association.

## 2. A Self-Falsification Case: The "Imported Black Frame" Gate

A real case in which I set hypotheses and checked them against the data: one part held up, and I rejected the other myself.

**Question:** do comments targeting Black people concern direct experience in Korea, or mediated discourse such as news and videos from the US?

**Procedure:** I classified the article and video titles of 175 comments targeting Black people (`race-black`; 169 single-target, 6 multi-target) with an international-news keyword list. Code: [`gate1_black_titles.py`](language_kold/gate1_black_titles.py).

| Check | Result |
|---|---|
| Title matches the broad keyword list (which includes "Black" itself, plus terms such as BLM, US, police, race) | 150/175 = 86% (44 matched on "Black" alone) |
| Manual review of the 25 unmatched | Mostly international context as well (English-language titles, the slave trade, and others). I found essentially no titles about conflict involving Black people in Korea. |
| Source = YouTube | 156/175 = 89% |

**Retained, with limits:** the comments sit mostly on content about overseas contexts, which is consistent with a mediated-discourse reading. This does not measure commenters' direct experience or establish where the association in the model came from.

**Second hypothesis (rejected):** comments about Black people would cluster around the BLM period (2020-05 to 06).

When I checked the `date` field ([`gate1_black_dates.py`](language_kold/gate1_black_dates.py), [`gate1_dates_result.txt`](language_kold/gate1_dates_result.txt)), black (175), and also unrelated groups such as islam (1,059) and female (1,129), had almost no comments in 2020 (1.7%, 0.7%, and 3.0%) and concentrated in 2021 and 2022. The `date` field therefore likely reflects **crawl or collection time** rather than posting time, so it could not support a timeline. I **dropped** this hypothesis and kept only the context analysis above (86%/89%).

The lesson: a plausible number cannot serve as evidence until the meaning of the field behind it has been checked. I found no description of this field in the KOLD paper. It surfaced only by inspecting the distribution directly.

## 3. Known Limitations

| Item | Limitation | Mitigation |
|---|---|---|
| KOLD representativeness | Keyword-based collection from offense-prone contexts; non-probability sample | Interpretation limited to structure and patterns rather than frequency and rank |
| Annotation reliability | Inter-annotator agreement of α = 0.55 in the original dataset | Only original labels used (target group, offensive span); no recoding |
| Co-targeting network | Multi-target comments only, n=278 | Centrality interpreted "within this network" only |
| Centrality definition | Female's first rank holds under `distance = 1/weight` and weighted degree, but not under unweighted betweenness | Distance definition stated with every BC value |
| WEAT / static embeddings | No sentence-level context; the permutation test addresses significance only, not causation | Described as "learned association", not as the model's "opinion" or direct proof of social reality |
