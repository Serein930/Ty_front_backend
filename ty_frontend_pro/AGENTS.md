# ty_frontend_pro — Vue 3 + Vite 前端

**父级：** `../AGENTS.md` — 请先阅读获取项目全局概览

## 概述

天眼情报系统 Vue 3 前端。共五个页面：态势感知（首页）、情报检索、监测预警、取证溯源（拓扑图）、登录。基于组合式 API（`<script setup>`）、TailwindCSS 暗色主题、ECharts 图表和 D3 力导向图构建。

## 目录结构

```
ty_frontend_pro/src/
├── main.js             # 应用入口（创建 Vue 实例、注册路由、全局样式）
├── App.vue             # 根组件（仅含 <router-view>）
├── auth.js             # Mock 认证（localStorage，无后端）
├── router/index.js     # 5 条路由，含认证守卫
├── views/              # 5 个页面视图
│   ├── LoginView.vue   # 登录页（品牌面板 + 登录表单）
│   ├── home.vue        # 态势感知 — 威胁地图、预警、追踪
│   ├── SearchView.vue  # 情报检索 — 关键词搜索 + AI 深度分析
│   ├── DashboardView.vue # 监测预警 — 告警、订阅、统计
│   └── TopologyView.vue # 取证溯源 — D3 知识图谱
├── components/         # 40+ 组件，按模块分组
│   ├── common/         # 通用：AppHeader、Pagination、Toast
│   ├── login/          # 登录：BrandPanel、LoginForm
│   ├── home/           # 首页 20 个组件（PageHeader、CaseList、ThreatMap 等）
│   ├── search/         # 检索 10 个组件（SearchStrip、AISearchPanel、IntelCard 等）
│   ├── dashboard/      # 监测：FilterPanel、AlertCard、StatisticsPanel
│   └── topology/       # 拓扑：TopologyHeader、Filters、Timeline、Sidebar
├── composables/        # 3 个 composable（页面数据逻辑）
├── mock/               # 模拟数据（告警、事件、拓扑）
└── assets/styles/      # CSS 变量 + 各页面样式文件
```

## 该去哪找

| 任务 | 位置 | 备注 |
|------|------|------|
| 新增页面 | `src/views/` + `src/router/index.js` 添加路由 | 参照已有页面的模式 |
| 新增组件 | `src/components/{模块}/` | Vue 3 `<script setup>` SFC。按页面模块分组 |
| 新增数据获取逻辑 | `src/composables/use*.js` | 使用 Vue `ref`/`reactive` 管理状态，导出为 composable |
| 修改认证 | `src/auth.js` | 当前为 Mock——需替换为真实 JWT 认证 |
| 修改主题/颜色 | `tailwind.config.js` + `src/assets/styles/variables.css` | 暗色调色板、发光阴影、语义分类颜色 |
| 修改路由 | `src/router/index.js` | `requiresAuth` meta + `beforeEach` 导航守卫 |
| 添加图表 | 使用 ECharts（首页地图/趋势、监测统计） | `echarts` + `echarts-wordcloud` 已引入 |
| 添加图谱 | 使用 D3.js（拓扑页力导向图） | `d3@7.9.0` 已引入 |
| API 代理 | `vite.config.js` | 将 `/api/*` 代理到 `http://localhost:8888` |

## 约定规范

- **Vue 3 `<script setup>` 专用**：不使用选项式 API。所有组件统一使用组合式 API + `<script setup>` 语法糖
- **Composable 模式**：页面级状态和逻辑抽取到 `src/composables/use*.js`。视图仅为薄封装层，调用 composable。示例：`const { alerts, filters, loading } = useDashboardData()`
- **组件分组**：组件按页面模块分目录（`components/home/`、`components/search/` 等），通用组件放 `common/`
- **CSS 方案**：绝大多数样式使用 Tailwind 工具类。各页面自定义样式放在 `assets/styles/pages/*.css`。主题变量在 `variables.css` 定义
- **Tailwind 设计系统**：
  - 主色：`#00f0ff`（青色发光）
  - 暗色调：`darkBlue: #051029`、`midBlue: #0b1b38`、`lightBlue: #102546`
  - 语义色：`danger: #ff3b30`、`warning: #ffcc00`、`logistics: #007aff`、`material: #bd00ff`、`traffic: #ff9500`、`propaganda: #d946ef`
  - 自定义阴影：`shadow-glow`、`shadow-glow-danger`、`shadow-glow-warning`、`shadow-glow-green`
  - 自定义动画：`pulse-fast`、`spin-slow`
- **Font Awesome 6**：图标系统。使用 `<i class="fas fa-name">` 或 `<FontAwesomeIcon>`（免费版）
- **无 TypeScript**：纯 `.js` 文件，无 `.ts` 配置
- **无测试框架**：前端零测试

## 反模式（前端特有）

1. **Mock 认证在生产代码中**：`auth.js` 硬编码凭证（`Administrator/admin123`、`analyst/123456`）存于 localStorage。无 JWT，无后端认证接口。上线前必须替换
2. **巨型视图**：`DashboardView.vue`（2545 行）和 `SearchView.vue`（1605 行）将 template、script、style 写在同一文件。应拆分为多个子组件，业务逻辑移入 composable
3. **模拟数据到处存在**：`useDashboardData.js` 含时间偏移逻辑保持模拟数据时效。`useSearch.js` 有内联 Mock 回退。后端稳定后应移除模拟数据层
4. **生产代码含 `console.error`**：`SearchView.vue` 有 5 处原始 `console.error()` 调用用于错误处理。应替换为统一的 toast/错误服务或日志 composable
5. **内联样式混用**：部分组件同时使用内联 `style` 绑定和 Tailwind 工具类。应统一以 Tailwind 类为主
6. **组件体量差异大**：部分组件仅 20 行，部分超 400 行且功能过多。应遵循单一职责原则

## 常用命令

```bash
npm run dev       # 启动开发服务器（vite --host，对外开放）
npm run build     # 生产构建 → dist/
npm run preview   # 本地预览生产构建
```

## 注意事项

- **开发代理**：所有 `/api/*` 请求自动代理到 `http://localhost:8888`（后端）。在 `vite.config.js` 配置
- **应用标题**："天眼情报系统"——在 `index.html` 设置
- **无热重载生产保障**：`auth.js` 的 `isAuthenticated()` 使用 `localStorage`。会话在刷新后保留，但不跨标签页
- **Vue Router 5**：使用 `createWebHistory()`（无 `#` 的干净 URL）。生产环境需配置服务端回退
- **D3 拓扑图**：`TopologyView.vue` 使用 D3 力模拟。节点/边数据来自 `mock/topologyData.js`
