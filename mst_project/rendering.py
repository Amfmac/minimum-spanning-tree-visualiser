"""Author: Aidan MacDonald
Date: 15/08/26
Module: HCS503
University of Abertay

Rendering the graph and the MST as an image, requirment 4
   use of the Renderer interface and Math module for validation checks
   using SVG for the image, with PNG backup to compare
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from pathlib import Path
from xml.sax.saxutils import escape
from .graph import Edge
from .point import Point


class ViewPort:
    """Maps data coordinates onto the canvas coordinates."""
    def __init__(
        self,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        width: float = 900,
        height: float = 900,
        margin: float = 70,
    ) -> None:
        if x_max <= x_min or y_max <= y_min:
            raise ValueError("must be used viewport area")
        if width <= 2 * margin or height <= 2 * margin:
            raise ValueError("no space has been left by margins")
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max
        self.width, self.height, self.margin = width, height, margin

    @classmethod
    def from_points(
        cls,
        points: Iterable[Point],
        width: float = 900,
        height: float = 900,
        margin: float = 70,
        step: float = 10,
    ) -> "ViewPort":
        """Fit a view port around the points.
           concept of snapping keeps the x and y axis labels conistant and expected rather than starting
           always at the smallest value only
        """
        points = list(points)
        if not points:
            raise ValueError("no points here")
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return cls(
            math.floor(min(xs) / step) * step,
            math.ceil(max(xs) / step) * step,
            math.floor(min(ys) / step) * step,
            math.ceil(max(ys) / step) * step,
            width,
            height,
            margin,
        )

    @property
    def plot_width(self) -> float:
        """width of the drawing area."""
        return self.width - 2 * self.margin

    @property
    def plot_height(self) -> float:
        """height of the drawing area."""
        return self.height - 2 * self.margin

    def x_to_canvas(self, x: float) -> float:
        """converts a data x value to a canvas coordinate."""
        return self.margin + (x - self.x_min) / (self.x_max - self.x_min) * self.plot_width

    def y_to_canvas(self, y: float) -> float:
        """converts a data y value to a canvas coordinate, flipped for different properties of SVG and Math module."""
        offset = (y - self.y_min) / (self.y_max - self.y_min) * self.plot_height
        return self.height - self.margin - offset

    def to_canvas(self, point: Point) -> tuple[float, float]:
        """convert a point iteslf to a canvas x,y pair."""
        return self.x_to_canvas(point.x), self.y_to_canvas(point.y)

    def ticks(self, axis: str, step: float = 20) -> list[float]:
        """return the data values for drawing label increments."""
        low, high = (self.x_min, self.x_max) if axis == "x" else (self.y_min, self.y_max)
        count = int((high - low) / step)
        return [low + i * step for i in range(count + 1)]


class Renderer(ABC):
    """to be used by anything that can draw points and edges to a file."""

    extension: str = ""

    @abstractmethod
    def render(
        self,
        points: Sequence[Point],
        edges: Sequence[Edge],
        output_path: str | Path,
        title: str = "",
    ) -> Path:
        """draw points and edges to output_path and return it."""


class SvgRenderer(Renderer):
    """Renders points and edges as a SVG, with
       same style as the helper file where there are blue
       point markers, red connecting lines, a light coloured grid for easy comparing images.
    """
    extension = ".svg"

    POINT_COLOUR = "#0000ff"
    EDGE_COLOUR = "#e60000"
    GRID_COLOUR = "#d9d9d9"

    def __init__(self, width: float = 900, height: float = 900, margin: float = 70) -> None:
        self.width = width
        self.height = height
        self.margin = margin

    @staticmethod
    def _num(value: float) -> str:
        """coordinate 3 decimal places no need for all the zeros."""
        return f"{value:.3f}".rstrip("0").rstrip(".")

    def to_svg(
        self,
        points: Sequence[Point],
        edges: Sequence[Edge],
        title: str = "",
    ) -> str:
        """build the complete SVG as a string for storing."""
        view = ViewPort.from_points(points, self.width, self.height, self.margin)
        n = self._num
        parts: list[str] = []

        """Standard ticks and details, height, width, stroke etc"""
        for x in view.ticks("x", 10):
            cx = n(view.x_to_canvas(x))
            parts.append(
                f'<line x1="{cx}" y1="{n(view.margin)}" x2="{cx}" '
                f'y2="{n(view.height - view.margin)}" stroke="{self.GRID_COLOUR}" />'
            )
        for y in view.ticks("y", 10):
            cy = n(view.y_to_canvas(y))
            parts.append(
                f'<line x1="{n(view.margin)}" y1="{cy}" '
                f'x2="{n(view.width - view.margin)}" y2="{cy}" stroke="{self.GRID_COLOUR}" />'
            )
        parts.append(
            f'<rect x="{n(view.margin)}" y="{n(view.margin)}" '
            f'width="{n(view.plot_width)}" height="{n(view.plot_height)}" '
            f'fill="none" stroke="#808080" />'
        )

        for x in view.ticks("x", 20):
            parts.append(self._text(view.x_to_canvas(x), view.height - view.margin + 22, f"{x:g}"))
        for y in view.ticks("y", 20):
            parts.append(
                self._text(view.margin - 12, view.y_to_canvas(y) + 4, f"{y:g}", anchor="end")
            )
        parts.append(self._text(view.width / 2, view.height - 18, "x", size=15))
        parts.append(self._text(22, view.height / 2, "y", size=15))
        if title:
            parts.append(
                self._text(view.width / 2, view.margin - 26, title, size=18, weight="bold")
            )

        # Edges before points, so the markers sit on top of the lines.
        for edge in edges:
            x1, y1 = view.to_canvas(edge.start)
            x2, y2 = view.to_canvas(edge.end)
            parts.append(
                f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" '
                f'stroke="{self.EDGE_COLOUR}" stroke-width="1.4" stroke-linecap="round" />'
            )
        for point in points:
            cx, cy = view.to_canvas(point)
            parts.append(
                f'<circle cx="{n(cx)}" cy="{n(cy)}" r="4" fill="{self.POINT_COLOUR}" />'
            )

        body = "\n  ".join(parts)
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(self.width)}" '
            f'height="{n(self.height)}" viewBox="0 0 {n(self.width)} {n(self.height)}">\n'
            f'  <rect width="100%" height="100%" fill="#ffffff" />\n'
            f"  {body}\n"
            "</svg>\n"
        )

    def _text(
        self,
        x: float,
        y: float,
        content: str,
        size: float = 13,
        anchor: str = "middle",
        weight: str = "normal",
    ) -> str:
        """build the SVG text element output where the content is XML escaped, typical detials."""
        return (
            f'<text x="{self._num(x)}" y="{self._num(y)}" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="{self._num(size)}" '
            f'fill="#333333" text-anchor="{anchor}" font-weight="{weight}">'
            f"{escape(content)}</text>"
        )


    def render(
        self,
        points: Sequence[Point],
        edges: Sequence[Edge],
        output_path: str | Path,
        title: str = "",
    ) -> Path:
        """Write the SVG for the edges and points to output_path."""
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.to_svg(points, edges, title), encoding="utf-8")
        return destination


class MatplotlibRenderer(Renderer):
    """renders the same data with matplotlib as well for extra check to compare with SVG.
       this render will output as PNG to differ for comparison, both should be viewed the same to help measure success.
       Use of same style and standard choices for enviroment values
    """
    extension = ".png"


    def __init__(self, dpi: int = 150) -> None:
        self.dpi = dpi

    def render(
        self,
        points: Sequence[Point],
        edges: Sequence[Edge],
        output_path: str | Path,
        title: str = "",
    ) -> Path:
        """Write a PNG for the points and edges."""
        try:
            import matplotlib.pyplot as plt
        except ImportError as error:
            raise ImportError(
                "matplotlib must be installed/imported. "
            ) from error

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        figure, axes = plt.subplots(figsize=(9, 9))
        for edge in edges:
            axes.plot(
                [edge.start.x, edge.end.x],
                [edge.start.y, edge.end.y],
                color="red",
                linewidth=1.0,
                zorder=1,
            )
        axes.scatter(
            [p.x for p in points], [p.y for p in points], color="blue", s=22, zorder=2
        )
        axes.set_title(title)
        axes.set_xlabel("x")
        axes.set_ylabel("y")
        axes.grid(True)
        figure.savefig(destination, dpi=self.dpi, bbox_inches="tight")
        plt.close(figure)
        return destination
