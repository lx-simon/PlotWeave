# PlotWeave Minimal Plot Loom Demo Run Log

Date: 2026-06-14

## Goal

Build and verify a minimal runnable PlotWeave demo that feels like a real "plot loom": it must call an intelligent model, generate a story seed, write an actual first chapter, persist the project, and show a real output file.

## Files Changed

- `.env`
  - WRITER configured to Xunfei MaaS endpoint.
  - VECTOR configured to OpenRouter `openai/text-embedding-3-small`.
- `mini_demo.py`
  - Upgraded from outline-only intelligent demo to real novel-output demo.
  - Calls LLM once to generate story seed JSON.
  - Calls LLM again to generate first chapter prose.
  - Saves outline/chapter metadata through PlotWeave models.
  - Writes the novel chapter to `datas/<project_id>/outputs/00_<chapter_title>.md`.
- `docs/MINIMAL_PLOT_LOOM_RUNBOOK_CN.md`
  - Added Chinese startup and chain documentation.
  - Explains which files participate in each step.
- `run_logs/2026-06-14_plot_loom_demo.md`
  - This log file.

## Run Command

```bash
uv run python mini_demo.py
```

## Run Result

```text
PlotWeave plot loom demo OK
project_id: c486120f-0648-42b6-8ceb-ac9be777fbda
project_dir: datas\c486120f-0648-42b6-8ceb-ac9be777fbda
project_name: Plot Loom Intelligent Demo
phase: OUTLINE
outline_title: 拾光修补匠
chapter_output_path: datas\c486120f-0648-42b6-8ceb-ac9be777fbda\outputs\00_雨夜的古董店.md
```

## Model Story Seed

```json
{
  "title": "拾光修补匠",
  "plots": [
    "主角在古董店发现能修补破碎记忆的神秘怀表，却因此卷入一场跨越百年的阴谋。",
    "为了找回失落的真相，他必须收集散落在城市角落的三段关键记忆碎片。",
    "在对抗黑暗势力的同时，他逐渐修复了自己与亲人之间因误会而破碎的情感羁绊。"
  ],
  "chapter_title": "雨夜的古董店",
  "chapter_intent": "引入主角身份与神秘怀表，营造悬疑氛围，同时通过主角对旧物的珍视奠定温暖基调。"
}
```

## Novel Excerpt

```text
# 雨夜的古董店

暴雨如注，敲打在“拾光阁”斑驳的玻璃窗上，发出沉闷而急促的声响，仿佛无数细小的手指在急切地叩问着这道隔绝尘世的屏障。林远坐在柜台后，指尖轻轻摩挲着一块黄铜怀表的表盖。店内光线昏黄，空气中弥漫着陈年纸张、旧木头和淡淡樟脑丸混合的气味，这是一种令人安心的、属于时间的味道。

作为这座城市里最后一位“修补匠”，林远修补的从来不是物品本身，而是附着其上被遗忘的情感与记忆。他的手指修长而稳定，此刻正对准那枚怀表内部一枚断裂的游丝。就在刚才，一位穿着黑色雨衣、面容模糊的老妇人将这枚怀表匆匆塞进他手中，留下一句语焉不详的“它快醒了”，便消失在雨幕中。
```

## Output Files

- `datas/c486120f-0648-42b6-8ceb-ac9be777fbda/metadata.json`
- `datas/c486120f-0648-42b6-8ceb-ac9be777fbda/outline.yaml`
- `datas/c486120f-0648-42b6-8ceb-ac9be777fbda/chapter_infos.yaml`
- `datas/c486120f-0648-42b6-8ceb-ac9be777fbda/outputs/00_雨夜的古董店.md`

## Chain Explanation

1. `config.py` loads `.env`.
2. `agent.py` creates `agent.llm` using WRITER_* config.
3. `mini_demo.py` calls `agent.llm.ainvoke(...)` to generate a story seed.
4. `mini_demo.py` calls `agent.llm.ainvoke(...)` again to write first chapter prose.
5. `ProjectInstant`, `Outline`, and `ChapterInfo` persist project metadata.
6. `project_instant.output_path(...)` determines the chapter markdown output location.
7. The project is reloaded through `load_from_directory(...)` to verify saved data.

## Verification

Status: PASS

The current development environment successfully generated a real novel chapter through the configured LLM and wrote it into the normal PlotWeave data directory.
