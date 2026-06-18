"""Compress reference novels into reusable knowledge text.

This script reads whole `.txt`/`.md` files from `reference_novels/`, chunks them,
asks the writer model to extract knowledge-style notes, and saves a compact
reference profile that later generation scripts can use.

Run:
    uv run python reference_compress_demo.py
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from openai import AsyncOpenAI

from config import config


REFERENCE_DIR = Path("reference_novels")
OUTPUT_DIR = Path("outputs/reference_story")
PROFILE_PATH = OUTPUT_DIR / "reference_knowledge_profile.md"
METADATA_PATH = OUTPUT_DIR / "reference_knowledge_metadata.json"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 120


def read_reference_texts() -> list[tuple[str, str]]:
    files = sorted([*REFERENCE_DIR.glob("*.txt"), *REFERENCE_DIR.glob("*.md")])
    texts: list[tuple[str, str]] = []
    for file in files:
        if file.name.lower() == "readme.md":
            continue
        content = file.read_text(encoding="utf-8-sig").strip()
        if content:
            texts.append((file.name, content))
    if not texts:
        raise FileNotFoundError(f"No reference .txt/.md files found in {REFERENCE_DIR}")
    return texts


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


async def call_writer(prompt: str, max_tokens: int = 1200) -> str:
    client = AsyncOpenAI(api_key=config.writer_api_key, base_url=config.writer_base_url)
    response = await client.chat.completions.create(
        model=config.writer_model,
        messages=[
            {
                "role": "system",
                "content": "You are a literary analysis agent. Output concise Simplified Chinese knowledge notes. Do not quote long original passages.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("writer model returned empty analysis")
    return content.strip()


async def analyze_chunk(source: str, index: int, chunk: str) -> str:
    prompt = f"""
Analyze this reference novel chunk and compress it into reusable writing knowledge.
Output in Simplified Chinese. Do not copy more than 20 continuous characters from the source.

Need these sections:
1. 文笔特征
2. 叙事结构
3. 节奏推进
4. 意象/物件/场景
5. 悬念与回收方式
6. 可借鉴但不可照抄的写作规则

source={source}
chunk_index={index}
chunk:
{chunk}
""".strip()
    return await call_writer(prompt)


async def merge_notes(notes: list[str]) -> str:
    joined = "\n\n---\n\n".join(notes)
    prompt = f"""
Merge the following chunk-level analysis notes into one compact reference knowledge profile.
Output Simplified Chinese Markdown.
Do not mention exact source sentences. Make it useful for writing a new original story.

Required sections:
# 参考小说知识压缩画像
## 1. 文笔画像
## 2. 结构规律
## 3. 节奏模式
## 4. 常用意象与物件
## 5. 悬念编织方法
## 6. 情感内核
## 7. 新故事生成注意事项

Notes:
{joined}
""".strip()
    return await call_writer(prompt, max_tokens=1800)


async def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    references = read_reference_texts()
    notes: list[str] = []
    chunk_records: list[dict[str, object]] = []

    for source, text in references:
        chunks = split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for index, chunk in enumerate(chunks):
            note = await analyze_chunk(source, index, chunk)
            notes.append(f"## {source} chunk {index}\n\n{note}")
            chunk_records.append({"source": source, "chunk_index": index, "chars": len(chunk)})

    profile = await merge_notes(notes)
    PROFILE_PATH.write_text(profile + "\n", encoding="utf-8")
    METADATA_PATH.write_text(
        json.dumps(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "reference_dir": str(REFERENCE_DIR),
                "reference_files": [source for source, _ in references],
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "chunk_count": len(chunk_records),
                "writer_model": config.writer_model,
                "profile_path": str(PROFILE_PATH),
                "chunks": chunk_records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("PlotWeave reference compression OK")
    print(f"reference_files: {[source for source, _ in references]}")
    print(f"chunk_count: {len(chunk_records)}")
    print(f"profile_path: {PROFILE_PATH}")
    print("--- profile_preview ---")
    print(profile[:1200])


if __name__ == "__main__":
    asyncio.run(main())
