from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.api_route("/health", methods=["GET", "HEAD", "OPTIONS"], include_in_schema=False)
def health_all():
    return PlainTextResponse("ok", media_type="text/plain")

@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root_all():
    return PlainTextResponse("ok", media_type="text/plain")

from fastapi.responses import RedirectResponse, JSONResponse
import os
import httpx
from urllib.parse import urlencode

APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
REDIRECT_URI = "https://metricstudio.onrender.com/auth/callback"

@app.get("/auth/login")
def auth_login():
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code"
    }
    url = "https://www.facebook.com/v20.0/dialog/oauth?" + urlencode(params)
    return RedirectResponse(url)

@app.get("/auth/callback")
async def auth_callback(code: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            "https://graph.facebook.com/v20.0/oauth/access_token",
            params={
                "client_id": APP_ID,
                "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code
            }
        )
    token = r.json().get("access_token")
    return JSONResponse({"status": "ok", "access_token": token})

@app.get("/debug/me_accounts")
async def debug_me_accounts(access_token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            "https://graph.facebook.com/v20.0/me/accounts",
            params={"access_token": access_token}
        )
    return JSONResponse({"status": r.status_code, "data": r.json()})


