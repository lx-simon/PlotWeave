# PlotWeave 中文教程（含代码注释与依赖说明）

本文档用于在本地完整复刻并运行 PlotWeave，并解释“每一步依赖哪些代码、执行的行为和作用”。

---

## 1. 项目目标
PlotWeave 是一个“以关系图/世界记忆为核心”的 AI 小说创作引擎。  
核心流程：
- 大纲设计（OUTLINE）
- 世界设定（WORLD_SETUP）
- 分章（CHAPERING）
- 章节写作（CHAPER_WRITING）

前端负责交互与阶段推进，后端负责 Agent 编排、世界记忆图谱与章节落盘。

---

## 2. 启动依赖总览（必须）
- Python 3.12（pyproject.toml 指定 `requires-python >= 3.12`）
- uv（用于安装 Python 依赖并运行后端）
- Node.js 18+（前端）
- Yarn 4（前端包管理，仓库已内置 `.yarnrc.yml`）

---

## 3. 配置说明（.env）
后端配置由 `config.py` 读取，会自动 `load_dotenv()`。  
变量：
- `WRITER_API_KEY` / `WRITER_BASE_URL` / `WRITER_MODEL`：用于主 LLM（OpenAI 兼容接口）
- `VECTOR_API_KEY` / `VECTOR_BASE_URL` / `VECTOR_MODEL`：用于 embedding（OpenAI 兼容 embeddings）
- `VECTOR_DIMENSION`：必须与 embedding 模型实际输出维度一致，否则 Qdrant 建库会失败

### 你提供的 API 信息
- Key：`tp-ce7hux48xtd2umbnfc6kx4a7lteh80gzpagts4eoist4688k`
- URL：`https://token-plan-cn.xiaomimimo.com/v1`
- Model：`mimo-v2.5-pro`

建议 `.env`：
- WRITER_* 使用你提供的接口和模型
- VECTOR_* 必须是“真正可调用 embeddings”的服务；如果该接口不支持 embeddings，需要替换为可用服务

---

## 4. 启动步骤（可直接复刻）

### 4.1 安装后端依赖
```bash
uv sync
```
作用：根据 `pyproject.toml` + `uv.lock` 安装 Python 依赖到 `.venv`。

### 4.2 启动后端 API
```bash
uv run uvicorn server:app --host 127.0.0.1 --port 8000
```
作用：启动 FastAPI 服务，所有 API 在 `server.py`。

### 4.3 安装前端依赖
```bash
cd webui
yarn install
```
作用：安装前端依赖（Yarn 4 配置已内置）。

### 4.4 启动前端开发服务
```bash
cd webui
yarn dev
```
作用：启动 Vite 开发服务器（默认 5173），并代理 `/api/*` 到后端 8000。

---

## 5. 每一步依赖哪些代码 & 做了什么

### 5.1 后端启动时
1. `config.py` 加载 `.env`，生成全局配置（writer/vector 参数）
2. `server.py` 创建 FastAPI，并启动后台守护任务清理不活跃项目
3. 首次访问项目接口会触发 `project_instant.load_from_directory` 从磁盘加载
4. 对话与写作由 `agent.py` / `writer_agent.py` 的 LangGraph 图驱动
5. 世界记忆与向量检索在 `world.py` 中使用 Qdrant，向量接口在 `vector.py`

### 5.2 前端交互时
1. 进入项目页面先调用 heartbeat 接口“激活/加载”项目实例
2. Outline/WorldSetup/Chaptering/ChapterWriting 各页面按阶段调用对应 API
3. 对话类页面通过 SSE（`/api/projects/{id}/chat/stream`）展示 token/tool 事件
4. 写作任务通过 `write/start` 启动后台 Task，再用 `write/stream` 接收写作事件

---

## 6. 本地复刻注意
- 必须保证 `.env` 里的向量接口真实可用（embedding 可调用且维度一致）
- 若你只有聊天接口，没有 embeddings：需要额外提供 embedding 服务或替换为兼容 embeddings 的模型/网关
- `datas/` 目录用于本地持久化项目数据（已被 `.gitignore` 排除）
- 项目处于开发中，README 已提示“核心功能仍在开发中”

---

## 7. 常见排错
- 启动报 `WRITER_API_KEY/VECTOR_API_KEY/VECTOR_DIMENSION` 未设置：确认 `.env` 存在于项目根目录
- Qdrant 创建集合/入库报维度问题：确认 `VECTOR_DIMENSION` 与 embedding 模型实际输出一致
- `/api/*` 404：确认后端已启动且端口是 8000
- 前端无法访问后端：确认用 `yarn dev` 走 Vite 代理（5173 → 8000）

---

## 8. 推荐后续
- 为向量服务单独配置可用 embeddings 模型（避免与聊天模型混用导致不兼容）
- 为写作文档增加导出/版本管理能力
- 为世界记忆图谱增加“只读快照/回滚”能力
