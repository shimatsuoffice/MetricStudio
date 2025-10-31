from fastapi import FastAPI, HTTPException
import os
import httpx
from fastapi.responses import JSONResponse

app = FastAPI()  # ← これが一番最初に必要！

GRAPH = "https://graph.facebook.com/v20.0"


# --- デバッグ用ルート ---
@app.get("/debug/me_accounts")
async def debug_me_accounts(access_token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{GRAPH}/me/accounts", params={"access_token": access_token})
        return {"status": r.status_code, "json": r.json()}


@app.get("/debug/ig_basic")
async def debug_ig_basic(page_id: str, access_token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        r1 = await client.get(f"{GRAPH}/{page_id}", params={
            "fields": "instagram_business_account", "access_token": access_token
        })
        if r1.status_code != 200:
            raise HTTPException(r1.status_code, r1.text)
        ig = (r1.json().get("instagram_business_account") or {}).get("id")
        if not ig:
            return {"error": "No instagram_business_account linked to the page."}

        r2 = await client.get(f"{GRAPH}/{ig}", params={
            "fields": "username,profile_picture_url", "access_token": access_token
        })
        return {"page_id": page_id, "ig_user_id": ig, "ig_profile": r2.json()}
