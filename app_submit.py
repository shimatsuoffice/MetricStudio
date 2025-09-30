import os
import secrets
import urllib.parse
from typing import Optional

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(
    dotenv_path=Path(__file__).with_name(".env")
)  # CWDに依存しない .env 読み込み

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import (
    JSONResponse,
    HTMLResponse,
    RedirectResponse,
    PlainTextResponse,
)
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import httpx

APP_NAME = "instagram-review-demo"

# Graph API endpoints
META_OAUTH_AUTHZ = "https://www.facebook.com/v20.0/dialog/oauth"
META_OAUTH_TOKEN = "https://graph.facebook.com/v20.0/oauth/access_token"
GRAPH_BASE = "https://graph.facebook.com/v20.0"

# env
META_APP_ID = os.getenv("META_APP_ID", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")
APP_SECRET = os.getenv("APP_SECRET", secrets.token_urlsafe(32))  # session secret
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
    if o.strip()
]

# scopes（審査は最小3つのみ）
REQUIRED_SCOPES = ["instagram_basic", "instagram_manage_insights", "pages_show_list"]

app = FastAPI(title="Instagram Review Demo", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# セッション（Cookie）
app.add_middleware(
    SessionMiddleware, secret_key=APP_SECRET, same_site="lax", https_only=False
)


# ---------- helpers ----------
async def _http_get(url: str, params: dict):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


def _require_login(request: Request) -> str:
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="not logged in")
    return token


async def _exchange_code_for_token(code: str) -> dict:
    params = {
        "client_id": META_APP_ID,
        "client_secret": META_APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    return await _http_get(META_OAUTH_TOKEN, params)


async def _get_ig_user_id(access_token: str) -> Optional[str]:
    # Facebookページ一覧→そこにぶら下がる instagram_business_account.id を拾う
    params = {"access_token": access_token, "fields": "instagram_business_account"}
    data = await _http_get(f"{GRAPH_BASE}/me/accounts", params)
    for page in data.get("data", []):
        ig = page.get("instagram_business_account")
        if ig and ig.get("id"):
            return ig["id"]
    return None


# ---------- routes ----------
@app.get("/", response_class=JSONResponse)
async def root():
    return {
        "status": "ok",
        "app": APP_NAME,
        "scopes": REQUIRED_SCOPES,
        "links": {
            "login": "/auth/login",
            "status": "/auth/status",
            "profile": "/me/profile",
            "insights": "/me/insights?metric=impressions,reach",
            "logout": "/auth/logout",
            "privacy": "/privacy",
            "data_deletion": "/data-deletion",
        },
    }


@app.get("/auth/login")
async def auth_login(request: Request):
    if not META_APP_ID or not META_APP_SECRET:
        raise HTTPException(500, detail="META_APP_ID / META_APP_SECRET not configured")
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state
    params = {
        "client_id": META_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "response_type": "code",
        "scope": ",".join(REQUIRED_SCOPES),
    }
    return RedirectResponse(f"{META_OAUTH_AUTHZ}?{urllib.parse.urlencode(params)}")


@app.get("/auth/callback")
async def auth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
):
    if error:
        return JSONResponse({"ok": False, "error": error}, status_code=400)
    saved = request.session.get("oauth_state")
    if not saved or state != saved:
        raise HTTPException(400, detail="state mismatch")
    if not code:
        raise HTTPException(400, detail="missing code")
    token_res = await _exchange_code_for_token(code)
    access_token = token_res.get("access_token")
    if not access_token:
        raise HTTPException(400, detail="no access_token in response")
    request.session["access_token"] = access_token
    return RedirectResponse("/auth/status")


@app.get("/auth/status")
async def auth_status(request: Request):
    return {"logged_in": bool(request.session.get("access_token"))}


@app.post("/auth/logout")
async def auth_logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/me/profile")
async def me_profile(request: Request):
    access_token = _require_login(request)
    ig_user_id = await _get_ig_user_id(access_token)
    if not ig_user_id:
        raise HTTPException(
            400, detail="no instagram_business_account linked to this user"
        )
    params = {
        "access_token": access_token,
        "fields": "id,username,followers_count,media_count",
    }
    return await _http_get(f"{GRAPH_BASE}/{ig_user_id}", params)


@app.get("/me/insights")
async def me_insights(request: Request, metric: str):
    access_token = _require_login(request)
    if not metric:
        raise HTTPException(400, detail="metric query parameter is required")
    ig_user_id = await _get_ig_user_id(access_token)
    if not ig_user_id:
        raise HTTPException(
            400, detail="no instagram_business_account linked to this user"
        )
    params = {"access_token": access_token, "metric": metric, "period": "day"}
    return await _http_get(f"{GRAPH_BASE}/{ig_user_id}/insights", params)


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return HTMLResponse(
        "<h1>Privacy Policy</h1>"
        "<p>This application uses Instagram Graph API with minimum scopes to display basic profile and insights data. "
        "No personal data is stored on our servers; data is shown only during your session.</p>"
        "<p>Contact: support@example.com</p>"
    )


@app.get("/data-deletion", response_class=HTMLResponse)
async def data_deletion():
    return HTMLResponse(
        "<h1>Data Deletion Instructions</h1>"
        "<p>We do not persist user data. If you want to request deletion of any server-side logs or residuals, "
        "please email support@example.com with your Meta User ID.</p>"
    )


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return PlainTextResponse("ok")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app_submit:app", host="0.0.0.0", port=8000, reload=True)
