"Author: Aidan MacDonald"
"Date: 15/08/26"
"Module: HCS503"
"University of Abertay"

"""
project that involves producing a minimum spanning tree and a graph given a dataset
"""

from .application import Application, PipelineResult
from .dataset import PUBLISHED_SHA256, Y_VALUES, DataSet
from .graph import MAX_ASSIGNMENT_DISTANCE, Edge, Graph
from .mst import (
    ALGORITHMS,
    DisjointSet,
    KruskalMST,
    MinimumSpanningTree,
    MSTAlgorithm,
    PrimMST,
)
from .point import Point, point_test
from .rendering import MatplotlibRenderer, Renderer, SvgRenderer, ViewPort

__version__ = "1.0.0"
"for default now"



__all__ = [
    "ALGORITHMS",
    "MAX_ASSIGNMENT_DISTANCE",
    "PUBLISHED_SHA256",
    "Y_VALUES",
    "Application",
    "DataSet",
    "DisjointSet",
    "Edge",
    "Graph",
    "KruskalMST",
    "MSTAlgorithm",
    "MatplotlibRenderer",
    "MinimumSpanningTree",
    "PipelineResult",
    "Point",
    "PrimMST",
    "Renderer",
    "SvgRenderer",
    "ViewPort",
    "point_test",
]
