# PlotWeave Minimal Demo Run Log

Date: 2026-06-13

## Goal

Create and verify a minimal runnable PlotWeave path without Node.js.

## Files Changed

- `.env`
  - Updated WRITER_* to use the provided API endpoint and model.
  - Kept VECTOR_* as dummy placeholders because the minimal demo does not call embeddings.
- `mini_demo.py`
  - Added a one-command Python demo that creates a project, writes outline/chapter data, saves to disk, reloads it, and prints the result.
- `mini_frontend.py`
  - Added a pure Python browser frontend on `http://127.0.0.1:9000`.
  - It proxies `/api/*` to the FastAPI backend on `http://127.0.0.1:8000`.
  - It supports creating projects, listing projects, reading outlines, and saving outlines.

## Minimal Demo Command

```bash
uv run python mini_demo.py
```

## Minimal Demo Result

```text
PlotWeave minimal demo OK
project_id: 4112fa62-14f6-4e7e-8bea-0d747c7d31cb
project_dir: datas\4112fa62-14f6-4e7e-8bea-0d747c7d31cb
project_name: Minimal Runnable Demo
phase: OUTLINE
outline_title: 最小可运行小说
plots:
  1. 主角在雨夜醒来，发现自己失去了最近三天的记忆。
  2. 他在口袋里找到一张写着陌生地址的纸条。
  3. 纸条指向一座废弃图书馆，也指向他身份的真相。
chapters:
  1. 雨夜醒来 - 建立悬疑开场，让主角发现失忆和线索。
```

## API Smoke Test

The backend API path used by `mini_frontend.py` was also tested through:

- `POST /api/projects`
- `GET /api/projects/{project_id}/outline`

Result:

```json
{
  "ok": true,
  "project_id": "a2ab8471-4513-499d-bf4e-c87dc28859dd",
  "project_name": "API Smoke Demo",
  "outline_title": "未命名小说",
  "phase": 0
}
```

## Note

During API smoke testing, starting another backend reported port `8000` was already in use. The API request still succeeded, which means an existing backend process was already listening on `127.0.0.1:8000`.

## Current Minimal Run Steps

1. Run core demo only:

```bash
uv run python mini_demo.py
```

2. Run backend for the Python frontend:

```bash
uv run uvicorn server:app --host 127.0.0.1 --port 8000
```

3. Run Python frontend:

```bash
uv run python mini_frontend.py
```

4. Open:

```text
http://127.0.0.1:9000
```
