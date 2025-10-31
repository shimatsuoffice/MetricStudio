# ---------- main.py 完全版 ----------
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse, RedirectResponse
import os
import httpx
from urllib.parse import urlencode

# --- FastAPI本体 ---
app = FastAPI()

# --- Healthチェック（Render監視用） ---
@app.api_route("/health", methods=["GET", "HEAD", "OPTIONS"], include_in_schema=False)
def health_all():
    return PlainTextResponse("ok", media_type="text/plain")

@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root_all():
    return PlainTextResponse("ok", media_type="text/plain")

# --- 環境変数 ---
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
REDIRECT_URI = (
    os.getenv("OAUTH_REDIRECT_URI")
    or os.getenv("REDIRECT_URI")
    or "https://metricstudio.onrender.com/auth/callback"
)
SCOPES = os.getenv("OAUTH_SCOPES", "")  # まずは空でOK（後で追加可）

FB_AUTH_BASE = "https://www.facebook.com/v20.0/dialog/oauth"
FB_TOKEN_ENDPOINT = "https://graph.facebook.com/v20.0/oauth/access_token"
GRAPH = "https://graph.facebook.com/v20.0"

# --- 必須環境変数チェック ---
def _require_env():
    miss = []
    if not APP_ID: miss.append("META_APP_ID")
    if not APP_SECRET: miss.append("META_APP_SECRET")
    if not REDIRECT_URI: miss.append("OAUTH_REDIRECT_URI または REDIRECT_URI")
    if miss:
        raise HTTPException(500, f"Missing environment variables: {', '.join(miss)}")

# --- OAuth開始 ---
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
    url = f"{FB_AUTH_BASE}?{urlencode(params)}"
    return RedirectResponse(url)

# --- OAuthコールバック ---
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

    return JSONResponse({
        "status": "ok",
        "message": "OAuth success",
        "access_token": token,
        "access_token_preview": (token or "")[:12] + "...",
        "token_type": token_json.get("token_type"),
        "expires_in": token_json.get("expires_in"),
        "scopes_requested": SCOPES.split(",") if SCOPES else [""],
        "note": "デバッグ用：access_tokenは保存していません"
    })

# --- デバッグ用：ページ一覧取得 ---
@app.get("/debug/me_accounts")
async def debug_me_accounts(access_token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{GRAPH}/me/accounts", params={"access_token": access_token})
        return {"status": r.status_code, "json": r.json()}

# --- デバッグ用：ページ→IG基本情報 ---
@app.get("/debug/ig_basic")
async def debug_ig_basic(page_id: str, access_token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r1 = await client.get(f"{GRAPH}/{page_id}", params={
            "fields": "instagram_business_account",
            "access_token": access_token
        })
        if r1.status_code != 200:
            raise HTTPException(r1.status_code, r1.text)

        ig = (r1.json().get("instagram_business_account") or {}).get("id")
        if not ig:
            return {"error": "No instagram_business_account linked to this page."}

        r2 = await client.get(f"{GRAPH}/{ig}", params={
            "fields": "username,profile_picture_url",
            "access_token": access_token
        })
        return {"page_id": page_id, "ig_user_id": ig, "ig_profile": r2.json()}

# --- ルート一覧確認 ---
@app.get("/__routes", include_in_schema=False)
def list_routes():
    return [getattr(r, "path", str(r)) for r in app.router.routes]

# ---------- end ----------
