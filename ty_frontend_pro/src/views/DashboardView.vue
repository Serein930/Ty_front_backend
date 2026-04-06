<template>
  <div class="page-container">
    <AppHeader />
    
    <div class="main-container">
      <aside class="sidebar" :class="{ 'collapsed': state.leftCollapsed }">
        <div class="sidebar-item" :class="{ active: state.activeModule === 'follow' }" @click="switchModule('follow')"><i class="fa-regular fa-heart"></i> <span>我的关注</span></div>
        <div class="sidebar-item" :class="{ active: state.activeModule === 'monitor' }" @click="switchModule('monitor')"><i class="fa-solid fa-desktop"></i> <span>专题监测</span></div>
        <div class="sidebar-item" :class="{ active: state.activeModule === 'subscription' }" @click="switchModule('subscription')"><i class="fa-solid fa-route"></i> <span>订阅监测</span></div>
        <div class="sidebar-item" :class="{ active: state.activeModule === 'topicList' }" @click="switchModule('topicList')"><i class="fa-solid fa-list-ul"></i> <span>专题列表</span></div>
        <div class="sidebar-item" :class="{ active: state.activeModule === 'alerts' }" @click="switchModule('alerts')">
          <i class="fa-solid fa-bell"></i> <span style="flex: 1;">告警信息</span>
          <i class="fa-solid fa-angle-right" style="padding-right:15px;"></i>
        </div>
      </aside>

      <div class="side-toggle-btn left-toggle-btn" :class="{ 'collapsed': state.leftCollapsed }" @click="toggleLeftSidebar" title="收起/展开左侧菜单">
        <i class="fa-solid" :class="state.leftCollapsed ? 'fa-angle-right' : 'fa-angle-left'"></i>
      </div>

      <main class="content-area">
        <div class="module-header-strip">
          <div class="module-title-wrap">
            <div class="module-main-title">{{ activeModuleMeta.title }}</div>
            <div class="module-main-subtitle">{{ activeModuleMeta.subtitle }}</div>
          </div>
          <div class="module-main-count">{{ activeModuleMeta.countText }}</div>
        </div>

        <template v-if="state.activeModule === 'alerts'">
        <div class="filter-panel" :class="{ 'collapsed': state.isFilterCollapsed }">
          <div class="tech-corner-tl"></div><div class="tech-corner-tr"></div>
          <div class="tech-corner-bl"></div><div class="tech-corner-br"></div>

          <div class="panel-header">
            <div class="panel-title">筛选条件</div>
            <div class="panel-actions">
              <button class="primary" @click="saveFilters">保存</button>
              <button @click="resetFilters">重置</button>
            </div>
          </div>

          <div class="filter-content">
            <div class="filter-grid">
              <div class="filter-label">起止时间:</div>
              <div class="filter-options">
                <div class="chip" :class="{ active: filters.time === 'all' }" @click="filters.time = 'all'; state.showCustomDate = false">全部</div>
                <div class="chip" :class="{ active: filters.time === 'today' }" @click="filters.time = 'today'; state.showCustomDate = false">当天</div>
                <div class="chip" :class="{ active: filters.time === '7days' }" @click="filters.time = '7days'; state.showCustomDate = false">近7天</div>
                <div class="chip" :class="{ active: filters.time === '30days' }" @click="filters.time = '30days'; state.showCustomDate = false">近30天</div>
                <div class="time-picker-btn" :class="{ active: state.showCustomDate }" @click="toggleCustomDate">
                  <i class="fa-regular fa-clock" style="margin-right:5px;"></i> 自定义时间
                </div>
                <div class="custom-date-range" :class="{ show: state.showCustomDate }">
                  <input type="date" class="date-input" v-model="filters.customStart">
                  <span>-</span>
                  <input type="date" class="date-input" v-model="filters.customEnd">
                </div>
              </div>

              <div class="filter-label">危害性:</div>
              <div class="filter-options">
                <div class="chip" :class="{ active: filters.risk === 'all' }" @click="filters.risk = 'all'">全部</div>
                <div class="chip" :class="{ active: filters.risk === 'high' }" @click="filters.risk = 'high'">高危</div>
                <div class="chip" :class="{ active: filters.risk === 'mid' }" @click="filters.risk = 'mid'">中危</div>
                <div class="chip" :class="{ active: filters.risk === 'low' }" @click="filters.risk = 'low'">低危</div>
              </div>

              <div class="filter-label">阅 读:</div>
              <div class="filter-options" style="grid-column: span 3;">
                <div class="chip" :class="{ active: filters.read === 'all' }" @click="filters.read = 'all'">全部</div>
                <div class="chip" :class="{ active: filters.read === 'read' }" @click="filters.read = 'read'">已读</div>
                <div class="chip" :class="{ active: filters.read === 'unread' }" @click="filters.read = 'unread'">未读</div>
              </div>

              <div class="filter-label">媒体类型:</div>
              <div class="filter-options" style="grid-column: span 3;">
                <div class="chip" :class="{ active: filters.media === 'all' }" @click="filters.media = 'all'">全部</div>
                <div class="chip" :class="{ active: filters.media === 'Tor' }" @click="filters.media = 'Tor'">Tor</div>
                <div class="chip" :class="{ active: filters.media === 'Telegram' }" @click="filters.media = 'Telegram'">Telegram</div>
                <div class="chip" :class="{ active: filters.media === 'Weibo' }" @click="filters.media = 'Weibo'">微博</div>
                <div class="chip" :class="{ active: filters.media === 'I2P' }" @click="filters.media = 'I2P'">I2P</div>
              </div>

              <div class="filter-label">监测专题:</div>
              <div class="filter-options" style="grid-column: span 3;">
                <div class="chip" :class="{ active: filters.topic === 'all' }" @click="filters.topic = 'all'">全部</div>
                <div v-for="t in availableTopics" :key="t" class="chip" :class="{ active: filters.topic === t }" @click="filters.topic = t">
                  {{ getTopicName(t) }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="toggle-btn" @click="state.isFilterCollapsed = !state.isFilterCollapsed">
            <i class="fa-solid" :class="state.isFilterCollapsed ? 'fa-angle-down' : 'fa-angle-up'"></i>
          </div>
        </div>

        <div class="content-body">
          <div class="list-section">
            
            <div class="list-toolbar">
              <div class="toolbar-left">
                <label><input type="checkbox" v-model="state.selectAll" @change="toggleSelectAll"> 全选</label>
                <div class="select-box" :class="{ open: state.isSortDropdownOpen }" @click="state.isSortDropdownOpen = !state.isSortDropdownOpen">
                  <i :class="sortIcon"></i> {{ sortText }}
                  <i class="fa-solid fa-caret-down" style="margin-left: auto; font-size: 12px;"></i>
                  <div class="select-dropdown">
                    <div class="select-option" :class="{ active: state.sort === 'time-desc' }" @click.stop="changeSort('time-desc')"><i class="fa-solid fa-arrow-down-wide-short"></i> 时间最新</div>
                    <div class="select-option" :class="{ active: state.sort === 'time-asc' }" @click.stop="changeSort('time-asc')"><i class="fa-solid fa-arrow-up-wide-short"></i> 时间最旧</div>
                    <div class="select-option" :class="{ active: state.sort === 'risk-desc' }" @click.stop="changeSort('risk-desc')"><i class="fa-solid fa-triangle-exclamation"></i> 危害等级降序</div>
                    <div class="select-option" :class="{ active: state.sort === 'risk-asc' }" @click.stop="changeSort('risk-asc')"><i class="fa-solid fa-triangle-exclamation" style="transform: rotate(180deg);"></i> 危害等级升序</div>
                  </div>
                </div>
                <div id="activeFilterHint" style="font-size:12px; color:var(--accent-blue);" v-html="activeFilterHint"></div>
              </div>

              <div class="toolbar-right">
                <button class="immersive-btn" :class="{ active: state.isImmersive }" @click="toggleImmersiveMode">
                  <i class="fa-solid" :class="state.isImmersive ? 'fa-compress' : 'fa-expand'"></i> {{ state.isImmersive ? '退出沉浸' : '沉浸模式' }}
                </button>
                <input type="text" v-model="state.searchQuery" class="search-input" placeholder="请输入搜索关键词...">
                <button class="export-btn" :disabled="!hasSelected" @click="exportSelected">
                  <i class="fa-solid fa-download"></i> 导出选中
                </button>
                <button class="manage-btn" @click="exportAll">
                  <i class="fa-solid fa-file-export"></i> 导出全部
                </button>
              </div>
            </div>

            <div class="list-container">
              <div v-for="item in paginatedList" :key="item.id" class="list-item-wrapper" style="margin-bottom: 10px;">
                <div class="list-item unified-card" :class="{ 'read': item.read, 'selected': item.selected, 'is-telegram': item.source === 'Telegram' }" @click="markAsRead(item)">
                  <div class="checkbox-area"><input type="checkbox" v-model="item.selected" @click.stop></div>
                  <div class="item-content">
                    <div class="item-header">
                      <div class="item-title-wrap">
                        <i class="item-source-icon fa-solid" :class="getSourceIcon(item.source)"></i>
                        <span class="item-title">{{ getDisplayTitle(item) }}</span>
                      </div>
                      <span class="badge" :class="item.risk">{{ getRiskText(item.risk) }}</span>
                    </div>
                    <div class="item-desc">{{ item.content }}</div>
                    <div class="item-meta">
                      <span class="meta-item clickable-author" title="点击查看该作者所有动态" @click.stop="toggleSidebarFilter('author', item.author)">
                        作者：<span class="meta-value">{{ item.author }}</span>
                      </span>
                      <span class="meta-item">
                        来自：<span class="meta-value">{{ item.source }}</span>
                      </span>
                      <span v-if="item.siteName" class="meta-item">
                        {{ getSiteLabel(item) }}：<span class="meta-value">{{ item.siteName }}</span>
                      </span>
                      <span class="item-meta-time">{{ formatTime(item.date) }}</span>
                    </div>
                    <div class="tag-row">
                      <div class="tag clickable-tag" @click.stop="toggleSidebarFilter('region', item.region)"><i class="fa-solid fa-location-dot"></i> {{ getProvince(item.region) }}</div>
                      <div class="tag clickable-tag tag-topic" @click.stop="toggleSidebarFilter('topic', item.topic)"><i class="fa-solid fa-tag"></i> {{ getTopicName(item.topic) }}</div>
                      <div class="tag clickable-tag tag-industry" @click.stop="toggleSidebarFilter('industry', item.industry)">{{ getIndustryName(item.industry) }}</div>
                      <span v-for="(ent, index) in item.entities" :key="index" class="entity-tag" :class="getEntityClass(ent.type)" @click.stop>
                        <i :class="getEntityIcon(ent.type)"></i> {{ ent.value }}
                      </span>
                    </div>
                    <div class="item-stats flex items-center" v-if="item.children && item.children.length">
                      <button class="cluster-toggle-btn" :class="{ open: item.isExpanded }" @click.stop="item.isExpanded = !item.isExpanded">
                        <i class="fa-solid fa-layer-group"></i> {{ item.isExpanded ? '收起' : '展开' }} {{ item.children.length }} 条相似线索
                        <i class="fa-solid fa-chevron-down ml-1"></i>
                      </button>
                    </div>
                  </div>
                  <div class="item-actions">
                    <button class="fp-btn" @click.stop="markFalsePositive(item)"><i class="fa-solid fa-ban"></i> 误报</button>
                    <button class="translate-btn" @click.stop="mockTranslate"><i class="fa-solid fa-language"></i> 翻译</button>
                    <button class="export-item-btn" @click.stop="exportSingle(item)"><i class="fa-solid fa-download"></i> 导出</button>
                    <button class="detail-btn" @click.stop="openDetail(item)"><i class="fa-solid fa-eye"></i> 详情</button>
                  </div>
                </div>

                  <div class="nested-alerts-container" :class="{ show: item.isExpanded }">
                    <div v-for="child in item.children" :key="child.id" class="nested-item">
                      <div class="nested-header">
                        <span class="text-white font-bold"><i class="fa-solid fa-reply text-gray-500 mr-1"></i>{{ child.author }}</span>
                        <span class="text-gray-500 font-mono">{{ child.date }}</span>
                      </div>
                      <div class="nested-content">{{ child.content }}</div>
                      <div class="mt-2 text-right">
                        <button class="detail-btn py-0.5 px-2 text-[10px]" @click.stop="openDetail(child, item)">独立查看</button>
                      </div>
                    </div>
                  </div>

              </div>
              
              <div v-if="paginatedList.length === 0" style="text-align:center; padding:40px; color:var(--text-dim);">没有找到符合条件的数据</div>
            </div>

            <div class="pagination" v-if="totalPages > 0">
              <i class="fa-solid fa-angle-left page-arrow" @click="changePage(state.pagination.currentPage - 1)"></i>
              <div class="page-num" :class="{ active: state.pagination.currentPage === 1 }" @click="changePage(1)">1</div>
              <span v-if="state.pagination.currentPage > 3">...</span>
              
              <template v-for="p in totalPages">
                <div v-if="p !== 1 && p !== totalPages && Math.abs(p - state.pagination.currentPage) <= 1" :key="p"
                     class="page-num" :class="{ active: p === state.pagination.currentPage }" @click="changePage(p)">
                  {{ p }}
                </div>
              </template>

              <span v-if="state.pagination.currentPage < totalPages - 2">...</span>
              <div v-if="totalPages > 1" class="page-num" :class="{ active: state.pagination.currentPage === totalPages }" @click="changePage(totalPages)">{{ totalPages }}</div>
              <i class="fa-solid fa-angle-right page-arrow" @click="changePage(state.pagination.currentPage + 1)"></i>
              <div class="page-info">第 {{ state.pagination.currentPage }}/{{ totalPages }} 页，共 {{ filteredList.length }} 条数据</div>
            </div>
          </div> 
          
          <div class="side-toggle-btn right-toggle-btn" :class="{ 'collapsed': state.rightCollapsed }" @click="toggleRightSidebar" title="收起/展开分析栏">
            <i class="fa-solid" :class="state.rightCollapsed ? 'fa-angle-left' : 'fa-angle-right'"></i>
          </div>

          <aside class="analysis-sidebar" :class="{ 'collapsed': state.rightCollapsed }">
            <div class="analysis-header">
              <div class="time-tabs">
                <div class="time-tab" :class="{ active: filters.time === 'today' }" @click="filters.time = 'today'">24H</div>
                <div class="time-tab" :class="{ active: filters.time === '7days' }" @click="filters.time = '7days'">7天</div>
                <div class="time-tab" :class="{ active: filters.time === '30days' }" @click="filters.time = '30days'">30天</div>
                <div class="time-tab" :class="{ active: filters.time === 'all' }" @click="filters.time = 'all'">全部</div>
              </div>
              <i class="fa-regular fa-calendar-days text-gray-400"></i>
            </div>

            <select class="region-select" v-model="filters.region">
              <option value="all">所有地区</option>
              <option v-for="r in availableRegions" :key="r" :value="r">{{ r }}</option>
            </select>

            <div>
              <div class="module-title"><i class="fa-solid fa-location-dot"></i> 地区分布</div>
              <div class="region-rank-container">
                <div class="region-rank-wrapper">
                  <div class="region-rank-slide" :style="{ transform: `translateY(-${state.carousel.region * 180}px)` }">
                    <div v-for="(region, index) in topRegions" :key="region.name" class="rank-item" :class="{ active: filters.region === region.name }" @click="toggleSidebarFilter('region', region.name)">
                      <div class="rank-num">{{ index + 1 < 10 ? '0' + (index + 1) : index + 1 }}</div> 
                      <div class="rank-name" style="color:var(--text-main); font-size:12px; min-width:60px;">{{ region.name }}</div>
                      <div class="progress-bg">
                        <div class="progress-bar" :style="{ width: region.percent + '%', background: getRegionColor(index) }"></div>
                      </div>
                      <span style="font-size:11px; color:var(--text-dim); margin-left:5px;">{{ region.count }}</span>
                    </div>
                  </div>
                </div>
                <div class="carousel-arrow prev" @click="prevRegionSlide"><i class="fa-solid fa-chevron-left"></i></div>
                <div class="carousel-arrow next" @click="nextRegionSlide"><i class="fa-solid fa-chevron-right"></i></div>
              </div>
            </div>

            <div>
              <div class="module-title"><i class="fa-solid fa-filter"></i> 命中规则 Top 5</div>
              <div class="region-rank-container" style="height: auto;">
                <div v-for="(rule, index) in topRules" :key="rule.name" class="rank-item" :class="{ active: filters.rule === rule.name }" @click="toggleSidebarFilter('rule', rule.name)" style="margin-bottom: 12px;">
                  <div class="rank-num" style="background: rgba(59,130,246,0.2); border-color: var(--accent-blue);">{{ index + 1 }}</div> 
                  <div style="flex:1; display:flex; flex-direction:column; gap:4px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px;"><span style="color:var(--text-main);">{{ getRuleName(rule.name) }}</span><span style="color:var(--text-dim)">{{ rule.count }}</span></div>
                    <div class="progress-bg" style="height:4px;"><div class="progress-bar" :style="{ width: rule.percent + '%', background: 'var(--accent-orange)' }"></div></div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <div class="module-title"><i class="fa-regular fa-comment-dots"></i> 话题过滤</div>
              <div class="chart-container">
                <div class="donut-chart" :style="{ background: topicChartData.background }">
                  <div class="donut-inner"><span class="donut-label">{{ topicChartData.total }}</span><span class="donut-sub">Total</span></div>
                </div>
              </div>
              <div class="chart-legend">
                <div v-for="item in topicChartData.legend" :key="item.key" class="legend-item" :class="{ active: filters.topic === item.key }" @click="toggleSidebarFilter('topic', item.key)">
                  <div class="legend-dot" :style="{ background: item.color }"></div> {{ item.name }} ({{ item.count }})
                </div>
              </div>
            </div>

            <div>
              <div class="module-title"><i class="fa-solid fa-tag"></i> 行业分布</div>
              <div class="chart-container">
                <div class="donut-chart" :style="{ background: industryChartData.background }">
                  <div class="donut-inner"><span class="donut-label">{{ industryChartData.total }}</span><span class="donut-sub">Ind</span></div>
                </div>
              </div>
              <div class="chart-legend">
                <div v-for="item in industryChartData.legend" :key="item.key" class="legend-item" :class="{ active: filters.industry === item.key }" @click="toggleSidebarFilter('industry', item.key)">
                  <div class="legend-dot" :style="{ background: item.color }"></div> {{ item.name }} ({{ item.count }})
                </div>
              </div>
            </div>

            <div>
              <div class="module-title"><i class="fa-solid fa-user-pen"></i> 作者统计</div>
              <div class="author-list-container">
                <div class="author-list-wrapper">
                  <div class="author-list-slide" :style="{ transform: `translateY(-${state.carousel.author * 230}px)` }">
                    <div v-for="(author, index) in topAuthors" :key="author.name" class="author-list-item" :class="{ active: filters.author === author.name }" @click="toggleSidebarFilter('author', author.name)">
                      <div class="author-rank-num">{{ index + 1 }}</div>
                      <div class="author-name">{{ author.name }}</div>
                      <div class="author-count">{{ author.count }}<span class="author-count-unit">条</span></div>
                    </div>
                  </div>
                </div>
                <div class="carousel-arrow prev" @click="prevAuthorSlide"><i class="fa-solid fa-chevron-left"></i></div>
                <div class="carousel-arrow next" @click="nextAuthorSlide"><i class="fa-solid fa-chevron-right"></i></div>
              </div>
            </div>
          </aside>
        </div>
        </template>

        <template v-else-if="state.activeModule === 'follow'">
          <div class="board-grid board-follow">
            <div class="summary-card">
              <div class="summary-item">
                <div class="summary-label">关注对象</div>
                <div class="summary-value">{{ followSummary.total }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">高危对象</div>
                <div class="summary-value danger">{{ followSummary.high }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">24H 新增线索</div>
                <div class="summary-value">{{ followSummary.alerts24h }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">已静默对象</div>
                <div class="summary-value mute">{{ followSummary.muted }}</div>
              </div>
            </div>

            <div class="panel board-panel">
              <div class="panel-line-title"><i class="fa-regular fa-heart"></i> 我的关注清单</div>
              <div class="follow-list">
                <div v-for="item in followList" :key="item.id" class="follow-card" :class="[{ muted: item.muted }, `risk-${item.risk}`]" @click="openFollowInAlerts(item)">
                  <div class="follow-head">
                    <div>
                      <div class="follow-name">{{ item.name }}</div>
                      <div class="follow-meta">{{ item.type }} · 最近活跃 {{ item.lastSeen }}</div>
                    </div>
                    <span class="risk-dot" :class="item.risk">{{ getRiskText(item.risk) }}</span>
                  </div>

                  <div class="follow-tags">
                    <span v-for="p in item.platforms" :key="`${item.id}-${p}`" class="mini-tag">{{ p }}</span>
                  </div>

                  <div class="follow-progress-row">
                    <span>关注热度</span>
                    <div class="progress-bg"><div class="progress-bar" :style="{ width: `${item.heat}%` }"></div></div>
                    <span>{{ item.heat }}%</span>
                  </div>

                  <div class="follow-foot">
                    <span>24H 告警：<b>{{ item.alerts24h }}</b></span>
                    <div class="follow-actions">
                      <button class="chip-btn" @click.stop="toggleFollowMute(item)">{{ item.muted ? '取消静默' : '静默' }}</button>
                      <button class="chip-btn primary" @click.stop="openFollowInAlerts(item)">查看告警</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="state.activeModule === 'monitor'">
          <div class="board-grid">
            <div class="summary-card">
              <div class="summary-item">
                <div class="summary-label">运行中专题</div>
                <div class="summary-value">{{ monitorSummary.running }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">暂停专题</div>
                <div class="summary-value mute">{{ monitorSummary.paused }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">24H 命中总量</div>
                <div class="summary-value">{{ monitorSummary.hits24h }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">待复核任务</div>
                <div class="summary-value danger">{{ monitorSummary.pending }}</div>
              </div>
            </div>

            <div class="panel board-panel">
              <div class="panel-line-title"><i class="fa-solid fa-desktop"></i> 专题监测任务</div>
              <div class="monitor-table">
                <div v-for="item in monitorTopics" :key="item.id" class="monitor-row" @click="openMonitorInAlerts(item)">
                  <div class="monitor-main">
                    <div class="monitor-title">{{ item.name }}</div>
                    <div class="monitor-meta">来源：{{ item.sources.join(' / ') }} · 周期：{{ item.schedule }}</div>
                    <div class="monitor-progress">
                      <span>覆盖度</span>
                      <div class="progress-bg"><div class="progress-bar warning" :style="{ width: `${item.coverage}%` }"></div></div>
                      <span>{{ item.coverage }}%</span>
                    </div>
                  </div>
                  <div class="monitor-side">
                    <span class="status-badge" :class="item.status === '运行中' ? 'on' : 'off'">{{ item.status }}</span>
                    <span class="monitor-hit">24H: {{ item.hits24h }}</span>
                    <span class="monitor-pending">待复核: {{ item.pendingReview }}</span>
                    <div class="monitor-actions">
                      <button class="chip-btn" @click.stop="toggleMonitorStatus(item)">{{ item.status === '运行中' ? '暂停' : '启动' }}</button>
                      <button class="chip-btn primary" @click.stop="runMonitorNow(item)">立即运行</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="state.activeModule === 'subscription'">
          <div class="board-grid subscription-grid">
            <div class="cfg3-shell">
              <section class="cfg3-left panel board-panel">
                <div class="cfg3-left-head">
                  <div class="panel-line-title"><i class="fa-solid fa-layer-group"></i> 订阅规则</div>
                  <button class="chip-btn primary" @click="createSubscriptionRule"><i class="fa-solid fa-plus"></i> 新建</button>
                </div>
                <div class="sub-list-toolbar">
                  <input v-model="subscriptionState.search" class="sub-input sub-search" placeholder="搜索：名称 / 专题 / 负责人 / 分发对象">
                </div>
                <div class="sub-rule-list">
                  <div
                    v-for="rule in filteredSubscriptionRules"
                    :key="rule.id"
                    class="sub-rule-item"
                    :class="{ active: rule.id === subscriptionState.selectedId }"
                    @click="selectSubscriptionRule(rule.id)">
                    <div class="sub-rule-top">
                      <div class="sub-rule-title">{{ rule.name || '未命名规则' }}</div>
                      <span class="status-badge" :class="rule.enabled ? 'on' : 'stop'">{{ rule.enabled ? '启用' : '停用' }}</span>
                    </div>
                    <div class="sub-rule-meta">{{ (rule.topics || []).length }} 专题 ｜ ≥ {{ rule.minSeverity }}</div>
                    <div class="sub-rule-meta">{{ rule.status === 'applied' ? '已发布' : '草稿' }}</div>
                    <div class="sub-rule-foot">
                      <span>{{ rule.schedule }}</span>
                      <span>{{ rule.owner || 'SystemAdmin' }}</span>
                    </div>
                  </div>
                </div>
              </section>

              <section class="cfg3-main panel board-panel">
                <div class="cfg3-toolbar">
                  <div class="cfg3-toolbar-title">
                    <i class="fa-solid fa-sliders"></i>
                    <span>规则编排工作台</span>
                  </div>
                  <div class="cfg3-toolbar-actions">
                    <button class="cfg3-btn ghost" @click="alertMock('版本历史即将开放')"><i class="fa-solid fa-clock-rotate-left"></i>版本历史</button>
                    <button class="cfg3-btn danger" @click="deleteSubscriptionRule"><i class="fa-solid fa-trash-can"></i>删除</button>
                    <button class="cfg3-btn ghost" @click="saveSubscriptionDraft"><i class="fa-solid fa-floppy-disk"></i>保存草稿</button>
                    <button class="cfg3-btn primary" @click="publishSubscriptionRule"><i class="fa-solid fa-bolt"></i>发布应用</button>
                  </div>
                </div>

                <div class="cfg3-headline">
                  <div>
                    <div class="cfg3-title-edit">
                      <input
                        v-if="subscriptionState.titleEditing"
                        v-model="subscriptionEditor.name"
                        class="cfg3-title-input"
                        @blur="finishSubscriptionTitleEdit"
                        @keyup.enter="finishSubscriptionTitleEdit"
                        @keyup.esc="cancelSubscriptionTitleEdit"
                        placeholder="请输入订阅主题标题">
                      <h3 v-else @click="startSubscriptionTitleEdit">{{ subscriptionEditor.name || '高危涉毒自动化分发 (Demo)' }}</h3>
                      <button v-if="!subscriptionState.titleEditing" class="cfg3-title-edit-btn" @click="startSubscriptionTitleEdit" title="编辑标题">
                        <i class="fa-solid fa-pen"></i>
                      </button>
                    </div>
                    <p>
                      草稿保存：{{ selectedSubscriptionRule?.updatedAt || '-' }}
                      <span class="cfg3-divider">|</span>
                      状态：{{ selectedSubscriptionRule?.status === 'applied' ? '已发布' : '草稿' }}
                    </p>
                  </div>
                  <select v-model="subscriptionEditor.enabled" class="cfg3-enable-select" :class="subscriptionEditor.enabled ? 'is-enabled' : 'is-disabled'">
                    <option :value="true">启用</option>
                    <option :value="false">停用</option>
                  </select>
                  <span class="cfg3-enable-tag" :class="subscriptionEditor.enabled ? 'enabled' : 'disabled'">{{ subscriptionEditor.enabled ? '启用中' : '已停用' }}</span>
                </div>

                <div class="cfg3-steps">
                  <button class="cfg3-step" :class="{ active: subscriptionState.step === 1 }" @click="subscriptionState.step = 1">
                    <small>步骤 1</small><b>识别条件</b><span>业务向导模式</span><i class="cfg3-step-dot"></i>
                  </button>
                  <button class="cfg3-step" :class="{ active: subscriptionState.step === 2 }" @click="subscriptionState.step = 2">
                    <small>步骤 2</small><b>降噪治理</b><span>去重: 关闭, 频控: 50/h</span><i class="cfg3-step-dot"></i>
                  </button>
                  <button class="cfg3-step" :class="{ active: subscriptionState.step === 3 }" @click="subscriptionState.step = 3">
                    <small>步骤 3</small><b>分发对象</b><span>已配置接收渠道</span><i class="cfg3-step-dot"></i>
                  </button>
                  <button class="cfg3-step" :class="{ active: subscriptionState.step === 4 }" @click="subscriptionState.step = 4">
                    <small>步骤 4</small><b>元数据与权限</b><span>负责人: {{ subscriptionEditor.owner || 'SystemAdmin' }}</span><i class="cfg3-step-dot"></i>
                  </button>
                </div>

                <div v-if="subscriptionState.step === 1" class="cfg3-step-pane">
                  <div class="cfg3-mode-switch">
                    <button class="active"><i class="fa-solid fa-gem"></i> 业务向导模式</button>
                    <button><i class="fa-solid fa-code-branch"></i> 专家 AST 模式</button>
                  </div>

                  <div class="cfg3-section-title"><i class="fa-solid fa-bookmark"></i> 快速订阅情报大盘专题</div>
                  <div class="cfg3-topic-grid">
                    <button
                      v-for="topic in SUBSCRIPTION_TOPICS"
                      :key="topic.id"
                      class="cfg3-topic"
                      :class="{ active: subscriptionEditor.topics.includes(topic.id) }"
                      @click="subscriptionEditor.topics = subscriptionEditor.topics.includes(topic.id) ? subscriptionEditor.topics.filter(t => t !== topic.id) : [...subscriptionEditor.topics, topic.id]">
                      <i class="fa-solid" :class="topic.id === 'TopicDrugs' ? 'fa-capsules' : topic.id === 'TopicSmuggle' ? 'fa-person-walking-luggage' : topic.id === 'TopicTerror' ? 'fa-bomb' : topic.id === 'TopicDataLeak' ? 'fa-database' : topic.id === 'TopicTaiwan' ? 'fa-map-location-dot' : 'fa-bug'"></i>
                      <span>{{ topic.name }}</span>
                    </button>
                  </div>

                  <div class="cfg3-form-grid">
                    <div class="cfg3-field">
                      <label><i class="fa-solid fa-triangle-exclamation"></i> 最低接收危害等级</label>
                      <select v-model="subscriptionEditor.minSeverity" class="sub-select">
                        <option value="CRITICAL">CRITICAL</option>
                        <option value="HIGH">HIGH</option>
                        <option value="MEDIUM">MEDIUM</option>
                        <option value="LOW">LOW</option>
                      </select>
                    </div>
                    <div class="cfg3-field">
                      <label><i class="fa-solid fa-chart-line"></i> 风险分数阈值</label>
                      <input v-model.number="subscriptionEditor.riskMin" class="sub-input" type="number" min="0" max="100" placeholder="如: 70">
                    </div>
                  </div>

                  <div class="cfg3-form-grid">
                    <div class="cfg3-field">
                      <label><i class="fa-solid fa-map-pin"></i> 地域关注</label>
                      <input v-model="subscriptionEditor.regionFocus" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本">
                    </div>
                    <div class="cfg3-field">
                      <label><i class="fa-solid fa-tags"></i> 业务标签关注 (智能适配专题)</label>
                      <input v-model="subscriptionEditor.bizTagFocus" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本">
                    </div>
                  </div>
                </div>

                <div v-else-if="subscriptionState.step === 2" class="cfg3-step-pane">
                  <div class="cfg3-note-box">治理层决定“最终送达多少条”。频控按小时桶独立计算，去重窗口按真实事件时间连续计算，不会在跨小时清空。</div>
                  <div class="cfg3-form-grid">
                    <div class="cfg3-field">
                      <label>去重键 (Deduplication Key)</label>
                      <select v-model="subscriptionEditor.dedupKey" class="sub-select">
                        <option value="不过滤 (每条独立推送)">不过滤 (每条独立推送)</option>
                        <option value="作者+主题">作者+主题</option>
                        <option value="正文哈希">正文哈希</option>
                      </select>
                    </div>
                    <div class="cfg3-field">
                      <label>去重时间窗 (分钟)</label>
                      <input v-model.number="subscriptionEditor.dedupWindow" class="sub-input" type="number" min="0">
                    </div>
                  </div>
                  <div class="cfg3-form-grid">
                    <div class="cfg3-field">
                      <label>频控：每小时最大推送</label>
                      <input v-model.number="subscriptionEditor.rateLimit" class="sub-input" type="number" min="1">
                    </div>
                    <div class="cfg3-field">
                      <label>超量后动作</label>
                      <select v-model="subscriptionEditor.overflowAction" class="sub-select">
                        <option value="静默丢弃">静默丢弃</option>
                        <option value="摘要合并">摘要合并</option>
                        <option value="降级推送">降级推送</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div v-else-if="subscriptionState.step === 3" class="cfg3-step-pane">
                  <div class="cfg3-two-panel">
                    <div class="cfg3-inner-card">
                      <h4><i class="fa-solid fa-users"></i> 内部收件人</h4>
                      <div class="cfg3-field"><label>用户 ID</label><input v-model="subscriptionEditor.internalUserIds" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本"></div>
                      <div class="cfg3-field"><label>用户组 ID</label><input v-model="subscriptionEditor.internalGroupIds" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本"></div>
                    </div>
                    <div class="cfg3-inner-card">
                      <h4><i class="fa-solid fa-bullhorn"></i> 外部通道</h4>
                      <label class="sub-check-chip" style="margin-bottom: 10px;"><input v-model="subscriptionEditor.externalDashboard" type="checkbox"><span>Dashboard 内展示</span></label>
                      <div class="cfg3-field"><label>Webhook URLs</label><input v-model="subscriptionEditor.webhookUrls" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本"></div>
                      <div class="cfg3-field"><label>Telegram IDs</label><input v-model="subscriptionEditor.telegramIds" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本"></div>
                    </div>
                  </div>
                </div>

                <div v-else class="cfg3-step-pane">
                  <div class="cfg3-form-grid">
                    <div class="cfg3-field">
                      <label>责任人 (Owner) *</label>
                      <input v-model="subscriptionEditor.owner" class="sub-input" placeholder="SystemAdmin">
                    </div>
                    <div class="cfg3-field">
                      <label>优先级</label>
                      <input v-model.number="subscriptionEditor.priority" class="sub-input" type="number" min="1" max="100">
                    </div>
                  </div>
                  <div class="cfg3-field">
                    <label>业务备注 / 摘要</label>
                    <textarea v-model="subscriptionEditor.note" class="sub-textarea" placeholder="简述该规则目的、适用边界、已知误报/漏报、值班说明等"></textarea>
                  </div>
                  <div class="cfg3-channel-box">
                    <div class="panel-line-title" style="margin-bottom: 10px;"><i class="fa-solid fa-lock"></i> 规则权限 (RBAC)</div>
                    <div class="cfg3-form-grid">
                      <div class="cfg3-field">
                        <label>可见范围</label>
                        <select v-model="subscriptionEditor.rbacVisibility" class="sub-select">
                          <option value="仅自己">仅自己</option>
                          <option value="本组">本组</option>
                          <option value="全局">全局</option>
                        </select>
                      </div>
                      <div class="cfg3-field">
                        <label>编辑者 (IDs)</label>
                        <input v-model="subscriptionEditor.editorIds" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本">
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section class="cfg3-side panel board-panel">
                <div class="panel-line-title"><i class="fa-solid fa-flask-vial"></i> 实时沙箱引擎</div>

                <div class="cfg3-kpi-grid">
                  <div class="cfg3-kpi"><span>初筛命中</span><b>{{ subscriptionSandbox.hit }}</b></div>
                  <div class="cfg3-kpi"><span>预计推送</span><b>{{ subscriptionSandbox.push }}</b></div>
                  <div class="cfg3-kpi"><span>摘要组</span><b>{{ subscriptionSandbox.digest }}</b></div>
                  <div class="cfg3-kpi"><span>治理拦截</span><b>{{ subscriptionSandbox.drop }}</b></div>
                </div>

                <div class="cfg3-warn">
                  风险提示：沙箱结果是基于当前 mock 样本的静态模拟，不代表真实线上分布。
                  建议点击下方「智能生成适配样本」快速验证规则逻辑。
                </div>

                <div class="cfg3-sim-title">模拟输入源 (Engine Output Mock)</div>
                <div class="cfg3-sim-actions">
                  <button class="cfg3-btn primary" @click="generateSmartSandboxSample"><i class="fa-solid fa-wand-magic-sparkles"></i>智能生成适配样本</button>
                  <button class="cfg3-btn ghost" @click="loadBurstSandboxSample"><i class="fa-solid fa-wave-square"></i>加载爆发样本</button>
                </div>

                <textarea
                  v-model="sandboxInputText"
                  class="cfg3-json-input"
                  spellcheck="false"
                  @change="runSandboxFromInput"
                  placeholder="在此编辑 Engine Output Mock JSON，修改后会重新执行沙箱。"></textarea>

                <div class="cfg3-result-list">
                  <div
                    v-for="(item, idx) in sandboxEvents"
                    :key="item.id"
                    class="cfg3-hit-card"
                    :class="item.state">
                    <div class="cfg3-hit-title">#{{ idx + 1 }} ｜ {{ item.statusText }} ｜ {{ item.severity }} ｜ [{{ item.topic }}] ｜ {{ item.handle }}</div>
                    <div class="cfg3-hit-line">实体：{{ item.entityType }}：{{ item.entityValue }}</div>
                    <div class="cfg3-hit-line">治理键：{{ item.dedupKey }}</div>
                    <div v-if="item.missReason" class="cfg3-hit-line">未命中原因：{{ item.missReason }}</div>
                    <div v-if="item.blockReason" class="cfg3-hit-line">被治理拦截原因：{{ item.blockReason }}</div>
                    <div class="cfg3-badge-row">
                      <span v-for="badge in item.badges" :key="badge.text" class="cfg3-mini-badge" :class="badge.type">{{ badge.text }}</span>
                    </div>
                    <button class="cfg3-pill" @click="item.expanded = !item.expanded">{{ item.expanded ? '收起详情' : (item.state === 'match' ? '查看命中详情' : '查看未命中详情') }}</button>
                    <pre v-if="item.expanded" class="cfg3-json-preview">{{ JSON.stringify(item.normalizedEvent, null, 2) }}</pre>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="board-grid">
            <div class="summary-card">
              <div class="summary-item">
                <div class="summary-label">专题总数</div>
                <div class="summary-value">{{ topicSummary.total }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">运行中</div>
                <div class="summary-value">{{ topicSummary.running }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">已归档</div>
                <div class="summary-value mute">{{ topicSummary.archived }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">全量命中</div>
                <div class="summary-value">{{ topicSummary.totalHits }}</div>
              </div>
            </div>

            <div class="panel board-panel">
              <div class="panel-line-title"><i class="fa-solid fa-list-ul"></i> 专题列表管理</div>
              <div class="topic-list-grid">
                <div v-for="topic in topicList" :key="topic.id" class="topic-card" @click="openTopicInAlerts(topic)">
                  <div class="topic-head">
                    <div class="topic-name">{{ topic.name }}</div>
                    <span class="status-badge" :class="topic.status === '运行中' ? 'on' : topic.status === '归档' ? 'archive' : 'off'">{{ topic.status }}</span>
                  </div>
                  <div class="topic-desc">{{ topic.desc }}</div>
                  <div class="topic-meta-grid">
                    <span>负责人：{{ topic.owner }}</span>
                    <span>关键词：{{ topic.keywordCount }}</span>
                    <span>数据源：{{ topic.sourceCount }}</span>
                    <span>命中量：{{ topic.hits }}</span>
                    <span>最近执行：{{ topic.lastRun }}</span>
                  </div>
                  <div class="topic-actions">
                    <button class="chip-btn" @click.stop="alertMock(`已复制专题：${topic.name}`)">复制</button>
                    <button class="chip-btn" @click.stop="alertMock(`已打开专题配置：${topic.name}`)">配置</button>
                    <button class="chip-btn primary" @click.stop="toggleTopicStatus(topic)">{{ topic.status === '运行中' ? '暂停' : '启动' }}</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </main>
    </div>

    <div class="modal-overlay" :class="{ open: state.isModalOpen }" @click.self="closeModal">
      <div class="modal-box" v-if="state.selectedDetailItem">
        <div class="modal-header">
          <div class="modal-title"><i class="fa-solid fa-eye"></i> 详情：{{ state.selectedDetailItem.title?.substring(0, 20) || '子线索' }}...</div>
          <div class="modal-close" @click="closeModal"><i class="fa-solid fa-xmark"></i></div>
        </div>
        <div class="modal-body" style="padding: 20px; color: #fff; font-size: 14px; line-height: 1.6;">
          <div v-if="state.selectedDetailItem.source === 'Telegram'" class="tg-container" style="padding:0; margin:-20px;">
              <div class="tg-header" style="padding: 10px 20px; background: #1e293b; border-bottom: 1px solid #000;">
                  <div class="tg-avatar" style="width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-orange), var(--accent-red)); display: flex; justify-content: center; align-items: center; font-weight: 600;">{{ state.selectedDetailItem.chatMeta?.avatarChar || 'A' }}</div>
                  <div class="tg-info" style="margin-left:15px;"><div class="tg-name" style="font-weight: 500;">{{ state.selectedDetailItem.siteName || '群组' }}</div><div class="tg-status" style="color: #8c9db5; font-size: 12px;">2304 members</div></div>
              </div>
              <div class="tg-body" style="padding: 20px; background: #0f172a; min-height:300px;">
                  <div class="tg-msg outgoing" style="display: flex; flex-direction: row-reverse; gap: 10px; margin-bottom: 5px;">
                      <div class="tg-bubble" style="background: #3b82f6; padding: 8px 10px; border-radius: 12px 0 12px 12px; max-width: 75%;">
                          {{ state.selectedDetailItem.content }}
                      </div>
                  </div>
              </div>
          </div>
          <div v-else>
            <h2 style="font-size: 18px; margin-bottom: 10px; color: var(--accent-blue);">{{ state.selectedDetailItem.title }}</h2>
            <p style="color: var(--text-dim); margin-bottom: 15px;">发布人: {{ state.selectedDetailItem.author }} | 时间: {{ state.selectedDetailItem.date }}</p>
            <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 6px; border: 1px solid var(--border-color);">
              {{ state.selectedDetailItem.content }}
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn btn-tool download-tool" @click="alertMock('开始下载原始取证包...')"><i class="fa-solid fa-file-zipper"></i> 下载原始取证包</button>
          <button class="modal-btn btn-tool graph-tool" @click="alertMock('已打开关系图谱分析系统...')"><i class="fa-solid fa-network-wired"></i> 查看关系图谱</button>
          <button class="modal-btn btn-tool translate-tool" @click="mockTranslate"><i class="fa-solid fa-language"></i> 全文翻译</button>
          <div style="flex: 1;"></div> 
          <button class="modal-btn btn-warning" @click="alertMock('正在生成情报线索流转单...')"><i class="fa-solid fa-share-from-square"></i> 转线索</button>
          <button class="modal-btn btn-primary" @click="alertMock('正在对接公安立案系统...')"><i class="fa-solid fa-gavel"></i> 一键立案</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue';
import AppHeader from '../components/AppHeader.vue';
import { mockData } from '../mock/data.js';

const MOCK_REFERENCE_TIME = '2024-06-10 10:25:12';

const parseDateTime = (dateStr) => {
  if (!dateStr) return null;
  const normalized = dateStr.includes('T') ? dateStr : dateStr.replace(' ', 'T');
  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

const padTime = (value) => String(value).padStart(2, '0');
const toDateTimeString = (date) => {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return '';
  return `${date.getFullYear()}-${padTime(date.getMonth() + 1)}-${padTime(date.getDate())} ${padTime(date.getHours())}:${padTime(date.getMinutes())}:${padTime(date.getSeconds())}`;
};

const shiftDateString = (dateStr, offsetMs) => {
  const parsed = parseDateTime(dateStr);
  if (!parsed) return dateStr;
  return toDateTimeString(new Date(parsed.getTime() + offsetMs));
};

const syncMockItemDates = (item, offsetMs) => {
  const nextItem = { ...item, date: shiftDateString(item.date, offsetMs) };

  if (Array.isArray(item.children)) {
    nextItem.children = item.children.map(child => ({
      ...child,
      date: shiftDateString(child.date, offsetMs)
    }));
  }

  return nextItem;
};

// === 1. 深度拷贝数据，使其完全响应式 (支持已读、选中、折叠、误报修改) ===
const initialListData = (() => {
  const offsetMs = Date.now() - (parseDateTime(MOCK_REFERENCE_TIME)?.getTime() || Date.now());
  return mockData.map(item => syncMockItemDates(item, offsetMs));
})();

const listData = ref(JSON.parse(JSON.stringify(initialListData)));

const followList = ref([
  { id: 1, name: '@shadow_pay', type: '高风险账号', risk: 'high', platforms: ['Telegram', 'X'], lastSeen: '8 分钟前', heat: 89, alerts24h: 16, muted: false },
  { id: 2, name: '0xA91f...D33', type: '可疑钱包地址', risk: 'high', platforms: ['链上', 'Telegram'], lastSeen: '22 分钟前', heat: 93, alerts24h: 21, muted: false },
  { id: 3, name: '沿海冷链灰链', type: '事件话题', risk: 'mid', platforms: ['Weibo', 'Telegram'], lastSeen: '1 小时前', heat: 74, alerts24h: 9, muted: false },
  { id: 4, name: 'tor:chem_cell', type: '暗网账号', risk: 'mid', platforms: ['Tor'], lastSeen: '2 小时前', heat: 68, alerts24h: 6, muted: true }
]);

const monitorTopics = ref([
  { id: 1, name: '跨境走私航线监测', status: '运行中', schedule: '每 30 分钟', coverage: 82, hits24h: 37, pendingReview: 8, sources: ['Telegram', 'Tor'] },
  { id: 2, name: '涉毒隐语语义追踪', status: '运行中', schedule: '每 15 分钟', coverage: 91, hits24h: 52, pendingReview: 13, sources: ['Weibo', 'X', 'Telegram'] },
  { id: 3, name: '暴恐传播链路识别', status: '已暂停', schedule: '每 1 小时', coverage: 64, hits24h: 11, pendingReview: 4, sources: ['Telegram', 'Tor'] },
  { id: 4, name: '社工库交易扩散预警', status: '运行中', schedule: '每 45 分钟', coverage: 77, hits24h: 26, pendingReview: 7, sources: ['社工库', 'X'] }
]);

const topicList = ref([
  { id: 1, name: '毒品交易链路专题', owner: '刘洋', keywordCount: 128, sourceCount: 6, hits: 1362, status: '运行中', lastRun: '2026-03-29 10:18', desc: '围绕暗语、物流与收款地址识别涉毒交易组织链路。' },
  { id: 2, name: '跨境走私热点专题', owner: '陈昕', keywordCount: 97, sourceCount: 5, hits: 978, status: '运行中', lastRun: '2026-03-29 09:42', desc: '重点关注沿海港口、边境节点、匿名联络渠道异常。' },
  { id: 3, name: '黑产数据泄露专题', owner: '王琪', keywordCount: 83, sourceCount: 4, hits: 745, status: '已暂停', lastRun: '2026-03-28 23:10', desc: '监控社工库售卖、账号包流转和诈骗引流路径。' },
  { id: 4, name: '暴恐传播专题（归档）', owner: '张澜', keywordCount: 61, sourceCount: 3, hits: 411, status: '归档', lastRun: '2026-03-22 17:08', desc: '历史阶段专项，保留规则与样本用于复盘审计。' }
]);

const SUBSCRIPTION_TOPICS = [
  { id: 'TopicDrugs', name: '毒品交易' },
  { id: 'TopicSmuggle', name: '非法走私' },
  { id: 'TopicTerror', name: '恐怖暴力' },
  { id: 'TopicDataLeak', name: '数据泄露' },
  { id: 'TopicTaiwan', name: '台湾' },
  { id: 'TopicRansom', name: '勒索软件' }
];

const subscriptionRules = ref([
  {
    id: 'sub-1',
    name: '涉毒高危订阅',
    owner: 'SystemAdmin',
    enabled: true,
    status: 'applied',
    topics: ['TopicDrugs'],
    minSeverity: 'HIGH',
    riskMin: 75,
    sources: ['Telegram', 'Tor'],
    channels: ['Dashboard', 'Telegram'],
    schedule: '每 15 分钟',
    desc: '对涉毒高危线索进行实时订阅并转发值班组。',
    updatedAt: toDateTimeString(new Date())
  }
]);

const subscriptionState = reactive({
  selectedId: 'sub-1',
  search: '',
  step: 1,
  titleEditing: false,
  titleBackup: ''
});

const subscriptionEditor = reactive({
  name: '',
  owner: '',
  enabled: true,
  status: 'draft',
  topics: [],
  minSeverity: 'HIGH',
  riskMin: 70,
  sources: ['Telegram'],
  channels: ['Dashboard'],
  schedule: '每 15 分钟',
  desc: '',
  regionFocus: '',
  bizTagFocus: '',
  dedupKey: '不过滤 (每条独立推送)',
  dedupWindow: 30,
  rateLimit: 50,
  overflowAction: '静默丢弃',
  internalUserIds: '',
  internalGroupIds: 'g_riskOps',
  externalDashboard: true,
  webhookUrls: '',
  telegramIds: '@ops_channel',
  priority: 50,
  note: '',
  rbacVisibility: '仅自己',
  editorIds: ''
});

// === 2. 集中化状态管理 (对应原版 APP_STATE) ===
const state = reactive({
  activeModule: 'alerts',
  leftCollapsed: false,
  rightCollapsed: false,
  isImmersive: false,
  isFilterCollapsed: false,
  showCustomDate: false,
  isSortDropdownOpen: false,
  searchQuery: '',
  selectAll: false,
  sort: 'time-desc',
  pagination: { currentPage: 1, pageSize: 10 },
  carousel: { region: 0, author: 0 },
  isModalOpen: false,
  selectedDetailItem: null
});

const filters = reactive({
  time: '7days', risk: 'all', read: 'all', media: 'all', topic: 'all',
  rule: 'all', author: 'all', region: 'all', industry: 'all', entity: '',
  customStart: '', customEnd: ''
});

const activeModuleMeta = computed(() => {
  if (state.activeModule === 'follow') {
    return { title: '我的关注', subtitle: '高价值对象持续追踪与动态预警', countText: `${followList.value.length} 个关注对象` };
  }
  if (state.activeModule === 'monitor') {
    return { title: '专题监测', subtitle: '任务运行状态、覆盖率与命中趋势', countText: `${monitorTopics.value.length} 个监测任务` };
  }
  if (state.activeModule === 'subscription') {
    return { title: '订阅监测', subtitle: '订阅路由与治理编排中枢', countText: `${subscriptionRules.value.length} 条订阅规则` };
  }
  if (state.activeModule === 'topicList') {
    return { title: '专题列表', subtitle: '专题资产管理与快速配置入口', countText: `${topicList.value.length} 个专题` };
  }
  return { title: '告警信息', subtitle: '多源风险告警聚合研判中心', countText: `${filteredList.value.length} 条线索` };
});

const followSummary = computed(() => ({
  total: followList.value.length,
  high: followList.value.filter(item => item.risk === 'high').length,
  alerts24h: followList.value.reduce((sum, item) => sum + item.alerts24h, 0),
  muted: followList.value.filter(item => item.muted).length
}));

const monitorSummary = computed(() => ({
  running: monitorTopics.value.filter(item => item.status === '运行中').length,
  paused: monitorTopics.value.filter(item => item.status !== '运行中').length,
  hits24h: monitorTopics.value.reduce((sum, item) => sum + item.hits24h, 0),
  pending: monitorTopics.value.reduce((sum, item) => sum + item.pendingReview, 0)
}));

const topicSummary = computed(() => ({
  total: topicList.value.length,
  running: topicList.value.filter(item => item.status === '运行中').length,
  archived: topicList.value.filter(item => item.status === '归档').length,
  totalHits: topicList.value.reduce((sum, item) => sum + item.hits, 0)
}));

// 关闭弹窗和下拉的全局监听
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.select-box')) state.isSortDropdownOpen = false;
  });
});

// === 3. 基础工具与映射方法 ===
const availableTopics = computed(() => [...new Set(listData.value.map(item => item.topic))].filter(Boolean));
const availableRegions = computed(() => [...new Set(listData.value.map(item => getProvince(item.region)))].filter(Boolean));

const getTopicName = (topic) => ({ 'TopicTaiwan': '台湾', 'TopicDataLeak': '数据泄露', 'TopicRansom': '勒索软件', 'TopicDrugs': '毒品交易', 'TopicTerror': '恐怖暴力', 'TopicSmuggle': '非法走私' }[topic] || topic);
const getRiskText = (risk) => ({ high: '高危', mid: '中危', low: '低危' }[risk] || risk);
const getRuleName = (code) => ({ 'Rule_Drug_Slang': '涉毒黑话检测', 'Rule_Terror_Action': '高危行为意图', 'Rule_Smuggle_Route': '走私路径监控', 'Rule_Crypto_Transfer': '暗网加密交易' }[code] || code);
const getIndustryName = (ind) => ({ 'Finance': '金融', 'Gov': '政府', 'Tech': '科技', 'Edu': '教育', 'Health': '医疗' }[ind] || ind);
const getProvince = (region) => region ? (region.includes('/') ? region.split('/')[0] : region) : '未知';
const formatTime = (dateStr) => dateStr ? dateStr.replace(/(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}):\d{2}/, '$1 $2') : '';
const getDisplayTitle = (item) => item.title || item.siteName || item.author || '未命名线索';
const getSiteLabel = (item) => item.source === 'Telegram' ? '群组/频道' : '网站';
const getSourceIcon = (source) => ({ Telegram: 'fa-paper-plane', Tor: 'fa-user-secret', Weibo: 'fa-globe', I2P: 'fa-network-wired' }[source] || 'fa-circle-user');
const getRuleList = (item) => {
  const rawRules = item.hitRules ?? item.hitRule ?? [];

  if (Array.isArray(rawRules)) return rawRules.filter(Boolean);
  if (typeof rawRules === 'string') return rawRules.split(/[，,|/]/).map(rule => rule.trim()).filter(Boolean);

  return [];
};
const hasRuleMatch = (item, rule) => getRuleList(item).includes(rule);

const getEntityClass = (type) => ({ identity: 'entity-id', money: 'entity-money', loc: 'entity-loc', logistics: 'entity-logistics', slang: 'entity-slang' }[type] || 'entity-slang');
const getEntityIcon = (type) => ({ identity: 'fa-regular fa-id-card', money: 'fa-solid fa-coins', loc: 'fa-solid fa-location-dot', logistics: 'fa-solid fa-box', slang: 'fa-solid fa-capsules' }[type] || 'fa-solid fa-hashtag');
const sourceFromPlatform = (platforms = []) => {
  const sourceMap = { Telegram: 'Telegram', Tor: 'Tor', Weibo: 'Weibo', I2P: 'I2P' };
  const first = platforms.find(p => sourceMap[p]);
  return first ? sourceMap[first] : 'all';
};

const getTopicCodeByName = (name = '') => {
  if (name.includes('毒品') || name.includes('涉毒')) return 'TopicDrugs';
  if (name.includes('走私')) return 'TopicSmuggle';
  if (name.includes('黑产') || name.includes('泄露')) return 'TopicDataLeak';
  if (name.includes('暴恐') || name.includes('恐怖')) return 'TopicTerror';
  if (name.includes('台湾')) return 'TopicTaiwan';
  return 'all';
};

// === 4. 核心过滤引擎 (支持误报剔除与多维联动) ===
const baseFilteredList = computed(() => {
  return listData.value.filter(item => {
    if (item.falsePositive) return false; // 误报剔除

    if (state.searchQuery && !item.title.toLowerCase().includes(state.searchQuery) && !item.content.toLowerCase().includes(state.searchQuery)) return false;
    if (filters.risk !== 'all' && item.risk !== filters.risk) return false;
    if (filters.read === 'read' && !item.read) return false;
    if (filters.read === 'unread' && item.read) return false;
    if (filters.media !== 'all' && item.source !== filters.media) return false;
    if (filters.topic !== 'all' && item.topic !== filters.topic) return false;
    if (filters.industry !== 'all' && item.industry !== filters.industry) return false;
    if (filters.author !== 'all' && item.author !== filters.author) return false;
    if (filters.region !== 'all') {
      if (getProvince(item.region) !== filters.region && item.region !== filters.region) return false;
    }
    
    const itemDate = parseDateTime(item.date);
    const now = new Date();
    if (!itemDate) return false;

    if (filters.time === 'custom' && filters.customStart && filters.customEnd) {
      const start = new Date(`${filters.customStart}T00:00:00`);
      const end = new Date(`${filters.customEnd}T23:59:59`);
      if (itemDate < start || itemDate > end) return false;
    } else if (filters.time !== 'all') {
      const diffMs = now.getTime() - itemDate.getTime();
      if (diffMs < 0) return false;

      if (filters.time === 'today') {
        const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        if (itemDate < startOfToday) return false;
      }
      if (filters.time === '7days' && diffMs > 7 * 24 * 60 * 60 * 1000) return false;
      if (filters.time === '30days' && diffMs > 30 * 24 * 60 * 60 * 1000) return false;
    }
    return true;
  });
});

const filteredList = computed(() => {
  let result = baseFilteredList.value.filter(item => {
    if (filters.rule !== 'all' && !hasRuleMatch(item, filters.rule)) return false;
    return true;
  });

  // 排序引擎
  result.sort((a, b) => {
    if (state.sort === 'time-desc') return new Date(b.date) - new Date(a.date);
    if (state.sort === 'time-asc') return new Date(a.date) - new Date(b.date);
    const riskMap = { high: 3, mid: 2, low: 1 };
    if (state.sort === 'risk-desc') return riskMap[b.risk] - riskMap[a.risk] || new Date(b.date) - new Date(a.date);
    if (state.sort === 'risk-asc') return riskMap[a.risk] - riskMap[b.risk] || new Date(b.date) - new Date(a.date);
    return 0;
  });

  return result;
});

// 分页截取
const paginatedList = computed(() => {
  const start = (state.pagination.currentPage - 1) * state.pagination.pageSize;
  return filteredList.value.slice(start, start + state.pagination.pageSize);
});
const totalPages = computed(() => Math.ceil(filteredList.value.length / state.pagination.pageSize));
const changePage = (p) => { if (p >= 1 && p <= totalPages.value) state.pagination.currentPage = p; };

// 选中逻辑
const hasSelected = computed(() => listData.value.some(i => i.selected));
const toggleSelectAll = () => { paginatedList.value.forEach(i => i.selected = state.selectAll); };

// 排序 UI 计算
const sortText = computed(() => ({ 'time-desc': '时间最新', 'time-asc': '时间最旧', 'risk-desc': '危害降序', 'risk-asc': '危害升序' }[state.sort]));
const sortIcon = computed(() => ({ 'time-desc': 'fa-solid fa-arrow-down-wide-short', 'time-asc': 'fa-solid fa-arrow-up-wide-short', 'risk-desc': 'fa-solid fa-triangle-exclamation', 'risk-asc': 'fa-solid fa-triangle-exclamation rotate-180' }[state.sort]));
const changeSort = (val) => { state.sort = val; state.isSortDropdownOpen = false; state.pagination.currentPage = 1; };

// 动态过滤提示
const activeFilterHint = computed(() => {
  let text = [];
  if(filters.risk !== 'all') text.push(getRiskText(filters.risk));
  if(filters.media !== 'all') text.push(filters.media);
  if(filters.topic !== 'all') text.push(getTopicName(filters.topic));
  if(filters.rule !== 'all') text.push(getRuleName(filters.rule));
  if(filters.region !== 'all') text.push(filters.region);
  if(state.searchQuery) text.push(`搜索:${state.searchQuery}`);
  return text.length ? `过滤中: <span style="color:#fff">${text.join(' + ')}</span> <span class="clear-filter-btn" onclick="document.querySelector('.primary').nextElementSibling.click()"><i class="fa-solid fa-xmark"></i> 清除</span>` : '';
});

// === 5. 交互方法 ===
const toggleLeftSidebar = () => state.leftCollapsed = !state.leftCollapsed;
const toggleRightSidebar = () => state.rightCollapsed = !state.rightCollapsed;
const switchModule = (module) => {
  state.activeModule = module;
  if (module === 'subscription') {
    ensureSubscriptionSelection();
  }
  if (module !== 'alerts') {
    state.isImmersive = false;
    state.leftCollapsed = false;
    state.rightCollapsed = false;
    state.isFilterCollapsed = false;
  }
};

const resetAlertFiltersByPreset = () => {
  filters.time = '7days';
  filters.risk = 'all';
  filters.read = 'all';
  filters.media = 'all';
  filters.topic = 'all';
  filters.rule = 'all';
  filters.author = 'all';
  filters.region = 'all';
  filters.industry = 'all';
  filters.entity = '';
  filters.customStart = '';
  filters.customEnd = '';
  state.searchQuery = '';
  state.sort = 'time-desc';
  state.pagination.currentPage = 1;
};

const openFollowInAlerts = (item) => {
  resetAlertFiltersByPreset();
  state.activeModule = 'alerts';
  state.searchQuery = item.name;
  filters.risk = item.risk;
  filters.media = sourceFromPlatform(item.platforms);
};

const openMonitorInAlerts = (item) => {
  resetAlertFiltersByPreset();
  state.activeModule = 'alerts';
  state.searchQuery = item.name;
  filters.topic = getTopicCodeByName(item.name);
  filters.media = sourceFromPlatform(item.sources);
};

const openTopicInAlerts = (topic) => {
  resetAlertFiltersByPreset();
  state.activeModule = 'alerts';
  state.searchQuery = topic.name;
  filters.topic = getTopicCodeByName(topic.name);
};

const filteredSubscriptionRules = computed(() => {
  const keyword = (subscriptionState.search || '').toLowerCase().trim();
  if (!keyword) return subscriptionRules.value;
  return subscriptionRules.value.filter((rule) => {
    const topicText = (rule.topics || []).map(getTopicName).join(' ');
    const text = `${rule.name || ''} ${rule.owner || ''} ${rule.desc || ''} ${topicText}`.toLowerCase();
    return text.includes(keyword);
  });
});

const selectedSubscriptionRule = computed(() => {
  return subscriptionRules.value.find((rule) => rule.id === subscriptionState.selectedId) || null;
});

const subscriptionSummary = computed(() => ({
  total: subscriptionRules.value.length,
  applied: subscriptionRules.value.filter((rule) => rule.status === 'applied').length,
  draft: subscriptionRules.value.filter((rule) => rule.status !== 'applied').length,
  monitorSync: monitorTopics.value.filter((item) => item.subscriptionRuleId).length
}));

const subscriptionSandboxStats = reactive({ hit: 0, push: 0, digest: 0, drop: 0 });
const subscriptionSandbox = computed(() => ({ ...subscriptionSandboxStats }));

const sandboxInputText = ref('');
const sandboxEvents = ref([]);

const severityWeight = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
const splitValues = (text = '') => String(text || '').split(/[，,|/\n]/).map(v => v.trim()).filter(Boolean);
const dedupeKeyLabelToMode = {
  '不过滤 (每条独立推送)': 'none',
  '内容哈希': 'content_hash',
  '实体聚合': 'entity',
  '来源账号': 'source_handle'
};

const canonField = (field, value) => {
  if (value === null || value === undefined) return value;
  if (field === 'source_handle' || field === 'content_hash') return String(value).trim().toLowerCase();
  if (field === 'severity') return String(value).trim().toUpperCase();
  return typeof value === 'string' ? String(value).trim() : value;
};

const stableHash = (text) => {
  const raw = String(text || '');
  let hash = 0;
  for (let i = 0; i < raw.length; i += 1) {
    hash = Math.imul(31, hash) + raw.charCodeAt(i) | 0;
  }
  return String(Math.abs(hash));
};

const normalizeSandboxEvent = (raw) => {
  const source = raw && typeof raw === 'object' ? raw : {};
  const iocs = source.extracted_iocs && typeof source.extracted_iocs === 'object' ? source.extracted_iocs : {};
  const labels = Array.isArray(source.labels)
    ? source.labels.map(item => typeof item === 'string' ? item : item?.label).filter(Boolean)
    : [];

  return {
    threat_category: source.threat_category || source.topic || source.category || '',
    severity: canonField('severity', source.severity || 'LOW') || 'LOW',
    risk_score: Number(source.risk_score ?? 0),
    source_platform: source.source_platform || source.platform || '',
    source_handle: source.source_handle || source.source || source.channel || '-',
    entity_type: source.entity_type || source.entities?.[0]?.type || '-',
    entity_value: source.entity_value || source.entities?.[0]?.value || '-',
    labels,
    ioc_location: Array.isArray(iocs.location) ? iocs.location : [],
    raw_content: source.raw_content || source.content || '',
    content_hash: canonField('content_hash', source.content_hash || stableHash(source.raw_content || JSON.stringify(source).slice(0, 3000))),
    event_time: Number(source.timestamp || source.event_time || Date.now())
  };
};

const buildSandboxInput = (mode = 'smart') => {
  const topic = subscriptionEditor.topics[0] || 'TopicDrugs';
  const source = subscriptionEditor.sources[0] || 'Telegram';
  const baseRisk = Number(subscriptionEditor.riskMin || 70) || 70;
  const region = splitValues(subscriptionEditor.regionFocus)[0] || '缅北';
  const tag = splitValues(subscriptionEditor.bizTagFocus)[0] || '贩毒';

  if (mode === 'burst') {
    const arr = [];
    const now = Date.now();
    for (let i = 0; i < 12; i += 1) {
      arr.push({
        threat_category: topic,
        severity: i % 5 === 0 ? 'CRITICAL' : 'HIGH',
        risk_score: i % 4 === 0 ? Math.max(baseRisk + 10, 85) : Math.max(baseRisk + 3, 75),
        source_platform: source,
        source_handle: i % 3 === 0 ? '@smart_mock_hot' : '@smart_mock_01',
        labels: [{ label: tag }, { label: '暗网担保' }],
        extracted_iocs: { location: [region] },
        entity_type: 'wallet',
        entity_value: `TXYZ_SMART_${100 + i}`,
        raw_content: `模拟爆发样本 ${i + 1}：高频命中，用于验证去重与频控。`,
        event_time: now + i * 20 * 60 * 1000
      });
    }
    return arr;
  }

  return [
    {
      threat_category: topic,
      severity: subscriptionEditor.minSeverity,
      risk_score: Math.max(baseRisk + 8, 80),
      source_platform: source,
      source_handle: '@smart_mock_01',
      labels: [{ label: tag }, { label: '暗网担保' }],
      extracted_iocs: { location: [region] },
      entity_type: 'wallet',
      entity_value: 'TXYZ_SMART_01',
      raw_content: '此数据旨在覆盖当前规则阈值，预期应命中并触发推送。',
      event_time: Date.now()
    },
    {
      threat_category: topic,
      severity: 'LOW',
      risk_score: Math.max(15, baseRisk - 35),
      source_platform: source,
      source_handle: '@smart_mock_02',
      labels: [{ label: '无关样本' }],
      extracted_iocs: { location: ['未知'] },
      entity_type: 'wallet',
      entity_value: 'TXYZ_SMART_02',
      raw_content: '此数据旨在模拟低危、低分、无关键标签等条件【不命中】。',
      event_time: Date.now() + 120000
    }
  ];
};

const evaluateSandboxEvent = (ev) => {
  const minSeverity = subscriptionEditor.minSeverity || 'HIGH';
  const minRisk = Number(subscriptionEditor.riskMin || 70);
  const matchTopic = !(subscriptionEditor.topics || []).length || (subscriptionEditor.topics || []).includes(ev.threat_category);
  const matchSource = !(subscriptionEditor.sources || []).length || (subscriptionEditor.sources || []).includes(ev.source_platform);
  const matchSeverity = (severityWeight[ev.severity] || 0) >= (severityWeight[minSeverity] || 0);
  const matchRisk = Number(ev.risk_score || 0) >= minRisk;
  const regionFilters = splitValues(subscriptionEditor.regionFocus).map(v => v.toLowerCase());
  const labelFilters = splitValues(subscriptionEditor.bizTagFocus).map(v => v.toLowerCase());
  const locTexts = (ev.ioc_location || []).map(v => String(v).toLowerCase());
  const labelTexts = (ev.labels || []).map(v => String(v).toLowerCase());
  const rawText = String(ev.raw_content || '').toLowerCase();
  const matchRegion = !regionFilters.length || regionFilters.some(v => locTexts.includes(v));
  const matchLabel = !labelFilters.length || labelFilters.some(v => labelTexts.includes(v) || rawText.includes(v));
  const pass = matchTopic && matchSource && matchSeverity && matchRisk && matchRegion && matchLabel;

  const failReason = !matchTopic
    ? '专题未命中'
    : !matchSource
      ? '来源未命中'
      : !matchSeverity
        ? '等级不足'
        : !matchRisk
          ? '风险分不足'
          : !matchRegion
            ? '地域未命中'
            : !matchLabel
              ? '业务标签未命中'
              : '未满足规则条件';

  return {
    pass,
    missReason: pass ? '' : failReason,
    trace: {
      topic: matchTopic,
      source: matchSource,
      severity: matchSeverity,
      risk: matchRisk,
      region: matchRegion,
      label: matchLabel
    }
  };
};

const computeSandboxDedupeKey = (ev) => {
  const mode = dedupeKeyLabelToMode[subscriptionEditor.dedupKey] || 'none';
  if (mode === 'content_hash') return `h:${ev.content_hash || ''}`;
  if (mode === 'entity') return `e:${ev.entity_type || ''}:${ev.entity_value || ''}`;
  if (mode === 'source_handle') return `s:${canonField('source_handle', ev.source_handle || '')}`;
  return '无去重键';
};

const simulateGovernance = (passedEvents) => {
  const delivered = [];
  const dropped = [];
  const digests = [];

  const dedupeWindowMs = Math.max(0, Number(subscriptionEditor.dedupWindow || 0)) * 60 * 1000;
  const rateLimit = Math.max(0, Number(subscriptionEditor.rateLimit || 0));
  const overflowToDigest = subscriptionEditor.overflowAction === '摘要合并';

  const dedupeCache = new Map();
  const hourCounter = new Map();
  const digestCounter = new Map();

  const sorted = [...passedEvents].sort((a, b) => (a.event_time || 0) - (b.event_time || 0));
  sorted.forEach((ev) => {
    const dedupeKey = computeSandboxDedupeKey(ev);
    if (dedupeKey !== '无去重键' && dedupeWindowMs > 0) {
      const lastAt = dedupeCache.get(dedupeKey) || 0;
      if (ev.event_time - lastAt < dedupeWindowMs) {
        dropped.push({ event: ev, reason: 'dedupe_window' });
        return;
      }
      dedupeCache.set(dedupeKey, ev.event_time);
    }

    const hourBucket = Math.floor((ev.event_time || Date.now()) / (60 * 60 * 1000));
    const sent = hourCounter.get(hourBucket) || 0;
    if (rateLimit > 0 && sent >= rateLimit) {
      if (overflowToDigest) {
        digestCounter.set(hourBucket, (digestCounter.get(hourBucket) || 0) + 1);
        dropped.push({ event: ev, reason: 'rate_limit_digest', hourBucket });
        return;
      }
      dropped.push({ event: ev, reason: 'rate_limit_drop', hourBucket });
      return;
    }

    hourCounter.set(hourBucket, sent + 1);
    delivered.push({ event: ev, hourBucket });
  });

  digestCounter.forEach((count, hourBucket) => {
    digests.push({ hourBucket, count });
  });

  return { delivered, dropped, digests };
};

const runSandboxFromInput = () => {
  try {
    const parsed = JSON.parse(sandboxInputText.value || '[]');
    const rawEvents = Array.isArray(parsed) ? parsed : (Array.isArray(parsed?.events) ? parsed.events : []);
    const normalizedEvents = rawEvents.map(ev => normalizeSandboxEvent(ev));

    const evals = normalizedEvents.map(ev => ({ event: ev, result: evaluateSandboxEvent(ev) }));
    const passed = evals.filter(item => item.result.pass).map(item => item.event);
    const gov = simulateGovernance(passed);

    subscriptionSandboxStats.hit = passed.length;
    subscriptionSandboxStats.push = gov.delivered.length;
    subscriptionSandboxStats.digest = gov.digests.length;
    subscriptionSandboxStats.drop = gov.dropped.length;

    sandboxEvents.value = normalizedEvents.map((ev, idx) => {
      const result = evals[idx].result;
      const delivered = gov.delivered.find(x => x.event === ev);
      const blocks = gov.dropped.filter(x => x.event === ev);
      const dedupKey = computeSandboxDedupeKey(ev);

      const state = delivered ? 'match' : (result.pass && blocks.length ? 'block' : 'miss');
      const statusText = delivered ? '✅ 已推送' : (result.pass && blocks.length ? '⚠️ 命中但被治理拦截' : '❌ 未命中');
      const blockReason = blocks.some(b => b.reason === 'dedupe_window')
        ? '命中去重窗，重复样本被拦截'
        : blocks.some(b => b.reason === 'rate_limit_digest')
          ? '超过频控上限，转为摘要合并'
          : blocks.some(b => b.reason === 'rate_limit_drop')
            ? '超过频控上限，执行静默丢弃'
            : '';

      const badges = [];
      if (delivered) badges.push({ type: 'ok', text: `小时桶 ${delivered.hourBucket}` });
      if (blocks.some(b => b.reason === 'dedupe_window')) badges.push({ type: 'warn', text: '去重窗拦截' });
      if (blocks.some(b => b.reason === 'rate_limit_digest')) badges.push({ type: 'warn', text: '超量转摘要' });
      if (blocks.some(b => b.reason === 'rate_limit_drop')) badges.push({ type: 'bad', text: '超量丢弃' });
      if (!result.pass) badges.push({ type: 'neutral', text: '初筛未命中' });

      return {
        id: `${Date.now()}-${idx}`,
        state,
        statusText,
        topic: ev.threat_category || '-',
        severity: ev.severity || '-',
        handle: ev.source_handle || '-',
        entityType: ev.entity_type || '-',
        entityValue: ev.entity_value || '-',
        dedupKey,
        missReason: result.missReason,
        blockReason,
        badges,
        expanded: idx === 0,
        normalizedEvent: {
          normalized_event: ev,
          trace: result.trace,
          routing: {
            channels: subscriptionEditor.channels,
            schedule: subscriptionEditor.schedule,
            overflow_action: subscriptionEditor.overflowAction
          }
        }
      };
    });

    if (!sandboxEvents.value.length) {
      subscriptionSandboxStats.hit = 0;
      subscriptionSandboxStats.push = 0;
      subscriptionSandboxStats.digest = 0;
      subscriptionSandboxStats.drop = 0;
    }
  } catch (error) {
    subscriptionSandboxStats.hit = 0;
    subscriptionSandboxStats.push = 0;
    subscriptionSandboxStats.digest = 0;
    subscriptionSandboxStats.drop = 0;
    sandboxEvents.value = [{
      id: `err-${Date.now()}`,
      state: 'bad',
      statusText: '❌ JSON 解析失败',
      topic: '-',
      severity: '-',
      handle: '-',
      entityType: '-',
      entityValue: '-',
      dedupKey: '-',
      missReason: `JSON 格式错误：${error?.message || '未知错误'}`,
      blockReason: '',
      badges: [{ type: 'bad', text: '请修复输入 JSON' }],
      expanded: false,
      normalizedEvent: {}
    }];
  }
};

const generateSmartSandboxSample = () => {
  sandboxInputText.value = JSON.stringify(buildSandboxInput('smart'), null, 2);
  runSandboxFromInput();
};

const loadBurstSandboxSample = () => {
  sandboxInputText.value = JSON.stringify(buildSandboxInput('burst'), null, 2);
  runSandboxFromInput();
};

watch(
  () => [
    subscriptionEditor.topics.join('|'),
    subscriptionEditor.sources.join('|'),
    subscriptionEditor.minSeverity,
    subscriptionEditor.riskMin,
    subscriptionEditor.regionFocus,
    subscriptionEditor.bizTagFocus,
    subscriptionEditor.dedupKey,
    subscriptionEditor.dedupWindow,
    subscriptionEditor.rateLimit,
    subscriptionEditor.overflowAction,
    subscriptionEditor.enabled
  ],
  () => {
    if (!sandboxInputText.value) return;
    runSandboxFromInput();
  }
);

const ensureSubscriptionSelection = () => {
  if (!subscriptionRules.value.length) {
    createSubscriptionRule();
    return;
  }
  if (!subscriptionState.selectedId || !selectedSubscriptionRule.value) {
    subscriptionState.selectedId = subscriptionRules.value[0].id;
  }
  syncSubscriptionEditor();
  if (!sandboxInputText.value) {
    generateSmartSandboxSample();
  }
};

const syncSubscriptionEditor = () => {
  const rule = selectedSubscriptionRule.value;
  if (!rule) return;
  subscriptionEditor.name = rule.name || '';
  subscriptionEditor.owner = rule.owner || '';
  subscriptionEditor.enabled = !!rule.enabled;
  subscriptionEditor.status = rule.status || 'draft';
  subscriptionEditor.topics = [...(rule.topics || [])];
  subscriptionEditor.minSeverity = rule.minSeverity || 'HIGH';
  subscriptionEditor.riskMin = Number(rule.riskMin ?? 70);
  subscriptionEditor.sources = [...(rule.sources || [])];
  subscriptionEditor.channels = [...(rule.channels || [])];
  subscriptionEditor.schedule = rule.schedule || '每 15 分钟';
  subscriptionEditor.desc = rule.desc || '';
  subscriptionEditor.regionFocus = rule.regionFocus || '';
  subscriptionEditor.bizTagFocus = rule.bizTagFocus || '';
  subscriptionEditor.dedupKey = rule.dedupKey || '不过滤 (每条独立推送)';
  subscriptionEditor.dedupWindow = Number(rule.dedupWindow ?? 30);
  subscriptionEditor.rateLimit = Number(rule.rateLimit ?? 50);
  subscriptionEditor.overflowAction = rule.overflowAction || '静默丢弃';
  subscriptionEditor.internalUserIds = rule.internalUserIds || '';
  subscriptionEditor.internalGroupIds = rule.internalGroupIds || 'g_riskOps';
  subscriptionEditor.externalDashboard = rule.externalDashboard !== false;
  subscriptionEditor.webhookUrls = rule.webhookUrls || '';
  subscriptionEditor.telegramIds = rule.telegramIds || '@ops_channel';
  subscriptionEditor.priority = Number(rule.priority ?? 50);
  subscriptionEditor.note = rule.note || '';
  subscriptionEditor.rbacVisibility = rule.rbacVisibility || '仅自己';
  subscriptionEditor.editorIds = rule.editorIds || '';
};

const persistSubscriptionEditor = () => {
  const rule = selectedSubscriptionRule.value;
  if (!rule) return null;
  rule.name = (subscriptionEditor.name || '').trim();
  rule.owner = (subscriptionEditor.owner || '').trim();
  rule.enabled = !!subscriptionEditor.enabled;
  rule.topics = [...(subscriptionEditor.topics || [])];
  rule.minSeverity = subscriptionEditor.minSeverity || 'HIGH';
  rule.riskMin = Number(subscriptionEditor.riskMin || 0);
  rule.sources = [...(subscriptionEditor.sources || [])];
  rule.channels = [...(subscriptionEditor.channels || [])];
  rule.schedule = subscriptionEditor.schedule || '每 15 分钟';
  rule.desc = (subscriptionEditor.desc || '').trim();
  rule.regionFocus = (subscriptionEditor.regionFocus || '').trim();
  rule.bizTagFocus = (subscriptionEditor.bizTagFocus || '').trim();
  rule.dedupKey = subscriptionEditor.dedupKey || '不过滤 (每条独立推送)';
  rule.dedupWindow = Number(subscriptionEditor.dedupWindow || 0);
  rule.rateLimit = Number(subscriptionEditor.rateLimit || 0);
  rule.overflowAction = subscriptionEditor.overflowAction || '静默丢弃';
  rule.internalUserIds = (subscriptionEditor.internalUserIds || '').trim();
  rule.internalGroupIds = (subscriptionEditor.internalGroupIds || '').trim();
  rule.externalDashboard = !!subscriptionEditor.externalDashboard;
  rule.webhookUrls = (subscriptionEditor.webhookUrls || '').trim();
  rule.telegramIds = (subscriptionEditor.telegramIds || '').trim();
  rule.priority = Number(subscriptionEditor.priority || 50);
  rule.note = (subscriptionEditor.note || '').trim();
  rule.rbacVisibility = subscriptionEditor.rbacVisibility || '仅自己';
  rule.editorIds = (subscriptionEditor.editorIds || '').trim();
  rule.updatedAt = toDateTimeString(new Date());
  return rule;
};

const validateSubscriptionEditor = () => {
  if (!(subscriptionEditor.name || '').trim()) return '规则名称不能为空';
  if (!(subscriptionEditor.owner || '').trim()) return '责任人不能为空';
  if (!(subscriptionEditor.topics || []).length) return '至少选择一个监测专题';
  if (!(subscriptionEditor.sources || []).length) return '至少选择一个监测来源';
  if (!(subscriptionEditor.channels || []).length) return '至少选择一个分发通道';
  return '';
};

const selectSubscriptionRule = (ruleId) => {
  subscriptionState.selectedId = ruleId;
  subscriptionState.titleEditing = false;
  syncSubscriptionEditor();
  generateSmartSandboxSample();
};

const startSubscriptionTitleEdit = () => {
  subscriptionState.titleBackup = subscriptionEditor.name || '';
  subscriptionState.titleEditing = true;
};

const finishSubscriptionTitleEdit = () => {
  const name = (subscriptionEditor.name || '').trim();
  subscriptionEditor.name = name || '未命名订阅';
  const rule = selectedSubscriptionRule.value;
  if (rule) {
    rule.name = subscriptionEditor.name;
    rule.updatedAt = toDateTimeString(new Date());
  }
  subscriptionState.titleEditing = false;
};

const cancelSubscriptionTitleEdit = () => {
  subscriptionEditor.name = subscriptionState.titleBackup;
  subscriptionState.titleEditing = false;
};

const createSubscriptionRule = () => {
  const id = `sub-${Date.now()}`;
  const rule = {
    id,
    name: '新建订阅规则',
    owner: '',
    enabled: true,
    status: 'draft',
    topics: [],
    minSeverity: 'HIGH',
    riskMin: 70,
    sources: ['Telegram'],
    channels: ['Dashboard'],
    schedule: '每 15 分钟',
    desc: '',
    regionFocus: '',
    bizTagFocus: '',
    dedupKey: '不过滤 (每条独立推送)',
    dedupWindow: 30,
    rateLimit: 50,
    overflowAction: '静默丢弃',
    internalUserIds: '',
    internalGroupIds: 'g_riskOps',
    externalDashboard: true,
    webhookUrls: '',
    telegramIds: '@ops_channel',
    priority: 50,
    note: '',
    rbacVisibility: '仅自己',
    editorIds: '',
    updatedAt: toDateTimeString(new Date())
  };
  subscriptionRules.value.unshift(rule);
  subscriptionState.selectedId = id;
  syncSubscriptionEditor();
};

const saveSubscriptionDraft = () => {
  const err = validateSubscriptionEditor();
  if (err) {
    alertMock(err);
    return;
  }
  const rule = persistSubscriptionEditor();
  if (!rule) return;
  rule.status = 'draft';
  generateSmartSandboxSample();
  alertMock('订阅规则草稿已保存');
};

const upsertMonitorTaskFromSubscription = (rule) => {
  const matched = monitorTopics.value.find((item) => item.subscriptionRuleId === rule.id);
  const task = {
    name: `订阅监测｜${rule.name}`,
    status: rule.enabled ? '运行中' : '已暂停',
    schedule: rule.schedule,
    coverage: Math.min(98, 55 + (rule.topics.length * 8) + (rule.sources.length * 4)),
    hits24h: Math.max(6, Math.round(subscriptionSandbox.value.hit * 0.5)),
    pendingReview: Math.max(1, Math.round(subscriptionSandbox.value.drop * 0.2)),
    sources: [...rule.sources]
  };

  if (matched) {
    Object.assign(matched, task);
    return;
  }

  monitorTopics.value.unshift({
    id: Date.now(),
    subscriptionRuleId: rule.id,
    ...task
  });
};

const publishSubscriptionRule = () => {
  const err = validateSubscriptionEditor();
  if (err) {
    alertMock(err);
    return;
  }
  const rule = persistSubscriptionEditor();
  if (!rule) return;
  rule.status = 'applied';
  upsertMonitorTaskFromSubscription(rule);
  alertMock(`订阅规则已发布：将对 ${rule.topics.map(getTopicName).join(' / ')} 执行监测`);
};

const deleteSubscriptionRule = () => {
  const rule = selectedSubscriptionRule.value;
  if (!rule) return;
  if (!confirm('确定删除当前订阅规则吗？')) return;
  subscriptionRules.value = subscriptionRules.value.filter((item) => item.id !== rule.id);
  monitorTopics.value = monitorTopics.value.filter((item) => item.subscriptionRuleId !== rule.id);
  subscriptionState.selectedId = subscriptionRules.value[0]?.id || '';
  ensureSubscriptionSelection();
};

const openSubscriptionInAlerts = (rule) => {
  if (!rule) return;
  resetAlertFiltersByPreset();
  state.activeModule = 'alerts';
  filters.topic = rule.topics[0] || 'all';
  filters.media = rule.sources[0] || 'all';
  state.searchQuery = rule.name || '';
};
const toggleImmersiveMode = () => {
  state.isImmersive = !state.isImmersive;
  state.leftCollapsed = state.rightCollapsed = state.isFilterCollapsed = state.isImmersive;
};

const toggleFollowMute = (item) => {
  item.muted = !item.muted;
};

const toggleMonitorStatus = (item) => {
  item.status = item.status === '运行中' ? '已暂停' : '运行中';
};

const runMonitorNow = (item) => {
  item.hits24h += Math.floor(Math.random() * 3);
  alertMock(`已触发「${item.name}」立即运行`);
};

const toggleTopicStatus = (topic) => {
  if (topic.status === '归档') {
    alertMock('归档专题请先恢复后再启动');
    return;
  }
  topic.status = topic.status === '运行中' ? '已暂停' : '运行中';
};

const toggleCustomDate = () => {
  state.showCustomDate = !state.showCustomDate;
  filters.time = state.showCustomDate ? 'custom' : '7days';
};

const toggleSidebarFilter = (type, val) => { filters[type] = filters[type] === val ? 'all' : val; state.pagination.currentPage = 1; };
const resetFilters = () => { Object.keys(filters).forEach(k => filters[k] = 'all'); filters.time = '7days'; state.searchQuery = ''; state.showCustomDate = false; state.sort = 'time-desc'; state.pagination.currentPage = 1; };
const saveFilters = () => alert('筛选条件已保存');

const markAsRead = (item) => item.read = true;
const markFalsePositive = (item) => {
  if (confirm('确定将此线索标记为“误报/噪音”吗？\n标记后该线索将从待办列表和统计图中彻底剔除。')) {
    item.falsePositive = true; item.selected = false;
  }
};
const mockTranslate = (e) => {
  const btn = e.currentTarget;
  if(btn.classList.contains('translated')) return;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 翻译中...'; btn.style.opacity = '0.8';
  setTimeout(() => {
    btn.innerHTML = '<i class="fa-solid fa-check"></i> 已翻译';
    btn.classList.add('translated'); btn.style.color = '#10b981'; btn.style.borderColor = '#10b981'; btn.style.background = 'rgba(16, 185, 129, 0.1)';
  }, 800);
};

const alertMock = (msg) => alert(msg);
const exportSelected = () => alert('导出选中项成功！');
const exportAll = () => alert('导出全部数据成功！');
const exportSingle = (item) => alert(`导出单条记录: ${item.title}`);

// 模态框逻辑
const openDetail = (item, parentItem = null) => { 
  state.selectedDetailItem = Object.assign({}, parentItem || item, item); // 继承父级属性
  state.selectedDetailItem.read = true;
  state.isModalOpen = true; 
};
const closeModal = () => { state.isModalOpen = false; setTimeout(() => state.selectedDetailItem = null, 300); };

// === 6. 右侧边栏动态数据计算 ===
const topRegions = computed(() => {
  const stats = {}; filteredList.value.forEach(i => { let k = getProvince(i.region); stats[k] = (stats[k] || 0) + 1; });
  const sorted = Object.entries(stats).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
  return sorted.map(item => ({ ...item, percent: (item.count / (sorted[0]?.count || 1)) * 100 }));
});
const getRegionColor = (i) => ['linear-gradient(90deg, #ff9a9e 0%, #fecfef 100%)', 'linear-gradient(90deg, #fbc2eb 0%, #a6c1ee 100%)', 'linear-gradient(90deg, #84fab0 0%, #8fd3f4 100%)', 'linear-gradient(90deg, #a6c0fe 0%, #f68084 100%)', 'linear-gradient(90deg, #fad0c4 0%, #ffd1ff 100%)'][i % 5];
const prevRegionSlide = () => { if(state.carousel.region > 0) state.carousel.region--; };
const nextRegionSlide = () => { if(state.carousel.region < Math.floor(topRegions.value.length/5)) state.carousel.region++; };

const topRules = computed(() => {
  const stats = {};
  baseFilteredList.value.forEach(item => {
    getRuleList(item).forEach(rule => {
      stats[rule] = (stats[rule] || 0) + 1;
    });
  });
  const sorted = Object.entries(stats).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count).slice(0, 5);
  return sorted.map(item => ({ ...item, percent: (item.count / (sorted[0]?.count || 1)) * 100 }));
});

const topAuthors = computed(() => {
  const stats = {}; filteredList.value.forEach(i => { stats[i.author] = (stats[i.author] || 0) + 1; });
  return Object.entries(stats).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
});
const prevAuthorSlide = () => { if(state.carousel.author > 0) state.carousel.author--; };
const nextAuthorSlide = () => { if(state.carousel.author < Math.floor(topAuthors.value.length/5)) state.carousel.author++; };

const generateDonutData = (dataKey, nameResolver) => {
  const stats = {}; let total = 0;
  filteredList.value.forEach(item => { if (item[dataKey]) { stats[item[dataKey]] = (stats[item[dataKey]] || 0) + 1; total++; } });
  const colors = ['#3b82f6', '#f59e0b', '#ec4899', '#06b6d4', '#f97316', '#10b981'];
  let conicGradient = []; let currentPercent = 0;
  const legend = Object.keys(stats).map((key, index) => {
    const color = colors[index % colors.length]; const percent = (stats[key] / total) * 100;
    conicGradient.push(`${color} ${currentPercent}% ${currentPercent + percent}%`); currentPercent += percent;
    return { key, count: stats[key], color, name: nameResolver(key) };
  });
  return { total, background: total > 0 ? `conic-gradient(${conicGradient.join(', ')})` : 'var(--bg-sidebar-right)', legend };
};
const topicChartData = computed(() => generateDonutData('topic', getTopicName));
const industryChartData = computed(() => generateDonutData('industry', getIndustryName));

ensureSubscriptionSelection();
</script>

<style scoped>
/* ====== 布局与侧边栏折叠 ====== */
.page-container { height: 100vh; display: flex; flex-direction: column; overflow: hidden; background: var(--bg-dark); }
.main-container { flex: 1; display: flex; overflow: hidden; padding: 10px; gap: 10px; position: relative; }

.sidebar { width: 165px; background: rgba(18, 26, 45, 0.7); border: 1px solid var(--border-color); display: flex; flex-direction: column; padding-top: 20px; flex-shrink: 0; clip-path: polygon(0 0, 100% 0, 100% 90%, 85% 100%, 0 100%); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.sidebar.collapsed { flex: 0 0 0 !important; width: 0 !important; padding: 0 !important; border: none !important; opacity: 0; }
.sidebar-item { padding: 15px 0 15px 20px; cursor: pointer; color: var(--text-main); display: flex; align-items: center; gap: 10px; transition: 0.3s; white-space: nowrap; border-left: 3px solid transparent; }
.sidebar-item:hover { background: var(--bg-hover); }
.sidebar-item.active { background: linear-gradient(90deg, rgba(59,130,246,0.2) 0%, rgba(0,0,0,0) 100%); border-left: 3px solid var(--accent-blue); color: var(--accent-blue); }

.analysis-sidebar { width: 320px; background: var(--bg-sidebar-right); border: 1px solid var(--border-color); padding: 15px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; flex-shrink: 0; border-radius: 6px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); transform-origin: right center; }
.analysis-sidebar.collapsed { flex: 0 0 0 !important; width: 0 !important; padding: 0 !important; border: none !important; opacity: 0; margin:0 !important; }

/* 折叠把手 */
.side-toggle-btn { position: absolute; top: 50%; transform: translateY(-50%); width: 16px; height: 60px; background: var(--bg-panel); border: 1px solid var(--border-color); color: var(--accent-blue); cursor: pointer; z-index: 100; display: flex; align-items: center; justify-content: center; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 15px rgba(0,0,0,0.5); }
.side-toggle-btn:hover { background: var(--bg-hover); color: #fff; }
.left-toggle-btn { left: 175px; border-left: none; border-radius: 0 8px 8px 0; }
.left-toggle-btn.collapsed { left: 10px; }
.right-toggle-btn { right: 330px; border-right: none; border-radius: 8px 0 0 8px; }
.right-toggle-btn.collapsed { right: 0; }

.content-area { flex: 1; display: flex; flex-direction: column; gap: 10px; overflow: hidden; position: relative; }
.content-body { display: flex; flex: 1; gap: 10px; overflow: hidden; position: relative; }
.list-section { flex: 1; display: flex; flex-direction: column; min-width: 0; gap: 10px; }

.module-header-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.15), rgba(15, 23, 42, 0.85));
  border: 1px solid rgba(59, 130, 246, 0.28);
  padding: 10px 14px;
  border-radius: 6px;
  flex-shrink: 0;
}
.module-main-title { color: #e2e8f0; font-size: 16px; font-weight: 700; }
.module-main-subtitle { color: #8ea5c4; font-size: 12px; margin-top: 2px; }
.module-main-count { color: #93c5fd; font-size: 12px; border: 1px solid rgba(59,130,246,.4); padding: 4px 10px; border-radius: 999px; }

.board-grid { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 10px; overflow: hidden; }
.summary-card {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  flex-shrink: 0;
}
.summary-item {
  background: rgba(18, 26, 45, 0.7);
  border: 1px solid rgba(71, 93, 132, 0.5);
  border-radius: 6px;
  padding: 10px 12px;
}
.summary-label { color: var(--text-dim); font-size: 12px; }
.summary-value { margin-top: 6px; color: #dbeafe; font-size: 22px; font-weight: 700; line-height: 1; }
.summary-value.danger { color: #fca5a5; }
.summary-value.mute { color: #94a3b8; }

.board-panel { flex: 1; min-height: 0; overflow: hidden; display: flex; flex-direction: column; padding: 12px; }
.panel-line-title {
  font-size: 14px;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  padding-bottom: 10px;
  margin-bottom: 10px;
}
.panel-line-title i { color: var(--accent-blue); }

.follow-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; overflow-y: auto; padding-right: 4px; }
.follow-card {
  background: linear-gradient(180deg, rgba(9,18,40,0.92), rgba(8,16,34,0.86));
  border: 1px solid rgba(49, 80, 134, 0.42);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: .2s;
}
.follow-card:hover { border-color: var(--accent-blue); transform: translateY(-1px); box-shadow: 0 6px 14px rgba(59,130,246,0.16); }
.follow-card.muted { opacity: .68; }
.follow-card.risk-high { border-left: 3px solid var(--accent-red); }
.follow-card.risk-mid { border-left: 3px solid var(--accent-orange); }
.follow-card.risk-low { border-left: 3px solid var(--accent-green); }
.follow-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.follow-name { color: #f8fafc; font-size: 14px; font-weight: 700; }
.follow-meta { color: #8ea5c4; font-size: 12px; margin-top: 2px; }
.risk-dot { font-size: 11px; border: 1px solid; border-radius: 999px; padding: 2px 8px; }
.risk-dot.high { color: #fca5a5; border-color: #ef4444; }
.risk-dot.mid { color: #fdba74; border-color: #f97316; }
.risk-dot.low { color: #86efac; border-color: #10b981; }
.follow-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.mini-tag { font-size: 11px; color: #bfdbfe; border: 1px solid rgba(96,165,250,.38); padding: 2px 8px; border-radius: 999px; background: rgba(59,130,246,.16); }
.follow-progress-row { display: grid; grid-template-columns: auto 1fr auto; gap: 8px; align-items: center; color: #9fb8da; font-size: 12px; }
.follow-foot { display: flex; justify-content: space-between; align-items: center; color: #9fb8da; font-size: 12px; gap: 10px; }
.follow-foot b { color: #dbeafe; }
.follow-actions { display: flex; gap: 8px; }

.chip-btn {
  border: 1px solid rgba(71, 93, 132, 0.8);
  color: #cbd5e1;
  background: rgba(15, 23, 41, 0.6);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
  transition: .2s;
}
.chip-btn:hover { border-color: var(--accent-blue); color: #fff; }
.chip-btn.primary { border-color: var(--accent-blue); color: #dbeafe; background: rgba(59,130,246,.15); }

.monitor-table { overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-right: 4px; }
.monitor-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  background: rgba(15, 23, 41, 0.65);
  border: 1px solid rgba(49, 80, 134, 0.42);
  border-radius: 8px;
  padding: 12px;
}
.monitor-title { color: #f8fafc; font-size: 14px; font-weight: 700; }
.monitor-meta { color: #8ea5c4; font-size: 12px; margin-top: 4px; }
.monitor-progress { display: grid; grid-template-columns: auto 1fr auto; gap: 8px; align-items: center; font-size: 12px; color: #9fb8da; margin-top: 10px; }
.monitor-side { min-width: 180px; display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.status-badge { font-size: 11px; padding: 2px 8px; border: 1px solid; border-radius: 999px; }
.status-badge.on { color: #86efac; border-color: #10b981; background: rgba(16,185,129,.15); }
.status-badge.off { color: #fdba74; border-color: #f97316; background: rgba(249,115,22,.15); }
.status-badge.stop { color: #fca5a5; border-color: #ef4444; background: rgba(239,68,68,.15); }
.status-badge.archive { color: #94a3b8; border-color: #64748b; background: rgba(100,116,139,.15); }
.monitor-hit, .monitor-pending { color: #9fb8da; font-size: 12px; }
.monitor-actions { display: flex; gap: 8px; margin-top: 2px; }

.topic-list-grid { overflow-y: auto; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; padding-right: 4px; }
.topic-card {
  background: rgba(15, 23, 41, 0.7);
  border: 1px solid rgba(49, 80, 134, 0.42);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.topic-card:hover { border-color: var(--accent-blue); }
.topic-head { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.topic-name { color: #f1f5f9; font-size: 14px; font-weight: 700; }
.topic-desc { color: #9fb0c9; font-size: 12px; line-height: 1.55; }
.topic-meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; color: #8ea5c4; font-size: 12px; }
.topic-actions { display: flex; gap: 8px; justify-content: flex-end; }

.subscription-grid { min-height: 0; }
.cfg3-shell {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 260px minmax(560px, 1fr) 340px;
  gap: 10px;
}
.cfg3-left, .cfg3-main, .cfg3-side { min-height: 0; }
.cfg3-left { display: flex; flex-direction: column; overflow: hidden; }
.cfg3-main { display: flex; flex-direction: column; overflow-y: auto; }
.cfg3-side { display: flex; flex-direction: column; overflow-y: auto; }

.cfg3-left-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.cfg3-left .panel-line-title { margin-bottom: 0; border-bottom: 0; padding-bottom: 0; }
.cfg3-left .sub-list-toolbar { margin-top: 8px; margin-bottom: 8px; }

.cfg3-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.cfg3-toolbar-title { display: flex; align-items: center; gap: 8px; color: #dbeafe; font-weight: 700; font-size: 15px; }
.cfg3-toolbar-title i { color: var(--accent-blue); }
.cfg3-toolbar-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.cfg3-btn {
  border: 1px solid rgba(71, 93, 132, 0.75);
  background: rgba(15, 23, 41, 0.65);
  color: #dbeafe;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: .2s;
}
.cfg3-btn i { margin-right: 6px; }
.cfg3-btn.ghost:hover { border-color: var(--accent-blue); color: #fff; }
.cfg3-btn.primary { background: linear-gradient(90deg, rgba(59,130,246,.92), rgba(37,99,235,.92)); border-color: #3b82f6; color: #fff; }
.cfg3-btn.primary:hover { filter: brightness(1.08); }
.cfg3-btn.danger { background: rgba(239,68,68,.2); border-color: rgba(239,68,68,.65); color: #fecaca; }
.cfg3-btn.danger:hover { background: rgba(239,68,68,.35); color: #fff; }

.cfg3-headline {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}
.cfg3-title-edit {
  display: flex;
  align-items: center;
  gap: 8px;
}
.cfg3-headline h3 { margin: 0; color: #f8fafc; font-size: 22px; line-height: 1.12; letter-spacing: .1px; }
.cfg3-headline h3 { cursor: text; }
.cfg3-title-input {
  height: 42px;
  min-width: 360px;
  border: 1px solid rgba(71, 93, 132, 0.75);
  border-radius: 8px;
  background: rgba(20, 31, 55, 0.8);
  color: #f8fafc;
  font-size: 22px;
  font-weight: 700;
  padding: 0 12px;
}
.cfg3-title-input:focus { outline: none; border-color: #3b82f6; }
.cfg3-title-edit-btn {
  width: 28px;
  height: 28px;
  border: 1px solid rgba(71, 93, 132, 0.75);
  border-radius: 6px;
  background: rgba(15, 23, 41, 0.75);
  color: #9fb8da;
  cursor: pointer;
  transition: .2s;
}
.cfg3-title-edit-btn:hover { color: #fff; border-color: #3b82f6; }
.cfg3-headline p { margin: 6px 0 0; color: #9fb0c9; font-size: 12px; }
.cfg3-divider { margin: 0 6px; color: #64748b; }
.cfg3-enable-select {
  height: 38px;
  min-width: 120px;
  border: 1px solid rgba(71, 93, 132, 0.7);
  background: rgba(20, 30, 54, 0.8);
  color: #dbeafe;
  border-radius: 6px;
  padding: 0 10px;
  font-weight: 600;
}
.cfg3-enable-select.is-enabled {
  border-color: rgba(16, 185, 129, 0.75);
  color: #86efac;
  background: rgba(16, 185, 129, 0.08);
}
.cfg3-enable-select.is-disabled {
  border-color: rgba(239, 68, 68, 0.75);
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.08);
}
.cfg3-enable-tag {
  display: inline-flex;
  align-items: center;
  border: 1px solid;
  border-radius: 999px;
  height: 28px;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 700;
}
.cfg3-enable-tag.enabled {
  color: #86efac;
  border-color: rgba(16, 185, 129, 0.75);
  background: rgba(16, 185, 129, 0.14);
}
.cfg3-enable-tag.disabled {
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.75);
  background: rgba(239, 68, 68, 0.14);
}

.cfg3-steps {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}
.cfg3-step {
  appearance: none;
  border: 1px solid rgba(71, 93, 132, 0.45);
  text-align: left;
  border: 1px solid rgba(71, 93, 132, 0.45);
  border-radius: 8px;
  padding: 10px;
  background: rgba(14, 22, 40, 0.72);
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
  position: relative;
  transition: .2s;
}
.cfg3-step small { color: #7c93b3; font-size: 11px; }
.cfg3-step b { color: #dbeafe; font-size: 16px; line-height: 1.1; }
.cfg3-step span { color: #8ea5c4; font-size: 12px; }
.cfg3-step.active { border-color: rgba(59,130,246,.65); box-shadow: inset 0 -2px 0 rgba(59,130,246,.85); background: rgba(20,38,78,.22); }
.cfg3-step-dot {
  position: absolute;
  right: 14px;
  top: 12px;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(59,130,246,.2);
}
.cfg3-step.active .cfg3-step-dot {
  background: #3b82f6;
  box-shadow: 0 0 10px rgba(59,130,246,.7);
}

.cfg3-step-pane { margin-top: 10px; }
.cfg3-note-box {
  border: 1px solid rgba(71, 93, 132, 0.45);
  border-radius: 8px;
  background: rgba(28, 45, 84, 0.35);
  color: #9fb0c9;
  font-size: 15px;
  line-height: 1.7;
  padding: 16px 20px;
  margin-bottom: 12px;
}
.cfg3-two-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.cfg3-inner-card {
  border: 1px solid rgba(71, 93, 132, 0.4);
  border-radius: 8px;
  background: rgba(14, 22, 40, 0.68);
  padding: 14px;
}
.cfg3-inner-card h4 {
  margin: 0 0 12px;
  color: #dbeafe;
  font-size: 20px;
  line-height: 1.2;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  padding-bottom: 10px;
}
.cfg3-inner-card h4 i { font-size: 18px; color: #cbd5e1; }

.cfg3-mode-switch {
  margin-top: 12px;
  display: inline-flex;
  border: 1px solid rgba(71, 93, 132, 0.6);
  border-radius: 999px;
  padding: 3px;
  background: rgba(10, 18, 35, 0.8);
  width: fit-content;
}
.cfg3-mode-switch button {
  border: 0;
  padding: 6px 14px;
  border-radius: 999px;
  background: transparent;
  color: #8ea5c4;
  font-size: 12px;
  cursor: pointer;
}
.cfg3-mode-switch button.active { color: #fff; background: linear-gradient(90deg, rgba(236,72,153,.75), rgba(59,130,246,.7)); }

.cfg3-section-title { margin-top: 12px; margin-bottom: 8px; font-size: 13px; color: #93c5fd; display: flex; align-items: center; gap: 6px; }
.cfg3-topic-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 8px;
}
.cfg3-topic {
  border: 1px solid rgba(71, 93, 132, 0.55);
  background: rgba(15, 23, 41, 0.7);
  color: #9fb8da;
  border-radius: 8px;
  min-height: 66px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
}
.cfg3-topic i { font-size: 16px; }
.cfg3-topic span { font-size: 14px; }
.cfg3-topic.active { color: #86efac; border-color: rgba(16,185,129,.7); background: rgba(16,185,129,.14); }

.cfg3-form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; }
.cfg3-bottom-grid { margin-top: 10px; }
.cfg3-field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }
.cfg3-field label { color: #9fb0c9; font-size: 12px; display: flex; gap: 6px; align-items: center; }
.cfg3-channel-box {
  margin-top: 8px;
  border: 1px solid rgba(71, 93, 132, 0.4);
  border-radius: 8px;
  background: rgba(15, 23, 41, 0.58);
  padding: 10px;
}

.sub-list-toolbar { display: flex; gap: 8px; margin-bottom: 10px; }
.sub-search { width: 100%; }
.sub-rule-list { overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-right: 4px; }
.sub-rule-item {
  border: 1px solid rgba(71, 93, 132, 0.55);
  background: rgba(12, 20, 38, 0.75);
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  transition: .2s;
}
.sub-rule-item:hover { border-color: var(--accent-blue); }
.sub-rule-item.active {
  border-color: var(--accent-green);
  background: rgba(16, 185, 129, 0.12);
  box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.22);
}
.sub-rule-top { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.sub-rule-title { color: #e2e8f0; font-size: 14px; font-weight: 700; }
.sub-rule-meta { color: #8ea5c4; font-size: 12px; margin-top: 6px; line-height: 1.45; }
.sub-rule-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 11px; color: #94a3b8; }

.cfg3-main .sub-rule-list,
.cfg3-side .sub-rule-list,
.cfg3-left .sub-rule-list { flex: 1; }

.sub-input, .sub-select {
  width: 100%;
  height: 34px;
  border-radius: 6px;
  border: 1px solid rgba(71, 93, 132, 0.6);
  background: rgba(15, 23, 41, 0.75);
  color: #e2e8f0;
  padding: 0 10px;
}
.sub-select:focus, .sub-input:focus, .sub-textarea:focus { border-color: var(--accent-blue); outline: none; }
.sub-textarea {
  width: 100%;
  min-height: 72px;
  border-radius: 6px;
  border: 1px solid rgba(71, 93, 132, 0.6);
  background: rgba(15, 23, 41, 0.75);
  color: #e2e8f0;
  padding: 10px;
  resize: vertical;
}
.sub-block {
  margin-bottom: 10px;
  border: 1px solid rgba(71, 93, 132, 0.4);
  border-radius: 8px;
  background: rgba(15, 23, 41, 0.65);
  padding: 10px;
}
.sub-block-title { font-size: 12px; color: #bfdbfe; margin-bottom: 8px; display: flex; gap: 6px; align-items: center; }
.sub-chip-group { display: flex; flex-wrap: wrap; gap: 8px; }
.sub-check-chip {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  border-radius: 999px;
  border: 1px solid rgba(71, 93, 132, 0.6);
  padding: 4px 10px;
  background: rgba(20, 32, 58, 0.7);
  color: #cbd5e1;
  font-size: 12px;
}
.sub-check-chip input { accent-color: var(--accent-blue); }
.sub-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px; }
.chip-btn.danger {
  border-color: rgba(239, 68, 68, 0.7);
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.08);
}
.chip-btn.danger:hover { border-color: #ef4444; color: #fff; background: rgba(239, 68, 68, 0.2); }

.sub-sandbox-metric { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 10px; }
.sub-metric-box {
  border: 1px solid rgba(71, 93, 132, 0.6);
  border-radius: 8px;
  padding: 10px;
  background: rgba(14, 22, 40, 0.75);
  text-align: center;
}
.sub-metric-box div { font-size: 12px; color: #94a3b8; }
.sub-metric-box b { display: block; margin-top: 6px; color: #dbeafe; font-size: 22px; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
.sub-hint {
  margin-bottom: 10px;
  border-left: 3px solid var(--accent-blue);
  background: rgba(59,130,246,.1);
  padding: 10px;
  border-radius: 6px;
  color: #bfdbfe;
  font-size: 12px;
  line-height: 1.6;
}
.sub-preview-card {
  border: 1px solid rgba(71, 93, 132, 0.6);
  border-radius: 8px;
  background: rgba(14, 22, 40, 0.75);
  padding: 10px;
  margin-bottom: 10px;
}
.sub-preview-title { font-size: 13px; color: #e2e8f0; margin-bottom: 8px; font-weight: 700; }
.sub-preview-line {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 8px;
  padding: 5px 0;
  font-size: 12px;
}
.sub-preview-line span { color: #94a3b8; }
.sub-preview-line b { color: #dbeafe; word-break: break-word; }


.cfg3-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 10px;
}
.cfg3-kpi {
  border: 1px solid rgba(71, 93, 132, 0.6);
  border-radius: 8px;
  background: rgba(14, 22, 40, 0.75);
  padding: 10px;
  text-align: center;
}
.cfg3-kpi span { font-size: 12px; color: #8ea5c4; }
.cfg3-kpi b { display: block; margin-top: 6px; font-size: 28px; line-height: 1; font-weight: 800; }
.cfg3-kpi:nth-child(1) b { color: #34d399; text-shadow: 0 0 10px rgba(52, 211, 153, 0.35); }
.cfg3-kpi:nth-child(2) b { color: #60a5fa; text-shadow: 0 0 10px rgba(96, 165, 250, 0.35); }
.cfg3-kpi:nth-child(3) b { color: #f59e0b; text-shadow: 0 0 10px rgba(245, 158, 11, 0.35); }
.cfg3-kpi:nth-child(4) b { color: #94a3b8; text-shadow: 0 0 10px rgba(148, 163, 184, 0.3); }

.cfg3-warn {
  border: 1px solid rgba(249,115,22,.45);
  background: rgba(249,115,22,.1);
  border-radius: 8px;
  padding: 10px;
  color: #fdba74;
  font-size: 12px;
  line-height: 1.6;
}

.cfg3-sim-title { margin: 10px 0 8px; color: #dbeafe; font-size: 14px; font-weight: 700; }
.cfg3-sim-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
.cfg3-json-preview {
  margin: 0 0 8px;
  border: 1px solid rgba(71, 93, 132, 0.6);
  border-radius: 8px;
  background: rgba(15, 23, 41, 0.92);
  color: #c7d2fe;
  font-size: 12px;
  line-height: 1.5;
  padding: 10px;
  max-height: 210px;
  overflow: auto;
}

.cfg3-json-input {
  width: 100%;
  min-height: 160px;
  border: 1px solid rgba(71, 93, 132, 0.65);
  border-radius: 8px;
  background: rgba(30, 43, 70, 0.72);
  color: #dbeafe;
  padding: 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.55;
  resize: vertical;
  margin-bottom: 10px;
}
.cfg3-json-input:focus { outline: none; border-color: #3b82f6; }

.cfg3-result-list { display: flex; flex-direction: column; gap: 10px; }

.cfg3-hit-card {
  border: 1px solid rgba(71, 93, 132, 0.6);
  border-radius: 8px;
  background: rgba(10, 17, 32, 0.86);
  padding: 10px;
}
.cfg3-hit-card.hit {
  border-color: rgba(52, 211, 153, 0.55);
  background: rgba(16, 74, 58, 0.22);
}
.cfg3-hit-card.miss {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(80, 23, 42, 0.16);
}
.cfg3-hit-card.block {
  border-color: rgba(249, 115, 22, 0.45);
  background: rgba(99, 56, 21, 0.2);
}
.cfg3-hit-card.bad {
  border-color: rgba(239, 68, 68, 0.55);
  background: rgba(127, 29, 29, 0.26);
}
.cfg3-hit-title { color: #dbeafe; font-size: 13px; font-weight: 700; margin-bottom: 8px; }
.cfg3-hit-line { color: #8ea5c4; font-size: 12px; margin-bottom: 4px; }
.cfg3-badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.cfg3-mini-badge {
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(100, 116, 139, 0.5);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  line-height: 1;
  color: #cbd5e1;
  background: rgba(30, 41, 59, 0.5);
}
.cfg3-mini-badge.ok {
  border-color: rgba(16, 185, 129, 0.6);
  color: #86efac;
  background: rgba(16, 185, 129, 0.12);
}
.cfg3-mini-badge.warn {
  border-color: rgba(249, 115, 22, 0.6);
  color: #fdba74;
  background: rgba(249, 115, 22, 0.12);
}
.cfg3-mini-badge.bad {
  border-color: rgba(239, 68, 68, 0.65);
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.14);
}
.cfg3-mini-badge.neutral {
  border-color: rgba(100, 116, 139, 0.6);
  color: #94a3b8;
  background: rgba(51, 65, 85, 0.35);
}
.cfg3-pill {
  margin-top: 6px;
  border: 1px solid rgba(71, 93, 132, 0.8);
  border-radius: 999px;
  padding: 4px 10px;
  background: rgba(30, 64, 175, 0.18);
  color: #bfdbfe;
  font-size: 12px;
  cursor: pointer;
}
@media (max-width: 1180px) {
  .cfg3-shell { grid-template-columns: 1fr; }
  .cfg3-left { max-height: 240px; }
  .cfg3-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .cfg3-steps { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .cfg3-topic-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

/* ====== 筛选面板与自定义时间 ====== */
.filter-panel { background: var(--bg-panel); border: 1px solid var(--border-color); padding: 10px 15px 5px 15px; position: relative; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); transition: all 0.3s ease; flex-shrink: 0; z-index: 20; }
.filter-content { overflow: hidden; transition: max-height 0.3s ease, opacity 0.3s ease; max-height: 500px; opacity: 1; }
.filter-panel.collapsed .filter-content { max-height: 0; opacity: 0; margin-bottom: 0; }
.panel-header { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 5px; }
.panel-title { font-size: 16px; color: var(--text-main); }
.panel-actions button { padding: 4px 15px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; margin-left: 10px; background: rgba(0,0,0,0.3); color: var(--text-main); cursor: pointer; transition: all 0.2s; }
.panel-actions button:hover { border-color: var(--accent-blue); }
.panel-actions button.primary { background: rgba(59, 130, 246, 0.2); border-color: var(--accent-blue); color: var(--accent-blue); }
.panel-actions button.primary:hover { background: rgba(59, 130, 246, 0.3); }

.filter-grid { display: grid; grid-template-columns: 80px 1fr 80px 1fr; gap: 12px; font-size: 12px; padding-bottom: 10px; }
.filter-label { color: var(--text-dim); text-align: right; padding-top: 6px; white-space: nowrap; }
.filter-options { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.chip { padding: 4px 12px; border-radius: 12px; cursor: pointer; color: var(--text-dim); border: 1px solid transparent; transition: all 0.2s; }
.chip:hover { color: var(--accent-blue); border: 1px solid rgba(59, 130, 246, 0.3); }
.chip.active { color: var(--accent-blue); background: var(--bg-active); border: 1px solid var(--border-color); font-weight: 500; }

.time-picker-btn { color: var(--text-dim); cursor: pointer; display: flex; align-items: center; gap: 5px; border: 1px solid transparent; padding: 4px 12px; border-radius: 12px; transition: all 0.2s; }
.time-picker-btn:hover, .time-picker-btn.active { color: var(--accent-blue); border-color: var(--border-color); background: rgba(0,0,0,0.2); }
.custom-date-range { display: none; align-items: center; gap: 5px; margin-left: 10px; }
.custom-date-range.show { display: flex; animation: fadeInRight 0.3s; }
.date-input { background: #1e293b; border: 1px solid var(--border-color); color: var(--text-main); padding: 2px 5px; border-radius: 4px; font-size: 11px; }
.date-input:focus { border-color: var(--accent-blue); }

.toggle-btn { position: absolute; bottom: -12px; left: 50%; transform: translateX(-50%); background: var(--bg-panel); border: 1px solid var(--border-color); border-top: none; border-radius: 0 0 10px 10px; padding: 2px 20px; color: var(--accent-blue); cursor: pointer; z-index: 10; font-size: 12px; transition: all 0.2s; }
.toggle-btn:hover { background: var(--bg-hover); }

/* 科技角 */
.tech-corner-tl, .tech-corner-tr, .tech-corner-bl, .tech-corner-br { position: absolute; width: 10px; height: 10px; }
.tech-corner-tl { top: 0; left: 0; border-top: 2px solid var(--accent-blue); border-left: 2px solid var(--accent-blue); }
.tech-corner-tr { top: 0; right: 0; border-top: 2px solid var(--accent-blue); border-right: 2px solid var(--accent-blue); }
.tech-corner-bl { bottom: 0; left: 0; border-bottom: 2px solid var(--accent-blue); border-left: 2px solid var(--accent-blue); }
.tech-corner-br { bottom: 0; right: 0; border-bottom: 2px solid var(--accent-blue); border-right: 2px solid var(--accent-blue); }

/* ====== 工具栏与排序下拉 ====== */
.list-toolbar { display: flex; justify-content: space-between; align-items: center; padding: 10px; background: rgba(18, 26, 45, 0.5); flex-shrink: 0; }
.toolbar-left, .toolbar-right { display: flex; gap: 15px; align-items: center; }

.select-box { background: #1e293b; border: 1px solid var(--border-color); color: var(--text-main); padding: 5px 10px; font-size: 12px; cursor: pointer; position: relative; border-radius: 4px; transition: all 0.2s; min-width: 130px; }
.select-box:hover { border-color: var(--accent-blue); background: var(--bg-hover); }
.select-box.open { border-color: var(--accent-blue); background: var(--bg-hover); border-bottom-left-radius: 0; border-bottom-right-radius: 0; }
.select-box i.fa-caret-down { transition: transform 0.3s ease; }
.select-box.open i.fa-caret-down { transform: rotate(180deg); }

.select-dropdown { position: absolute; top: 100%; left: -1px; background: var(--bg-panel); border: 1px solid var(--accent-blue); width: calc(100% + 2px); display: none; z-index: 100; border-top: none; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; overflow: hidden; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3); }
.select-box.open .select-dropdown { display: block; animation: slideDown 0.2s ease; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.select-option { padding: 8px 12px; cursor: pointer; font-size: 12px; transition: all 0.2s; border-left: 3px solid transparent; color: var(--text-dim); }
.select-option:hover { background: var(--bg-hover); color: var(--accent-blue); border-left-color: var(--accent-blue); }
.select-option.active { color: var(--accent-blue); background: var(--bg-active); border-left-color: var(--accent-blue); font-weight: 500; }
.select-option i { margin-right: 6px; width: 14px; text-align: center; }

:deep(.clear-filter-btn) { margin-left: 12px; color: #fca5a5; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 4px; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); }
:deep(.clear-filter-btn:hover) { background: rgba(239, 68, 68, 0.25); color: #fff; border-color: rgba(239, 68, 68, 0.6); }

/* 按钮群 */
.immersive-btn { background: transparent; color: var(--text-dim); border: 1px solid var(--border-color); padding: 5px 12px; border-radius: 4px; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 6px; font-size: 13px; margin-right: 10px; }
.immersive-btn:hover { color: var(--accent-blue); border-color: var(--accent-blue); background: var(--bg-hover); }
.immersive-btn.active { color: var(--accent-orange); border-color: var(--accent-orange); background: rgba(249, 115, 22, 0.1); box-shadow: 0 0 10px rgba(249, 115, 22, 0.2); }

.search-input { background: #1e293b; border: 1px solid var(--border-color); color: var(--text-main); padding: 5px 10px; width: 200px; border-radius: 4px; transition: border-color 0.2s; }
.search-input:focus { border-color: var(--accent-blue); }
.manage-btn { background: var(--accent-blue); color: #fff; padding: 5px 15px; font-weight: 500; border-radius: 4px; cursor: pointer; border: none; transition: all 0.2s; }
.manage-btn:hover { background: #2563eb; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
.export-btn { background: var(--accent-green); color: #fff; padding: 5px 15px; font-weight: 500; border-radius: 4px; cursor: pointer; margin-left: 10px; border: none; transition: all 0.2s; }
.export-btn:hover { background: #059669; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
.export-btn:disabled { opacity: 0.5; cursor: not-allowed; background: #475569; }

/* ====== 列表项通用 ====== */
.list-container { flex: 1; overflow-y: auto; padding-right: 5px; }
.list-item-wrapper { position: relative; }
.list-item { background: linear-gradient(180deg, rgba(9, 18, 40, 0.94) 0%, rgba(8, 16, 34, 0.88) 100%); border: 1px solid rgba(49, 80, 134, 0.42); padding: 15px 16px 52px; display: flex; gap: 15px; position: relative; cursor: pointer; transition: all 0.2s; border-radius: 6px; overflow: hidden; }
.list-item:hover { border-color: var(--accent-blue); box-shadow: 0 0 15px rgba(59, 130, 246, 0.1); transform: translateY(-2px); }
.list-item.read { background: linear-gradient(180deg, rgba(9, 18, 40, 0.94) 0%, rgba(8, 16, 34, 0.88) 100%); border-color: rgba(63, 88, 138, 0.38); box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02); }
.list-item.read .item-title { color: #f8fbff; font-weight: 700; }
.list-item.read .item-desc { color: rgba(226, 232, 240, 0.92); }
.list-item.read .meta-item { color: #9fb0c9; }
.list-item.read .meta-value { color: #4d8dff; }
.list-item.read .item-meta-time { color: #9fb0c9; }
.list-item.read .item-source-icon { color: #f6c453; }
.list-item.read .badge { opacity: 1; filter: none; }
.list-item.read .tag { color: #dbe7ff; }
.list-item.read .entity-tag { opacity: 1; }
.list-item.selected { border-color: var(--accent-green); background: var(--bg-selected); box-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }

.checkbox-area { padding-top: 5px; }
.item-content { flex: 1; }
.item-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.item-title-wrap { display: flex; align-items: center; gap: 10px; min-width: 0; }
.item-source-icon { color: #f6c453; width: 18px; text-align: center; flex-shrink: 0; margin-top: 2px; }
.item-title { font-size: 15px; font-weight: 700; color: #f8fbff; transition: color 0.3s; line-height: 1.35; }
.item-desc { font-size: 13px; color: rgba(226, 232, 240, 0.92); line-height: 1.65; margin-bottom: 12px; display: -webkit-box; line-clamp: 2; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.item-meta { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; font-size: 12px; color: var(--text-dim); margin-bottom: 10px; position: relative; padding-right: 180px; }
.meta-item { color: #9fb0c9; }
.meta-value { color: #4d8dff; font-weight: 500; }
.item-meta-time { position: absolute; right: 0; top: 0; color: #9fb0c9; font-size: 11px; }

/* 风险标签 */
.badge { font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid; font-weight: 500; height: 20px; display: inline-flex; align-items: center; justify-content: center; min-width: 40px; margin-left: auto; }
.badge.high { color: var(--accent-red); border-color: var(--accent-red); background: rgba(239, 68, 68, 0.1); }
.badge.mid { color: var(--accent-orange); border-color: var(--accent-orange); background: rgba(249, 115, 22, 0.1); }
.badge.low { color: var(--accent-green); border-color: var(--accent-green); background: rgba(16, 185, 129, 0.1); }

/* 实体标签 */
.tag-row { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; align-items: center; }
.tag { border: 1px solid rgba(68, 90, 128, 0.55); padding: 4px 12px; border-radius: 999px; color: #dbe7ff; display: flex; align-items: center; gap: 6px; font-size: 12px; background: rgba(31, 46, 78, 0.5); transition: all 0.2s; }
.tag.clickable-tag { cursor: pointer; }
.tag.clickable-tag:hover { background: var(--accent-blue); color: #fff; border-color: var(--accent-blue); transform: translateY(-1px); box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3); }
.tag i { color: var(--accent-blue); }
.tag-topic { background: rgba(37, 99, 235, 0.12); border-color: rgba(78, 127, 255, 0.45); }
.tag-industry { background: rgba(255, 255, 255, 0.03); }
.clickable-author:hover { color: var(--accent-blue) !important; text-decoration: underline; cursor: pointer; }

.entity-tag { border: 1px solid transparent; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 500; display: flex; align-items: center; gap: 6px; cursor: pointer; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
.entity-id { background: rgba(59, 130, 246, 0.15); border-color: rgba(59, 130, 246, 0.4); color: #60a5fa; }
.entity-id:hover { background: #3b82f6; color: #fff; border-color: #3b82f6; box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3); }
.entity-money { background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.4); color: #fbbf24; }
.entity-money:hover { background: #f59e0b; color: #fff; border-color: #f59e0b; box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3); }
.entity-loc { background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.4); color: #34d399; }
.entity-loc:hover { background: #10b981; color: #fff; border-color: #10b981; box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3); }
.entity-logistics { background: rgba(249, 115, 22, 0.15); border-color: rgba(249, 115, 22, 0.4); color: #fb923c; }
.entity-logistics:hover { background: #f97316; color: #fff; border-color: #f97316; box-shadow: 0 4px 8px rgba(249, 115, 22, 0.3); }
.entity-slang { background: rgba(168, 85, 247, 0.15); border-color: rgba(168, 85, 247, 0.4); color: #c084fc; }
.entity-slang:hover { background: #a855f7; color: #fff; border-color: #a855f7; box-shadow: 0 4px 8px rgba(168, 85, 247, 0.3); }

/* ====== Telegram 专属样式 ====== */
.telegram-message-item { display: flex; gap: 12px; padding: 15px; background: rgba(15, 23, 41, 0.7); border: 1px solid rgba(38, 51, 77, 0.5); border-radius: 4px; transition: all 0.2s; position: relative; cursor: pointer; }
.telegram-message-item:hover { border-color: var(--accent-blue); box-shadow: 0 0 15px rgba(59, 130, 246, 0.1); transform: translateY(-2px); }
.telegram-message-item.read { background: rgba(15, 23, 41, 0.4); border-color: rgba(38, 51, 77, 0.3); }
.telegram-message-item.read .telegram-username { color: var(--text-dim); font-weight: normal; }
.telegram-message-item.selected { border-color: var(--accent-green); background: var(--bg-selected); box-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }

.telegram-avatar { width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0; overflow: hidden; border: 2px solid rgba(59, 130, 246, 0.3); }
.telegram-avatar img { width: 100%; height: 100%; object-fit: cover; }
.telegram-content { flex: 1; min-width: 0; }
.telegram-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.telegram-user-info { flex: 1; min-width: 0; }
.telegram-username { font-weight: 600; color: #fff; font-size: 14px; margin-bottom: 4px; display: block; }
.telegram-message-text { color: var(--text-main); line-height: 1.5; margin-bottom: 8px; font-size: 13px; word-break: break-word; display: -webkit-box; line-clamp: 2; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.telegram-meta { display: flex; align-items: center; font-size: 12px; color: var(--text-dim); margin-bottom: 8px; line-height: 1.4; gap: 15px; flex-wrap: wrap; position: relative; }
.telegram-source, .telegram-group-info { display: flex; align-items: center; gap: 5px; }
.telegram-group-name { color: var(--accent-blue); }
.telegram-time { position: absolute; right: 0; bottom: 0; color: var(--text-dim); font-size: 11px; }
.telegram-stats { display: flex; gap: 15px; font-size: 12px; color: var(--text-dim); margin-top: 8px; }
.telegram-actions { position: absolute; right: 15px; bottom: 15px; display: flex; gap: 10px; }

/* ====== 操作按钮 ====== */
.item-actions { position: absolute; right: 15px; bottom: 12px; display: flex; gap: 10px; }
.detail-btn, .export-item-btn, .fp-btn, .translate-btn { padding: 5px 12px; border: 1px solid; background: transparent; cursor: pointer; font-size: 12px; border-radius: 4px; transition: 0.2s; font-weight: 500; }
.detail-btn { border-color: var(--accent-blue); color: var(--accent-blue); }
.detail-btn:hover { background: rgba(59, 130, 246, 0.15); }
.export-item-btn { border-color: var(--accent-green); color: var(--accent-green); }
.export-item-btn:hover { background: rgba(16, 185, 129, 0.15); }
.fp-btn { border-color: var(--border-color); color: var(--text-dim); }
.fp-btn:hover { border-color: var(--accent-red); color: var(--accent-red); background: rgba(239, 68, 68, 0.15); box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); }
.translate-btn { border-color: #8b5cf6; color: #8b5cf6; }
.translate-btn:hover { background: rgba(139, 92, 246, 0.15); box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2); }

/* ====== 聚合线索 ====== */
.cluster-toggle-btn { background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.4); color: #c084fc; padding: 3px 10px; border-radius: 12px; font-size: 12px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; margin-left: 10px; }
.cluster-toggle-btn:hover { background: #8b5cf6; color: #fff; box-shadow: 0 0 10px rgba(139, 92, 246, 0.3); }
.cluster-toggle-btn i { transition: transform 0.3s ease; }
.cluster-toggle-btn.open i { transform: rotate(180deg); }

.nested-alerts-container { display: none; margin-top: 10px; margin-left: 30px; padding-left: 15px; border-left: 2px dashed rgba(59, 130, 246, 0.4); animation: slideDown 0.3s ease-out; }
.nested-alerts-container.show { display: block; }
.nested-item { background: rgba(15, 23, 41, 0.4); border: 1px solid rgba(38, 51, 77, 0.3); padding: 10px 15px; margin-bottom: 8px; border-radius: 4px; position: relative; transition: background 0.2s; }
.nested-item:hover { background: rgba(15, 23, 41, 0.8); border-color: rgba(59, 130, 246, 0.3); }
.nested-item::before { content: ''; position: absolute; left: -15px; top: 20px; width: 15px; height: 2px; background: dashed rgba(59, 130, 246, 0.4); }
.nested-header { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 13px; }
.nested-content { font-size: 12px; color: var(--text-dim); display: -webkit-box; line-clamp: 2; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* ====== 分页 ====== */
.pagination { display: flex; justify-content: center; align-items: center; padding: 10px; gap: 10px; font-size: 12px; flex-shrink: 0; }
.page-num { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; cursor: pointer; border-radius: 4px; transition: all 0.2s; }
.page-num:hover { background: var(--bg-hover); }
.page-num.active { background: var(--accent-blue); color: #fff; font-weight: 500; }
.page-arrow { color: var(--text-dim); cursor: pointer; transition: color 0.2s; }
.page-arrow:hover { color: var(--accent-blue); }
.page-info { color: var(--text-dim); margin-left: 10px; }

/* ====== 右侧分析栏组件 ====== */
.analysis-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.time-tabs { display: flex; background: #1e293b; border-radius: 15px; padding: 2px; font-size: 12px; }
.time-tab { padding: 4px 12px; border-radius: 12px; cursor: pointer; color: var(--text-dim); transition: all 0.2s; }
.time-tab:hover { color: var(--accent-blue); }
.time-tab.active { background: linear-gradient(90deg, var(--chart-blue) 0%, var(--chart-pink) 100%); color: #fff; font-weight: 500; }
.region-select { width: 100%; background: #1e293b; border: 1px solid var(--border-color); color: var(--text-main); padding: 8px; border-radius: 4px; font-size: 12px; outline: none; cursor: pointer; transition: border-color 0.2s; }
.region-select:hover { border-color: var(--accent-blue); }

.module-title { font-size: 14px; color: #fff; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; font-weight: 500; }
.module-title i { color: var(--chart-blue); }
.module-title::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(0,0,0,0) 100%); }

.rank-item { display: flex; align-items: center; font-size: 12px; margin-bottom: 8px; color: var(--text-dim); cursor: pointer; gap: 8px; transition: color 0.2s; }
.rank-item:hover { color: var(--accent-blue); }
.rank-item.active { color: var(--accent-blue); font-weight: 500; }
.rank-num { width: 20px; height: 20px; border: 1px solid #475569; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #fff; flex-shrink: 0;}
.progress-bg { flex: 1; height: 6px; background: #1e293b; border-radius: 3px; overflow: hidden; }
.progress-bar { height: 100%; border-radius: 3px; }

.chart-container { display: flex; justify-content: center; position: relative; margin: 10px 0; height: 140px; }
.donut-chart { width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background 0.3s; }
.donut-inner { width: 90px; height: 90px; background: var(--bg-sidebar-right); border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; }
.donut-label { font-size: 20px; font-weight: 600; }
.donut-sub { font-size: 12px; color: var(--text-dim); }

.chart-legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; font-size: 12px; margin-bottom: 20px; }
.legend-item { display: flex; align-items: center; gap: 5px; cursor: pointer; padding: 4px 8px; border-radius: 8px; transition: all 0.2s; color: var(--text-main); }
.legend-item:hover, .legend-item.active { color: var(--accent-blue); background: var(--bg-active); }
.legend-dot { width: 10px; height: 6px; border-radius: 2px; }

/* 轮播器 */
.author-list-container, .region-rank-container { margin-top: 10px; position: relative; overflow: hidden; }
.author-list-container { height: 220px; }
.region-rank-container { height: 160px; }
.author-list-wrapper, .region-rank-wrapper { position: relative; overflow: hidden; }
.author-list-wrapper { height: 220px; }
.region-rank-wrapper { height: 160px; }
.author-list-slide, .region-rank-slide { display: flex; flex-direction: column; transition: transform 0.5s ease; }

.author-list-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; margin-bottom: 8px; background: rgba(15, 23, 41, 0.7); border: 1px solid rgba(38, 51, 77, 0.5); border-radius: 6px; cursor: pointer; transition: all 0.3s; font-size: 13px; height: 38px;}
.author-list-item:hover, .author-list-item.active { border-color: var(--accent-blue); background: var(--bg-hover); transform: translateY(-2px); }
.author-rank-num { width: 22px; height: 22px; background: linear-gradient(135deg, var(--chart-blue), var(--chart-pink)); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 11px; color: #fff; font-weight: 600; flex-shrink: 0;}
.author-list-item.active .author-rank-num { background: linear-gradient(135deg, var(--accent-green), var(--accent-blue)); }
.author-name { color: var(--text-main); font-weight: 500; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding-right:10px;}
.author-count { color: #fff; font-weight: 600; font-size: 16px; background: linear-gradient(90deg, var(--chart-blue), var(--chart-cyan)); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
.author-count-unit { color: var(--text-dim); font-size: 12px; font-weight: normal; margin-left: 2px; }

.carousel-arrow { position: absolute; top: 50%; transform: translateY(-50%); width: 24px; height: 24px; background: rgba(59, 130, 246, 0.2); border: 1px solid var(--accent-blue); border-radius: 50%; color: var(--accent-blue); display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 10; transition: all 0.3s; opacity: 0; }
.author-list-container:hover .carousel-arrow, .region-rank-container:hover .carousel-arrow { opacity: 1; }
.carousel-arrow:hover { background: rgba(59, 130, 246, 0.4); }
.carousel-arrow.prev { left: 5px; }
.carousel-arrow.next { right: 5px; }

/* ====== 模态弹窗 ====== */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); z-index: 1000; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(5px); opacity: 0; pointer-events: none; transition: opacity 0.3s; }
.modal-overlay.open { opacity: 1; pointer-events: auto; }
.modal-box { width: 700px; max-width: 90%; background: var(--bg-panel); border: 1px solid var(--accent-blue); border-radius: 6px; box-shadow: 0 0 40px rgba(59, 130, 246, 0.25); display: flex; flex-direction: column; max-height: 85vh; transform: translateY(-20px); transition: transform 0.3s; }
.modal-overlay.open .modal-box { transform: translateY(0); }
.modal-header { padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); }
.modal-title { font-size: 16px; font-weight: 600; color: var(--accent-blue); display: flex; align-items: center; gap: 10px; }
.modal-close { cursor: pointer; color: var(--text-dim); font-size: 18px; transition: 0.2s; }
.modal-close:hover { color: #fff; }
.modal-body { padding: 0; overflow-y: auto; flex: 1; background: var(--bg-sidebar-right); }
.modal-footer { padding: 12px 20px; border-top: 1px solid rgba(255, 255, 255, 0.05); background: rgba(0, 0, 0, 0.3); display: flex; align-items: center; gap: 12px; flex-shrink: 0; border-radius: 0 0 6px 6px; }

.modal-btn { padding: 7px 16px; font-size: 13px; font-weight: 500; border-radius: 4px; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.2s; border: 1px solid transparent; color: #fff; }
.btn-tool { background: rgba(15, 23, 41, 0.8); border: 1px solid rgba(38, 51, 77, 0.8); color: var(--text-dim); }
.btn-tool.download-tool i { color: var(--accent-green); transition: color 0.3s; }
.btn-tool.download-tool:hover { border-color: var(--accent-green); background: rgba(16, 185, 129, 0.1); color: #fff; box-shadow: 0 0 12px rgba(16, 185, 129, 0.25); }
.btn-tool.graph-tool i { color: var(--chart-cyan); transition: color 0.3s; }
.btn-tool.graph-tool:hover { border-color: var(--chart-cyan); background: rgba(6, 182, 212, 0.1); color: #fff; box-shadow: 0 0 12px rgba(6, 182, 212, 0.25); }
.btn-tool.translate-tool i { color: #c084fc; transition: color 0.3s; }
.btn-tool.translate-tool:hover { border-color: #a855f7; background: rgba(168, 85, 247, 0.1); color: #fff; box-shadow: 0 0 12px rgba(168, 85, 247, 0.25); }
.modal-btn.btn-primary { background: var(--accent-blue); }
.modal-btn.btn-primary:hover { background: #2563eb; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
.modal-btn.btn-warning { background: var(--accent-orange); }
.modal-btn.btn-warning:hover { background: #ea580c; box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3); }

@media (max-width: 1380px) {
  .summary-card { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .follow-list, .topic-list-grid { grid-template-columns: 1fr; }
}

@media (max-width: 1024px) {
  .monitor-row { grid-template-columns: 1fr; }
  .monitor-side { min-width: 0; align-items: flex-start; }
  .topic-meta-grid { grid-template-columns: 1fr; }
}
</style>