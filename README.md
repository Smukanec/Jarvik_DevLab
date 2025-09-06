# DevLab

Minimal Flask-based development assistant.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## AI backend

The `/api/ai` endpoint forwards requests to a [Jarvik Model Gateway](MODEL_GATEWAY.md) instance
that proxies local models through an OpenAI-compatible API.
See [MODEL_GATEWAY.md](MODEL_GATEWAY.md) for full installation and usage instructions.
Configure access via environment variables:

- `MODEL_GATEWAY_URL` (default `http://localhost:8095`)
- `MODEL_GATEWAY_API_KEY` (Bearer token for the gateway)
- `MODEL_GATEWAY_MODEL` (default `jarvik-chat`)

Run the gateway and desired model containers separately, for example:

```bash
docker run -it --rm --gpus all -p 8001:8000 jarvik-chat:latest
```

The gateway offers endpoints such as `/healthz`, `/v1/models`, `/v1/chat/completions`,
and `/v1/embeddings`.

### Text interface

```bash
python tui.py
```

The application starts on [http://localhost:8020](http://localhost:8020).
Use the interface to log in, browse files, edit, diff, invoke AI, and download the project as a ZIP.
