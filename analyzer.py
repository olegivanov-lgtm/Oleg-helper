"""
Image analysis module using Claude API vision to extract ceiling dimensions from drawings.
"""

import base64
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import anthropic

# Load .env file from project root
load_dotenv(Path(__file__).parent / ".env")

SUPPORTED_IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

EXTRACTION_PROMPT = """You are an expert at reading architectural and hand-drawn ceiling/floor plan drawings.

Analyze this image of a stretch ceiling drawing. Extract ALL dimensions and the shape.

IMPORTANT RULES:
1. Identify the shape: rectangle, triangle, l_shape, trapezoid, circle, or polygon (for irregular shapes).
2. Read ALL measurements and their units from the drawing. Handle messy handwriting carefully.
3. If no unit is labeled, try to infer from the numbers (e.g., 4200 is likely mm, 4.2 is likely m, 14 is likely ft).
4. For irregular shapes, provide vertices as (x, y) coordinates based on the dimensions shown.
5. Be precise — these measurements are used to order materials.
6. For EACH measurement, rate your confidence: "high" if clearly readable, "low" if the handwriting is unclear, smudged, ambiguous, or you had to guess.
7. If you are unsure about the unit, mark unit_confidence as "low".

Return ONLY valid JSON. Always include a "confidence" object that maps each measurement label to "high" or "low".

For RECTANGLE:
{"shape": "rectangle", "unit": "m", "unit_confidence": "high", "sides": {"length": 5.2, "width": 3.1}, "confidence": {"length": "high", "width": "low"}}

For TRIANGLE:
{"shape": "triangle", "unit": "m", "unit_confidence": "high", "sides": {"base": 4.0, "height": 3.0, "side_a": 4.0, "side_b": 3.0, "side_c": 5.0}, "confidence": {"base": "high", "height": "high", "side_a": "low", "side_b": "high", "side_c": "high"}}

For L-SHAPE:
{"shape": "l_shape", "unit": "m", "unit_confidence": "high", "rect1": {"length": 5.0, "width": 3.0}, "rect2": {"length": 2.0, "width": 2.0}, "confidence": {"rect1_length": "high", "rect1_width": "low", "rect2_length": "high", "rect2_width": "high"}}

For TRAPEZOID:
{"shape": "trapezoid", "unit": "m", "unit_confidence": "high", "sides": {"top": 3.0, "bottom": 5.0, "height": 4.0, "left": 4.1, "right": 4.1}, "confidence": {"top": "high", "bottom": "high", "height": "low", "left": "high", "right": "high"}}

For CIRCLE:
{"shape": "circle", "unit": "m", "unit_confidence": "high", "radius": 2.5, "confidence": {"radius": "high"}}

For ANY IRREGULAR POLYGON (use this when the shape doesn't fit the above):
{"shape": "polygon", "unit": "m", "unit_confidence": "high", "vertices": [[0,0], [5,0], [5,3], [3,3], [3,5], [0,5]], "confidence": {"vertex_0": "high", "vertex_1": "high", "vertex_2": "low", "vertex_3": "high", "vertex_4": "low", "vertex_5": "high"}}

Return ONLY the JSON, no other text."""


def load_image_as_base64(image_path):
    """Load an image file and return base64-encoded data with media type."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_IMAGE_TYPES:
        raise ValueError(
            f"Unsupported image format: {suffix}. "
            f"Supported: {list(SUPPORTED_IMAGE_TYPES.keys())}"
        )

    media_type = SUPPORTED_IMAGE_TYPES[suffix]
    image_data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    return image_data, media_type


def analyze_image(image_path):
    """
    Send a ceiling drawing image to Claude vision API and extract shape data.

    Args:
        image_path: Path to the image file (jpg, png, gif, webp).

    Returns:
        dict with shape data ready for calculator.calculate().

    Requires ANTHROPIC_API_KEY environment variable to be set.
    """
    image_data, media_type = load_image_as_base64(image_path)

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT,
                    },
                ],
            }
        ],
    )

    response_text = message.content[0].text.strip()

    # Extract JSON from response (handle if wrapped in markdown code block)
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        json_lines = [l for l in lines if not l.startswith("```")]
        response_text = "\n".join(json_lines)

    try:
        shape_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse AI response as JSON.", file=sys.stderr)
        print(f"Raw response:\n{response_text}", file=sys.stderr)
        raise ValueError(f"Failed to parse shape data from image: {e}")

    return shape_data
