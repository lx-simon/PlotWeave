"""Reference-novel generation demo with selectable reference modes.

Modes from `reference_mode_config.json`:
- compressed: use the compressed knowledge profile as full-course guidance.
- full: put whole reference text into the prompt, within a char limit.
- hybrid: use compressed guidance plus retrieved chunks. Recommended.

Run:
    uv run python reference_compress_demo.py   # optional but recommended
    uv run python reference_story_demo.py
"""

from __future__ import annotations

import asyncio
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from config import config
import vector


CONFIG_PATH = Path("reference_mode_config.json")
DEFAULT_OUTPUT_DIR = Path("outputs/reference_story")


@dataclass
class Chunk:
    source: str
    index: int
    text: str
    embedding: list[float]


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def read_reference_texts(reference_dir: Path) -> list[tuple[str, str]]:
    files = sorted([*reference_dir.glob("*.txt"), *reference_dir.glob("*.md")])
    texts: list[tuple[str, str]] = []
    for file in files:
        if file.name.lower() == "readme.md":
            continue
        content = file.read_text(encoding="utf-8-sig").strip()
        if content:
            texts.append((file.name, content))
    if not texts:
        raise FileNotFoundError(f"No .txt or .md reference novels found in {reference_dir}")
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


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


async def build_index(reference_dir: Path, chunk_size: int, overlap: int) -> list[Chunk]:
    indexed: list[Chunk] = []
    for source, text in read_reference_texts(reference_dir):
        for index, chunk_text in enumerate(split_text(text, chunk_size, overlap)):
            embedding = await vector.generate_vector(chunk_text)
            if not embedding:
                raise RuntimeError(f"Embedding failed for {source} chunk {index}")
            indexed.append(Chunk(source=source, index=index, text=chunk_text, embedding=embedding))
    return indexed


async def retrieve(chunks: list[Chunk], query: str, top_k: int) -> list[tuple[float, Chunk]]:
    query_embedding = await vector.generate_vector(query)
    if not query_embedding:
        raise RuntimeError("Embedding failed for query")
    scored = [(cosine_similarity(query_embedding, chunk.embedding), chunk) for chunk in chunks]
    return sorted(scored, key=lambda item: item[0], reverse=True)[:top_k]


def load_full_reference_block(reference_dir: Path, char_limit: int) -> str:
    parts: list[str] = []
    total = 0
    for source, text in read_reference_texts(reference_dir):
        remaining = char_limit - total
        if remaining <= 0:
            break
        clipped = text[:remaining]
        parts.append(f"[FULL_REFERENCE source={source}]\n{clipped}")
        total += len(clipped)
    return "\n\n".join(parts)


def load_profile(profile_path: Path) -> str:
    if not profile_path.exists():
        return ""
    return profile_path.read_text(encoding="utf-8-sig").strip()


def build_reference_context(
    mode: str,
    profile: str,
    full_reference: str,
    retrieved: list[tuple[float, Chunk]],
) -> str:
    retrieved_block = "\n\n".join(
        f"[retrieved {rank}] source={chunk.source} chunk={chunk.index} score={score:.4f}\n{chunk.text}"
        for rank, (score, chunk) in enumerate(retrieved, start=1)
    )

    if mode == "compressed":
        return f"[COMPRESSED_GUIDANCE]\n{profile}"
    if mode == "full":
        return f"[FULL_REFERENCE_TEXT]\n{full_reference}"
    if mode == "hybrid":
        return (
            f"[COMPRESSED_GUIDANCE]\n{profile}\n\n"
            f"[RETRIEVED_CHUNKS]\n{retrieved_block}"
        )
    raise ValueError(f"Unsupported reference_mode: {mode}")


async def generate_story(config_data: dict[str, Any], reference_context: str) -> str:
    generation = config_data["generation"]
    retrieval = config_data["retrieval"]
    prompt = f"""
You are PlotWeave, a plot-loom fiction agent.
The following reference context is full-course guidance for a new original story.
Use it for structure, atmosphere, rhythm, motif usage, clue weaving, and emotional movement.
Do not copy source sentences. Do not reuse original character names. Do not imitate any living author's style.

Reference mode: {config_data['reference_mode']}
User writing direction: {retrieval['query']}
Target length: {generation['length_chinese_chars']} Chinese characters
User instruction: {generation['instruction']}

Reference context:
{reference_context}

Output only the new story in Simplified Chinese. First line must be a Markdown H1 title.
""".strip()

    client = AsyncOpenAI(api_key=config.writer_api_key, base_url=config.writer_base_url)
    response = await client.chat.completions.create(
        model=config.writer_model,
        messages=[
            {
                "role": "system",
                "content": "You are a Chinese fiction writing agent. Output only Simplified Chinese prose.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=2600,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Writer model returned empty content")
    return content.strip()


async def main() -> None:
    config_data = load_config()
    paths = config_data["paths"]
    retrieval_cfg = config_data["retrieval"]
    mode = config_data["reference_mode"]

    reference_dir = Path(paths["reference_dir"])
    output_dir = Path(paths.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
    output_dir.mkdir(parents=True, exist_ok=True)

    chunks = await build_index(
        reference_dir,
        int(retrieval_cfg["chunk_size"]),
        int(retrieval_cfg["chunk_overlap"]),
    )
    retrieved = await retrieve(chunks, retrieval_cfg["query"], int(retrieval_cfg["top_k"]))
    profile = load_profile(Path(paths["knowledge_profile"]))
    full_reference = load_full_reference_block(reference_dir, int(config_data["full_text_char_limit"]))
    reference_context = build_reference_context(mode, profile, full_reference, retrieved)
    story = await generate_story(config_data, reference_context)

    story_path = output_dir / f"story_{mode}.md"
    retrieved_path = output_dir / f"retrieved_chunks_{mode}.json"
    metadata_path = output_dir / f"run_metadata_{mode}.json"

    story_path.write_text(story + "\n", encoding="utf-8")
    retrieved_path.write_text(
        json.dumps(
            [
                {
                    "score": score,
                    "source": chunk.source,
                    "chunk_index": chunk.index,
                    "text": chunk.text,
                }
                for score, chunk in retrieved
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "mode": mode,
                "reference_dir": str(reference_dir),
                "query": retrieval_cfg["query"],
                "chunk_count": len(chunks),
                "top_k": retrieval_cfg["top_k"],
                "has_profile": bool(profile),
                "full_reference_chars": len(full_reference),
                "writer_model": config.writer_model,
                "embedding_model": config.vector_model,
                "story_path": str(story_path),
                "retrieved_path": str(retrieved_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("PlotWeave reference story demo OK")
    print(f"mode: {mode}")
    print(f"reference_files: {[source for source, _ in read_reference_texts(reference_dir)]}")
    print(f"chunk_count: {len(chunks)}")
    print(f"has_profile: {bool(profile)}")
    print(f"full_reference_chars: {len(full_reference)}")
    print(f"story_path: {story_path}")
    print(f"retrieved_path: {retrieved_path}")
    print("--- story_preview ---")
    print(story[:1200])


if __name__ == "__main__":
    asyncio.run(main())
