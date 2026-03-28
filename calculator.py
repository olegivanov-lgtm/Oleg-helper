"""
Geometry calculations and unit conversion for stretch ceiling measurements.
"""

import math

# Conversion factors to meters
TO_METERS = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "in": 0.0254,
    "inch": 0.0254,
    "inches": 0.0254,
    "ft": 0.3048,
    "feet": 0.3048,
    "foot": 0.3048,
}

# Conversion factors from square meters
FROM_SQ_METERS = {
    "m2": 1.0,
    "ft2": 10.7639,
    "in2": 1550.0031,
    "cm2": 10000.0,
}

# Conversion factors from meters (linear)
FROM_METERS = {
    "m": 1.0,
    "ft": 3.28084,
    "in": 39.3701,
    "cm": 100.0,
    "mm": 1000.0,
}


def convert_to_meters(value, unit):
    """Convert a measurement value to meters."""
    unit = unit.lower().strip()
    if unit not in TO_METERS:
        raise ValueError(f"Unknown unit: '{unit}'. Supported: {list(TO_METERS.keys())}")
    return value * TO_METERS[unit]


def polygon_area_and_perimeter(vertices_m):
    """
    Calculate area and perimeter of any polygon given vertices in meters.
    Uses the Shoelace formula for area.
    Vertices should be a list of (x, y) tuples in order.
    """
    n = len(vertices_m)
    if n < 3:
        raise ValueError("A polygon needs at least 3 vertices.")

    # Shoelace formula for area
    area = 0.0
    for i in range(n):
        x1, y1 = vertices_m[i]
        x2, y2 = vertices_m[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    area = abs(area) / 2.0

    # Perimeter
    perimeter = 0.0
    for i in range(n):
        x1, y1 = vertices_m[i]
        x2, y2 = vertices_m[(i + 1) % n]
        perimeter += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    return area, perimeter


def circle_area_and_perimeter(radius_m):
    """Calculate area and circumference of a circle."""
    area = math.pi * radius_m ** 2
    perimeter = 2 * math.pi * radius_m
    return area, perimeter


def calculate(shape_data):
    """
    Main calculation dispatcher.

    Accepts shape_data dict from the analyzer with format:
    {
        "shape": "rectangle" | "polygon" | "circle" | "l_shape" | "triangle" | ...,
        "unit": "mm" | "cm" | "m" | "ft" | "in" | ...,
        "vertices": [[x1,y1], [x2,y2], ...],  # for polygon-based shapes
        -- OR --
        "sides": {"length": ..., "width": ...},  # for rectangle
        "sides": {"base": ..., "height": ..., "side_a": ..., "side_b": ...},  # triangle
        "radius": ...,  # for circle
        -- OR for L-shape --
        "rect1": {"length": ..., "width": ...},
        "rect2": {"length": ..., "width": ...},
    }

    Returns dict with area and perimeter in both metric and imperial.
    """
    shape = shape_data["shape"].lower().strip()
    unit = shape_data.get("unit", "m")

    area_m2 = 0.0
    perimeter_m = 0.0

    if "vertices" in shape_data:
        # Universal polygon path — works for ANY shape
        vertices_m = [
            (convert_to_meters(x, unit), convert_to_meters(y, unit))
            for x, y in shape_data["vertices"]
        ]
        area_m2, perimeter_m = polygon_area_and_perimeter(vertices_m)

    elif shape == "rectangle":
        sides = shape_data["sides"]
        l = convert_to_meters(sides["length"], unit)
        w = convert_to_meters(sides["width"], unit)
        area_m2 = l * w
        perimeter_m = 2 * (l + w)

    elif shape == "triangle":
        sides = shape_data["sides"]
        base = convert_to_meters(sides["base"], unit)
        height = convert_to_meters(sides["height"], unit)
        area_m2 = 0.5 * base * height
        # If individual side lengths provided, use them for perimeter
        if "side_a" in sides and "side_b" in sides and "side_c" in sides:
            a = convert_to_meters(sides["side_a"], unit)
            b = convert_to_meters(sides["side_b"], unit)
            c = convert_to_meters(sides["side_c"], unit)
            perimeter_m = a + b + c
        else:
            # Approximate: assume right triangle if only base/height given
            hyp = math.sqrt(base ** 2 + height ** 2)
            perimeter_m = base + height + hyp

    elif shape == "l_shape":
        r1 = shape_data["rect1"]
        r2 = shape_data["rect2"]
        l1 = convert_to_meters(r1["length"], unit)
        w1 = convert_to_meters(r1["width"], unit)
        l2 = convert_to_meters(r2["length"], unit)
        w2 = convert_to_meters(r2["width"], unit)
        area_m2 = (l1 * w1) + (l2 * w2)
        # L-shape perimeter (outer edges of combined rectangles)
        perimeter_m = 2 * (l1 + w1) + 2 * (l2 + w2) - 2 * min(w1, w2)

    elif shape == "trapezoid":
        sides = shape_data["sides"]
        a = convert_to_meters(sides["top"], unit)
        b = convert_to_meters(sides["bottom"], unit)
        h = convert_to_meters(sides["height"], unit)
        area_m2 = 0.5 * (a + b) * h
        if "left" in sides and "right" in sides:
            left = convert_to_meters(sides["left"], unit)
            right = convert_to_meters(sides["right"], unit)
            perimeter_m = a + b + left + right
        else:
            # Approximate slanted sides
            offset = abs(b - a) / 2
            slant = math.sqrt(offset ** 2 + h ** 2)
            perimeter_m = a + b + 2 * slant

    elif shape == "circle":
        radius = convert_to_meters(shape_data["radius"], unit)
        area_m2, perimeter_m = circle_area_and_perimeter(radius)

    else:
        raise ValueError(f"Unsupported shape: '{shape}'. Provide vertices for custom shapes.")

    return format_results(area_m2, perimeter_m, shape)


def format_results(area_m2, perimeter_m, shape):
    """Format calculation results with multiple unit conversions."""
    return {
        "shape": shape,
        "area": {
            "m2": round(area_m2, 4),
            "ft2": round(area_m2 * FROM_SQ_METERS["ft2"], 4),
        },
        "perimeter": {
            "m": round(perimeter_m, 4),
            "ft": round(perimeter_m * FROM_METERS["ft"], 4),
        },
    }
