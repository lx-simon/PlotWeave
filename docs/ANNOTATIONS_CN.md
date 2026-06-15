# PlotWeave 代码注释索引（中文）

下面是“关键代码位置 + 启动依赖”的注释版索引，方便你从入口一路追到具体行为。

## 后端（Python）
- `config.py:10` `Config` / `config.py:20` `from_env`：读取 `.env`，构建全局配置
- `vector.py:10` `generate_vector`：调用 embedding 接口
- `project_metadata.py:7` `ProjectPhase` / `project_metadata.py:22` `ProjectMetadata`：阶段与元数据
- `project_instant.py:12` `ProjectInstant`：项目实例（world/outline/chapter_infos/metadata）
- `project_instant.py:49` `load_from_directory`：从磁盘加载项目
- `project_instant.py:65` `save_to_directory`：持久化项目到磁盘
- `world.py:140` `World`：世界记忆图谱（NetworkX + Qdrant）
- `world.py:172` `initialize`：初始化 Qdrant collection
- `world.py:186` `add_entity` / `world.py:228` `add_edge`：图与向量入库
- `agent.py:15` `State`：对话图状态
- `agent.py:60` `build_graph`：构建 LangGraph 图
- `writer_agent.py:26` `State`：写作图状态
- `writer_agent.py:140` `build_hint_prompt`：按写作阶段注入提示词
- `writer_agent.py:242` `router_edge`：写作图路由（tools/review/结束）
- `server.py:35` `ActiveProjectManager`：内存中项目实例管理（心跳回收）
- `server.py:130` `lifespan`：FastAPI 生命周期（启动守护任务）
- `server.py:270` `stream_agent_response`：对话 SSE 流
- `server.py:468` `run_writing_agent_in_background`：后台写作任务
- `server.py:558` `stream_writing_progress`：写作 SSE 流

## 前端（React/Vite）
- `webui/src/App.tsx`：路由与页面挂载
- `webui/src/layouts/ProjectLayout.tsx`：项目页心跳与激活（15s）
- `webui/src/components/ProjectSidebar.tsx`：阶段导航与禁用控制
- `webui/src/pages/WorldSetupPage.tsx`：世界设定对话页
- `webui/src/pages/ChapteringPage.tsx`：分章对话页
- `webui/src/pages/ChapterWritingPage.tsx`：章节写作页
