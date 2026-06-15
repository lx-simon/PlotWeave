"""Generate a reproducible minimal PlotWeave-style short story.

This script is the smallest end-to-end intelligent demo:
- Reads `minimal_story_config.json`.
- Uses the configured qwen writer model from `.env`.
- Uses OpenRouter embeddings from `.env` to verify semantic-vector capability.
- Generates a complete short Chinese story based on user preferences.
- Saves the story and run metadata under outputs/minimal_story/.

Run:
    uv run python mini_story_demo.py
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from config import config
import vector


CONFIG_PATH = Path("minimal_story_config.json")


def load_story_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def build_prompt(story_request: dict[str, Any]) -> str:
    includes = ", ".join(story_request["must_include"])
    # Use ASCII instructions because this provider handles English prompts more reliably,
    # while still asking the model to output Simplified Chinese prose.
    return f"""
You are PlotWeave, a plot-loom fiction agent.
Write one complete Simplified Chinese short story.

User preferences:
- Title hint: {story_request['title_hint']}
- Genre: {story_request['genre']}
- Reader preference: {story_request['reader_preference']}
- Reference mode: {story_request['reference_mode']}
- Must include: {includes}
- Length: {story_request['length_chinese_chars']} Chinese characters

Rules:
1. Output only the story, no explanation.
2. Use a Markdown H1 title on the first line.
3. Do not imitate any living author's style.
4. You may learn from broad public-domain or genre-level techniques: suspense pacing, object clue, layered reveal, warm emotional resolution.
5. The story must feel like a loom weaving clues: each paragraph should add one thread, and the final paragraph should tie them together while leaving a hook.
""".strip()


async def generate_story(prompt: str) -> str:
    client = AsyncOpenAI(
        api_key=config.writer_api_key,
        base_url=config.writer_base_url,
    )
    response = await client.chat.completions.create(
        model=config.writer_model,
        messages=[
            {
                "role": "system",
                "content": "You are a fiction writing agent. Output only Simplified Chinese prose unless explicitly asked otherwise.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=2200,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("writer model returned empty content")
    return content.strip()


async def main() -> None:
    story_config = load_story_config()
    prompt = build_prompt(story_config["story_request"])
    story = await generate_story(prompt)
    embedding = await vector.generate_vector(story[:500])
    if not embedding:
        raise RuntimeError("embedding model returned empty vector")

    output_dir = Path(story_config["output"]["directory"])
    output_dir.mkdir(parents=True, exist_ok=True)
    story_path = output_dir / story_config["output"]["story_file"]
    metadata_path = output_dir / story_config["output"]["metadata_file"]

    story_path.write_text(story + "\n", encoding="utf-8")
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "writer_base_url": config.writer_base_url,
        "writer_model": config.writer_model,
        "embedding_base_url": config.vector_base_url,
        "embedding_model": config.vector_model,
        "embedding_dimension": len(embedding),
        "story_path": str(story_path),
        "config_path": str(CONFIG_PATH),
        "prompt": prompt,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print("PlotWeave minimal story demo OK")
    print(f"story_path: {story_path}")
    print(f"metadata_path: {metadata_path}")
    print(f"embedding_dimension: {len(embedding)}")
    print("--- story_preview ---")
    print(story[:1200])


if __name__ == "__main__":
    asyncio.run(main())

