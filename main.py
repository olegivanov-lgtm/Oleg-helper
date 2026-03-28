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
import csv
import json
import os
import sys
from pathlib import Path

from analyzer import analyze_image
from calculator import calculate

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


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


def process_single(image_path, no_confirm=False):
    """Process a single image and return results."""
    print(f"Analyzing image: {image_path} ...")
    shape_data = analyze_image(image_path)
    print(f"Detected shape: {shape_data['shape']} (unit: {shape_data.get('unit', '?')})")

    if not no_confirm:
        shape_data = confirm_uncertain_measurements(shape_data)

    return calculate(shape_data)


def process_batch(folder_path, output_csv=None):
    """Process all images in a folder. Optionally save results to CSV."""
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    images = sorted(
        f for f in folder.iterdir()
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not images:
        print(f"No supported images found in '{folder_path}'.")
        return

    print(f"Found {len(images)} image(s) in '{folder_path}'.\n")

    all_results = []
    for i, img in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] {img.name}")
        print("-" * 45)
        try:
            results = process_single(str(img), no_confirm=True)
            results["file"] = img.name
            all_results.append(results)
            print_results(results)
        except Exception as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            all_results.append({"file": img.name, "error": str(e)})

    # Summary
    successful = [r for r in all_results if "error" not in r]
    failed = [r for r in all_results if "error" in r]

    print("\n" + "=" * 45)
    print(f"  BATCH COMPLETE: {len(successful)} OK, {len(failed)} failed")
    print("=" * 45)

    if successful:
        total_ft2 = sum(r["area"]["ft2"] for r in successful)
        total_m2 = sum(r["area"]["m2"] for r in successful)
        print(f"  Total area:  {total_ft2:.2f} sq ft / {total_m2:.4f} sq m")

    # Save CSV if requested
    if output_csv and successful:
        with open(output_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["File", "Shape", "Area (sq ft)", "Area (sq m)", "Perimeter (ft)", "Perimeter (m)"])
            for r in successful:
                writer.writerow([
                    r["file"], r["shape"],
                    f"{r['area']['ft2']:.2f}", f"{r['area']['m2']:.4f}",
                    f"{r['perimeter']['ft']:.2f}", f"{r['perimeter']['m']:.4f}",
                ])
        print(f"\n  Results saved to: {output_csv}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Calculate stretch ceiling area and perimeter from drawing photos."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Single image mode (default)
    single = subparsers.add_parser("calc", help="Calculate from a single image.")
    single.add_argument("image", help="Path to the ceiling drawing image.")
    single.add_argument("--json", action="store_true", help="Output raw JSON.")
    single.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompts.")

    # Batch mode
    batch = subparsers.add_parser("batch", help="Process all images in a folder.")
    batch.add_argument("folder", help="Path to folder with drawing images.")
    batch.add_argument("--csv", metavar="FILE", help="Save results to a CSV file.")

    # Web server
    web = subparsers.add_parser("web", help="Start the web interface.")
    web.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0).")
    web.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000).")

    args = parser.parse_args()

    # Default to showing help if no command
    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "calc":
            results = process_single(args.image, no_confirm=args.no_confirm)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print_results(results)

        elif args.command == "batch":
            process_batch(args.folder, output_csv=args.csv)

        elif args.command == "web":
            from web_app import create_app
            app = create_app()
            print(f"Starting web interface at http://{args.host}:{args.port}")
            app.run(host=args.host, port=args.port, debug=True)

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
