# -*- coding: utf-8 -*-
"""
BC 심층 3방향 검증:
 ① winner-take-all: female 제거 시 BC 재분배 — 0이었던 노드가 살아나나?
 ② distance 정의 민감도: 1/weight vs weight vs unweighted 비교
 ③ BC=0 노드 분류: '대체됨'(male형) vs '주변부'(진짜 변두리)
    - 판별: 노드 제거 시 그래프 효율/연결성 변화 + 이웃 수 + 이웃 쌍 우회 가능성
"""
import json
from collections import Counter
import networkx as nx

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

multi = [d for d in data if "&" in str(d.get("GRP", ""))]
def parse_grps(s): return [p.split("-")[-1] for p in (x.strip() for x in s.split("&"))]

edges = []
for d in multi:
    g = parse_grps(str(d["GRP"]))
    for i in range(len(g)):
        for j in range(i+1, len(g)):
            edges.append(tuple(sorted([g[i], g[j]])))
edge_counts = Counter(edges)
G = nx.Graph()
for (a, b), w in edge_counts.items():
    G.add_edge(a, b, weight=w)

def dist_graph(g):
    Gd = nx.Graph()
    for u, v, d in g.edges(data=True):
        Gd.add_edge(u, v, weight=d["weight"], distance=1/d["weight"])
    return Gd

out = []
def W(s=""): out.append(str(s))

# ═══════════════════════════════════════════════════════════
W("="*68)
W("① WINNER-TAKE-ALL 검증: female 제거 후 BC 재분배")
W("="*68)
bc_full = nx.betweenness_centrality(dist_graph(G), weight="distance")
W("\n[원본] BC 상위:")
for n, s in sorted(bc_full.items(), key=lambda x: -x[1])[:8]:
    W(f"  {n:<18} {s:.4f}")

G_nofem = G.copy()
G_nofem.remove_node("female")
bc_nofem = nx.betweenness_centrality(dist_graph(G_nofem), weight="distance")
W("\n[female 제거 후] BC 상위:")
for n, s in sorted(bc_nofem.items(), key=lambda x: -x[1])[:8]:
    delta = s - bc_full.get(n, 0)
    arrow = "↑" if delta > 0.01 else ""
    W(f"  {n:<18} {s:.4f}  (Δ{delta:+.4f}) {arrow}")

# male이 살아나나?
W(f"\n  >> male: {bc_full.get('male',0):.4f} → {bc_nofem.get('male',0):.4f}")
W(f"  >> 해석: female이 독점하던 경로가 male에게 넘어가면 male은 '대체됨',")
W(f"          여전히 0이면 male은 애초에 '주변부'")

# ═══════════════════════════════════════════════════════════
W("\n" + "="*68)
W("② DISTANCE 정의 민감도: 같은 그래프, 다른 거리 정의")
W("="*68)
# (a) distance = 1/weight (현재)
bc_a = nx.betweenness_centrality(dist_graph(G), weight="distance")
# (b) unweighted (모든 엣지 거리 1)
bc_b = nx.betweenness_centrality(G, weight=None)
# (c) weight 그대로 거리로 (강할수록 멀다 — 비상식적, 대조용)
Gw = nx.Graph()
for u, v, d in G.edges(data=True):
    Gw.add_edge(u, v, w=d["weight"])
bc_c = nx.betweenness_centrality(Gw, weight="w")

nodes_sorted = sorted(G.nodes(), key=lambda n: -bc_a[n])
W(f"\n  {'노드':<18} {'1/weight':>9} {'unweighted':>11} {'weight직접':>10}")
W(f"  {'-'*50}")
for n in nodes_sorted[:10]:
    W(f"  {n:<18} {bc_a[n]:>9.4f} {bc_b[n]:>11.4f} {bc_c[n]:>10.4f}")
W(f"\n  >> female이 세 정의 모두에서 1위면 robust, 정의 따라 흔들리면 artifact")

# ═══════════════════════════════════════════════════════════
W("\n" + "="*68)
W("③ BC=0 노드 분류: '대체됨'(male형) vs '진짜 주변부'")
W("="*68)
zero_nodes = [n for n in G.nodes() if bc_full[n] < 1e-9]
W(f"\nBC=0 노드 {len(zero_nodes)}개: {sorted(zero_nodes)}\n")

W(f"  {'노드':<18} {'이웃수':>5} {'최대weight':>9} {'female제거후BC':>13}  판정")
W(f"  {'-'*62}")
rows = []
for n in sorted(zero_nodes, key=lambda x: -G.degree(x)):
    deg = G.degree(n)
    max_w = max((G[n][nb]["weight"] for nb in G.neighbors(n)), default=0)
    bc_after = bc_nofem.get(n, 0)
    # 대체됨 판정: 이웃 많고(≥4) 강한연결(maxw≥3) → male형 / 그 외 주변부
    if deg >= 4 and max_w >= 3:
        verdict = "대체됨(허브인데 0)"
    elif deg >= 4:
        verdict = "약한허브"
    else:
        verdict = "주변부"
    rows.append((n, deg, max_w, bc_after, verdict))
    W(f"  {n:<18} {deg:>5} {max_w:>9} {bc_after:>13.4f}  {verdict}")

W("\n  >> '대체됨': 연결 많은데 BC=0 = female 그림자에 가림 (구조적 발견)")
W("  >> '주변부': 연결 적어 BC=0 = 그냥 변두리 (당연)")

result = "\n".join(out)
with open(BASE + r"\03_analysis\language_kold\gate2_bc_deep_result.txt", "w", encoding="utf-8") as f:
    f.write(result)
print("DONE")
