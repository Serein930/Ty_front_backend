<template>
  <div class="home-page">
    <header class="top-header">
      <div class="logo-area">
        <i class="fa-solid fa-shield-halved"></i> 天眼情报
      </div>
      <nav class="nav-menu">
        <a href="#" class="nav-item active"><i class="fa-regular fa-chart-bar"></i> 态势感知</a>
        <a href="#" class="nav-item" @click.prevent="goTo('/search')"><i class="fa-solid fa-magnifying-glass"></i> 情报检索</a>
        <a href="#" class="nav-item" @click.prevent="goTo('/dashboard')"><i class="fa-solid fa-circle-exclamation"></i> 监测预警</a>
        <a href="#" class="nav-item" @click.prevent="goTo('/topology')"><i class="fa-solid fa-share-nodes"></i> 取证溯源</a>
      </nav>
      <div class="header-right">
        <span>administrator, 欢迎您!</span>
        <span class="time-display">{{ nowTime }} UTC</span>
        <div class="view-selector-wrapper">
          <i class="fa-solid fa-satellite-dish"></i>
          <select v-model="selectedSubscription" class="view-select" @change="applySubscription">
            <option v-for="s in subscriptions" :key="s.name" :value="s.name">{{ s.name }}</option>
          </select>
        </div>
        <div class="btn-logout" @click="logoutToLogin"><i class="fa-solid fa-power-off"></i> 退出</div>
      </div>
    </header>

    <div id="sysToast" class="sys-toast" :class="{ show: toastVisible }">
      <i class="fa-solid fa-circle-check"></i>
      <span>{{ toastMessage }}</span>
    </div>

    <div class="main-container">
      <div class="panel" style="grid-column: 1; grid-row: 1;">
        <div class="panel-title"><span class="title-text">我的近期案件</span></div>
        <div class="controls">
          <select v-model="warningStatusFilter">
            <option value="all">全部状态</option>
            <option value="待处理">待处理</option>
            <option value="正在研判">正在研判</option>
            <option value="已结案">已结案</option>
          </select>
        </div>
        <div class="warning-container">
          <div class="case-list">
            <div
              v-for="item in filteredWarnings"
              :key="item.id"
              class="case-card"
              :class="`level-${item.level}`"
              @click="showWarningDetail(item)"
            >
              <div class="case-header">
                <div class="case-title">
                  <span class="pulse-dot" v-if="item.level === 'high'"></span>
                  {{ item.name }}
                </div>
                <div class="case-id">CASE-{{ String(item.id).padStart(4, '0') }}</div>
              </div>
              <div class="case-meta">
                <div class="case-meta-info">
                  <span class="case-meta-item"><i class="fa-regular fa-clock"></i>{{ item.time }}</span>
                  <span class="case-meta-item"><i class="fa-solid fa-location-dot"></i>{{ item.country }}</span>
                </div>
                <span class="case-status-badge" :class="statusClass(item.status)">{{ item.status }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel" style="grid-column: 2; grid-row: 1;">
        <div class="panel-title"><span class="title-text">主题情报总量</span></div>
        <div class="controls" style="left:auto;right:15px;">
          <select v-model="selectedType">
            <option value="all">请选择类别</option>
            <option value="black">黑灰产</option>
            <option value="fraud">诈骗</option>
            <option value="attack">攻击</option>
          </select>
          <select v-model="statsTimeFilter">
            <option value="24h">请选择时间</option>
            <option value="7d">近7天</option>
            <option value="30d">近30天</option>
          </select>
        </div>
        <div class="center-stats">
          <div class="circle-stat">
            <div class="stat-num">{{ warningCount }}</div>
            <div class="stat-label">待处理</div>
          </div>
          <div class="main-stat">
            <div class="main-title">当前监测总数</div>
            <div class="main-num">{{ totalCount }}</div>
            <div class="main-time">{{ nowTimeDisplay }}</div>
          </div>
          <div class="circle-stat">
            <div class="stat-num">{{ handledCount }}</div>
            <div class="stat-label">已处置</div>
          </div>
        </div>
      </div>

      <div class="panel" style="grid-column: 3; grid-row: 1;">
        <div class="panel-title"><span class="title-text">今日情报趋势</span></div>
        <div class="controls">
          <select v-model="trendTypeFilter">
            <option value="all">请选择来源</option>
            <option value="black">黑灰产</option>
            <option value="fraud">诈骗</option>
            <option value="attack">攻击</option>
          </select>
          <select v-model="trendRangeFilter">
            <option value="24">今天</option>
            <option value="12">12小时</option>
          </select>
        </div>
        <div ref="trendChartRef" id="trendChart"></div>
      </div>

      <div class="panel" style="grid-column: 1; grid-row: 2 / 4;">
        <div class="panel-title" style="display:flex;justify-content:space-between;align-items:center;padding-right:15px;">
          <span class="title-text">重点人物追踪</span>
          <button class="view-all-btn" style="position:static;" @click="personsModalVisible = true">查看全部</button>
        </div>
        <div class="controls">
          <select v-model="selectedType">
            <option value="all">全部类别</option>
            <option value="black">黑灰产</option>
            <option value="fraud">诈骗</option>
            <option value="attack">攻击</option>
          </select>
        </div>
        <div class="hot-list active">
          <div
            v-for="p in filteredPersons"
            :key="p.id"
            class="target-card"
            :class="{ 'level-critical': p.score >= 90 }"
            @click="showPersonDetail(p)"
          >
            <div class="target-avatar-wrapper">
              <div class="avatar-fallback">{{ avatarInitial(p.alias) }}</div>
              <span class="target-status" :class="p.score >= 90 ? 'danger' : ''"></span>
            </div>
            <div class="target-info">
              <div class="target-header">
                <div class="target-alias"><i class="fa-solid fa-user-secret"></i> {{ p.alias }}</div>
                <div class="target-city"><i class="fa-solid fa-crosshairs"></i> {{ p.city }}</div>
              </div>
              <div class="target-loc">疑似涉及大规模洗钱活动的核心人员。近期频繁跨平台活跃。</div>
              <div class="target-desc">{{ p.desc }}</div>
              <div class="target-tags">
                <span class="target-tag" v-for="tag in p.tags" :key="tag">{{ tag }}</span>
              </div>
              <div class="target-threat-box">
                <span class="p-score-badge" :class="scoreClass(p.score)">P-{{ p.score }}</span>
                <span class="conf-badge">{{ p.confidence }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel ticker-panel" style="grid-column: 2; grid-row: 2;">
        <div class="ticker-left">
          <i class="fa-solid fa-satellite-dish"></i>
          <span class="ticker-title">重点监控节点</span>
        </div>
        <div class="monitored-entities-wrapper">
          <div class="monitored-entities-track">
            <div class="marquee-group" v-for="i in 2" :key="i">
              <div class="monitored-entity" v-for="m in monitoredEntities" :key="`${i}-${m.id}`">
                <div class="entity-avatar">
                  <div class="avatar-fallback avatar-mini">{{ avatarInitial(m.name) }}</div>
                  <span class="entity-platform" :class="m.platformClass"><i :class="m.icon"></i></span>
                </div>
                <div class="entity-info">
                  <div class="entity-name">{{ m.name }}</div>
                  <div class="entity-stat" :class="m.levelClass">{{ m.stat }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel" style="grid-column: 2; grid-row: 3;">
        <div class="panel-title" style="justify-content:space-between;padding-right:15px;gap:15px;">
          <div class="title-text">态势地图</div>
          <div class="pill-tabs-container">
            <div class="pill-tab" :class="{ active: mapScene === 'global' }" @click="mapScene = 'global'; mapMode = 'world'">全球态势</div>
            <div class="pill-tab" :class="{ active: mapScene === 'black' }" @click="mapScene = 'black'; mapMode = 'world'">黑产网络</div>
            <div class="pill-tab" :class="{ active: mapScene === 'leak' }" @click="mapScene = 'leak'; mapMode = 'world'">数据泄露</div>
            <div class="pill-tab" :class="{ active: mapScene === 'terror' }" @click="mapScene = 'terror'; mapMode = 'world'">暴恐分布</div>
            <div class="pill-tab" :class="{ active: mapScene === 'smuggle' }" @click="mapScene = 'smuggle'; mapMode = 'world'">走私链路</div>
            <div class="pill-tab" :class="{ active: mapScene === 'drug' }" @click="mapScene = 'drug'; mapMode = 'world'">毒品流向</div>
          </div>
        </div>
        <div class="map-controls">
          <button id="btnBackWorld" class="view-all-btn" v-show="mapMode === 'china'" @click="mapMode = 'world'">
            <i class="fa-solid fa-earth-asia"></i> 返回全球
          </button>
        </div>
        <div ref="mapChartRef" id="mapChart" v-show="!mapFallback"></div>
        <div v-show="mapFallback" class="map-fallback">
          <div class="map-fallback-grid"></div>
          <div class="map-fallback-line line-a"></div>
          <div class="map-fallback-line line-b"></div>
          <div class="map-fallback-line line-c"></div>
          <div class="map-fallback-node node-cn">中国</div>
          <div class="map-fallback-node node-us">美国</div>
          <div class="map-fallback-node node-jp">日本</div>
          <div class="map-fallback-node node-sg">新加坡</div>
          <div class="map-fallback-tip">地图底图离线模式</div>
        </div>
      </div>

      <div class="panel" style="grid-column: 3; grid-row: 2 / 4;">
        <div class="panel-title" style="display:flex;justify-content:space-between;align-items:center;padding-right:15px;">
          <span class="title-text">实时情报事件簇</span>
          <button class="view-all-btn" style="position:static;" @click="eventsModalVisible = true">事件列表</button>
        </div>
        <div class="controls" style="left:auto;right:15px;gap:8px;">
          <span class="live-pill live-pill-danger"><i class="fa-solid fa-signal"></i> 智能归并中</span>
          <span class="live-pill"><i class="fa-solid fa-shield-halved"></i> 自动降噪</span>
        </div>
        <div id="sourceChart">
          <div class="live-feed-shell">
            <div class="live-feed-timeline">
              <div class="live-feed-scroll">
                <div class="live-feed-track" :style="{ '--scroll-distance': `${feedScrollDistance}px` }">
                  <div class="live-feed-item" v-for="f in doubledFeed" :key="f.uid" @click="showFeedDetail(f)">
                    <div class="live-feed-header">
                      <span class="live-source-group"><i :class="f.icon"></i>{{ f.source }}</span>
                      <span class="cluster-count-badge"><i class="fa-solid fa-layer-group"></i>{{ f.clusterCount }}条归并</span>
                      <span class="live-severity-badge" :class="f.level">{{ levelText(f.level) }}</span>
                      <span class="live-meta"><i class="fa-regular fa-clock"></i>{{ f.time }}</span>
                    </div>
                    <div class="live-feed-title">{{ f.title }}</div>
                    <div class="live-feed-text">{{ f.text }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer class="footer" style="grid-column: 1 / 4; grid-row: 4;">
        <div class="footer-copyright">© 2023 东莞智盾 版权所有 | 天眼情报平台 v2.1 (Tactical Edition)</div>
        <div class="footer-links">
          <a href="#" class="footer-link">关于我们</a>
          <a href="#" class="footer-link">隐私政策</a>
          <a href="#" class="footer-link">服务条款</a>
        </div>
      </footer>
    </div>

    <div id="detailModal" class="modal-overlay" v-show="detailVisible" @click.self="closeDetailModal">
      <div class="modal-content" :style="detailMode === 'person' ? 'max-width: 1400px; min-height: 680px;' : 'max-width: 900px; min-height: 500px;'">
        <div class="modal-header">
          <div class="modal-title">{{ detailTitle }}</div>
          <button class="modal-close" @click="closeDetailModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="detailMode === 'person' && currentPerson" class="person-detail-layout">
            <div class="person-detail-head">
              <div class="person-detail-avatar">{{ avatarInitial(currentPerson.alias) }}</div>
              <div class="person-detail-main">
                <div class="person-detail-name-row">
                  <span class="person-detail-name">{{ currentPerson.alias }}</span>
                  <span class="person-badge high">HIGH TARGET</span>
                  <span class="p-score-badge" :class="scoreClass(currentPerson.score)">P-{{ currentPerson.score }}</span>
                  <span class="conf-badge">{{ currentPerson.confidence }}% 综合置信度</span>
                </div>
                <div class="person-detail-meta">物理侧写: {{ currentPerson.city }} / {{ currentPerson.country }}</div>
                <div class="person-detail-desc">{{ currentPerson.desc }}</div>
              </div>
            </div>

            <div class="person-asset-row">
              <div class="asset-group">
                <div class="asset-title">虚拟身份与映射</div>
                <div class="asset-tags"><span class="asset-tag" v-for="tag in currentPerson.assets.identities" :key="tag"><i class="fa-solid fa-user"></i>{{ tag }}</span></div>
              </div>
              <div class="asset-group">
                <div class="asset-title">通讯资产 (Comm Assets)</div>
                <div class="asset-tags"><span class="asset-tag" v-for="tag in currentPerson.assets.comms" :key="tag"><i class="fa-solid fa-envelope"></i>{{ tag }}</span></div>
              </div>
              <div class="asset-group">
                <div class="asset-title">资金资产 (Financial Assets)</div>
                <div class="asset-tags"><span class="asset-tag" v-for="tag in currentPerson.assets.finance" :key="tag"><i class="fa-solid fa-wallet"></i>{{ tag }}</span></div>
              </div>
              <div class="asset-group">
                <div class="asset-title">网络足迹 (Network Footprints)</div>
                <div class="asset-tags"><span class="asset-tag" v-for="tag in currentPerson.assets.network" :key="tag"><i class="fa-solid fa-globe"></i>{{ tag }}</span></div>
              </div>
              <div class="asset-group">
                <div class="asset-title">历史关联案件 (Cases)</div>
                <div class="asset-tags"><span class="asset-tag" v-for="tag in currentPerson.assets.cases" :key="tag"><i class="fa-solid fa-link"></i>{{ tag }}</span></div>
              </div>
            </div>

            <div class="person-chart-row">
              <div class="person-chart-card">
                <div class="person-chart-title">目标综合威胁指数 (Threat Index)</div>
                <div :id="`personRadar-${currentPerson.id}`" class="person-chart"></div>
              </div>
              <div class="person-chart-card">
                <div class="person-chart-title">全网行为活跃热力图 (UTC)</div>
                <div :id="`personHeat-${currentPerson.id}`" class="person-chart"></div>
              </div>
              <div class="person-chart-card">
                <div class="person-chart-title">目标核心关系图谱</div>
                <div :id="`personGraph-${currentPerson.id}`" class="person-chart"></div>
              </div>
            </div>

            <div class="person-detail-actions">
              <button class="btn-dash3 danger"><i class="fa-solid fa-circle-xmark"></i> 下发布控</button>
              <button class="btn-dash3 primary" @click="openCloneWorkspace(currentPerson)"><i class="fa-solid fa-robot"></i> 生成数字身份</button>
              <button class="btn-dash3 success"><i class="fa-solid fa-download"></i> 导出画像简报</button>
            </div>
          </div>
          <div v-else class="detail-content-card" v-html="detailHtml"></div>
        </div>
      </div>
    </div>

    <div id="eventsListModal" class="modal-overlay" v-show="eventsModalVisible" @click.self="eventsModalVisible = false">
      <div class="modal-content" style="max-width: 1200px;">
        <div class="modal-header">
          <div class="modal-title">事件列表</div>
          <button class="modal-close" @click="eventsModalVisible = false">&times;</button>
        </div>
        <div class="modal-body">
          <table class="events-table">
            <thead>
              <tr>
                <th>事件ID</th>
                <th>事件名称</th>
                <th>国家</th>
                <th>等级</th>
                <th>状态</th>
                <th>时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in warnings" :key="`ev-${row.id}`">
                <td>CASE-{{ String(row.id).padStart(4, '0') }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.country }}</td>
                <td>{{ row.level }}</td>
                <td>{{ row.status }}</td>
                <td>{{ row.time }}</td>
                <td>
                  <button class="btn-action" @click="showWarningDetail(row)">详情</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div id="personsListModal" class="modal-overlay" v-show="personsModalVisible" @click.self="personsModalVisible = false">
      <div class="modal-content" style="max-width: 1200px;">
        <div class="modal-header">
          <div class="modal-title">重点人物列表 - {{ personsModalCountry === 'all' ? '全域' : personsModalCountry }}</div>
          <button class="modal-close" @click="personsModalVisible = false">&times;</button>
        </div>
        <div class="modal-body">
          <table class="events-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>别名</th>
                <th>地区</th>
                <th>平台</th>
                <th>风险分</th>
                <th>标签</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in personsTableRows" :key="`person-${row.id}`">
                <td>{{ row.id }}</td>
                <td>{{ row.alias }}</td>
                <td>{{ row.country }}</td>
                <td>{{ row.platform }}</td>
                <td>{{ row.score }}</td>
                <td>{{ row.tags.join(' / ') }}</td>
                <td>
                  <button class="btn-action" @click="showPersonDetail(row)">画像</button>
                  <button class="btn-action" @click="openCloneWorkspace(row)">分身</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div id="orgListModal" class="modal-overlay" v-show="orgModalVisible" @click.self="orgModalVisible = false">
      <div class="modal-content" style="max-width: 900px; height: 700px;">
        <div class="modal-header" style="background: #0f1729; border-bottom: 1px solid #1e293b;">
          <div class="modal-title" style="color:#fff;">群组列表 - {{ orgCountry }}</div>
          <button class="modal-close" @click="orgModalVisible = false">&times;</button>
        </div>
        <div class="modal-body" style="background: #0f1729; padding: 0;">
          <div class="org-tabs">
            <div class="org-tab-item" :class="{ active: orgTab === 'telegram' }" @click="orgTab = 'telegram'">Telegram群组</div>
            <div class="org-tab-item" :class="{ active: orgTab === 'forum' }" @click="orgTab = 'forum'">论坛频道</div>
            <div class="org-tab-item" :class="{ active: orgTab === 'social' }" @click="orgTab = 'social'">社媒社群</div>
          </div>
          <div class="org-filter-bar">
            <select class="org-select" v-model="orgRiskFilter">
              <option value="all">风险等级: 全部</option>
              <option value="high">高危</option>
              <option value="medium">中危</option>
              <option value="low">低危</option>
            </select>
          </div>
          <div class="org-list-container">
            <div class="drawer-event-item" v-for="g in filteredOrgRows" :key="g.id">
              <div class="drawer-event-title">{{ g.name }}</div>
              <div class="drawer-event-meta">
                <span>{{ g.platform }} · {{ g.members }} 成员</span>
                <span>{{ g.risk }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div id="nativePlatformModal" class="modal-overlay" v-show="nativePlatformVisible" @click.self="nativePlatformVisible = false" style="z-index:1100;">
      <div class="modal-content" style="width:90%;max-width:520px;height:80vh;max-height:680px;background:#000;border:none;border-radius:12px;overflow:hidden;">
        <div class="tw-app" v-if="nativePlatformType === 'x'">
          <div class="tw-header"><h2>Home</h2><span class="tw-header-sub">For you</span></div>
          <div class="tw-post" v-for="i in 3" :key="`x-${i}`">
            <img class="tw-avatar" :src="activePlatformAvatar" alt="avatar" />
            <div class="tw-content">
              <div class="tw-user-info"><span class="tw-name">{{ activePlatformName }}</span><span class="tw-handle">@intel_watch</span><span class="tw-time">· {{ i }}h</span></div>
              <div class="tw-text">{{ activePlatformText }}</div>
            </div>
          </div>
        </div>
        <div class="tg-app" v-else-if="nativePlatformType === 'telegram'">
          <div class="tg-header">
            <img class="tg-avatar" :src="activePlatformAvatar" alt="avatar" />
            <div class="tg-title-area"><div class="tg-name">{{ activePlatformName }}</div><div class="tg-members">12,842 members</div></div>
          </div>
          <div class="tg-chat-bg">
            <div class="tg-date-pill">Today</div>
            <div class="tg-msg-bubble" v-for="i in 4" :key="`tg-${i}`">
              <span class="tg-msg-author">{{ activePlatformName }}</span>
              {{ activePlatformText }}
              <div class="tg-msg-meta">{{ 10 + i }}:2{{ i }}</div>
            </div>
          </div>
        </div>
        <div class="fb-app" v-else>
          <div class="fb-header">{{ activePlatformName }}</div>
          <div class="fb-post" v-for="i in 2" :key="`fb-${i}`">
            <div class="fb-author-row">
              <img class="tw-avatar" :src="activePlatformAvatar" alt="avatar" />
              <div>
                <div class="fb-author-name">{{ activePlatformName }}</div>
                <div class="fb-time">{{ i }} 小时前</div>
              </div>
            </div>
            <div class="fb-text">{{ activePlatformText }}</div>
          </div>
        </div>
      </div>
    </div>

    <div id="cloneWorkspaceModal" class="modal-overlay" v-show="cloneWorkspaceVisible" @click.self="cloneWorkspaceVisible = false" style="z-index:1200;">
      <div class="modal-content" style="max-width: 1400px; width: 95%; height: 90vh;">
        <div class="modal-header" style="background: linear-gradient(90deg, #1e1b4b 0%, #0f172a 100%); border-bottom-color: #4338ca;">
          <div class="modal-title" style="color: #a855f7; display:flex;align-items:center;gap:8px;"><i class="fa-solid fa-robot"></i> 数字分身社工工作台</div>
          <button class="modal-close" @click="cloneWorkspaceVisible = false">&times;</button>
        </div>
        <div class="workspace-layout">
          <div class="ws-sidebar">
            <div class="ws-section-title">Agent配置 <span class="status-dot"></span></div>
            <div class="ws-config-box">
              <label class="ws-label">目标人物</label>
              <input class="ws-input" :value="cloneTarget?.alias || ''" disabled />
              <label class="ws-label">侵入通道</label>
              <select class="ws-select" v-model="cloneChannel">
                <option value="telegram">Telegram</option>
                <option value="x">X</option>
                <option value="facebook">Facebook</option>
              </select>
            </div>
            <div class="ws-config-box">
              <div class="agent-stats">
                <div class="agent-stat-card"><div class="agent-stat-val">{{ cloneStats.replies }}</div><div class="ws-label">回复轮次</div></div>
                <div class="agent-stat-card"><div class="agent-stat-val">{{ cloneStats.hitRate }}%</div><div class="ws-label">命中率</div></div>
              </div>
            </div>
          </div>
          <div class="ws-chat-area">
            <div class="chat-header">
              <div class="chat-target-info">
                <img class="chat-target-avatar" :src="cloneTarget?.avatar || 'https://i.pravatar.cc/80?img=10'" alt="avatar" />
                <div>
                  <div style="font-size:13px;color:#fff;font-weight:700;">{{ cloneTarget?.alias || 'Unknown' }}</div>
                  <div style="font-size:11px;color:#94a3b8;">通道: {{ cloneChannel.toUpperCase() }}</div>
                </div>
              </div>
            </div>
            <div class="chat-messages">
              <div v-for="m in cloneMessages" :key="m.id" class="msg-bubble-wrapper" :class="m.side">
                <img class="msg-avatar" :src="m.side === 'left' ? (cloneTarget?.avatar || 'https://i.pravatar.cc/40?img=4') : 'https://i.pravatar.cc/40?img=18'" alt="avatar" />
                <div class="msg-bubble">
                  <div v-if="m.thought" class="llm-thought">{{ m.thought }}</div>
                  <div>{{ m.text }}</div>
                  <div class="msg-meta"><span>{{ m.time }}</span></div>
                </div>
              </div>
            </div>
            <div class="chat-input-area">
              <div class="hitl-toolbar">
                <span style="font-size:12px;color:#94a3b8;">HITL人工审核</span>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="hitlEnabled" />
                  <span class="slider"></span>
                </label>
              </div>
              <textarea class="hitl-textarea" v-model="cloneDraft" placeholder="输入话术...按发送模拟大模型对话"></textarea>
              <div style="display:flex;justify-content:flex-end;margin-top:10px;gap:10px;">
                <button class="btn-dash3" @click="cloneDraft = ''">清空</button>
                <button class="btn-dash3 primary" @click="sendAgentMessage"><i class="fa-solid fa-paper-plane"></i> 发送</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="map-context-menu" v-show="mapContextVisible" :style="{ left: `${mapContextX}px`, top: `${mapContextY}px` }" @click.stop>
      <div class="map-context-header">{{ mapContextCountry }} 快捷操作</div>
      <div class="map-context-body">
        <button class="btn-action" style="margin-bottom:8px; width:100%;" @click="openCircleMenuAtContext">
          <i class="fa-solid fa-bullseye"></i> 打开战术菜单
        </button>
        <button class="btn-action" style="width:100%;" @click="showCountryDrawerFromMenu">
          <i class="fa-solid fa-address-card"></i> 打开地区档案
        </button>
      </div>
    </div>

    <div id="circleMenu" class="circle-menu" v-show="circleMenuVisible" :style="{ left: `${circleMenuX}px`, top: `${circleMenuY}px` }" @click.stop>
      <div class="circle-menu-item" style="top:8px;left:65px;" @click="showCountryDrawerFromMenu"><i class="fa-solid fa-earth-asia"></i></div>
      <div class="circle-menu-item" style="top:65px;right:8px;" @click="showCountryEventsList(mapContextCountry)"><i class="fa-solid fa-list"></i></div>
      <div class="circle-menu-item" style="bottom:8px;left:65px;" @click="showPersonList(mapContextCountry)"><i class="fa-solid fa-user-group"></i></div>
      <div class="circle-menu-item" style="top:65px;left:8px;" @click="openOrgList(mapContextCountry)"><i class="fa-solid fa-users"></i></div>
      <div class="circle-menu-center" @click="circleMenuVisible = false"><i class="fa-solid fa-times"></i></div>
    </div>

    <div id="countryEventsListModal" class="modal-overlay" v-show="countryEventsModalVisible" @click.self="countryEventsModalVisible = false">
      <div class="modal-content" style="max-width: 1200px;">
        <div class="modal-header">
          <div class="modal-title">{{ countryEventsTitle }}</div>
          <button class="modal-close" @click="countryEventsModalVisible = false">&times;</button>
        </div>
        <div class="modal-body">
          <table class="events-table">
            <thead>
              <tr>
                <th>事件ID</th>
                <th>事件名称</th>
                <th>来源类型</th>
                <th>等级</th>
                <th>状态</th>
                <th>时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in countryEventRows" :key="`country-ev-${row.id}`">
                <td>CASE-{{ String(row.id).padStart(4, '0') }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.type }}</td>
                <td>{{ row.level }}</td>
                <td>{{ row.status }}</td>
                <td>{{ row.time }}</td>
                <td><button class="btn-action" @click="showWarningDetail(row)">详情</button></td>
              </tr>
              <tr v-if="countryEventRows.length === 0">
                <td colspan="7" style="text-align:center;color:#8c9db5;">暂无事件数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div id="countryDrawer" class="country-drawer" :class="{ active: drawerVisible }">
      <div class="drawer-header">
        <div class="drawer-title"><i class="fa-solid fa-earth-americas"></i> {{ drawerCountry }} 档案</div>
        <button class="drawer-close" @click="drawerVisible = false">&times;</button>
      </div>
      <div class="drawer-body">
        <div class="drawer-stat-grid">
          <div class="drawer-stat-card">
            <div class="drawer-stat-val">{{ drawerThreat }}</div>
            <div class="drawer-stat-label">风险评分</div>
          </div>
          <div class="drawer-stat-card" style="background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.2);">
            <div class="drawer-stat-val">{{ drawerCount }}</div>
            <div class="drawer-stat-label">近7天情报</div>
          </div>
        </div>

        <div class="drawer-section-title">
          <span>重点关注人物 (TOP5)</span>
          <button class="btn-action" @click="showPersonList(drawerCountry)">查看全部</button>
        </div>
        <div class="drawer-person-list">
          <div class="drawer-person-card" v-for="p in drawerPersons" :key="p.id" @click="showPersonDetail(p)">
            <div class="drawer-person-avatar"><img :src="p.avatar" alt="avatar" /></div>
            <div class="drawer-person-info">
              <div class="drawer-person-name">{{ p.alias }} <span class="p-score-badge" :class="scoreClass(p.score)">P{{ p.score }}</span></div>
              <div class="drawer-person-desc">{{ p.desc }}</div>
            </div>
          </div>
        </div>

        <div class="drawer-section-title">
          <span>近期重要事件</span>
          <button class="btn-action" @click="showCountryEventsList(drawerCountry)">查看全部</button>
        </div>
        <div class="drawer-event-list">
          <div class="drawer-event-item" v-for="e in drawerEvents" :key="e.id" @click="showWarningDetail(e)">
            <div class="drawer-event-title">{{ e.name }}</div>
            <div class="drawer-event-meta"><span>{{ e.time }}</span><span>{{ e.level }}</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as echarts from 'echarts';
import 'echarts-wordcloud';
import { useRouter } from 'vue-router';
import { logout } from '../auth';

const router = useRouter();

const trendChartRef = ref(null);
const mapChartRef = ref(null);
const trendChart = ref(null);
const mapChart = ref(null);

const warningStatusFilter = ref('all');
const selectedType = ref('all');
const statsTimeFilter = ref('24h');
const trendTypeFilter = ref('all');
const trendRangeFilter = ref('24');
const selectedSubscription = ref('全局监控态势（默认）');
const mapMode = ref('world');
const mapScene = ref('global');
const mapFallback = ref(false);

const nowTime = ref('');
const nowTimeDisplay = ref('');
let timeTimer = null;

const toastVisible = ref(false);
const toastMessage = ref('');
let toastTimer = null;

const detailVisible = ref(false);
const detailTitle = ref('详情');
const detailHtml = ref('');
const detailMode = ref('generic');
const currentPerson = ref(null);
const personChartInstances = [];

const eventsModalVisible = ref(false);
const personsModalVisible = ref(false);
const orgModalVisible = ref(false);
const nativePlatformVisible = ref(false);
const cloneWorkspaceVisible = ref(false);
const countryEventsModalVisible = ref(false);

const drawerVisible = ref(false);
const drawerCountry = ref('全球');
const personsModalCountry = ref('all');
const countryEventsTitle = ref('国家事件列表');
const mapContextVisible = ref(false);
const mapContextX = ref(0);
const mapContextY = ref(0);
const mapContextCountry = ref('中国');
const circleMenuVisible = ref(false);
const circleMenuX = ref(0);
const circleMenuY = ref(0);
const orgCountry = ref('中国');
const orgTab = ref('telegram');
const orgRiskFilter = ref('all');

const nativePlatformType = ref('telegram');
const activePlatformName = ref('');
const activePlatformText = ref('');
const activePlatformAvatar = ref('https://i.pravatar.cc/80?img=8');

const cloneTarget = ref(null);
const cloneChannel = ref('telegram');
const cloneDraft = ref('');
const hitlEnabled = ref(true);
const cloneStats = ref({ replies: 0, hitRate: 93 });
const cloneMessages = ref([]);

const subscriptions = [
  { name: '全局监控态势（默认）', country: null, type: 'all' },
  { name: '中国重点监测战位', country: '中国', type: 'all' },
  { name: '东南亚黑灰产战位', country: '新加坡', type: 'black' }
];

const warnings = ref([
  { id: 1, name: '跨境Telegram频道诈骗组织活跃', time: '2023-10-27 11:24:19', level: 'high', country: '中国', type: 'fraud', status: '待处理', detail: '多个TG频道同步发布高收益投资诱导内容，疑似同团伙控制。' },
  { id: 2, name: '暗网信用卡交易论坛出现新卖家', time: '2023-10-27 10:11:03', level: 'medium', country: '美国', type: 'black', status: '正在研判', detail: '新账户72小时内上架大量卡料，活跃于多个交易串。' },
  { id: 3, name: '仿冒支付页面钓鱼攻击升级', time: '2023-10-27 09:43:30', level: 'high', country: '中国', type: 'attack', status: '待处理', detail: '检测到批量仿冒收银台页面并通过短信进行分发。' },
  { id: 4, name: '跨境洗钱链路关联钱包增多', time: '2023-10-26 21:16:45', level: 'medium', country: '新加坡', type: 'black', status: '正在研判', detail: '链上标签显示新地址簇与历史风险实体关系增强。' },
  { id: 5, name: 'Apache漏洞攻击溯源', time: '2023-10-23 10:55:47', level: 'high', country: '日本', type: 'attack', status: '已结案', detail: '检测到Apache Struts2远程代码执行漏洞攻击尝试，需研判攻击组织。' }
]);

const hotPersons = ref([
  {
    id: 101,
    alias: 'Nexus_47',
    country: '中国',
    city: '广东省 深圳市',
    platform: 'Telegram',
    score: 95,
    confidence: 97,
    type: 'fraud',
    tags: ['洗钱', '电诈', '分销'],
    desc: '活跃于跨境诈骗群组，近期交易频次上升。',
    avatar: 'https://i.pravatar.cc/80?img=12',
    assets: {
      identities: ['Nexus_47', 'Nexus-OPS', 'K-Node'],
      comms: ['+852 6912 88xx', 'nexus47@proton.me', '@nexus_ops'],
      finance: ['TRX: TQ7s...9Aa', 'USDT OTC 账户簇 #A31', '风险钱包簇 RW-13'],
      network: ['103.221.xx.xx', 'AS4134 异常节点', 'Tor Exit #9f3'],
      cases: ['Case-2024-041 电诈洗钱链', 'Case-2023-227 跨境资金回流']
    }
  },
  {
    id: 102,
    alias: 'GhostMall',
    country: '美国',
    city: '加利福尼亚州 洛杉矶',
    platform: 'Darkweb',
    score: 88,
    confidence: 92,
    type: 'black',
    tags: ['卡料', '黑市'],
    desc: '暗网交易论坛核心中介，关联多个卖家。',
    avatar: 'https://i.pravatar.cc/80?img=31',
    assets: {
      identities: ['GhostMall', 'GM-Root'],
      comms: ['session: 05ab...d2', 'ghostmall@onionmail.org'],
      finance: ['BTC: bc1q...k2p', 'Monero: 87x...4u'],
      network: ['TOR Hidden Service #gmu7', 'Cloud VPS 簇 #US-2'],
      cases: ['Case-2024-019 卡料交易网络']
    }
  },
  {
    id: 103,
    alias: 'RiverFox',
    country: '中国',
    city: '浙江省 杭州市',
    platform: 'X',
    score: 79,
    confidence: 86,
    type: 'attack',
    tags: ['漏洞', '扫描'],
    desc: '频繁发布漏洞利用脚本与目标IP段信息。',
    avatar: 'https://i.pravatar.cc/80?img=22',
    assets: {
      identities: ['RiverFox', 'rf_lab'],
      comms: ['riverfox@riseup.net', '@rf_scan'],
      finance: ['ETH: 0x8a...f3'],
      network: ['CDN 节点簇 #CN-EAST', '扫描出口 #hx2'],
      cases: ['Case-2023-088 漏洞扩散事件']
    }
  },
  {
    id: 104,
    alias: 'BlueLedger',
    country: '新加坡',
    city: '新加坡 乌节路',
    platform: 'Telegram',
    score: 84,
    confidence: 89,
    type: 'black',
    tags: ['USDT', 'OTC'],
    desc: '加密资产OTC群主，地址簇关联异常。',
    avatar: 'https://i.pravatar.cc/80?img=52',
    assets: {
      identities: ['BlueLedger', 'BL-trade'],
      comms: ['+65 91xx 77xx', '@blueledger_sg'],
      finance: ['USDT 簇 #SG-11', 'TRX: TY2...Kq'],
      network: ['SG IDC 节点 #3', '边界网关 #A7'],
      cases: ['Case-2024-113 OTC 洗钱路径']
    }
  }
]);

const feed = ref([
  { id: 1, source: 'Telegram', icon: 'fa-brands fa-telegram', level: 'critical', clusterCount: 12, time: '11:26', title: '诈骗脚本包更新', text: '发现新版本话术模板，含银行客服冒充流程。', country: '中国' },
  { id: 2, source: 'Darkweb', icon: 'fa-solid fa-mask', level: 'high', clusterCount: 8, time: '11:14', title: '卡料交易价格波动', text: '欧美卡料批发价下调，疑似供给增加。', country: '美国' },
  { id: 3, source: 'X', icon: 'fa-brands fa-x-twitter', level: 'medium', clusterCount: 6, time: '10:58', title: '漏洞利用POC传播', text: '多个账号扩散同一漏洞POC链接，需持续跟踪。', country: '日本' },
  { id: 4, source: 'Facebook', icon: 'fa-brands fa-facebook', level: 'high', clusterCount: 4, time: '10:33', title: '仿冒投放活动', text: '发现新一轮仿冒商城广告，导流至钓鱼域名。', country: '新加坡' }
]);

const monitoredEntities = ref([
  { id: 1, name: 'Nexus_47', stat: '高危链路活跃', levelClass: 'critical', platformClass: 'plat-tg', icon: 'fa-brands fa-telegram', avatar: 'https://i.pravatar.cc/40?img=12' },
  { id: 2, name: 'GhostMall', stat: '黑市成交增长', levelClass: 'warning', platformClass: 'plat-tor', icon: 'fa-solid fa-ghost', avatar: 'https://i.pravatar.cc/40?img=31' },
  { id: 3, name: 'RiverFox', stat: '漏洞话题上升', levelClass: 'warning', platformClass: 'plat-x', icon: 'fa-brands fa-x-twitter', avatar: 'https://i.pravatar.cc/40?img=22' },
  { id: 4, name: 'BlueLedger', stat: '资金流向异常', levelClass: 'critical', platformClass: 'plat-fb', icon: 'fa-brands fa-facebook-f', avatar: 'https://i.pravatar.cc/40?img=52' }
]);

const countryCoordinates = {
  中国: [116.4074, 39.9042],
  美国: [-95.7129, 37.0902],
  日本: [139.6917, 35.6895],
  新加坡: [103.8198, 1.3521]
};

const orgRows = ref([
  { id: 1, name: 'SEA-OTC-HUB', platform: 'telegram', risk: 'high', members: 8421, country: '新加坡' },
  { id: 2, name: 'Fraud-Script-Market', platform: 'forum', risk: 'high', members: 2388, country: '中国' },
  { id: 3, name: 'Carding-Exchange', platform: 'forum', risk: 'medium', members: 1350, country: '美国' },
  { id: 4, name: 'BlueLedger Channel', platform: 'telegram', risk: 'medium', members: 6233, country: '新加坡' },
  { id: 5, name: 'RiverFox Mirror', platform: 'social', risk: 'low', members: 932, country: '中国' }
]);

const filteredWarnings = computed(() => {
  return warnings.value.filter(w => {
    const matchStatus = warningStatusFilter.value === 'all' || w.status === warningStatusFilter.value;
    const matchType = selectedType.value === 'all' || w.type === selectedType.value;
    const sub = subscriptions.find(s => s.name === selectedSubscription.value);
    const matchCountry = !sub || !sub.country || w.country === sub.country;
    const matchSubType = !sub || sub.type === 'all' || w.type === sub.type;
    return matchStatus && matchType && matchCountry && matchSubType;
  });
});

const filteredPersons = computed(() => {
  return hotPersons.value.filter(p => {
    const matchType = selectedType.value === 'all' || p.type === selectedType.value;
    const sub = subscriptions.find(s => s.name === selectedSubscription.value);
    const matchCountry = !sub || !sub.country || p.country === sub.country;
    const matchSubType = !sub || sub.type === 'all' || p.type === sub.type;
    return matchType && matchCountry && matchSubType;
  });
});

const filteredFeed = computed(() => {
  const sub = subscriptions.find(s => s.name === selectedSubscription.value);
  return feed.value.filter(f => {
    const matchCountry = !sub || !sub.country || f.country === sub.country;
    return matchCountry;
  });
});

const doubledFeed = computed(() => {
  const base = filteredFeed.value.map((item, idx) => ({ ...item, uid: `a-${item.id}-${idx}` }));
  const clone = filteredFeed.value.map((item, idx) => ({ ...item, uid: `b-${item.id}-${idx}` }));
  return [...base, ...clone];
});

const feedScrollDistance = computed(() => Math.max(filteredFeed.value.length * 158, 320));

const warningCount = computed(() => filteredWarnings.value.filter(w => w.status !== '已结案').length);
const handledCount = computed(() => filteredWarnings.value.filter(w => w.status === '已结案').length);
const totalCount = computed(() => {
  const scale = statsTimeFilter.value === '24h' ? 4 : statsTimeFilter.value === '7d' ? 28 : 110;
  return filteredWarnings.value.length * scale;
});

const drawerPersons = computed(() => hotPersons.value.filter(p => p.country === drawerCountry.value).slice(0, 5));
const drawerEvents = computed(() => warnings.value.filter(w => w.country === drawerCountry.value).slice(0, 8));
const drawerThreat = computed(() => {
  const all = [...drawerPersons.value.map(p => p.score), ...drawerEvents.value.map(e => (e.level === 'high' ? 90 : 70))];
  return all.length ? Math.max(...all) : 'N/A';
});
const drawerCount = computed(() => drawerEvents.value.length * 120 + drawerPersons.value.length * 40);

const filteredOrgRows = computed(() => {
  return orgRows.value.filter(r => {
    const platformMatch = orgTab.value === 'social' ? r.platform === 'social' : r.platform === orgTab.value;
    const riskMatch = orgRiskFilter.value === 'all' || r.risk === orgRiskFilter.value;
    const countryMatch = !orgCountry.value || r.country === orgCountry.value;
    return platformMatch && riskMatch && countryMatch;
  });
});

const personsTableRows = computed(() => {
  if (personsModalCountry.value === 'all') return hotPersons.value;
  return hotPersons.value.filter(p => p.country === personsModalCountry.value);
});

const countryEventRows = computed(() => {
  return warnings.value.filter(w => w.country === mapContextCountry.value);
});

const statusClass = (status) => {
  if (status === '待处理') return 'status-todo';
  if (status === '正在研判') return 'status-doing';
  return 'status-done';
};

const scoreClass = (score) => {
  if (score >= 90) return 'p-score-critical';
  if (score >= 75) return 'p-score-high';
  if (score >= 50) return 'p-score-medium';
  return 'p-score-low';
};

const levelText = (level) => {
  if (level === 'critical') return '高危';
  if (level === 'high') return '关注';
  if (level === 'medium') return '追踪';
  return '低危';
};

const showToast = (msg) => {
  toastMessage.value = msg;
  toastVisible.value = true;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastVisible.value = false;
  }, 1800);
};

const applySubscription = () => {
  const current = subscriptions.find(s => s.name === selectedSubscription.value);
  if (!current) return;
  selectedType.value = current.type;
  if (current.country === '中国') mapMode.value = 'china';
  showToast(`已切换至专属战位视图：【${current.name}】`);
  updateTrendChart();
  updateMapChart();
};

const showWarningDetail = (item) => {
  detailMode.value = 'generic';
  currentPerson.value = null;
  detailTitle.value = '案件追踪档案 (InvestigationCase)';
  detailHtml.value = `
    <h3 style="color:#fff;margin-bottom:10px;">${escapeHTML(item.name)}</h3>
    <p style="margin-bottom:8px;"><b>发生时间:</b> ${escapeHTML(item.time)}</p>
    <p style="margin-bottom:8px;"><b>地区:</b> ${escapeHTML(item.country)}</p>
    <p style="margin-bottom:8px;"><b>状态:</b> ${escapeHTML(item.status)}</p>
    <p><b>研判摘要:</b> ${escapeHTML(item.detail || '暂无')}</p>
  `;
  detailVisible.value = true;
};

const showPersonDetail = (person) => {
  detailMode.value = 'person';
  currentPerson.value = person;
  detailTitle.value = '重点人物战术画像 (SubjectProfile)';
  detailVisible.value = true;
  nextTick(() => initPersonDetailCharts(person));
};

const showFeedDetail = (cluster) => {
  detailMode.value = 'generic';
  currentPerson.value = null;
  detailTitle.value = '事件簇详情 (CorrelationCluster)';
  detailHtml.value = `
    <h3 style="color:#fff;margin-bottom:10px;">${escapeHTML(cluster.title)}</h3>
    <p style="margin-bottom:8px;"><b>来源:</b> ${escapeHTML(cluster.source)}</p>
    <p style="margin-bottom:8px;"><b>时间:</b> ${escapeHTML(cluster.time)}</p>
    <p style="margin-bottom:8px;"><b>归并量:</b> ${escapeHTML(String(cluster.clusterCount))}</p>
    <p style="margin-bottom:8px;"><b>等级:</b> ${escapeHTML(levelText(cluster.level))}</p>
    <p><b>摘要:</b> ${escapeHTML(cluster.text)}</p>
  `;
  detailVisible.value = true;
};

const openOrgList = (country) => {
  orgCountry.value = country || '中国';
  orgModalVisible.value = true;
};

const showCountryEventsList = (country) => {
  mapContextCountry.value = country || '中国';
  countryEventsTitle.value = `${mapContextCountry.value} 国家事件列表`;
  countryEventsModalVisible.value = true;
  mapContextVisible.value = false;
  circleMenuVisible.value = false;
};

const showPersonList = (country) => {
  personsModalCountry.value = country || 'all';
  personsModalVisible.value = true;
  mapContextVisible.value = false;
  circleMenuVisible.value = false;
};

const showCountryDrawerFromMenu = () => {
  drawerCountry.value = mapContextCountry.value;
  drawerVisible.value = true;
  mapContextVisible.value = false;
  circleMenuVisible.value = false;
};

const openCircleMenuAtContext = () => {
  circleMenuX.value = mapContextX.value + 10;
  circleMenuY.value = mapContextY.value + 10;
  circleMenuVisible.value = true;
  mapContextVisible.value = false;
};

const hideFloatingMenus = () => {
  mapContextVisible.value = false;
  circleMenuVisible.value = false;
};

const detectPlatformType = (platform) => {
  const p = String(platform || '').toLowerCase();
  if (p.includes('telegram') || p.includes('tg')) return 'telegram';
  if (p === 'x' || p.includes('twitter')) return 'x';
  return 'facebook';
};

const showPlatformDetail = (person) => {
  nativePlatformType.value = detectPlatformType(person.platform);
  activePlatformName.value = person.alias;
  activePlatformText.value = person.desc;
  activePlatformAvatar.value = person.avatar;
  nativePlatformVisible.value = true;
};

const openCloneWorkspace = (person) => {
  cloneTarget.value = person;
  cloneChannel.value = detectPlatformType(person.platform);
  cloneWorkspaceVisible.value = true;
  cloneStats.value = { replies: 0, hitRate: Math.max(80, Math.min(99, Math.round(person.score * 0.92))) };
  cloneMessages.value = [
    {
      id: 1,
      side: 'left',
      thought: '',
      text: `我是${person.alias}，最近有个新项目可以聊。`,
      time: '10:21'
    }
  ];
  cloneDraft.value = `你好，我看到你最近在${person.platform}很活跃，想和你交流下资源。`;
};

const sendAgentMessage = () => {
  const text = cloneDraft.value.trim();
  if (!text) return;

  const t = new Date();
  const hm = `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}`;
  cloneMessages.value.push({
    id: Date.now(),
    side: 'right',
    thought: hitlEnabled.value ? 'HITL审核已启用，话术通过风控后发送。' : '',
    text,
    time: hm
  });
  cloneDraft.value = '';

  const replyPool = [
    '可以，先说你的合作模式。',
    '我这边只接受熟人介绍，你是谁带的？',
    '先发下你手里的量和周期。',
    '这个方向可以聊，但需要看你历史记录。'
  ];
  const reply = replyPool[Math.floor(Math.random() * replyPool.length)];

  setTimeout(() => {
    const tt = new Date();
    const rhm = `${String(tt.getHours()).padStart(2, '0')}:${String(tt.getMinutes()).padStart(2, '0')}`;
    cloneMessages.value.push({
      id: Date.now() + 1,
      side: 'left',
      thought: '',
      text: reply,
      time: rhm
    });
    cloneStats.value.replies += 1;
  }, 700);
};

const escapeHTML = (str = '') => {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

const disposePersonCharts = () => {
  while (personChartInstances.length) {
    const chart = personChartInstances.pop();
    chart?.dispose();
  }
};

const closeDetailModal = () => {
  detailVisible.value = false;
  disposePersonCharts();
};

const initPersonDetailCharts = (person) => {
  disposePersonCharts();
  const radarEl = document.getElementById(`personRadar-${person.id}`);
  const heatEl = document.getElementById(`personHeat-${person.id}`);
  const graphEl = document.getElementById(`personGraph-${person.id}`);
  if (!radarEl || !heatEl || !graphEl) return;

  const radar = echarts.init(radarEl);
  radar.setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator: [
        { name: '影响力', max: 100 },
        { name: '活跃度', max: 100 },
        { name: '隐蔽性', max: 100 },
        { name: '关联度', max: 100 },
        { name: '破坏性', max: 100 }
      ],
      axisName: { color: '#9fb6da' },
      splitLine: { lineStyle: { color: 'rgba(105,144,201,0.22)' } },
      splitArea: { areaStyle: { color: ['rgba(22,44,78,0.22)', 'rgba(13,30,56,0.08)'] } }
    },
    series: [{
      type: 'radar',
      data: [{ value: [person.score, 82, 76, 88, 91], areaStyle: { color: 'rgba(37,99,235,0.28)' }, lineStyle: { color: '#3b82f6' }, itemStyle: { color: '#60a5fa' } }]
    }]
  });

  const heat = echarts.init(heatEl);
  const heatData = [];
  for (let d = 0; d < 7; d += 1) {
    for (let h = 0; h < 24; h += 1) {
      heatData.push([h, d, Math.round(20 + Math.abs(Math.sin((h + d) / 4) * 60))]);
    }
  }
  heat.setOption({
    grid: { left: 36, right: 12, top: 20, bottom: 28 },
    xAxis: { type: 'category', data: Array.from({ length: 24 }, (_, i) => `${i}`), axisLabel: { color: '#8fa7cc', fontSize: 10 }, axisLine: { lineStyle: { color: '#2d4f7f' } } },
    yAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'], axisLabel: { color: '#8fa7cc', fontSize: 10 }, axisLine: { lineStyle: { color: '#2d4f7f' } } },
    visualMap: { min: 0, max: 100, show: false, inRange: { color: ['#0b1b3c', '#1d4ed8', '#22d3ee'] } },
    series: [{ type: 'heatmap', data: heatData }]
  });

  const graph = echarts.init(graphEl);
  graph.setOption({
    backgroundColor: 'transparent',
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      force: { repulsion: 180, edgeLength: [50, 110] },
      label: { show: true, color: '#d9e6ff', fontSize: 10 },
      lineStyle: { color: 'rgba(96,165,250,0.45)' },
      data: [
        { name: person.alias, symbolSize: 46, itemStyle: { color: '#f97316' } },
        { name: '钱包簇', symbolSize: 30, itemStyle: { color: '#3b82f6' } },
        { name: '中继节点', symbolSize: 26, itemStyle: { color: '#06b6d4' } },
        { name: '通信账号', symbolSize: 28, itemStyle: { color: '#10b981' } },
        { name: '关联案件', symbolSize: 32, itemStyle: { color: '#ef4444' } }
      ],
      links: [
        { source: person.alias, target: '钱包簇' },
        { source: person.alias, target: '中继节点' },
        { source: person.alias, target: '通信账号' },
        { source: person.alias, target: '关联案件' },
        { source: '通信账号', target: '中继节点' }
      ]
    }]
  });

  personChartInstances.push(radar, heat, graph);
};

const loadScript = (src) => {
  return new Promise((resolve, reject) => {
    const exists = Array.from(document.querySelectorAll('script')).some(s => s.src === src);
    if (exists) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(script);
  });
};

const updateNowTime = () => {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  const ss = String(now.getSeconds()).padStart(2, '0');
  nowTime.value = `${y}-${m}-${d} ${hh}:${mm}:${ss}`;
  nowTimeDisplay.value = `${y}年${m}月${d}日 ${hh}:${mm}:${ss}`;
};

const goTo = (path) => {
  router.push(path);
};

const logoutToLogin = () => {
  logout();
  router.replace('/login');
};

const avatarInitial = (name = '') => {
  const s = String(name).trim();
  if (!s) return 'NA';
  if (s.length === 1) return s.toUpperCase();
  return s.slice(0, 2).toUpperCase();
};

const buildTrendOption = () => {
  const points = Number(trendRangeFilter.value);
  const x = Array.from({ length: points }, (_, i) => `${i}:00`);
  const base = trendTypeFilter.value === 'all' ? 18 : trendTypeFilter.value === 'black' ? 22 : trendTypeFilter.value === 'fraud' ? 16 : 20;
  const data = x.map((_, i) => Math.max(3, Math.round(base + Math.sin(i / 2.7) * 6 + (i % 3) * 1.5)));

  return {
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: x,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#8c9db5', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#8c9db5', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.14)' } }
    },
    series: [
      {
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data,
        lineStyle: { width: 3, color: '#3b82f6' },
        itemStyle: { color: '#60a5fa' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59,130,246,0.35)' },
            { offset: 1, color: 'rgba(59,130,246,0.02)' }
          ])
        }
      }
    ]
  };
};

const buildMapOption = () => {
  const name = mapMode.value === 'china' ? 'china' : 'world';
  const sceneColorMap = {
    global: '#8b5cf6',
    black: '#22d3ee',
    leak: '#3b82f6',
    terror: '#ef4444',
    smuggle: '#f59e0b',
    drug: '#10b981'
  };
  const lineColor = sceneColorMap[mapScene.value] || '#8b5cf6';
  const points = filteredWarnings.value
    .map(w => ({
      name: w.country,
      value: countryCoordinates[w.country] ? [...countryCoordinates[w.country], w.level === 'high' ? 90 : 65] : null,
      level: w.level
    }))
    .filter(p => p.value);

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (Array.isArray(params.value)) {
          return `${params.name}<br/>风险值: ${params.value[2]}`;
        }
        return `${params.name}`;
      }
    },
    geo: {
      map: name,
      roam: true,
      zoom: mapMode.value === 'china' ? 1.2 : 1,
      label: { show: false, color: '#94a3b8' },
      itemStyle: {
        areaColor: '#10213f',
        borderColor: '#2d4d80'
      },
      emphasis: {
        label: { show: false },
        itemStyle: { areaColor: '#1d4b86' }
      }
    },
    series: [
      {
        type: 'lines',
        coordinateSystem: 'geo',
        zlevel: 2,
        effect: {
          show: true,
          period: 4,
          trailLength: 0.2,
          symbol: 'arrow',
          symbolSize: 6
        },
        lineStyle: {
          width: 1.4,
          opacity: 0.7,
          curveness: 0.3,
          color: lineColor
        },
        data: [
          { coords: [[-95.7129, 37.0902], [116.4074, 39.9042]] },
          { coords: [[139.6917, 35.6895], [116.4074, 39.9042]] },
          { coords: [[103.8198, 1.3521], [116.4074, 39.9042]] },
          { coords: [[-46.6333, -23.5505], [-95.7129, 37.0902]] }
        ]
      },
      {
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: points,
        symbolSize: (val) => Math.max(8, Math.round(val[2] / 10)),
        rippleEffect: { brushType: 'stroke' },
        itemStyle: { color: lineColor }
      }
    ]
  };
};

const updateTrendChart = () => {
  if (!trendChart.value) return;
  trendChart.value.setOption(buildTrendOption(), true);
};

const updateMapChart = () => {
  if (!mapChart.value) return;
  try {
    mapChart.value.setOption(buildMapOption(), true);
    mapFallback.value = false;
  } catch {
    mapFallback.value = true;
  }
};

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart.value = echarts.init(trendChartRef.value);
    updateTrendChart();
  }
  if (mapChartRef.value) {
    mapChart.value = echarts.init(mapChartRef.value);
    updateMapChart();
    mapChart.value.on('click', (params) => {
      if (!params || !params.name) return;
      drawerCountry.value = params.name;
      mapContextCountry.value = params.name;
      drawerVisible.value = true;
    });

    mapChartRef.value.addEventListener('contextmenu', (event) => {
      event.preventDefault();
      const sub = subscriptions.find(s => s.name === selectedSubscription.value);
      mapContextCountry.value = drawerCountry.value !== '全球' ? drawerCountry.value : (sub?.country || '中国');
      mapContextX.value = event.clientX;
      mapContextY.value = event.clientY;
      mapContextVisible.value = true;
      circleMenuVisible.value = false;
    });
  }
};

const handleResize = () => {
  trendChart.value?.resize();
  mapChart.value?.resize();
};

watch([trendTypeFilter, trendRangeFilter, selectedType, selectedSubscription], () => {
  updateTrendChart();
});

watch([mapMode, selectedType, selectedSubscription], () => {
  updateMapChart();
});

watch(mapScene, () => {
  updateMapChart();
});

onMounted(async () => {
  updateNowTime();
  timeTimer = setInterval(updateNowTime, 1000);

  // Load map definitions, but do not block page initialization if network is unavailable.
  try {
    await loadScript('https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/js/world.js');
    await loadScript('https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/js/china.js');
  } catch {
    mapFallback.value = true;
    showToast('地图底图资源加载失败，已降级显示。');
  }

  await nextTick();
  initCharts();
  window.addEventListener('resize', handleResize);
  document.addEventListener('click', hideFloatingMenus);
});

onBeforeUnmount(() => {
  clearInterval(timeTimer);
  clearTimeout(toastTimer);
  window.removeEventListener('resize', handleResize);
  document.removeEventListener('click', hideFloatingMenus);
  trendChart.value?.dispose();
  mapChart.value?.dispose();
  disposePersonCharts();
});
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: var(--bg-dark);
  background-image: radial-gradient(circle at center, #071746 0%, var(--bg-dark) 100%);
  color: var(--text-main);
}

.top-header {
  height: 70px;
  background: rgba(18, 26, 45, 0.95);
  border-bottom: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.12);
  position: relative;
  z-index: 100;
  flex-shrink: 0;
}

.logo-area {
  font-size: 24px;
  font-weight: bold;
  color: var(--accent-blue);
  margin-right: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-menu {
  display: flex;
  gap: 5px;
  flex: 1;
}

.nav-item {
  padding: 8px 20px;
  color: var(--text-dim);
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  font-size: 14px;
}

.nav-item.active,
.nav-item:hover {
  color: var(--accent-blue);
  background: linear-gradient(180deg, rgba(59, 130, 246, 0) 0%, rgba(59, 130, 246, 0.08) 100%);
  border-bottom: 2px solid var(--accent-blue);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 12px;
  color: var(--text-dim);
}

.time-display {
  font-family: 'Courier New', Courier, monospace;
  color: var(--accent-blue);
  font-weight: 500;
}

.view-selector-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.3);
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid rgba(59, 130, 246, 0.4);
  box-shadow: inset 0 0 10px rgba(59, 130, 246, 0.1);
}

.btn-logout {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: var(--bg-hover);
  color: var(--accent-blue);
}

.sys-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(16, 185, 129, 0.9);
  color: #fff;
  padding: 10px 24px;
  border-radius: 6px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
  z-index: 9999;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s, transform 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
}

.sys-toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(10px);
}

.main-container {
  flex: 1;
  padding: 15px;
  display: grid;
  grid-template-columns: 28fr 44fr 28fr;
  grid-template-rows: 3.5fr 55px 5.5fr 60px;
  gap: 15px;
  height: calc(100vh - 70px);
  min-height: 720px;
  max-height: 900px;
  margin: 0 auto;
  width: 100%;
}

.panel {
  background: rgba(18, 26, 45, 0.7);
  border: 1px solid var(--border-color);
  position: relative;
  padding: 40px 15px 15px 15px;
  display: flex;
  flex-direction: column;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
  min-height: 0;
  overflow: hidden;
}

.panel:hover {
  border-color: var(--border-highlight);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.1);
}

.panel-title {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 40px;
  background: linear-gradient(90deg, rgba(14, 43, 88, 0.8) 0%, rgba(6, 21, 55, 0) 100%);
  display: flex;
  align-items: center;
  padding-left: 15px;
  color: var(--accent-blue);
  font-size: 14px;
  font-weight: bold;
  border-bottom: 1px solid var(--border-color);
  border-radius: 4px 4px 0 0;
  z-index: 5;
}

.title-text {
  display: inline-flex;
  align-items: center;
}

.title-text::after {
  content: '';
  display: inline-block;
  width: 4px;
  height: 14px;
  background: var(--accent-blue);
  margin-left: 8px;
  border-radius: 2px;
}

.controls {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  position: absolute;
  top: 45px;
  left: 15px;
  z-index: 10;
}

select {
  background: rgba(10, 39, 87, 0.8);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 4px 8px;
  font-size: 12px;
  outline: none;
  cursor: pointer;
  min-width: 100px;
  border-radius: 4px;
}

.warning-container {
  width: 100%;
  margin-top: 30px;
  height: calc(100% - 60px);
  overflow-y: auto;
  position: relative;
  padding-right: 5px;
}

.case-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 10px;
}

.case-card {
  background: linear-gradient(90deg, rgba(16, 29, 52, 0.8) 0%, rgba(11, 20, 37, 0.4) 100%);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 4px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border-left: 3px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.case-card:hover {
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateX(4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.case-card.level-high {
  border-left-color: var(--accent-red);
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.08) 0%, rgba(11, 20, 37, 0.4) 100%);
}

.case-card.level-medium {
  border-left-color: var(--accent-orange);
  background: linear-gradient(90deg, rgba(249, 115, 22, 0.08) 0%, rgba(11, 20, 37, 0.4) 100%);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.case-title {
  font-weight: 600;
  color: #f8fafc;
  font-size: 13px;
  display: flex;
  align-items: center;
  line-height: 1.4;
}

.case-id {
  font-family: 'Consolas', monospace;
  color: #64748b;
  font-size: 10px;
  letter-spacing: 0.5px;
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.case-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.case-meta-info {
  display: flex;
  gap: 12px;
  color: var(--text-dim);
}

.case-meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.case-status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.status-doing {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-todo {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.status-done {
  color: #10b981;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background-color: #ef4444;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  animation: pulse-red 1.5s infinite;
  margin-right: 8px;
  flex-shrink: 0;
}

@keyframes pulse-red {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
  70% { box-shadow: 0 0 0 5px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.center-stats {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 100%;
  padding-top: 20px;
}

.circle-stat {
  width: 100px;
  height: 100px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-shadow: 0 0 15px rgba(0, 116, 255, 0.2) inset;
  position: relative;
  background: rgba(18, 26, 45, 0.5);
}

.circle-stat::before {
  content: '';
  position: absolute;
  width: 110px;
  height: 110px;
  border: 1px dashed var(--accent-blue);
  border-radius: 50%;
  animation: rotate 10s linear infinite;
}

.stat-num {
  font-size: 24px;
  color: #ffaa00;
  font-weight: bold;
}

.stat-label {
  font-size: 12px;
  color: var(--accent-blue);
  margin-top: 5px;
}

.main-stat {
  text-align: center;
  padding: 16px 24px;
  background: linear-gradient(180deg, rgba(11, 28, 54, 0.88) 0%, rgba(8, 20, 40, 0.92) 100%);
  border: 1px solid rgba(58, 109, 178, 0.7);
  border-radius: 4px;
  box-shadow: inset 0 0 22px rgba(18, 70, 143, 0.2), 0 0 18px rgba(22, 106, 202, 0.15);
}

.main-title {
  font-size: 14px;
  color: #9fc3ff;
  letter-spacing: 2px;
  margin-bottom: 6px;
}

.main-num {
  font-size: 56px;
  color: #ffcc00;
  font-weight: bold;
  font-family: 'Impact', sans-serif;
  letter-spacing: 3px;
  text-shadow: 0 0 12px rgba(255, 204, 0, 0.35);
  line-height: 1;
}

.main-time {
  color: #7ba0d6;
  font-size: 12px;
  margin-top: 8px;
}

.hot-list {
  overflow-y: auto;
  margin-top: 30px;
  height: calc(100% - 30px);
  padding-right: 5px;
}

.target-card {
  display: flex;
  align-items: flex-start;
  background: linear-gradient(180deg, rgba(13, 25, 47, 0.95) 0%, rgba(9, 18, 37, 0.95) 100%);
  border: 1px solid rgba(51, 99, 163, 0.65);
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.target-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background: var(--accent-blue);
  opacity: 0.5;
}

.target-card.level-critical::before {
  background: #ef4444;
  opacity: 0.8;
}

.target-card:hover {
  background: linear-gradient(180deg, rgba(18, 34, 62, 0.98) 0%, rgba(11, 24, 47, 0.98) 100%);
  border-color: rgba(80, 148, 232, 0.75);
  transform: translateX(3px);
}

.target-avatar-wrapper {
  position: relative;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  margin-right: 10px;
  border-radius: 2px;
  border: 1px solid #35527d;
  overflow: hidden;
  background: #0a0f18;
}

.avatar-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f4f6ff;
  font-weight: 800;
  font-size: 16px;
  background: radial-gradient(circle at 30% 20%, #1b3159 0%, #0b1220 68%);
}

.avatar-mini {
  font-size: 10px;
}

.target-status {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 1px solid #0f172a;
  background: var(--accent-green);
}

.target-status.danger {
  background: var(--accent-red);
}

.target-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.target-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.target-alias {
  font-size: 12px;
  font-weight: bold;
  color: #d8e7ff;
  display: flex;
  align-items: center;
  gap: 6px;
}

.target-city {
  font-size: 11px;
  color: #8fb0dc;
  display: flex;
  align-items: center;
  gap: 4px;
}

.target-loc {
  font-size: 11px;
  color: #7ea0cf;
  line-height: 1.4;
}

.target-desc {
  font-size: 11px;
  color: #9ab3d8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.target-tags {
  display: flex;
  gap: 5px;
  margin-top: 2px;
}

.target-actions {
  display: none;
}

.target-tag {
  font-size: 9px;
  padding: 2px 6px;
  background: rgba(42, 85, 152, 0.26);
  color: #9ac3ff;
  border: 1px solid rgba(84, 143, 219, 0.35);
  border-radius: 2px;
}

.target-threat-box {
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.p-score-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-radius: 2px;
  font-size: 11px;
  font-weight: 800;
  font-family: 'Impact', 'Consolas', monospace;
  letter-spacing: 0.5px;
  line-height: 1;
}

.conf-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  border: 1px solid rgba(74, 222, 128, 0.45);
  background: rgba(22, 101, 52, 0.25);
  color: #86efac;
  border-radius: 2px;
  font-size: 10px;
  font-weight: 700;
}

.p-score-critical {
  color: #fff;
  background: linear-gradient(90deg, #dc2626, #991b1b);
  border: 1px solid #f87171;
}

.p-score-high {
  color: #fff;
  background: linear-gradient(90deg, #ea580c, #c2410c);
  border: 1px solid #fb923c;
}

.p-score-medium {
  color: #fff;
  background: linear-gradient(90deg, #2563eb, #1e40af);
  border: 1px solid #60a5fa;
}

.p-score-low {
  color: #fff;
  background: linear-gradient(90deg, #475569, #334155);
  border: 1px solid #94a3b8;
}

.ticker-panel {
  padding: 0;
  display: flex;
  align-items: center;
  background: rgba(10, 15, 26, 0.9);
  border: 1px solid var(--accent-blue);
  border-radius: 6px;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.15) inset;
  overflow: hidden;
  min-height: 50px;
}

.ticker-left {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  color: var(--accent-blue);
  white-space: nowrap;
}

.view-select {
  border: none;
  background: transparent;
  color: #60a5fa;
  font-weight: bold;
  font-size: 13px;
  min-width: 210px;
}

.monitored-entities-wrapper {
  position: relative;
  flex: 1;
  overflow: hidden;
  z-index: 10;
  height: 35px;
  display: flex;
  align-items: center;
  mask-image: linear-gradient(to right, transparent, black 3%, black 97%, transparent);
}

.monitored-entities-track {
  display: flex;
  width: max-content;
  animation: marqueeHorizontal 30s linear infinite;
}

.marquee-group {
  display: flex;
  gap: 15px;
  padding-right: 15px;
}

@keyframes marqueeHorizontal {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.monitored-entity {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid var(--border-color);
  padding: 4px 12px 4px 4px;
  border-radius: 20px;
  white-space: nowrap;
}

.entity-avatar {
  position: relative;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #1e293b;
}

.entity-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.entity-platform {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8px;
  color: #fff;
  border: 2px solid rgba(15, 23, 42, 0.9);
}

.plat-tg { background: #38bdf8; }
.plat-x { background: #0f1419; }
.plat-fb { background: #1877f2; }
.plat-tor { background: #8b5cf6; }

.entity-info {
  display: flex;
  flex-direction: column;
}

.entity-name {
  font-size: 11px;
  font-weight: bold;
  color: #e2e8f0;
  line-height: 1.1;
}

.entity-stat {
  font-size: 9px;
  color: var(--text-dim);
  margin-top: 2px;
}

.entity-stat.critical { color: var(--accent-red); }
.entity-stat.warning { color: var(--accent-orange); }

#mapChart {
  width: 100%;
  height: 100%;
  flex: 1;
  min-height: 0;
  margin-top: 25px;
}

.map-fallback {
  position: relative;
  margin-top: 25px;
  width: 100%;
  height: calc(100% - 25px);
  border: 1px solid rgba(55, 108, 179, 0.45);
  border-radius: 6px;
  background:
    radial-gradient(circle at 70% 30%, rgba(37, 99, 235, 0.18) 0%, transparent 42%),
    radial-gradient(circle at 25% 60%, rgba(14, 165, 233, 0.15) 0%, transparent 40%),
    linear-gradient(180deg, #08152f 0%, #061025 100%);
  overflow: hidden;
}

.map-fallback-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(56, 101, 169, 0.16) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56, 101, 169, 0.16) 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: 0.35;
}

.map-fallback-line {
  position: absolute;
  height: 2px;
  background: linear-gradient(90deg, rgba(34, 211, 238, 0.2) 0%, rgba(34, 211, 238, 0.9) 60%, rgba(34, 211, 238, 0.2) 100%);
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.45);
  transform-origin: left center;
}

.line-a { left: 22%; top: 46%; width: 40%; transform: rotate(-8deg); }
.line-b { left: 56%; top: 40%; width: 18%; transform: rotate(32deg); }
.line-c { left: 36%; top: 56%; width: 32%; transform: rotate(12deg); }

.map-fallback-node {
  position: absolute;
  transform: translate(-50%, -50%);
  padding: 3px 8px;
  font-size: 11px;
  color: #d9ecff;
  border: 1px solid rgba(96, 165, 250, 0.7);
  border-radius: 12px;
  background: rgba(30, 64, 175, 0.4);
  box-shadow: 0 0 10px rgba(96, 165, 250, 0.3);
}

.node-cn { left: 58%; top: 46%; }
.node-us { left: 24%; top: 45%; }
.node-jp { left: 74%; top: 40%; }
.node-sg { left: 65%; top: 60%; }

.map-fallback-tip {
  position: absolute;
  right: 10px;
  bottom: 10px;
  font-size: 11px;
  color: #93c5fd;
  padding: 3px 8px;
  border: 1px solid rgba(59, 130, 246, 0.45);
  background: rgba(15, 23, 42, 0.65);
  border-radius: 3px;
}

#trendChart {
  width: 100%;
  height: 100%;
  margin-top: 20px;
  flex: 1;
  min-height: 0;
}

.pill-tabs-container {
  display: inline-flex;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 3px;
}

.pill-tab {
  padding: 4px 14px;
  font-size: 12px;
  color: #94a3b8;
  border-radius: 16px;
  cursor: pointer;
}

.pill-tab.active {
  background: var(--accent-blue);
  color: #ffffff;
  font-weight: 600;
}

.view-all-btn {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid var(--accent-blue);
  color: var(--accent-blue);
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
}

.map-controls {
  display: flex;
  gap: 10px;
  align-items: center;
  position: absolute;
  top: 45px;
  left: 15px;
  z-index: 100;
}

#sourceChart {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-top: 35px;
  min-height: 0;
  overflow: hidden;
}

.live-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid rgba(59, 130, 246, 0.35);
  background: rgba(59, 130, 246, 0.10);
  color: var(--accent-blue);
  font-size: 11px;
}

.live-pill-danger {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.35);
  color: #f87171;
}

.live-feed-shell {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.live-feed-timeline {
  position: relative;
  flex: 1;
  min-height: 0;
  border: 1px solid rgba(59, 130, 246, 0.16);
  background: linear-gradient(180deg, rgba(4, 12, 24, 0.95) 0%, rgba(9, 21, 39, 0.92) 100%);
  border-radius: 10px;
  overflow: hidden;
}

.live-feed-scroll {
  position: relative;
  height: 100%;
  overflow: hidden;
  padding: 14px 10px;
}

.live-feed-track {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  padding: 12px;
  animation: liveFeedMarquee 40s linear infinite;
  will-change: transform;
}

.live-feed-scroll:hover .live-feed-track {
  animation-play-state: paused;
}

@keyframes liveFeedMarquee {
  from { transform: translateY(0); }
  to { transform: translateY(calc(-1 * var(--scroll-distance))); }
}

.live-feed-item {
  position: relative;
  margin-left: 2px;
  margin-bottom: 14px;
  padding: 14px;
  border-radius: 10px;
  border: 1px solid rgba(59, 130, 246, 0.14);
  background: linear-gradient(180deg, rgba(11, 20, 37, 0.92) 0%, rgba(16, 29, 52, 0.72) 100%);
  cursor: pointer;
}

.live-feed-item:hover {
  transform: translateX(4px);
}

.live-feed-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.live-source-group {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 13px;
}

.cluster-count-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #10b981;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
}

.live-severity-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 10px;
  font-weight: 600;
}

.live-severity-badge.critical {
  color: #fecaca;
  background: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.30);
}

.live-severity-badge.high {
  color: #fed7aa;
  background: rgba(249, 115, 22, 0.14);
  border: 1px solid rgba(249, 115, 22, 0.30);
}

.live-severity-badge.medium {
  color: #fde68a;
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.30);
}

.live-meta {
  margin-left: auto;
  color: var(--text-dim);
  font-size: 10px;
}

.live-feed-title {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 6px;
}

.live-feed-text {
  color: #cbd5e1;
  font-size: 12px;
  line-height: 1.6;
}

.footer {
  grid-column: 1 / 4;
  background: rgba(10, 15, 26, 0.9);
  border-top: 1px solid var(--border-color);
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-dim);
  height: 60px;
  border-radius: 4px;
}

.footer-copyright {
  text-align: center;
  flex: 1;
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-link {
  color: var(--text-dim);
  text-decoration: none;
}

.footer-link:hover {
  color: var(--accent-blue);
}

.events-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  color: var(--text-main);
}

.events-table th {
  background: rgba(10, 15, 26, 0.8);
  padding: 12px 10px;
  text-align: left;
  color: var(--text-dim);
  border-bottom: 2px solid var(--border-color);
}

.events-table td {
  padding: 12px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.events-table tr:hover td {
  background: rgba(59, 130, 246, 0.05);
}

.btn-action {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: rgba(59, 130, 246, 0.1);
  color: var(--accent-blue);
  cursor: pointer;
  font-size: 11px;
  margin: 0 3px;
  transition: all 0.2s;
}

.btn-action:hover {
  background: var(--accent-blue);
  color: #fff;
  border-color: var(--accent-blue);
}

.btn-export {
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-green);
  border-color: rgba(16, 185, 129, 0.3);
}

.btn-export:hover {
  background: var(--accent-green);
  color: #fff;
  border-color: var(--accent-green);
}

.map-context-menu {
  position: fixed;
  background: rgba(18, 26, 45, 0.95);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 1300;
  min-width: 200px;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.map-context-header {
  padding: 12px 15px;
  background: linear-gradient(90deg, rgba(14, 43, 88, 0.9) 0%, rgba(6, 21, 55, 0.7) 100%);
  border-bottom: 1px solid var(--border-color);
  color: var(--accent-blue);
  font-weight: bold;
  font-size: 14px;
}

.map-context-body {
  padding: 15px;
}

.circle-menu {
  position: fixed;
  width: 180px;
  height: 180px;
  background: rgba(18, 26, 45, 0.95);
  border-radius: 50%;
  border: 2px solid var(--accent-blue);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1301;
  backdrop-filter: blur(10px);
}

.circle-menu-center {
  width: 60px;
  height: 60px;
  background: var(--accent-blue);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: bold;
  font-size: 12px;
  cursor: pointer;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.circle-menu-item {
  position: absolute;
  width: 50px;
  height: 50px;
  background: var(--bg-panel);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-main);
  cursor: pointer;
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.circle-menu-item:hover {
  background: var(--accent-blue);
  color: #fff;
  transform: scale(1.08);
}

.org-tabs {
  display: flex;
  gap: 20px;
  padding: 15px 20px;
  border-bottom: 1px solid #1e293b;
  font-size: 13px;
}

.org-tab-item {
  color: #94a3b8;
  cursor: pointer;
  padding-bottom: 15px;
  margin-bottom: -16px;
  border-bottom: 2px solid transparent;
}

.org-tab-item:hover {
  color: #fff;
}

.org-tab-item.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
  font-weight: bold;
}

.org-filter-bar {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  background: #0f1729;
  align-items: center;
}

.org-select {
  background: #1e293b;
  border: 1px solid #334155;
  color: #e2e8f0;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
}

.org-list-container {
  padding: 0 20px 20px 20px;
  height: 500px;
  overflow-y: auto;
}

.workspace-layout {
  display: flex;
  height: calc(90vh - 60px);
  width: 100%;
  background: #0f1729;
}

.ws-sidebar {
  width: 320px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.2);
}

.ws-chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.ws-section-title {
  font-size: 12px;
  font-weight: bold;
  color: var(--accent-blue);
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(59, 130, 246, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ws-config-box {
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.ws-label {
  font-size: 11px;
  color: var(--text-dim);
  margin-bottom: 8px;
  display: block;
}

.ws-select,
.ws-input {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  color: #fff;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 10px;
}

.agent-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.agent-stat-card {
  background: rgba(16, 185, 129, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  padding: 10px;
  border-radius: 4px;
  text-align: center;
}

.agent-stat-val {
  font-size: 16px;
  font-weight: bold;
  color: #10b981;
  font-family: 'Consolas', monospace;
}

.chat-header {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
}

.chat-target-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-target-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #ef4444;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: #0b1020;
}

.msg-bubble-wrapper {
  display: flex;
  max-width: 80%;
}

.msg-bubble-wrapper.left {
  align-self: flex-start;
}

.msg-bubble-wrapper.right {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin: 0 10px;
  flex-shrink: 0;
}

.msg-bubble {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  position: relative;
}

.left .msg-bubble {
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top-left-radius: 0;
  color: #e2e8f0;
}

.right .msg-bubble {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-top-right-radius: 0;
  color: #fff;
}

.msg-meta {
  font-size: 10px;
  color: #64748b;
  margin-top: 5px;
  display: flex;
  gap: 10px;
}

.llm-thought {
  font-size: 11px;
  color: #a855f7;
  background: rgba(168, 85, 247, 0.05);
  border-left: 2px solid #a855f7;
  padding: 6px 10px;
  margin-bottom: 6px;
  border-radius: 2px;
  font-family: 'Consolas', monospace;
}

.chat-input-area {
  border-top: 1px solid var(--border-color);
  padding: 15px;
  background: rgba(15, 23, 42, 0.9);
}

.hitl-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 46px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #334155;
  transition: 0.4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: '';
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--accent-blue);
}

input:checked + .slider:before {
  transform: translateX(22px);
}

.hitl-textarea {
  width: 100%;
  background: #000;
  border: 1px solid var(--border-color);
  color: #fff;
  padding: 12px;
  border-radius: 6px;
  font-size: 13px;
  resize: none;
  height: 80px;
}

.btn-dash3 {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-dash3.primary {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
  color: #fff;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 8px #10b981;
}

.tw-app {
  background-color: #000;
  height: 100%;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  color: #e7e9ea;
}

.tw-header {
  position: sticky;
  top: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(12px);
  padding: 10px 15px;
  display: flex;
  align-items: center;
  gap: 20px;
  border-bottom: 1px solid #2f3336;
  z-index: 10;
}

.tw-header h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: #e7e9ea;
}

.tw-header-sub {
  font-size: 13px;
  color: #71767b;
}

.tw-post {
  padding: 12px 16px;
  border-bottom: 1px solid #2f3336;
  display: flex;
  gap: 12px;
}

.tw-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.tw-content { flex: 1; }

.tw-user-info {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
  font-size: 15px;
}

.tw-name { font-weight: 700; color: #e7e9ea; }
.tw-handle, .tw-time { color: #71767b; }
.tw-text { font-size: 15px; line-height: 1.4; color: #e7e9ea; }

.tg-app {
  background-color: #0e1621;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tg-header {
  background-color: #17212b;
  padding: 10px 15px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #000;
}

.tg-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  margin-right: 15px;
}

.tg-title-area { flex: 1; }
.tg-name { color: #fff; font-size: 16px; font-weight: 600; }
.tg-members { color: #7f91a4; font-size: 13px; }

.tg-chat-bg {
  flex: 1;
  overflow-y: auto;
  padding: 20px 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tg-date-pill {
  background: rgba(23, 33, 43, 0.5);
  color: #fff;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 12px;
  align-self: center;
  margin-bottom: 15px;
}

.tg-msg-bubble {
  background-color: #182533;
  border-radius: 12px;
  border-bottom-left-radius: 4px;
  padding: 8px 12px 6px 12px;
  max-width: 85%;
  color: #fff;
  font-size: 15px;
  line-height: 1.4;
}

.tg-msg-author {
  color: #64b5ef;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  display: block;
}

.tg-msg-meta {
  font-size: 11px;
  color: #6b7a8a;
  margin-top: 4px;
  text-align: right;
}

.fb-app {
  background: #18191a;
  color: #e4e6eb;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.fb-header {
  background: #242526;
  padding: 12px 16px;
  border-bottom: 1px solid #3e4042;
  font-weight: bold;
  font-size: 17px;
}

.fb-post {
  background: #242526;
  border-radius: 8px;
  margin: 16px;
  padding: 12px 16px;
}

.fb-author-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.fb-author-name { font-weight: 600; font-size: 15px; }
.fb-time { font-size: 13px; color: #b0b3b8; }
.fb-text { font-size: 15px; margin-bottom: 12px; line-height: 1.5; }

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-panel);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 15px 20px;
  background: linear-gradient(90deg, rgba(14, 43, 88, 0.9) 0%, rgba(6, 21, 55, 0.7) 100%);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  color: var(--accent-blue);
  font-size: 16px;
  font-weight: bold;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 20px;
  cursor: pointer;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.detail-content-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 20px;
  font-size: 13px;
  line-height: 1.6;
  color: #e2e8f0;
}

.person-detail-layout {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.person-detail-head {
  display: flex;
  gap: 12px;
  border: 1px solid rgba(66, 118, 184, 0.55);
  background: linear-gradient(180deg, rgba(11, 28, 54, 0.94) 0%, rgba(9, 20, 38, 0.94) 100%);
  border-radius: 4px;
  padding: 12px;
}

.person-detail-avatar {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  border: 1px solid #395f96;
  background: radial-gradient(circle at 30% 20%, #284a80 0%, #0b1220 75%);
  color: #e9f2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
}

.person-detail-main {
  flex: 1;
  min-width: 0;
}

.person-detail-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.person-detail-name {
  font-size: 22px;
  font-family: 'Impact', 'Consolas', monospace;
  color: #f8fbff;
  letter-spacing: 1px;
}

.person-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  border-radius: 2px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.6px;
}

.person-badge.high {
  color: #ffe7e7;
  background: linear-gradient(90deg, #7f1d1d, #b91c1c);
  border: 1px solid #f87171;
}

.person-detail-meta {
  margin-top: 6px;
  color: #9fc1ed;
  font-size: 12px;
}

.person-detail-desc {
  margin-top: 6px;
  color: #b4cae9;
  font-size: 12px;
  line-height: 1.55;
}

.person-asset-row {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.asset-group {
  border: 1px solid rgba(56, 104, 169, 0.5);
  background: rgba(8, 20, 40, 0.86);
  border-radius: 4px;
  padding: 10px;
  min-height: 120px;
}

.asset-title {
  color: #7fb0f0;
  font-size: 11px;
  margin-bottom: 8px;
  font-weight: 700;
}

.asset-tags {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.asset-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 6px;
  border: 1px solid rgba(78, 140, 219, 0.4);
  background: rgba(19, 43, 78, 0.45);
  color: #d6e7ff;
  border-radius: 2px;
  font-size: 11px;
}

.person-chart-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.person-chart-card {
  border: 1px solid rgba(56, 104, 169, 0.5);
  background: rgba(8, 20, 40, 0.86);
  border-radius: 4px;
  padding: 10px;
}

.person-chart-title {
  color: #9ac0f2;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 8px;
}

.person-chart {
  height: 220px;
}

.person-detail-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-dash3 {
  border: 1px solid #3b82f6;
  background: rgba(30, 64, 175, 0.2);
  color: #dbeafe;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12px;
}

.btn-dash3.primary { border-color: #2563eb; background: rgba(37, 99, 235, 0.24); }
.btn-dash3.success { border-color: #16a34a; background: rgba(22, 163, 74, 0.24); }
.btn-dash3.danger { border-color: #dc2626; background: rgba(220, 38, 38, 0.24); }

.tag-badge {
  display: inline-block;
  padding: 3px 8px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  font-size: 11px;
  margin: 2px;
}

.country-drawer {
  position: fixed;
  top: 72px;
  right: -450px;
  width: 420px;
  height: calc(100vh - 72px);
  background: rgba(18, 26, 45, 0.98);
  border-left: 2px solid var(--accent-blue);
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
  z-index: 950;
  transition: right 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
}

.country-drawer.active {
  right: 0;
}

.drawer-header {
  padding: 15px 20px;
  background: linear-gradient(90deg, rgba(14, 43, 88, 0.9) 0%, rgba(6, 21, 55, 0) 100%);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--accent-blue);
}

.drawer-close {
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 18px;
  cursor: pointer;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.drawer-stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 25px;
}

.drawer-stat-card {
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 6px;
  padding: 12px 5px;
  text-align: center;
}

.drawer-stat-val {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 5px;
}

.drawer-stat-label {
  font-size: 11px;
  color: var(--text-dim);
}

.drawer-section-title {
  font-size: 14px;
  color: #fff;
  border-left: 3px solid var(--accent-blue);
  padding-left: 10px;
  margin-bottom: 15px;
  font-weight: bold;
  margin-top: 20px;
}

.drawer-person-list,
.drawer-event-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.drawer-person-card {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 10px;
  cursor: pointer;
}

.drawer-person-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 12px;
  border: 1px solid #475569;
  overflow: hidden;
}

.drawer-person-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.drawer-person-info {
  flex: 1;
}

.drawer-person-name {
  font-weight: bold;
  color: #fff;
  font-size: 13px;
  margin-bottom: 3px;
  display: flex;
  justify-content: space-between;
}

.drawer-person-desc {
  color: var(--text-dim);
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.drawer-event-item {
  padding: 10px;
  border-left: 2px solid var(--border-color);
  background: rgba(0, 0, 0, 0.1);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.drawer-event-title {
  font-size: 12px;
  color: #e2e8f0;
  line-height: 1.4;
}

.drawer-event-meta {
  font-size: 10px;
  color: #64748b;
  display: flex;
  justify-content: space-between;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 1200px) {
  .main-container {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto auto;
    overflow-y: auto;
    display: block;
    height: auto;
    min-height: auto;
    max-height: none;
  }

  .panel {
    margin-bottom: 15px;
    height: 360px;
  }

  .footer {
    flex-direction: column;
    height: auto;
    padding: 15px;
    gap: 10px;
    text-align: center;
  }

  .person-asset-row {
    grid-template-columns: 1fr 1fr;
  }

  .person-chart-row {
    grid-template-columns: 1fr;
  }

  .person-detail-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}

@media (max-width: 760px) {
  .person-asset-row {
    grid-template-columns: 1fr;
  }

  .person-detail-head {
    flex-direction: column;
  }
}
</style>
