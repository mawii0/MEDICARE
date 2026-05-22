# MEDIBoT - Integration Progress
**Last updated: 2026-05-22**

---

## Completed Work

### 1. Navbar Redesign (DONE)
- Rewrote `NavBar.tsx` into 3 components:
  - `Sidebar` — Desktop sidebar (w-64, collapsible to icon-only)
  - `MobileTopBar` — Mobile top bar with logo + dark mode + logout
  - `BottomNav` — Mobile bottom tab bar (4 tabs, 44px touch targets)
- Updated `App.tsx` with new flex layout (sidebar + main content column)
- Sidebar is collapsible with `PanelLeftClose`/`PanelLeftOpen` toggle
- Pure Tailwind CSS, lucide-react icons, dark mode support
- Logout button in Sidebar (shows user email) and MobileTopBar

### 2. Backend Server Setup (DONE)
- Express.js + TypeScript server
- Dependencies: express, better-sqlite3, jsonwebtoken, bcryptjs, cors, tsx, undici
- SQLite database (`mediguide.db`) with tables: users, history_entries, saved_meds
- JWT auth middleware (7-day token expiry)
- Vite proxy configured (`/api` → `localhost:3001`)

### 3. Auth Routes (DONE & TESTED)
- `POST /api/auth/register` — returns token + user
- `POST /api/auth/login` — returns token + user
- Password hashing with bcryptjs

### 4. Chat Endpoint (DONE — integrated with Pharmacare Flask API)
- Frontend calls `http://localhost:5000/chat` directly (Flask NLP service)
- Express `/api/chat` placeholder still exists but is bypassed
- Response transformed from Pharmacare structured JSON to MedicineCard format
- Supports bilingual responses (English/Taglish)
- Handles emergency detection with 911/DOH escalation
- Rx flag for prescription drugs with mandatory warnings
- Brand names, prices (PHP), availability at PH pharmacies
- Intent classification (otc_recommendation, rx_info_restricted, etc.)

### 5. History & Saved Meds Routes (DONE & TESTED)
- `GET/POST/DELETE /api/history` — JWT-protected, per-user
- `GET/POST/DELETE /api/saved-meds` — JWT-protected, per-user

### 6. Frontend Integration (DONE)
- `src/lib/api.ts` — fetch wrapper with auth token + Pharmacare transformer
- `src/lib/auth.tsx` — AuthProvider + useAuth hook, localStorage persistence
- `src/app/components/LoginScreen.tsx` — login/register form with validation
- `App.tsx` — AuthProvider wraps app, LoginScreen shown if not authenticated
- `ChatScreen.tsx` — calls Flask NLP API, displays rich medicine cards with brand names, prices, availability
- `PharmacyScreen.tsx` — fetches from `/api/pharmacy/nearby` with geolocation, real Leaflet map
- `HistoryScreen.tsx` — fetches from `/api/history` and `/api/saved-meds`
- `OnboardingScreen.tsx` — updated with Pharmacare branding, NLP pipeline info, safety features

### 7. Pharmacy Endpoint (DONE & TESTED)
- `GET /api/pharmacy/nearby` — queries Nominatim OpenStreetMap API
- Uses `undici.fetch` + `child_process` fallback for network isolation issue
- Calculates distances with haversine formula, returns sorted results

### 8. Interactive Map (DONE)
- Real Leaflet map with OpenStreetMap tiles (no API key needed)
- User location marker + pharmacy markers with popups
- Auto-fits bounds to show all results
- Installed: `leaflet` (plain, no react-leaflet wrapper — avoids React 18/19 peer dep conflict)

### 9. Pharmacare NLP Model Integration (DONE)
- Flask API at `model/api.py` serves fine-tuned TinyLlama-1.1B + LoRA
- NLP pipeline: text preprocessing → TF-IDF classifiers → BM25 retrieval → QLoRA LLM
- Structured output: drug_name, brand_names, drug_class, indications, dosage, side effects, prices
- Safety guardrails: emergency bypass, Rx restriction, RA 9165 controlled substance, disclaimer
- `src/lib/api.ts` transforms Flask response to MedicineCard format
- `ChatScreen.tsx` renders rich medicine cards with price/availability/Rx warnings
- `OnboardingScreen.tsx` updated to reflect Pharmacare capabilities

### 10. End-to-End Testing (DONE)
- Full flow verified via curl: register → login → chat → history → saved-meds → pharmacy
- All endpoints return correct data

---

## How to Run

```bash
# Terminal 1 — NLP service (Flask)
cd model
python api.py              # http://localhost:5000

# Terminal 2 — Express API server (auth, db, pharmacy)
npm run server             # http://localhost:3001

# Terminal 3 — Vite dev server
npm run dev                # http://localhost:5173
```

The Flask NLP service runs on port 5000, Express on 3001, Vite on 5173.
Frontend chat calls Flask directly; auth/db/pharmacy go through Express.

**Note:** After modifying server code, fully restart the server to clear tsx cache.

---

## File Structure
```
model/                    # Pharmacare NLP service (Python/Flask)
  api.py                  # Flask REST API entry point
  src/
    inference.py          # PharmacareInference class
    guardrails.py         # Safety layer + classifiers
    retrieval.py          # BM25 drug retrieval
    preprocess.py         # Text cleaning
  data/                   # Training data + drug database
  models/                 # Trained artifacts (LoRA, classifiers, W2V)

server/                   # Express backend (auth, db, pharmacy)
  index.ts                # Express entry point
  db.ts                   # SQLite setup + schema
  routes/
    auth.ts               # Register + login
    chat.ts               # Legacy placeholder (bypassed)
    pharmacy.ts           # Nominatim/Overpass pharmacy lookup
    history.ts            # History CRUD (protected)
    saved-meds.ts         # Saved meds CRUD (protected)
  middleware/
    auth.ts               # JWT verification

src/lib/
  api.ts                  # Frontend fetch wrapper + Pharmacare transformer
  auth.tsx                # Auth context + hook

src/app/components/
  LoginScreen.tsx         # Login/register form
  NavBar.tsx              # Sidebar + BottomNav + MobileTopBar
  ChatScreen.tsx          # Chat with Pharmacare integration
  PharmacyScreen.tsx      # Real Leaflet map + pharmacy data
  HistoryScreen.tsx       # History + saved meds from API
  OnboardingScreen.tsx    # Home screen with Pharmacare branding
```

---

## Remaining / Nice-to-Have

1. **Error handling polish** — better error messages in UI for network failures
2. **Stale token handling** — auto-logout when JWT expires
3. **HistoryScreen fake exports** — "Export to PDF" and Settings tab are non-functional
4. **PharmacyScreen dead code** — `CenterOnMe` component defined but never rendered
