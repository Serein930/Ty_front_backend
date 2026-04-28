<template>
  <header class="top-header">
    <div class="logo-area">
      <i class="fa-solid fa-shield-halved"></i> 天眼情报
    </div>
    <nav class="nav-menu">
      <a href="#" class="nav-item active"><i class="fa-regular fa-chart-bar"></i> 态势感知</a>
      <a href="#" class="nav-item" @click.prevent="$emit('navigate', '/search')"><i class="fa-solid fa-magnifying-glass"></i> 情报检索</a>
      <a href="#" class="nav-item" @click.prevent="$emit('navigate', '/dashboard')"><i class="fa-solid fa-circle-exclamation"></i> 监测预警</a>
      <a href="#" class="nav-item" @click.prevent="$emit('navigate', '/topology')"><i class="fa-solid fa-share-nodes"></i> 取证溯源</a>
    </nav>
    <div class="header-right">
      <span>administrator, 欢迎您!</span>
      <span class="time-display">{{ nowTime }} UTC</span>
      <div class="view-selector-wrapper">
        <i class="fa-solid fa-satellite-dish"></i>
        <select :value="selectedSubscription" class="view-select" @change="$emit('update:subscription', $event.target.value)">
          <option v-for="s in subscriptions" :key="s.name" :value="s.name">{{ s.name }}</option>
        </select>
      </div>
      <div class="btn-logout" @click="$emit('logout')"><i class="fa-solid fa-power-off"></i> 退出</div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  nowTime: {
    type: String,
    default: ''
  },
  selectedSubscription: {
    type: String,
    default: ''
  },
  subscriptions: {
    type: Array,
    default: () => []
  }
});

defineEmits(['navigate', 'logout', 'update:subscription']);
</script>

