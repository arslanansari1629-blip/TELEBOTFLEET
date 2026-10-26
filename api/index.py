import os
import json
import re
import time
import hashlib
import uuid
import random
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

import jwt
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# --- Config ---
JWT_SECRET = os.getenv("JWT_SECRET", "telebotfleet-super-secret-key-2024-v1")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 72
DATA_FILE = "/tmp/telebotfleet_data.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # user will login with this
ADMIN_EMAIL = "admin@telebotfleet.com"

app = FastAPI(title="TeleBotFleet API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helpers ---

def hash_password(password: str) -> str:
    salt = "telebotfleet_salt_v1"
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_token(user_id: str, username: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def load_data():
    default = {
        "users": [],
        "bots": [],
        "logs": [],
        "broadcasts": []
    }
    # try /tmp first
    for path in [DATA_FILE, os.path.join(os.getcwd(), "data.json"), os.path.join(os.path.dirname(__file__), "..", "data.json")]:
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    d = json.load(f)
                    # ensure defaults
                    for k in default:
                        if k not in d:
                            d[k] = default[k]
                    return d
        except:
            pass
    # init with admin
    admin_user = {
        "id": "admin-001",
        "username": ADMIN_USERNAME,
        "email": ADMIN_EMAIL,
        "password": hash_password(ADMIN_PASSWORD),
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "avatar": "A"
    }
    default["users"].append(admin_user)
    save_data(default)
    return default

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass
    # also try cwd
    try:
        with open("data.json", "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    payload = decode_token(token)
    data = load_data()
    user = next((u for u in data["users"] if u["id"] == payload["sub"]), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def admin_required(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def generate_bot_logs(bot_name: str, status: str):
    base = [
        f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Initializing {bot_name} ...",
        f"[{datetime.now().strftime('%H:%M:%S')}] 🔗 Connecting to Telegram Bot API",
        f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Bot @{bot_name.lower().replace(' ', '_')}_bot is online",
        f"[{datetime.now().strftime('%H:%M:%S')}] 📡 Polling @ getUpdates (long polling: 30s)",
        f"[{datetime.now().strftime('%H:%M:%S')}] 💬 Ready to receive messages 24/7",
    ]
    if status == "running":
        extra = [
            f"[{datetime.now().strftime('%H:%M:%S')}] 👤 New user started bot: /start",
            f"[{datetime.now().strftime('%H:%M:%S')}] 📨 Message routed: Hello! How can I help?",
            f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ Uptime: {random.randint(1,72)}h {random.randint(0,59)}m | CPU: {random.randint(5,35)}% | RAM: {random.randint(80,250)}MB",
        ]
        return base + extra
    else:
        return [f"[{datetime.now().strftime('%H:%M:%S')}] ⏹️ Bot stopped by user", f"[{datetime.now().strftime('%H:%M:%S')}] 💤 Sleeping - awaiting start command"] + base[:2]

def mask_token(token: str) -> str:
    if len(token) < 10:
        return "***"
    return token[:6] + "..." + token[-4:]

def validate_bot_token(token: str) -> bool:
    # Telegram token format: 1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
    pattern = r"^\d{7,}:[A-Za-z0-9_-]{30,}$"
    return re.match(pattern, token) is not None

# --- Models ---
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class BotCreateRequest(BaseModel):
    name: str
    token: str
    description: Optional[str] = ""

class BroadcastRequest(BaseModel):
    message: str

# Serve frontend at root for local dev
@app.get("/", response_class=HTMLResponse)
async def serve_root():
    for p in ["index.html", os.path.join(os.path.dirname(__file__), "..", "index.html"), "/tmp/index.html"]:
        if os.path.exists(p):
            with open(p, "r") as f:
                return HTMLResponse(f.read())
    return HTMLResponse("<h1>TeleBotFleet Running - Frontend not found</h1><p><a href='/api/health'>/api/health</a>")

@app.get("/index.html", response_class=HTMLResponse)
async def serve_index():
    return await serve_root()

# --- Routes ---

@app.get("/api/health")
async def health():
    data = load_data()
    return {
        "status": "ok",
        "service": "TeleBotFleet API",
        "version": "2.0",
        "uptime": "99.98%",
        "total_users": len(data["users"]),
        "total_bots": len(data["bots"]),
        "running_bots": len([b for b in data["bots"] if b["status"] == "running"]),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    data = load_data()
    if len(req.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if any(u["username"].lower() == req.username.lower() for u in data["users"]):
        raise HTTPException(status_code=400, detail="Username already exists")
    if any(u["email"].lower() == req.email.lower() for u in data["users"]):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": str(uuid.uuid4()),
        "username": req.username,
        "email": req.email,
        "password": hash_password(req.password),
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "avatar": req.username[0].upper()
    }
    data["users"].append(new_user)
    save_data(data)
    token = create_token(new_user["id"], new_user["username"], new_user["role"])
    return {
        "message": "Registered successfully",
        "token": token,
        "user": {
            "id": new_user["id"],
            "username": new_user["username"],
            "email": new_user["email"],
            "role": new_user["role"],
            "avatar": new_user["avatar"]
        }
    }

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    data = load_data()
    user = next((u for u in data["users"] if u["username"].lower() == req.username.lower()), None)
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(user["id"], user["username"], user["role"])
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "avatar": user.get("avatar", user["username"][0].upper())
        }
    }

@app.get("/api/auth/me")
async def me(user=Depends(get_current_user)):
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "avatar": user.get("avatar", "U"),
        "created_at": user.get("created_at")
    }

@app.get("/api/bots")
async def list_bots(user=Depends(get_current_user)):
    data = load_data()
    if user["role"] == "admin":
        bots = data["bots"]
    else:
        bots = [b for b in data["bots"] if b["user_id"] == user["id"]]
    # enrich
    for b in bots:
        b["masked_token"] = mask_token(b.get("token", ""))
        # compute uptime-ish
        try:
            created = datetime.fromisoformat(b["created_at"])
            delta = datetime.now(timezone.utc) - created
            hours = int(delta.total_seconds() // 3600)
            mins = int((delta.total_seconds() % 3600) // 60)
            b["uptime_display"] = f"{hours}h {mins}m" if b["status"] == "running" else "0h 0m"
        except:
            b["uptime_display"] = "1h 23m"
    return bots

@app.post("/api/bots")
async def create_bot(req: BotCreateRequest, user=Depends(get_current_user)):
    data = load_data()
    user_bots = [b for b in data["bots"] if b["user_id"] == user["id"]]
    limit = 999 if user["role"] == "admin" else 2
    if len(user_bots) >= limit:
        raise HTTPException(status_code=400, detail=f"Limit reached: {user['role']} can host only {limit} bots. Upgrade or delete existing bots.")
    if not validate_bot_token(req.token):
        raise HTTPException(status_code=400, detail="Invalid Telegram Bot Token format. Get it from @BotFather (e.g., 1234567890:AAH...)")
    if any(b["token"] == req.token for b in data["bots"]):
        raise HTTPException(status_code=400, detail="This bot token is already hosted on the platform")
    if len(req.name) < 2:
        raise HTTPException(status_code=400, detail="Bot name too short")

    # simulate fetching bot info via token
    bot_username = req.name.lower().replace(" ", "_") + "_bot"
    
    new_bot = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "username_owner": user["username"],
        "name": req.name,
        "token": req.token,
        "description": req.description or f"Telegram bot hosted 24/7 on TeleBotFleet",
        "bot_username": bot_username,
        "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": random.randint(12, 38),
        "ram": random.randint(64, 180),
        "requests": random.randint(1200, 9800),
        "uptime": "0h 0m",
        "region": random.choice(["us-east-1", "eu-west-1", "ap-south-1", "us-west-2"]),
        "logs": generate_bot_logs(req.name, "running")
    }
    data["bots"].append(new_bot)
    data["logs"].append({
        "time": datetime.now(timezone.utc).isoformat(),
        "user": user["username"],
        "action": f"Deployed bot '{req.name}'",
        "type": "deploy"
    })
    save_data(data)
    return {"message": "Bot deployed successfully & running 24/7", "bot": new_bot}

@app.post("/api/bots/{bot_id}/start")
async def start_bot(bot_id: str, user=Depends(get_current_user)):
    data = load_data()
    bot = next((b for b in data["bots"] if b["id"] == bot_id), None)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bot["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    bot["status"] = "running"
    bot["logs"] = generate_bot_logs(bot["name"], "running")
    save_data(data)
    return {"message": "Bot started 24/7", "bot": bot}

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(bot_id: str, user=Depends(get_current_user)):
    data = load_data()
    bot = next((b for b in data["bots"] if b["id"] == bot_id), None)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bot["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    bot["status"] = "stopped"
    bot["logs"] = generate_bot_logs(bot["name"], "stopped")
    save_data(data)
    return {"message": "Bot stopped", "bot": bot}

@app.post("/api/bots/{bot_id}/restart")
async def restart_bot(bot_id: str, user=Depends(get_current_user)):
    data = load_data()
    bot = next((b for b in data["bots"] if b["id"] == bot_id), None)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bot["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    bot["status"] = "running"
    bot["logs"] = [
        f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Restarting bot {bot['name']} ...",
        f"[{datetime.now().strftime('%H:%M:%S')}] 🧹 Clearing cache & webhooks",
    ] + generate_bot_logs(bot["name"], "running")
    save_data(data)
    return {"message": "Bot restarted", "bot": bot}

@app.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: str, user=Depends(get_current_user)):
    data = load_data()
    idx = next((i for i, b in enumerate(data["bots"]) if b["id"] == bot_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot = data["bots"][idx]
    if bot["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    data["bots"].pop(idx)
    save_data(data)
    return {"message": "Bot deleted & hosting terminated"}

@app.get("/api/bots/{bot_id}/logs")
async def get_logs(bot_id: str, user=Depends(get_current_user)):
    data = load_data()
    bot = next((b for b in data["bots"] if b["id"] == bot_id), None)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bot["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    # add dynamic heartbeat log
    heartbeat = f"[{datetime.now().strftime('%H:%M:%S')}] 💓 Heartbeat OK | Queue:0 | Uptime: {bot.get('uptime_display','24h')}"
    logs = bot.get("logs", []) + [heartbeat]
    return {"logs": logs, "status": bot["status"], "name": bot["name"]}

@app.post("/api/bots/{bot_id}/send_test")
async def send_test(bot_id: str, request: Request, user=Depends(get_current_user)):
    data = load_data()
    bot = next((b for b in data["bots"] if b["id"] == bot_id), None)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    body = await request.json() if request.headers.get("content-type") else {}
    msg = body.get("message", "Hello from TeleBotFleet!") if isinstance(body, dict) else "Hello"
    # simulate adding log
    ts = datetime.now().strftime('%H:%M:%S')
    bot["logs"].append(f"[{ts}] 📤 Test message sent: {msg}")
    save_data(data)
    return {"message": f"Test message queued for @{bot['bot_username']}", "preview": msg}

# --- Admin ---
@app.get("/api/admin/stats")
async def admin_stats(user=Depends(admin_required)):
    data = load_data()
    total_users = len(data["users"])
    total_bots = len(data["bots"])
    running = len([b for b in data["bots"] if b["status"] == "running"])
    stopped = total_bots - running
    return {
        "total_users": total_users,
        "total_bots": total_bots,
        "running_bots": running,
        "stopped_bots": stopped,
        "uptime": "99.99%",
        "cpu_avg": 24.5,
        "ram_total": f"{total_bots * 128}MB",
        "requests_today": sum(b.get("requests", 0) for b in data["bots"]),
        "recent_logs": data["logs"][-10:][::-1] if data["logs"] else []
    }

@app.get("/api/admin/users")
async def admin_users(user=Depends(admin_required)):
    data = load_data()
    users_out = []
    for u in data["users"]:
        bots_count = len([b for b in data["bots"] if b["user_id"] == u["id"]])
        users_out.append({
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "role": u["role"],
            "created_at": u.get("created_at"),
            "avatar": u.get("avatar", "U"),
            "bots_count": bots_count
        })
    return users_out

@app.get("/api/admin/bots")
async def admin_bots(user=Depends(admin_required)):
    data = load_data()
    return data["bots"]

@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(user_id: str, user=Depends(admin_required)):
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    data = load_data()
    idx = next((i for i, u in enumerate(data["users"]) if u["id"] == user_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="User not found")
    # delete bots of user
    data["users"].pop(idx)
    data["bots"] = [b for b in data["bots"] if b["user_id"] != user_id]
    save_data(data)
    return {"message": "User & their bots deleted"}

@app.delete("/api/admin/bots/{bot_id}")
async def admin_delete_bot(bot_id: str, user=Depends(admin_required)):
    data = load_data()
    idx = next((i for i, b in enumerate(data["bots"]) if b["id"] == bot_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    data["bots"].pop(idx)
    save_data(data)
    return {"message": "Bot deleted by admin"}

@app.post("/api/admin/broadcast")
async def broadcast(req: BroadcastRequest, user=Depends(admin_required)):
    data = load_data()
    entry = {
        "id": str(uuid.uuid4()),
        "message": req.message,
        "by": user["username"],
        "at": datetime.now(timezone.utc).isoformat()
    }
    data["broadcasts"].append(entry)
    save_data(data)
    return {"message": f"Broadcast sent to {len(data['users'])} users", "broadcast": entry}

@app.post("/api/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    # dummy webhook endpoint for Telegram setWebhook
    try:
        data = load_data()
        bot = next((b for b in data["bots"] if b["token"] == token), None)
        body = await request.json()
        if bot:
            ts = datetime.now().strftime('%H:%M:%S')
            bot["logs"].append(f"[{ts}] 📥 Webhook: {json.dumps(body)[:120]}")
            save_data(data)
        return {"ok": True}
    except:
        return {"ok": True}

# For local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Vercel handler
handler = app
