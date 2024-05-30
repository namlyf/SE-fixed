from pulp import *
import networkx as nx
import matplotlib.pyplot as plt

# Define G
# G = 5 nodes 8 links
G = nx.DiGraph()

for i in range(5):
    G.add_node(i, a=10)

for i in range(4):
    G.add_edge(i, i + 1, a=10)
    G.add_edge(i + 1, i, a=10)

# Define GS
# GS = 3 nodes 2 link

SFCs = nx.DiGraph()

SFCs.add_node(0, r=2)
SFCs.add_node(1, r=2)
SFCs.add_node(2, r=2)

SFCs.add_edge(0, 1, r=5)
SFCs.add_edge(1, 2, r=5)

# input
G
SFCs

# G, K{SFC}

# ILP
problem = pulp.LpProblem(name="graph-maaping", sense=pulp.LpMaximize)

xNode = list()
for sfc in SFCs:
    xNode.append(
        pulp.LpVariable.dicts(
            name=f"xNode{SFCs.index(sfc)}",
            indices=(sfc.nodes, G.nodes),
            cat="Binary"
        )
    )

xEdge = list()
for sfc in SFCs:
    xEdge.append(
        pulp.LpVariable.dicts(
            name=f"xEdge{SFCs.index(sfc)}",
            indices=(sfc.edges, G.edges),
            cat="Binary"
        )
    )


pi = pulp.LpVariable(
    name="pi",
    indices=(range(len(SFCs))),
    cat=pulp.LpBinary
)

aNode = nx.get_node_attributes(G, "a")
aEdge = nx.get_edge_attributes(G, "a")

rNode = nx.get_node_attributes(SFCs, "r")
rEdge = nx.get_edge_attributes(SFCs, "r")

# C1

for i in G.nodes:
    problem += (
        pulp.lpSum(
            pulp.lpSum(
                xNode[SFCs.index(sfc)][v][i] * rNode[v]
                for v in SFCs.nodes
            )
            for sfc in SFCs
        ) <= aNode[i],
        f"C1_{i}"
    )

# C2

for ij in G.edges:
    problem += (
        pulp.lpSum(
            pulp.lpSum(
                xEdge[SFCs.index(sfc)][vw][ij] * rEdge[vw]
                for vw in SFCs.edges
            )
            for sfc in SFCs
        ) <= aEdge[ij],
        f"C2_{ij}"
    )

# C3

for sfc in SFCs:
    for i in G.nodes:
        problem += (
            pulp.lpSum(
                xNode[SFCs.index(sfc)][v][i]
                for v in SFCs.nodes
            ) <= 1,
            f"C3_{i}_{SFCs.index(sfc)}"
        )

# C4

for sfc in SFCs:
    for v in SFCs.nodes:
        problem += (
            pulp.lpSum(
                xNode[SFCs.index(sfc)][v][i]
                for i in G.nodes
            ) == pi[SFCs.index(sfc)],
            f"C4_{v}_{SFCs.index(sfc)}"
        )

# C5

for sfc in SFCs:
    for vw in SFCs.edges:
        for i in G.nodes:
            problem += (
                pulp.lpSum(
                    xEdge[SFCs.index(sfc)][vw].get(i, j)
                    for j in G.nodes
                )
                -
                pulp.lpSum(
                    xEdge[SFCs.index(sfc)][vw].get(j, i)
                    for j in G.nodes
                ) == xNode[SFCs.index(sfc)][vw[0]][i] - xNode[SFCs.index(sfc)][vw[1]][i],
                f"C5_{vw}_{i}_{SFCs.index(sfc)}"
            )

problem += (
    pulp.lpSum(
        xNode[v][i]
        for v in SFCs.nodes
        for i in G.nodes
    )
)
print(problem)
