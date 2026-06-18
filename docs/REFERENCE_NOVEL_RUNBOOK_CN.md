# PlotWeave 参考整本小说读取与生成说明

这个最小链路用于恢复“读取整本其它小说作为参考”的能力。

## 你要怎么放参考小说

把 `.txt` 或 `.md` 文件放到：

```text
reference_novels/
```

例如：

```text
reference_novels/my_reference_novel.txt
reference_novels/another_reference.md
```

脚本会自动读取该目录下全部 `.txt` 和 `.md` 文件，`README.md` 会被跳过。

## 怎么运行

在项目根目录执行：

```bash
uv run python reference_story_demo.py
```

## 整条链路怎么跑

1. `reference_story_demo.py` 扫描 `reference_novels/`。
2. 读取每一整本 `.txt/.md` 文件。
3. 按 `CHUNK_SIZE=420`、`CHUNK_OVERLAP=80` 切块。
4. 调用 `vector.generate_vector(...)`，使用 OpenRouter embedding：

```text
VECTOR_MODEL=openai/text-embedding-3-small
VECTOR_DIMENSION=1536
```

5. 对用户需求 `QUERY` 做 embedding。
6. 用 cosine similarity 检索最相关片段。
7. 把检索片段交给 qwen 写作模型。
8. 模型只借鉴结构、气氛、线索组织和节奏，不复制原文。
9. 输出新短篇到：

```text
outputs/reference_story/story_from_references.md
```

10. 输出检索片段到：

```text
outputs/reference_story/retrieved_chunks.json
```

11. 输出运行元数据到：

```text
outputs/reference_story/run_metadata.json
```

## 怎么调整参考方向

编辑 `reference_story_demo.py` 顶部：

```python
QUERY = "雨夜旧书店，记忆修补物件，失踪亲人，悬疑奇幻，温暖但留下悬念"
CHUNK_SIZE = 420
CHUNK_OVERLAP = 80
TOP_K = 3
```

- `QUERY`：你想写的故事方向
- `CHUNK_SIZE`：每个参考片段长度
- `CHUNK_OVERLAP`：相邻片段重叠字符数，避免切断上下文
- `TOP_K`：取几个最相关片段给模型参考

## 和“借鉴其它小说”的关系

这个 demo 是“参考式生成”，不是复制式生成：

可以借鉴：

- 叙事结构
- 氛围
- 节奏
- 线索铺陈方式
- 意象组织
- 悬念推进方式

不建议做：

- 直接仿写在世作者风格
- 复制原文句子
- 复刻已有作品剧情
- 复用受保护作品中的独特人物和设定

## 当前已验证结果

已验证成功：

```text
reference_files: ['sample_fog_bell.md']
chunk_count: 2
story_path: outputs\reference_story\story_from_references.md
retrieved_path: outputs\reference_story\retrieved_chunks.json
```
