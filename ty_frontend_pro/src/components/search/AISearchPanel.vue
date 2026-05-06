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
        <div class="ai-ref-card-list">
          <IntelCard
            v-for="source in sources"
            :key="source.id"
            :item="source"
            :keyword="keyword"
            :display-title="source.title || '未命名线索'"
            :channel="source.channel || ''"
            :time="source.date || ''"
            :entities="source.entities || []"
            :stats="{ fwd: undefined, cmt: undefined }"
            :score="source.score"
            :compact="true"
            :show-checkbox="false"
            :show-basket-btn="false"
            :risk-class="riskClass || defaultRiskClass"
            :get-media-icon="getMediaIcon || defaultGetMediaIcon"
            :get-entity-tone="defaultGetEntityTone"
            :highlight-keyword="defaultHighlightKeyword"
            @click="$emit('open-detail', source)"
          />
        </div>
      </div>
      <div v-else class="empty-block">暂无参考源</div>
    </div>
  </div>
</template>

<script setup>
import IntelCard from './IntelCard.vue';

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
  keyword: {
    type: String,
    default: ''
  },
  riskClass: {
    type: Function,
    default: null
  },
  getMediaIcon: {
    type: Function,
    default: null
  }
});

defineEmits(['toggle-left', 'toggle-right', 'send-followup', 'open-detail']);

// 默认工具函数
const defaultRiskClass = (risk) => risk === 'high' ? 'high' : risk === 'mid' ? 'mid' : 'low';
const defaultGetMediaIcon = (media) => {
  const map = {
    'Telegram': 'fa-brands fa-telegram',
    'Weibo': 'fa-brands fa-weibo',
    'X': 'fa-brands fa-x-twitter',
    'Tor': 'fa-solid fa-user-secret',
    '跨平台聚合': 'fa-solid fa-circle-nodes',
    '社工库关联': 'fa-solid fa-database'
  };
  return map[media] || 'fa-solid fa-globe';
};
const defaultGetEntityTone = () => 'id';
const defaultHighlightKeyword = (text) => text;
</script>

