# Pharmacare

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6.0-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-Educational-green.svg)]()

**Philippine-Contextualized Pharmaceutical Chatbot — Bilingual, Safety-First, API-Deployable**

---

## Table of Contents

1. [What is Pharmacare?](#1-what-is-pharmacare-ph)
2. [Key Features](#2-key-features)
3. [System Architecture](#3-system-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Quick Start — Run the API (No Training Needed)](#5-quick-start--run-the-api-no-training-needed)
6. [Full Pipeline — Train from Scratch](#6-full-pipeline--train-from-scratch)
7. [API Documentation](#7-api-documentation)
8. [Project Structure](#8-project-structure)
9. [Safety & Compliance](#9-safety--compliance)
10. [Future Roadmap](#10-future-roadmap)
11. [License](#11-license)

---

## 1. What is Pharmacare?

Pharmacare is a bilingual pharmaceutical information chatbot designed for patients in the Philippines. It answers medicine-related queries using a fine-tuned lightweight LLM, grounded by a local drug database, and protected by multiple safety guardrails. All inference runs locally on the server — no external LLM APIs are called at runtime.

This project was developed for **CCS 249 — Natural Language Processing**, demonstrating secure, privacy-preserving AI that never leaks patient data to external APIs.

### Why This Matters

- **Local inference** — no external LLM APIs are called at runtime, ensuring data sovereignty
- **Patient safety first** — Rx drugs never include dosage recommendations
- **Philippine context** — Prices in ₱, PH brand names, FDA-PH registered drugs
- **Bilingual** — English queries → English answers; Taglish queries → Taglish answers

---

## 2. Key Features

| Feature | Description |
|---------|-------------|
| **OTC Medicine Recommendations** | Suggests over-the-counter drugs for common symptoms with standard adult dosages and approximate Philippine prices |
| **Prescription Drug Information** | Provides neutral, factual overviews of Rx drugs **without** dosage instructions. Automatically injects a mandatory prescription warning |
| **Price & Availability (PH)** | Cites approximate generic and branded prices in ₱, and lists major PH pharmacies |
| **Side Effects & Interactions** | Describes common/serious side effects and warns about potential drug-drug interactions |
| **Emergency Escalation** | Detects emergency keywords and immediately bypasses the LLM to return a 911 / DOH Hotline escalation message |
| **Bilingual Responses** | Detects Taglish/Filipino queries and responds in Taglish; English queries receive English responses |
| **Controlled Substance Warning** | Appends RA 9165 (Dangerous Drugs Act) warnings for controlled medicines |
| **Medical Disclaimer** | Every response ends with an educational disclaimer |
| **Structured JSON Output** | Backend-ready JSON with segmented drug info (name, price, dosage, side effects, etc.) plus human-readable Markdown |

---

## 3. System Architecture

```
User Query
    |
    v
[Preprocess] → normalize PH drug names, clean text
    |
    v
[Guardrails] ──→ Emergency? ──→ YES → Return escalation text
    |               NO
    v
[Classifier] ──→ Intent (8 classes) + OTC/Rx flag
    |
    v
[BM25 Retrieval] ──→ Fetch top-k drug records from local JSONL
    |
    v
[Prompt Builder] ──→ System msg + Retrieved Context + User query
    |
    v
[QLoRA LLM] ──→ TinyLlama-1.1B-Chat (4-bit) + LoRA adapter
    |
    v
[Post-Generation Safety] ──→ Rx note injection, disclaimer, RA 9165 check
    |
    v
Response (Markdown + Structured JSON)
```

**Key Decision:** Standard intents (OTC rec, drug info, side effects, price, interaction, intake, emergency) bypass LLM generation entirely. The LLM is fine-tuned but primarily serves as a fallback for out-of-distribution queries.

---

## 4. Technology Stack

| Layer | Component | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.10+ | Core runtime |
| **Deep Learning** | PyTorch | 2.6.0+cu124 | Tensor computation, GPU acceleration |
| **LLM** | Transformers (Hugging Face) | 4.49+ | TinyLlama loading, tokenization, training |
| **Quantization** | bitsandbytes | 0.45+ | 4-bit NF4 quantization for 6 GB VRAM |
| **Fine-Tuning** | PEFT (LoRA) | 0.14+ | Parameter-efficient fine-tuning |
| **Optimization** | Accelerate | 1.5+ | Mixed-precision training helpers |
| **Classical ML** | scikit-learn | 1.6+ | Intent classifier (ComplementNB), Rx classifier (Logistic Regression) |
| **Embeddings** | Gensim | 4.3+ | Skip-gram Word2Vec on pharma corpus |
| **Retrieval** | rank-bm25 | 0.2+ | BM25 lexical search over drug database |
| **API** | Flask | 3.0+ | REST API wrapper |
| **CORS** | flask-cors | 5.0+ | Cross-origin request support |
| **Data Science** | NumPy, Pandas, Matplotlib, Seaborn | — | Analysis & visualization |
| **Serialization** | joblib | 1.5+ | Model artifact persistence |
| **Datasets** | datasets (Hugging Face) | 3.5+ | Loading pharmacare-dataset corpus for LLM fine-tuning |

For complete technical details (hyperparameters, training procedures, evaluation metrics, NLP concepts), see **[TECHNICAL.md](TECHNICAL.md)**.

---

## 5. Quick Start — Run the API (No Training Needed)

This repository includes all pre-trained artifacts. You can run the API immediately without training.

### Prerequisites

- Python 3.10+
- NVIDIA GPU with CUDA 12.x (RTX 4050 or better recommended; 6 GB VRAM minimum)
- Git

### Step 1: Clone & Enter Directory

```bash
git clone <repo-url>
cd Pharmacare-PH
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start the API Server

```bash
python api.py
```

Default: `http://0.0.0.0:5000`

Environment variables:
- `FLASK_HOST` — bind address (default: `0.0.0.0`)
- `FLASK_PORT` — port (default: `5000`)

On first startup the model warms up (~30–60s). Wait for:
```
[INFO] Model warm-up complete. API ready.
```

### Step 5: Test It

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What can I take for headache?"}'
```

**Sample Response:**
```json
{
  "query": "What can I take for headache?",
  "response": "**Drug Name:** Paracetamol\n**Brand Names:** Biogesic, Tempra\n**Adult Dosage:** 500–1000 mg every 4–6 hours...",
  "structured": {
    "drug_name": "Paracetamol",
    "brand_names": "Biogesic, Tempra",
    "generic_price": "PHP1.50",
    ...
  },
  "intent": "otc_recommendation",
  "rx_flag": false,
  "emergency": false,
  "language": "en",
  "latency_seconds": 1.234
}
```

For full API documentation, see **[API_SETUP.md](API_SETUP.md)**.

---

## 6. Full Pipeline — Train from Scratch

If you want to retrain everything, run the notebook:

```bash
jupyter notebook 01_end_to_end_demo.ipynb
```

Run all cells top-to-bottom. The notebook will produce every artifact automatically.

| Section | What It Does | Time |
|---------|-------------|------|
| 0–2 | Setup, DB load, preprocessing demo | ~2 min |
| 3 | Build pharmacare-dataset corpus (~5,291 examples) | ~2 min |
| 4 | Train classifiers (fast) | ~2 min |
| 5 | Train Word2Vec (fast) | ~2 min |
| 6 | BM25 demo (fast) | ~1 min |
| 7 | **QLoRA fine-tuning** | ~2.0–2.3 hours on RTX 4050 |
| 8 | Metrics (fast) | ~1 min |
| 9 | Inference demo (loads model) | ~1 min |
| 10 | Gradio UI (optional) | — |
| 11–12 | Safety checklist + summary | ~1 min |

---

## 7. API Documentation

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Send a message, get structured response |
| `GET` | `/health` | Check model load status and GPU availability |
| `GET` | `/info` | Return system metadata |

### `POST /chat`

**Request:**
```json
{"message": "What can I take for headache?"}
```

**Response:**
```json
{
  "query": "What can I take for headache?",
  "response": "**Drug Name:** Paracetamol\n**Brand Names:** Biogesic...",
  "structured": {
    "drug_name": "Paracetamol",
    "brand_names": "Biogesic, Tempra",
    "drug_class": "Analgesic / Antipyretic",
    "indications": "mild to moderate pain, fever, headache",
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

The `structured` field is a backend-ready JSON object. The `response` field is a human-readable Markdown string with **bold labels**.

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

Response:
```json
{
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
    "BM25 grounding retrieval"
  ]
}
```

For full setup and troubleshooting, see **[API_SETUP.md](API_SETUP.md)**.

---

## 8. Project Structure

```
Pharmacare-PH/
|
|-- api.py                          # Flask REST API entry point
|-- 01_end_to_end_demo.ipynb        # Main notebook: full pipeline
|-- requirements.txt                # Python dependencies
|-- README.md                       # This file
|-- TECHNICAL.md                    # Deep technical documentation
|-- API_SETUP.md                    # API deployment guide
|
|-- data/                           # All datasets (tracked in Git)
|   |-- ph_drug_database.jsonl      # Master drug reference (140 drugs)
|   |-- pharma_qa_pairs.jsonl       # LLM training corpus (~5,291 examples)
|   |-- classifier_training_data.jsonl  # Parallel classifier labels
|
|-- models/                         # All trained artifacts (tracked in Git)
|   |-- intent_clf.pkl              # ComplementNB intent classifier
|   |-- rx_clf.pkl                  # LogisticRegression Rx classifier
|   |-- tfidf_vectorizer.pkl        # TF-IDF for intent classifier
|   |-- rx_tfidf_vectorizer.pkl     # TF-IDF for Rx classifier
|   |-- label_encoder.pkl           # Intent label encoder
|   |-- pharma_w2v.model            # Domain Word2Vec (skip-gram)
|   |-- pharmacare_lora/             # LoRA adapter + tokenizer
|       |-- adapter_config.json
|       |-- adapter_model.safetensors
|       |-- tokenizer.json
|       |-- tokenizer_config.json
|       |-- checkpoint-719/         # Training checkpoint (epoch 1)
|       |-- checkpoint-1438/        # Training checkpoint (epoch 2)
|       |-- checkpoint-2157/        # Training checkpoint (epoch 3)
|
|-- src/                            # Source modules
|   |-- __init__.py
|   |-- inference.py                # PharmacareInference class
|   |-- build_dataset.py            # Dataset processing pipeline
|   |-- preprocess.py               # Text cleaning + chat template
|   |-- guardrails.py               # Safety layer + classifiers
|   |-- retrieval.py                # BM25 drug retrieval
|   |-- ph_drug_map.py            # Brand-to-generic normalization
|   |-- hf_dataset_probe.py         # HF dataset schema probe (defense)
|   |-- generate_drug_db.py         # Initial drug DB generator
|   |-- append_drugs.py             # Drug DB expansion script
```

---

## 9. Safety & Compliance

- All drug data is approximate (2024 estimates) for **educational use only**
- **Controlled substances** include warnings under **Republic Act 9165** (Comprehensive Dangerous Drugs Act of 2002)
- User query logs must be **anonymized** per **Republic Act 10173** (Data Privacy Act of 2012)
- **Disclaimer**: This information is for general educational purposes only and is **not a substitute for professional medical advice, diagnosis, or treatment**. Always consult a licensed physician or pharmacist before taking any medication.

---

## 10. Future Roadmap

| Feature | Description | Priority |
|---------|-------------|----------|
| **Expand Drug DB** | Increase from 80 to 200+ FDA-PH registered drugs | High |
| **Neural Intent Classifier** | Replace ComplementNB with a fine-tuned BERT-like model | Medium |
| **RAG Hybrid** | Combine BM25 with dense vector retrieval (FAISS) | Medium |
| **Voice Interface** | Add STT/TTS for hands-free pharmacy assistance | Low |
| **Mobile Packaging** | Wrap the API in a lightweight React Native or Flutter app | Low |
| **Continuous Learning** | Log anonymized queries (per RA 10173) and retrain LoRA adapter quarterly | Low |

---

## 11. License

This project is for **educational use only** in the context of **CCS 249 — Natural Language Processing**.

**Developed for:** CCS 249 — Natural Language Processing  
**Target GPU:** NVIDIA RTX 4050 (6 GB VRAM)  
**Base LLM:** TinyLlama/TinyLlama-1.1B-Chat-v1.0 + QLoRA 4-bit

---

For deep technical details, see **[TECHNICAL.md](TECHNICAL.md)**.
