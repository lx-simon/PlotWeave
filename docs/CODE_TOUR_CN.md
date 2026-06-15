# PlotWeave 代码走读与启动依赖（中文）

## 一、项目结构总览
PlotWeave = 后端（Python/FastAPI/LangGraph） + 前端（React/Vite）。  
后端负责：项目元数据、世界记忆图谱（NetworkX + Qdrant）、Agent 对话与写作图。  
前端负责：阶段化 UI、SSE 流式展示、大纲编辑、章节编辑。

---

## 二、启动链路（后端）

### 1) 配置加载
- 文件：`config.py`
- 行为：`load_dotenv()` 读取 `.env`，构建全局 `config`
- 影响：`WRITER_*` 决定 LLM，`VECTOR_*` 决定 embedding

### 2) FastAPI 应用与生命周期
- 文件：`server.py`
- 行为：创建 FastAPI `app`，`lifespan` 启动后台守护任务
- 影响：心跳超时回收不活跃项目实例（`ActiveProjectManager.cleanup_task`）

### 3) 项目实例加载/激活
- 文件：`project_instant.py`
- 行为：`ProjectInstant` 持有 world/outline/chapter_infos/metadata
- 影响：首次访问会从 `datas/<uuid>` 加载并初始化资源

### 4) Agent 图（世界设定/分章）
- 文件：`agent.py`
- 行为：`world_setup_graph` / `chaptering_graph` 绑定工具并驱动对话
- 影响：前端 `chat/stream` 接口消费图事件并流式返回

### 5) 写作图
- 文件：`writer_agent.py`
- 行为：状态机（计划→提议→审查→整合写作→完成）+ 工具
- 影响：`write/start` 启动后台任务，`write/stream` 推送写作进度

### 6) 世界记忆与向量检索
- 文件：`world.py` + `vector.py`
- 行为：`World` 用 Qdrant 做向量存储，用 NetworkX 做关系图
- 影响：实体/边的增删改查都会更新图与向量

---

## 三、启动链路（前端）

### 1) 路由与页面
- 文件：`webui/src/App.tsx`
- 行为：`/projects/:projectId` 下挂载 Outline/WorldSetup/Chaptering/ChapterWriting

### 2) 项目激活与心跳
- 文件：`webui/src/layouts/ProjectLayout.tsx`
- 行为：进入项目页先 POST heartbeat，再 15s 轮询保活
- 影响：后端按心跳回收不活跃项目

### 3) 阶段导航与只读控制
- 文件：`webui/src/components/ProjectSidebar.tsx`
- 行为：按 `project.phase` 决定哪些阶段可点、哪些禁用

### 4) 对话流式展示
- 文件：`WorldSetupPage.tsx` / `ChapteringPage.tsx`
- 行为：`/chat/stream` 的 SSE 拆分为 token/thinking/tool_result

### 5) 写作任务流式展示
- 文件：`ChapterWritingPage.tsx`
- 行为：`write/start` 启动任务后，`write/stream` 推送工具调用与内容块

---

## 四、快速启动命令

### 后端
```bash
uv sync
uv run uvicorn server:app --host 127.0.0.1 --port 8000
```

### 前端
```bash
cd webui
yarn install
yarn dev
```

---

## 五、配置建议（基于你提供的 API）
你的 API 可直接用于 WRITER_*（聊天），但该接口不支持 embeddings，因此 VECTOR_* 需替换为可用服务。

建议 `.env`：
- WRITER_* = 你的接口 + `mimo-v2.5-pro`
- VECTOR_* = 专用 embeddings 服务（支持 OpenAI 兼容 embeddings）
- `VECTOR_DIMENSION` = 与 embedding 模型输出维度一致
