<template>
  <div
    class="case-card"
    :class="`level-${item.level}`"
    @click="$emit('click', item)"
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
        <span class="case-meta-item">
          <i class="fa-regular fa-clock"></i>{{ item.time }}
        </span>
        <span class="case-meta-item">
          <i class="fa-solid fa-location-dot"></i>{{ item.country }}
        </span>
      </div>
      <span class="case-status-badge" :class="statusClass(item.status)">
        {{ item.status }}
      </span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  item: {
    type: Object,
    required: true
  }
});

defineEmits(['click']);

const statusClass = (status) => {
  const classes = {
    '待处理': 'pending',
    '正在研判': 'processing',
    '已结案': 'closed'
  };
  return classes[status] || '';
};
</script>

