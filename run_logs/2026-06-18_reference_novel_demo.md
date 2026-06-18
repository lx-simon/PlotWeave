# PlotWeave Reference Novel Demo Run Log

Date: 2026-06-18

## Goal

Restore a minimal working path for reading a whole reference novel and generating a new story using retrieved reference chunks.

## Files Added

- `reference_novels/README.md`
- `reference_novels/sample_fog_bell.md`
- `reference_story_demo.py`
- `docs/REFERENCE_NOVEL_RUNBOOK_CN.md`
- `outputs/reference_story/story_from_references.md`
- `outputs/reference_story/retrieved_chunks.json`
- `outputs/reference_story/run_metadata.json`

## Run Command

```bash
uv run python reference_story_demo.py
```

## Result

```text
PlotWeave reference story demo OK
reference_files: ['sample_fog_bell.md']
chunk_count: 2
story_path: outputs\reference_story\story_from_references.md
retrieved_path: outputs\reference_story\retrieved_chunks.json
```

## Retrieved Chunks

```text
1. sample_fog_bell.md#0 score=0.5997
2. sample_fog_bell.md#1 score=0.5513
```

## Story Output

```text
# 雨夜修补匠

暴雨如注，敲打着“拾遗斋”斑驳的木门，发出沉闷的声响，仿佛无数只湿冷的手指在叩问门扉。林远坐在昏黄的台灯下，手里握着一把极细的银镊子。他是这家旧书店的店主，也是城里少有人知的“记忆修补匠”。
```

## Verification

Status: PASS

The local environment successfully:

1. Read a whole reference `.md` novel file.
2. Split it into chunks.
3. Embedded chunks through OpenRouter.
4. Retrieved relevant chunks by cosine similarity.
5. Generated a new story through qwen.
6. Saved story, retrieved chunks, and metadata to disk.
