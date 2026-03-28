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


def get_measurement_value(shape_data, key):
    """Get a measurement value from shape_data by its confidence key."""
    shape = shape_data["shape"].lower()

    if shape == "circle" and key == "radius":
        return shape_data["radius"]

    if key.startswith("rect1_"):
        field = key.replace("rect1_", "")
        return shape_data["rect1"][field]
    if key.startswith("rect2_"):
        field = key.replace("rect2_", "")
        return shape_data["rect2"][field]

    if key.startswith("vertex_"):
        idx = int(key.replace("vertex_", ""))
        return shape_data["vertices"][idx]

    if "sides" in shape_data and key in shape_data["sides"]:
        return shape_data["sides"][key]

    return None


def set_measurement_value(shape_data, key, new_value):
    """Update a measurement value in shape_data by its confidence key."""
    shape = shape_data["shape"].lower()

    if shape == "circle" and key == "radius":
        shape_data["radius"] = new_value
        return

    if key.startswith("rect1_"):
        field = key.replace("rect1_", "")
        shape_data["rect1"][field] = new_value
        return
    if key.startswith("rect2_"):
        field = key.replace("rect2_", "")
        shape_data["rect2"][field] = new_value
        return

    if key.startswith("vertex_"):
        idx = int(key.replace("vertex_", ""))
        shape_data["vertices"][idx] = new_value
        return

    if "sides" in shape_data and key in shape_data["sides"]:
        shape_data["sides"][key] = new_value


def confirm_uncertain_measurements(shape_data):
    """
    Check for low-confidence measurements and ask user to confirm or correct them.
    Returns the (possibly modified) shape_data.
    """
    confidence = shape_data.get("confidence", {})
    unit = shape_data.get("unit", "?")
    unit_confidence = shape_data.get("unit_confidence", "high")

    uncertain = {k: v for k, v in confidence.items() if v == "low"}

    if not uncertain and unit_confidence != "low":
        print("All measurements read with high confidence.")
        return shape_data

    print("\n" + "!" * 45)
    print("  CONFIRMATION NEEDED — uncertain readings")
    print("!" * 45)

    # Check unit confidence first
    if unit_confidence == "low":
        print(f"\n  Unit detected: {unit}  [LOW CONFIDENCE]")
        new_unit = input(f"  Confirm unit or type correct one [{unit}]: ").strip()
        if new_unit:
            shape_data["unit"] = new_unit

    # Check each uncertain measurement
    for key in uncertain:
        current_value = get_measurement_value(shape_data, key)
        if current_value is None:
            continue

        if key.startswith("vertex_"):
            print(f"\n  {key}: {current_value}  [LOW CONFIDENCE]")
            new_val = input(f"  Confirm or enter correct [x,y] ({current_value}): ").strip()
            if new_val:
                try:
                    parts = [float(x.strip()) for x in new_val.replace("[", "").replace("]", "").split(",")]
                    if len(parts) == 2:
                        set_measurement_value(shape_data, key, parts)
                except ValueError:
                    print("  Invalid input, keeping original value.")
        else:
            print(f"\n  {key}: {current_value} {unit}  [LOW CONFIDENCE]")
            new_val = input(f"  Confirm or enter correct value ({current_value}): ").strip()
            if new_val:
                try:
                    set_measurement_value(shape_data, key, float(new_val))
                except ValueError:
                    print("  Invalid number, keeping original value.")

    print("\nMeasurements confirmed.\n")
    return shape_data


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
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation prompts for uncertain measurements.",
    )
    args = parser.parse_args()

    try:
        print(f"Analyzing image: {args.image} ...")
        shape_data = analyze_image(args.image)
        print(f"Detected shape: {shape_data['shape']} (unit: {shape_data.get('unit', '?')})")

        if not args.no_confirm:
            shape_data = confirm_uncertain_measurements(shape_data)

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
