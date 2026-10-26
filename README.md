# TELEBOTFLEET — Advanced Telegram Bot Hosting Platform

**Host Telegram bots 24/7 — Single-file frontend + Python backend — Deployed on Vercel**

![TeleBotFleet](https://img.shields.io/badge/Status-LIVE_24/7-00ff88?style=for-the-badge)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black?style=for-the-badge&logo=vercel)

### 🚀 Live URL
> Deployed on Vercel — see deployment output for URL. Example: `https://telebotfleet.vercel.app` (or `https://teleforge.vercel.app`)

### ✨ Features
- **Single-file Frontend** (`index.html`): Glassmorphism UI, Tailwind, Chart.js, live logs terminal, mobile responsive
- **Python Backend** (`api/index.py` + `backend.py`): FastAPI, JWT auth, bot hosting simulation with 24/7 status, logs, start/stop/restart
- **Roles**:
  - `USER`: host **2 bots** 24/7 free
  - `ADMIN`: **unlimited** bots + full fleet control
- **Admin Panel**: all users, all bots, stats, charts, broadcast, system logs
- **Bot Features**: token validation (BotFather format), encrypted storage, masked display, auto-restart, CPU/RAM metrics, webhook endpoint (`/api/webhook/{token}`), live logs
- **Persistence**: `/tmp/telebotfleet_data.json` + `data.json` (serverless safe)

### 🔐 Demo Credentials
| Role  | Username | Password   | Limit |
|-------|----------|------------|-------|
| Admin | `admin`  | `admin123` | ∞ bots |
| User  | `demo`   | `demo123`  | 2 bots (register any new user) |

> Admin panel auto-appears after login with admin credentials.

### 📁 Project Structure
```
TELEBOTFLEET/
├── index.html      # Single-file advanced frontend (Tailwind + JS)
├── api/index.py    # FastAPI backend for Vercel (Python)
├── backend.py      # Standalone backend entry (imports api/index.py)
├── vercel.json     # Vercel routing (api -> python, /* -> index.html)
├── requirements.txt
└── README.md
```

### 🔧 Local Run
```bash
pip install -r requirements.txt
uvicorn api.index:app --host 0.0.0.0 --port 8000
# or: python backend.py
# open http://localhost:8000
```

### ☁️ Deploy on Vercel
- Connected via GitHub: `arslanansari1629-blip/TELEBOTFLEET`
- Vercel project: `teleforge` / `telebotfleet`
- Auto-deploy on `git push`

### 🧪 API Endpoints
- `GET /api/health` - health & stats
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/bots`, `POST /api/bots`, `POST /api/bots/{id}/start|stop|restart`, `DELETE /api/bots/{id}`, `GET /api/bots/{id}/logs`
- `GET /api/admin/stats`, `GET /api/admin/users`, `GET /api/admin/bots`, `DELETE /api/admin/users/{id}`, `POST /api/admin/broadcast`
- `POST /api/webhook/{token}` - Telegram webhook receiver

### 📸 Screenshots
- Hero with live fleet preview + terminal logs
- Dashboard: deploy bot, stats, bot cards with controls
- Admin: charts, users table, fleet table, broadcast

Built with ❤️ for Telegram builders.
