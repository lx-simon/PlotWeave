# PlotWeave 本地复刻与启动教程（中文）

本教程覆盖：项目架构、代码依赖关系、启动步骤、配置说明、常见问题处理。  
目标是：**在你本机完整复刻并跑通项目（后端 + 前端）**。

---

## 一、项目总览
PlotWeave 是一个以“世界记忆图谱（关系图 + 向量检索）”为核心的小说创作引擎。  
它把创作过程分为阶段（`ProjectPhase`）：
1. 大纲设计（OUTLINE）
2. 世界设定（WORLD_SETUP）
3. 分章（CHAPERING）
4. 章节写作（CHAPER_WRITING）

前端根据阶段推进 UI 流程，后端用 LangGraph Agent 驱动对话与写作任务。

---

## 二、整体架构（代码层面）

### 后端入口与 API
- `server.py`：FastAPI 应用入口，定义所有 REST/SSE API
- `agent.py`：构建对话图（`world_setup_graph` / `chaptering_graph`）
- `writer_agent.py`：构建写作图（计划 → 提议世界修改 → 审查 → 整合写作 → 完成）
- `project_instant.py`：项目实例（内存中）生命周期管理（加载/保存/路径）
- `project_metadata.py`：项目元数据（阶段 `phase`、写到哪章 `writing_chapter_index`）
- `outline.py` / `chapter.py`：大纲与章节信息（YAML 存储）
- `world.py`：世界记忆图谱（NetworkX 图 + Qdrant 向量库）
- `vector.py`：调用向量嵌入接口（OpenAI 兼容 embeddings）
- `config.py`：读取 `.env` 并生成全局 `config` 对象

### 前端入口与页面
- `webui/src/main.tsx`：React 根入口
- `webui/src/App.tsx`：路由配置
- `webui/src/pages/ProjectListPage.tsx`：项目列表（创建/删除/进入）
- `webui/src/pages/OutlinePage.tsx`：大纲编辑（YAML 编辑器）
- `webui/src/pages/WorldSetupPage.tsx`：世界设定（对话式 Agent）
- `webui/src/pages/ChapteringPage.tsx`：分章（对话式 Agent）
- `webui/src/pages/ChapterWritingPage.tsx`：章节写作（写作 Agent + 流式输出）

---

## 三、启动前依赖（必须）
- Python 3.12（`pyproject.toml` 指定 `requires-python >= 3.12`）
- `uv`（用于按 lockfile 安装依赖并运行）
- Node.js 18+（前端）
- Yarn 4（前端包管理，仓库已内置 `.yarnrc.yml`）

---

## 四、配置说明（.env）

后端配置由 `config.py` 读取（会自动 `load_dotenv()`），变量：
- `WRITER_API_KEY` / `WRITER_BASE_URL` / `WRITER_MODEL`：用于主 LLM（OpenAI 兼容接口）
- `VECTOR_API_KEY` / `VECTOR_BASE_URL` / `VECTOR_MODEL`：用于嵌入（OpenAI 兼容 embeddings）
- `VECTOR_DIMENSION`：必须与向量模型实际输出维度一致，否则 Qdrant 建库会失败

### 你提供的 API 信息
- Key: `tp-ce7hux48xtd2umbnfc6kx4a7lteh80gzpagts4eoist4688k`
- URL: `https://token-plan-cn.xiaomimimo.com/v1`
- Model: `mimo-v2.5-pro`

### 推荐写法（根目录 `.env`）
```env
WRITER_API_KEY=tp-ce7hux48xtd2umbnfc6kx4a7lteh80gzpagts4eoist4688k
WRITER_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
WRITER_MODEL=mimo-v2.5-pro

# 向量接口必须支持 embeddings（否则世界记忆相关流程会失败）
VECTOR_API_KEY=your_vector_api_key_here
VECTOR_BASE_URL=https://your-embedding-compatible-endpoint/v1
VECTOR_MODEL=your-embedding-model
VECTOR_DIMENSION=1024
```

> 说明：我已帮你创建 `.env` 文件并写入 WRITER_* 配置；但该接口不提供 embeddings，因此 VECTOR_* 仍需替换为可用服务。

---

## 五、启动步骤（可直接执行）

### 1) 安装后端依赖
```bash
uv sync
```
作用：根据 `pyproject.toml` + `uv.lock` 安装 Python 依赖到 `.venv`。

### 2) 启动后端服务
```bash
uv run uvicorn server:app --host 127.0.0.1 --port 8000
```
作用：启动 FastAPI 服务（默认 8000），所有 API 路由在 `server.py`。

### 3) 安装前端依赖
```bash
cd webui
yarn install
```
作用：安装前端依赖（基于 Yarn 4 配置）。

### 4) 启动前端开发服务
```bash
cd webui
yarn dev
```
作用：启动 Vite 开发服务器（默认 5173），并代理 `/api/*` 到后端 8000。

---

## 六、每一步依赖哪些代码 & 做了什么

### 后端启动阶段
1. `config.py` 加载 `.env`，生成全局配置（writer/vector 参数）
2. `server.py` 创建 FastAPI，并启动后台守护任务清理不活跃项目
3. 首次访问项目接口会触发 `project_instant.load_from_directory` 从磁盘加载
4. 对话与写作由 `agent.py` / `writer_agent.py` 的 LangGraph 图驱动
5. 世界记忆与向量检索在 `world.py` 中使用 Qdrant，向量接口在 `vector.py`

### 前端交互阶段
1. 进入项目页面先调用 heartbeat 接口“激活/加载”项目实例
2. Outline/WorldSetup/Chaptering/ChapterWriting 各页面按阶段调用对应 API
3. 对话类页面通过 SSE（`/api/projects/{id}/chat/stream`）展示 token/tool 事件
4. 写作任务通过 `write/start` 启动后台 Task，再用 `write/stream` 接收写作事件

---

## 七、本地复刻注意
- 必须保证 `.env` 里的向量接口真实可用（embedding 可调用且维度一致）
- 若你只有聊天接口，没有 embeddings：需要额外提供 embedding 服务或替换为兼容 embeddings 的模型/网关
- `datas/` 目录用于本地持久化项目数据（已被 `.gitignore` 排除）
- 项目处于开发中，README 已提示“核心功能仍在开发中”

---

## 八、常见排错
- 启动报 `WRITER_API_KEY/VECTOR_API_KEY/VECTOR_DIMENSION` 未设置：确认 `.env` 在项目根目录
- Qdrant 创建集合/入库报维度问题：确认 `VECTOR_DIMENSION` 与 embedding 模型输出一致
- `/api/*` 404：确认后端已启动且端口是 8000
- 前端无法访问后端：确认用 `yarn dev` 走 Vite 代理（5173 → 8000）

---

## 九、推荐后续
- 为向量服务单独配置可用 embeddings 模型（避免与聊天模型混用导致不兼容）
- 为写作文档增加导出/版本管理能力
- 为世界记忆图谱增加“只读快照/回滚”能力
