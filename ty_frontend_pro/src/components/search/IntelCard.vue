<template>
  <article
    class="entity-card"
    :class="{ 'intel-card-compact': compact, 'intel-card-selected': isSelected }"
    @click="$emit('click')"
  >
    <label v-if="showCheckbox" class="intel-pick" @click.stop>
      <input type="checkbox" :checked="isSelected" @change="$emit('toggle-basket')" />
    </label>

    <div class="intel-main">
      <div class="intel-title-row">
        <div class="intel-title-left">
          <span class="intel-icon"><i class="fa-solid fa-file-shield"></i></span>
          <strong class="intel-title">{{ displayTitle }}</strong>
        </div>
        <div class="intel-title-right">
          <span class="badge" :class="riskBadgeClass(item.risk)">{{ getRiskText(item.risk) }}</span>
          <span v-if="item.topic" class="topic-badge"># {{ item.topic }}</span>
          <span v-if="score !== undefined && score !== null" class="ai-source-score intel-relevance-badge">
            相关度: {{ (score * 100).toFixed(1) }}%
          </span>
        </div>
      </div>

      <div v-if="entities && entities.length > 0" class="intel-entity-row">
        <button
          v-for="ent in entities"
          :key="ent"
          class="intel-entity-chip"
          :class="`entity-${getEntityTone(ent)}`"
          @click.stop="$emit('drill-down', ent)"
        >
          <i class="fa-solid fa-tag"></i>
          {{ ent }}
        </button>
      </div>

      <div class="intel-desc" v-html="highlightKeyword(item.summary || item.content || '', keyword)"></div>

      <div class="intel-footer">
        <div class="intel-meta-row">
          <span class="meta-source">
            <i :class="getMediaIcon(item.media)"></i>
            {{ item.media }}
            <template v-if="channel"> / {{ channel }}</template>
          </span>
          <span><i class="fa-regular fa-clock"></i> {{ time || item.date }}</span>
          <span v-if="item.region"><i class="fa-solid fa-location-dot"></i> {{ item.region }}</span>
        </div>

        <div class="intel-footer-right">
          <button
            v-if="showBasketBtn"
            class="entity-chip intel-basket-btn"
            @click.stop="$emit('toggle-basket')"
          >
            <i class="fa-solid" :class="isSelected ? 'fa-circle-check' : 'fa-circle-plus'"></i>
            {{ isSelected ? '移出线索篮' : '加入线索篮' }}
          </button>

          <div v-if="stats && (stats.fwd !== undefined || stats.cmt !== undefined)" class="intel-social">
            <span v-if="stats.fwd !== undefined" class="intel-stats"><i class="fa-solid fa-share-nodes"></i> {{ stats.fwd }}</span>
            <span v-if="stats.cmt !== undefined" class="intel-stats"><i class="fa-solid fa-comment"></i> {{ stats.cmt }}</span>
          </div>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  keyword: {
    type: String,
    default: ''
  },
  displayTitle: {
    type: String,
    default: ''
  },
  channel: {
    type: String,
    default: ''
  },
  time: {
    type: String,
    default: ''
  },
  stats: {
    type: Object,
    default: () => ({ fwd: 0, cmt: 0 })
  },
  entities: {
    type: Array,
    default: () => []
  },
  /** AI 参考源相关度分数 (0-1)，用于展示检索匹配度 */
  score: {
    type: Number,
    default: undefined
  },
  /** 紧凑模式：用于 AI 参考源侧栏，缩减内边距和字体 */
  compact: {
    type: Boolean,
    default: false
  },
  /** 是否显示左侧勾选框 */
  showCheckbox: {
    type: Boolean,
    default: true
  },
  /** 是否显示「加入/移出线索篮」按钮 */
  showBasketBtn: {
    type: Boolean,
    default: true
  },
  riskClass: {
    type: Function,
    default: (risk) => risk === 'high' ? 'high' : risk === 'mid' ? 'mid' : 'low'
  },
  riskBadgeClass: {
    type: Function,
    default: (risk) => {
      // 归一化：中英文/大小写 → 颜色类
      if (risk === 'CRITICAL' || risk === 'CRITICALHIGH' || risk === 'HIGH'
        || risk === 'high' || risk === '高危') return 'badge-danger';
      if (risk === 'MEDIUM' || risk === 'mid' || risk === '中危') return 'badge-warning';
      if (risk === 'LOW' || risk === 'low' || risk === '低危') return 'badge-success';
      return 'badge-success';
    }
  },
  getMediaIcon: {
    type: Function,
    default: () => 'fa-solid fa-globe'
  },
  getEntityTone: {
    type: Function,
    default: () => 'id'
  },
  highlightKeyword: {
    type: Function,
    default: (text) => text
  }
});

defineEmits(['click', 'toggle-basket', 'drill-down']);

const getRiskText = (risk) => {
  // 后端返回的英文风险等级 → 中文映射
  const map = {
    'CRITICAL': '高危',
    'HIGH': '高危',
    'MEDIUM': '中危',
    'LOW': '低危',
    // 同时兼容已有的小写 key
    'high': '高危',
    'mid': '中危',
    'low': '低危'
  };
  return map[risk] || risk;
};
</script>

