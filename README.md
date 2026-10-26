# TELEBOTFLEET — Advanced Telegram Bot Hosting Platform

**Host Telegram bots 24/7 — Single-file frontend + Python backend — Deployed on Vercel**

![TeleBotFleet](https://img.shields.io/badge/Status-LIVE_24/7-00ff88?style=for-the-badge)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black?style=for-the-badge&logo=vercel)
![Python](https://img.shields.io/badge/Backend-FastAPI_/_Python-3776AB?style=for-the-badge&logo=python)

### 🚀 Live URLs
- **Vercel (Production):** `https://teleforge-arslanansari1629-blips-projects.vercel.app` *(if shows Vercel login → see Fix below)*
- **Vercel Direct Deployment:** `https://teleforge-55gh3bfbb-arslanansari1629-blips-projects.vercel.app`
- **GitHub:** `https://github.com/arslanansari1629-blip/TELEBOTFLEET`

> ⚠️ **Vercel Authentication Fix (one-click):** If Vercel URL asks for login, go to **Vercel Dashboard → Project teleforge → Settings → Deployment Protection → Vercel Authentication → DISABLE** → Redeploy. Then URL works public.

### ✨ Features
- **Single-file Frontend** (`index.html` 66KB): Glassmorphism dark UI, Tailwind CDN, Chart.js, live terminal logs, mobile responsive
- **Python Backend** (`api/index.py`): FastAPI, JWT auth, 24/7 hosting simulation, bot lifecycle
- **Roles:**
  - `USER` → host **2 bots 24/7** free
  - `ADMIN` → **unlimited** bots + Fleet Control
- **Admin Panel:** Global stats, users table, fleet table, broadcast, system logs, charts
- **Bot Features:** BotFather token validation (`123456:AAH...`), AES masked storage, auto-restart, CPU/RAM metrics, webhook `POST /api/webhook/{token}`, live logs `GET /api/bots/{id}/logs`
- **Persistence:** `/tmp/telebotfleet_data.json` + `data.json` (serverless-safe)

### 🔐 Demo Credentials
| Role  | Username | Password   | Limit |
|-------|----------|------------|-------|
| Admin | `admin`  | `admin123` | ∞ bots |
| User  | `demo`   | `demo123`  | 2 bots |
| Any   | register | —          | 2 bots |

Admin panel auto-appears after admin login. User limit enforced in `POST /api/bots` (2) vs admin 999.

### 📁 Project Structure (Single-File Frontend + Single Python Backend)
```
TELEBOTFLEET/
├── index.html      # Single-file advanced frontend (Tailwind + JS)
├── api/index.py    # FastAPI backend for Vercel serverless (Python)
├── backend.py      # Standalone local entry (imports api/index.py)
├── vercel.json     # Vercel rewrites: /api/* → python, /* → index.html
├── requirements.txt # fastapi, uvicorn, PyJWT, python-jose, httpx
└── README.md
```

### 🔧 Local Run
```bash
pip install -r requirements.txt
uvicorn api.index:app --host 0.0.0.0 --port 8000
# open http://localhost:8000  (frontend + API same origin)
# Test: curl http://localhost:8000/api/health
```

### ☁️ Vercel Deploy
- GitHub: `arslanansari1629-blip/TELEBOTFLEET` → auto-deploy via `git push`
- Vercel projects: `teleforge` (prod), `telebotfleet-advanced`
- Build: `functions: api/index.py (python3.12)` + `rewrites`

### 🧪 API Endpoints
- `GET /api/health`
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/bots`, `POST /api/bots`, `POST /api/bots/{id}/start|stop|restart`, `DELETE /api/bots/{id}`, `GET /api/bots/{id}/logs`, `POST /api/bots/{id}/send_test`
- `GET /api/admin/stats`, `GET /api/admin/users`, `GET /api/admin/bots`, `DELETE /api/admin/users/{id}`, `POST /api/admin/broadcast`
- `POST /api/webhook/{token}`

### 📸 UI Preview
- Hero with live fleet + terminal
- Dashboard: deploy bot in 8s, stats, bot cards with controls
- Admin: charts, users, fleet, broadcast

Built for Telegram builders — Lucknow, IN.
