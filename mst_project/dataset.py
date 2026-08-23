"""Author: Aidan MacDonald
Date: 15/08/26
Module: HCS503
University of Abertay

The test data from the helper file and the first requirement of SHA-256 check validation
check against the checksum from the helper file using the string of y values
"""

from __future__ import annotations
import hashlib
from collections.abc import Iterable
from .point import Point

"The 100 y values from the week 1 helperfile"
Y_VALUES: tuple[int, ...] = (
    37, 66, 65, 84, 69, 94, 34, 40, 3, 80,
    81, 41, 54, 66, 83, 86, 10, 61, 44, 96,
    79, 96, 83, 31, 44, 35, 76, 51, 99, 1,
    93, 89, 94, 19, 74, 41, 41, 32, 6, 40,
    29, 37, 10, 21, 43, 30, 12, 27, 15, 41,
    35, 74, 65, 4, 68, 15, 49, 83, 48, 40,
    50, 25, 61, 12, 66, 48, 75, 41, 20, 71,
    70, 35, 26, 24, 64, 3, 27, 99, 35, 42,
    13, 95, 43, 45, 72, 0, 49, 93, 69, 43,
    22, 97, 25, 72, 84, 93, 35, 87, 88, 20,
)

PUBLISHED_SHA256 = "bec69bfbafe2e553b70fd682656c4a1c79089b648382123cb72fddd65427b7c0"
"""taken from file"""

class DataSet:
    """
    The x and y test data, along with with the checksum to verify it
    function seperation for individual needs
    """

    def __init__(
        self,
        y_values: Iterable[int],
        expected_checksum: str | None = None,
        x_start: int = 1,
    ) -> None:
        self.y_values: tuple[int, ...] = tuple(y_values)
        self.expected_checksum = expected_checksum
        self.x_start = x_start

    @classmethod
    def week1(cls) -> "DataSet":
        """returns the data set week one helper file, code reuse from previous weeks theme"""
        return cls(Y_VALUES, PUBLISHED_SHA256)

    @property
    def x_values(self) -> tuple[int, ...]:
        return tuple(range(self.x_start, self.x_start + len(self.y_values)))

    def y_string(self) -> str:
        """return the y values concatenated into one string, no seperators like week 1 file
        """
        return "".join(str(value) for value in self.y_values)

    def checksum(self) -> str:
        """return the SHA-256 digest form the  initialised string"""
        return hashlib.sha256(self.y_string().encode("utf-8")).hexdigest()

    def is_valid(self) -> bool:
        """
        return true if the digest matches the one from file, no checksum will be valid as isn't different for current cleanliness
        """
        return self.expected_checksum is None or self.checksum() == self.expected_checksum

    def points(self) -> list[Point]:
        """second requirement to instatiate the point values, zip obejct"""
        return [Point(x, y) for x, y in zip(self.x_values, self.y_values)]

    def __len__(self) -> int:
        return len(self.y_values)

    def __str__(self) -> str:
        return f"DataSet({len(self)} points, checksum {'valid' if self.is_valid() else 'invalid'})"
