"""Author: Aidan MacDonald
Date: 15/08/26
Module: HCS503
University of Abertay

Finding the neighbors of a eahc point given a distance, creating a weighted undirected graph built from the new point objects, includes requirement 3 an 4.
To keep the whole structure in the Graph class with the connecting straight lines between points as the edges
Weights and edge count will be calculated for results
"""

from __future__ import annotations
import itertools
from collections.abc import Iterable
from .point import Point

"""As stated by requirements"""
MAX_ASSIGNMENT_DISTANCE = 20.0




class Edge:
    """ The connection between two points with weights being the distance between the endpoints
        The edges are compared for order and checks are in place to spot the same edge when pairs or ordered differently
    """
    def __init__(self, start: Point, end: Point, weight: float | None = None) -> None:
        if start == end:
            raise ValueError(f"an edge need two distinct points, but have {start!r} twice")
        self.start = start
        self.end = end
        self.weight = start.distance(end) if weight is None else float(weight)

    def other(self, point: Point) -> Point:
        """return the endpoint that is not the parameter point"""
        if point == self.start:
            return self.end
        if point == self.end:
            return self.start
        raise ValueError(f"{point!r} is not an endpoint of {self!r}")

    def __lt__(self, other: "Edge") -> bool:
        """ordered by weight, so Kruskal's order is folowed"""
        return self.weight < other.weight

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        return (
            frozenset((self.start, self.end)) == frozenset((other.start, other.end))
            and self.weight == other.weight
        )

    def __hash__(self) -> int:
        return hash((frozenset((self.start, self.end)), self.weight))

    def __str__(self) -> str:
        return f"({self.start}) <-> ({self.end})  weight = {self.weight:.5f}"

    def __repr__(self) -> str:
        return f"Edge({self.start!r}, {self.end!r}, {self.weight!r})"


class Graph:
    """A weighted graph with vertices that are point objects, undirected.
        The graph has an adjacency map so any traversals such as the components search and Prim's algorithm 
        invlove the edges actually there rather than to every possible pair, more efficient
    """

    def __init__(self, points: Iterable[Point] = ()) -> None:
        self._vertices: list[Point] = []
        self._adjacency: dict[Point, list[Edge]] = {}
        self._edges: list[Edge] = []
        for point in points:
            self.add_vertex(point)



    @classmethod
    def from_points(cls, points: Iterable[Point], max_distance: float) -> "Graph":
        """Connect every pair of points, but not more than the max_distance
             edges weighted by the distance between the two points
        """
        if max_distance <= 0:
            raise ValueError(f"the max distance must be > 0, it is {max_distance}")
        graph = cls(points)
        for a, b in itertools.combinations(graph.vertices, 2):
            distance = a.distance(b)
            if distance <= max_distance:
                graph.add_edge(a, b, distance)

        return graph

    def add_vertex(self, point: Point) -> bool:
        """return false if point already has a vertex added."""
        if point in self._adjacency:
            return False
        self._adjacency[point] = []
        self._vertices.append(point)
        return True

    def add_edge(self, start: Point, end: Point, weight: float | None = None) -> Edge:
        """connect two points together adding as a vertex if it is not one already one."""

        edge = Edge(start, end, weight)
        self.add_vertex(start)
        self.add_vertex(end)
        self._adjacency[start].append(edge)
        self._adjacency[end].append(edge)
        self._edges.append(edge)

        return edge

    @property
    def vertices(self) -> tuple[Point, ...]:
        """All vertices ordered."""
        return tuple(self._vertices)

    @property
    def edges(self) -> tuple[Edge, ...]:
        """All edges, ordered."""
        return tuple(self._edges)

    @property
    def order(self) -> int:
        """The number of vertices."""
        return len(self._vertices)

    @property
    def size(self) -> int:
        """The number of edges."""
        return len(self._edges)

    @property
    def total_weight(self) -> float:
        """The total sum of all the edge weights from the graph"""
        return sum(edge.weight for edge in self._edges)

    def incident_edges(self, point: Point) -> list[Edge]:
        """return every edge that touches parameter point."""
        if point not in self._adjacency:
            raise KeyError(f"{point!r} is not in the graph")
        return self._adjacency[point]


    def degree(self, point: Point) -> int:
        """return the number of edges touching (number of neighbours) the paramter point."""
        """Inclusion after debugging to check"""
        return len(self.incident_edges(point))

    def neighbours(
        self,
        origin: Point,
        distance: float,
        include_origin: bool = False,
    ) -> list[tuple[Point, float]]:
        """return every vertex within the distance of origin point, requirement 3 .
        searches the vertices set, not the edges, so it works even
        for distance larger than the graph was should include
        specifcally returns point distance pairs ordered by increasing distance.
        """

        if distance <= 0:
            raise ValueError(f"distance must be > 0 but it is {distance}")
        found: list[tuple[Point, float]] = []

        for point in self._vertices:
            if point == origin and not include_origin:
                continue
            separation = origin.distance(point)
            if separation <= distance:
                found.append((point, separation))
                
        """order goes to lowest x and y value distance is the same"""
        found.sort(key=lambda pair: (pair[1], pair[0].x, pair[0].y))
        return found

    def connected_components(self) -> list[list[Point]]:
        """puts the vertices into connected components where they can.
        needed as a spanning tree technically only exists for a connected
        graph, so with the distances is isn't exactly guaranteed.The
        component count itself determines if the MST stage results in a tree or a forest.
        """
        seen: set[Point] = set()
        components: list[list[Point]] = []
        for start in self._vertices:
            if start in seen:
                continue
            component: list[Point] = []
            stack = [start]
            seen.add(start)
            while stack:
                current = stack.pop()
                component.append(current)
                for edge in self._adjacency[current]:
                    neighbour = edge.other(current)
                    if neighbour not in seen:
                        seen.add(neighbour)
                        stack.append(neighbour)
            components.append(component)

        return components

    def is_connected(self) -> bool:
        """return true if every vertex is connected to each other."""
        return self.order <= 1 or len(self.connected_components()) == 1

    def __len__(self) -> int:
        return self.order

    def __str__(self) -> str:
        return f"Graph({self.order} vertices, {self.size} edges)"
