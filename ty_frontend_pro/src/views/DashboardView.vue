<template>
  <div class="page-container dashboard-page">
    <AppHeader />
    
    <div class="main-container">
      <aside class="sidebar" :class="{ 'collapsed': state.leftCollapsed }">
        <div class="sidebar-item" :class="{ active: state.activeModule === 'follow' }" @click="switchModule('follow')"><i class="fa-regular fa-heart"></i> <span>我的关注</span></div>
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

            <div v-if="alertListLoading" class="alert-list-loading">
              <div class="loading-spinner"></div>
              <span>加载告警列表...</span>
            </div>
            <div v-else-if="alertListError" class="alert-list-error">
              <span>{{ alertListError }}</span>
              <button class="retry-btn" @click="fetchAlertList">重试</button>
            </div>
            <template v-else>
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
                    <div v-if="item.translatedContent" class="item-desc translated-content" style="color:#10b981;border-left:2px solid #10b981;padding-left:8px;margin-top:4px;">{{ item.translatedContent }}</div>
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
                    <button class="follow-btn" :class="{ active: item.followed }" @click.stop="toggleAlertFollow(item)"><i class="fa-regular" :class="item.followed ? 'fa-heart-circle-check' : 'fa-heart'"></i> {{ item.followed ? '已关注' : '关注' }}</button>
                    <button v-if="!item.authorFollowed" class="follow-btn author-follow-btn" @click.stop="followAuthor(item)"><i class="fa-solid fa-user-plus"></i> 关注作者</button>
                    <button v-else class="follow-btn author-follow-btn active" @click.stop="unfollowAuthor(item)"><i class="fa-solid fa-user-check"></i> 已关注作者</button>
                    <button class="fp-btn" @click.stop="markFalsePositive(item)"><i class="fa-solid fa-ban"></i> 误报</button>
                    <button class="translate-btn" @click.stop="translateItem(item, $event)"><i class="fa-solid fa-language"></i> 翻译</button>
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
          </template>
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
          <div class="board-grid">
            <div class="summary-card">
              <div class="summary-item">
                <div class="summary-label">关注线索总数</div>
                <div class="summary-value">{{ followSummary.total }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">高危线索</div>
                <div class="summary-value danger">{{ followSummary.high }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">中危线索</div>
                <div class="summary-value">{{ followSummary.mid }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">低危线索</div>
                <div class="summary-value mute">{{ followSummary.low }}</div>
              </div>
            </div>

            <div class="panel board-panel">
              <div class="panel-line-title"><i class="fa-regular fa-heart"></i> 我的关注清单</div>
              <div v-if="followLoading" class="alert-list-loading">
                <div class="loading-spinner"></div>
                <span>加载关注列表...</span>
              </div>
              <div v-else-if="followError" class="alert-list-error">
                <span>{{ followError }}</span>
                <button class="retry-btn" @click="fetchFollowList">重试</button>
              </div>
              <div v-else-if="followedAlerts.length === 0" style="padding: 24px; color: var(--text-dim);">暂无关注线索，请在告警信息列表点击"关注"按钮。</div>
              <div v-else class="topic-list-grid">
                <div v-for="item in followedAlerts" :key="item.id" class="topic-card" @click="openFollowedAlertInAlerts(item)">
                  <div class="topic-head">
                    <div class="topic-name">{{ getDisplayTitle(item) }}</div>
                    <span class="status-badge" :class="item.risk === 'high' ? 'danger' : item.risk === 'mid' ? 'warn' : 'on'">{{ getRiskText(item.risk) }}</span>
                  </div>
                  <div class="topic-desc">{{ item.content }}</div>
                  <div class="topic-meta-grid">
                    <span>作者：{{ item.author }}</span>
                    <span>来源：{{ item.source }}</span>
                    <span>专题：{{ getTopicName(item.topic) }}</span>
                    <span>时间：{{ formatTime(item.date) }}</span>
                  </div>
                  <div class="topic-actions">
                    <button class="chip-btn" @click.stop="toggleAlertFollow(item)">取消关注</button>
                    <button class="chip-btn primary" @click.stop="openDetail(item)">查看详情</button>
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
                  <div class="cfg3-left-title-wrap">
                    <div class="panel-line-title"><i class="fa-solid fa-layer-group"></i> 订阅规则</div>
                    <div class="cfg3-left-subtitle">共 {{ filteredSubscriptionRules.length }} 条规则，点击左侧卡片可切换编辑</div>
                  </div>
                  <button class="chip-btn primary" @click="createSubscriptionRule"><i class="fa-solid fa-plus"></i> 新建</button>
                </div>
                <div class="sub-list-toolbar">
                  <input v-model="subscriptionState.search" class="sub-input sub-search" placeholder="搜索：名称 / 专题 / 负责人 / 分发对象">
                </div>
                <div v-if="topicListLoading" class="sub-list-skeleton">
                  <div v-for="n in 3" :key="'sk-'+n" class="sub-skeleton-card"></div>
                </div>
                <div v-else-if="topicListError" class="sub-list-error">
                  <span>{{ topicListError }}</span>
                  <button class="chip-btn" @click="fetchTopicList">重试</button>
                </div>
                <div v-else-if="filteredSubscriptionRules.length === 0" class="sub-empty-state">
                  <i class="fa-regular fa-folder-open"></i>
                  <div class="sub-empty-title">暂无匹配规则</div>
                  <div class="sub-empty-desc">尝试清空搜索条件，或新建一条订阅规则</div>
                  <button class="chip-btn primary" @click="createSubscriptionRule"><i class="fa-solid fa-plus"></i> 新建规则</button>
                </div>
                <div v-else class="sub-rule-list">
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
                    <span v-if="configLoading" class="cfg3-config-loading"><i class="fa-solid fa-spinner fa-spin"></i> 加载配置...</span>
                  </div>
                  <div class="cfg3-toolbar-actions">
                    <button class="cfg3-btn ghost" @click="openHistory"><i class="fa-solid fa-clock-rotate-left"></i>版本历史</button>
                    <button class="cfg3-btn danger" :disabled="deletingRule" @click="deleteSubscriptionRule"><i class="fa-solid fa-trash-can"></i>{{ deletingRule ? '删除中...' : '删除' }}</button>
                    <button class="cfg3-btn ghost" :disabled="savingSubscription" @click="saveSubscriptionDraft">
                      <i class="fa-solid fa-floppy-disk"></i>{{ savingSubscription ? '保存中...' : '保存草稿' }}
                    </button>
                    <button class="cfg3-btn primary" :disabled="savingSubscription" @click="publishSubscriptionRule">
                      <i class="fa-solid fa-bolt"></i>{{ savingSubscription ? '提交中...' : '发布应用' }}
                    </button>
                  </div>
                </div>

                <!-- 版本历史面板 -->
                <template v-if="subscriptionState.showHistory">
                  <div class="cfg3-history-head">
                    <button class="cfg3-btn ghost" @click="closeHistory">
                      <i class="fa-solid fa-arrow-left"></i> 返回编辑
                    </button>
                    <span class="cfg3-history-title">
                      <i class="fa-solid fa-clock-rotate-left"></i>
                      版本历史 - {{ selectedSubscriptionRule?.name || '' }}
                    </span>
                  </div>

                  <div v-if="historyLoading" class="cfg3-history-loading">
                    <div class="loading-spinner"></div>
                    <span>加载历史记录...</span>
                  </div>
                  <div v-else-if="historyError" class="cfg3-history-error">
                    <span>{{ historyError }}</span>
                    <button class="retry-btn" @click="openHistory">重试</button>
                  </div>
                  <div v-else-if="!historyList.length" class="cfg3-history-empty">
                    <i class="fa-solid fa-inbox"></i>
                    <span>暂无历史版本记录</span>
                  </div>
                  <div v-else class="cfg3-history-list">
                    <div v-for="item in historyList" :key="item.history_id" class="cfg3-history-item">
                      <div class="cfg3-history-item-head" @click="historyExpandedId = historyExpandedId === item.history_id ? null : item.history_id">
                        <span class="cfg3-history-badge" :class="'action-' + item.action">
                          {{ item.action === 'apply' ? '已发布' : item.action === 'save_draft' ? '草稿保存' : item.action }}
                        </span>
                        <span class="cfg3-history-operator">{{ item.operator }}</span>
                        <span class="cfg3-history-time">{{ item.created_at }}</span>
                        <i class="fa-solid" :class="historyExpandedId === item.history_id ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                      </div>
                      <pre v-if="historyExpandedId === item.history_id" class="cfg3-json-preview">{{ JSON.stringify(item.snapshot_data, null, 2) }}</pre>
                      <div v-if="historyExpandedId === item.history_id" class="cfg3-history-actions">
                        <button
                          class="cfg3-btn ghost cfg3-rollback-btn"
                          :disabled="rollbackLoading"
                          @click.stop="confirmRollback(item)"
                        >
                          <i class="fa-solid fa-rotate-left"></i>
                          {{ rollbackLoading ? '回滚中...' : '回滚至此版本' }}
                        </button>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 规则编辑表单 -->
                <template v-else>
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
                    <p v-if="saveSubscriptionError" class="cfg3-save-error">{{ saveSubscriptionError }}</p>
                  </div>
                  <div class="cfg3-headline-right">
                    <select v-model="subscriptionEditor.enabled" :disabled="toggleLoading" class="cfg3-enable-select" :class="subscriptionEditor.enabled ? 'is-enabled' : 'is-disabled'">
                      <option :value="true">启用</option>
                      <option :value="false">停用</option>
                    </select>
                  </div>
                </div>

                <div class="cfg3-quick-metrics">
                  <div class="cfg3-quick-card">
                    <span>当前步骤</span>
                    <b>{{ subscriptionState.step }} / 4</b>
                  </div>
                  <div class="cfg3-quick-card">
                    <span>已选专题</span>
                    <b>{{ (subscriptionEditor.topics || []).length }}</b>
                  </div>
                  <div class="cfg3-quick-card">
                    <span>预计推送</span>
                    <b>{{ subscriptionSandbox.push }}</b>
                  </div>
                  <div class="cfg3-quick-card is-warn">
                    <span>治理拦截</span>
                    <b>{{ subscriptionSandbox.drop }}</b>
                  </div>
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
                    <button :class="{ active: subscriptionState.ruleMode === 'basic' }" @click="requestRuleModeSwitch('basic')"><i class="fa-solid fa-gem"></i> 业务向导模式</button>
                    <button :class="{ active: subscriptionState.ruleMode === 'ast' }" @click="requestRuleModeSwitch('ast')"><i class="fa-solid fa-code-branch"></i> 专家 AST 模式</button>
                  </div>

                  <template v-if="subscriptionState.ruleMode === 'basic'">
                    <div class="cfg3-section-title"><i class="fa-solid fa-bookmark"></i> 快速订阅情报大盘专题</div>
                    <div class="cfg3-topic-grid">
                      <button
                        v-for="topic in SUBSCRIPTION_TOPICS"
                        :key="topic.id"
                        class="cfg3-topic"
                        :class="{ active: subscriptionEditor.topics.includes(topic.id) }"
                        @click="subscriptionEditor.topics = subscriptionEditor.topics.includes(topic.id) ? subscriptionEditor.topics.filter(t => t !== topic.id) : [...subscriptionEditor.topics, topic.id]">
                        <i class="fa-solid" :class="topic.id === 'TopicDrugs' ? 'fa-capsules' : topic.id === 'TopicSmuggle' ? 'fa-person-walking-luggage' : topic.id === 'TopicTerror' ? 'fa-bomb' : topic.id === 'TopicDataLeak' ? 'fa-database' : topic.id === 'TopicCybercrime' ? 'fa-user-ninja' : 'fa-network-wired'"></i>
                        <span>{{ topic.name }}</span>
                      </button>
                    </div>

                    <div class="cfg3-form-grid">
                      <div class="cfg3-field">
                        <label><i class="fa-solid fa-triangle-exclamation"></i> 最低接收危害等级</label>
                        <select v-model="subscriptionEditor.minSeverity" class="sub-select cfg3-severity-select">
                          <option value="ALL">全部接收</option>
                          <option value="LOW">低危及以上</option>
                          <option value="MEDIUM">中危及以上</option>
                          <option value="HIGH">高危及以上</option>
                          <option value="CRITICAL">致命及以上</option>
                        </select>
                      </div>
                      <div class="cfg3-field">
                        <label><i class="fa-solid fa-chart-line"></i> 风险分数阈值</label>
                        <input v-model.number="subscriptionEditor.riskMin" class="sub-input" type="number" min="0" max="100" placeholder="如: 70">
                      </div>
                    </div>

                    <div class="cfg3-form-grid">
                      <div class="cfg3-field">
                        <label class="cfg3-label-with-action">
                          <span><i class="fa-solid fa-map-pin"></i> 地域关注</span>
                          <button class="cfg3-dict-trigger" @click="openRegionDictModal"><i class="fa-solid fa-list-check"></i> 字典</button>
                        </label>
                        <input v-model="subscriptionEditor.regionFocus" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本">
                      </div>
                      <div class="cfg3-field">
                        <label class="cfg3-label-with-action">
                          <span><i class="fa-solid fa-tags"></i> 业务标签关注 (智能适配专题)</span>
                          <button class="cfg3-dict-trigger" @click="openLabelDictModal"><i class="fa-solid fa-list-check"></i> 字典</button>
                        </label>
                        <input v-model="subscriptionEditor.bizTagFocus" class="sub-input" placeholder="输入回车，或直接粘贴带逗号的整段文本">
                      </div>
                    </div>
                  </template>

                  <template v-else>
                    <div class="cfg3-note-box">专家 AST 模式：使用可视化逻辑树配置规则。支持 AND 且 / OR 或 / NOT 非，支持添加条件与子组，并自动生成表达式用于沙箱模拟。</div>
                    <div class="cfg3-ast-box">
                      <div class="cfg3-ast-helper" style="margin-top: 0; margin-bottom: 12px;">
                        <span class="cfg3-ast-chip">逻辑运算：AND 且 / OR 或 / NOT 非</span>
                        <span class="cfg3-ast-chip">能力：条件、子组、嵌套组合</span>
                        <span class="cfg3-ast-chip">NOT 非组代表“子条件均不满足”</span>
                      </div>

                      <div class="cfg3-ast-tree">
                        <div
                          v-for="row in astGroupRows"
                          :key="row.group.id"
                          class="cfg3-ast-group-row"
                          :style="{ marginLeft: `${row.level * 12}px` }">
                          <div class="cfg3-ast-group-head">
                            <select v-model="row.group.op" class="sub-select cfg3-ast-op-select" :class="{ 'is-not': row.group.op === 'NOT' }">
                              <option value="AND">AND 且</option>
                              <option value="OR">OR 或</option>
                              <option value="NOT">NOT 非</option>
                            </select>
                            <div class="cfg3-ast-group-actions">
                              <button class="cfg3-ast-mini-btn" @click="addAstCondition(row.group.id)"><i class="fa-solid fa-plus"></i> 条件</button>
                              <button class="cfg3-ast-mini-btn" @click="addAstSubgroup(row.group.id)"><i class="fa-solid fa-folder-plus"></i> 子组</button>
                              <button v-if="!row.isRoot" class="cfg3-ast-mini-btn danger" @click="removeAstGroup(row.group.id)"><i class="fa-solid fa-trash-can"></i> 删除组</button>
                            </div>
                          </div>

                          <div class="cfg3-ast-condition-list">
                            <div v-for="cond in row.group.conditions" :key="cond.id" class="cfg3-ast-condition-row">
                              <select v-model="cond.field" class="sub-select cfg3-ast-field-select" @change="syncAstConditionOperator(cond)">
                                <option v-for="field in AST_FIELD_OPTIONS" :key="field.value" :value="field.value">{{ field.label }}</option>
                              </select>
                              <select v-model="cond.operator" class="sub-select cfg3-ast-opr-select">
                                <option v-for="op in getAstOperators(cond.field)" :key="op.value" :value="op.value">{{ op.label }}</option>
                              </select>
                              <input
                                v-if="!isAstUnaryOperator(cond.operator)"
                                v-model="cond.value"
                                class="sub-input cfg3-ast-value-input"
                                :placeholder="getAstValuePlaceholder(cond.field, cond.operator)">
                              <div v-else class="cfg3-ast-unary-tip">无需输入值</div>
                              <button class="cfg3-ast-del" title="删除条件" @click="removeAstCondition(row.group.id, cond.id)"><i class="fa-solid fa-xmark"></i></button>
                            </div>
                          </div>

                          <div v-if="!row.group.conditions.length && !row.group.groups.length" class="cfg3-ast-empty-tip">
                            当前逻辑组为空，请至少添加一个条件或子组。
                          </div>
                        </div>
                      </div>

                      <div class="cfg3-field">
                        <label><i class="fa-solid fa-code"></i> AST 条件表达式（自动生成）</label>
                        <textarea
                          v-model="subscriptionEditor.astExpression"
                          class="sub-textarea cfg3-ast-textarea"
                          readonly
                          placeholder="表达式将基于可视化 AST 条件自动生成"></textarea>
                      </div>
                    </div>
                  </template>
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
              </template>
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
              <div v-if="statsLoading" class="alert-list-loading">
                <div class="loading-spinner"></div>
                <span>加载专题统计...</span>
              </div>
              <div v-else-if="statsError" class="alert-list-error">
                <span>{{ statsError }}</span>
                <button class="retry-btn" @click="fetchRuleNameStats">重试</button>
              </div>
              <div v-else-if="topicList.length === 0" style="padding: 24px; color: var(--text-dim);">暂无专题数据</div>
              <div v-else class="topic-list-grid">
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
                          <div v-if="detailLoading" class="loading-spinner"></div>
                          <template v-else>{{ detailRawContent || state.selectedDetailItem.content }}</template>
                      </div>
                  </div>
              </div>
          </div>
          <div v-else>
            <h2 style="font-size: 18px; margin-bottom: 10px; color: var(--accent-blue);">{{ state.selectedDetailItem.title }}</h2>
            <p style="color: var(--text-dim); margin-bottom: 15px;">发布人: {{ state.selectedDetailItem.author }} | 时间: {{ state.selectedDetailItem.date }}</p>
            <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 6px; border: 1px solid var(--border-color);">
              <div v-if="detailLoading" class="loading-spinner"></div>
              <template v-else>{{ detailRawContent || state.selectedDetailItem.content }}</template>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn btn-tool download-tool" @click="alertMock('开始下载原始取证包...')"><i class="fa-solid fa-file-zipper"></i> 下载原始取证包</button>
          <button class="modal-btn btn-tool graph-tool" @click="alertMock('已打开关系图谱分析系统...')"><i class="fa-solid fa-network-wired"></i> 查看关系图谱</button>
          <button class="modal-btn btn-tool translate-tool" @click="translateItem(state.selectedDetailItem, $event)"><i class="fa-solid fa-language"></i> 全文翻译</button>
          <div style="flex: 1;"></div> 
          <button class="modal-btn btn-warning" @click="alertMock('正在生成情报线索流转单...')"><i class="fa-solid fa-share-from-square"></i> 转线索</button>
          <button class="modal-btn btn-primary" @click="alertMock('正在对接公安立案系统...')"><i class="fa-solid fa-gavel"></i> 一键立案</button>
        </div>
      </div>
    </div>

    <div class="modal-overlay" :class="{ open: subscriptionState.modeModalOpen }" @click.self="closeRuleModeSwitchModal">
      <div class="modal-box cfg3-mode-modal" v-if="subscriptionState.modeModalOpen">
        <div class="modal-header">
          <div class="modal-title"><i class="fa-solid fa-shuffle"></i> 模式迁移预览</div>
          <div class="modal-close" @click="closeRuleModeSwitchModal"><i class="fa-solid fa-xmark"></i></div>
        </div>
        <div class="modal-body cfg3-mode-modal-body">
          <div class="cfg3-mode-tip">将尝试把当前规则迁移为 {{ subscriptionState.pendingRuleMode === 'basic' ? '业务向导模式' : '专家 AST 模式' }}。迁移采用 JSON 请求/响应结构预览，确认后写入当前规则。</div>
          <div class="cfg3-mode-preview-title">迁移预览</div>
          <pre class="cfg3-json-preview cfg3-mode-json">{{ JSON.stringify(subscriptionState.modeSwitchPreview || {}, null, 2) }}</pre>
          <div class="cfg3-mode-desc">当前模式内容会自动保留在规则中，可随时切回。</div>
        </div>
        <div class="modal-footer cfg3-mode-footer">
          <div style="flex: 1;"></div>
          <button class="modal-btn btn-tool" @click="closeRuleModeSwitchModal">取消</button>
          <button class="modal-btn btn-primary" @click="applyRuleModeSwitch">确认切换</button>
        </div>
      </div>
    </div>

    <div class="modal-overlay" :class="{ open: regionDictState.open }" @click.self="closeRegionDictModal">
      <div class="modal-box cfg3-dict-modal" v-if="regionDictState.open">
        <div class="modal-header cfg3-dict-header">
          <div class="modal-title"><i class="fa-solid fa-location-dot"></i> 地理位置字典</div>
          <div class="modal-close" @click="closeRegionDictModal"><i class="fa-solid fa-xmark"></i></div>
        </div>
        <div class="modal-body cfg3-dict-body">
          <aside class="cfg3-dict-side">
            <button
              v-for="cat in regionDictCategories"
              :key="cat.id"
              class="cfg3-dict-cat"
              :class="{ active: regionDictState.category === cat.id }"
              @click="regionDictState.category = cat.id">
              <span>{{ cat.name }}</span>
              <b>{{ cat.count }}</b>
            </button>
          </aside>

          <section class="cfg3-dict-main">
            <input
              v-model="regionDictState.keyword"
              class="cfg3-dict-search"
              placeholder="支持跨分类全局搜索...">

            <div class="cfg3-dict-grid">
              <button
                v-for="item in regionDictVisibleItems"
                :key="item.id"
                class="cfg3-dict-card"
                :class="{ selected: regionDictSelectedSet.has(item.id) }"
                @click="toggleRegionDictItem(item.id)">
                <div class="cfg3-dict-icon"><i class="fa-solid fa-map-location-dot"></i></div>
                <div class="cfg3-dict-meta">
                  <div class="cfg3-dict-name">{{ item.name }}</div>
                  <div class="cfg3-dict-sub">{{ item.province }} · {{ item.categoryName }}</div>
                </div>
                <div class="cfg3-dict-check"><i class="fa-solid" :class="regionDictSelectedSet.has(item.id) ? 'fa-circle-check' : 'fa-circle' "></i></div>
              </button>
            </div>
          </section>
        </div>

        <div class="modal-footer cfg3-dict-footer">
          <span class="cfg3-dict-selected">已选：{{ regionDictState.selectedIds.length }} 项</span>
          <div style="flex: 1;"></div>
          <button class="modal-btn btn-tool" @click="closeRegionDictModal">取消</button>
          <button class="modal-btn btn-primary" @click="applyRegionDictSelection">确认使用</button>
        </div>
      </div>
    </div>

    <div class="modal-overlay" :class="{ open: labelDictState.open }" @click.self="closeLabelDictModal">
      <div class="modal-box cfg3-dict-modal is-label" v-if="labelDictState.open">
        <div class="modal-header cfg3-dict-header">
          <div class="modal-title"><i class="fa-solid fa-tags"></i> 分析标签库 (自动适配当前所选专题)</div>
          <div class="modal-close" @click="closeLabelDictModal"><i class="fa-solid fa-xmark"></i></div>
        </div>
        <div class="modal-body cfg3-dict-body">
          <aside class="cfg3-dict-side">
            <button
              v-for="cat in labelDictCategories"
              :key="cat.id"
              class="cfg3-dict-cat"
              :class="{ active: labelDictState.category === cat.id }"
              @click="labelDictState.category = cat.id">
              <span>{{ cat.name }}</span>
              <b>{{ cat.count }}</b>
            </button>
          </aside>

          <section class="cfg3-dict-main">
            <input
              v-model="labelDictState.keyword"
              class="cfg3-dict-search"
              placeholder="支持跨分类全局搜索...">

            <div class="cfg3-dict-grid">
              <button
                v-for="item in labelDictVisibleItems"
                :key="item.id"
                class="cfg3-dict-card"
                :class="{ selected: labelDictSelectedSet.has(item.id) }"
                @click="toggleLabelDictItem(item.id)">
                <div class="cfg3-dict-icon cfg3-dict-icon-label"><i class="fa-solid fa-tag"></i></div>
                <div class="cfg3-dict-meta">
                  <div class="cfg3-dict-name">{{ item.name }}</div>
                  <div class="cfg3-dict-sub">{{ item.desc }} · {{ item.categoryName }}</div>
                </div>
                <div class="cfg3-dict-check"><i class="fa-solid" :class="labelDictSelectedSet.has(item.id) ? 'fa-circle-check' : 'fa-circle' "></i></div>
              </button>
            </div>
          </section>
        </div>

        <div class="modal-footer cfg3-dict-footer">
          <span class="cfg3-dict-selected">已选：{{ labelDictState.selectedIds.length }} 项</span>
          <div style="flex: 1;"></div>
          <button class="modal-btn btn-tool" @click="closeLabelDictModal">取消</button>
          <button class="modal-btn btn-primary" @click="applyLabelDictSelection">确认使用</button>
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

const followListData = ref([]);
const followLoading = ref(false);
const followError = ref('');

const ruleNameStats = ref([]);
const statsLoading = ref(false);
const statsError = ref('');

const detailLoading = ref(false);
const detailRawContent = ref('');

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
  { id: 'TopicCybercrime', name: '网络黑产' },
  { id: 'TopicAPT', name: 'APT攻击' }
];

const subscriptionRules = ref([
  {
    id: 'sub-1',
    name: '涉毒高危订阅',
    owner: 'SystemAdmin',
    ruleMode: 'basic',
    enabled: true,
    status: 'applied',
    topics: ['TopicDrugs'],
    minSeverity: 'HIGH',
    riskMin: 75,
    sources: ['Telegram', 'Tor'],
    channels: ['Dashboard', 'Telegram'],
    schedule: '每 15 分钟',
    desc: '对涉毒高危线索进行实时订阅并转发值班组。',
    astExpression: '',
    astTree: {
      id: 'group-seed-root',
      op: 'AND',
      conditions: [{ id: 'cond-seed-1', field: 'threat_category', operator: 'in', value: '' }],
      groups: []
    },
    updatedAt: toDateTimeString(new Date())
  }
]);

const subscriptionState = reactive({
  selectedId: 'sub-1',
  search: '',
  step: 1,
  ruleMode: 'basic',
  titleEditing: false,
  titleBackup: '',
  modeModalOpen: false,
  pendingRuleMode: '',
  modeSwitchPreview: null,
  showHistory: false
});

const savingSubscription = ref(false);
const saveSubscriptionError = ref('');
const topicListLoading = ref(false);
const topicListError = ref('');
const alertListLoading = ref(false);
const alertListError = ref('');
const configLoading = ref(false);
const toggleLoading = ref(false);
const supressEnableWatch = ref(false);
const deletingRule = ref(false);
const historyLoading = ref(false);
const historyError = ref('');
const historyList = ref([]);
const historyExpandedId = ref(null);
const rollbackLoading = ref(false);
const DELETED_STORAGE_KEY = 'deleted_subscription_rule_codes';
const loadDeletedCodes = () => {
  try { return new Set(JSON.parse(localStorage.getItem(DELETED_STORAGE_KEY) || '[]')); }
  catch { return new Set(); }
};
const saveDeletedCodes = (codes) => {
  localStorage.setItem(DELETED_STORAGE_KEY, JSON.stringify([...codes]));
};
const deletedRuleCodes = loadDeletedCodes();

const subscriptionEditor = reactive({
  name: '',
  owner: '',
  enabled: true,
  ruleMode: 'basic',
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
  astExpression: '',
  astTree: {
    id: 'group-editor-root',
    op: 'AND',
    conditions: [{ id: 'cond-editor-1', field: 'threat_category', operator: 'in', value: '' }],
    groups: []
  },
  rbacVisibility: '仅自己',
  editorIds: ''
});

let astNodeSeq = 0;
const nextAstNodeId = (prefix = 'ast') => `${prefix}-${Date.now()}-${astNodeSeq++}`;

const AST_FIELD_OPTIONS = [
  { value: 'threat_category', label: '威胁专题', type: 'string' },
  { value: 'severity', label: '危害等级', type: 'string' },
  { value: 'risk_score', label: '风险分', type: 'number' },
  { value: 'source_platform', label: '来源平台', type: 'string' },
  { value: 'source_handle', label: '来源账号/频道', type: 'string' },
  { value: 'entity_type', label: '实体类型', type: 'string' },
  { value: 'entity_value', label: '实体值', type: 'string' },
  { value: 'labels', label: '标签列表', type: 'array' },
  { value: 'ioc_location', label: '地域 IOC', type: 'array' },
  { value: 'raw_content', label: '正文内容', type: 'string' }
];

const AST_OP_MAP = {
  string: [
    { value: 'eq', label: '等于' },
    { value: 'neq', label: '不等于' },
    { value: 'contains', label: '包含' },
    { value: 'in', label: '属于列表' },
    { value: 'regex', label: '正则匹配' },
    { value: 'exists', label: '存在' },
    { value: 'not_exists', label: '不存在' }
  ],
  number: [
    { value: 'eq', label: '等于' },
    { value: 'gte', label: '大于等于' },
    { value: 'lte', label: '小于等于' },
    { value: 'range', label: '区间 Min,Max' },
    { value: 'exists', label: '存在' },
    { value: 'not_exists', label: '不存在' }
  ],
  array: [
    { value: 'contains', label: '包含任一项' },
    { value: 'in', label: '完全命中列表' },
    { value: 'exists', label: '存在' },
    { value: 'not_exists', label: '不存在' }
  ]
};

const AST_FIELD_TYPE = AST_FIELD_OPTIONS.reduce((acc, item) => {
  acc[item.value] = item.type;
  return acc;
}, {});

const createAstCondition = (field = 'threat_category') => {
  const type = AST_FIELD_TYPE[field] || 'string';
  return {
    id: nextAstNodeId('cond'),
    field,
    operator: AST_OP_MAP[type][0].value,
    value: ''
  };
};

const createAstGroup = (op = 'AND') => ({
  id: nextAstNodeId('group'),
  op,
  conditions: [createAstCondition()],
  groups: []
});

const cloneAstTree = (tree) => JSON.parse(JSON.stringify(tree));

const REGION_DICT_LIBRARY = [
  { id: 'gd', name: '广东省', province: '广东', category: 'domestic', categoryName: '国内高发区' },
  { id: 'yn', name: '云南省', province: '云南', category: 'domestic', categoryName: '国内高发区' },
  { id: 'mb', name: '缅北', province: '缅北', category: 'overseas', categoryName: '境外监控区' },
  { id: 'jsj', name: '金三角', province: '金三角', category: 'overseas', categoryName: '境外监控区' }
];

const BIZ_LABEL_DICT_LIBRARY = [
  { id: 'lbl-drug-trade', name: '大宗交易', desc: '大宗交易', category: 'drug', categoryName: '涉毒专属', topics: ['TopicDrugs'] },
  { id: 'lbl-drug-sell', name: '贩毒', desc: '贩毒', category: 'drug', categoryName: '涉毒专属', topics: ['TopicDrugs'] },
  { id: 'lbl-drug-guarantee', name: '暗网担保', desc: '暗网担保', category: 'drug', categoryName: '涉毒专属', topics: ['TopicDrugs'] },
  { id: 'lbl-drug-new', name: '新型毒品', desc: '新型毒品', category: 'drug', categoryName: '涉毒专属', topics: ['TopicDrugs'] },
  { id: 'lbl-smuggle-water', name: '水客带货', desc: '水客带货', category: 'smuggle', categoryName: '走私专属', topics: ['TopicSmuggle'] },
  { id: 'lbl-smuggle-fly', name: '飞缆走私', desc: '飞缆走私', category: 'smuggle', categoryName: '走私专属', topics: ['TopicSmuggle'] },
  { id: 'lbl-common-fraud', name: '诈骗引流', desc: '诈骗引流', category: 'common', categoryName: '通用标签', topics: ['common'] },
  { id: 'lbl-common-split', name: '分销网络', desc: '分销网络', category: 'common', categoryName: '通用标签', topics: ['common'] },
  { id: 'lbl-common-launder', name: '洗钱通道', desc: '洗钱通道', category: 'common', categoryName: '通用标签', topics: ['common'] },
  { id: 'lbl-common-coin', name: '虚假庄传', desc: '虚假庄传', category: 'common', categoryName: '通用标签', topics: ['common'] }
];

const regionDictState = reactive({
  open: false,
  category: 'all',
  keyword: '',
  selectedIds: []
});

const labelDictState = reactive({
  open: false,
  category: 'all',
  keyword: '',
  selectedIds: []
});

const regionDictSelectedSet = computed(() => new Set(regionDictState.selectedIds));
const labelDictSelectedSet = computed(() => new Set(labelDictState.selectedIds));

const adaptedLabelDictItems = computed(() => {
  const selectedTopics = subscriptionEditor.topics || [];
  if (!selectedTopics.length) return BIZ_LABEL_DICT_LIBRARY;
  return BIZ_LABEL_DICT_LIBRARY.filter((item) => item.topics.includes('common') || item.topics.some((topic) => selectedTopics.includes(topic)));
});

const regionDictCategories = computed(() => {
  const domesticCount = REGION_DICT_LIBRARY.filter(item => item.category === 'domestic').length;
  const overseasCount = REGION_DICT_LIBRARY.filter(item => item.category === 'overseas').length;
  return [
    { id: 'all', name: '全部分类', count: REGION_DICT_LIBRARY.length },
    { id: 'domestic', name: '国内高发区', count: domesticCount },
    { id: 'overseas', name: '境外监控区', count: overseasCount }
  ];
});

const regionDictVisibleItems = computed(() => {
  const keyword = (regionDictState.keyword || '').trim().toLowerCase();
  return REGION_DICT_LIBRARY.filter((item) => {
    const hitCategory = regionDictState.category === 'all' || item.category === regionDictState.category;
    if (!hitCategory) return false;
    if (!keyword) return true;
    const text = `${item.name} ${item.province} ${item.categoryName}`.toLowerCase();
    return text.includes(keyword);
  });
});

const labelDictCategories = computed(() => {
  const source = adaptedLabelDictItems.value;
  const drugCount = source.filter(item => item.category === 'drug').length;
  const smuggleCount = source.filter(item => item.category === 'smuggle').length;
  const commonCount = source.filter(item => item.category === 'common').length;
  return [
    { id: 'all', name: '全部分类', count: source.length },
    { id: 'drug', name: '涉毒专属', count: drugCount },
    { id: 'smuggle', name: '走私专属', count: smuggleCount },
    { id: 'common', name: '通用标签', count: commonCount }
  ];
});

const labelDictVisibleItems = computed(() => {
  const keyword = (labelDictState.keyword || '').trim().toLowerCase();
  return adaptedLabelDictItems.value.filter((item) => {
    const hitCategory = labelDictState.category === 'all' || item.category === labelDictState.category;
    if (!hitCategory) return false;
    if (!keyword) return true;
    const text = `${item.name} ${item.desc} ${item.categoryName}`.toLowerCase();
    return text.includes(keyword);
  });
});

const toggleRegionDictItem = (itemId) => {
  if (regionDictSelectedSet.value.has(itemId)) {
    regionDictState.selectedIds = regionDictState.selectedIds.filter(id => id !== itemId);
    return;
  }
  regionDictState.selectedIds = [...regionDictState.selectedIds, itemId];
};

const toggleLabelDictItem = (itemId) => {
  if (labelDictSelectedSet.value.has(itemId)) {
    labelDictState.selectedIds = labelDictState.selectedIds.filter(id => id !== itemId);
    return;
  }
  labelDictState.selectedIds = [...labelDictState.selectedIds, itemId];
};

const openRegionDictModal = () => {
  const tokens = splitValues(subscriptionEditor.regionFocus).map(item => item.toLowerCase());
  regionDictState.selectedIds = REGION_DICT_LIBRARY
    .filter(item => tokens.some(token => token === item.name.toLowerCase() || token === item.province.toLowerCase()))
    .map(item => item.id);
  regionDictState.category = 'all';
  regionDictState.keyword = '';
  regionDictState.open = true;
};

const closeRegionDictModal = () => {
  regionDictState.open = false;
};

const applyRegionDictSelection = () => {
  const names = REGION_DICT_LIBRARY
    .filter(item => regionDictSelectedSet.value.has(item.id))
    .map(item => item.name);
  subscriptionEditor.regionFocus = names.join(',');
  closeRegionDictModal();
};

const openLabelDictModal = () => {
  const tokens = splitValues(subscriptionEditor.bizTagFocus).map(item => item.toLowerCase());
  labelDictState.selectedIds = adaptedLabelDictItems.value
    .filter(item => tokens.some(token => token === item.name.toLowerCase()))
    .map(item => item.id);
  labelDictState.category = 'all';
  labelDictState.keyword = '';
  labelDictState.open = true;
};

const closeLabelDictModal = () => {
  labelDictState.open = false;
};

const applyLabelDictSelection = () => {
  const names = adaptedLabelDictItems.value
    .filter(item => labelDictSelectedSet.value.has(item.id))
    .map(item => item.name);
  subscriptionEditor.bizTagFocus = names.join(',');
  closeLabelDictModal();
};

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

const followedAlerts = computed(() => {
  return followListData.value.filter(item => !item.falsePositive);
});

const followSummary = computed(() => ({
  total: followedAlerts.value.length,
  high: followedAlerts.value.filter(item => item.risk === 'high').length,
  mid: followedAlerts.value.filter(item => item.risk === 'mid').length,
  low: followedAlerts.value.filter(item => item.risk === 'low').length
}));

const topicSummary = computed(() => ({
  total: topicList.value.length,
  running: topicList.value.filter(item => item.status === '运行中').length,
  archived: topicList.value.filter(item => item.status === '归档').length,
  totalHits: topicList.value.reduce((sum, item) => sum + (typeof item.hits === 'number' ? item.hits : 0), 0)
}));

// 关闭弹窗和下拉的全局监听
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.select-box')) state.isSortDropdownOpen = false;
  });
});

// === 3. 基础工具与映射方法 ===
const availableTopics = computed(() => SUBSCRIPTION_TOPICS.map(t => t.id));
const availableRegions = computed(() => [...new Set(listData.value.map(item => getProvince(item.region)))].filter(Boolean));

const getTopicName = (topic) => ({
  'TopicCybercrime': '网络黑产',
  'TopicAPT': 'APT攻击',
  'TopicTaiwan': '网络黑产',
  'TopicRansom': 'APT攻击',
  'TopicDataLeak': '数据泄露',
  'TopicDrugs': '毒品交易',
  'TopicTerror': '恐怖暴力',
  'TopicSmuggle': '非法走私'
}[topic] || topic);
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
  if (name.includes('黑产') || name.includes('台湾')) return 'TopicCybercrime';
  if (name.includes('APT') || name.includes('勒索')) return 'TopicAPT';
  if (name.includes('泄露')) return 'TopicDataLeak';
  if (name.includes('暴恐') || name.includes('恐怖')) return 'TopicTerror';
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
    fetchTopicList();
  }
  if (module === 'alerts') {
    fetchAlertList();
  }
  if (module === 'follow') {
    fetchFollowList();
  }
  if (module === 'topicList') {
    fetchRuleNameStats();
  }
  if (module !== 'alerts') {
    state.isImmersive = false;
    state.leftCollapsed = false;
    state.rightCollapsed = false;
    state.isFilterCollapsed = false;
  }
};

const SEVERITY_MAP = { 'CRITICAL': 'high', 'HIGH': 'high', 'MEDIUM': 'mid', 'LOW': 'low' };

const mapAlertFields = (alert, index) => ({
  id: alert.event_id || `alert-${index}`,
  title: alert.title || '',
  content: alert.text_preview || '',
  risk: SEVERITY_MAP[alert.severity] || 'low',
  source: alert.platform || '',
  sourceType: alert.source_type || '',
  siteName: alert.site_name || '',
  author: alert.author_name || '',
  hitRule: alert.rule_code || '',
  hitRules: alert.rule_code ? [alert.rule_code] : [],
  date: alert.report_time || '',
  region: alert.region || '',
  topic: alert.topic || '',
  industry: alert.industry || '',
  read: alert.read_status === 1,
  followed: alert.is_monitor_target === 1,
  falsePositive: alert.false_positive === 1,
  entities: (alert.entity_tags || []).map(tag => ({ type: 'tag', value: tag })),
  selected: false,
  isExpanded: false,
  children: [],
  stats: { fwd: 0, cmt: 0, sim: 0 },
  chatMeta: null,
  contentId: alert.content_id || '',
  exportStatus: alert.export_status || 0,
  sourceHandle: alert.source_handle || '',
  authorFollowed: false,
  authorTargetId: '',
  translatedContent: ''
});

const mapAlertToItem = (alert, index) => mapAlertFields(alert, index);
const mapFollowItem = (alert, index) => mapAlertFields(alert, index);

const fetchAlertList = async () => {
  alertListLoading.value = true;
  alertListError.value = '';
  try {
    const res = await fetch('/api/topics/alert/list_all');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '获取告警列表失败');
    listData.value = (json.data || []).map(mapAlertToItem);
  } catch (e) {
    alertListError.value = e.message || '请求失败';
  } finally {
    alertListLoading.value = false;
  }
  fetchAuthorFollowStatus(listData.value);
};

const fetchFollowList = async () => {
  followLoading.value = true;
  followError.value = '';
  try {
    const res = await fetch('/api/monitor/event');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '获取关注列表失败');
    followListData.value = (json.data || []).map(mapFollowItem);
    // 合并本地已关注但后端尚未返回的条目（处理异步延迟）
    const localFollowed = listData.value.filter(item => item.followed && !item.falsePositive);
    for (const item of localFollowed) {
      if (!followListData.value.find(f => f.id === item.id)) {
        followListData.value.unshift(item);
      }
    }
  } catch (e) {
    followError.value = e.message || '请求失败';
  } finally {
    followLoading.value = false;
  }
  fetchAuthorFollowStatus(followListData.value);
};

const fetchAlertsByTopic = async (threatCategory) => {
  alertListLoading.value = true;
  alertListError.value = '';
  try {
    const url = `/api/topics/alert/list?threat_category=${encodeURIComponent(threatCategory)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '获取专题告警列表失败');
    listData.value = (json.data || []).map(mapAlertToItem);
  } catch (e) {
    alertListError.value = e.message || '请求失败';
  } finally {
    alertListLoading.value = false;
  }
  fetchAuthorFollowStatus(listData.value);
};

const fetchAlertsByTopicName = async (topicName) => {
  alertListLoading.value = true;
  alertListError.value = '';
  try {
    const url = `/api/topics/alert/list_by_topic_name?name=${encodeURIComponent(topicName)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '获取专题告警列表失败');
    listData.value = (json.data || []).map(mapAlertToItem);
  } catch (e) {
    alertListError.value = e.message || '请求失败';
  } finally {
    alertListLoading.value = false;
  }
  fetchAuthorFollowStatus(listData.value);
};

const fetchRuleNameStats = async () => {
  statsLoading.value = true;
  statsError.value = '';
  try {
    const res = await fetch('/api/topics/alert/rule_name_stats');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '获取专题统计失败');
    ruleNameStats.value = (json.data || []).map((item, index) => ({
      id: index + 1,
      name: item.rule_name,
      hits: item.count,
      owner: '-',
      keywordCount: '-',
      sourceCount: '-',
      status: '运行中',
      lastRun: '-',
      desc: ''
    }));
    topicList.value = ruleNameStats.value;
  } catch (e) {
    statsError.value = e.message || '请求失败';
  } finally {
    statsLoading.value = false;
  }
};

const fetchAuthorFollowStatus = async (items) => {
  const authors = items
    .filter(item => item.author && item.source)
    .map(item => ({
      profile_id: item.authorTargetId || '',
      platform: item.source,
      source_handle_norm: item.sourceHandle || item.author || ''
    }));
  if (!authors.length) return;
  try {
    const res = await fetch('/api/monitor/authors/follow-status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ authors })
    });
    if (!res.ok) return;
    const json = await res.json();
    if (json.code === 200 && json.data) {
      for (const item of items) {
        const targetId = item.authorTargetId || `${item.source}:${item.sourceHandle || item.author}`;
        if (json.data[targetId] !== undefined) {
          item.authorFollowed = json.data[targetId];
          if (json.data[targetId]) item.authorTargetId = targetId;
        }
      }
    }
  } catch { /* 静默失败 */ }
};

const fetchAlertDetail = async (eventId, contentId) => {
  detailLoading.value = true;
  detailRawContent.value = '';
  try {
    const url = `/api/topics/alert/${encodeURIComponent(eventId)}/detail?content_id=${encodeURIComponent(contentId)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code === 200 && json.data) {
      detailRawContent.value = json.data.raw_content || '';
    }
  } catch {
    detailRawContent.value = '';
  } finally {
    detailLoading.value = false;
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

const openFollowedAlertInAlerts = (item) => {
  resetAlertFiltersByPreset();
  state.activeModule = 'alerts';
  state.searchQuery = item.title || item.author || '';
  filters.risk = item.risk;
  filters.media = item.source || 'all';
  filters.topic = item.topic || 'all';
};

const openTopicInAlerts = (topic) => {
  resetAlertFiltersByPreset();
  state.activeModule = 'alerts';
  filters.topic = getTopicCodeByName(topic.name);
  fetchAlertsByTopicName(topic.name);
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
  draft: subscriptionRules.value.filter((rule) => rule.status !== 'applied').length
}));

const subscriptionSandboxStats = reactive({ hit: 0, push: 0, digest: 0, drop: 0 });
const subscriptionSandbox = computed(() => ({ ...subscriptionSandboxStats }));

const sandboxInputText = ref('');
const sandboxEvents = ref([]);

const severityWeight = { ALL: 0, LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 };
const splitValues = (text = '') => String(text || '').split(/[，,|/\n]/).map(v => v.trim()).filter(Boolean);

const normalizeAstTree = (input) => {
  const walk = (node) => {
    const raw = node && typeof node === 'object' ? node : {};
    const op = ['AND', 'OR', 'NOT'].includes(raw.op) ? raw.op : 'AND';
    const conditions = Array.isArray(raw.conditions) ? raw.conditions.map((item) => {
      const field = AST_FIELD_TYPE[item?.field] ? item.field : 'threat_category';
      const type = AST_FIELD_TYPE[field] || 'string';
      const validOps = AST_OP_MAP[type].map(opItem => opItem.value);
      return {
        id: item?.id || nextAstNodeId('cond'),
        field,
        operator: validOps.includes(item?.operator) ? item.operator : AST_OP_MAP[type][0].value,
        value: String(item?.value || '')
      };
    }) : [];
    const groups = Array.isArray(raw.groups) ? raw.groups.map(walk) : [];
    return {
      id: raw.id || nextAstNodeId('group'),
      op,
      conditions,
      groups
    };
  };

  const root = walk(input);
  if (!root.conditions.length && !root.groups.length) {
    root.conditions.push(createAstCondition());
  }
  return root;
};

const flattenAstGroups = (group, level = 0, acc = []) => {
  if (!group) return acc;
  acc.push({ group, level, isRoot: level === 0 });
  (group.groups || []).forEach((child) => flattenAstGroups(child, level + 1, acc));
  return acc;
};

const astGroupRows = computed(() => flattenAstGroups(subscriptionEditor.astTree));

const findAstGroupById = (root, groupId) => {
  if (!root) return null;
  if (root.id === groupId) return root;
  for (const child of root.groups || []) {
    const found = findAstGroupById(child, groupId);
    if (found) return found;
  }
  return null;
};

const removeAstGroupById = (root, groupId) => {
  if (!root?.groups?.length) return false;
  const idx = root.groups.findIndex(item => item.id === groupId);
  if (idx >= 0) {
    root.groups.splice(idx, 1);
    return true;
  }
  return root.groups.some(item => removeAstGroupById(item, groupId));
};

const getAstOperators = (field) => {
  const type = AST_FIELD_TYPE[field] || 'string';
  return AST_OP_MAP[type] || AST_OP_MAP.string;
};

const syncAstConditionOperator = (cond) => {
  const validOps = getAstOperators(cond.field).map(item => item.value);
  if (!validOps.includes(cond.operator)) {
    cond.operator = validOps[0];
  }
};

const isAstUnaryOperator = (operator) => operator === 'exists' || operator === 'not_exists';

const getAstValuePlaceholder = (field, operator) => {
  if (operator === 'range') return '例如：70,100';
  if (operator === 'in') return AST_FIELD_TYPE[field] === 'array' ? '例如：贩毒,暗网担保' : '例如：TopicDrugs,TopicSmuggle';
  if (operator === 'regex') return '例如：(?i)担保|跑分';
  return '输入比较值';
};

const addAstCondition = (groupId) => {
  const root = normalizeAstTree(subscriptionEditor.astTree);
  const group = findAstGroupById(root, groupId);
  if (!group) return;
  group.conditions.push(createAstCondition());
  subscriptionEditor.astTree = root;
};

const removeAstCondition = (groupId, condId) => {
  const root = normalizeAstTree(subscriptionEditor.astTree);
  const group = findAstGroupById(root, groupId);
  if (!group) return;
  group.conditions = (group.conditions || []).filter(item => item.id !== condId);
  if (!group.conditions.length && !group.groups.length) {
    group.conditions.push(createAstCondition());
  }
  subscriptionEditor.astTree = root;
};

const addAstSubgroup = (groupId) => {
  const root = normalizeAstTree(subscriptionEditor.astTree);
  const group = findAstGroupById(root, groupId);
  if (!group) return;
  group.groups.push(createAstGroup('AND'));
  subscriptionEditor.astTree = root;
};

const removeAstGroup = (groupId) => {
  const root = normalizeAstTree(subscriptionEditor.astTree);
  if (root.id === groupId) return;
  removeAstGroupById(root, groupId);
  subscriptionEditor.astTree = root;
};

const formatAstValue = (cond) => {
  if (isAstUnaryOperator(cond.operator)) return '';
  if (cond.operator === 'in' || cond.operator === 'range') {
    return `[${splitValues(cond.value).join(',')}]`;
  }
  if (AST_FIELD_TYPE[cond.field] === 'number') return cond.value;
  return `'${String(cond.value || '').replace(/'/g, "\\'")}'`;
};

const stringifyAstCondition = (cond) => {
  const field = cond.field || 'threat_category';
  const opMap = {
    eq: '==',
    neq: '!=',
    contains: 'contains',
    in: 'in',
    regex: 'regex',
    gte: '>=',
    lte: '<=',
    range: 'range',
    exists: 'exists',
    not_exists: 'not_exists'
  };

  if (cond.operator === 'exists' || cond.operator === 'not_exists') {
    return `${field} ${opMap[cond.operator]}`;
  }
  return `${field} ${opMap[cond.operator] || '=='} ${formatAstValue(cond)}`;
};

const buildAstExpression = (group) => {
  if (!group) return '';
  const entries = [
    ...(group.conditions || []).map(stringifyAstCondition),
    ...(group.groups || []).map(child => buildAstExpression(child)).filter(Boolean)
  ].filter(Boolean);
  if (!entries.length) return '';
  if (group.op === 'NOT') return `NOT (${entries.join(' OR ')})`;
  const sep = ` ${group.op} `;
  return entries.length > 1 ? `(${entries.join(sep)})` : entries[0];
};

const hasEffectiveAstCondition = (group) => {
  if (!group) return false;
  const selfValid = (group.conditions || []).some((cond) => {
    if (isAstUnaryOperator(cond.operator)) return true;
    if (cond.operator === 'in' || cond.operator === 'range') return splitValues(cond.value).length > 0;
    return String(cond.value || '').trim().length > 0;
  });
  if (selfValid) return true;
  return (group.groups || []).some(child => hasEffectiveAstCondition(child));
};

const refreshAstExpression = () => {
  const root = subscriptionEditor.astTree || createAstGroup('AND');
  subscriptionEditor.astExpression = buildAstExpression(root);
};

const buildRuleModePreview = (targetMode) => {
  const now = toDateTimeString(new Date());
  const request = {
    action: 'switch_rule_mode',
    from_mode: subscriptionState.ruleMode,
    to_mode: targetMode,
    rule_id: subscriptionState.selectedId,
    request_time: now
  };

  if (targetMode === 'basic') {
    return {
      request,
      response: {
        mode: 'basic',
        basic: {
          topics: subscriptionEditor.topics,
          severity: subscriptionEditor.minSeverity,
          risk_min: Number(subscriptionEditor.riskMin || 0),
          locations: splitValues(subscriptionEditor.regionFocus),
          labels: splitValues(subscriptionEditor.bizTagFocus)
        }
      }
    };
  }

  return {
    request,
    response: {
      mode: 'ast',
      ast: {
        expression: buildAstExpression(normalizeAstTree(subscriptionEditor.astTree)),
        logic_tree: normalizeAstTree(subscriptionEditor.astTree)
      }
    }
  };
};

const requestRuleModeSwitch = (targetMode) => {
  if (targetMode === subscriptionState.ruleMode) return;
  subscriptionState.pendingRuleMode = targetMode;
  subscriptionState.modeSwitchPreview = buildRuleModePreview(targetMode);
  subscriptionState.modeModalOpen = true;
};

const closeRuleModeSwitchModal = () => {
  subscriptionState.modeModalOpen = false;
  subscriptionState.pendingRuleMode = '';
  subscriptionState.modeSwitchPreview = null;
};

const applyRuleModeSwitch = () => {
  if (!subscriptionState.pendingRuleMode) {
    closeRuleModeSwitchModal();
    return;
  }
  subscriptionState.ruleMode = subscriptionState.pendingRuleMode;
  if (subscriptionState.ruleMode === 'ast') {
    refreshAstExpression();
  }
  if (sandboxInputText.value) runSandboxFromInput();
  closeRuleModeSwitchModal();
};

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

const getAstEventFieldValue = (ev, field) => {
  if (field === 'labels') return Array.isArray(ev.labels) ? ev.labels : [];
  if (field === 'ioc_location') return Array.isArray(ev.ioc_location) ? ev.ioc_location : [];
  return ev[field];
};

const evalAstCondition = (cond, ev) => {
  const fieldType = AST_FIELD_TYPE[cond.field] || 'string';
  const leftRaw = getAstEventFieldValue(ev, cond.field);

  if (cond.operator === 'exists') {
    if (Array.isArray(leftRaw)) return leftRaw.length > 0;
    return !(leftRaw === undefined || leftRaw === null || String(leftRaw).trim() === '');
  }
  if (cond.operator === 'not_exists') {
    if (Array.isArray(leftRaw)) return leftRaw.length === 0;
    return leftRaw === undefined || leftRaw === null || String(leftRaw).trim() === '';
  }

  if (fieldType === 'number') {
    const left = Number(leftRaw);
    if (!Number.isFinite(left)) return false;
    if (cond.operator === 'range') {
      const values = splitValues(cond.value).map(Number).filter(Number.isFinite);
      if (values.length < 2) return false;
      const [min, max] = values;
      return left >= min && left <= max;
    }
    const right = Number(String(cond.value || '').trim());
    if (!Number.isFinite(right)) return false;
    if (cond.operator === 'eq') return left === right;
    if (cond.operator === 'gte') return left >= right;
    if (cond.operator === 'lte') return left <= right;
    return false;
  }

  if (fieldType === 'array') {
    const left = (Array.isArray(leftRaw) ? leftRaw : []).map(v => String(v).toLowerCase());
    const right = splitValues(cond.value).map(v => v.toLowerCase());
    if (!right.length) return false;
    if (cond.operator === 'contains') return right.some(v => left.includes(v));
    if (cond.operator === 'in') return right.every(v => left.includes(v));
    return false;
  }

  const left = String(leftRaw || '').toLowerCase();
  const right = String(cond.value || '').trim().toLowerCase();
  if (cond.operator === 'eq') return left === right;
  if (cond.operator === 'neq') return left !== right;
  if (cond.operator === 'contains') return right ? left.includes(right) : false;
  if (cond.operator === 'in') {
    const values = splitValues(cond.value).map(v => v.toLowerCase());
    return values.includes(left);
  }
  if (cond.operator === 'regex') {
    try {
      return new RegExp(cond.value || '', 'i').test(String(leftRaw || ''));
    } catch {
      return false;
    }
  }
  return false;
};

const evalAstGroup = (group, ev) => {
  const condResults = (group.conditions || []).map(cond => evalAstCondition(cond, ev));
  const childResults = (group.groups || []).map(child => evalAstGroup(child, ev));
  const allResults = [...condResults, ...childResults];
  if (!allResults.length) return false;
  if (group.op === 'OR') return allResults.some(Boolean);
  if (group.op === 'NOT') return !allResults.some(Boolean);
  return allResults.every(Boolean);
};

const evaluateSandboxEvent = (ev) => {
  if (subscriptionState.ruleMode === 'ast') {
    const tree = normalizeAstTree(subscriptionEditor.astTree);
    const pass = evalAstGroup(tree, ev);
    return {
      pass,
      missReason: pass ? '' : 'AST 条件树未命中',
      trace: {
        mode: 'ast',
        expression: buildAstExpression(tree),
        astTree: tree
      }
    };
  }

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
      mode: 'basic',
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
    subscriptionEditor.enabled,
    subscriptionState.ruleMode
  ],
  () => {
    if (subscriptionState.ruleMode === 'ast') refreshAstExpression();
    if (!sandboxInputText.value) return;
    runSandboxFromInput();
  }
);

watch(
  () => subscriptionEditor.astTree,
  () => {
    if (subscriptionState.ruleMode !== 'ast') return;
    refreshAstExpression();
    if (!sandboxInputText.value) return;
    runSandboxFromInput();
  },
  { deep: true }
);

watch(saveSubscriptionError, (val) => {
  if (val) setTimeout(() => { saveSubscriptionError.value = ''; }, 5000);
});

watch(() => subscriptionEditor.enabled, async (newVal, oldVal) => {
  if (supressEnableWatch.value) return;
  if (newVal === oldVal) return;
  const rule = selectedSubscriptionRule.value;
  if (!rule?.rule_code) return;
  const result = await toggleTopicEnabled(rule.rule_code, newVal);
  if (!result.success) {
    subscriptionEditor.enabled = oldVal;
    alertMock('切换失败：' + result.error);
  }
});

const openHistory = async () => {
  const rule = selectedSubscriptionRule.value;
  if (!rule?.rule_code) {
    alertMock('请先选择一个已创建的专题');
    return;
  }
  subscriptionState.showHistory = true;
  await fetchTopicHistory(rule.rule_code);
};

const closeHistory = () => {
  subscriptionState.showHistory = false;
  historyList.value = [];
  historyError.value = '';
  historyExpandedId.value = null;
};

const confirmRollback = async (historyItem) => {
  const rule = selectedSubscriptionRule.value;
  if (!rule?.rule_code) return;
  if (!confirm(`确认回滚到该版本吗？\n\n操作：${historyItem.action}\n时间：${historyItem.created_at}\n\n当前未保存的编辑内容将丢失。`)) return;

  const result = await rollbackToHistory(rule.rule_code, historyItem.history_id);
  if (result.success && result.data) {
    applyConfigToRule(result.data);
    syncSubscriptionEditor();
    closeHistory();
    alertMock('已回滚至指定版本');
  }
};

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
  supressEnableWatch.value = true;
  const rule = selectedSubscriptionRule.value;
  if (!rule) { supressEnableWatch.value = false; return; }
  subscriptionEditor.name = rule.name || '';
  subscriptionEditor.owner = rule.owner || '';
  subscriptionEditor.ruleMode = rule.ruleMode || 'basic';
  subscriptionState.ruleMode = subscriptionEditor.ruleMode;
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
  subscriptionEditor.internalGroupIds = rule.internalGroupIds || '';
  subscriptionEditor.externalDashboard = rule.externalDashboard !== false;
  subscriptionEditor.webhookUrls = rule.webhookUrls || '';
  subscriptionEditor.telegramIds = rule.telegramIds || '';
  subscriptionEditor.priority = Number(rule.priority ?? 50);
  subscriptionEditor.note = rule.note || '';
  subscriptionEditor.astTree = normalizeAstTree(rule.astTree);
  subscriptionEditor.astExpression = rule.astExpression || buildAstExpression(subscriptionEditor.astTree);
  subscriptionEditor.rbacVisibility = rule.rbacVisibility || '仅自己';
  subscriptionEditor.editorIds = rule.editorIds || '';
  supressEnableWatch.value = false;
};

const persistSubscriptionEditor = () => {
  const rule = selectedSubscriptionRule.value;
  if (!rule) return null;
  rule.name = (subscriptionEditor.name || '').trim();
  rule.owner = (subscriptionEditor.owner || '').trim();
  rule.ruleMode = subscriptionState.ruleMode || 'basic';
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
  rule.astTree = cloneAstTree(normalizeAstTree(subscriptionEditor.astTree));
  rule.astExpression = (subscriptionState.ruleMode === 'ast'
    ? buildAstExpression(rule.astTree)
    : (subscriptionEditor.astExpression || '')).trim();
  rule.rbacVisibility = subscriptionEditor.rbacVisibility || '仅自己';
  rule.editorIds = (subscriptionEditor.editorIds || '').trim();
  rule.updatedAt = toDateTimeString(new Date());
  return rule;
};

const validateSubscriptionEditor = () => {
  if (!(subscriptionEditor.name || '').trim()) return '规则名称不能为空';
  if (!(subscriptionEditor.owner || '').trim()) return '责任人不能为空';
  if (subscriptionState.ruleMode === 'basic' && !(subscriptionEditor.topics || []).length) return '至少选择一个监测专题';
  if (subscriptionState.ruleMode === 'ast') {
    const tree = normalizeAstTree(subscriptionEditor.astTree);
    const expression = buildAstExpression(tree);
    if (!expression.trim() || !hasEffectiveAstCondition(tree)) return 'AST 模式下请至少配置一个有效条件';
  }
  if (!(subscriptionEditor.sources || []).length) return '至少选择一个监测来源';
  if (!(subscriptionEditor.channels || []).length) return '至少选择一个分发通道';
  return '';
};

const selectSubscriptionRule = async (ruleId) => {
  subscriptionState.selectedId = ruleId;
  subscriptionState.titleEditing = false;

  const rule = subscriptionRules.value.find(r => r.id === ruleId);
  if (rule?.rule_code) {
    const config = await fetchTopicConfig(rule.rule_code);
    if (config) applyConfigToRule(config);
  }

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

const parseCsv = (str) => (str || '').split(',').map(s => s.trim()).filter(Boolean);

const DEDUP_KEY_MAP = {
  '不过滤 (每条独立推送)': 'none',
  '作者+主题': 'author_topic',
  '正文哈希': 'content_hash',
  '内容哈希': 'content_hash',
  '实体聚合': 'entity',
  '来源账号': 'source_handle'
};
const OVERFLOW_ACTION_MAP = {
  '静默丢弃': 'drop',
  '摘要合并': 'digest',
  '降级推送': 'degrade'
};
const VISIBILITY_MAP = {
  '仅自己': 'private',
  '本组': 'team',
  '全局': 'global'
};
const DEDUP_KEY_REVERSE = { 'none': '不过滤 (每条独立推送)', 'content_hash': '正文哈希', 'author_topic': '作者+主题', 'entity': '实体聚合', 'source_handle': '来源账号' };
const OVERFLOW_REVERSE = { 'drop': '静默丢弃', 'digest': '摘要合并', 'degrade': '降级推送' };
const VISIBILITY_REVERSE = { 'private': '仅自己', 'team': '本组', 'global': '全局' };

const buildCreateTopicBody = () => {
  const ed = subscriptionEditor;
  const rule = selectedSubscriptionRule.value;
  const body = {
    rule_id: rule?.rule_code || '',
    rule_name: (ed.name || '').trim(),
    enabled: ed.enabled ? 1 : 0,
    status: ed.status || 'draft',
    mode: ed.ruleMode || 'basic',
    basic_config: {
      threat_category: ed.topics || [],
      risk_level: ed.minSeverity || 'HIGH',
      risk_score: Number(ed.riskMin || 70),
      region: parseCsv(ed.regionFocus),
      entity_tags: parseCsv(ed.bizTagFocus)
    },
    governance: {
      dedupe_key: DEDUP_KEY_MAP[ed.dedupKey] || 'none',
      dedupe_window: Number(ed.dedupWindow || 30),
      frequency_hour: Number(ed.rateLimit || 50),
      excess: OVERFLOW_ACTION_MAP[ed.overflowAction] || 'drop'
    },
    delivery: {
      user_ids: parseCsv(ed.internalUserIds),
      group_ids: parseCsv(ed.internalGroupIds),
      dashboard_enabled: ed.externalDashboard ? 1 : 0,
      webhook_urls: parseCsv(ed.webhookUrls),
      telegram_ids: parseCsv(ed.telegramIds)
    },
    meta: {
      charge_person: (ed.owner || '').trim(),
      priority: Number(ed.priority || 50),
      summary: (ed.note || '').trim(),
      visible_scope: VISIBILITY_MAP[ed.rbacVisibility] || 'private',
      editor_ids: parseCsv(ed.editorIds)
    }
  };
  if (ed.ruleMode === 'ast') {
    body.ast_config = normalizeAstTree(ed.astTree);
  }
  return body;
};

const createTopicOnServer = async (action) => {
  savingSubscription.value = true;
  saveSubscriptionError.value = '';
  try {
    const body = buildCreateTopicBody();
    const res = await fetch(`/api/topics/?action=${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '创建失败');
    const rule = selectedSubscriptionRule.value;
    if (rule) {
      rule.rule_code = json.data?.rule_code || '';
      rule.created_at = json.data?.created_at || '';
      rule.updatedAt = json.data?.updated_at || toDateTimeString(new Date());
    }
    fetchTopicList();
    return { success: true, data: json.data };
  } catch (e) {
    saveSubscriptionError.value = e.message || '请求失败，请检查网络后重试';
    return { success: false, error: e.message };
  } finally {
    savingSubscription.value = false;
  }
};

const applyConfigToRule = (config) => {
  if (!config) return;
  const rule = subscriptionRules.value.find(r => r.rule_code === config.rule_code);
  if (!rule) return;

  rule.name = config.rule_name || rule.name;
  rule.ruleMode = config.mode || rule.ruleMode;
  rule.enabled = config.enabled === 1;
  rule.status = config.status || rule.status;
  rule.owner = config.meta?.charge_person || rule.owner;

  if (config.basic_config) {
    rule.topics = config.basic_config.threat_category || [];
    rule.minSeverity = config.basic_config.risk_level || 'HIGH';
    rule.riskMin = config.basic_config.risk_score ?? 70;
    rule.regionFocus = (config.basic_config.region || []).join(',');
    rule.bizTagFocus = (config.basic_config.entity_tags || []).join(',');
  }

  if (config.ast_config) {
    rule.astTree = config.ast_config;
  }

  if (config.governance) {
    const rawDedup = config.governance.dedupe_key || '';
    rule.dedupKey = DEDUP_KEY_REVERSE[rawDedup] || rawDedup || rule.dedupKey;
    rule.dedupWindow = config.governance.dedupe_window ?? rule.dedupWindow;
    rule.rateLimit = config.governance.frequency_hour ?? rule.rateLimit;
    const rawOverflow = config.governance.excess || '';
    rule.overflowAction = OVERFLOW_REVERSE[rawOverflow] || rawOverflow || rule.overflowAction;
  }

  if (config.delivery) {
    rule.internalUserIds = (config.delivery.user_ids || []).join(',');
    rule.internalGroupIds = (config.delivery.group_ids || []).join(',');
    rule.externalDashboard = config.delivery.dashboard_enabled === 1;
    rule.webhookUrls = (config.delivery.webhook_urls || []).join(',');
    rule.telegramIds = (config.delivery.telegram_ids || []).join(',');
    const ch = [];
    if (config.delivery.dashboard_enabled === 1) ch.push('Dashboard');
    if ((config.delivery.webhook_urls || []).length) ch.push('Webhook');
    if ((config.delivery.telegram_ids || []).length) ch.push('Telegram');
    if (ch.length) rule.channels = ch;
  }

  if (config.meta) {
    rule.priority = config.meta.priority ?? rule.priority;
    rule.note = config.meta.summary || rule.note;
    const rawVis = config.meta.visible_scope || '';
    rule.rbacVisibility = VISIBILITY_REVERSE[rawVis] || rawVis || rule.rbacVisibility;
    rule.editorIds = (config.meta.editor_ids || []).join(',');
  }

  rule.created_at = config.created_at || '';
  rule.updatedAt = config.updated_at || config.final_syn_time || rule.updatedAt;
};

const fetchTopicConfig = async (ruleCode) => {
  if (!ruleCode) return null;
  configLoading.value = true;
  try {
    const res = await fetch(`/api/topics/${ruleCode}/config`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '获取配置失败');
    return json.data?.config || null;
  } catch (e) {
    console.error('获取专题配置失败:', e);
    return null;
  } finally {
    configLoading.value = false;
  }
};

const fetchTopicHistory = async (ruleCode) => {
  if (!ruleCode) return;
  historyLoading.value = true;
  historyError.value = '';
  historyList.value = [];
  try {
    const res = await fetch(`/api/topics/${ruleCode}/history`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '获取历史失败');
    historyList.value = json.data || [];
  } catch (e) {
    historyError.value = e.message || '请求失败';
  } finally {
    historyLoading.value = false;
  }
};

const rollbackToHistory = async (ruleCode, historyId) => {
  rollbackLoading.value = true;
  try {
    const res = await fetch(`/api/topics/${ruleCode}/rollback/${historyId}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '回滚失败');
    return { success: true, data: json.data };
  } catch (e) {
    alertMock('回滚失败：' + e.message);
    return { success: false, error: e.message };
  } finally {
    rollbackLoading.value = false;
  }
};

const toggleTopicEnabled = async (ruleCode, enabled) => {
  toggleLoading.value = true;
  try {
    const res = await fetch(`/api/topics/${ruleCode}/toggle`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: enabled ? 1 : 0 })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '切换失败');

    const rule = subscriptionRules.value.find(r => r.rule_code === ruleCode);
    if (rule) rule.enabled = enabled;

    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  } finally {
    toggleLoading.value = false;
  }
};

const mapTopicToRule = (item) => ({
  id: item.rule_code || '',
  rule_code: item.rule_code || '',
  name: item.rule_name || '未命名规则',
  owner: item.charge_person || '',
  ruleMode: 'basic',
  enabled: item.enabled === 1,
  status: item.status || 'draft',
  topics: [],
  minSeverity: 'HIGH',
  riskMin: 70,
  sources: ['Telegram'],
  channels: ['Dashboard'],
  schedule: '每 15 分钟',
  desc: item.summary || '',
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
  astExpression: '',
  astTree: createAstGroup('AND'),
  rbacVisibility: '仅自己',
  editorIds: '',
  updatedAt: item.final_syn_time || toDateTimeString(new Date())
});

const fetchTopicList = async () => {
  topicListLoading.value = true;
  topicListError.value = '';
  try {
    const res = await fetch('/api/topics/list');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg || '获取专题列表失败');
    const items = json.data || [];
    if (items.length) {
      subscriptionRules.value = items
        .filter(item => !deletedRuleCodes.has(item.rule_code))
        .map(mapTopicToRule);
      subscriptionState.selectedId = subscriptionRules.value[0].id;
    }
  } catch (e) {
    topicListError.value = e.message || '请求失败';
  } finally {
    topicListLoading.value = false;
  }
  ensureSubscriptionSelection();
};


const createSubscriptionRule = () => {
  const id = `sub-${Date.now()}`;
  const rule = {
    id,
    name: '新建订阅规则',
    owner: '',
    ruleMode: 'basic',
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
    astExpression: '',
    astTree: createAstGroup('AND'),
    rbacVisibility: '仅自己',
    editorIds: '',
    updatedAt: toDateTimeString(new Date())
  };
  subscriptionRules.value.unshift(rule);
  subscriptionState.selectedId = id;
  syncSubscriptionEditor();
};

const saveSubscriptionDraft = async () => {
  const err = validateSubscriptionEditor();
  if (err) {
    alertMock(err);
    return;
  }
  const rule = persistSubscriptionEditor();
  if (!rule) return;
  rule.status = 'draft';
  saveSubscriptionError.value = '';
  const result = await createTopicOnServer('save_draft');
  if (result.success) {
    generateSmartSandboxSample();
    alertMock('订阅规则草稿已保存，专题已创建');
  }
};

const publishSubscriptionRule = async () => {
  const err = validateSubscriptionEditor();
  if (err) {
    alertMock(err);
    return;
  }
  const rule = persistSubscriptionEditor();
  if (!rule) return;
  rule.status = 'applied';
  saveSubscriptionError.value = '';
  const result = await createTopicOnServer('apply');
  if (result.success) {
    alertMock(`订阅规则已发布：将对 ${rule.topics.map(getTopicName).join(' / ')} 执行监测`);
  }
};

const deleteSubscriptionRule = async () => {
  const rule = selectedSubscriptionRule.value;
  if (!rule) return;
  if (!confirm('确定删除当前订阅规则吗？')) return;

  const ruleCode = rule.rule_code;
  if (ruleCode) {
    deletingRule.value = true;
    try {
      const res = await fetch(`/api/topics/${ruleCode}`, { method: 'DELETE' });
      if (res.status !== 404 && !res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      if (res.status !== 404) {
        const json = await res.json();
        if (json.code !== 200) throw new Error(json.msg || '删除失败');
      }
      deletedRuleCodes.add(ruleCode);
      saveDeletedCodes(deletedRuleCodes);
    } catch (e) {
      alertMock('删除失败：' + (e.message || '请重试'));
      deletingRule.value = false;
      return;
    }
    deletingRule.value = false;
  }

  subscriptionRules.value = subscriptionRules.value.filter(item => item.id !== rule.id);
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

const toggleAlertFollow = async (targetItem) => {
  const previousFollowed = targetItem.followed;
  const newFollowed = !previousFollowed;

  // 乐观更新：立即切换本地状态，UI 即时响应
  targetItem.followed = newFollowed;
  const source = listData.value.find((item) => item.id === targetItem.id);
  if (source) source.followed = newFollowed;
  if (newFollowed) {
    // 关注：同步加入关注列表
    const exists = followListData.value.find(item => item.id === targetItem.id);
    if (!exists) followListData.value.unshift(targetItem);
  } else {
    // 取消关注：从关注列表移除
    followListData.value = followListData.value.filter(item => item.id !== targetItem.id);
  }

  try {
    const res = await fetch(
      `/api/monitor/${encodeURIComponent(targetItem.id)}?status=${newFollowed ? 1 : 0}`,
      { method: 'POST' }
    );
    if (!res.ok) throw new Error('API error');
    const json = await res.json();
    if (json.code !== 200) throw new Error(json.msg);
  } catch {
    // API 失败不 revert 本地状态——乐观更新已生效
    // 服务端数据将在下次 fetchAlertList/fetchFollowList 时同步
  }
};

const followAuthor = async (item) => {
  try {
    const body = JSON.stringify({
      profile_id: '',
      platform: item.source || '',
      source_handle_norm: item.sourceHandle || item.author || '',
      author_name: item.author || '',
      avatar_url: ''
    });
    const res = await fetch('/api/monitor/authors/follow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body
    });
    if (!res.ok) throw new Error('API error');
    const json = await res.json();
    if (json.code === 200) {
      item.authorFollowed = true;
      item.authorTargetId = json.data.target_id;
      alert(`已关注作者: ${item.author}`);
    }
  } catch {
    alert('关注作者失败，请重试');
  }
};

const unfollowAuthor = async (item) => {
  try {
    const body = JSON.stringify({
      profile_id: item.authorTargetId || '',
      platform: item.source || '',
      source_handle_norm: item.sourceHandle || item.author || '',
      author_name: item.author || '',
      avatar_url: ''
    });
    const res = await fetch('/api/monitor/authors/unfollow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body
    });
    if (!res.ok) throw new Error('API error');
    const json = await res.json();
    if (json.code === 200) {
      item.authorFollowed = false;
      alert(`已取消关注作者: ${item.author}`);
    }
  } catch {
    alert('取消关注失败，请重试');
  }
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

const markAsRead = async (item) => {
  if (item.read) return;
  try {
    const res = await fetch(`/api/topics/alert/${encodeURIComponent(item.id)}/toggle_read`, {
      method: 'POST'
    });
    if (!res.ok) return;
    const json = await res.json();
    if (json.code === 200) {
      item.read = json.data.read_status === 1;
    }
  } catch {
    // 静默失败
  }
};
const markFalsePositive = async (item) => {
  if (!confirm('确定将此线索标记为”误报/噪音”吗？\n标记后该线索将从待办列表和统计图中彻底剔除。')) return;
  const previous = { falsePositive: item.falsePositive, selected: item.selected, followed: item.followed };
  item.falsePositive = true;
  item.selected = false;
  item.followed = false;
  followListData.value = followListData.value.filter(f => f.id !== item.id);
  try {
    const res = await fetch(`/api/topics/alert/${encodeURIComponent(item.id)}/false_positive`, { method: 'POST' });
    if (!res.ok) throw new Error('API error');
  } catch {
    item.falsePositive = previous.falsePositive;
    item.selected = previous.selected;
    item.followed = previous.followed;
    alert('误报标记失败，请重试');
  }
};
const translateItem = async (item, e) => {
  const btn = e.currentTarget;
  if (item.translatedContent) return;

  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 翻译中...'; btn.style.opacity = '0.8';
  try {
    const body = JSON.stringify({
      title: item.title || '',
      content: item.content || '',
      target_lang: '简体中文'
    });
    const res = await fetch('/api/topics/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code === 200 && json.data) {
      item.translatedContent = json.data;
      btn.innerHTML = '<i class="fa-solid fa-check"></i> 已翻译';
      btn.classList.add('translated');
      btn.style.color = '#10b981'; btn.style.borderColor = '#10b981';
      btn.style.background = 'rgba(16, 185, 129, 0.1)';
    } else {
      throw new Error(json.detail || json.msg || '翻译失败');
    }
  } catch (err) {
    btn.innerHTML = '<i class="fa-solid fa-language"></i> 翻译';
    btn.style.opacity = '1';
    alert('翻译失败：' + (err.message || '请重试'));
  }
};

const alertMock = (msg) => alert(msg);
const exportSingle = async (item) => {
  try {
    const res = await fetch(`/api/topics/alert/${encodeURIComponent(item.id)}/export`, { method: 'POST' });
    if (!res.ok) throw new Error('API error');
    const json = await res.json();
    if (json.code === 200) {
      item.exportStatus = json.data.export_status;
      alert(`已导出: ${item.title?.substring(0, 30) || '告警记录'}`);
    }
  } catch {
    alert('导出失败，请重试');
  }
};

const exportSelected = async () => {
  const selected = listData.value.filter(item => item.selected && !item.exportStatus);
  if (!selected.length) return alert('没有可导出的选中项');
  let count = 0;
  for (const item of selected) {
    try {
      const res = await fetch(`/api/topics/alert/${encodeURIComponent(item.id)}/export`, { method: 'POST' });
      const json = await res.json();
      if (json.code === 200) { item.exportStatus = 1; count++; }
    } catch { /* 跳过 */ }
  }
  alert(`导出完成: ${count}/${selected.length} 条`);
};

const exportAll = async () => {
  const pending = listData.value.filter(item => !item.exportStatus);
  if (!pending.length) return alert('所有数据均已导出');
  let count = 0;
  for (const item of pending) {
    try {
      const res = await fetch(`/api/topics/alert/${encodeURIComponent(item.id)}/export`, { method: 'POST' });
      const json = await res.json();
      if (json.code === 200) { item.exportStatus = 1; count++; }
    } catch { /* 跳过 */ }
  }
  alert(`导出完成: ${count}/${pending.length} 条`);
};

// 模态框逻辑
const openDetail = (item, parentItem = null) => {
  state.selectedDetailItem = Object.assign({}, parentItem || item, item); // 继承父级属性
  state.selectedDetailItem.read = true;
  state.isModalOpen = true;
  if (item.id && item.contentId) {
    fetchAlertDetail(item.id, item.contentId);
  } else {
    detailRawContent.value = '';
  }
};
const closeModal = () => {
  state.isModalOpen = false;
  detailRawContent.value = '';
  setTimeout(() => state.selectedDetailItem = null, 300);
};

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

fetchTopicList();
</script>


<style src="../assets/styles/pages/dashboard.css"></style>
