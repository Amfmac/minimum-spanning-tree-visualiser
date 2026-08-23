"""Author: Aidan MacDonald
Date: 15/08/26
Module: HCS503
University of Abertay
"""

from __future__ import annotations
import math

class Point:
    """
    Points can't change, they are immutable so x and y are read only properties.
    That way points can be hashed properly and safely, so they can be used
    by the graph and the MST algorithms without a key being able to change its own hash after being inserted into the graph.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        """The horizontal x coordinate."""
        return self._x

    @property
    def y(self) -> float:
        """The vertical y coordinate."""
        return self._y

    def getX(self) -> float:
        """return the x coordinate."""
        return self._x

    def getY(self) -> float: 
        """return the y coordinate."""
        return self._y

    def distance(self, other: "Point") -> float:
        """return the distance using math module between this point and other parameter point."""
        return math.hypot(self._x - other.x, self._y - other.y)

    def __str__(self) -> str:
        """to be redable format like in past module acitvities, like activity 1.6 early on"""
        return f"x: {self._x}  y: {self._y}"

    def __repr__(self) -> str:
        return f"Point({self._x!r}, {self._y!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self._x == other.x and self._y == other.y

    def __hash__(self) -> int:
        return hash((self._x, self._y))




def point_test() -> None:
    """reused the test code from activity 1.6 earlier in the module."""
    p1 = Point(1, 1)
    p2 = Point(2, 2)
    print(f" p1: {p1}")
    print(f" p2: {p2}")
    print(f"distance p1 <-> p2 { p1.distance(p2) }")

if __name__ == "__main__":
    point_test()
