# 天眼情报系统 (Tianyan Intelligence System)

**生成时间：** 2026-04-29
**提交：** 221974e
**分支：** main

## 概述

威胁情报平台 Monorepo。后端：Python FastAPI + ClickHouse + Milvus + LLM (Qwen)。前端：Vue 3 + Vite + TailwindCSS + ECharts + D3。界面为中文。

## 目录结构

```
Ty_front_backend/
├── ty_back/              # Python FastAPI 后端
│   └── app/
│       ├── config/       # ClickHouse、LLM、Milvus、Rerank 配置 (.env)
│       ├── routers/      # API 接口 (search, rag_search, topics, translate)
│       ├── services/     # 业务逻辑 (RAG 管线、LLM 调用、翻译)
│       ├── crud/         # ClickHouse 数据访问
│       ├── schemas/      # Pydantic 校验模型
│       ├── utils/        # ClickHouse 客户端、MinIO 处理器、实体分析器
│       └── milvus/       # Milvus 向量库子应用 (同步、向量化、检索)
├── ty_frontend_pro/      # Vue 3 + Vite 前端
│   └── src/
│       ├── views/        # 5 个页面：登录、首页、搜索、监测预警、拓扑
│       ├── components/   # 40+ 组件，按模块分组
│       ├── composables/  # 3 个 composable (useHomeData, useSearch, useDashboardData)
│       ├── router/       # Vue Router 5 (含认证守卫)
│       └── mock/         # 模拟数据 (告警、事件、拓扑)
├── models/               # 本地 ML 模型 (bge-reranker-v2-m3, ~1.1GB)
├── Struct.md             # 后端架构文档（中文，部分过时）
└── docs/                 # 空目录
```

## 该去哪找

| 任务 | 位置 | 备注 |
|------|------|------|
| 新增 API 接口 | `ty_back/app/routers/` + schemas | 模式：router 调 crud/service，返回 `Result<T>` |
| 新增前端页面 | `ty_frontend_pro/src/views/` + `src/router/index.js` | 需添加路由配置 |
| 新增前端功能 | `ty_frontend_pro/src/composables/` | 遵循 Vue 3 `<script setup>` 模式 |
| 修改数据库查询 | `ty_back/app/crud/` | 通过 `httpx` 发送原始 SQL 到 ClickHouse |
| 调整 LLM 提示词 | `ty_back/app/services/llm_service.py` 或 `rag_search_service.py` | 兼容 OpenAI 接口 |
| RAG 管线 | `ty_back/app/services/rag_search_service.py` | 查询→改写→检索→重排→生成 |
| Milvus/向量操作 | `ty_back/app/milvus/` | 子应用，含独立 router/service/crud |
| Tailwind 主题 | `ty_frontend_pro/tailwind.config.js` | 自定义暗色调色板、发光阴影 |
| 认证 | `ty_frontend_pro/src/auth.js` | 仅客户端 Mock，无后端认证 |
| 配置 | `ty_back/app/config/.env` + `config.py` | ClickHouse、LLM、Milvus、Rerank 参数 |

## 约定规范

### 后端
- **Result\<T\> 响应模式**：所有 API 响应通过 `Result(code, msg, data)` 包装（Pydantic 泛型）
- **分层架构**：Router → Service → CRUD → Database。Router 处理 HTTP，Service 处理业务逻辑，CRUD 执行 SQL
- **配置外部化**：所有配置通过 `.env` 环境变量加载，配置类使用单例模式
- **服务单例**：`RAGSearchService` 和 `TranslationService` 使用 `__new__` 单例模式
- **优雅降级**：LLM 调用失败时返回 Mock 回复（见 `_build_mock_reply`）

### 前端
- **Vue 3 `<script setup>` SFC**：仅使用组合式 API，不使用选项式 API
- **Composable 模式**：页面数据逻辑抽取到 `src/composables/use*.js`，视图层调 composable
- **Tailwind 设计系统**：自定义配色（`primary: #00f0ff`、语义分类颜色）。发光阴影。仅暗色主题
- **Font Awesome 6**：图标系统（免费版），无自定义图标组件

### 项目全局
- **无 TypeScript**：前端为纯 JavaScript，无 `.ts`/`.tsx` 文件，无 `tsconfig.json`
- **无 Linter/格式化工具**：未配置 ESLint、Prettier、black、flake8
- **无 CI/CD**：无 GitHub Actions、Dockerfile、部署脚本
- **无正式测试框架**：后端测试为独立 Python 脚本，前端零测试

## 反模式（本项目特有）

1. **`Dict[str, Any]` 泛滥**：Python 后端几乎所有函数返回 `Dict[str, Any]`，实际上绕过了类型检查。应改用 Pydantic 模型或 TypedDict
2. **字符串拼接 SQL**：`crud/search.py` 通过字符串插值拼接 ClickHouse SQL，仅做最基础的转义。应用参数化查询或 ORM
3. **Mock 认证**：`auth.js` 将凭证存于 localStorage。无 JWT，无后端认证接口。上线前必须替换
4. **巨型组件**：`DashboardView.vue`（2545 行）、`SearchView.vue`（1605 行）——单文件包含 template+script+style。应拆分子组件
5. **生产代码含 `console.error`**：`SearchView.vue` 中有 5 处原始 `console.error()` 调用。应使用统一错误上报
6. **不完整的 requirements.txt**：仅列出 `pymilvus` 和 `httpx`，但代码导入了 `langchain`、`langchain_openai`、`langchain_core`、`FlagEmbedding`、`minio`、`FastAPI`、`pydantic` 等

## 常用命令

```bash
# 后端 (Python)
cd ty_back
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8888

# 后端测试（独立脚本，非 pytest）
python ty_back/tests/test_rag_search_test.py
python ty_back/tests/topic_ast_engine_test.py --rules ty_back/tests/rules.json --input ty_back/tests/test_messages.json

# 前端 (Node.js)
cd ty_frontend_pro
npm run dev       # 启动开发服务器（Vite，代理到后端）
npm run build     # 生产构建 → dist/
npm run preview   # 预览生产构建
```

## 注意事项

- **Struct.md 已过时**：引用了已删除的 `routers/intel.py` 和 `routers/debug.py`。当前 router 为：search、rag_search、topics、translate
- **models/ 是 git 子模块**：`models/bge-reranker-v2-m3/` 自含 `.git/`，可能是从 Hugging Face 克隆的
- **空目录**：`docs/`、`ty_back/app/models/` 为空。`ty_back/app/data/` 含一个 19K 行的 JSON 导出文件
- **后端开发服务器端口**：8888（非默认的 8000）。前端 Vite 将 `/api/*` 代理到此端口
- **LLM 模型**：Qwen3.6-35B-A3B（MoE，35B 总参数，3B 激活参数），通过兼容 OpenAI 的接口访问，端口 6006
