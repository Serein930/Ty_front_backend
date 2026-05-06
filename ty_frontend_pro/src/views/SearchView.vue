<template>
  <div class="page-container search-page">
    <AppHeader />

    <main class="main-container">
      <section v-if="!state.hasSubmitted" class="legacy-landing panel">
        <div class="legacy-search-wrapper">
          <h2 class="legacy-title">情报检索</h2>
          <p class="legacy-subtitle">请输入关键词、Hash、手机号或 Telegram ID...</p>
          <div class="legacy-search-box">
            <select v-model="state.currentView" class="control-input view-select">
              <option value="all">全域检索 (All)</option>
              <option value="intel">情报线索 (Event)</option>
              <option value="person">人物画像 (Entity)</option>
              <option value="account">账号视图 (Account)</option>
            </select>

            <input
              v-model="state.inputKeyword"
              class="control-input search-input"
              type="text"
              placeholder="请输入关键词，例如：USDT / 珠江口 / 走私"
              @keyup.enter="submitSearch('normal')"
            />

            <button class="btn btn-primary" @click="submitSearch('normal')">
              <i class="fa-solid fa-magnifying-glass"></i>
              搜索
            </button>
            <button class="btn btn-ai" @click="submitSearch('ai')">
              <i class="fa-solid fa-wand-magic-sparkles"></i>
              AI深度分析
            </button>
          </div>
        </div>
      </section>

      <template v-else>
        <section class="top-search-panel">
          <div class="search-strip">
            <select v-model="state.currentView" class="control-input view-select">
              <option value="all">全域检索</option>
              <option value="intel">情报线索 (Event)</option>
              <option value="person">人物画像 (Entity)</option>
              <option value="account">账号视图 (Account)</option>
            </select>

            <div class="search-box-wrap">
              <i class="fa-solid fa-magnifying-glass"></i>
              <input
                v-model="state.inputKeyword"
                class="control-input search-input"
                type="text"
                placeholder="输入关键词、Hash、TG ID、实体或人员别名..."
                @keyup.enter="submitSearch('normal')"
              />
            </div>

            <button class="btn btn-primary" @click="submitSearch('normal')">
              <i class="fa-solid fa-magnifying-glass"></i>
              搜索
            </button>
            <button class="btn btn-ai" @click="submitSearch('ai')">
              <i class="fa-solid fa-wand-magic-sparkles"></i>
              AI深度分析
            </button>
            <button class="btn btn-ghost" @click="resetAll">
              <i class="fa-solid fa-rotate-right"></i>
              重置
            </button>
          </div>
        </section>

        <section class="workspace" :class="{ 'ai-workspace': state.mode === 'ai' }">
        <div class="center-content panel">
          <template v-if="state.mode === 'normal'">
            <div class="group-tabs">
              <button v-for="tab in visibleGroupTabs" :key="tab.type" class="group-tab" :class="{ active: state.groupTab === tab.type }" @click="state.groupTab = tab.type">{{ tab.label }} ({{ tab.count }})</button>
            </div>

            <div class="context-bar">
              <span>当前视图：<b>{{ state.currentView }}</b></span>
              <span>关键词：<b>{{ state.submittedKeyword || '（空）' }}</b></span>
              <span>过滤时间：<b>{{ quickTimeLabel }}</b></span>
              <span>地域：<b>{{ state.region }}</b></span>
            </div>

            <div class="result-scroll custom-scrollbar">
              <template v-if="renderGroups.length">
                <section v-for="group in renderGroups" :key="group.type" class="result-group">
                  <h3 class="group-title">{{ group.label }} ({{ group.items.length }})</h3>
                  <div class="card-list">
                    <article v-for="item in group.items" :key="item.id" class="entity-card" @click="openDetail(item)">
                      <template v-if="item.viewType === 'account'">
                        <div class="account-card-head">
                          <label class="account-pick" @click.stop>
                            <input type="checkbox" :checked="basketIdSet.has(item.id)" @change="toggleBasket(item)" />
                          </label>

                          <div class="account-main">
                            <div class="account-title-row">
                              <img class="account-avatar" :src="item.avatar" alt="avatar" />
                              <div class="account-name-wrap">
                                <div class="account-name-line">
                                  <strong class="account-name">{{ getAccountDisplayName(item) }}</strong>
                                  <span class="media-pill"><i :class="getMediaIcon(item.media)"></i> {{ getPlatformLabel(item.media) }}</span>
                                  <span class="risk-badge" :class="riskClass(item.risk)">{{ getRiskText(item.risk) }}</span>
                                  <span class="topic-badge"># {{ item.topic }}</span>
                                </div>
                                <div class="account-handle">{{ getAccountHandle(item) }}</div>
                                <div class="desc account-desc" v-html="highlightKeyword(item.summary, state.submittedKeyword)"></div>
                              </div>
                            </div>

                            <div class="account-metrics">
                              <div class="metric-box">
                                <div class="metric-k">粉丝</div>
                                <div class="metric-v">{{ getAccountStat(item, 'followers') }}</div>
                              </div>
                              <div class="metric-box">
                                <div class="metric-k">关注</div>
                                <div class="metric-v">{{ getAccountStat(item, 'following') }}</div>
                              </div>
                              <div class="metric-box">
                                <div class="metric-k">发帖</div>
                                <div class="metric-v">{{ getAccountStat(item, 'posts') }}</div>
                              </div>
                              <div class="metric-box">
                                <div class="metric-k">记录时间</div>
                                <div class="metric-v">{{ item.date }}</div>
                              </div>
                            </div>

                            <div class="account-actions">
                              <button class="entity-chip account-action-btn" @click.stop="viewAssociatedPerson(item)">
                                <i class="fa-solid fa-user-check"></i>
                                查看人物
                              </button>
                              <button class="entity-chip account-action-btn" @click.stop="toggleBasket(item)">
                                <i class="fa-solid" :class="basketIdSet.has(item.id) ? 'fa-circle-check' : 'fa-circle-plus'"></i>
                                {{ basketIdSet.has(item.id) ? '移出线索篮' : '加入线索篮' }}
                              </button>
                            </div>
                          </div>

                          <div class="account-side">
                            <div class="account-side-label">归属人物</div>
                            <button class="account-side-link" @click.stop="viewAssociatedPerson(item)">
                              {{ getAssociatedPerson(item) }}
                            </button>
                          </div>
                        </div>
                      </template>

                      <template v-else-if="item.viewType === 'person'">
                        <div class="person-card-head">
                          <label class="person-pick" @click.stop>
                            <input type="checkbox" :checked="basketIdSet.has(item.id)" @change="toggleBasket(item)" />
                          </label>

                          <div class="person-main">
                            <div class="person-title-row">
                                <span class="person-icon"><i class="fa-solid fa-user-astronaut"></i></span>
                                <strong class="person-title">{{ getPersonDisplayName(item) }}</strong>
                                <span class="risk-badge" :class="riskClass(item.risk)">{{ getRiskText(item.risk) }}</span>
                                <span class="topic-badge"># {{ item.topic }}</span>
                              </div>

                            <div class="person-desc" v-html="highlightKeyword(item.summary, state.submittedKeyword)"></div>

                            <div class="person-alias-row">
                              <button v-for="alias in getPersonAliases(item)" :key="alias" class="person-alias-chip" @click.stop="drillDown(alias)">
                                <i class="fa-solid fa-user-tag"></i>
                                Alias: {{ alias }}
                              </button>
                            </div>

                            <div class="person-meta-row">
                              <span class="meta-source"><i :class="getMediaIcon(item.media)"></i> {{ item.media }}</span>
                              <span><i class="fa-regular fa-clock"></i> 最后活跃: {{ item.date }}</span>
                              <span><i class="fa-solid fa-location-dot"></i> {{ item.region }}</span>
                            </div>

                            <div class="person-confidence-row">
                              <span><i :class="getMediaIcon(item.media)"></i> {{ item.media }}</span>
                              <span class="person-confidence-pill">置信度 {{ getPersonConfidence(item) }}%</span>
                              <button class="entity-chip person-action-btn" @click.stop="toggleBasket(item)">
                                <i class="fa-solid" :class="basketIdSet.has(item.id) ? 'fa-circle-check' : 'fa-circle-plus'"></i>
                                {{ basketIdSet.has(item.id) ? '移出线索篮' : '加入线索篮' }}
                              </button>
                            </div>
                          </div>
                        </div>
                      </template>

                      <template v-else-if="item.viewType === 'intel'">
                        <label class="intel-pick" @click.stop>
                          <input type="checkbox" :checked="basketIdSet.has(item.id)" @change="toggleBasket(item)" />
                        </label>

                        <div class="intel-main">
                          <div class="intel-title-row">
                            <div class="intel-title-left">
                              <span class="intel-icon"><i class="fa-solid fa-file-shield"></i></span>
                              <strong class="intel-title">{{ getIntelDisplayTitle(item) }}</strong>
                            </div>
                            <div class="intel-title-right">
                              <span class="badge" :class="riskBadgeClass(item.risk)">{{ getRiskText(item.risk) }}</span>
                              <span class="topic-badge"># {{ item.topic }}</span>
                            </div>
                          </div>

                          <div v-if="getIntelEntities(item).length > 0" class="intel-entity-row">
                            <button v-for="ent in getIntelEntities(item)" :key="ent" class="intel-entity-chip" :class="`entity-${getIntelEntityTone(ent)}`" @click.stop="drillDown(ent)">
                              <i class="fa-solid fa-tag"></i>
                              {{ ent }}
                            </button>
                          </div>

                          <div class="intel-desc" v-html="highlightKeyword(item.summary, state.submittedKeyword)"></div>

                          <div class="intel-footer">
                            <div class="intel-meta-row">
                              <span class="meta-source"><i :class="getMediaIcon(item.media)"></i> {{ item.media }} / {{ getIntelChannel(item) }}</span>
                              <span><i class="fa-regular fa-clock"></i> {{ getIntelTime(item) }}</span>
                              <span><i class="fa-solid fa-location-dot"></i> {{ item.region }}</span>
                            </div>

                            <div class="intel-footer-right">
                              <button class="entity-chip intel-basket-btn" @click.stop="toggleBasket(item)">
                                <i class="fa-solid" :class="basketIdSet.has(item.id) ? 'fa-circle-check' : 'fa-circle-plus'"></i>
                                {{ basketIdSet.has(item.id) ? '移出线索篮' : '加入线索篮' }}
                              </button>

                              <div class="intel-social">
                                <span class="intel-stats"><i class="fa-solid fa-share-nodes"></i> {{ getIntelStats(item).fwd }}</span>
                                <span class="intel-stats"><i class="fa-solid fa-comment"></i> {{ getIntelStats(item).cmt }}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </template>

                      <template v-else>
                        <div class="card-top">
                          <div class="left-head">
                            <span class="head-icon"><i :class="getMediaIcon(item.media)"></i></span>
                            <div class="top-meta">
                              <div class="title-row">
                                <strong class="card-title" v-html="highlightKeyword(item.title, state.submittedKeyword)"></strong>
                                <span class="risk-badge" :class="riskClass(item.risk)">{{ getRiskText(item.risk) }}</span>
                                <span class="topic-badge"># {{ item.topic }}</span>
                              </div>
                              <div class="desc" v-html="highlightKeyword(item.summary, state.submittedKeyword)"></div>
                            </div>
                          </div>
                          <label class="pick-box" @click.stop>
                            <input type="checkbox" :checked="basketIdSet.has(item.id)" @change="toggleBasket(item)" />
                            加入线索篮
                          </label>
                        </div>

                        <div class="meta-row">
                          <span class="meta-source"><i :class="getMediaIcon(item.media)"></i> {{ item.media }}</span>
                          <span>{{ item.region }}</span>
                          <span>{{ item.date }}</span>
                          <span>{{ item.topic }}</span>
                        </div>

                        <div class="entity-row">
                          <button v-for="ent in item.entities" :key="ent" class="entity-chip" @click.stop="drillDown(ent)">
                            <i class="fa-solid fa-tag"></i>
                            {{ ent }}
                          </button>
                        </div>
                      </template>
                    </article>
                  </div>
                </section>
              </template>
              <div v-else class="empty-block">当前筛选条件下暂无命中</div>
            </div>
          </template>

          <template v-else>
            <div class="ai-mode" :class="{ 'focus-right': state.aiFullscreenTarget === 'right', 'focus-left': state.aiFullscreenTarget === 'left' }">
              <div class="ai-left" :class="{ collapsed: state.aiLeftCollapsed }">
                <div class="ai-header">
                  <div class="ai-header-title"><i class="fa-solid fa-sparkles"></i> AI全域感知与深度研判助手</div>
                  <div class="ai-header-actions">
                    <span class="ai-header-badge">实时研判</span>
                    <button class="ai-header-expand-btn" @click.stop="toggleAiLeftFullscreen" :title="state.aiFullscreenTarget === 'left' ? '恢复双栏' : '展开左侧助手栏'">
                      <i class="fa-solid" :class="state.aiFullscreenTarget === 'left' ? 'fa-compress' : 'fa-expand'"></i>
                    </button>
                  </div>
                </div>
                <div class="ai-output custom-scrollbar" ref="aiOutputRef" v-html="state.aiOutputHtml"></div>
                <div class="follow-up-row">
                  <input v-model="state.followUpInput" class="control-input" type="text" placeholder="继续追问，例如：请给出跨平台关联链路" @keyup.enter="sendFollowUp" />
                  <button class="btn btn-ai" @click="sendFollowUp"><i class="fa-solid fa-paper-plane"></i> 发送</button>
                </div>
              </div>

              <div class="ai-right" :class="{ collapsed: state.aiRightCollapsed }">
                <div class="ai-header">
                  <div class="ai-header-title"><i class="fa-solid fa-book-bookmark"></i> 检索参考源（Reference）</div>
                  <div class="ai-header-actions">
                    <span class="ai-header-badge">{{ finalFiltered.length }} 条</span>
                    <span class="ai-header-badge">{{ state.aiSources.length }} 条</span>
                    <button class="ai-header-expand-btn" @click.stop="toggleAiRightFullscreen" :title="state.aiFullscreenTarget === 'right' ? '恢复双栏' : '展开右侧参考源'">
                      <i class="fa-solid" :class="state.aiFullscreenTarget === 'right' ? 'fa-compress' : 'fa-expand'"></i>
                    </button>
                  </div>
                </div>
                <div v-if="state.aiLoading" class="ai-loading-indicator">
                  <i class="fa-solid fa-circle-notch fa-spin"></i> 正在检索...
                </div>
                <div v-else-if="state.aiSources.length > 0" class="ref-list custom-scrollbar">
                  <div class="ai-ref-card-list">
                    <IntelCard
                      v-for="source in state.aiSources"
                      :key="source.id"
                      :item="source"
                      :keyword="state.submittedKeyword"
                      :display-title="source.title || '未命名线索'"
                      :channel="source.channel || ''"
                      :time="source.date || ''"
                      :entities="source.entities || []"
                      :stats="{ fwd: undefined, cmt: undefined }"
                      :score="source.score"
                      :compact="true"
                      :show-checkbox="false"
                      :show-basket-btn="false"
                      :risk-class="riskClass"
                      :get-media-icon="getMediaIcon"
                      :get-entity-tone="getIntelEntityTone"
                      :highlight-keyword="highlightKeyword"
                      @click="openDetail(source)"
                    />
                  </div>
                </div>
                <div v-else-if="finalFiltered.length === 0" class="empty-block">暂无参考源</div>
                <div v-else class="ref-list custom-scrollbar">
                  <section v-for="group in aiReferenceGroups" :key="`ai-${group.type}`" class="ai-ref-group">
                    <h4 class="ai-ref-group-title">{{ group.label }} ({{ group.items.length }})</h4>
                    <div class="card-list ai-ref-card-list">
                      <article v-for="item in group.items" :key="`ref-${item.id}`" class="entity-card" @click="openDetail(item)">
                        <template v-if="item.viewType === 'account'">
                          <div class="account-card-head">
                            <label class="account-pick" @click.stop>
                              <input type="checkbox" :checked="basketIdSet.has(item.id)" @change="toggleBasket(item)" />
                            </label>

                            <div class="account-main">
                              <div class="account-title-row">
                                <img class="account-avatar" :src="item.avatar" alt="avatar" />
                                <div class="account-name-wrap">
                                  <div class="account-name-line">
                                    <strong class="account-name">{{ getAccountDisplayName(item) }}</strong>
                                    <span class="media-pill"><i :class="getMediaIcon(item.media)"></i> {{ getPlatformLabel(item.media) }}</span>
                                    <span class="risk-badge" :class="riskClass(item.risk)">{{ getRiskText(item.risk) }}</span>
                                    <span class="topic-badge"># {{ item.topic }}</span>
                                  </div>
                                  <div class="account-handle">{{ getAccountHandle(item) }}</div>
                                  <div class="desc account-desc" v-html="highlightKeyword(item.summary, state.submittedKeyword)"></div>
                                </div>
                              </div>

                              <div class="account-metrics">
                                <div class="metric-box">
                                  <div class="metric-k">粉丝</div>
                                  <div class="metric-v">{{ getAccountStat(item, 'followers') }}</div>
                                </div>
                                <div class="metric-box">
                                  <div class="metric-k">关注</div>
                                  <div class="metric-v">{{ getAccountStat(item, 'following') }}</div>
                                </div>
                                <div class="metric-box">
                                  <div class="metric-k">发帖</div>
                                  <div class="metric-v">{{ getAccountStat(item, 'posts') }}</div>
                                </div>
                                <div class="metric-box">
                                  <div class="metric-k">记录时间</div>
                                  <div class="metric-v">{{ item.date }}</div>
                                </div>
                              </div>

                              <div class="account-actions">
                                <button class="entity-chip account-action-btn" @click.stop="viewAssociatedPerson(item)">
                                  <i class="fa-solid fa-user-check"></i>
                                  查看人物
                                </button>
                                <button class="entity-chip account-action-btn" @click.stop="toggleBasket(item)">
                                  <i class="fa-solid" :class="basketIdSet.has(item.id) ? 'fa-circle-check' : 'fa-circle-plus'"></i>
                                  {{ basketIdSet.has(item.id) ? '移出线索篮' : '加入线索篮' }}
                                </button>
                              </div>
                            </div>

                            <div class="account-side">
                              <div class="account-side-label">归属人物</div>
                              <button class="account-side-link" @click.stop="viewAssociatedPerson(item)">
                                {{ getAssociatedPerson(item) }}
                              </button>
                            </div>
                          </div>
                        </template>

                        <template v-else-if="item.viewType === 'person'">
                          <div class="person-card-head">
                            <label class="person-pick" @click.stop>
                              <input type="checkbox" :checked="basketIdSet.has(item.id)" @change="toggleBasket(item)" />
                            </label>

                            <div class="person-main">
                              <div class="person-title-row">
                                <span class="person-icon"><i class="fa-solid fa-user-astronaut"></i></span>
                                <strong class="person-title">{{ getPersonDisplayName(item) }}</strong>
                                <span class="risk-badge" :class="riskClass(item.risk)">{{ getRiskText(item.risk) }}</span>
                                <span class="topic-badge"># {{ item.topic }}</span>
                              </div>

                              <div class="person-desc" v-html="highlightKeyword(item.summary, state.submittedKeyword)"></div>

                              <div class="person-alias-row">
                                <button v-for="alias in getPersonAliases(item)" :key="alias" class="person-alias-chip" @click.stop="drillDown(alias)">
                                  <i class="fa-solid fa-user-tag"></i>
                                  Alias: {{ alias }}
                                </button>
                              </div>

                              <div class="person-meta-row">
                                <span class="meta-source"><i :class="getMediaIcon(item.media)"></i> {{ item.media }}</span>
                                <span><i class="fa-regular fa-clock"></i> 最后活跃: {{ item.date }}</span>
                                <span><i class="fa-solid fa-location-dot"></i> {{ item.region }}</span>
                              </div>

                              <div class="person-confidence-row">
                                <span><i :class="getMediaIcon(item.media)"></i> {{ item.media }}</span>
                                <span class="person-confidence-pill">置信度 {{ getPersonConfidence(item) }}%</span>
                                <button class="entity-chip person-action-btn" @click.stop="toggleBasket(item)">
                                  <i class="fa-solid" :class="basketIdSet.has(item.id) ? 'fa-circle-check' : 'fa-circle-plus'"></i>
                                  {{ basketIdSet.has(item.id) ? '移出线索篮' : '加入线索篮' }}
                                </button>
                              </div>
                            </div>
                          </div>
                        </template>

                        <template v-else-if="item.viewType === 'intel'">
                          <label class="intel-pick" @click.stop>
                            <input type="checkbox" :checked="basketIdSet.has(item.id)" @change="toggleBasket(item)" />
                          </label>

                          <div class="intel-main">
                            <div class="intel-title-row">
                              <div class="intel-title-left">
                                <span class="intel-icon"><i class="fa-solid fa-file-shield"></i></span>
                                <strong class="intel-title">{{ getIntelDisplayTitle(item) }}</strong>
                              </div>
                              <div class="intel-title-right">
                                <span class="badge" :class="riskBadgeClass(item.risk)">{{ getRiskText(item.risk) }}</span>
                                <span class="topic-badge"># {{ item.topic }}</span>
                              </div>
                            </div>

                            <div v-if="getIntelEntities(item).length > 0" class="intel-entity-row">
                              <button v-for="ent in getIntelEntities(item)" :key="ent" class="intel-entity-chip" :class="`entity-${getIntelEntityTone(ent)}`" @click.stop="drillDown(ent)">
                                <i class="fa-solid fa-tag"></i>
                                {{ ent }}
                              </button>
                            </div>

                            <div class="intel-desc" v-html="highlightKeyword(item.summary, state.submittedKeyword)"></div>

                            <div class="intel-footer">
                              <div class="intel-meta-row">
                                <span class="meta-source"><i :class="getMediaIcon(item.media)"></i> {{ item.media }} / {{ getIntelChannel(item) }}</span>
                                <span><i class="fa-regular fa-clock"></i> {{ getIntelTime(item) }}</span>
                                <span><i class="fa-solid fa-location-dot"></i> {{ item.region }}</span>
                              </div>

                              <div class="intel-footer-right">
                                <button class="entity-chip intel-basket-btn" @click.stop="toggleBasket(item)">
                                  <i class="fa-solid" :class="basketIdSet.has(item.id) ? 'fa-circle-check' : 'fa-circle-plus'"></i>
                                  {{ basketIdSet.has(item.id) ? '移出线索篮' : '加入线索篮' }}
                                </button>

                                <div class="intel-social">
                                  <span class="intel-stats"><i class="fa-solid fa-share-nodes"></i> {{ getIntelStats(item).fwd }}</span>
                                  <span class="intel-stats"><i class="fa-solid fa-comment"></i> {{ getIntelStats(item).cmt }}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </template>
                      </article>
                    </div>
                  </section>
                </div>
              </div>
            </div>
          </template>
        </div>

        <aside v-if="state.mode === 'normal'" class="right-sidebar panel">
          <div class="right-tabs">
            <button class="tab-btn" :class="{ active: state.leftTab === 'filters' }" @click="state.leftTab = 'filters'">属性筛选</button>
            <button class="tab-btn" :class="{ active: state.leftTab === 'basket' }" @click="state.leftTab = 'basket'">线索篮 ({{ basketItems.length }})</button>
          </div>

          <div v-if="state.leftTab === 'filters'" class="right-scroll-section custom-scrollbar">
            <div class="filter-block">
              <div class="filter-title">时间快捷筛选</div>
              <div class="chips-wrap">
                <button v-for="opt in quickTimeOptions" :key="opt.value" class="chip" :class="{ active: state.quickTime === opt.value }" @click="state.quickTime = opt.value">{{ opt.label }}</button>
              </div>
            </div>

            <div class="filter-block">
              <div class="filter-title">地区</div>
              <select v-model="state.region" class="control-input full">
                <option value="all">全部地区</option>
                <option v-for="r in regionOptions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>

            <div class="filter-block">
              <div class="filter-title">风险评估</div>
              <div class="chips-wrap">
                <button v-for="risk in riskOptions" :key="risk" class="chip" :class="{ active: state.riskSet.includes(risk) }" @click="toggleArrayFilter('riskSet', risk)">{{ risk }}</button>
              </div>
            </div>

            <div class="filter-block">
              <div class="filter-title">媒介分布</div>
              <div class="chips-wrap">
                <button v-for="media in mediaOptions" :key="media" class="chip" :class="{ active: state.mediaSet.includes(media) }" @click="toggleArrayFilter('mediaSet', media)">{{ media }}</button>
              </div>
            </div>

            <div class="filter-block">
              <div class="filter-title">话题分类</div>
              <div class="chips-wrap topic-row">
                <button v-for="topic in topicOptions" :key="topic" class="chip" :class="{ active: state.topicSet.includes(topic) }" @click="toggleArrayFilter('topicSet', topic)">{{ topic }}</button>
              </div>
            </div>

            <div class="divider-line"></div>

            <div class="rank-module">
              <div class="module-title">地区分布排行</div>
              <div v-if="regionRank.length === 0" class="empty-block">暂无数据</div>
              <div v-else>
                <div
                  v-for="(row, idx) in regionRank"
                  :key="row.name"
                  class="rank-row clickable"
                  :class="{ active: state.region === row.name }"
                  @click="applyRegionFilterFromRank(row.name)"
                >
                  <span class="rank-num">{{ idx + 1 }}</span>
                  <span class="rank-name">{{ row.name }}</span>
                  <div class="progress-wrap"><div class="progress-bar" :style="{ width: `${row.percent}%` }"></div></div>
                  <span class="rank-value">{{ row.count }}</span>
                </div>
              </div>
            </div>

            <div class="rank-module">
              <div class="module-title">命中规则 Top5</div>
              <div v-if="ruleTop5.length === 0" class="empty-block">暂无数据</div>
              <div v-else>
                <div
                  v-for="(row, idx) in ruleTop5"
                  :key="row.name"
                  class="rank-row clickable"
                  :class="{ active: state.selectedRule === row.name }"
                  @click="applyRuleFilterFromRank(row.name)"
                >
                  <span class="rank-num">{{ idx + 1 }}</span>
                  <span class="rank-name">{{ row.name }}</span>
                  <div class="progress-wrap"><div class="progress-bar warning" :style="{ width: `${row.percent}%` }"></div></div>
                  <span class="rank-value">{{ row.count }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="right-scroll-section custom-scrollbar">
            <div class="basket-actions">
              <button class="btn btn-small" @click="clearBasket">清空</button>
              <button class="btn btn-ai btn-small" @click="analyzeBasketWithAI" :disabled="state.aiLoading">
                <i class="fa-solid fa-wand-magic-sparkles"></i>
                {{ state.aiLoading ? '分析中...' : '基于已选证据研判' }}
              </button>
            </div>

            <div v-if="basketItems.length === 0" class="empty-block">暂无已选线索</div>
            <div v-else class="basket-list">
              <div v-for="item in basketItems" :key="item.id" class="basket-item">
                <div class="basket-item-main" @click="openDetail(item)">
                  <div class="basket-title" v-html="highlightKeyword(item.title, state.submittedKeyword)"></div>
                  <div class="basket-meta">{{ item.viewType }} · {{ getRiskText(item.risk) }} · {{ item.region }}</div>
                </div>
                <button class="icon-btn" @click="removeFromBasket(item.id)"><i class="fa-solid fa-trash"></i></button>
              </div>
            </div>
          </div>
        </aside>
        </section>
      </template>
    </main>

    <div class="drawer-mask" :class="{ open: state.detailOpen }" @click.self="closeDetail">
      <div class="drawer" v-if="state.detailItem">
        <div class="drawer-header">
          <h3>{{ state.detailItem.viewType === 'person' ? getPersonDisplayName(state.detailItem) : state.detailItem.viewType === 'account' ? getAccountDisplayName(state.detailItem) : state.detailItem.title }}</h3>
          <button class="icon-btn" @click="closeDetail"><i class="fa-solid fa-xmark"></i></button>
        </div>

        <div class="drawer-body custom-scrollbar">
          <template v-if="state.detailItem.viewType === 'intel'">
            <div class="intel-drawer-chat">
              <div class="intel-drawer-chat-head">
                <span><i :class="getMediaIcon(state.detailItem.media)"></i> {{ getIntelChannel(state.detailItem) }}</span>
                <span>Members: {{ getIntelMemberCount(state.detailItem) }}</span>
              </div>
              <div class="intel-drawer-chat-body">
                <div class="intel-msg">
                  <div class="intel-msg-head">
                    <span>{{ getIntelPeerName(state.detailItem) }}</span>
                    <span>{{ getIntelPeerTime(state.detailItem) }}</span>
                  </div>
                  <div>{{ getIntelPeerText(state.detailItem) }}</div>
                </div>
                <div class="intel-msg self">
                  <div class="intel-msg-head">
                    <span>{{ getIntelPosterName(state.detailItem) }}</span>
                    <span>{{ getIntelPosterTime(state.detailItem) }}</span>
                  </div>
                  <div>{{ state.detailItem.summary }}</div>
                </div>
              </div>
            </div>

            <div class="intel-entities-box">
              <div class="module-title"><i class="fa-solid fa-tags"></i> 机器提取实体 (NLP Entities)</div>
              <div class="intel-entities-wrap">
                <span v-for="ent in getIntelEntities(state.detailItem)" :key="`drawer-${ent}`" class="intel-drawer-entity-chip" :class="`tone-${getIntelEntityTone(ent)}`">
                  <i class="fa-solid fa-tag"></i>
                  {{ ent }}
                </span>
              </div>
            </div>

            <div class="intel-workflow-title">工作流指令 (P2 Actions)</div>
          </template>

          <template v-else-if="state.detailItem.viewType === 'person'">
            <div class="person2-hero">
              <img src="/offline/avatar-default.svg" alt="avatar" class="person2-avatar" />
              <div class="person2-meta">
                <div class="person2-name">{{ getPersonDisplayName(state.detailItem) }}</div>
                <div class="person2-confidence">多源聚合置信度 {{ getPersonConfidence(state.detailItem) }}%</div>
              </div>
            </div>

            <div class="person2-proof-box">
              <div class="person2-proof-title"><i class="fa-solid fa-link"></i> 同人聚合证据链推演</div>
              <div class="person2-proof-line"><strong>[用户名特征]</strong> {{ getPersonEvidenceLine(state.detailItem) }} 呈现高度重合</div>
            </div>

            <div class="intel-workflow-title">工作流指令 (P2 Actions)</div>
          </template>

          <template v-else-if="state.detailItem.viewType === 'account'">
            <div class="account2-hero">
              <img src="/offline/avatar-default.svg" alt="avatar" class="account2-avatar" />
              <div class="account2-meta">
                <div class="account2-name">{{ getAccountDisplayName(state.detailItem) }}</div>
                <div class="account2-platform"><i :class="getMediaIcon(state.detailItem.media)"></i> {{ getPlatformLabel(state.detailItem.media) }} 账号</div>
              </div>
            </div>

            <div class="account2-profile-box">
              <div class="account2-profile-title"><i class="fa-solid fa-address-card"></i> 账号档案 (Profile)</div>
              <div class="account2-profile-row"><strong>签名/Bio:</strong><span>{{ getAccountBio(state.detailItem) }}</span></div>
              <div class="account2-profile-row"><strong>归属人物:</strong><button class="account2-owner-link" @click="openOwnerFromAccountDrawer(state.detailItem)">{{ getAccountOwnerName(state.detailItem) }}</button></div>
            </div>

            <div class="intel-workflow-title">工作流指令 (P2 Actions)</div>
          </template>

          <template v-else>
            <div class="base-grid">
              <div><span>类型：</span>{{ state.detailItem.viewType }}</div>
              <div><span>风险：</span>{{ state.detailItem.risk }}</div>
              <div><span>媒介：</span>{{ state.detailItem.media }}</div>
              <div><span>地区：</span>{{ state.detailItem.region }}</div>
              <div><span>话题：</span>{{ state.detailItem.topic }}</div>
              <div><span>时间：</span>{{ state.detailItem.date }}</div>
            </div>

            <div class="detail-summary">{{ state.detailItem.summary }}</div>

            <div v-if="state.detailItem.relatedAccounts?.length" class="related-block">
              <div class="module-title">关联账号</div>
              <ul>
                <li v-for="acc in state.detailItem.relatedAccounts" :key="acc">
                  <img src="/offline/avatar-default.svg" alt="avatar" />
                  <span>{{ acc }}</span>
                </li>
              </ul>
            </div>
          </template>
        </div>

        <div class="drawer-actions" :class="{ 'intel-actions': state.detailItem.viewType === 'intel' || state.detailItem.viewType === 'person' || state.detailItem.viewType === 'account' }">
          <template v-if="state.detailItem.viewType === 'intel'">
            <button class="btn intel-action-btn" @click="showToast('实时监控任务已启动')"><i class="fa-solid fa-satellite-dish"></i> 开启实时监控</button>
            <button class="btn intel-action-btn" @click="showToast('人工标注研判已记录')"><i class="fa-solid fa-pen-to-square"></i> 人工标注研判</button>
            <button class="btn btn-ai intel-action-btn primary" @click="showToast('已推送图谱扩线引擎')"><i class="fa-solid fa-diagram-project"></i> 推送图谱扩线引擎</button>
          </template>
          <template v-else-if="state.detailItem.viewType === 'person'">
            <button class="btn intel-action-btn" @click="showToast('人物实时监控任务已启动')"><i class="fa-solid fa-satellite-dish"></i> 开启实时监控</button>
            <button class="btn intel-action-btn" @click="showToast('人物人工标注研判已记录')"><i class="fa-solid fa-pen-to-square"></i> 人工标注研判</button>
            <button class="btn btn-ai intel-action-btn primary" @click="showToast('人物节点已推送图谱扩线引擎')"><i class="fa-solid fa-diagram-project"></i> 推送图谱扩线引擎</button>
          </template>
          <template v-else-if="state.detailItem.viewType === 'account'">
            <button class="btn intel-action-btn" @click="showToast('账号实时监控任务已启动')"><i class="fa-solid fa-satellite-dish"></i> 开启实时监控</button>
            <button class="btn intel-action-btn" @click="showToast('账号人工标注研判已记录')"><i class="fa-solid fa-pen-to-square"></i> 人工标注研判</button>
            <button class="btn btn-ai intel-action-btn primary" @click="showToast('账号节点已推送图谱扩线引擎')"><i class="fa-solid fa-diagram-project"></i> 推送图谱扩线引擎</button>
          </template>
          <template v-else>
            <button class="btn btn-primary" @click="showToast('已开启监控')">开启监控</button>
            <button class="btn" @click="showToast('已记录人工标注')">人工标注</button>
            <button class="btn btn-ai" @click="showToast('已推送至图谱扩线引擎')">推送图谱扩线引擎</button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue';
import AppHeader from '../components/AppHeader.vue';
import IntelCard from '../components/search/IntelCard.vue';

const BASE_DATE = new Date('2026-03-25T00:00:00+08:00');

const baseMockItems = [
  { id: 1, viewType: 'intel', title: '跨平台洗钱通道曝光（USDT）', summary: '发现 Telegram 与 X 双平台账号共用收款地址，资金在 24 小时内多跳转移。', risk: '高危', media: '跨平台聚合', region: '广东省', topic: '黑产', date: '2026-03-24', dayDiff: 1, entities: ['USDT', '0xA91f...D33', '@shadow_pay', '跨平台聚合'], relatedAccounts: ['@shadow_pay', 'x:shadow_pay_02', 'tg:pay_lane'] },
  { id: 2, viewType: 'intel', title: '疑似沿海走私补给链条', summary: '线索显示夜间海域接驳频繁，关联多个匿名账号同步发布暗语。', risk: '中危', media: 'Telegram', region: '福建省', topic: '走私', date: '2026-03-20', dayDiff: 5, entities: ['珠江口', '接驳', '@sea-hub', 'Tor'], relatedAccounts: ['@sea-hub', '@dock_signal'] },
  { id: 3, viewType: 'person', title: '人物画像：暗网前体中介 “M”', summary: '常用 Tor 论坛与 Telegram 进行撮合，近一月活动显著上升。', risk: '高危', media: 'Tor', region: '云南省', topic: '毒品', date: '2026-03-23', dayDiff: 2, entities: ['前体', 'Monero', 'M-bridge'], relatedAccounts: ['tor:m_bridge', 'tg:@m-ops'] },
  { id: 4, viewType: 'person', title: '人物画像：跨境社工库倒卖组织者', summary: '社工库关联渠道活跃，疑似按行业批量售卖账号与身份数据。', risk: '中危', media: '社工库关联', region: '北京市', topic: '黑产', date: '2026-03-12', dayDiff: 13, entities: ['社工库', '身份信息', '数据包'], relatedAccounts: ['@data_whale', 'x:leak-river'] },
  { id: 5, viewType: 'account', title: '账号视图：@Guide_Jihad', summary: '账号多次发布暴恐导向话题，存在群组扩散行为。', risk: '高危', media: 'Telegram', region: '新疆维吾尔自治区', topic: '暴恐', date: '2026-03-24', dayDiff: 1, entities: ['Guide_Jihad', '群组扩散', '节点账号'], relatedAccounts: ['@Guide_Jihad_backup', '@silent_node'] },
  { id: 6, viewType: 'account', title: '账号视图：x:runner_007', summary: '同城隐语交易高频，疑似向多平台引流。', risk: '低危', media: 'X', region: '上海市', topic: '毒品', date: '2025-12-28', dayDiff: 87, entities: ['飞叶子', '同城配送', 'runner_007'], relatedAccounts: ['weibo:runner_007', 'tg:@runner-007'] },
  { id: 7, viewType: 'intel', title: '涉毒渠道“冰糖”暗语再现', summary: 'Weibo 与 Telegram 同时出现“冰糖”与“走线”组合词，疑似复活旧链路。', risk: '中危', media: 'Weibo', region: '广西壮族自治区', topic: '毒品', date: '2026-03-25', dayDiff: 0, entities: ['冰糖', '走线', '同群转发'], relatedAccounts: ['weibo:cloud-9', 'tg:@line_227'] },
  { id: 8, viewType: 'account', title: '账号视图：tor:coil_drop', summary: '暗网账号疑似发布简易爆炸物教程链接，下载量异常上涨。', risk: '高危', media: 'Tor', region: '未知', topic: '暴恐', date: '2026-03-18', dayDiff: 7, entities: ['IED', '教程包', '匿名网盘'], relatedAccounts: [] },
  { id: 9, viewType: 'person', title: '人物画像：沿海物流“灰链协调员”', summary: '长期在 Telegram 分发货运口令，关联多个走私话题账号。', risk: '中危', media: 'Telegram', region: '广东省', topic: '走私', date: '2025-10-15', dayDiff: 161, entities: ['海运', '口令', '灰链'], relatedAccounts: ['@wolf_ship', '@bay_31'] },

  { id: 10, viewType: 'intel', title: '港口异常报关单批量复现', summary: '同一批次报关模板在多港口重复出现，疑似模板化走私操作。', risk: '高危', media: '跨平台聚合', region: '天津市', topic: '走私', date: '2026-03-24', dayDiff: 1, entities: ['报关单', '冷链柜', '中转车队'], relatedAccounts: ['tg:@port_line', 'x:port_line_a'] },
  { id: 11, viewType: 'intel', title: '可疑匿名筹资地址扩散', summary: '多个频道转发同一钱包地址并配套短链跳转。', risk: '中危', media: 'Telegram', region: '台湾省', topic: '暴恐', date: '2026-03-22', dayDiff: 3, entities: ['TRX地址', '短链跳转', '匿名筹资'], relatedAccounts: ['@island_fund', 'x:island_fund'] },
  { id: 12, viewType: 'intel', title: '跨境前体快递节点告警', summary: '疑似前体物质以分段包裹方式在多城市中转。', risk: '高危', media: 'Tor', region: '江苏省', topic: '毒品', date: '2026-03-21', dayDiff: 4, entities: ['前体', '国际EMS', '中转仓'], relatedAccounts: ['tor:chem_route', 'tg:@chem_route'] },
  { id: 13, viewType: 'intel', title: '社工库样本售卖渠道活跃', summary: '出现按行业拆包售卖账号数据行为。', risk: '中危', media: '社工库关联', region: '浙江省', topic: '黑产', date: '2026-03-19', dayDiff: 6, entities: ['账号包', '行业拆分', 'USDT'], relatedAccounts: ['@data_split', 'x:data_splitter'] },
  { id: 14, viewType: 'intel', title: '同城暗语交易高频联动', summary: '“飞叶子”“口令红包”等词在同城圈层同步上升。', risk: '低危', media: 'Weibo', region: '北京市', topic: '毒品', date: '2026-03-17', dayDiff: 8, entities: ['飞叶子', '口令红包', '同城配送'], relatedAccounts: ['weibo:runner_bj', 'tg:@runner_bj'] },
  { id: 15, viewType: 'intel', title: '疑似离岸洗钱跳板复现', summary: '链上监测发现地址在 12 小时内多次跨链桥转移。', risk: '高危', media: '跨平台聚合', region: '上海市', topic: '黑产', date: '2026-03-16', dayDiff: 9, entities: ['跨链桥', 'USDT', '跳板地址'], relatedAccounts: ['x:bridge_ops', 'tg:@bridge_ops'] },

  { id: 16, viewType: 'person', title: '人物画像：跨链洗钱执行人', summary: '长期在匿名频道发布资金清洗服务，具备多链操作经验。', risk: '高危', media: '跨平台聚合', region: '香港特别行政区', topic: '黑产', date: '2026-03-24', dayDiff: 1, entities: ['跨链桥', '混币', '冷钱包'], relatedAccounts: ['@mix_runner', 'x:mix_runner'] },
  { id: 17, viewType: 'person', title: '人物画像：边境仓储协调者', summary: '控制多个仓储节点并协调跨境转运。', risk: '中危', media: 'Telegram', region: '云南省', topic: '走私', date: '2026-03-20', dayDiff: 5, entities: ['边境仓', '车队', '夜间接驳'], relatedAccounts: ['@border_hub', '@yunnan_flow'] },
  { id: 18, viewType: 'person', title: '人物画像：匿名论坛教程分发者', summary: '在暗网论坛高频分发具破坏性教程链接。', risk: '高危', media: 'Tor', region: '未知', topic: '暴恐', date: '2026-03-23', dayDiff: 2, entities: ['教程包', '匿名网盘', '镜像站'], relatedAccounts: ['tor:guide_drop'] },
  { id: 19, viewType: 'person', title: '人物画像：同城零散分销中介', summary: '通过多平台分发同城交易暗语，活跃于夜间时段。', risk: '低危', media: 'Weibo', region: '重庆市', topic: '毒品', date: '2026-03-14', dayDiff: 11, entities: ['同城配送', '暗语', '收款码'], relatedAccounts: ['weibo:night_run', 'x:night_run_77'] },
  { id: 20, viewType: 'person', title: '人物画像：数据黑产包销代理', summary: '按地区维度分销泄露账号，售后群活跃。', risk: '中危', media: '社工库关联', region: '湖北省', topic: '黑产', date: '2026-03-10', dayDiff: 15, entities: ['账号包', '售后群', '批发价'], relatedAccounts: ['@data_agent_hb', 'x:data_agent_hb'] },

  { id: 21, viewType: 'account', title: '账号视图：@port_signal_01', summary: '多次发布港口口令与中转时间窗。', risk: '高危', media: 'Telegram', region: '广东省', topic: '走私', date: '2026-03-25', dayDiff: 0, entities: ['港口口令', '时间窗', '中转'], relatedAccounts: ['@port_signal_backup'] },
  { id: 22, viewType: 'account', title: '账号视图：x:shadow_broker', summary: 'X 账号疑似为多个高危频道引流。', risk: '中危', media: 'X', region: '福建省', topic: '黑产', date: '2026-03-23', dayDiff: 2, entities: ['引流', '短链', '推广矩阵'], relatedAccounts: ['tg:@shadow_broker'] },
  { id: 23, viewType: 'account', title: '账号视图：tor:chem_cell', summary: '暗网账号反复发布化学前体交易帖。', risk: '高危', media: 'Tor', region: '海外', topic: '毒品', date: '2026-03-22', dayDiff: 3, entities: ['前体', '匿名邮箱', '暗网论坛'], relatedAccounts: ['tor:chem_cell_2'] },
  { id: 24, viewType: 'account', title: '账号视图：weibo:city_runner_b', summary: '微博账号涉同城暗语与隐蔽联系方式。', risk: '低危', media: 'Weibo', region: '四川省', topic: '毒品', date: '2026-03-18', dayDiff: 7, entities: ['同城', '暗语', '引流'], relatedAccounts: ['x:city_runner_b'] },
  { id: 25, viewType: 'account', title: '账号视图：@fund_node_tw', summary: '长期发布筹资地址及话术模板。', risk: '高危', media: 'Telegram', region: '台湾省', topic: '暴恐', date: '2026-03-20', dayDiff: 5, entities: ['筹资地址', '模板', '分发'], relatedAccounts: ['@fund_node_tw_2'] },

  { id: 26, viewType: 'intel', title: '历史样本：冷链夹带路线库', summary: '用于测试 180 天与 365 天过滤窗口边界。', risk: '中危', media: '跨平台聚合', region: '辽宁省', topic: '走私', date: '2025-09-30', dayDiff: 176, entities: ['冷链', '夹带', '路线库'], relatedAccounts: ['@cold_route'] },
  { id: 27, viewType: 'intel', title: '历史样本：旧社工库交易贴', summary: '用于测试 1 年窗口内历史数据可见性。', risk: '低危', media: '社工库关联', region: '河南省', topic: '黑产', date: '2025-08-28', dayDiff: 210, entities: ['社工库', '旧帖', '打包'], relatedAccounts: ['x:old_leak_pack'] },
  { id: 28, viewType: 'person', title: '人物画像：历史链路中转者', summary: '仅在长周期窗口出现，便于测试趋势筛选。', risk: '中危', media: 'Telegram', region: '陕西省', topic: '走私', date: '2025-07-21', dayDiff: 247, entities: ['中转', '长链路', '旧节点'], relatedAccounts: ['@relay_old'] },
  { id: 29, viewType: 'account', title: '账号视图：x:legacy_node_09', summary: '历史活跃账号，当前已低频。', risk: '低危', media: 'X', region: '吉林省', topic: '黑产', date: '2025-06-11', dayDiff: 287, entities: ['低频', '历史账号', '旧话术'], relatedAccounts: ['tg:@legacy_node_09'] },
  { id: 30, viewType: 'intel', title: '极近实时样本：凌晨突发链路', summary: '用于验证 24H 筛选与右侧分析栏联动。', risk: '高危', media: 'Telegram', region: '广西壮族自治区', topic: '暴恐', date: '2026-03-25', dayDiff: 0, entities: ['凌晨告警', '群组扩散', '高危词'], relatedAccounts: ['@flash_node_01'] }
];

const formatDateByDiff = (dayDiff) => {
  const ms = BASE_DATE.getTime() - (dayDiff * 24 * 60 * 60 * 1000);
  const d = new Date(ms);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};

const generatedMockItems = Array.from({ length: 90 }, (_, idx) => {
  const id = 31 + idx;
  const viewTypes = ['intel', 'person', 'account'];
  const medias = ['Telegram', 'Tor', 'Weibo', 'X', '跨平台聚合', '社工库关联'];
  const topics = ['毒品', '走私', '黑产', '暴恐'];
  const risks = ['高危', '中危', '低危'];
  const regions = [
    '广东省', '福建省', '云南省', '北京市', '上海市', '天津市', '重庆市', '浙江省',
    '江苏省', '四川省', '湖北省', '广西壮族自治区', '香港特别行政区', '台湾省', '海外', '未知'
  ];

  const viewType = viewTypes[idx % viewTypes.length];
  const media = medias[idx % medias.length];
  const topic = topics[idx % topics.length];
  const risk = risks[(idx + Math.floor(idx / 7)) % risks.length];
  const region = regions[idx % regions.length];

  let dayDiff = 0;
  if (idx < 25) dayDiff = idx % 7;
  else if (idx < 60) dayDiff = 7 + (idx % 24);
  else if (idx < 80) dayDiff = 45 + (idx % 120);
  else dayDiff = 190 + (idx % 150);

  const date = formatDateByDiff(dayDiff);
  const titlePrefix = viewType === 'intel' ? '情报线索' : viewType === 'person' ? '人物画像' : '账号视图';
  const topicLabel = topic === '毒品' ? '涉毒隐语' : topic === '走私' ? '跨境走私' : topic === '黑产' ? '数据黑产' : '暴恐扩散';
  const mediaLabel = media === '跨平台聚合' ? '跨平台链路' : media === '社工库关联' ? '社工关联链路' : `${media} 渠道`;

  const summaryMap = {
    intel: `监测到${topicLabel}在${mediaLabel}出现阶段性升温，建议结合实体标签进行扩线。`,
    person: `该对象在${mediaLabel}持续活跃，行为特征与${topicLabel}画像高度重合。`,
    account: `该账号近期在${mediaLabel}发布${topicLabel}相关内容，存在跨平台联动迹象。`
  };

  const entityPoolByTopic = {
    '毒品': ['冰糖', '白面', '前体', 'USDT', '国际EMS', '同城配送'],
    '走私': ['接驳', '边境仓', '冷链柜', '口令', '中转车队', '埋包'],
    '黑产': ['社工库', '账号包', '短链', '跳板地址', '引流矩阵', '售后群'],
    '暴恐': ['匿名筹资', '镜像站', '教程包', '群组扩散', '高危词', '节点账号']
  };
  const picked = entityPoolByTopic[topic];
  const entities = [picked[idx % picked.length], picked[(idx + 2) % picked.length], media, `样本#${id}`];

  const accountSeed = `node_${String(id).padStart(3, '0')}`;
  const relatedAccounts = [
    `@${accountSeed}`,
    `x:${accountSeed}`,
    media === 'Tor' ? `tor:${accountSeed}` : `tg:@${accountSeed}`
  ];

  return {
    id,
    viewType,
    title: `${titlePrefix}：${topicLabel}样本 ${String(id).padStart(3, '0')}`,
    summary: summaryMap[viewType],
    risk,
    media,
    region,
    topic,
    date,
    dayDiff,
    entities,
    relatedAccounts
  };
});

// const mockItems = [...baseMockItems, ...generatedMockItems].map((item) => ({ ...item, avatar: '/offline/avatar-default.svg' }));

const quickTimeOptions = [{ label: '全部', value: 'all' }, { label: '7天', value: '7d' }, { label: '1个月', value: '1m' }, { label: '半年', value: '6m' }, { label: '1年', value: '1y' }];
const riskOptions = ['高危', '中危', '低危'];
const mediaOptions = ['Telegram', 'Tor', 'Weibo', 'X', '跨平台聚合', '社工库关联'];
const topicOptions = ['毒品', '走私', '黑产', '暴恐'];
const analysisTimeTabs = [{ label: '24H', value: '24h' }, { label: '7天', value: '7d' }, { label: '30天', value: '30d' }, { label: '全部', value: 'all' }];

const state = reactive({
  mode: 'normal', hasSubmitted: false, currentView: 'all', inputKeyword: '', submittedKeyword: '',
  leftTab: 'filters', quickTime: 'all', region: 'all', riskSet: [], mediaSet: [], topicSet: [],
  basketIds: [], groupTab: 'all', analysisTime: '7d', selectedRule: 'all',
  aiLeftCollapsed: false, aiRightCollapsed: false, aiOutputHtml: '', followUpInput: '',
  aiFullscreenTarget: null,
  detailOpen: false, detailItem: null,
  // AI 搜索相关状态
  aiSessionId: null,
  aiLoading: false,
  aiSources: []
});

const aiOutputRef = ref(null);
const loading = ref(false);
const error = ref(null);
const apiData = ref([]);

const fetchSearchResults = async (keyword = '') => {
  loading.value = true;
  error.value = null;
  try {
    const params = new URLSearchParams();
    params.append('limit', '20');
    if (keyword) params.append('keyword', keyword);
    const response = await fetch(`/api/search/unified?${params.toString()}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const result = await response.json();
    if (result.items && Array.isArray(result.items)) {
      apiData.value = result.items.map((item) => ({ ...item, avatar: '/offline/avatar-default.svg' }));
    } else {
      apiData.value = [];
    }
  } catch (e) {
    error.value = e.message;
    apiData.value = [];
  } finally {
    loading.value = false;
  }
};

// ================== AI RAG 搜索 API 调用 ==================

// 生成唯一会话 ID
const generateSessionId = () => {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

// RAG 智能搜索
const fetchRAGSearch = async (question, sessionId, useRerank = false) => {
  try {
    const response = await fetch('/api/rag/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        session_id: sessionId,
        use_rerank: useRerank
      })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('RAG 搜索失败:', e);
    throw e;
  }
};

// 获取对话历史
const fetchRAGHistory = async (sessionId) => {
  try {
    const response = await fetch(`/api/rag/history/${sessionId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('获取历史失败:', e);
    return null;
  }
};

// 清除对话历史
const clearRAGHistory = async (sessionId) => {
  try {
    const response = await fetch(`/api/rag/history/${sessionId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('清除历史失败:', e);
    throw e;
  }
};

const regionOptions = computed(() => Array.from(new Set(apiData.value.map((x) => x.region))));
const quickTimeLabel = computed(() => quickTimeOptions.find((x) => x.value === state.quickTime)?.label || '全部');
const basketIdSet = computed(() => new Set(state.basketIds));

const quickTimePass = (item) => {
  const windowMap = { all: Infinity, '7d': 7, '1m': 30, '6m': 180, '1y': 365 };
  const limit = windowMap[state.quickTime] ?? Infinity;
  return limit === Infinity ? true : item.dayDiff <= limit;
};

const keywordPass = (item) => {
  if (!state.submittedKeyword) return true;
  const target = [item.title, item.summary, item.region, item.topic, item.media, ...item.entities, ...(item.relatedAccounts || [])].join(' | ').toLowerCase();
  return target.includes(state.submittedKeyword.toLowerCase());
};

const highlightKeyword = (text, keyword) => {
  if (!keyword || !text) return text;
  if (typeof text !== 'string') return text;
  const regex = new RegExp(`(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<mark class="search-highlight">$1</mark>');
};

const getRuleNameByItem = (item) => {
  if (item.topic === '暴恐') return '暴恐关键词链路命中';
  if (item.topic === '毒品') return '涉毒隐语识别';
  if (item.topic === '走私') return '沿海走私路径模式';
  if (item.media === '社工库关联') return '社工库关联泄漏';
  return '跨平台异常关联';
};

// const finalFiltered = computed(() => mockItems.filter((item) => {
const finalFiltered = computed(() => apiData.value.filter((item) => {
  const passType = state.currentView === 'all' ? true : item.viewType === state.currentView;
  const passRisk = state.riskSet.length ? state.riskSet.includes(item.risk) : true;
  const passMedia = state.mediaSet.length ? state.mediaSet.includes(item.media) : true;
  const passRegion = state.region === 'all' ? true : item.region === state.region;
  const passTopic = state.topicSet.length ? state.topicSet.includes(item.topic) : true;
  const passRule = state.selectedRule === 'all' ? true : getRuleNameByItem(item) === state.selectedRule;
  return passType && keywordPass(item) && passRisk && passMedia && passRegion && passTopic && passRule && quickTimePass(item);
}));

const groupedByType = computed(() => {
  const map = { intel: [], person: [], account: [] };
  finalFiltered.value.forEach((item) => map[item.viewType].push(item));
  return map;
});

const visibleGroupTabs = computed(() => {
  const labels = { all: '全部', intel: '情报线索', person: '人物画像', account: '账号视图' };
  return ['all', 'intel', 'person', 'account']
    .map((type) => ({ type, label: labels[type], count: type === 'all' ? finalFiltered.value.length : groupedByType.value[type].length }))
    .filter((tab) => tab.count > 0 || tab.type === 'all');
});

const renderGroups = computed(() => {
  const labels = { intel: '情报线索', person: '人物画像', account: '账号视图' };
  if (state.groupTab !== 'all') return [{ type: state.groupTab, label: labels[state.groupTab], items: groupedByType.value[state.groupTab] || [] }].filter((x) => x.items.length);
  return ['intel', 'person', 'account'].map((type) => ({ type, label: labels[type], items: groupedByType.value[type] })).filter((x) => x.items.length);
});

const aiReferenceGroups = computed(() => {
  const labels = { intel: '情报线索', person: '人物画像', account: '账号视图' };
  return ['intel', 'person', 'account']
    .map((type) => ({ type, label: labels[type], items: groupedByType.value[type] || [] }))
    .filter((group) => group.items.length > 0);
});

// const basketItems = computed(() => mockItems.filter((x) => basketIdSet.value.has(x.id)));
const basketItems = computed(() => apiData.value.filter((x) => basketIdSet.value.has(x.id)));

const analysisWindowPass = (item) => {
  if (state.analysisTime === 'all') return true;
  if (state.analysisTime === '24h') return item.dayDiff <= 1;
  if (state.analysisTime === '7d') return item.dayDiff <= 7;
  if (state.analysisTime === '30d') return item.dayDiff <= 30;
  return true;
};

const analysisSource = computed(() => finalFiltered.value.filter((item) => analysisWindowPass(item)));

const regionRank = computed(() => {
  const stat = {};
  analysisSource.value.forEach((item) => { stat[item.region] = (stat[item.region] || 0) + 1; });
  const list = Object.entries(stat).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count).slice(0, 6);
  const top = list[0]?.count || 1;
  return list.map((x) => ({ ...x, percent: Math.round((x.count / top) * 100) }));
});

const ruleTop5 = computed(() => {
  const stat = {};
  analysisSource.value.forEach((item) => { const name = getRuleNameByItem(item); stat[name] = (stat[name] || 0) + 1; });
  const list = Object.entries(stat).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count).slice(0, 5);
  const top = list[0]?.count || 1;
  return list.map((x) => ({ ...x, percent: Math.round((x.count / top) * 100) }));
});

const getRiskText = (risk) => ({ high: '高危', mid: '中危', low: '低危' }[risk] || risk);
const riskClass = (risk) => (risk === 'high' ? 'high' : risk === 'mid' ? 'mid' : 'low');
const riskBadgeClass = (risk) => (risk === 'high' ? 'badge-danger' : risk === 'mid' ? 'badge-warning' : 'badge-success');
const getPlatformLabel = (media) => {
  if (media === 'X') return 'X (Twitter)';
  return media;
};

const getPersonDisplayName = (item) => {
  if (!item?.title) return '未命名对象';
  const parts = item.title.split('：');
  return (parts[1] || item.title).trim();
};

const getPersonAliases = (item) => {
  const aliases = Array.isArray(item?.relatedAccounts) ? item.relatedAccounts : [];
  if (!aliases.length) return ['unknown'];
  return aliases.slice(0, 2).map(v => v.replace(/^tg:@|^@/, '').replace(/^x:|^tor:|^weibo:/, ''));
};

const getPersonConfidence = (item) => {
  const seed = Number(item?.id || 0);
  return 80 + (seed % 17);
};

const getPersonEvidenceLine = (item) => {
  const aliases = getPersonAliases(item);
  if (!aliases.length) return '用户名样本缺失';
  return aliases.join(' / ');
};

const getIntelDisplayTitle = (item) => item?.title || '未命名线索';

const getIntelEntities = (item) => {
  const list = Array.isArray(item?.entities) ? item.entities : [];
  return list.slice(0, 5);
};

const getIntelEntityTone = (entity = '') => {
  const raw = String(entity || '').trim();
  const t = raw.toLowerCase();

  // 资金类：钱包、币种、地址、链上关键词
  if (/usdt|btc|xmr|trx|wallet|0x|eth|sol|bnb|收款|转账|打款|汇款|钱|币/.test(t)) return 'money';

  // 地域类：省市区县、边境、港口等地理节点
  if (/省|市|区|县|州|港|边境|口岸|云南|广东|福建|北京|上海|香港|台湾|海外|东南亚|北美|中东|欧洲/.test(raw)) return 'loc';

  // 黑话/行为类：走私交易语义、流程动作词
  if (/白面|冰糖|前体|暗语|走线|黑话|口令|埋包|接驳|代发|出货|同城|担保|放货|上游|下家/.test(raw)) return 'slang';

  // 身份/账号/平台类：账号标识、平台名、样本编号、渠道节点
  if (/^@|tg|id|supplier|_|telegram|weibo|tor|\bx\b|样本#|社工库|短链|镜像|节点|账号|频道|群/.test(t)) return 'id';

  // 兜底：仍未命中的实体按稳定哈希分配色调，避免出现“无色标签”
  const seed = raw.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  return ['id', 'slang', 'loc', 'money'][seed % 4];
};

const getIntelTime = (item) => {
  const seed = Number(item?.id || 0);
  const hour = String((seed * 3) % 24).padStart(2, '0');
  const minute = String((seed * 7) % 60).padStart(2, '0');
  return `${item?.date || ''} ${hour}:${minute}`.trim();
};

const getIntelChannel = (item) => {
  const seed = Number(item?.id || 0);
  const dict = {
    Telegram: ['东南亚特货担保群', '边境走线观察', '匿名交易频道'],
    Tor: ['Dread 镜像论坛', '隐匿交易板', '洋葱市场讨论区'],
    Weibo: ['同城超话', '热点话题区', '公开线索池'],
    X: ['OSINT 联动流', '匿名链路观察', '灰产追踪列表'],
    '跨平台聚合': ['跨源聚合引擎', '多域融合节点', '全域关联池'],
    '社工库关联': ['社工库索引', '泄露样本关联', '黑产渠道镜像']
  };
  const options = dict[item?.media] || ['默认渠道'];
  return options[seed % options.length];
};

const getIntelStats = (item) => {
  const seed = Number(item?.id || 0);
  return {
    fwd: 8 + ((seed * 11) % 60),
    cmt: 2 + ((seed * 7) % 26)
  };
};

const getIntelMemberCount = (item) => {
  const seed = Number(item?.id || 0);
  const count = 1000 + ((seed * 91) % 5800);
  return `${(count / 1000).toFixed(1)}K`;
};

const getIntelPosterName = (item) => {
  const ids = Array.isArray(item?.relatedAccounts) ? item.relatedAccounts : [];
  return (ids[0] || '@intel_poster').replace(/^tg:|^x:|^tor:|^weibo:/, '');
};

const getIntelPeerName = (item) => {
  const seed = Number(item?.id || 0);
  return `Buyer_${(seed * 37) % 999}`;
};

const getIntelPosterTime = (item) => {
  const time = getIntelTime(item).split(' ')[1] || '10:15';
  return time;
};

const getIntelPeerTime = (item) => {
  const seed = Number(item?.id || 0);
  const hour = String((seed * 5) % 24).padStart(2, '0');
  const minute = String((seed * 11) % 60).padStart(2, '0');
  return `${hour}:${minute}`;
};

const getIntelPeerText = (item) => {
  if (item?.topic === '毒品') return '场子里缺货了，谁家有现货？走边境的。';
  if (item?.topic === '走私') return '这批货什么时候能到口岸，今晚能接吗？';
  if (item?.topic === '黑产') return '新样本到手了，账号包和短链都齐。';
  return '这个节点还在线吗？有新消息就同步。';
};

const getAccountHandle = (item) => {
  if (!item?.title) return 'unknown';
  const parts = item.title.split('：');
  return (parts[1] || item.title).trim();
};

const getAccountDisplayName = (item) => {
  const handle = getAccountHandle(item);
  return handle.startsWith('@') ? handle : `@${handle.replace(/^x:|^tor:|^weibo:/, '')}`;
};

const compactNumber = (num) => {
  if (num >= 10000) return `${(num / 1000).toFixed(1)}K`;
  return String(num);
};

const getAccountStat = (item, key) => {
  const seed = Number(item?.id || 0);
  const followersRaw = 6000 + ((seed * 973) % 18000);
  const followingRaw = 35 + ((seed * 17) % 420);
  const postsRaw = 120 + ((seed * 31) % 2400);
  const map = {
    followers: compactNumber(followersRaw),
    following: String(followingRaw),
    posts: compactNumber(postsRaw)
  };
  return map[key] || '--';
};

const getAccountBio = (item) => {
  const topicMap = {
    '毒品': 'privacy | crypto | osint notes',
    '走私': 'route ops | dark logistics',
    '黑产': 'data trade | leak mirror',
    '暴恐': 'anon channel relay'
  };
  return topicMap[item?.topic] || 'intel relay account';
};

const getAccountOwnerName = (item) => {
  const topicMap = {
    '毒品': 'Ivan Petrov (ShadowFox)',
    '走私': 'Mekong Supplier',
    '黑产': 'Dark_Chemist',
    '暴恐': 'Node Relay Operator'
  };
  return topicMap[item?.topic] || getAssociatedPerson(item);
};

const getAssociatedPerson = (item) => {
  if (item.relatedAccounts?.length) {
    return item.relatedAccounts[0].replace(/^tg:@|^@/, '').replace(/^x:|^tor:|^weibo:/, '');
  }
  const handle = getAccountHandle(item).replace(/^@/, '');
  return handle || '未建立关联';
};

const getMediaIcon = (media) => {
  if (media === 'Telegram') return 'fa-brands fa-telegram';
  if (media === 'Tor') return 'fa-solid fa-user-secret';
  if (media === 'Weibo') return 'fa-brands fa-weibo';
  if (media === 'X') return 'fa-brands fa-twitter';
  if (media === '社工库关联') return 'fa-solid fa-database';
  return 'fa-solid fa-circle-nodes';
};
const toggleArrayFilter = (field, value) => {
  const arr = state[field];
  const idx = arr.indexOf(value);
  if (idx >= 0) arr.splice(idx, 1); else arr.push(value);
};

const applyRegionFilterFromRank = (regionName) => {
  state.region = state.region === regionName ? 'all' : regionName;
};

const applyRuleFilterFromRank = (ruleName) => {
  state.selectedRule = state.selectedRule === ruleName ? 'all' : ruleName;
};

const submitSearch = async (mode) => {
  const isNewKeyword = state.submittedKeyword !== state.inputKeyword.trim();
  state.submittedKeyword = state.inputKeyword.trim();
  state.mode = mode === 'ai' ? 'ai' : 'normal';
  state.hasSubmitted = true;
  if (!visibleGroupTabs.value.some((x) => x.type === state.groupTab)) state.groupTab = 'all';

  if (state.mode === 'ai') {
    state.aiLeftCollapsed = false;
    state.aiRightCollapsed = false;
    state.aiFullscreenTarget = null;
    state.aiLoading = true;

    // 【修复 1：彻底重置会话状态】
    // 只要是从顶部搜索框触发的请求，一律作为新会话处理
    if (state.aiSessionId) {
      // 异步通知后端清理旧历史，释放内存，不需要 await 阻塞前端
      clearRAGHistory(state.aiSessionId).catch(e => console.error('清理历史失败:', e));
    }
    
    // 清空前端上下文与输出
    state.aiOutputHtml = '';
    state.aiSources = [];
    state.followUpInput = '';
    
    // 生成全新的会话 ID，切断上下文关联
    state.aiSessionId = generateSessionId();

    try {
      const result = await fetchRAGSearch(state.submittedKeyword, state.aiSessionId, false);
      state.aiSources = formatAISources(result.sources);

      const htmlContent = markdownToHtml(result.answer);
      typeWriteHtml(htmlContent); // 此时 append 默认为 false
    } catch (e) {
      state.aiOutputHtml = `<div class="ai-error">搜索失败: ${e.message}</div>`;
    } finally {
      state.aiLoading = false;
    }
  } else {
    // 普通模式
    await fetchSearchResults(state.submittedKeyword);
  }
};

const resetAll = async () => {
  // 如果有 AI 会话，清除后端历史
  if (state.aiSessionId) {
    try {
      await clearRAGHistory(state.aiSessionId);
    } catch (e) {
      console.error('清除后端历史失败:', e);
    }
  }

  state.mode = 'normal'; state.currentView = 'all'; state.inputKeyword = ''; state.submittedKeyword = '';
  state.quickTime = 'all'; state.region = 'all'; state.riskSet = []; state.mediaSet = []; state.topicSet = [];
  state.groupTab = 'all'; state.analysisTime = '7d'; state.selectedRule = 'all'; state.followUpInput = '';
  state.aiOutputHtml = ''; state.hasSubmitted = false;
  state.aiFullscreenTarget = null;
  state.aiSessionId = null;
  state.aiSources = [];
};

const toggleBasket = (item) => {
  if (basketIdSet.value.has(item.id)) state.basketIds = state.basketIds.filter((id) => id !== item.id);
  else state.basketIds = [...state.basketIds, item.id];
};
const removeFromBasket = (id) => { state.basketIds = state.basketIds.filter((x) => x !== id); };
const clearBasket = () => { state.basketIds = []; };

const analyzeBasket = () => {
  if (!basketItems.value.length) { window.alert('线索篮为空，请先勾选至少一条证据。'); return; }
  state.mode = 'ai';
  analyzeBasketWithAI();
};

const drillDown = (keyword) => { state.inputKeyword = keyword; submitSearch('normal'); };
const viewAssociatedPerson = (item) => {
  state.currentView = 'person';
  state.groupTab = 'person';
  state.inputKeyword = getAssociatedPerson(item);
  submitSearch('normal');
};
const openOwnerFromAccountDrawer = (item) => {
  closeDetail();
  state.currentView = 'person';
  state.groupTab = 'person';
  state.inputKeyword = getAccountOwnerName(item);
  submitSearch('normal');
};
const openDetail = (item) => { state.detailItem = item; state.detailOpen = true; };
const closeDetail = () => { state.detailOpen = false; setTimeout(() => { state.detailItem = null; }, 180); };
const showToast = (msg) => { window.alert(msg); };

let typingTimer = null;

// 打字机效果（纯文本）
const typeWrite = (text) => {
  if (typingTimer) clearTimeout(typingTimer);
  state.aiOutputHtml = '<span class="cursor"></span>';
  let i = 0;
  const step = () => {
    if (i >= text.length) { state.aiOutputHtml = state.aiOutputHtml.replace('<span class="cursor"></span>', ''); return; }
    const char = text[i] === '\n' ? '<br>' : text[i];
    state.aiOutputHtml = `${state.aiOutputHtml.replace('<span class="cursor"></span>', '')}${char}<span class="cursor"></span>`;
    i += 1;
    nextTick(() => { if (aiOutputRef.value) aiOutputRef.value.scrollTop = aiOutputRef.value.scrollHeight; });
    typingTimer = setTimeout(step, 18);
  };
  step();
};

// 打字机效果（HTML，追加模式）
const typeWriteHtml = (html, append = false) => {
  if (typingTimer) clearTimeout(typingTimer);

  if (!append) {
    state.aiOutputHtml = '';
  }

  // 【修复 2：锁定基准 HTML】
  // 记录开始打字前的完整内容。移除末尾可能存在的旧光标。
  const baseHtml = append ? state.aiOutputHtml.replace(/<span class="cursor"><\/span>$/, '') : '';

  // 创建一个临时容器来解析 HTML
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = html;
  const textContent = tempDiv.textContent || tempDiv.innerText || '';

  let i = 0;
  const step = () => {
    if (i >= textContent.length) {
      // 完成后直接在基准 HTML 后拼接完整的结构化 HTML
      state.aiOutputHtml = baseHtml + html;
      return;
    }

    // 显示部分文本 + 光标
    const partialText = textContent.substring(0, i + 1);
    
    // 每次都基于静态的 baseHtml 进行拼接，避免将 partialText 再次累加给自己
    state.aiOutputHtml = baseHtml + partialText + '<span class="cursor"></span>';

    i += 1;
    nextTick(() => { 
      if (aiOutputRef.value) aiOutputRef.value.scrollTop = aiOutputRef.value.scrollHeight; 
    });
    typingTimer = setTimeout(step, 12);
  };
  step();
};

// Markdown 转 HTML 简单实现
const markdownToHtml = (markdown) => {
  if (!markdown) return '';

  let html = markdown
    // 转义 HTML 特殊字符
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // 标题
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // 粗体
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // 斜体
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // 引用
    .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
    // 无序列表
    .replace(/^\- (.*$)/gim, '<ul><li>$1</li></ul>')
    // 有序列表
    .replace(/^\d+\. (.*$)/gim, '<ol><li>$1</li></ol>')
    // 代码块
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // 行内代码
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 链接
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    // 分隔线
    .replace(/^\-\-\-+/gim, '<hr>')
    // 换行
    .replace(/\n/g, '<br>');

  // 合并相邻的列表
  html = html.replace(/<\/ul><ul>/g, '');
  html = html.replace(/<\/ol><ol>/g, '');

  return html;
};

// HTML 转义
const escapeHtml = (text) => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

const makeAiReport = (fromBasket = false) => {
  const src = fromBasket ? basketItems.value : finalFiltered.value;
  const typeStat = { intel: 0, person: 0, account: 0 };
  src.forEach((item) => { typeStat[item.viewType] += 1; });
  const lines = [
    `基准时间：${BASE_DATE.toISOString().slice(0, 10)}（day-window）`,
    `当前筛选命中：${src.length} 条`,
    `结构分布：intel ${typeStat.intel} / person ${typeStat.person} / account ${typeStat.account}`,
    '',
    '研判摘要：',
    '- 命中目标存在跨平台扩散迹象，建议优先关注高危账号与资金介质。',
    '- 已识别出可下钻实体（账号、地址、暗语）并可用于图谱扩线。',
    '- 建议结合地区排行与规则 Top5 开展后续重点监测。'
  ];
  typeWrite(lines.join('\n'));
};

// 将后端返回的参考源转换为前端显示格式
const formatAISources = (sources) => {
  if (!sources || !Array.isArray(sources)) return [];

  let formatted = sources.map((source, index) => {
    // 【修复 3：提取真实的检索相似度，而不是用情报的风险等级分数(risk_score)代替】
    let relevance = 0;
    if (source.rerank_score !== undefined) {
      // Rerank 分数通常是 logit，用 sigmoid 映射到 0-1
      relevance = 1 / (1 + Math.exp(-source.rerank_score));
    } else if (source.distance !== undefined) {
      // L2 distance 越小越好，映射到 0-1
      relevance = 1 / (1 + source.distance);
    } else {
      relevance = 0.9 - (index * 0.05); // 兜底
    }

    return {
      id: source.content_id || `ai-source-${index}`,
      viewType: 'intel',
      title: source.title || '未命名线索',
      summary: source.text_preview || source.raw_content || '',
      risk: source.risk_level || '中危',
      media: source.platform || '跨平台聚合',
      region: source.region || '未知',
      topic: source.threat_category || '黑产',
      date: source.publish_time ? new Date(source.publish_time * 1000).toISOString().slice(0, 10) : BASE_DATE.toISOString().slice(0, 10),
      dayDiff: 0,
      entities: source.entities_industry || [],
      relatedAccounts: [],
      score: relevance, // 绑定真实计算的相关度
      avatar: '/offline/avatar-default.svg'
    };
  });

  // 按真实相关度从高到低二次排序
  formatted.sort((a, b) => b.score - a.score);
  return formatted;
};

// 基于已选证据进行 AI 分析
const analyzeBasketWithAI = async () => {
  if (!basketItems.value.length) {
    window.alert('线索篮为空，请先勾选至少一条证据。');
    return;
  }

  state.mode = 'ai';
  state.aiLoading = true;
  state.aiLeftCollapsed = false;
  state.aiRightCollapsed = false;
  state.aiFullscreenTarget = null;

  // 生成新的会话 ID
  state.aiSessionId = generateSessionId();

  // 构建分析提示
  const basketSummary = basketItems.value.map(item =>
    `[${item.viewType}] ${item.title}: ${item.summary}`
  ).join('\n');

  const analysisPrompt = `基于以下已选证据进行深度研判分析：\n\n${basketSummary}\n\n请提供综合分析报告，包括关联关系、风险等级评估和扩线建议。`;

  try {
    const result = await fetchRAGSearch(analysisPrompt, state.aiSessionId, false);
    state.aiSources = formatAISources(result.sources);

    const htmlContent = markdownToHtml(result.answer);
    typeWriteHtml(htmlContent);
  } catch (e) {
    state.aiOutputHtml = `<div class="ai-error">AI 分析失败: ${e.message}</div>`;
  } finally {
    state.aiLoading = false;
  }
};

const sendFollowUp = async () => {
  const q = state.followUpInput.trim();
  if (!q) return;

  state.aiLoading = true;

  try {
    // 追加显示用户的问题
    const userQuestionHtml = `<div class="ai-user-question"><strong>追问：</strong>${escapeHtml(q)}</div>`;
    state.aiOutputHtml += userQuestionHtml;
    state.followUpInput = '';

    // 【修复 1：追加 DOM 后立即触发滚动到底部】
    nextTick(() => {
      if (aiOutputRef.value) {
        aiOutputRef.value.scrollTop = aiOutputRef.value.scrollHeight;
      }
    });

    // 【修复 2：将 false 改为 true，开启 rerank 提升检索的语义匹配精度】
    const result = await fetchRAGSearch(q, state.aiSessionId, true);
    
    // 使用 formatAISources 转换后端数据格式
    state.aiSources = formatAISources(result.sources || []);

    // 显示 AI 回答
    const aiAnswerHtml = markdownToHtml(result.answer);
    typeWriteHtml(aiAnswerHtml, true);
  } catch (e) {
    state.aiOutputHtml += `<div class="ai-error">追问失败: ${e.message}</div>`;
  } finally {
    state.aiLoading = false;
  }
};

const toggleAiLeftFullscreen = () => {
  if (state.aiFullscreenTarget === 'left') {
    state.aiFullscreenTarget = null;
    return;
  }
  state.aiFullscreenTarget = 'left';
};

const toggleAiRightFullscreen = () => {
  if (state.aiFullscreenTarget === 'right') {
    state.aiFullscreenTarget = null;
    return;
  }
  state.aiFullscreenTarget = 'right';
};

watch(() => [state.currentView, state.quickTime, state.region, state.riskSet.length, state.mediaSet.length, state.topicSet.length, state.selectedRule], () => {
  if (!visibleGroupTabs.value.some((x) => x.type === state.groupTab)) state.groupTab = 'all';
});
</script>


<style src="../assets/styles/pages/search.css"></style>
