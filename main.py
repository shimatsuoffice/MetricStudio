import os
import httpx
from fastapi import HTTPException

GRAPH = "https://graph.facebook.com/v20.0"

@app.get("/debug/me_accounts")
async def debug_me_accounts(access_token: str):
    # 例: /debug/me_accounts?access_token=EAAB...
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{GRAPH}/me/accounts", params={"access_token": access_token})
        return {"status": r.status_code, "json": r.json()}

@app.get("/debug/ig_basic")
async def debug_ig_basic(page_id: str, access_token: str):
    # 1) ページから IG ビジネスID取得
    async with httpx.AsyncClient(timeout=20.0) as client:
        r1 = await client.get(f"{GRAPH}/{page_id}", params={
            "fields": "instagram_business_account", "access_token": access_token
        })
        if r1.status_code != 200:
            raise HTTPException(r1.status_code, r1.text)
        ig = (r1.json().get("instagram_business_account") or {}).get("id")
        if not ig:
            return {"error": "No instagram_business_account linked to the page."}

        # 2) IGの基本情報
        r2 = await client.get(f"{GRAPH}/{ig}", params={
            "fields": "username,profile_picture_url", "access_token": access_token
        })
        return {"page_id": page_id, "ig_user_id": ig, "ig_profile": r2.json()}
