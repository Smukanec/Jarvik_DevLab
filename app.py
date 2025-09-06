# main.py
from flask import Flask, send_from_directory, request, Response
import requests
import os

# ------- Konfigurace -------
GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://127.0.0.1:8095")  # model-gateway (OpenAI kompat.)
BIND_HOST   = os.environ.get("BIND_HOST", "127.0.0.1")
BIND_PORT   = int(os.environ.get("BIND_PORT", "8010"))
TIMEOUT     = int(os.environ.get("TIMEOUT", "120"))

app = Flask(__name__, static_folder="static")

# ------- UI (kořen) -------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/healthz")
def healthz():
    return {"status": "ok", "ui": True, "proxy": True}, 200

# ------- Jednoduché CORS (UI→/v1/*) -------
@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp

@app.route("/v1/<path:subpath>", methods=["GET", "POST", "OPTIONS"])
def proxy_v1(subpath):
    # OPTIONS preflight
    if request.method == "OPTIONS":
        return ("", 204)

    upstream = f"{GATEWAY_URL}/v1/{subpath}"

    # Forward headers (bez Host)
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

    # JSON / raw forward
    data = request.get_data()
    try:
        r = requests.request(
            method=request.method,
            url=upstream,
            headers=headers,
            data=data,
            stream=True,
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        return {"error": f"gateway_unreachable: {str(e)}"}, 502

    # Stream zpět k UI (zachovat kód + hlavičky)
    excluded = {"content-encoding", "transfer-encoding", "connection"}
    resp_headers = [(k, v) for k, v in r.headers.items() if k.lower() not in excluded]

    def generate():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return Response(generate(), status=r.status_code, headers=resp_headers)

if __name__ == "__main__":
    app.run(host=BIND_HOST, port=BIND_PORT, debug=False)
