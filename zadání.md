Takže shrnutí požadavků na DevLab apku (náhrada Codexu):

1) Co má být nezávislé

Apka není vázaná na Jarvik_U ani na Otce Furu, ale:

může použít stejné modely z Ollamy (Mistral, LLaMA3, Phi-3, …),

může volat jejich API přímo (http://localhost:11434/api/generate).

Otec Fura = knowledge + historie, ale DevLab má být schopný běžet i bez něj.

2) Funkce aplikace

Správa projektu

Zobrazí strom projektu.

Načte soubor (pokud chybí → vytvoří).

Uloží nové verze.

Umožní stáhnout ZIP.

AI asistence

Pošle prompt na Ollamu (vybraný model).

Vloží/změní kód podle výsledku.

Porovnání

Diff starý vs. nový soubor.

Kontrola

Jednoduchá kontrola závislostí (requirements.txt, importy).

Rozšíření později

Testování (pytest/PKku).

3) Architektura

Backend (Flask)

/api/tree – vrátí JSON strom projektu.

/api/file – GET = načti, POST = ulož.

/api/diff – diff.

/api/download – ZIP.

/api/ai – proxy na Ollamu (model vybere uživatel).

Frontend (HTML/JS – MVP, později React)

Levý panel = strom projektu.

Pravý panel = editor (CodeMirror/Monaco).

Ovládání:

Vyber model.

Prompt → AI vrátí návrh kódu.

Tlačítko „Diff“ a „Uložit“.

Tlačítko „Stáhnout ZIP“.

4) Výhody

Nezávislá apka – běží sama, používá Ollamu přímo.

Kompatibilní s Jarvikem – když běží i Jarvik/Fura, můžeš volit, odkud brát znalosti.

Hot-swap modelů – stejné jako v Jarvik_U, jen UI pro vývoj.

👉 otázka:
Chceš, abych ti teď připravil kompletní skeleton projektu (Flask backend + HTML UI se stromem a editorem), který už rovnou umí:

volat Ollamu pro generování kódu,

načítat a ukládat soubory projektu,

dělat diff?

To by byla první verze DevLab apky.

Řekl/a jsi:
je vazaná na otec fura plně..  autoriuzace, pamet a knowledge, je tam.
ChatGPT řekl:

Ok ✅ takže je to jasné:

DevLab apka = plně napojená na Otce Furu, tzn.:

Autorizace přes API Fura (stejný login/uživatelé jako Jarvik_U).

Paměť + knowledge se neřeší lokálně, ale vždy voláním Fura API.

Modely – stejně jako Jarvik, vyvolávají se přes API (Ollama / Fura proxy).

Apka se stará o UI pro vývoj, tedy správa souborů, diff, generování kódu.

Architektura DevLab (navázaná na Furu)

Frontend (UI – HTML/JS, později React)

Levý panel: strom projektu (získaný přes /project/tree).

Pravý panel: editor souboru (CodeMirror/Monaco).

Ovládací prvky:

Přihlášení (token od Fura).

Výběr modelu (seznam z Fura).

Tlačítka: „Generovat“, „Diff“, „Uložit“, „Stáhnout ZIP“.

Backend (Flask, běží vedle Jarvik_U)

/api/login – proxy login na Fura → uloží token.

/api/tree – strom projektu.

/api/file – načíst/uložit soubor.

/api/diff – porovnání verzí.

/api/download – stáhnout ZIP.

/api/ai – proxy na /ask Fura (s tokenem).

vše ostatní (knowledge, memory) už řeší Fura.

Tok požadavků

Uživatel se přihlásí → /login → Fura (dostane token).

Token se používá pro všechny operace (AI, knowledge, memory).

Strom projektu a soubory se spravují lokálně na serveru, ale AI vždy přes Fura.

Uložené změny → do složky projektu na serveru.

👉 otázka pro tebe:
Chceš, abych ti teď připravil MVP skeleton DevLab apky (Flask backend + HTML UI), který už:

zvládá login přes Furu,

strom/načtení/uložení souborů,

volání modelů přes Furu /ask,

základní diff?

Pak to budeme postupně rozšiřovat o export ZIP, testy, atd.

Řekl/a jsi:
jo, tak nejak si to predstavuji.ů
ChatGPT řekl:

Perfektní ✅
Takže první krok: připravím MVP skeleton DevLab apky:

Flask backend (API):

/api/login → proxy na Fura login → uloží token.

/api/tree → vrací strom projektu.

/api/file → načtení/uložení souboru.

/api/diff → diff starý/nový soubor.

/api/ai → proxy na /ask Fura s tokenem.

HTML/JS UI (zatím jednoduché, později React):

Přihlášení (uživatel/heslo).

Levý panel: strom projektu.

Pravý panel: editor kódu.

Tlačítka: Generovat kód (AI), Uložit, Diff.

👉 potvrď, jestli to chceš mít rovnou připravené jako celý funkční skeleton projektu se soubory (app.py, static/index.html, templates, atd.), který ti sem vypíšu. Pak to můžeš rovnou hodit na server a zkoušet.

Mám to takhle udělat?

Řekl/a jsi:
napal jsem všechno
ChatGPT řekl:

Dobře 👍
Tak já ti to rovnou připravím celé jako skeleton projektu DevLab, který:

Běží na Flasku

Má základní API (/api/login, /api/tree, /api/file, /api/diff, /api/ai)

Má HTML UI (index.html) se stromem projektu a editorem

Všechny AI požadavky posílá přes Otce Furu (autorizace tokenem)

Umí pracovat se soubory (načíst, uložit, vytvořit, diff)

Struktura projektu
DevLab/
├── app.py               # Flask backend
├── requirements.txt     # závislosti
├── static/
│   ├── index.html       # UI
│   ├── style.css        # vzhled
│   └── app.js           # logika UI (fetch, diff, atd.)
└── project/             # složka pro zdrojové soubory projektu

app.py
from flask import Flask, request, jsonify, send_file
import os, json, difflib, zipfile, io, requests

app = Flask(__name__)

# Config
FURA_URL = "http://localhost:8090"   # Otec Fura API
PROJECT_ROOT = "project"
SESSION = {"token": None}

os.makedirs(PROJECT_ROOT, exist_ok=True)

# ---- Helpers ----
def get_tree(path=PROJECT_ROOT):
    tree = []
    for root, dirs, files in os.walk(path):
        rel_root = os.path.relpath(root, PROJECT_ROOT)
        for f in files:
            tree.append(os.path.join(rel_root, f) if rel_root != "." else f)
    return tree

# ---- API ----
@app.route("/api/login", methods=["POST"])
def login():
    creds = request.json
    r = requests.post(f"{FURA_URL}/login", json=creds)
    if r.status_code == 200:
        SESSION["token"] = r.json().get("token")
    return jsonify(r.json()), r.status_code

@app.route("/api/tree", methods=["GET"])
def tree():
    return jsonify(get_tree())

@app.route("/api/file", methods=["GET", "POST"])
def file_api():
    path = os.path.join(PROJECT_ROOT, request.args.get("path", ""))
    if request.method == "GET":
        if os.path.exists(path):
            with open(path, "r") as f:
                return jsonify({"content": f.read()})
        else:
            return jsonify({"content": ""})
    else:  # POST = save
        data = request.json.get("content", "")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(data)
        return jsonify({"status": "saved"})

@app.route("/api/diff", methods=["POST"])
def diff_api():
    data = request.json
    old = data.get("old", "").splitlines()
    new = data.get("new", "").splitlines()
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    return jsonify({"diff": "\n".join(diff)})

@app.route("/api/ai", methods=["POST"])
def ai_api():
    if not SESSION["token"]:
        return jsonify({"error": "Not logged in"}), 403
    payload = request.json
    headers = {"Authorization": f"Bearer {SESSION['token']}"}
    r = requests.post(f"{FURA_URL}/ask", json=payload, headers=headers)
    return jsonify(r.json()), r.status_code

@app.route("/api/download", methods=["GET"])
def download():
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, "w") as zf:
        for root, _, files in os.walk(PROJECT_ROOT):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, PROJECT_ROOT)
                zf.write(full, rel)
    mem_zip.seek(0)
    return send_file(mem_zip, as_attachment=True, download_name="project.zip")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8020, debug=True)

static/index.html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>DevLab</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>DevLab</h1>
  <div id="login">
    <input id="user" placeholder="Uživatel">
    <input id="pass" placeholder="Heslo" type="password">
    <button onclick="login()">Přihlásit</button>
  </div>
  <div id="main" style="display:none;">
    <div id="sidebar">
      <h3>Projekt</h3>
      <ul id="tree"></ul>
      <button onclick="download()">Stáhnout ZIP</button>
    </div>
    <div id="editor">
      <h3 id="filename">Žádný soubor</h3>
      <textarea id="code" rows="25" cols="80"></textarea><br>
      <button onclick="save()">Uložit</button>
      <button onclick="ai()">Generovat (AI)</button>
      <button onclick="diff()">Diff</button>
      <pre id="diffout"></pre>
      <pre id="aiout"></pre>
    </div>
  </div>
  <script src="app.js"></script>
</body>
</html>

static/app.js
let currentFile = null;
let oldContent = "";

async function login() {
  let user = document.getElementById("user").value;
  let pass = document.getElementById("pass").value;
  let res = await fetch("/api/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({username: user, password: pass})
  });
  let data = await res.json();
  if (res.ok) {
    document.getElementById("login").style.display="none";
    document.getElementById("main").style.display="block";
    loadTree();
  } else {
    alert("Login failed: " + JSON.stringify(data));
  }
}

async function loadTree() {
  let res = await fetch("/api/tree");
  let files = await res.json();
  let ul = document.getElementById("tree");
  ul.innerHTML = "";
  files.forEach(f=>{
    let li=document.createElement("li");
    li.textContent=f;
    li.onclick=()=>loadFile(f);
    ul.appendChild(li);
  });
}

async function loadFile(path) {
  let res = await fetch("/api/file?path="+encodeURIComponent(path));
  let data = await res.json();
  currentFile=path;
  oldContent=data.content;
  document.getElementById("filename").textContent=path;
  document.getElementById("code").value=data.content;
}

async function save() {
  if (!currentFile) return;
  let content=document.getElementById("code").value;
  await fetch("/api/file?path="+encodeURIComponent(currentFile), {
    method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({content})
  });
  oldContent=content;
}

async function diff() {
  let newContent=document.getElementById("code").value;
  let res=await fetch("/api/diff",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({old:oldContent,new:newContent})});
  let data=await res.json();
  document.getElementById("diffout").textContent=data.diff;
}

async function ai() {
  let prompt="Uprav soubor: "+currentFile+"\n\n"+document.getElementById("code").value;
  let res=await fetch("/api/ai",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:prompt})});
  let data=await res.json();
  document.getElementById("aiout").textContent=data.response || JSON.stringify(data);
}

function download() {
  window.location="/api/download";
}

static/style.css
body { font-family: sans-serif; background: #1e1e1e; color: #ddd; }
h1 { color: #6f6; }
#sidebar { float:left; width:20%; border-right:1px solid #444; padding:1em; }
#editor { margin-left:22%; padding:1em; }
textarea { width:100%; background:#111; color:#eee; font-family: monospace; }
pre { background:#222; padding:0.5em; }
button { margin:0.2em; }


👉 Tohle je základ. Stačí hodit do složky a spustit:

pip install flask requests
python app.py


a pojede to na http://localhost:8020.

Chceš, abych to ještě propojil rovnou s konkrétními endpointy Otce Fura (login, ask), podle tvého skutečného API formátu?

Řekl/a jsi:
 tkže ten puvodni muzu smazat a jdeme nanovo?
ChatGPT řekl:

Jo přesně tak 👍

Ten původní pokus (Codex/DevLab, co ti padal) můžeš klidně smazat.

Tohle je nový skeleton, čistý start → funguje samostatně a je rovnou připravený na propojení s Otcem Fura (login, ask).

Projekt si můžeš uložit jako DevLab/ a postupně budeme doplňovat funkce (ZIP export, testy, kontrola závislostí).

👉 doporučený postup:

Vytvoř složku DevLab.

Vlož tam soubory, co jsem ti napsal (app.py, static/…, requirements.txt, project/).

Spusť pip install flask requests.

Spusť python app.py.

Otevři v prohlížeči http://localhost:8020.

Chceš, abych ti rovnou napsal i requirements.txt a základní README.md k tomuhle skeletonu?

ChatGPT může dělat chyby. OpenAI nepoužívá k trénování svých modelů data z pracovního prostoru Vibe Factory.
