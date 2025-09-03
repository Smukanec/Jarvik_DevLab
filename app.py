import os
import io
import zipfile
import difflib

from flask import Flask, request, jsonify, send_from_directory, send_file, abort
import requests

app = Flask(__name__, static_folder='static', static_url_path='')

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), 'project')
MODEL_GATEWAY_URL = os.environ.get('MODEL_GATEWAY_URL', 'http://localhost:8095')
MODEL_GATEWAY_API_KEY = os.environ.get('MODEL_GATEWAY_API_KEY', '')
DEFAULT_MODEL = os.environ.get('MODEL_GATEWAY_MODEL', 'jarvik-chat')


def safe_path(path: str) -> str:
    """Ensure the path stays within PROJECT_ROOT."""
    full_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    if not full_path.startswith(PROJECT_ROOT):
        abort(400, 'Invalid path')
    return full_path


@app.route('/')
def index() -> "str":
    return send_from_directory(app.static_folder, 'index.html')


@app.post('/api/login')
def login():
    data = request.get_json() or {}
    user = data.get('username')
    password = data.get('password')
    if user and password:
        return jsonify({'token': 'dummy-token'})
    return jsonify({'error': 'Invalid credentials'}), 401


@app.get('/api/tree')
def tree():
    files = []
    for root, _, filenames in os.walk(PROJECT_ROOT):
        for name in filenames:
            files.append(os.path.relpath(os.path.join(root, name), PROJECT_ROOT))
    return jsonify(files)


@app.route('/api/file', methods=['GET', 'POST'])
def file():
    path = request.args.get('path', '')
    file_path = safe_path(path)
    if request.method == 'GET':
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            open(file_path, 'w').close()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content})
    else:
        data = request.get_json() or {}
        content = data.get('content', '')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'status': 'ok'})


@app.post('/api/diff')
def diff_api():
    data = request.get_json() or {}
    old = (data.get('old') or '').splitlines(keepends=True)
    new = (data.get('new') or '').splitlines(keepends=True)
    diff_text = ''.join(difflib.unified_diff(old, new, fromfile='old', tofile='new'))
    return jsonify({'diff': diff_text})


@app.get('/api/download')
def download():
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(PROJECT_ROOT):
            for filename in files:
                filepath = os.path.join(root, filename)
                arcname = os.path.relpath(filepath, PROJECT_ROOT)
                zf.write(filepath, arcname)
    mem.seek(0)
    return send_file(mem, mimetype='application/zip', download_name='project.zip', as_attachment=True)


@app.post('/api/ai')
def ai():
    data = request.get_json() or {}
    message = data.get('message', '')
    model = data.get('model', DEFAULT_MODEL)
    try:
        headers = {}
        if MODEL_GATEWAY_API_KEY:
            headers['Authorization'] = f'Bearer {MODEL_GATEWAY_API_KEY}'
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': message}],
        }
        res = requests.post(f"{MODEL_GATEWAY_URL}/v1/chat/completions", json=payload, headers=headers)
        res.raise_for_status()
        completion = res.json()
        text = completion['choices'][0]['message']['content']
        return jsonify({'response': text})
    except requests.RequestException as exc:
        return jsonify({'error': str(exc)}), 500
    except (KeyError, IndexError):
        return jsonify({'error': 'Invalid response from model gateway'}), 500


if __name__ == '__main__':
    app.run(port=8020, debug=True)
