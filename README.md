# Oleg-helper

Stretch ceiling calculator — snap a photo of a hand-drawn ceiling plan and get area + perimeter instantly.

## How it works

1. Dealer takes a photo of their hand-drawn ceiling drawing (any shape, any units)
2. Claude AI vision reads the shape, dimensions, and units — even messy handwriting
3. If any measurement is hard to read, it asks for confirmation before calculating
4. Calculator computes **square footage** and **perimeter** with unit conversion

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

### Single image (CLI)

```bash
python main.py calc photo.jpg
python main.py calc photo.jpg --json
python main.py calc photo.jpg --no-confirm
```

### Batch processing

Process all images in a folder:

```bash
python main.py batch ./drawings/
python main.py batch ./drawings/ --csv results.csv
```

### Web interface

```bash
python main.py web
python main.py web --port 8080
```

Open your browser to `http://localhost:5000` — drag and drop drawings to get instant results. Uncertain measurements are highlighted for correction.

### WhatsApp (via Twilio)

Dealers send photos directly via WhatsApp and get results back automatically.

Setup:
1. Create a Twilio account and set up a WhatsApp sandbox
2. Set environment variables:
   ```bash
   export TWILIO_ACCOUNT_SID=your-sid
   export TWILIO_AUTH_TOKEN=your-token
   ```
3. Start the web server: `python main.py web`
4. Set your Twilio WhatsApp webhook URL to: `https://your-domain.com/whatsapp`

If a measurement is unclear, the bot warns the dealer in the reply.
