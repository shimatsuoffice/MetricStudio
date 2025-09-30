import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI

# .env を mini.py と同じ場所からロード（CWD非依存）
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

app = FastAPI(title="Mini Test")

@app.get("/debug/env")
async def debug_env():
    return {
        "cwd": os.getcwd(),
        "META_APP_ID_set": bool(os.getenv("META_APP_ID")),
        "META_APP_SECRET_set": bool(os.getenv("META_APP_SECRET")),
        "REDIRECT_URI": os.getenv("REDIRECT_URI"),
    }
