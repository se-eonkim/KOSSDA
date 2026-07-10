# -*- coding: utf-8 -*-
"""male 노드의 실제 엣지와 BC=0 이유 확인"""
import json
from collections import Counter
import networkx as nx
from networkx.algorithms import community as nxc

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

multi = [d for d in data if "&" in str(d.get("GRP", ""))]

def parse_grps(grp_str):
    parts = [g.strip() for g in grp_str.split("&")]
    return [p.split("-")[-1] for p in parts]

edges = []
for d in multi:
    grps = parse_grps(str(d["GRP"]))
    for i in range(len(grps)):
        for j in range(i+1, len(grps)):
            a, b = sorted([grps[i], grps[j]])
            edges.append((a, b))

edge_counts = Counter(edges)
G = nx.Graph()
for (a, b), w in edge_counts.items():
    G.add_edge(a, b, weight=w)

G_dist = nx.Graph()
for u, v, d in G.edges(data=True):
    G_dist.add_edge(u, v, weight=d["weight"], distance=1/d["weight"])

out = []
def W(s=""): out.append(str(s))

# male의 실제 엣지
W("=== male 노드의 실제 엣지 (weight = 같이 공격한 댓글 수) ===")
male_edges = [(u, v, d["weight"]) for u, v, d in G.edges(data=True)
              if u == "male" or v == "male"]
male_edges_sorted = sorted(male_edges, key=lambda x: -x[2])
for u, v, w in male_edges_sorted:
    other = v if u == "male" else u
    W(f"  male ─── {other:<20} weight={w}")

W()
W("=== female 노드의 실제 엣지 (비교용) ===")
female_edges = [(u, v, d["weight"]) for u, v, d in G.edges(data=True)
                if u == "female" or v == "female"]
female_edges_sorted = sorted(female_edges, key=lambda x: -x[2])
for u, v, w in female_edges_sorted:
    other = v if u == "female" else u
    W(f"  female ─── {other:<20} weight={w}")

W()
W("=== 왜 male BC=0인가: 최단경로 직접 확인 ===")
W("male 이웃 노드들 사이에 direct edge가 있나?")
male_neighbors = list(G.neighbors("male"))
W(f"male 이웃: {sorted(male_neighbors)}")
W()
for i in range(len(male_neighbors)):
    for j in range(i+1, len(male_neighbors)):
        a, b = male_neighbors[i], male_neighbors[j]
        if G.has_edge(a, b):
            w = G[a][b]["weight"]
            # male을 거치는 경로 vs 직접 경로 거리 비교
            direct = 1/w
            via_male = 1/G["male"][a]["weight"] + 1/G["male"][b]["weight"]
            shorter = "직접" if direct <= via_male else "male경유"
            W(f"  {a} ─── {b}: direct거리={direct:.3f}, male경유={via_male:.3f} → 최단={shorter}")
        else:
            W(f"  {a} ─── {b}: direct edge 없음 → male 경유 가능")

W()
W("=== 전체 BC 재확인 ===")
bc = nx.betweenness_centrality(G_dist, weight="distance")
for node, score in sorted(bc.items(), key=lambda x: -x[1]):
    bar = "█" * int(score * 30)
    W(f"  {node:<20} {score:.4f}  {bar}")

result = "\n".join(out)
with open(BASE + r"\03_analysis\language_kold\debug_male_edges_result.txt",
          "w", encoding="utf-8") as f:
    f.write(result)
print("DONE")
