"""Tiny Python frontend for the smallest stable PlotWeave flow.

Run the backend first:
    uv run uvicorn server:app --host 127.0.0.1 --port 8000

Then run this file:
    uv run python mini_frontend.py

Open:
    http://127.0.0.1:9000
"""

from __future__ import annotations

import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer


BACKEND = "http://127.0.0.1:8000"
HOST = "127.0.0.1"
PORT = 9000


HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>PlotWeave Python Mini Frontend</title>
  <style>
    body { font-family: sans-serif; max-width: 960px; margin: 24px auto; line-height: 1.5; }
    input, textarea, button { font-size: 14px; }
    input, textarea { box-sizing: border-box; width: 100%; padding: 8px; margin: 6px 0 12px; }
    textarea { min-height: 160px; }
    button { padding: 8px 14px; margin-right: 8px; cursor: pointer; }
    .row { display: flex; gap: 24px; align-items: flex-start; }
    .col { flex: 1; }
    ul { padding-left: 20px; }
    li { cursor: pointer; margin: 6px 0; }
    .hint { color: #666; font-size: 13px; }
    .box { border: 1px solid #ddd; padding: 16px; border-radius: 8px; margin-bottom: 16px; }
    .error { color: #b00020; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>PlotWeave 最小前端（Python 版）</h1>
  <p class="hint">功能：创建项目、查看项目列表、读取/保存大纲。不依赖 Node，不调用 embeddings。</p>

  <div class="box">
    <h2>创建项目</h2>
    <input id="projectName" placeholder="输入项目名，比如：我的测试小说">
    <button onclick="createProject()">创建项目</button>
    <button onclick="loadProjects()">刷新项目列表</button>
    <p id="error" class="error"></p>
  </div>

  <div class="row">
    <div class="col box">
      <h2>项目列表</h2>
      <ul id="projectList"></ul>
    </div>

    <div class="col box">
      <h2>当前项目大纲</h2>
      <input id="projectId" placeholder="项目ID" readonly>
      <input id="title" placeholder="小说标题">
      <textarea id="plots" placeholder="每行一条剧情"></textarea>
      <button onclick="loadOutline()">读取大纲</button>
      <button onclick="saveOutline()">保存大纲</button>
    </div>
  </div>

<script>
function setError(message) {
  document.getElementById("error").textContent = message || "";
}

async function api(path, method="GET", data=null) {
  setError("");
  const options = { method, headers: {} };
  if (data !== null) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }
  const resp = await fetch(path, options);
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || ("HTTP " + resp.status));
  }
  const ct = resp.headers.get("content-type") || "";
  if (ct.includes("application/json")) return await resp.json();
  return await resp.text();
}

async function loadProjects() {
  try {
    const data = await api("/api/projects");
    const list = document.getElementById("projectList");
    list.innerHTML = "";
    for (const p of data.projects || []) {
      const li = document.createElement("li");
      li.textContent = `${p.name} [phase=${p.phase}] [${p.id}]`;
      li.onclick = () => {
        document.getElementById("projectId").value = p.id;
        loadOutline();
      };
      list.appendChild(li);
    }
  } catch (error) {
    setError(String(error));
  }
}

async function createProject() {
  try {
    const name = document.getElementById("projectName").value.trim();
    if (!name) {
      alert("请输入项目名");
      return;
    }
    const project = await api("/api/projects", "POST", { name });
    document.getElementById("projectId").value = project.id;
    await loadProjects();
    await loadOutline();
  } catch (error) {
    setError(String(error));
  }
}

async function loadOutline() {
  try {
    const projectId = document.getElementById("projectId").value.trim();
    if (!projectId) {
      alert("没有项目ID");
      return;
    }
    const outline = await api(`/api/projects/${projectId}/outline`);
    document.getElementById("title").value = outline.title || "";
    document.getElementById("plots").value = (outline.plots || []).join("\n");
  } catch (error) {
    setError(String(error));
  }
}

async function saveOutline() {
  try {
    const projectId = document.getElementById("projectId").value.trim();
    if (!projectId) {
      alert("没有项目ID");
      return;
    }
    const title = document.getElementById("title").value.trim();
    const plots = document.getElementById("plots").value
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
    await api(`/api/projects/${projectId}/outline`, "PUT", { title, plots });
    alert("保存成功");
    await loadProjects();
  } catch (error) {
    setError(String(error));
  }
}

loadProjects();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            self._send_html(HTML)
            return
        if self.path.startswith("/api/"):
            self._proxy("GET")
            return
        self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        if self.path.startswith("/api/"):
            self._proxy("POST")
            return
        self.send_error(404, "Not Found")

    def do_PUT(self) -> None:
        if self.path.startswith("/api/"):
            self._proxy("PUT")
            return
        self.send_error(404, "Not Found")

    def _proxy(self, method: str) -> None:
        body = None
        length = int(self.headers.get("Content-Length", "0"))
        if length > 0:
            body = self.rfile.read(length)

        headers = {}
        content_type = self.headers.get("Content-Type")
        if content_type:
            headers["Content-Type"] = content_type

        request = urllib.request.Request(
            BACKEND + self.path,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request) as response:
                data = response.read()
                self.send_response(response.status)
                self.send_header(
                    "Content-Type",
                    response.headers.get("Content-Type", "application/json; charset=utf-8"),
                )
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as error:
            self.send_response(error.code)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(error.read())
        except urllib.error.URLError as error:
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Backend unavailable: {error}".encode("utf-8"))

    def _send_html(self, content: str) -> None:
        data = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print(f"mini frontend running: http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), Handler).serve_forever()
