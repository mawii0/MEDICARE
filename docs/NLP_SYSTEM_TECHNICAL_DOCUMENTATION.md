# NLP System — Technical Documentation Template

Use this document to describe the technical aspects of your developed NLP system. Fill each section with project-specific details, versions, and evidence (logs, screenshots, file paths).

---

## I. Overview and Introduction

### 1. App Name

- [Provide the application name]

### 2. Purpose

- [Short description of the app's purpose and target users]
- Example: "Assist users with medication information and basic symptom triage for the Philippines."

### 3. Technology Stack

- Backend framework: Flask (Python) — version: [e.g. 2.x]
- Frontend framework: Vite + React — version: [e.g. React 18.x, Vite x.x]
- Runtime / Server: Node (for API proxy) — version: [e.g. 18.x]
- Model libraries: Transformers, PEFT, BitsAndBytes, PyTorch — versions: [list exact versions used]
- Storage / DB: better-sqlite3 / files / other — versions: [list]
- Other important packages: list (e.g., scikit-learn, rank_bm25, nltk, sentencepiece)

> NOTE: For each package above, include the exact version used and where it appears in the repository (package.json, requirements.txt, pyproject.toml).

---

## II. Functional Requirements

### 1. Core Features (with descriptions)

- Chat / Symptom Q&A
  - Description: Accept a symptom query, consult local drug DB and model, return a structured answer + human-readable summary.
  - Entry points: Frontend Chat UI -> `src/lib/api.ts` -> Flask NLP server `/chat` (model server) or Node `/api/chat` (placeholder).

- Retrieval / Grounding
  - Description: BM25-based retrieval from `data/ph_drug_database.jsonl` used to ground model answers.
  - Files: `model/src/retrieval.py`, data: `model/data/ph_drug_database.jsonl`.

- Safety / Guardrails
  - Description: Classifiers and rule-based checks to detect emergencies, Rx-only flags, or controlled substances; fallback messages.
  - Files: `model/src/guardrails.py`, classifier interfaces in `model/src`.

- History & Saved Medications
  - Description: Store user history and saved meds in local DB and expose via Node API endpoints.
  - Files: `server/routes/history.ts`, `server/routes/saved-meds.ts`, DB schema: `server/db.ts`.

- Pharmacy Lookup
  - Description: Geolocation-based nearby pharmacy search using OSM/Overpass and Nominatim (server route: `/api/pharmacy`).
  - Files: `server/routes/pharmacy.ts`.

### 2. Libraries / Packages

- Frontend (from `package.json`): list major libs and versions (React, Vite, Tailwind, MUI, Radix, etc.)
- Backend (server): Express, better-sqlite3, cors, tsx (versions in package.json)
- Model & Python (from `model/requirements.txt` or `model/src/*`): PyTorch, Transformers, PEFT, bitsandbytes, rank_bm25, nltk, scikit-learn, flask, flask-cors

> Action item: Paste the exact contents of `package.json` and `model/requirements.txt` here or link to them for reviewers.

---

## III. Model Development & Training (brief)

- Base model used: [e.g. TinyLlama/TinyLlama-1.1B-Chat-v1.0]
- Adapter / Fine-tune: LoRA adapter path: `model/models/pharmacare_lora`
- Training data: Describe dataset source(s), count of examples, train/val split
- Training hyperparameters: epochs, batch size, learning rate, optimizer
- Evaluation metrics: list metric names (accuracy, F1, BLEU, ROUGE, human eval) and results (put tables or plots)
- Reproducibility: commands to re-run training and evaluation (shell snippets)

Example run commands:

```bash
# Activate model venv
cd model
source .venv/bin/activate
python train.py --data data/my_training.jsonl --output models/pharmacare_lora --epochs 3
```

---

## IV. Inference & Integration

- Flask model server: `model/api.py` exposes `/chat`, `/health`, `/info`.
- Inference wrapper: `model/src/inference.py` — loads tokenizer, base model, adapter (LoRA), retrieval engine, and classifiers.
- Frontend integration: `src/lib/api.ts` posts to `http://localhost:5000/chat` and transforms response into the UI shape.
- Fallbacks: Node `server/routes/chat.ts` contains placeholder responses for offline demos.

---

## V. Functional & Non-functional Verification Checklist

- [ ] Backend Flask `/chat` returns `response` and `structured` fields when given a valid message
- [ ] Frontend `api.chat.send()` uses `http://localhost:5000/chat` and displays returned `medicine` cards
- [ ] Retrieval returns at least 1 matched record for known drug queries
- [ ] Classifier flags (`emergency`, `rx_flag`) correctly influence output (test cases)
- [ ] System behaves reasonably when model server is down (fallback or error shown)

Include sample test queries and expected structured output.

---

## VI. Future Enhancements and Roadmap

- Add unit/integration tests for model I/O and backend routes
- CI pipeline to train, evaluate, and publish model artifacts
- Replace placeholder Node `server/routes/chat.ts` with a proxy to Flask or remove it
- Add clear admin/debug endpoint showing preprocessing -> retrieval -> model prompt -> model output

### Known Limitations

- Dependency on local model server availability (Flask). If Flask is down the frontend chat fails.
- Some responses currently use deterministic structured answers instead of pure model output for safety.
- Large binary model files are stored in repo; consider using LFS or external artifact storage.

---

## VII. Appendices

- List of important file paths
  - `model/api.py`, `model/src/inference.py`, `model/src/preprocess.py`, `model/src/retrieval.py`
  - `server/index.ts`, `server/routes/*.ts`
  - `src/lib/api.ts`, `src/app/components/ChatScreen.tsx`
- Recommended reviewer steps: boot Flask model server, start Node server, start Vite frontend, run sample prompts, and compare structured outputs to expected.


---

Generated by: Documentation template for project review

Fill in the placeholders and attach training logs/screenshots where possible to strengthen the submission.
