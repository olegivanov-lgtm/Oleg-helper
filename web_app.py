"""
Flask web app — web upload interface + WhatsApp webhook (Twilio).
"""

import json
import os
import tempfile
from pathlib import Path

from flask import Flask, request, jsonify, render_template

from analyzer import analyze_image
from calculator import calculate


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

    UPLOAD_DIR = Path(tempfile.gettempdir()) / "ceiling_uploads"
    UPLOAD_DIR.mkdir(exist_ok=True)

    SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # ── Web Interface ────────────────────────────────────

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/upload", methods=["POST"])
    def upload():
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        ext = Path(file.filename).suffix.lower()
        if ext not in SUPPORTED:
            return jsonify({"error": f"Unsupported format: {ext}"}), 400

        # Save temp file
        tmp_path = UPLOAD_DIR / f"upload_{os.urandom(8).hex()}{ext}"
        file.save(str(tmp_path))

        try:
            shape_data = analyze_image(str(tmp_path))
            results = calculate(shape_data)

            # Add confidence info for the UI
            results["confidence"] = shape_data.get("confidence", {})
            results["unit_confidence"] = shape_data.get("unit_confidence", "high")
            results["raw"] = {
                k: v for k, v in shape_data.items()
                if k not in ("confidence", "unit_confidence")
            }

            return jsonify(results)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            tmp_path.unlink(missing_ok=True)

    @app.route("/recalculate", methods=["POST"])
    def recalculate():
        """Recalculate after user corrects measurements."""
        shape_data = request.get_json()
        if not shape_data:
            return jsonify({"error": "No data provided"}), 400

        try:
            results = calculate(shape_data)
            return jsonify(results)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ── WhatsApp Webhook (Twilio) ────────────────────────

    @app.route("/whatsapp", methods=["POST"])
    def whatsapp_webhook():
        """
        Twilio WhatsApp webhook endpoint.
        Receives images from dealers, processes them, replies with results.
        """
        from twilio.twiml.messaging_response import MessagingResponse

        resp = MessagingResponse()
        num_media = int(request.form.get("NumMedia", 0))
        sender = request.form.get("From", "unknown")

        if num_media == 0:
            resp.message(
                "Hi! Send me a photo of your ceiling drawing and "
                "I'll calculate the area and perimeter for you."
            )
            return str(resp), 200, {"Content-Type": "text/xml"}

        # Process each image sent
        for i in range(num_media):
            media_url = request.form.get(f"MediaUrl{i}")
            media_type = request.form.get(f"MediaContentType{i}", "")

            if not media_type.startswith("image/"):
                resp.message(f"File {i+1}: Not an image. Please send a photo of your drawing.")
                continue

            try:
                # Download image from Twilio
                ext = _media_type_to_ext(media_type)
                tmp_path = UPLOAD_DIR / f"wa_{os.urandom(8).hex()}{ext}"
                _download_twilio_media(media_url, str(tmp_path))

                # Analyze and calculate
                shape_data = analyze_image(str(tmp_path))
                results = calculate(shape_data)

                # Check confidence
                confidence = shape_data.get("confidence", {})
                low_conf = [k for k, v in confidence.items() if v == "low"]

                # Build reply
                reply = (
                    f"*Ceiling Calculation Results*\n"
                    f"Shape: {results['shape'].upper()}\n\n"
                    f"Area: {results['area']['ft2']:.2f} sq ft "
                    f"({results['area']['m2']:.4f} sq m)\n"
                    f"Perimeter: {results['perimeter']['ft']:.2f} ft "
                    f"({results['perimeter']['m']:.4f} m)"
                )

                if low_conf:
                    reply += (
                        f"\n\n⚠️ *Some measurements were hard to read:* "
                        f"{', '.join(low_conf)}\n"
                        f"Please double-check these values. "
                        f"Reply with corrections if needed."
                    )

                resp.message(reply)

            except Exception as e:
                resp.message(f"Sorry, I couldn't process that image: {e}")
            finally:
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)

        return str(resp), 200, {"Content-Type": "text/xml"}

    return app


def _media_type_to_ext(media_type):
    """Convert MIME type to file extension."""
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
    }
    return mapping.get(media_type, ".jpg")


def _download_twilio_media(url, save_path):
    """Download media from Twilio with authentication."""
    import requests

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")

    response = requests.get(url, auth=(account_sid, auth_token), timeout=30)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)
