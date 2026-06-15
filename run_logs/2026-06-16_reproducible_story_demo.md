# PlotWeave Reproducible Short Story Demo Verification

Date: 2026-06-16

## Goal

Verify that the local development environment can run a minimal PlotWeave-style story demo that uses:

- Qwen writer model through Xunfei MaaS
- OpenRouter embeddings
- A reproducible local config file
- Real short-story output saved to disk

## Config Files

- `.env`
  - `WRITER_BASE_URL=https://maas-api.cn-huabei-1.xf-yun.com/v2`
  - `WRITER_MODEL=xopqwen36v35b`
  - `VECTOR_BASE_URL=https://openrouter.ai/api/v1`
  - `VECTOR_MODEL=openai/text-embedding-3-small`
  - `VECTOR_DIMENSION=1536`

- `minimal_story_config.json`
  - Stores reproducible story request settings.
  - Includes title hint, genre, reader preference, reference mode, must-include elements, and output locations.

## Validation 1: Writer Model

A direct qwen call succeeded when using English instructions that request Simplified Chinese output.

Result excerpt:

```text
暴雨如注，叩打着古董店斑驳的橱窗。昏黄灯光下，店主轻推那枚黄铜怀表，齿轮咬合声在寂静中格外清晰。
```

Note: A Chinese prompt was misinterpreted by the provider gateway, so the reproducible demo uses ASCII/English instructions and asks the model to output Simplified Chinese.

## Validation 2: Embedding

Command used project `vector.py` with current `.env`.

Result:

```text
embedding_ok: True
dimension: 1536
first_values: [0.009033203125, -0.00373077392578125, -0.036468505859375, -0.0330810546875, -0.0196685791015625]
```

## Validation 3: Reproducible Short Story Demo

Command:

```bash
uv run python mini_story_demo.py
```

First run failed because `minimal_story_config.json` had a UTF-8 BOM. Fixed `mini_story_demo.py` to read config with `utf-8-sig`.

Final result:

```text
PlotWeave minimal story demo OK
story_path: outputs\minimal_story\short_story.md
metadata_path: outputs\minimal_story\run_metadata.json
embedding_dimension: 1536
```

Story preview:

```text
# 雨夜旧书店

暴雨如注，敲打着青石板路，发出沉闷而急促的鼓点。林默推开“拾光阁”厚重的木门，门楣上的铜铃发出一声喑哑的脆响，仿佛叹息。店内弥漫着陈旧纸张、樟脑和潮湿霉菌混合的气息，昏黄的灯光在堆积如山的书脊间摇曳，将阴影拉得细长如鬼魅。
```

## Output Files

- `outputs/minimal_story/short_story.md`
- `outputs/minimal_story/run_metadata.json`

## Status

PASS. The local environment can run the minimal reproducible story demo, call the qwen writer model, call OpenRouter embeddings, and save an actual short story result.
