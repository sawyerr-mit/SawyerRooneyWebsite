"""
graph.py

Minimal undirected/directed weighted graph. Attribute names (V, id, tags, edges,
s, t, weight) match the fields stored in the .pickle files, so do not rename them.
"""


class Graph:

    class Edge:
        def __init__(self, s: int, t: int, weight: float = 1.0):
            self.s = s
            self.t = t
            self.weight = weight

        def __repr__(self):
            return f'Edge({self.s}->{self.t}, w={self.weight:.6g})'

    class Vertex:
        def __init__(self, id: int, tags: dict = None):
            self.id = id
            self.tags = tags if tags is not None else {}
            self.edges = set()          # set of Graph.Edge (default identity hash)

        def __repr__(self):
            return f'Vertex({self.id}, {len(self.edges)} edges)'

    def __init__(self):
        self.V = []

    # ---- building -------------------------------------------------------
    def addVertex(self, tags: dict = None) -> int:
        v = Graph.Vertex(len(self.V), tags)
        self.V.append(v)
        return v.id

    def addEdge(self, s: int, t: int, weight: float = 1.0, directed: bool = False):
        self._vertex(s).edges.add(Graph.Edge(s, t, weight))
        if not directed:
            self._vertex(t).edges.add(Graph.Edge(t, s, weight))

    # ---- queries --------------------------------------------------------
    def _vertex(self, v: int):
        """Fast path: vertex id == list index (true for the provided data)."""
        if 0 <= v < len(self.V) and self.V[v].id == v:
            return self.V[v]
        idx = self.__dict__.get('_idx')
        if idx is None:
            idx = self.__dict__['_idx'] = {x.id: x for x in self.V}
        return idx[v]

    def sizeV(self) -> int:
        return len(self.V)

    def sizeE(self) -> int:
        return sum(len(v.edges) for v in self.V)

    def getVertices(self):
        return self.V

    def getVertex(self, v: int):
        return self._vertex(v)

    def getTags(self, v: int) -> dict:
        return self._vertex(v).tags

    def edgesOf(self, v: int):
        return self._vertex(v).edges

    def __repr__(self):
        return f'Graph(|V|={self.sizeV()}, |E|={self.sizeE()})'


# Aliases in case a pickle references module-level names (graph.Vertex / graph.Edge)
Vertex = Graph.Vertex
Edge = Graph.Edge
