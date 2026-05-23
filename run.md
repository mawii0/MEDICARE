# Run the system

This file contains quick commands to start the three dev services (frontend Vite, Node API, Flask model) and to verify they are running.

Notes
- Prefer Python 3.12 (tested). If you have multiple Python installations use `py -3.12` to create the venv.
- The Flask model expects to be started from the `model/` directory so its relative `data/` files load correctly.

1) Install dependencies (one-time)

PowerShell
```powershell
# Node deps
npm install

# Create Python venv (from repo root)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r model/requirements.txt
```

Bash (WSL / macOS / Linux)
```bash
# Node deps
npm install

# Create Python venv (from repo root)
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r model/requirements.txt
```

2) Start services (three separate terminals)

PowerShell (recommended for Windows)
```powershell
# Terminal 1: frontend (Vite)
npm run dev

# Terminal 2: Node API
npm run server

# Terminal 3: model server — start from repo root so we can reference venv
cd model
..\.venv\Scripts\python.exe -u api.py
# OR if you already activated venv from repo root:
# cd model; python -u api.py
```

Bash
```bash
# Terminal 1: frontend (Vite)
npm run dev

# Terminal 2: Node API
npm run server

# Terminal 3: model server
cd model
../.venv/bin/python -u api.py
# OR if venv is activated: cd model; python -u api.py
```

3) Quick health checks

PowerShell
```powershell
Invoke-WebRequest -Uri http://localhost:5173 -UseBasicParsing -TimeoutSec 5
Invoke-WebRequest -Uri http://localhost:3001 -UseBasicParsing -TimeoutSec 5
Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing -TimeoutSec 5
```

curl (bash)
```bash
curl -I http://localhost:5173/
curl -I http://localhost:3001/
curl http://localhost:5000/health
```

If Vite is unreachable on `localhost` try IPv6 loopback:
```
http://[::1]:5173/
```

4) Quick /chat test (POST)

PowerShell
```powershell
$body = @{ message = 'Is ibuprofen prescription or OTC?' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:5000/chat' -Body $body -ContentType 'application/json'
```

curl
```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"message":"Is ibuprofen prescription or OTC?"}'
```

5) Troubleshooting
- If `/health` reports missing files (e.g. `data/ph_drug_database.jsonl`) restart the model from the `model/` directory so relative paths resolve.
- If the UI shows stale behavior after backend fixes, hard-refresh the browser (Ctrl+Shift+R) or disable cache and reload.
- If you changed Python version or recreated the venv, re-run `pip install -r model/requirements.txt`.

That's it — open three terminals, run the three start commands, then use the health checks above to confirm services are up.