# --- main.py 先頭の正しい順序（最小安定版） ---
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import os
import httpx

app = FastAPI()  # ←←← app を最初に作る（超重要）

# どのメソッドでも 200 を返す軽量ヘルス
@app.api_route("/health", methods=["GET", "HEAD", "OPTIONS"], include_in_schema=False)
def health_all():
    return PlainTextResponse("ok", media_type="text/plain")

# ルートもヘルス扱い（Render のデフォ監視対策）
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root_all():
    return PlainTextResponse("ok", media_type="text/plain")

# （この下に OAuth, /auth/login, /auth/callback, /debug/... を置く）
