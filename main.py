from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.api_route("/health", methods=["GET", "HEAD", "OPTIONS"], include_in_schema=False)
def health_all():
    return PlainTextResponse("ok", media_type="text/plain")

@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root_all():
    return PlainTextResponse("ok", media_type="text/plain")
