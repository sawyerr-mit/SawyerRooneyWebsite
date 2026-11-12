"""
search.py

BFS, Dijkstra and A* graph searches.

Adapted from CIS 454 (AI and Advanced Python) Assignment 6, University of Maine at Augusta,
Spring 2026. Original assignment given by Rocko Graziano.
"""

import math
import pickle
from collections import deque
from typing import Optional

from IndexMinPQ import *
from graph import Graph


def _build_path(prior: dict, t: int) -> list[int]:
    """ Walk the prior links back from t to the source (whose prior is None). """
    path = []
    node = t
    while node is not None:
        path.append(node)
        node = prior.get(node)
    path.reverse()
    return path


def BFS(G: Graph, s: int, t: int, debug: bool = False,
        trace: Optional[list] = None) -> tuple[list[int], int, int]:
    """
    Find the path with the fewest edges from s to t in an unweighted search.
    The target is considered found when it is first encountered, not when it is popped.

    trace: optional list; every popped node is appended in pop order (for plotting).

    return:  path        - a list of the nodes from s to t, including both
             path length - the number of edges in the path
             popcount    - the number of pops from the search frontier
    """

    popcount = 0

    print(f'\nUsing BFS to find path from {s} to {t}')

    # Trivial case: the target is the source (it would otherwise never be "encountered")
    if s == t:
        return [s], 0, popcount

    explored = {s: True}        # Source node starts explored
    prior = {s: None}           # Source node doesn't have a prior node
    frontier = deque([s])

    while frontier:

        # Pop the first node off; the first iteration returns the source node
        v = frontier.popleft()
        popcount += 1
        if trace is not None:
            trace.append(v)
        if debug:
            print(f'  pop #{popcount}: {v}')

        # Iterate over all the edges connected to the current node (breadth)
        for edge in G.edgesOf(v):
            u = edge.t

            # Only look at nodes that haven't been explored
            if not explored.get(u, False):
                explored[u] = True
                prior[u] = v

                # Target found when first encountered: rebuild and return the path
                if u == t:
                    path = _build_path(prior, t)
                    return path, len(path) - 1, popcount

                frontier.append(u)

    # Return flag data in case no path exists
    return [], -1, popcount


def Dijkstra(G: Graph, s: int, t: int, debug: bool = False,
             trace: Optional[list] = None) -> tuple[list[int], float, int]:
    """
    Find the shortest path (by edge weights) from s to t in a weighted graph.

    trace: optional list; every popped node is appended in pop order (for plotting).

    return:  path     - a list of the nodes from s to t, including both
             distance - the sum of the edge weights from s to t
             popcount - the number of pops from the search frontier
    """

    popcount = 0

    print(f'\nUsing Dijkstra to find path from {s} to {t}')

    prior = {s: None}                   # Stores previous nodes visited
    pathcost = {s: 0}                   # Cheapest known cost from s to each node
    frontier = IndexMinPQ(G.sizeV())    # Min priority queue keyed by cost

    # Every node starts at infinity except the source
    for v in G.getVertices():
        frontier.push(v.id, 0 if v.id == s else math.inf)

    while not frontier.isEmpty():

        v, cost = frontier.pop()
        popcount += 1
        if trace is not None:
            trace.append(v)
        if debug:
            print(f'  pop #{popcount}: {v} (cost {cost:.6g})')

        # Everything left is unreachable from s, so stop searching
        if cost == math.inf:
            break

        # Because the frontier is a min priority queue, t is only popped once
        # its cheapest path has been found
        if v == t:
            return _build_path(prior, t), pathcost[t], popcount

        # Relax every edge leaving v
        for edge in G.edgesOf(v):
            u = edge.t
            new_cost = pathcost[v] + edge.weight

            if new_cost < pathcost.get(u, math.inf):
                prior[u] = v
                pathcost[u] = new_cost
                if frontier.contains(u):
                    frontier.update(u, new_cost)

    # Return flag data in case no path exists
    return [], -1, popcount


def aStar(G: Graph, s: int, t: int, debug: bool = False,
          trace: Optional[list] = None) -> tuple[list[int], float, int]:
    """
    Find the shortest path (by edge weights) from s to t in a weighted graph,
    guided by a euclidean-distance heuristic on each vertex's lat/lon.

    trace: optional list; every popped node is appended in pop order (for plotting).

    return:  path     - a list of the nodes from s to t, including both
             distance - the distance from s to t
             popcount - the number of pops from the search frontier
    """

    def H(u: int, v: int) -> float:
        """ Euclidean distance between the lat/lon of vertices u and v. """
        tags_u = G.getTags(u)
        tags_v = G.getTags(v)
        lat_u, lon_u = tags_u['lat'], tags_u['lon']
        lat_v, lon_v = tags_v['lat'], tags_v['lon']
        return math.sqrt((lat_u - lat_v) ** 2 + (lon_u - lon_v) ** 2)

    popcount = 0

    print(f'\nUsing A* to find path from {s} to {t}')

    prior = {s: None}                   # Stores previous nodes visited
    pathcost = {s: 0}                   # g(n): cheapest known cost from s to n
    frontier = IndexMinPQ(G.sizeV())    # Keyed by f(n) = g(n) + H(n, t)

    # The only difference from Dijkstra's setup: the source starts at H(s, t), not 0
    for v in G.getVertices():
        frontier.push(v.id, H(s, t) if v.id == s else math.inf)

    while not frontier.isEmpty():

        v, cost = frontier.pop()
        popcount += 1
        if trace is not None:
            trace.append(v)
        if debug:
            print(f'  pop #{popcount}: {v} (f {cost:.6g})')

        # Everything left is unreachable from s, so stop searching
        if cost == math.inf:
            break

        # With a consistent heuristic the first pop of t is on a cheapest path
        if v == t:
            return _build_path(prior, t), pathcost[t], popcount

        for edge in G.edgesOf(v):
            u = edge.t
            new_g = pathcost[v] + edge.weight

            if new_g < pathcost.get(u, math.inf):
                prior[u] = v
                pathcost[u] = new_g
                # The key is g plus the heuristic, so nodes heading toward t pop
                # first. You wouldn't start driving north to get to Florida.
                if frontier.contains(u):
                    frontier.update(u, new_g + H(u, t))

    # Return flag data in case no path exists
    return [], -1, popcount


if __name__ == "__main__":
    import os

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    testcases = [('romania.pickle', 0, 1, False),
                 ('romania.pickle', 13, 4, False),
                 ('kennebec.pickle', 31358, 101336, False),
                 ]

    for testcase in testcases:
        print(f'\nTesting against {testcase[0]}\n')

        with open(testcase[0], 'rb') as f:
            G = pickle.load(f)

        print(f'There are {G.sizeV()} nodes in this graph')

        path, pathlength, popcount = BFS(G, testcase[1], testcase[2], debug=testcase[3])
        print(f'BFS Path is {pathlength} edges long; found in {popcount:,d} pops\n{path}')

        path, pathlength, popcount = Dijkstra(G, testcase[1], testcase[2], debug=testcase[3])
        print(f'Dijkstra Path is {pathlength} long in {len(path)-1} edges; found in {popcount:,d} pops\n{path} ')

        path, pathlength, popcount = aStar(G, testcase[1], testcase[2], debug=testcase[3])
        print(f'A* Path is {pathlength} long in {len(path)-1} edges; found in {popcount:,d} pops\n{path} ')
