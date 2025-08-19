let currentFile = null;
let oldContent = "";

async function login() {
  let user = document.getElementById("user").value;
  let pass = document.getElementById("pass").value;
  let res = await fetch("/api/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username: user, password: pass})
  });
  let data = await res.json();
  if (res.ok) {
    document.getElementById("login").style.display = "none";
    document.getElementById("main").style.display = "block";
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
  files.forEach(f => {
    let li = document.createElement("li");
    li.textContent = f;
    li.onclick = () => loadFile(f);
    ul.appendChild(li);
  });
}

async function loadFile(path) {
  let res = await fetch("/api/file?path=" + encodeURIComponent(path));
  let data = await res.json();
  currentFile = path;
  oldContent = data.content;
  document.getElementById("filename").textContent = path;
  document.getElementById("code").value = data.content;
}

async function save() {
  if (!currentFile) return;
  let content = document.getElementById("code").value;
  await fetch("/api/file?path=" + encodeURIComponent(currentFile), {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({content})
  });
  oldContent = content;
}

async function diff() {
  let newContent = document.getElementById("code").value;
  let res = await fetch("/api/diff", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({old: oldContent, new: newContent})
  });
  let data = await res.json();
  document.getElementById("diffout").textContent = data.diff;
}

async function ai() {
  if (!currentFile) return;
  let prompt = "Uprav soubor: " + currentFile + "\n\n" + document.getElementById("code").value;
  let res = await fetch("/api/ai", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: prompt})
  });
  let data = await res.json();
  document.getElementById("aiout").textContent = data.response || JSON.stringify(data);
}

function download() {
  window.location = "/api/download";
}
