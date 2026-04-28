<template>
  <div class="panel ticker-panel" style="grid-column: 1 / 4; grid-row: 2;">
    <div class="ticker-left">
      <i class="fa-solid fa-satellite-dish"></i>
      <span class="ticker-title">重点监控节点</span>
    </div>
    <div class="monitored-entities-wrapper">
      <div class="monitored-entities-track">
        <div class="marquee-group" v-for="i in 2" :key="i">
          <div class="monitored-entity" v-for="m in entities" :key="`${i}-${m.id}`">
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
</template>

<script setup>
defineProps({
  entities: {
    type: Array,
    default: () => []
  },
  avatarInitial: {
    type: Function,
    default: (name) => name ? name.charAt(0).toUpperCase() : 'U'
  }
});
</script>

