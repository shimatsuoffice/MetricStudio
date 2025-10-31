from fastapi.responses import PlainTextResponse

# どのメソッドでも200を返す・軽量テキスト
@app.api_route("/health", methods=["GET","HEAD","OPTIONS"], include_in_schema=False)
def health_all():
    return PlainTextResponse("ok", media_type="text/plain")

# ルートもヘルス兼用に（Renderのデフォ監視対策）
@app.api_route("/", methods=["GET","HEAD"], include_in_schema=False)
def root_all():
    return PlainTextResponse("ok", media_type="text/plain")
