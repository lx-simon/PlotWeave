"""Minimal intelligent PlotWeave demo that produces an actual novel chapter.

This is the smallest "plot loom" path that produces visible fiction output:
1. Calls the configured WRITER_* LLM to generate a story seed as JSON.
2. Calls the LLM again to write the first chapter prose.
3. Saves outline/chapter metadata through PlotWeave's normal persistence models.
4. Writes the generated chapter to datas/<uuid>/outputs/00_<chapter>.md.
5. Reloads the project from disk and prints the persisted novel output.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any

import aiofiles
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import agent
import project_instant
from chapter import ChapterInfo
from outline import Outline
from project_instant import ProjectInstant, load_from_directory, save_to_directory


SEED_PROMPT = """请为 PlotWeave 的最小可运行 demo 生成一个原创中文小说设定。
必须只输出 JSON，不要 Markdown，不要解释。
JSON 格式如下：
{
  "title": "小说标题",
  "plots": ["剧情1", "剧情2", "剧情3"],
  "chapter_title": "第一章标题",
  "chapter_intent": "第一章写作意图"
}
要求：
- 标题不超过 12 个汉字
- plots 必须正好 3 条
- 风格：悬疑、奇幻、带一点温暖
"""

CHAPTER_PROMPT_TEMPLATE = """你是 PlotWeave 剧情织布机的小说写作智能体。
请根据以下小说设定，写出第一章正文。

小说标题：{title}
第一章标题：{chapter_title}
第一章意图：{chapter_intent}
整体剧情：
{plots}

写作要求：
- 必须输出中文小说正文，不要 JSON，不要解释，不要标题之外的说明
- 正文 900 到 1400 个汉字
- 必须有画面感、悬疑推进、人物心理和一个结尾钩子
- 允许分段，但不要使用项目符号
- 开头第一行使用 Markdown 一级标题：# {chapter_title}
"""


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError(f"LLM response does not contain JSON: {text}")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("LLM JSON root must be an object")
    return data


async def call_llm(messages: list[SystemMessage | HumanMessage]) -> str:
    response = await agent.llm.ainvoke(messages)
    if not isinstance(response, AIMessage):
        raise TypeError(f"Unexpected LLM response type: {type(response)!r}")
    if not isinstance(response.content, str):
        raise TypeError("LLM response content is not text")
    return response.content.strip()


async def generate_story_seed() -> tuple[str, dict[str, Any]]:
    raw = await call_llm(
        [
            SystemMessage(content="你是一个中文小说策划智能体。你必须严格按用户要求输出 JSON。"),
            HumanMessage(content=SEED_PROMPT),
        ]
    )
    return raw, extract_json(raw)


async def generate_chapter(seed: dict[str, Any]) -> str:
    plots_text = "\n".join(f"- {plot}" for plot in seed["plots"])
    prompt = CHAPTER_PROMPT_TEMPLATE.format(
        title=seed["title"],
        chapter_title=seed["chapter_title"],
        chapter_intent=seed["chapter_intent"],
        plots=plots_text,
    )
    return await call_llm(
        [
            SystemMessage(content="你是一个擅长悬疑奇幻小说的中文作家。你只输出可直接保存的小说正文。"),
            HumanMessage(content=prompt),
        ]
    )


async def write_chapter_output(
    project: ProjectInstant,
    chapter_index: int,
    chapter_info: ChapterInfo,
    content: str,
) -> Path:
    output_path = Path(project_instant.output_path(project.id, chapter_index, chapter_info))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(output_path, "w", encoding="utf-8") as file:
        await file.write(content.strip() + "\n")
    return output_path


async def run_demo() -> None:
    raw_seed_response, seed = await generate_story_seed()
    chapter_content = await generate_chapter(seed)

    title = str(seed["title"])
    plots = [str(item) for item in seed["plots"]]
    chapter_info = ChapterInfo(
        title=str(seed["chapter_title"]),
        intent=str(seed["chapter_intent"]),
    )

    project = ProjectInstant("Plot Loom Intelligent Demo")
    await project.initialize()
    project.outline = Outline(title=title, plots=plots)
    project.chapter_infos.chapters.append(chapter_info)

    output_path = await write_chapter_output(project, 0, chapter_info, chapter_content)
    await save_to_directory(project)
    await project.close()

    project_dir = Path("datas") / str(project.id)
    reloaded = await load_from_directory(str(project_dir).replace("\\", "/"))
    await reloaded.initialize()

    print("PlotWeave plot loom demo OK")
    print("--- raw_seed_response ---")
    print(raw_seed_response)
    print("--- persisted_project ---")
    print(f"project_id: {reloaded.id}")
    print(f"project_dir: {project_dir}")
    print(f"project_name: {reloaded.metadata.name}")
    print(f"phase: {reloaded.metadata.phase.name}")
    print(f"outline_title: {reloaded.outline.title}")
    print("plots:")
    for index, plot in enumerate(reloaded.outline.plots, start=1):
        print(f"  {index}. {plot}")
    print("chapters:")
    for index, chapter in enumerate(reloaded.chapter_infos.chapters, start=1):
        print(f"  {index}. {chapter.title} - {chapter.intent}")
    print(f"chapter_output_path: {output_path}")
    print("--- novel_excerpt ---")
    print(chapter_content[:1000])

    await reloaded.close()


if __name__ == "__main__":
    asyncio.run(run_demo())
