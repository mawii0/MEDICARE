# Pharmacare — API Setup Guide

This guide covers deploying Pharmacare as a **Flask REST API**.

---

## Prerequisites

- Python 3.10+
- NVIDIA GPU with CUDA 12.x (RTX 4050 or better recommended; 6 GB VRAM minimum)
- Git

---

## 1. Clone & Enter Directory

```bash
git clone <repo-url>
cd Pharmacare-PH
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `torch` (with CUDA 12.4)
- `transformers`, `peft`, `bitsandbytes`, `accelerate`
- `flask`, `flask-cors`
- `scikit-learn`, `gensim`, `rank-bm25`, `joblib`

---

## 4. Prepare Data & Models

This repository includes all pre-trained artifacts. **No training is needed** to run the API.

Simply verify that `data/` and `models/` folders exist:

```bash
ls data/    # Should show ph_drug_database.jsonl, pharma_qa_pairs.jsonl, classifier_training_data.jsonl
ls models/  # Should show intent_clf.pkl, rx_clf.pkl, pharma_w2v.model, pharmacare_lora/
```

If you want to retrain everything from scratch, run the notebook:

```bash
jupyter notebook 01_end_to_end_demo.ipynb
```

---

## 5. Start the API Server

```bash
python api.py
```

Default: `http://0.0.0.0:5000`

Environment variables:
- `FLASK_HOST` — bind address (default: `0.0.0.0`)
- `FLASK_PORT` — port (default: `5000`)

Example:
```bash
set FLASK_PORT=8080
python api.py
```

On first startup the model warms up (~30–60s). Wait for:
```
[INFO] Model warm-up complete. API ready.
```

---

## 6. API Endpoints

### `GET /health`

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "device": "cuda",
  "gpu_name": "NVIDIA GeForce RTX 4050 Laptop GPU"
}
```

### `GET /info`

```bash
curl http://localhost:5000/info
```

Returns system metadata (model name, adapter path, safety features, supported languages).

### `POST /chat`

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What can I take for headache?"}'
```

**Response (enriched JSON):**
```json
{
  "query": "What can I take for headache?",
  "response": "**Drug Name:** Paracetamol\n**Brand Names:** Biogesic, Tempra...",
  "structured": {
    "drug_name": "Paracetamol",
    "brand_names": "Biogesic, Tempra",
    "drug_class": "Analgesic / Antipyretic",
    "indications": "fever, headache, mild to moderate pain",
    "dosage_adult": "500–1000 mg every 4–6 hours",
    "instructions": "Can be taken with or without food",
    "common_side_effects": "nausea, stomach discomfort",
    "generic_price": "PHP1.50",
    "branded_price": "PHP8.00",
    "where_to_find": "Mercury Drug, Rose Pharmacy, Generics Pharmacy, Botika ng Barangay"
  },
  "intent": "otc_recommendation",
  "rx_flag": false,
  "emergency": false,
  "language": "en",
  "latency_seconds": 1.234
}
```

**Field descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Echo of the user's message |
| `response` | string | Human-readable Markdown with **bold labels** |
| `structured` | object | Backend-ready JSON with segmented drug info |
| `intent` | string | Classified intent (e.g., `otc_recommendation`) |
| `rx_flag` | boolean | True if query involves a prescription drug |
| `emergency` | boolean | True if emergency keywords were detected |
| `language` | string | Detected language (`en` or `tl`) |
| `latency_seconds` | float | Total response time |

**The `response` field** is optimized for human reading: it uses bold labels, skips empty fields, and displays prices with the ₱ symbol.

**The `structured` field** is optimized for backend consumption: it keeps prices as `"PHP"` for clean parsing, includes all relevant segments per intent, and follows a consistent schema.

---

## 7. Python Integration

### Using `chat()` (response string only)

```python
from src.inference import chat

response = chat("What can I take for headache?")
print(response)
# Output: **Drug Name:** Paracetamol...
```

### Using `chat_full()` (full response dict)

```python
from src.inference import chat_full

result = chat_full("What can I take for headache?")
print(result["response"])      # Markdown string
print(result["structured"])     # JSON dict
print(result["intent"])         # "otc_recommendation"
print(result["rx_flag"])        # False
```

### Using the Flask API from Python

```python
import requests

response = requests.post(
    "http://localhost:5000/chat",
    json={"message": "What can I take for headache?"}
)
data = response.json()

print(data["response"])      # Markdown
print(data["structured"])    # JSON
```

---

## 8. Notes

- **Offline only**: No external LLM APIs are called at inference time.
- **First request**: May be slightly slower due to GPU warm-up.
- **Safety**: The `/chat` endpoint enforces emergency bypass, Rx warnings, disclaimers, and RA 9165 controlled-substance notes automatically.
- **Structured output**: The `structured` field makes it easy to build frontend UIs, mobile apps, or database integrations.

---

## 9. Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'flask'` | `pip install flask flask-cors` |
| `CUDA out of memory` | Close other GPU apps; ensure 4-bit quantization is active |
| `Adapter not found` | Verify `models/pharmacare_lora/adapter_model.safetensors` exists |
| `Classifier inference failed` | Verify `models/intent_clf.pkl`, `models/rx_clf.pkl`, and vectorizers exist |
| `Empty structured JSON` | Restart Jupyter kernel / delete `src/__pycache__` after source edits |
| `UnicodeEncodeError` | Ensure terminal supports UTF-8; the ₱ symbol requires UTF-8 |

---

## 10. Production Checklist

Before deploying to production:

- [ ] Set `FLASK_HOST=0.0.0.0` for external access (or use a reverse proxy)
- [ ] Run behind **Gunicorn** or **uWSGI** for production WSGI serving
- [ ] Add **rate limiting** (e.g., Flask-Limiter)
- [ ] Add **request logging** (anonymized per RA 10173)
- [ ] Set up **health checks** via `/health` endpoint
- [ ] Monitor GPU memory usage
- [ ] Test emergency keyword detection with sample queries

---

## License & Compliance

- Drug data is approximate (2024 estimates) for educational use.
- Controlled substances include RA 9165 warnings.
- Always consult a licensed physician or pharmacist.
