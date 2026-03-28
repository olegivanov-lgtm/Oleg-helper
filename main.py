#!/usr/bin/env python3
"""
Stretch Ceiling Calculator — CLI entry point.

Usage:
    python main.py <image_path>

Analyzes a photo of a hand-drawn ceiling plan and calculates
square footage, perimeter, and shape.

Requires: ANTHROPIC_API_KEY environment variable.
"""

import argparse
import sys

from analyzer import analyze_image
from calculator import calculate


def print_results(results):
    """Print calculation results in a clean, readable format."""
    print("\n" + "=" * 45)
    print("  STRETCH CEILING CALCULATION RESULTS")
    print("=" * 45)
    print(f"  Shape detected:  {results['shape'].upper()}")
    print("-" * 45)
    print(f"  Area:            {results['area']['ft2']:.2f} sq ft")
    print(f"                   {results['area']['m2']:.4f} sq m")
    print("-" * 45)
    print(f"  Perimeter:       {results['perimeter']['ft']:.2f} ft")
    print(f"                   {results['perimeter']['m']:.4f} m")
    print("=" * 45 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate stretch ceiling area and perimeter from a drawing photo."
    )
    parser.add_argument(
        "image",
        help="Path to the ceiling drawing image (jpg, png, gif, webp).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text.",
    )
    args = parser.parse_args()

    try:
        print(f"Analyzing image: {args.image} ...")
        shape_data = analyze_image(args.image)
        print(f"Detected shape: {shape_data['shape']} (unit: {shape_data.get('unit', '?')})")

        results = calculate(shape_data)

        if args.json:
            import json
            print(json.dumps(results, indent=2))
        else:
            print_results(results)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
