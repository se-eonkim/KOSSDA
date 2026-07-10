# -*- coding: utf-8 -*-
"""
Gate 2: male-nationality 클러스터 강건성 3종 검증
원 알고리즘: greedy_modularity_communities (결정론적, 시드 없음)
검증:
  ① Louvain 교차검증 (N=200회, 시드 변화)
  ② resolution 스윕 (greedy_modularity, 0.5~2.0)
  ③ 엣지 부트스트랩 (80% 샘플링, N=200회)
+ male BC=0 재확인
"""
import json, random
from collections import Counter, defaultdict
import networkx as nx
from networkx.algorithms import community as nxc

BASE = r"C:\Users\82109\OneDrive\바탕 화면\se_eon\projects\KOSSDA"
with open(BASE + r"\01_data\raw\kold_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ── 원 코드 그대로: 멀티표적 댓글에서 엣지 구성 ─────────────────
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

# 거리 그래프 (BC용)
G_dist = nx.Graph()
for u, v, d in G.edges(data=True):
    G_dist.add_edge(u, v, weight=d["weight"], distance=1/d["weight"])

out = []
def W(s=""): out.append(str(s))

W("="*65)
W("  Gate 2: male-nationality 클러스터 강건성 검증")
W(f"  네트워크: {G.number_of_nodes()}개 노드, {G.number_of_edges()}개 엣지")
W(f"  멀티표적 댓글: {len(multi)}개")
W("="*65)

# ── 원 알고리즘 결과 (기준선) ────────────────────────────────────
W("\n[기준선] greedy_modularity_communities (원 알고리즘)")
orig_comms = list(nxc.greedy_modularity_communities(G))
orig_Q = nxc.modularity(G, orig_comms)
male_orig = None
for i, c in enumerate(orig_comms):
    if "male" in c:
        male_orig = frozenset(c)
        W(f"  Cluster {i+1} (male 소속): {sorted(c)}")
W(f"  modularity Q = {orig_Q:.4f}")
W(f"  클러스터 수 = {len(orig_comms)}")

# nationality 표적 정의
nationality_set = {"chinese", "korean_chinese", "indian", "southeast_asian", "asian", "white"}

def male_nationality_overlap(comm):
    """male 소속 클러스터에 nationality 노드가 몇 개 있나"""
    if comm is None: return 0
    return len(comm & nationality_set)

orig_overlap = male_nationality_overlap(male_orig)
W(f"  male 클러스터 내 nationality 노드: {sorted(male_orig & nationality_set)} ({orig_overlap}개)")

# ── ① Louvain 교차검증 ───────────────────────────────────────────
W("\n[① Louvain 교차검증 N=200]")
N = 200
louvain_same = 0
louvain_overlap_counts = []

for seed in range(N):
    comms = nxc.louvain_communities(G, weight="weight", seed=seed)
    for c in comms:
        if "male" in c:
            fc = frozenset(c)
            overlap = male_nationality_overlap(fc)
            louvain_overlap_counts.append(overlap)
            if overlap >= 2:  # nationality 노드 2개 이상 함께 있으면 "동거"
                louvain_same += 1
            break

W(f"  male-nationality 동거율 (≥2개): {louvain_same}/{N} = {louvain_same/N*100:.1f}%")
W(f"  평균 nationality 공존 노드 수: {sum(louvain_overlap_counts)/N:.2f}")
W(f"  분포: {sorted(Counter(louvain_overlap_counts).items())}")

# ── ② resolution 스윕 ────────────────────────────────────────────
W("\n[② resolution 스윕 (greedy_modularity, 0.5~2.0, step 0.1)]")
resolutions = [round(0.5 + 0.1*i, 1) for i in range(16)]
res_results = []
for res in resolutions:
    try:
        comms = list(nxc.greedy_modularity_communities(G, resolution=res))
        for c in comms:
            if "male" in c:
                fc = frozenset(c)
                overlap = male_nationality_overlap(fc)
                res_results.append((res, len(comms), overlap, sorted(fc & nationality_set)))
                break
    except Exception as e:
        res_results.append((res, -1, -1, [str(e)]))

W(f"  {'res':>5}  {'클러스터수':>6}  {'nat겹침':>6}  male 클러스터 내 nationality 노드")
for res, nc, ov, nodes in res_results:
    W(f"  {res:>5.1f}  {nc:>6}  {ov:>6}  {nodes}")

res_stable = sum(1 for _, _, ov, _ in res_results if ov >= 2)
W(f"\n  nationality ≥2 구간: {res_stable}/{len(resolutions)} = {res_stable/len(resolutions)*100:.0f}%")

# ── ③ 엣지 부트스트랩 ─────────────────────────────────────────────
W("\n[③ 엣지 부트스트랩 N=200, 80% 샘플링]")
edge_list = list(G.edges(data=True))
boot_same = 0
boot_overlap_counts = []

random.seed(42)
for _ in range(N):
    sampled = random.sample(edge_list, int(len(edge_list) * 0.8))
    Gb = nx.Graph()
    for u, v, d in sampled:
        Gb.add_edge(u, v, weight=d["weight"])
    if "male" not in Gb.nodes:
        continue
    try:
        comms = list(nxc.greedy_modularity_communities(Gb))
        for c in comms:
            if "male" in c:
                fc = frozenset(c)
                overlap = male_nationality_overlap(fc)
                boot_overlap_counts.append(overlap)
                if overlap >= 2:
                    boot_same += 1
                break
    except:
        pass

W(f"  male-nationality 동거율 (≥2개): {boot_same}/{N} = {boot_same/N*100:.1f}%")
W(f"  평균 nationality 공존 노드 수: {sum(boot_overlap_counts)/len(boot_overlap_counts):.2f}" if boot_overlap_counts else "  결과 없음")
W(f"  분포: {sorted(Counter(boot_overlap_counts).items())}")

# ── male BC 재확인 ────────────────────────────────────────────────
W("\n[male BC 재확인 (distance=1/weight)]")
bc = nx.betweenness_centrality(G_dist, weight="distance")
bc_sorted = sorted(bc.items(), key=lambda x: -x[1])
W(f"  {'순위':<4}  {'노드':<20}  {'BC':>8}")
for rank, (node, score) in enumerate(bc_sorted[:10], 1):
    marker = " ← MALE" if node == "male" else ""
    W(f"  {rank:<4}  {node:<20}  {score:.4f}{marker}")

# ── 종합 판정 ─────────────────────────────────────────────────────
W("\n" + "="*65)
W("  종합 합의율 요약")
W("="*65)
louvain_rate = louvain_same/N*100
boot_rate = boot_same/N*100 if boot_overlap_counts else 0
res_rate = res_stable/len(resolutions)*100

W(f"  ① Louvain 200회:     {louvain_rate:.1f}%")
W(f"  ② resolution 스윕:   {res_rate:.0f}%")
W(f"  ③ 엣지 부트스트랩:   {boot_rate:.1f}%")

avg = (louvain_rate + boot_rate + res_rate) / 3
W(f"\n  평균 합의율: {avg:.1f}%")
if avg >= 80:
    W("  판정: 안정적 → S5 male-nationality 동거 주장 유지 가능")
elif avg >= 60:
    W("  판정: 부분 안정 → 주의 요함, 슬라이드에서 강도 낮춰 서술")
else:
    W("  판정: 불안정 → male-nationality 연결 주장 철회, S5 이중 대비로 축소")

result = "\n".join(out)
with open(BASE + r"\03_analysis\language_kold\gate2_robustness_result.txt", "w", encoding="utf-8") as f:
    f.write(result)
print("DONE")
