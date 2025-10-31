# ==== ここを main.py に追加（/health の定義の下あたり） ====
from urllib.parse import urlencode
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import os

# --- 環境変数 ---
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
REDIRECT_URI = (
    os.getenv("OAUTH_REDIRECT_URI")
    or os.getenv("REDIRECT_URI")
    or "https://metricstudio.onrender.com/auth/callback"
)
SCOPES = os.getenv("OAUTH_SCOPES", "")  # まずは空 or "public_profile,email"

FB_AUTH_BASE = "https://www.facebook.com/v20.0/dialog/oauth"
FB_TOKEN_ENDPOINT = "https://graph.facebook.com/v20.0/oauth/access_token"

def _require_env():
    miss = []
    if not APP_ID: miss.append("META_APP_ID")
    if not APP_SECRET: miss.append("META_APP_SECRET")
    if not REDIRECT_URI: miss.append("OAUTH_REDIRECT_URI/REDIRECT_URI")
    if miss:
        raise HTTPException(500, f"Missing env: {', '.join(miss)}")

# --- OAuth開始 (/auth/login) ---
@app.get("/auth/login")
def auth_login():
    _require_env()
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
    }
    if SCOPES:
        params["scope"] = SCOPES
    return RedirectResponse(f"{FB_AUTH_BASE}?{urlencode(params)}")

# --- OAuthコールバック (/auth/callback) ---
@app.get("/auth/callback")
async def auth_callback(request: Request, code: str | None = None, error: str | None = None):
    _require_env()
    if error:
        raise HTTPException(400, f"OAuth error: {error}")
    if not code:
        raise HTTPException(400, "Missing code")

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(FB_TOKEN_ENDPOINT, params={
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        })
    if r.status_code != 200:
        raise HTTPException(400, f"Token exchange failed: {r.text}")

    token_json = r.json()
    token = token_json.get("access_token", "")

    # デバッグ用：検証が終わったら access_token は外してください
    return JSONResponse({
        "status": "ok",
        "message": "OAuth success",
        "access_token": token,
        "access_token_preview": (token or "")[:12] + "...",
        "token_type": token_json.get("token_type"),
        "expires_in": token_json.get("expires_in"),
        "scopes_requested": SCOPES.split(",") if SCOPES else [""]
    })

# --- ルート一覧（確認用） ---
@app.get("/__routes", include_in_schema=False)
def list_routes():
    return [getattr(r, "path", str(r)) for r in app.router.routes]
# ==== ここまで ====
