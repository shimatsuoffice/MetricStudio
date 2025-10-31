import os
from urllib.parse import urlencode

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import httpx

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

# === 必要な環境変数 ===
# Render の「Environment」か GitHub の Actions/Render で設定しておくこと
APP_ID = os.getenv("META_APP_ID")              # 例: 2429.........
APP_SECRET = os.getenv("META_APP_SECRET")      # 例: xxxxxxxxxxxxx
REDIRECT_URI = (
    os.getenv("OAUTH_REDIRECT_URI")
    or os.getenv("REDIRECT_URI")
    or "https://metricstudio.onrender.com/auth/callback"
)


# 要求スコープ（2025年仕様：instagram_business_* を使用）
SCOPES = "instagram_business_basic,pages_show_list,instagram_business_manage_insights"

FB_AUTH_BASE = "https://www.facebook.com/v20.0/dialog/oauth"
FB_TOKEN_ENDPOINT = "https://graph.facebook.com/v20.0/oauth/access_token"

def _require_env():
    if not APP_ID or not APP_SECRET or not REDIRECT_URI:
        raise HTTPException(status_code=500, detail="META_APP_ID / META_APP_SECRET / OAUTH_REDIRECT_URI が未設定です。")

@app.get("/auth/login")
def auth_login():
    _require_env()
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
    }
    return RedirectResponse(f"{FB_AUTH_BASE}?{urlencode(params)}")

@app.get("/auth/callback")
async def auth_callback(request: Request, code: str | None = None, error: str | None = None):
    _require_env()
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    # code → access_token 交換
    async with httpx.AsyncClient(timeout=20.0) as client:
        token_params = {
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        }
        r = await client.get(FB_TOKEN_ENDPOINT, params=token_params)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {r.text}")
        token_json = r.json()

    # 最小の動作確認結果だけ返す（審査前なので保存しない）
    return JSONResponse({
        "status": "ok",
        "message": "OAuth success",
        "access_token_preview": token_json.get("access_token", "")[:12] + "...",
        "token_type": token_json.get("token_type"),
        "expires_in": token_json.get("expires_in"),
        "scopes_requested": SCOPES.split(","),
        "note": "このトークンはDB保存していません（セッション表示のみ）"
    })

