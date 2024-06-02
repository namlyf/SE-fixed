from pulp import *
import networkx as nx
import pulp as pl

# Define G
# G = 5 nodes 8 links

#Definition of Graph
def slice_generate():
    G = nx.DiGraph()

    for i in range(5):
        G.add_node(i, a=10)

    for i in range(4):
        G.add_edge(i, i + 1, a=10)
        G.add_edge(i + 1, i, a=10)

    return G

# Define GS
# GS = 3 nodes 2 link

PHY=nx.DiGraph()
for i in range(5):
    PHY.add_node(i,a=10)
for i in range(4):
    PHY.add_edge(i, i+1, a=10)
    PHY.add_edge(i+1, i, a=10)

S = list()
for i in range(5):
    S.append(slice_generate())


# ILP
problem = pulp.LpProblem(name="graph-maaping", sense=LpMaximize)

#variables
xNode = pl.LpVariable.dicts(name="xNode",
                              indices= [(i,v,s) for i in PHY.nodes for s in range(len(S)) for v in S[s].nodes],
                              cat=LpBinary)


xEdge = pl.LpVariable.dicts(name="xEdge",
                            indices=[(i,w,v,j,s)
                               for i,j in PHY.edges
                               for s in range(len(S))
                               for w,v in S[s].edges],
                            cat=LpBinary)




pi = pulp.LpVariable( name="pi",cat=LpBinary)


aNode = nx.get_node_attributes(PHY, "a")
aEdge = nx.get_edge_attributes(PHY, "a")

for s in range(len(S)):
    rNode = nx.get_node_attributes(S[s], "r")
    rEdge = nx.get_edge_attributes(S[s], "r")

# C1
for i in PHY.nodes:
    problem += pulp.lpSum(
                    xNode[(i,v,s)] * rNode[v] for s in range(len(S)) for v in S[s].nodes
                ) <= aNode[i], f"C1_{i}"

# C2

for i,j in PHY.edges:                                           
    problem += (
        pulp.lpSum(
                xEdge[(i,j,v,w,s)] *rNode[(v,w)] for s in range(len(S)) for (v,w) in S[s].edges
            )
         <= aEdge[(i,j)],
       f,"C2_{i}_{j}"
       )

# C3
    for i in PHY.nodes:
        problem += (
            pulp.lpSum(
               xNode[(s,v,i)] for v in S[s].nodes for s in range(len(S))
            ) <= pi[s],
            f"C3_{i}"
        )

# C4
for s in range(len(S)):
    for v in S[s].nodes:
        problem += (
            pulp.lpSum(
                xNode[(s,v,i)] for i in PHY.nodes
            ) == pi[s],
            f"C4_{s}_{v}"

        )

# C5
for s in range(len(S)):
    for w,v in S[s].edges:
        for i in PHY.nodes:
            for j in PHY.nodes:
                if i != j:
                   if (s,w,v,i,j) in xEdge and (s,w,v,j,i) in xEdge:
                       problem += (
                           pulp.lpSum(
                               xEdge[(s,w,v,i,j)]
                           ) - pulp.lpSum(
                               xEdge[(s,w,v,j,i)]
                           ) == xNode[(s,v,i)] - xNode[(s,w,i)],
                           f"C5_{s}_{w}_{v}_{i}_{j}"
                       )

# Objective function
problem += (
    pulp.lpSum(pi[s] for s in range(len(S)))
    )
print(problem)

#solve problem
result=problem.solve()
print(pulp.LpStatus[result])

# Output
for v in problem.variables():
    print(v.name, "=", v.varValue)

