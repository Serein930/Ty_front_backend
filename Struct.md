# ty_back 目录结构详细分析

## 一、项目整体架构

`ty_back` 是一个基于 **FastAPI** 框架构建的后端项目，采用经典的**分层架构**设计模式。整个项目围绕**情报数据检索**和 **AI 智能分析**两大核心功能展开。

---

## 二、目录结构详解

```
ty_back/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口，路由注册
│   ├── config/                 # 配置层
│   │   ├── __init__.py
│   │   ├── config.py           # 配置类定义（ClickHouse、LLM）
│   │   └── .env                # 环境变量文件
│   ├── routers/                # 路由层（接口层）
│   │   ├── __init__.py
│   │   ├── intel.py            # 情报数据接口
│   │   ├── search.py           # 全局检索接口
│   │   └── debug.py            # 调试接口
│   ├── services/               # 服务层（业务逻辑层）
│   │   ├── __init__.py
│   │   └── llm_service.py      # LLM 服务（AI 摘要生成）
│   ├── crud/                   # 数据访问层
│   │   ├── __init__.py
│   │   └── search.py           # 搜索相关 CRUD 操作
│   ├── models/                 # 数据模型层
│   │   ├── __init__.py
│   ├── schemas/                # 数据验证层（Pydantic 模型）
│   │   ├── __init__.py
│   │   ├── base.py             # 基础响应结构 Result<T>
│   │   ├── search.py           # 搜索相关 Schema
│   │   └── intel.py            # 情报相关 Schema
│   └── utils/                  # 工具层
│       ├── __init__.py
│       └── ch_client.py        # ClickHouse 异步客户端
├── test_main.http              # API 测试文件
└── .gitignore                  # Git 忽略配置
```

---

## 三、各层功能详解

### 1. **app/main.py** - 应用入口层

这是 FastAPI 应用程序的核心入口文件，负责：
- 创建 FastAPI 应用实例
- 注册路由路由器（routers）
- 定义根路径健康检查接口

**核心代码结构：**

```python
from fastapi import FastAPI
from app.routers import intel, search

app = FastAPI()

# 注册路由前缀为 /api/v1，标签为"情报数据"
app.include_router(intel.router, prefix="/api/v1", tags=["情报数据"])
# 注册搜索路由，标签为"全局检索"
app.include_router(search.router, tags=["全局检索"])

@app.get("/")
async def root():
    return {"message": "Project is running"}
```

---

### 2. **app/config/** - 配置层

配置层采用**单例模式**的设置类，**集中管理**所有第三方服务和数据库连接配置。

#### config.py 核心功能：

- **ClickHouseSettings**：管理 ClickHouse 数据库连接参数
  - `HOST`: 数据库主机地址
  - `PORT`: HTTP 端口（默认 8123）
  - `USER`: 用户名
  - `PASSWORD`: 密码
  - `DATABASE`: 默认数据库（hawkeye）

- **LLMSettings**：管理大语言模型 API 配置
  - `API_BASE`: LLM 服务地址
  - `API_KEY`: API 密钥

- **环境变量加载**：支持从 `.env` 文件加载配置，具有回退机制

---

### 3. **app/routers/** - 路由层（接口层）

路由层是 **API 的 HTTP 接口定义层**，负责接收用户请求、参数验证、调用下层服务、返回响应。

#### intel.py - 情报数据接口

- **路径**：`/api/v1/intel/list`
- **功能**：获取情报列表
- **特点**：
  - 支持 `limit` 和 `keyword` 参数
  - 使用 `Result[T]` 统一响应格式
  - 直接调用 `execute_ch_query` 执行 ClickHouse SQL

#### search.py - 全局检索接口

- **路径**：`/api/search/unified`、`/api/search/ai-summary`
- **功能**：
  - `unified_search`：统一检索（支持分页、类型过滤）
  - `ai_summary`：基于检索结果生成 AI 研判摘要

---

### 4. **app/services/** - 服务层（业务逻辑层）

服务层封装**核心业务逻辑**，是系统的**业务处理中心**。

#### llm_service.py 核心功能：

- **generate_ai_summary()**：调用外部 LLM API 生成智能摘要
  - 支持 OpenAI-compatible 接口
  - 内置错误处理和降级机制（mock 回复）
  - 返回标准化结果包含：摘要文本、模型名称、耗时、错误信息

**设计亮点**：

- 优雅的降级策略：当 LLM 服务不可用时，返回预设的 mock 回复
- 异常捕获：所有 API 调用异常都会被捕获并记录

---

### 5. **app/crud/** - 数据访问层

CRUD 层负责**与数据库交互**，执行 SQL 查询和数据封装。

#### search.py 核心功能：

- **get_search_counts()**：获取各类型检索结果的统计数量
- **get_search_results()**：获取分页的详细检索列表

**设计特点**：

- SQL 注入防护：对 keyword 进行简单转义处理
- 参数化封装：查询逻辑与路由层分离
- 底层调用 `_execute_ch_sql()` 发送原生 SQL 到 ClickHouse

---

### 6. **app/schemas/** - 数据验证层

使用 **Pydantic** 进行数据验证和序列化，是**前后端数据交互的契约**。

#### base.py - 统一响应结构

```python
class Result(BaseModel, Generic[T]):
    code: int           # 状态码
    msg: str            # 消息
    data: Optional[T]   # 数据
```

#### search.py - 搜索相关 Schema

- `SearchTabCount`：Tab 统计数量
- `SearchResultItem`：检索结果项
- `SearchResponse`：完整响应结构

#### intel.py - 情报相关 Schema

定义情报数据项的结构

---

### 7. **app/utils/** - 工具层

工具层提供**通用工具函数和客户端封装**。

#### ch_client.py - ClickHouse 异步客户端

- **execute_ch_query()**：异步执行 ClickHouse 查询
- 使用 `httpx.AsyncClient` 实现异步 HTTP 请求
- 直接调用 ClickHouse HTTP API（端口 8123）

---

## 四、架构设计原则分析

### 1. **分层职责清晰**

```
请求 → Router → Service → CRUD → ClickHouse
                ↓
            Schemas（验证）
                ↓
响应 ← Router ← Service ← 数据
```

### 2. **依赖倒置原则**

- 上层依赖下层抽象（路由依赖服务接口）
- 下层不影响上层（数据库变化不影响业务逻辑）

### 3. **配置外部化**

- 所有敏感信息和配置集中在 config 层
- 支持 .env 文件管理环境变量
- 符合 12-FACTOR App 配置管理原则

### 4. **错误处理统一**

- 使用 `Result<T>` 泛型类统一成功/失败响应
- 异常在服务层捕获，避免向上扩散

---

## 五、数据流向图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端请求                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  app/routers/ - 路由层                                           │
│  • 参数提取与基础验证                                             │
│  • 调用 Service 层处理业务                                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  app/services/ - 服务层（业务逻辑中心）                            │
│  • llm_service.py: AI 摘要生成                                   │
│  • 处理核心业务逻辑                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  app/crud/ - 数据访问层                                          │
│  • search.py: 封装 SQL 查询                                      │
│  • 调用 utils 中的 ClickHouse 客户端                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  app/utils/ - 工具层                                             │
│  • ch_client.py: ClickHouse HTTP 客户端                         │
│  • 发送 SQL 到 ClickHouse 数据库                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ClickHouse 数据库                             │
│                    (hawkeye 数据库)                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、核心模块协作示例

以 **AI 摘要生成** 为例：

1. **客户端** POST `/api/search/ai-summary` 请求
2. **Router**（search.py）接收请求，调用 `crud_search.get_search_results()` 获取数据
3. **CRUD** 层查询 ClickHouse，返回原始数据列表
4. **Router** 构建 prompt，调用 `llm_service.generate_ai_summary()`
5. **Service** 层调用外部 LLM API，生成智能摘要
6. **Router** 组装响应，通过 **Pydantic Schema** 验证后返回
7. **客户端** 收到包含摘要、引用列表、元信息的统一响应

---

## 七、技术栈总结

| 层次 | 技术/框架 | 作用 |
|------|-----------|------|
| Web 框架 | FastAPI | 高性能异步 API 框架 |
| 数据验证 | Pydantic | 请求/响应数据验证 |
| 数据库 | ClickHouse | OLAP 数据库，存储情报数据 |
| LLM | OpenAI-compatible API | AI 摘要生成 |
| HTTP 客户端 | httpx | 异步 HTTP 请求 |
| 配置管理 | python-dotenv | 环境变量加载 |

---

这个架构是一个**简洁但完整**的分层后端项目，核心解决**情报数据检索**和**AI智能分析**两大需求，代码组织清晰，便于维护和扩展。