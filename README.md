# Oleg-helper

Stretch ceiling calculator — snap a photo of a hand-drawn ceiling plan and get area + perimeter instantly.

## How it works

1. Dealer takes a photo of their hand-drawn ceiling drawing (any shape, any units)
2. Claude AI vision reads the shape, dimensions, and units — even messy handwriting
3. Calculator computes **square footage** and **perimeter** with unit conversion

## Supported shapes

- Rectangle
- Triangle
- L-shape
- Trapezoid
- Circle
- Any irregular polygon

## Supported units

mm, cm, m, inches, feet — auto-detected from the drawing

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## Usage

```bash
python main.py photo_of_drawing.jpg
```

Output:
```
=============================================
  STRETCH CEILING CALCULATION RESULTS
=============================================
  Shape detected:  RECTANGLE
---------------------------------------------
  Area:            167.92 sq ft
                   15.6000 sq m
---------------------------------------------
  Perimeter:       51.18 ft
                   15.6000 m
=============================================
```

For JSON output:
```bash
python main.py photo_of_drawing.jpg --json
```
