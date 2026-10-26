# TELEBOTFLEET — Advanced Telegram Bot Hosting Platform

**Host Telegram bots 24/7 — Single-file frontend + Python backend — Deployed on Vercel**

![TeleBotFleet](https://img.shields.io/badge/Status-LIVE_24/7-00ff88?style=for-the-badge)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black?style=for-the-badge&logo=vercel)
![Python](https://img.shields.io/badge/Backend-FastAPI_/_Python-3776AB?style=for-the-badge&logo=python)

### 🚀 Live URLs
- **Arena Preview (LIVE NOW, no auth):** `https://8000-iaz9og8t5wjk8wbsjrr2c.e2b.app` — frontend + API same origin
- **Vercel Production (needs redeploy fix):** `https://teleforge-arslanansari1629-blips-projects.vercel.app` + `https://teleforge-rust.vercel.app` + preview `https://teleforge-k11r2ibr5-arslanansari1629-blips-projects.vercel.app`
- **GitHub:** `https://github.com/arslanansari1629-blip/TELEBOTFLEET` (main at a5efda7)

> ⚠️ **Fix for https://vercel.com/arslanansari1629-blips-projects/telebotfleet-advanced/settings/general (your link):**
> 1. **Framework Preset:** Settings → General → Framework Preset → `Other` (or `null` — not `Next.js`)
> 2. **Deployment Protection:** Settings → Deployment Protection → Vercel Authentication → **DISABLE** (otherwise `*.vercel.app` shows login wall → 404)
> 3. **Git Deployments:** Settings → Git → Deployments → **ENABLE Create Deployments** + disable `disableRepositoryDispatchEvents`
> 4. **Redeploy:** Deployments → ⋯ → Redeploy (or `git push` to main triggers new build). Latest vercel.json at `a5efda7` fixes 404: adds `@vercel/static` build.

> Current teleforge project has framework `nextjs` + disabled git deployments, so `git push` does not auto-deploy and old vercel.json missed static build → 404. Use steps above or manually Redeploy in dashboard. Arena preview is fully working.

### ✨ Features
- **Single-file Frontend** (`index.html` 66KB): Glassmorphism dark UI, Tailwind CDN, Chart.js, live terminal logs, mobile responsive
- **Python Backend** (`api/index.py`): FastAPI, JWT auth, 24/7 hosting simulation, bot lifecycle
- **Roles:**
  - `USER` → host **2 bots 24/7** free (enforced in POST /api/bots)
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

### 📁 Project Structure
```
TELEBOTFLEET/
├── index.html      # Single-file advanced frontend (Tailwind + JS)
├── api/index.py    # FastAPI backend for Vercel serverless (Python)
├── backend.py      # Standalone local entry (imports api/index.py)
├── vercel.json     # builds: @vercel/python + @vercel/static, routes
├── requirements.txt
└── README.md
```

### 🔧 Local Run
```bash
pip install -r requirements.txt
uvicorn api.index:app --host 0.0.0.0 --port 8000
# open http://localhost:8000
curl http://localhost:8000/api/health
```

### ☁️ Vercel Deploy Fix Applied
- `vercel.json` at `a5efda7`: `builds: [{src: api/index.py, use: @vercel/python}, {src: index.html, use: @vercel/static}]` + `routes: /api/* → api/index.py, /* → index.html` — fixes previous 404 (missing static build) and `invalid_function_runtime` (functions vs nextjs framework)
- GitHub main `a5efda7` ready to deploy. Vercel teleforge latest preview `dpl_Cbkgn6ZKFQxNjCW99pfqrvkNSZYG` at `b604656` READY (before static fix), next deploy at `a5efda7` will be live.

### 🧪 API Endpoints
- `GET /api/health`
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/bots`, `POST /api/bots`, `POST /api/bots/{id}/start|stop|restart`, `DELETE /api/bots/{id}`, `GET /api/bots/{id}/logs`, `POST /api/bots/{id}/send_test`
- `GET /api/admin/stats`, `GET /api/admin/users`, `GET /api/admin/bots`, `DELETE /api/admin/users/{id}`, `POST /api/admin/broadcast`
- `POST /api/webhook/{token}`

Built for Telegram builders — Lucknow, IN.
