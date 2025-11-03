# main.py（コピペで置き換えOK）

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse, JSONResponse
import os
import httpx
from urllib.parse import urlencode

app = FastAPI()

# --- ping系 ---
@app.api_route("/health", methods=["GET", "HEAD", "OPTIONS"], include_in_schema=False)
def health_all():
    return PlainTextResponse("ok", media_type="text/plain")

@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root_all():
    return PlainTextResponse("ok", media_type="text/plain")

# --- 環境変数 ---
APP_ID = os.getenv("META_APP_ID")               # 例: 2429...
APP_SECRET = os.getenv("META_APP_SECRET")       # 例: xxxxxx
REDIRECT_URI = (
    os.getenv("OAUTH_REDIRECT_URI")
    or os.getenv("REDIRECT_URI")
    or "https://metricstudio.onrender.com/auth/callback"
)
SCOPES = os.getenv("OAUTH_SCOPES") or "pages_show_list,instagram_business_basic"

# --- OAuth開始（スコープ付き & 再同意） ---
@app.get("/auth/login")
def auth_login():
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,            # ★重要：権限要求
        "auth_type": "rerequest",   # ★重要：取りこぼし時に再同意を促す
    }
    url = "https://www.facebook.com/v20.0/dialog/oauth?" + urlencode(params)
    return RedirectResponse(url)

# --- コールバック：トークン交換 ---
@app.get("/auth/callback")
async def auth_callback(code: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            "https://graph.facebook.com/v20.0/oauth/access_token",
            params={
                "client_id": APP_ID,
                "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            },
        )
    data = r.json()
    token = data.get("access_token")
    return JSONResponse({
        "status": "ok",
        "message": "OAuth success",
        "access_token_preview": (token[:12] + "..." if token else None),
        "token_type": data.get("token_type"),
        "expires_in": data.get("expires_in"),
        "scopes_requested": SCOPES.split(","),
        "note": "このトークンはDB保存していません（セッション表示のみ）",
    })

# --- トークン中身を可視化（scopes確認） ---
@app.get("/debug/token_info")
async def debug_token_info(access_token: str):
    app_access_token = f"{APP_ID}|{APP_SECRET}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            "https://graph.facebook.com/v20.0/debug_token",
            params={"input_token": access_token, "access_token": app_access_token},
        )
    return JSONResponse(r.json())

# --- FBページ一覧（pages_show_list が効いているか確認） ---
@app.get("/debug/me_accounts")
async def debug_me_accounts(access_token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            "https://graph.facebook.com/v20.0/me/accounts",
            params={"access_token": access_token},
        )
    return JSONResponse({"status": r.status_code, "data": r.json()})

# --- 任意：ログインユーザー確認 ---
@app.get("/debug/me")
async def debug_me(access_token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            "https://graph.facebook.com/v20.0/me",
            params={"access_token": access_token, "fields": "id,name"},
        )
    return JSONResponse(r.json())

# --- ページ→InstagramビジネスID・基本情報確認 ---
@app.get("/debug/ig_basic")
async def debug_ig_basic(page_id: str, access_token: str):
    # 例: /debug/ig_basic?page_id=123456789012345&access_token=...
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"https://graph.facebook.com/v20.0/{page_id}",
            params={
                "access_token": access_token,
                # instagram_business_account の基本情報を取得
                "fields": "instagram_business_account{id,username,profile_picture_url}",
            },
        )
    return JSONResponse({"status": r.status_code, "data": r.json()})
