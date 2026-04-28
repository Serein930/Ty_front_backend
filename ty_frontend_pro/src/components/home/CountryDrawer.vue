<template>
  <div id="countryDrawer" class="country-drawer" :class="{ active: visible }">
    <div class="drawer-header">
      <div class="drawer-title"><i class="fa-solid fa-earth-americas"></i> {{ country }} 档案</div>
      <button class="drawer-close" @click="$emit('close')">&times;</button>
    </div>
    <div class="drawer-body">
      <div class="drawer-stat-grid">
        <div class="drawer-stat-card">
          <div class="drawer-stat-val">{{ threat }}</div>
          <div class="drawer-stat-label">风险评分</div>
        </div>
        <div class="drawer-stat-card" style="background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.2);">
          <div class="drawer-stat-val">{{ count }}</div>
          <div class="drawer-stat-label">近7天情报</div>
        </div>
      </div>

      <div class="drawer-section-title">
        <span>重点关注人物 (TOP5)</span>
        <button class="btn-action" @click="$emit('show-persons', country)">查看全部</button>
      </div>
      <div class="drawer-person-list">
        <div class="drawer-person-card" v-for="p in persons" :key="p.id" @click="$emit('show-person', p)">
          <div class="drawer-person-avatar"><img :src="p.avatar" alt="avatar" /></div>
          <div class="drawer-person-info">
            <div class="drawer-person-name">{{ p.alias }} <span class="p-score-badge" :class="scoreClass(p.score)">P{{ p.score }}</span></div>
            <div class="drawer-person-desc">{{ p.desc }}</div>
          </div>
        </div>
      </div>

      <div class="drawer-section-title">
        <span>近期重要事件</span>
        <button class="btn-action" @click="$emit('show-events', country)">查看全部</button>
      </div>
      <div class="drawer-event-list">
        <div class="drawer-event-item" v-for="e in events" :key="e.id" @click="$emit('show-event', e)">
          <div class="drawer-event-title">{{ e.name }}</div>
          <div class="drawer-event-meta"><span>{{ e.time }}</span><span>{{ e.level }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  country: {
    type: String,
    default: '全球'
  },
  threat: {
    type: [String, Number],
    default: 'N/A'
  },
  count: {
    type: Number,
    default: 0
  },
  persons: {
    type: Array,
    default: () => []
  },
  events: {
    type: Array,
    default: () => []
  },
  scoreClass: {
    type: Function,
    default: (score) => {
      if (score >= 90) return 'p-score-critical';
      if (score >= 75) return 'p-score-high';
      if (score >= 50) return 'p-score-medium';
      return 'p-score-low';
    }
  }
});

defineEmits(['close', 'show-persons', 'show-events', 'show-person', 'show-event']);
</script>

