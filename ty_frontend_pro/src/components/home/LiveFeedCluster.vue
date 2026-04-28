<template>
  <div class="panel" style="grid-column: 3; grid-row: 3;">
    <div class="panel-title" style="display:flex;justify-content:space-between;align-items:center;padding-right:15px;">
      <span class="title-text">实时情报事件簇</span>
      <button class="view-all-btn" style="position:static;" @click="$emit('view-all')">事件列表</button>
    </div>
    <div class="controls" style="left:auto;right:15px;gap:8px;">
      <span class="live-pill live-pill-danger"><i class="fa-solid fa-signal"></i> 智能归并中</span>
      <span class="live-pill"><i class="fa-solid fa-shield-halved"></i> 自动降噪</span>
    </div>
    <div id="sourceChart">
      <div class="live-feed-shell">
        <div class="live-feed-timeline">
          <div class="live-feed-scroll">
            <div class="live-feed-track" :style="{ '--scroll-distance': `${scrollDistance}px` }">
              <div class="live-feed-item" v-for="f in doubledFeed" :key="f.uid" @click="$emit('show-detail', f)">
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
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  feed: {
    type: Array,
    default: () => []
  }
});

defineEmits(['view-all', 'show-detail']);

const doubledFeed = computed(() => {
  const base = props.feed.map((item, idx) => ({ ...item, uid: `a-${item.id}-${idx}` }));
  const clone = props.feed.map((item, idx) => ({ ...item, uid: `b-${item.id}-${idx}` }));
  return [...base, ...clone];
});

const scrollDistance = computed(() => Math.max(props.feed.length * 158, 320));

const levelText = (level) => {
  if (level === 'critical') return '高危';
  if (level === 'high') return '关注';
  if (level === 'medium') return '追踪';
  return '低危';
};
</script>

