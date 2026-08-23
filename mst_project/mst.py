"""Author: Aidan MacDonald
Date: 15/08/26
Module: HCS503
University of Abertay

The MST minimum spanning tree algorithms.
   within the MSTAlgroithm interface, 2 algrothms will be used,
   the Kruskal and Prim, in the KruskalMST and PrimMST classes, use of
   two implementations for ensuring accurate results.
   Both algorithms return a spanning forest when the graph is disconnected, but with
   a connected graph a valid MST can be outputted ready for rendering.
"""

from __future__ import annotations
import heapq
from abc import ABC, abstractmethod
from collections.abc import Iterable
from .graph import Edge, Graph
from .point import Point

class DisjointSet:
    """ Union-find for set with the union by rank and path compression,
        checks needed often for two points already being joined for speed (for Kruskal)
    """

    def __init__(self, items: Iterable[object] = ()) -> None:
        self._parent: dict[object, object] = {}
        self._rank: dict[object, int] = {}
        self.set_count = 0
        for item in items:
            self.make_set(item)

    def make_set(self, item: object) -> None:
        """if item isnt know have its own set."""
        if item not in self._parent:
            self._parent[item] = item
            self._rank[item] = 0
            self.set_count += 1

    def find(self, item: object) -> object:
        root = item
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[item] != root:
            self._parent[item], item = root, self._parent[item]
        return root
        

    def union(self, a: object, b: object) -> bool:
        """Merge the sets that have a and b by a union.
           returns true if they were separate and are now merged, false if they
            were already together.
        """
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self._rank[root_a] < self._rank[root_b]:
            root_a, root_b = root_b, root_a
        self._parent[root_b] = root_a
        if self._rank[root_a] == self._rank[root_b]:
            self._rank[root_a] += 1
        self.set_count -= 1
        return True

    def connected(self, a: object, b: object) -> bool:
        """return true if a and b are already in the same set."""
        return self.find(a) == self.find(b)


class MinimumSpanningTree:
    """The result of the MST calculation with chosen edges
       the list of edges is contained/wrapped in an object to keep the total weight
       next to the data so the values can be reused each time there is a call
    """

    def __init__(
        self,
        edges: Iterable[Edge],
        vertex_count: int,
        algorithm: str = "not known yet",
    ) -> None:
        self.edges: tuple[Edge, ...] = tuple(edges)
        self.vertex_count = vertex_count
        self.algorithm = algorithm

    @property
    def total_weight(self) -> float:
        """the total sum of the selected edge wieghts"""
        return sum(edge.weight for edge in self.edges)

    @property
    def component_count(self) -> int:
        return self.vertex_count - len(self.edges)

    @property
    def is_spanning_tree(self) -> bool:
        """true for a tree, false for a forest."""
        return self.component_count == 1

    def vertices(self) -> set[Point]:
        """The set of points touching one selected edge at least"""
        return {point for edge in self.edges for point in (edge.start, edge.end)}

    def __len__(self) -> int:
        return len(self.edges)

    def __iter__(self):
        return iter(self.edges)

    def __str__(self) -> str:
        shape = "tree" if self.is_spanning_tree else f"forest of {self.component_count}"
        return (
            f"MinimumSpanningTree({len(self.edges)} edges, "
            f"total weight {self.total_weight:.5f}, {shape}, using  {self.algorithm})"
        )


class MSTAlgorithm(ABC):
    """Interface used for all minimum spanning trees
      simple rather than a harcoded algorithm, only requires
      swapping out Kruskal for Prim, only changing the single word when calling
    """
    name: str = "abstract"

    @abstractmethod
    def compute(self, graph: Graph) -> MinimumSpanningTree:
        """return a minimum spanning tree for the graph."""

    def __str__(self) -> str:
        return self.name




class KruskalMST(MSTAlgorithm):
    """Kruskal's algorithm, lowest/cheapest edge first."""

    name = "Kruskal"

    def compute(self, graph: Graph) -> MinimumSpanningTree:
        components = DisjointSet(graph.vertices)
        ordered = sorted(
            graph.edges,
            key=lambda e: (e.weight, e.start.x, e.start.y, e.end.x, e.end.y),
        )

        chosen: list[Edge] = []
        for edge in ordered:
            if components.union(edge.start, edge.end):
                chosen.append(edge)
                if len(chosen) == graph.order - 1:
                    break
        return MinimumSpanningTree(chosen, graph.order, self.name)


class PrimMST(MSTAlgorithm):
    """Prim's algorithm, outward direction with the cheapest edge first (frontierr edge)."""

    name = "Prim"

    def compute(self, graph: Graph) -> MinimumSpanningTree:
        visited: set[Point] = set()
        chosen: list[Edge] = []
        counter = 0

        for root in graph.vertices:
            if root in visited:
                continue
            frontier: list[tuple[float, int, Edge | None, Point]] = [
                (0.0, counter, None, root)
            ]
            counter += 1

            while frontier:
                _, _, edge, target = heapq.heappop(frontier)
                if target in visited:
                    continue
                visited.add(target)
                if edge is not None:
                    chosen.append(edge)
                for next_edge in graph.incident_edges(target):
                    far_end = next_edge.other(target)
                    if far_end not in visited:
                        heapq.heappush(
                            frontier, (next_edge.weight, counter, next_edge, far_end)
                        )
                        counter += 1

        return MinimumSpanningTree(chosen, graph.order, self.name)



ALGORITHMS: dict[str, type[MSTAlgorithm]] = {
    "kruskal": KruskalMST,
    "prim": PrimMST,
}
