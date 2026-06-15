# PlotWeave 最小剧情织布机运行文档

本文档说明当前仓库中最小可运行、且能真实产出小说正文的 demo：`mini_demo.py`。

## 目标

这个 demo 不是空壳，也不是单纯打印固定内容。它会：

1. 调用真实 LLM 生成小说设定 JSON。
2. 再调用真实 LLM 根据设定写出第一章正文。
3. 使用 PlotWeave 原有项目模型保存大纲、章节信息和正文。
4. 从磁盘重新加载项目，证明数据已落盘。
5. 在终端打印大纲、章节意图和正文片段。

## 依赖文件

### 配置入口

- `.env`
  - `WRITER_API_KEY`
  - `WRITER_BASE_URL`
  - `WRITER_MODEL`
  - `VECTOR_API_KEY`
  - `VECTOR_BASE_URL`
  - `VECTOR_MODEL`
  - `VECTOR_DIMENSION`

- `config.py`
  - 通过 `load_dotenv()` 读取 `.env`。
  - 构建全局 `config`。

### LLM 调用链路

- `agent.py`
  - 在模块加载时读取 `config`。
  - 创建 `llm = init_chat_model(...)`。
  - `mini_demo.py` 直接复用 `agent.llm.ainvoke(...)` 调用模型。

### 项目保存链路

- `project_instant.py`
  - `ProjectInstant` 创建项目实例。
  - `save_to_directory` 保存项目。
  - `load_from_directory` 重新读取项目。
  - `output_path` 生成章节正文路径。

- `outline.py`
  - `Outline` 保存小说标题和剧情列表。

- `chapter.py`
  - `ChapterInfo` 保存章节标题和章节意图。

### 输出目录

每次运行会创建一个新项目目录：

```text
datas/<project_id>/
```

目录内包含：

```text
metadata.json
outline.yaml
chapter_infos.yaml
graph.pkl
qdrant/
outputs/00_<chapter_title>.md
```

其中 `outputs/00_<chapter_title>.md` 就是真实模型生成的小说正文。

## 运行命令

在项目根目录执行：

```bash
uv sync
uv run python mini_demo.py
```

## 可选 Python 前端

如果需要浏览器操作最小项目/大纲流程，可先启动后端：

```bash
uv run uvicorn server:app --host 127.0.0.1 --port 8000
```

另开终端启动 Python 前端：

```bash
uv run python mini_frontend.py
```

浏览器打开：

```text
http://127.0.0.1:9000
```

## 当前最小链路和完整项目的关系

这个 demo 故意不走 React/Vite 前端，因为当前环境 Node 版本不足以运行 Vite 7。  
它也不走完整 LangGraph 工具循环，因为最小可运行目标是先证明：

- 模型可调用
- 小说设定可生成
- 小说正文可生成
- PlotWeave 项目文件可保存
- 输出可以在本地复查

后续可以在这个基础上继续接入：

- 世界图谱实体生成
- 向量检索
- 分章 Agent
- 完整写作 Agent
- React 前端或更完整 Python 前端
