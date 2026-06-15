# PlotWeave Intelligent Minimal Demo Run Log

Date: 2026-06-14

## Goal

Upgrade the previous minimal demo from a local persistence-only shell into a real intelligent demo that calls an LLM and writes the model output into PlotWeave project files.

## API Configuration

- WRITER_BASE_URL: https://maas-api.cn-huabei-1.xf-yun.com/v2
- WRITER_MODEL: xopqwen36v35b
- VECTOR_BASE_URL: https://openrouter.ai/api/v1
- VECTOR_MODEL: openai/text-embedding-3-small
- VECTOR_DIMENSION: 1536

Keys are stored in `.env` and should not be committed.

## Files Changed

- `.env`
  - Updated WRITER_* to the provided Xunfei MaaS endpoint and model.
  - Updated VECTOR_* to OpenRouter embeddings using `openai/text-embedding-3-small`.
- `mini_demo.py`
  - Replaced local-only placeholder behavior with a real LLM call through `agent.llm.ainvoke`.
  - The LLM is prompted to output JSON containing a title, 3 plot points, chapter title, and chapter intent.
  - The parsed LLM output is saved through PlotWeave's existing `ProjectInstant`, `Outline`, and `ChapterInfo` persistence flow.
- `mini_frontend.py`
  - Kept as the no-Node browser UI for project creation, listing, and outline editing.

## Intelligent Demo Command

```bash
uv run python mini_demo.py
```

## Intelligent Demo Result

```text
PlotWeave intelligent demo OK
--- raw_llm_response ---
{
  "title": "遗忘当铺的守夜人",
  "plots": [
    "主角在深夜的当铺收到一段被抵押的童年记忆，发现记忆片段中隐藏着城市地下遗迹的线索。",
    "主角在追寻记忆真相时，与一位能够看见灵体的少女相遇，两人共同解开记忆背后的诅咒。",
    "主角最终选择赎回记忆，用温暖的陪伴治愈少女的孤独，并让被遗忘的城市传说重新焕发生机。"
  ],
  "chapter_title": "雨夜的第十二声钟响",
  "chapter_intent": "通过雨夜氛围营造悬疑感，引入当铺这一奇幻场景，并暗示主角内心的孤独与对过去的渴望，为后续温暖的情感铺垫基调。"
}
--- persisted_project ---
project_id: 8bf83a20-a27e-4a78-8f11-9aa6b3682505
project_dir: datas\8bf83a20-a27e-4a78-8f11-9aa6b3682505
project_name: Intelligent Minimal Demo
phase: OUTLINE
outline_title: 遗忘当铺的守夜人
plots:
  1. 主角在深夜的当铺收到一段被抵押的童年记忆，发现记忆片段中隐藏着城市地下遗迹的线索。
  2. 主角在追寻记忆真相时，与一位能够看见灵体的少女相遇，两人共同解开记忆背后的诅咒。
  3. 主角最终选择赎回记忆，用温暖的陪伴治愈少女的孤独，并让被遗忘的城市传说重新焕发生机。
chapters:
  1. 雨夜的第十二声钟响 - 通过雨夜氛围营造悬疑感，引入当铺这一奇幻场景，并暗示主角内心的孤独与对过去的渴望，为后续温暖的情感铺垫基调。
```

## Embedding Smoke Test

Command used a direct `vector.generate_vector(...)` call through the project code.

Result:

```text
embedding_ok True 1536 [0.017822265625, 0.0028533935546875, 0.01363372802734375]
```

## Current Minimal Run Steps

1. Run intelligent minimal demo:

```bash
uv run python mini_demo.py
```

2. Optional no-Node frontend:

```bash
uv run uvicorn server:app --host 127.0.0.1 --port 8000
uv run python mini_frontend.py
```

Then open:

```text
http://127.0.0.1:9000
```
