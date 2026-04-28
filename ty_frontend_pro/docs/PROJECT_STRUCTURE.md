# 前端项目文件结构总览

> 生成时间：2026-04-28

---

## 一、根目录核心文件

| 文件路径 | 功能说明 |
|---------|---------|
| `src/main.js` | Vue 应用入口文件，创建 Vue 实例，注册全局配置，挂载 App |
| `src/App.vue` | 根组件，包含路由视图 `<router-view>` 和全局布局 |
| `src/style.css` | 全局基础样式（Tailwind CSS 导入等） |
| `src/auth.js` | 认证逻辑模块，处理用户登录/登出、Token 管理 |

---

## 二、路由配置 (`src/router/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `src/router/index.js` | Vue Router 配置，定义所有页面路由规则和导航守卫 |

---

## 三、页面视图 (`src/views/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `src/views/LoginView.vue` | **登录页面** - 用户认证入口 |
| `src/views/home.vue` | **态势感知页面** - 首页仪表盘，展示预警列表、统计概览、威胁地图、实时动态等 |
| `src/views/SearchView.vue` | **情报检索页面** - 支持普通搜索和 AI 深度分析两种模式 |
| `src/views/DashboardView.vue` | **监测预警页面** - 告警信息管理、订阅监测、专题列表 |
| `src/views/TopologyView.vue` | **取证溯源页面** - 知识图谱可视化，D3.js 力导向图展示实体关联 |

---

## 四、公共组件 (`src/components/`)

### 4.1 通用组件 (`src/components/common/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `AppHeader.vue` | 顶部导航栏组件（用于 SearchView 等页面） |
| `Pagination.vue` | 分页器组件 |
| `Toast.vue` | 消息提示组件 |

### 4.2 登录模块组件 (`src/components/login/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `BrandPanel.vue` | 登录页左侧品牌展示面板 |
| `LoginForm.vue` | 登录表单组件（账号密码输入、登录按钮） |

### 4.3 态势感知模块组件 (`src/components/home/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `PageHeader.vue` | 首页顶部导航栏（时间显示、订阅选择、导航菜单） |
| `PageFooter.vue` | 首页底部页脚（版权信息、链接） |
| `CaseList.vue` | **预警案件列表** - 左侧预警卡片列表，支持状态筛选 |
| `CaseCard.vue` | 预警案件卡片组件 |
| `StatsOverview.vue` | **统计概览** - 顶部中央统计数据（预警数、已处理、总数） |
| `PersonTrackList.vue` | **人员轨迹列表** - 右侧重点人员追踪卡片 |
| `PersonCard.vue` | 人员卡片组件 |
| `ThreatMap.vue` | **威胁地图** - 中央地图可视化（ECharts） |
| `TrendChart.vue` | **趋势图表** - 右侧趋势折线图 |
| `MonitoredTicker.vue` | **监测实体滚动条** - 底部横向滚动的监测对象 |
| `LiveFeedCluster.vue` | **实时动态流** - 右下角实时情报滚动列表 |
| `DetailModal.vue` | 详情弹窗（人员/事件详情展示） |
| `EventsListModal.vue` | 事件列表弹窗 |
| `PersonsListModal.vue` | 人员列表弹窗 |
| `OrgListModal.vue` | 组织列表弹窗 |
| `CountryEventsModal.vue` | 国家事件列表弹窗 |
| `CloneWorkspaceModal.vue` | 克隆工作空间弹窗 |
| `MapContextMenu.vue` | 地图右键菜单 |
| `CircleMenu.vue` | 环形菜单（地图交互） |
| `CountryDrawer.vue` | 国家侧边抽屉 |

### 4.4 情报检索模块组件 (`src/components/search/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `SearchLanding.vue` | 搜索落地页（未提交搜索前的初始界面） |
| `SearchStrip.vue` | 顶部搜索条（关键词输入、视图切换、搜索按钮） |
| `SearchFilters.vue` | 筛选面板（时间、地区、风险、媒体、话题等筛选） |
| `SearchSidebar.vue` | 右侧边栏（属性筛选 + 线索篮 + 排行榜） |
| `SearchBasket.vue` | 线索篮组件（已选证据列表、AI 分析按钮） |
| `SearchDetailDrawer.vue` | 详情抽屉（点击卡片后的右侧展开详情） |
| `AISearchPanel.vue` | AI 深度分析面板（左侧 AI 回答 + 右侧参考源） |
| `AccountCard.vue` | 账号类型搜索结果卡片 |
| `PersonCard.vue` | 人物类型搜索结果卡片 |
| `IntelCard.vue` | 情报类型搜索结果卡片 |

### 4.5 监测预警模块组件 (`src/components/dashboard/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `FilterPanel.vue` | 筛选条件面板（时间、危害性、阅读状态、媒体类型、专题） |
| `AlertCard.vue` | 告警卡片组件 |
| `StatisticsPanel.vue` | 右侧统计分析面板 |

### 4.6 取证溯源模块组件 (`src/components/topology/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `TopologyHeader.vue` | 图谱页面顶部工具栏（搜索、布局切换、导出等） |
| `TopologyFilters.vue` | 左侧筛选面板（实体类型、关系类型筛选） |
| `TopologyTimeline.vue` | 时间轴组件（时间范围选择） |
| `TopologySidebar.vue` | 右侧边栏（实体详情、关系统计） |

---

## 五、业务逻辑 composables (`src/composables/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `useHomeData.js` | 态势感知页面数据逻辑（预警数据、人员数据、地图数据、弹窗状态等） |
| `useSearch.js` | 情报检索页面数据逻辑（搜索状态、筛选条件、线索篮、AI 搜索调用等） |
| `useDashboardData.js` | 监测预警页面数据逻辑（告警列表、订阅规则、筛选状态、分页等） |

---

## 六、样式文件 (`src/assets/styles/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `variables.css` | CSS 变量定义（颜色、边框、间距等主题变量） |
| `pages/login.css` | 登录页面专属样式 |
| `pages/home.css` | 态势感知页面样式（Grid 布局、面板样式、地图、趋势图等） |
| `pages/search.css` | 情报检索页面样式（搜索条、结果卡片、AI 面板等） |
| `pages/dashboard.css` | 监测预警页面样式（侧边栏、列表、筛选面板等） |
| `pages/topology.css` | 取证溯源页面样式（D3 节点/连线、力导向图动画等） |

---

## 七、Mock 数据 (`src/mock/`)

| 文件路径 | 功能说明 |
|---------|---------|
| `data.js` | 模拟数据（告警、人员、事件等） |
| `topologyData.js` | 图谱模拟数据（节点、关系数据） |

---

## 八、项目架构树形图

```
ty_frontend_pro/
├── src/
│   ├── main.js                 # 应用入口
│   ├── App.vue                 # 根组件
│   ├── auth.js                 # 认证模块
│   ├── style.css               # 全局样式
│   │
│   ├── router/
│   │   └── index.js            # 路由配置
│   │
│   ├── views/                  # 页面视图（5个主要页面）
│   │   ├── LoginView.vue       # 登录
│   │   ├── home.vue            # 态势感知
│   │   ├── SearchView.vue      # 情报检索
│   │   ├── DashboardView.vue  # 监测预警
│   │   └── TopologyView.vue    # 取证溯源
│   │
│   ├── components/             # 组件库（按模块分组）
│   │   ├── common/             # 通用组件（3个）
│   │   ├── login/              # 登录模块（2个）
│   │   ├── home/               # 态势感知模块（18个）
│   │   ├── search/             # 情报检索模块（10个）
│   │   ├── dashboard/          # 监测预警模块（3个）
│   │   └── topology/          # 取证溯源模块（4个）
│   │
│   ├── composables/            # 业务逻辑 Hook（3个）
│   │   ├── useHomeData.js
│   │   ├── useSearch.js
│   │   └── useDashboardData.js
│   │
│   ├── assets/styles/          # 样式文件
│   │   ├── variables.css       # CSS 变量
│   │   └── pages/              # 页面样式（5个）
│   │
│   └── mock/                   # 模拟数据
│       ├── data.js
│       └── topologyData.js
```

---

## 九、统计

| 类型 | 数量 |
|-----|------|
| 页面视图 | 5 |
| Vue 组件 | 40+ |
| Composables | 3 |
| CSS 文件 | 6 |
| 核心配置文件 | 2 |
| Mock 数据文件 | 2 |

---

## 十、页面与组件对应关系

| 页面 | 主要组件 | Composable |
|-----|---------|------------|
| LoginView | BrandPanel, LoginForm | - |
| home (态势感知) | PageHeader, CaseList, StatsOverview, PersonTrackList, ThreatMap, TrendChart, MonitoredTicker, LiveFeedCluster, PageFooter + 多个弹窗 | useHomeData |
| SearchView | SearchStrip, SearchLanding, SearchFilters, SearchSidebar, SearchBasket, AISearchPanel, AccountCard, PersonCard, IntelCard | useSearch |
| DashboardView | FilterPanel, AlertCard, StatisticsPanel | useDashboardData |
| TopologyView | TopologyHeader, TopologyFilters, TopologyTimeline, TopologySidebar | - |
