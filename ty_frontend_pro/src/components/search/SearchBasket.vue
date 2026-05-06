<template>
  <div class="basket-actions">
    <button class="btn btn-small" @click="$emit('clear')">清空</button>
    <button class="btn btn-ai btn-small" @click="$emit('analyze')" :disabled="aiLoading">
      <i class="fa-solid fa-wand-magic-sparkles"></i>
      {{ aiLoading ? '分析中...' : '基于已选证据研判' }}
    </button>
  </div>

  <div v-if="basketItems.length === 0" class="empty-block">暂无已选线索</div>
  <div v-else class="basket-list">
    <div v-for="item in basketItems" :key="item.id" class="basket-item">
      <div class="basket-item-main" @click="$emit('open-detail', item)">
        <div class="basket-title" v-html="highlightKeyword(item.title, keyword)"></div>
        <div class="basket-meta">{{ item.viewType }} · {{ getRiskText(item.risk) }} · {{ item.region }}</div>
      </div>
      <button class="icon-btn" @click="$emit('remove', item.id)"><i class="fa-solid fa-trash"></i></button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  basketItems: {
    type: Array,
    default: () => []
  },
  keyword: {
    type: String,
    default: ''
  },
  aiLoading: {
    type: Boolean,
    default: false
  },
  highlightKeyword: {
    type: Function,
    default: (text) => text
  }
});

defineEmits(['clear', 'analyze', 'open-detail', 'remove']);

const getRiskText = (risk) => ({ high: '高危', mid: '中危', low: '低危' }[risk] || risk);
</script>

