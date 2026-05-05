# ty_back — FastAPI 后端

**父级：** `../AGENTS.md` — 请先阅读获取项目全局概览

## 概述

Python FastAPI 后端，为威胁情报平台提供服务。提供情报检索、RAG 智能分析、订阅专题管理、告警监控、翻译以及 Milvus 向量库同步等 REST API。

## 目录结构

```
ty_back/app/
├── main.py            # FastAPI 应用入口，路由注册
├── config/            # 配置（ClickHouse、LLM、Milvus、Rerank）+ .env
├── routers/           # API 接口（5 个 router）
├── services/          # 业务逻辑（RAG、LLM、翻译）
├── crud/              # ClickHouse 数据访问（检索、告警）
├── schemas/           # Pydantic 校验模型
├── utils/             # ClickHouse 客户端、MinIO、实体分析器
└── milvus/            # Milvus 子应用（同步、向量化、集合管理）
```

## 该去哪找

| 任务 | 位置 | 备注 |
|------|------|------|
| 新增 REST 接口 | `routers/` + `schemas/` | 使用 APIRouter + prefix，返回 `Result<T>` |
| 新增 Pydantic 模型 | `schemas/` | 按领域分文件（search.py、alert.py、topic.py） |
| 新增业务逻辑 | `services/` | 有状态服务使用单例模式 |
| 新增 ClickHouse 查询 | `crud/` | 通过 `httpx.AsyncClient` 发原始 SQL 到 8123 端口 |
| 修改 LLM 提示词 | `services/llm_service.py` 或 `services/rag_search_service.py` | 兼容 OpenAI 接口，端口 6006 |
| 修改 RAG 管线 | `services/rag_search_service.py` | 查询→改写→Milvus 检索→重排→LLM 生成 |
| 新增 Milvus 集合 | `milvus/service.py` | 向量化通过外部 API（端口 5005，4096 维） |
| 添加测试 | `tests/` | 独立 Python 脚本（非 pytest） |
| 修改配置 | `config/config.py` + `config/.env` | 配置类为单例模式 |

## API 路由总览

| 前缀 | 文件 | 主要接口 |
|------|------|----------|
| `/api/search` | routers/search.py | `GET /unified`（分页检索），`POST /ai-summary`（LLM 研判） |
| `/api/rag` | routers/rag_search.py | `POST /search`，`POST /search/stream`（SSE 流式），历史记录增删查，`/sessions`，`/stats` |
| `/api/topics` | routers/topics.py | `POST /create`，`GET /list`，告警增删查（list、detail、toggle、export） |
| `/api/topics` | routers/translate.py | `POST /translate`，`/translate/stream` |
| `/api/milvus` | milvus/router.py | `GET/POST /sync`，`POST /recreate`，`GET /stats` |

## 约定规范

- **响应格式**：统一为 `{ code: int, msg: str, data: T | null }`，由 `schemas/base.py::Result<T>` 定义。使用 `Result.success(data)` / `Result.error(code, msg)` 工厂方法
- **服务单例**：`RAGSearchService` 和 `TranslationService` 使用 `__new__` 单例。通过模块级实例访问：`from app.services.rag_search_service import rag_search_service`
- **优雅降级**：LLM 调用失败返回 Mock 回复。使用 `generate_ai_summary()` 模式，响应中通过 `mock_used: bool` 标记
- **配置通过环境变量**：所有配置通过 `.env` 文件加载（`python-dotenv`，含手动后备解析器）。配置类（ClickHouseSettings、LLMSettings 等）为模块级实例
- **错误处理**：异常在 Service 层捕获，返回 `Result.error()` 而非向上抛出。Router 层避免裸异常
- **日志**：标准 `logging` 模块，输出到 stdout（在 `main.py` 配置）。运行信息用 `logger.info()`，降级用 `logger.warning()`，异常用 `logger.error()`

## 反模式（后端特有）

1. **`Dict[str, Any]` 作为通用返回类型**：crud/、services/、utils/ 全部返回 `Dict[str, Any]`。应为每种数据形态定义 Pydantic 模型或 TypedDict
2. **字符串拼接 SQL**：`crud/search.py` 仅对单引号转义。无参数化查询。对未过滤的关键词存在 SQL 注入风险
3. **同步/异步混用**：`crud/alert.py` 使用同步 `httpx.Client`，而 `utils/ch_client.py` 使用 `httpx.AsyncClient`。应统一为异步
4. **依赖不完整**：`requirements.txt` 列出 2 个包，但实际依赖约 15+。执行 `pip freeze > requirements.txt` 生成完整依赖清单
5. **巨型文件**：`services/rag_search_service.py` 1139 行——内含初始化、提示词、检索管线、流式生成、历史管理及 `__main__` 测试代码。应按功能拆分为多个模块
6. **`# type: ignore`**：`config/config.py` 第 14 行用于 dotenv 导入。用 `try/except ImportError` 替代
