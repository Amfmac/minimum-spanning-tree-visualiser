"""Author: Aidan MacDonald
Date: 15/08/26
Module: HCS503
University of Abertay

The application class for keeping all the components together in one easy to digest file

will touch on each of the 6 requirements in order, printing the results at each step, and returns a result that holds everything
it produced that can be used in the tests.

seperation of concerns for making new small class for each area of project

will be consistant use of naming conventions as professional as possible across these classes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .dataset import DataSet
from .graph import MAX_ASSIGNMENT_DISTANCE, Graph
from .mst import KruskalMST, MinimumSpanningTree, MSTAlgorithm, PrimMST
from .point import Point
from .rendering import MatplotlibRenderer, SvgRenderer

@dataclass
class PipelineResult:
    """Everything a single run produces, the whole pipeline view like past projects."""

    checksum: str
    checksum_valid: bool
    points: list[Point]
    graph: Graph
    mst: MinimumSpanningTree
    cross_check: MinimumSpanningTree | None = None
    images: list[Path] = field(default_factory=list)

    @property
    def weights_agree(self) -> bool:
        """True only if the second algorithmn found the same total weight."""
        if self.cross_check is None:
            return True
        return abs(self.mst.total_weight - self.cross_check.total_weight) < 1e-9




class Application:

    """Runs the full points to a graph, MST, and graph image.
       distance distance will need to be 0 to <=20 as values outside the range aren't allowed
       algorithm choice and the MST strategy used for the reported result.
       cross_check is used to also run the other algorithm, to verify the total weight
       render_png writes matplotlib PNG as well as the the SVG for extra checks
    """
    def __init__(
        self,
        distance: float = MAX_ASSIGNMENT_DISTANCE,
        algorithm: MSTAlgorithm | None = None,
        cross_check: bool = True,
        output_dir: str | Path = "output",
        render_png: bool = True,
        verbose: bool = True,
    ) -> None:
        if not 0 < distance <= MAX_ASSIGNMENT_DISTANCE:
            raise ValueError(
                f"distance must be 0 < distance <= {MAX_ASSIGNMENT_DISTANCE:g}, "
                f"is {distance}"
            )
        self.distance = distance
        self.algorithm = algorithm or KruskalMST()
        self.cross_check: MSTAlgorithm | None = None
        if cross_check:
            self.cross_check = (
                PrimMST() if isinstance(self.algorithm, KruskalMST) else KruskalMST()
            )

        self.output_dir = Path(output_dir)
        self.render_png = render_png
        self.verbose = verbose

    def _say(self, message: str = "") -> None:
        "Messages for different stages and readability"
        if self.verbose:
            print(message)

    def _heading(self, number: str, title: str) -> None:
        self._say()
        self._say(f"{number}  {title}")
        self._say("-" * 66)

    def run(self) -> PipelineResult:
        """run all requirements to show results"""
        self._say("=" * 66)
        self._say(" HCS503 Python Assignment MST and graph")
        self._say("=" * 66)

        dataset, checksum = self.step_validate_data()
        points = self.step_create_points(dataset)
        self.step_demonstrate_neighbours(points)
        graph = self.step_build_graph(points)
        mst, cross = self.step_compute_mst(graph)
        images = self.step_render(points, graph, mst)

        result = PipelineResult(
            checksum=checksum,
            checksum_valid=dataset.is_valid(),
            points=points,
            graph=graph,
            mst=mst,
            cross_check=cross,
            images=images,
        )
        self._summarise(result)
        return result

    def step_validate_data(self) -> tuple[DataSet, str]:
        """Requirement 1, the SHA-256 checksum of the dataset y values."""
        self._heading("1.", "Validating the test data using SHA-256")
        dataset = DataSet.week1()
        digest = dataset.checksum()

        self._say(f"y values read      : {len(dataset)}")
        self._say(f"concatenated char length: {len(dataset.y_string())} characters")
        self._say(f"computed SHA-256   : {digest}")
        self._say(f"published SHA-256  : {dataset.expected_checksum}")
        if not dataset.is_valid():
            raise SystemExit("error: the test data does not match the checksum")
        self._say("result matches")
        return dataset, digest

    def step_create_points(self, dataset: DataSet) -> list[Point]:
        """Requirement 2, instantiate one Point for the x/y pair."""
        self._heading("2.", "Instantiating the point objects")
        points = dataset.points()
        y_values = [p.y for p in points]
        self._say(f"Point objects created: {len(points)}")
        self._say(f"first point          : {points[0]}")
        self._say(f"last point           : {points[-1]}")
        self._say(f"y range              : {min(y_values)} to {max(y_values)}")
        return points

    def step_demonstrate_neighbours(self, points: list[Point]) -> None:
        """Requirement 3, find the neighbours of a point within a distance"""
        self._heading("3.", f"finding the neighbours within {self.distance:g}")
        scratch = Graph(points)
        origin = points[0]

        self._say(f"neighbours from ({origin}) within {self.distance:g}:")
        for neighbour, distance in scratch.neighbours(origin, self.distance, True):
            self._say(f"  ({neighbour})   distance = {distance:.5f}")

        wide = scratch.neighbours(origin, 125.0)
        self._say(f"neighbours of the same point within 125: {len(wide)} "
                  f"(all {len(points) - 1} other points)")

    def step_build_graph(self, points: list[Point]) -> Graph:
        """Requirement 4 to build the weighted graph from the points."""
        self._heading("4", "Building the weighted graph")
        graph = Graph.from_points(points, self.distance)
        components = graph.connected_components()
        degrees = [graph.degree(p) for p in graph.vertices]

        self._say(f"vertices          : {graph.order}")
        self._say(f"edges               : {graph.size} "
                  f"(of {graph.order * (graph.order - 1) // 2}  possible pairs)")
        self._say(f"total edge weight   : {graph.total_weight:.5f}")
        self._say(f"mean degree         : {sum(degrees) / len(degrees):.2f}")
        self._say(f"degree range        : {min(degrees)} to {max(degrees)}")
        self._say(f"connected components: {len(components)}")
        if len(components) > 1:
            self._say(f"component sizes   : {sorted((len(c) for c in components), reverse=True)}")
        return graph

    def step_compute_mst(
        self, graph: Graph
    ) -> tuple[MinimumSpanningTree, MinimumSpanningTree | None]:
        """Requirement 5 to compute the actual minimum spanning tree MST."""
        self._heading("5.", f"Computing the MST ({self.algorithm.name}  algorithm)")
        mst = self.algorithm.compute(graph)
        shape = (
            "spanning tree"
            if mst.is_spanning_tree
            else f"spanning forest ({mst.component_count} trees)"
        )

        self._say(f"edges selected  : {len(mst)} of {graph.size}")
        self._say(f"total weight    : {mst.total_weight:.5f}")
        self._say(f"resulting shape    : {shape}")
        if mst.edges:
            self._say(f"shortest edge   : {min(mst.edges, key=lambda e: e.weight)}")
            self._say(f"longest edge    : {max(mst.edges, key=lambda e: e.weight)}")

        cross = None
        if self.cross_check is not None:
            cross = self.cross_check.compute(graph)
            agree = abs(cross.total_weight - mst.total_weight) < 1e-9
            self._say()
            self._say(f"cross-check with {self.cross_check.name}'s algorithm:")
            self._say(f"  total weight : {cross.total_weight:.5f}")
            self._say(f"  agreement    : "
                      f"{'Yes the totals are identical' if agree else 'No, the results are different'}")
        return mst, cross

    def step_render(
        self, points: list[Point], graph: Graph, mst: MinimumSpanningTree
    ) -> list[Path]:
        """Requirement 6 to render the results as images both PNG but mainly SVG."""
        self._heading("6.", "Rendering the images")
        label = f"d = {self.distance:g}"
        svg = SvgRenderer()
        written = [
            svg.render(points, (), self.output_dir / "points.svg",
                       "Test data: 100 points"),
            svg.render(points, graph.edges, self.output_dir / "graph.svg",
                       f"Graph ({label}, {graph.size} edges)"),
            svg.render(points, mst.edges, self.output_dir / "mst.svg",
                       f"Minimum spanning tree ({self.algorithm.name}, {label}, "
                       f"weight {mst.total_weight:.2f})"),
        ]


        if self.render_png:
            try:
                png = MatplotlibRenderer()
                written.append(
                    png.render(points, mst.edges, self.output_dir / "mst.png",
                               f"MST ({self.algorithm.name}, {label})")
                )
                written.append(
                    png.render(points, (), self.output_dir / "scatter.png",
                               "Test data scatter plot")
                )
            except ImportError as error:
                self._say(f"nevermind, no PNG this time:  {error}")

        for path in written:
            self._say(f"wrote {path}")
        return written

    def _summarise(self, result: PipelineResult) -> None:
        "Results output summary for easy visualisation"
        self._say()
        self._say("=" * 66)
        self._say("  SUMMARY")
        self._say("=" * 66)
        self._say(f"  data checksum   : {'valid' if result.checksum_valid else 'invalid'}")
        self._say(f"  points          : {len(result.points)}")
        self._say(f"  distance limit  : {self.distance:g}")
        self._say(f"  graph          : {result.graph.size} edges, "
                  f"{len(result.graph.connected_components())} component(s)")
        self._say(f"  MST             : {len(result.mst)} edges, "
                  f"weight {result.mst.total_weight:.5f}")
        self._say(f"  cross-check    : "
                  f"{'algorithms agree' if result.weights_agree else 'dont agree'}")
        self._say(f"  images          : {len(result.images)} written to {self.output_dir}/")
        self._say()

    def sweep(self, distances: list[float] | None = None) -> list[dict[str, float]]:
        """Extra interest to rebuild the graph at several distance limits to see effects"""
        distances = distances or [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        points = DataSet.week1().points()
        rows: list[dict[str, float]] = []

        self._heading("-.", "distance limit's effect on the result")
        header = (f"{'distance':>9}  {'edges':>7}  {'components':>11}  "
                  f"{'MST edges':>10}  {'MST weight':>11}")
        self._say(header)
        self._say("-" * len(header))
        for distance in distances:
            graph = Graph.from_points(points, distance)
            mst = self.algorithm.compute(graph)
            components = len(graph.connected_components())
            rows.append({
                "distance": float(distance),
                "edges": graph.size,
                "components": components,
                "mst_edges": len(mst),
                "mst_weight": mst.total_weight,
            })
            self._say(f"{distance:>9g}  {graph.size:>7}  {components:>11}  "
                      f"{len(mst):>10}  {mst.total_weight:>11.5f}")
        self._say()
        return rows
