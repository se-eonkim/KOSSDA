# -*- coding: utf-8 -*-
# 0328_networkX.ipynb 로직 재현 → Gephi import용 nodes/edges CSV
import json, csv, os
from itertools import combinations
from collections import Counter
import networkx as nx

base = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
path = os.path.join(base, "01_data", "raw", "kold_v1.json")
outdir = os.path.join(base, "04_output", "figures")
os.makedirs(outdir, exist_ok=True)

with open(path, encoding="utf-8") as f:
    data = json.load(f)

def extract_groups(grp):
    if grp is None:
        return []
    return [it.split("-")[1] for it in grp.split(" & ") if "-" in it]

# 노트북과 동일: 다중표적(>1) 댓글에서 그룹쌍 추출
edges = []
n_multi = 0
for row in data:
    groups = extract_groups(row.get("GRP"))
    if len(groups) > 1:
        n_multi += 1
        edges.extend(combinations(groups, 2))

edge_counts = Counter(edges)

# 그래프 + BC (distance = 1/weight)
G = nx.Graph()
for (a, b), w in edge_counts.items():
    G.add_edge(a, b, weight=w)

Gd = nx.Graph()
for u, v, d in G.edges(data=True):
    Gd.add_edge(u, v, weight=d["weight"], distance=1 / d["weight"])

bc = nx.betweenness_centrality(Gd, weight="distance")
wdeg = dict(G.degree(weight="weight"))

# 검증: 사용자가 준 값과 일치하는지
print("[검증] multi-target comments =", n_multi, "(기대 278)")
print("[검증] female BC =", round(bc.get("female", 0), 4), "(기대 0.5673)")
print("[검증] male   BC =", round(bc.get("male", 0), 4), "(기대 0.0)")
print("[검증] female wdeg =", wdeg.get("female"), "(기대 103)")

# 색 카테고리 (노트북 attribute_map 기반)
attr = {
    'female': 'Gender', 'male': 'Gender', 'feminist': 'Gender',
    'queer': 'Sexual', 'homosexual': 'Sexual',
    'asian': 'Race', 'black': 'Race', 'white': 'Race', 'chinese': 'Race',
    'korean_chinese': 'Race', 'indian': 'Race', 'southeast_asian': 'Race',
    'progressive': 'Politics', 'conservative': 'Politics',
    'islam': 'Religion', 'christian': 'Religion', 'catholic': 'Religion',
    'age': 'Other', 'socioeconomic_status': 'Other', 'others': 'Other',
}
color = {'Gender': '#AFA9EC', 'Sexual': '#ED93B1', 'Race': '#5DCAA5',
         'Politics': '#F0997B', 'Religion': '#85B7EB', 'Other': '#B4B2A9'}

# nodes.csv
nodes_path = os.path.join(outdir, "fig7-2_cotarget_nodes.csv")
with open(nodes_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Id", "Label", "Category", "Color", "BC", "WeightedDegree"])
    for n in G.nodes():
        cat = attr.get(n, "Other")
        w.writerow([n, n, cat, color[cat], round(bc.get(n, 0), 4), wdeg.get(n, 0)])

# edges.csv (무방향 통일·self-loop 제외)
seen = {}
for (a, b), wt in edge_counts.items():
    if a == b:
        continue
    key = tuple(sorted([a, b]))
    seen[key] = seen.get(key, 0) + wt

edges_path = os.path.join(outdir, "fig7-2_cotarget_edges.csv")
with open(edges_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Source", "Target", "Type", "Weight"])
    for (a, b), wt in sorted(seen.items(), key=lambda x: -x[1]):
        w.writerow([a, b, "Undirected", wt])

print("[저장]", nodes_path, "(", len(G.nodes()), "nodes )")
print("[저장]", edges_path, "(", len(seen), "edges )")
