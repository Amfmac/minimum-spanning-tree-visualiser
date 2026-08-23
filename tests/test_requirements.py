"Author: Aidan MacDonald"
"Date: 15/08/26"
"Module: HCS503"
"University of Abertay"

"""Tests for the 6 requirements, using pytest and assertions
    Each of the classes from the project are imported to use, with
    each test relating to a requirement by returning a figure or data to back up the desired and intended outcome.
    Ran using  python3 -m pytest -v when direct IDE running failed, either method available however.
"""
import pytest
from mst_project.application import Application
from mst_project.dataset import PUBLISHED_SHA256, Y_VALUES, DataSet
from mst_project.graph import Graph
from mst_project.mst import KruskalMST
from mst_project.point import Point
from mst_project.rendering import SvgRenderer


@pytest.fixture(scope="module")
def points():
    """The 100 Point objects built using the week 1 test data."""
    return DataSet.week1().points()


@pytest.fixture(scope="module")
def graph(points):
    """The graph with the max allowed distance of 20."""
    return Graph.from_points(points, 20)


@pytest.fixture(scope="module")
def mst(graph):
    """The minimum spanning tree (MST) of that graph"""
    return KruskalMST().compute(graph)


class TestRequirement1_Checksum:
    """checking the validity of the test data with a SHA-256 checksum."""

    def test_digest_matches_the_one_published_in_the_helper_file(self):
        assert DataSet.week1().checksum() == PUBLISHED_SHA256
        assert DataSet.week1().is_valid() is True

    def test_a_single_altered_digit_is_detected(self):
        corrupted = list(Y_VALUES)
        corrupted[50] += 1
        assert DataSet(corrupted, PUBLISHED_SHA256).is_valid() is False


class TestRequirement2_Points:
    """Implement a point class and instantiate all x and y coordinate values."""

    def test_distance_matches_the_worked_example_in_the_brief(self):
        """the assertion value is stated in the specifcation."""
        assert Point(1, 1).distance(Point(2, 2)) == pytest.approx(1.4142135623730951)


class TestRequirement3_Neighbours:
    """Find all neighbours of each point within a specified distance."""

    def test_reproduces_the_worked_example_in_the_brief(self, points):
        """The spec states the neighbours  (1, 37) within 20."""
        found = Graph(points).neighbours(points[0], 20, include_origin=True)
        assert [(p.x, p.y) for p, _ in found] == [
            (1, 37), (7, 34), (8, 40), (12, 41), (19, 44)
        ]
        assert [round(d, 5) for _, d in found] == [
            0.0, 6.70820, 7.61577, 11.70470, 19.31321
        ]

    def test_a_distance_of_125_returns_every_other_point(self, points):
        """The spec states this."""
        assert len(Graph(points).neighbours(points[0], 125)) == 99


class TestRequirement4_Graph:
    """A graph of point vertices with the computed distances as weights."""

    def test_every_edge_weight_is_the_distance_between_its_endpoints(self, graph):
        for edge in graph.edges:
            assert edge.weight == pytest.approx(edge.start.distance(edge.end))


class TestRequirement5_MST:
    """Apply an appropriate algorithm for genarating the MST."""

    def test_satisfies_the_cycle_property(self, graph, mst):
        """verify directly rather than trusting the algorithm themesleves."""
        tree = Graph(graph.vertices)
        for edge in mst.edges:
            tree.add_edge(edge.start, edge.end, edge.weight)

        for edge in set(graph.edges) - set(mst.edges):
            heaviest = self._heaviest_edge_on_path(tree, edge.start, edge.end)
            assert edge.weight >= heaviest - 1e-9, (
                f"{edge} is lighter than the {heaviest:.5f} edge it could replace"
            )



    @staticmethod
    def _heaviest_edge_on_path(tree, start, end):
        """return the largest edge weight on the path thorugh tree."""
        stack = [(start, 0.0)]
        seen = {start}
        while stack:
            current, worst = stack.pop()
            if current == end:
                return worst
            for edge in tree.incident_edges(current):
                far = edge.other(current)
                if far not in seen:
                    seen.add(far)
                    stack.append((far, max(worst, edge.weight)))
        raise AssertionError("every pair should be connected")


class TestRequirement6_Rendering:
    """Use SVG or another appropriate method to render the MST as an image."""

    def test_the_image_contains_every_point_and_every_mst_edge(self, points, mst):
        """The picture actually shows the full MST, not just empty file."""
        svg = SvgRenderer().to_svg(points, mst.edges, "MST")
        assert svg.count("<circle") == 100
        assert svg.count(SvgRenderer.EDGE_COLOUR) == len(mst.edges) == 99


class TestEndToEnd:
    """The whole end to end test for running the necessary assertions to report on."""

    def test_a_single_run_satisfies_all_six_requirements(self, tmp_path):
        result = Application(
            distance=20, output_dir=tmp_path, render_png=False, verbose=False
        ).run()

        assert result.checksum_valid is True                    
        assert len(result.points) == 100                       
        assert result.graph.order == 100                        
        assert result.graph.size == 539
        assert len(result.mst) == 99                            
        assert result.mst.total_weight == pytest.approx(659.57790, abs=1e-5)
        assert result.weights_agree is True
        assert {p.name for p in result.images} == { 
            "points.svg", "graph.svg", "mst.svg"
        }
        assert all(path.exists() for path in result.images)
