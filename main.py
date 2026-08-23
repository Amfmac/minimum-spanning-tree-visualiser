"""Author: Aidan MacDonald
Date: 15/08/26
Module: HCS503
University of Abertay

Main file, for running the python application
Running through Application.py was error prone, leading to 
the main.py being created for the specific purpose of running and parsing args
Industry standard approach from research online and via OpenAI, 2026 best practice insights and was able to fix issues
"""

from __future__ import annotations

import argparse
import sys
from mst_project.application import Application
from mst_project.graph import MAX_ASSIGNMENT_DISTANCE
from mst_project.mst import ALGORITHMS


def build_parser() -> argparse.ArgumentParser:
    """for defining the command line interface to eventually run, but also can use IDE run"""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="validate the week 1 test data and build a graph with limits on distances "
                    "and create the minimum spanning tree and render the it as an image SVG.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d", "--distance", type=float, default=MAX_ASSIGNMENT_DISTANCE,
    )
    parser.add_argument(
        "-a", "--algorithm", choices=sorted(ALGORITHMS), default="kruskal",
        help="algorithm used for the minimum spanning tree",
    )
    parser.add_argument(
        "-o", "--output-dir", default="output",
        help="where the rendered SVG and PNG images are written to",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="suppress the step-by-step narrative",
    )
    parser.add_argument(
        "--sweep", action="store_true",
        help="for edges, components, and MST weights across different distances",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the application itself."""
    args = build_parser().parse_args(argv)

    try:
        application = Application(
            distance=args.distance,
            algorithm=ALGORITHMS[args.algorithm](),
            output_dir=args.output_dir,
            verbose=not args.quiet,
        )
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    result = application.run()
    if args.sweep:
        application.sweep()

    return 0 if result.checksum_valid and result.weights_agree else 1

if __name__ == "__main__":
    raise SystemExit(main())
