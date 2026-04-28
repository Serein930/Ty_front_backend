<template>
  <div class="ai-mode" :class="{ 'focus-right': fullscreenTarget === 'right', 'focus-left': fullscreenTarget === 'left' }">
    <div class="ai-left" :class="{ collapsed: leftCollapsed }">
      <div class="ai-header">
        <div class="ai-header-title"><i class="fa-solid fa-sparkles"></i> AI全域感知与深度研判助手</div>
        <div class="ai-header-actions">
          <span class="ai-header-badge">实时研判</span>
          <button class="ai-header-expand-btn" @click.stop="$emit('toggle-left')" :title="fullscreenTarget === 'left' ? '恢复双栏' : '展开左侧助手栏'">
            <i class="fa-solid" :class="fullscreenTarget === 'left' ? 'fa-compress' : 'fa-expand'"></i>
          </button>
        </div>
      </div>
      <div class="ai-output custom-scrollbar" ref="outputRef" v-html="outputHtml"></div>
      <div class="follow-up-row">
        <input v-model="followUpInput" class="control-input" type="text" placeholder="继续追问，例如：请给出跨平台关联链路" @keyup.enter="$emit('send-followup')" />
        <button class="btn btn-ai" @click="$emit('send-followup')"><i class="fa-solid fa-paper-plane"></i> 发送</button>
      </div>
    </div>

    <div class="ai-right" :class="{ collapsed: rightCollapsed }">
      <div class="ai-header">
        <div class="ai-header-title"><i class="fa-solid fa-book-bookmark"></i> 检索参考源（Reference）</div>
        <div class="ai-header-actions">
          <span class="ai-header-badge">{{ filteredCount }} 条</span>
          <span class="ai-header-badge">{{ sourceCount }} 条</span>
          <button class="ai-header-expand-btn" @click.stop="$emit('toggle-right')" :title="fullscreenTarget === 'right' ? '恢复双栏' : '展开右侧参考源'">
            <i class="fa-solid" :class="fullscreenTarget === 'right' ? 'fa-compress' : 'fa-expand'"></i>
          </button>
        </div>
      </div>
      <div v-if="loading" class="ai-loading-indicator">
        <i class="fa-solid fa-circle-notch fa-spin"></i> 正在检索...
      </div>
      <div v-else-if="sourceCount > 0" class="ref-list custom-scrollbar">
        <div class="ai-sources-list">
          <div
            v-for="source in sources"
            :key="source.id"
            class="ai-source-item"
            @click="$emit('open-detail', source)"
          >
            <div class="ai-source-header">
              <span class="ai-source-type" :class="source.viewType">
                {{ source.viewType === 'intel' ? '情报' : source.viewType === 'person' ? '人物' : '账号' }}
              </span>
              <span class="ai-source-score" v-if="source.score">相关度: {{ (source.score * 100).toFixed(1) }}%</span>
            </div>
            <div class="ai-source-title">{{ source.title }}</div>
            <div class="ai-source-summary">{{ source.summary.substring(0, 80) }}...</div>
            <div class="ai-source-meta">
              <span :class="['risk-tag', riskClass(source.risk)]">{{ source.risk }}</span>
              <span class="source-media"><i :class="getMediaIcon(source.media)"></i> {{ source.media }}</span>
              <span class="source-region">{{ source.region }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-block">暂无参考源</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  outputHtml: {
    type: String,
    default: ''
  },
  followUpInput: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  sources: {
    type: Array,
    default: () => []
  },
  filteredCount: {
    type: Number,
    default: 0
  },
  sourceCount: {
    type: Number,
    default: 0
  },
  fullscreenTarget: {
    type: String,
    default: null
  },
  leftCollapsed: {
    type: Boolean,
    default: false
  },
  rightCollapsed: {
    type: Boolean,
    default: false
  },
  riskClass: {
    type: Function,
    default: (risk) => risk === '高危' ? 'high' : risk === '中危' ? 'mid' : 'low'
  },
  getMediaIcon: {
    type: Function,
    default: (media) => 'fa-solid fa-globe'
  }
});

defineEmits(['toggle-left', 'toggle-right', 'send-followup', 'open-detail']);
</script>

