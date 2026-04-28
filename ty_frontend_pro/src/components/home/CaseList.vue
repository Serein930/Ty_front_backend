<template>
  <div class="panel" style="grid-column: 1; grid-row: 1;">
    <div class="panel-title"><span class="title-text">我的近期案件</span></div>
    <div class="controls">
      <select :value="statusFilter" @change="$emit('update:statusFilter', $event.target.value)">
        <option value="all">全部状态</option>
        <option value="待处理">待处理</option>
        <option value="正在研判">正在研判</option>
        <option value="已结案">已结案</option>
      </select>
    </div>
    <div class="warning-container">
      <div class="case-list">
        <CaseCard
          v-for="item in warnings"
          :key="item.id"
          :item="item"
          @click="$emit('show-detail', item)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import CaseCard from './CaseCard.vue';

defineProps({
  warnings: {
    type: Array,
    default: () => []
  },
  statusFilter: {
    type: String,
    default: 'all'
  }
});

defineEmits(['update:statusFilter', 'show-detail']);
</script>

