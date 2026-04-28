<template>
  <div class="panel" style="grid-column: 2; grid-row: 1;">
    <div class="panel-title"><span class="title-text">主题情报总量</span></div>
    <div class="controls" style="left:auto;right:15px;">
      <select :value="selectedType" @change="$emit('update:selectedType', $event.target.value)">
        <option value="all">请选择类别</option>
        <option value="black">黑灰产</option>
        <option value="fraud">诈骗</option>
        <option value="attack">攻击</option>
      </select>
      <select :value="timeFilter" @change="$emit('update:timeFilter', $event.target.value)">
        <option value="24h">请选择时间</option>
        <option value="7d">近7天</option>
        <option value="30d">近30天</option>
      </select>
    </div>
    <div class="center-stats">
      <div class="circle-stat">
        <div class="stat-num">{{ warningCount }}</div>
        <div class="stat-label">待处理</div>
      </div>
      <div class="main-stat">
        <div class="main-title">当前监测总数</div>
        <div class="main-num">{{ totalCount }}</div>
        <div class="main-time">{{ nowTimeDisplay }}</div>
      </div>
      <div class="circle-stat">
        <div class="stat-num">{{ handledCount }}</div>
        <div class="stat-label">已处置</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  warningCount: {
    type: Number,
    default: 0
  },
  handledCount: {
    type: Number,
    default: 0
  },
  totalCount: {
    type: Number,
    default: 0
  },
  nowTimeDisplay: {
    type: String,
    default: ''
  },
  selectedType: {
    type: String,
    default: 'all'
  },
  timeFilter: {
    type: String,
    default: '24h'
  }
});

defineEmits(['update:selectedType', 'update:timeFilter']);
</script>

