"""
Pharmacare — Flask REST API
=================================
Serves the fine-tuned TinyLlama-1.1B-Chat + LoRA chatbot via HTTP.

Endpoints:
  POST /chat          — Get a bot response
  GET  /health        — Health check
  GET  /info          — System metadata

Usage:
  python api.py

Environment:
  FLASK_PORT  (default: 5000)
  FLASK_HOST  (default: 0.0.0.0)
"""

import os
import sys
import time
import threading
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ensure project root on path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.inference import chat, chat_full

app = Flask(__name__)
CORS(app)

model_state = {
    "loading": True,
    "ready": False,
    "error": None,
}


def _warmup_model():
    print("[INFO] Loading model + adapters (this may take ~30-60s)...")
    try:
        chat_full("Hello")
        model_state["ready"] = True
        model_state["error"] = None
        print("[INFO] Model warm-up complete. API ready.")
    except Exception as e:
        model_state["error"] = str(e)
        print(f"[FATAL] Model failed to load: {e}")
    finally:
        model_state["loading"] = False

# ------------------------------------------------------------------------------
# Warm-up: verify model loads before accepting traffic
# ------------------------------------------------------------------------------
print("[INFO] Starting Pharmacare API...")
threading.Thread(target=_warmup_model, daemon=True).start()

# ------------------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    status = "ready" if model_state["ready"] else "loading" if model_state["loading"] else "error"
    return jsonify({
        "status": status,
        "model_loaded": model_state["ready"],
        "loading": model_state["loading"],
        "error": model_state["error"],
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    })


@app.route("/info", methods=["GET"])
def info():
    return jsonify({
        "app": "Pharmacare",
        "version": "1.0.0",
        "base_model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "adapter_path": "models/pharmacare_lora",
        "quantization": "4-bit NF4",
        "languages": ["en", "tl"],
        "safety_features": [
            "Emergency keyword bypass",
            "Rx restriction injection",
            "RA 9165 controlled-substance warning",
            "Mandatory disclaimer",
            "BM25 grounding retrieval",
        ],
    })


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json(force=True, silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Missing 'message' field."}), 400

    if not model_state["ready"]:
        return jsonify({
            "error": "Model is still loading.",
            "status": "loading",
        }), 503

    start = time.time()
    try:
        result = chat_full(user_message)
        latency = time.time() - start
        return jsonify({
            "query": user_message,
            "response": result["response"],
            "structured": result.get("structured", {}),
            "intent": result.get("intent", "unknown"),
            "rx_flag": result.get("rx_flag", False),
            "emergency": result.get("emergency", False),
            "language": result.get("language", "en"),
            "latency_seconds": round(latency, 3),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 5000))
    # threaded=True allows concurrent requests
    app.run(host=host, port=port, threaded=True)
