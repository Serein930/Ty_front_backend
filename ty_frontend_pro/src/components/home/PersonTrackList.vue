<template>
  <div class="panel" style="grid-column: 1; grid-row: 3;">
    <div class="panel-title" style="display:flex;justify-content:space-between;align-items:center;padding-right:15px;">
      <span class="title-text">重点人物追踪</span>
      <button class="view-all-btn" style="position:static;" @click="$emit('view-all')">查看全部</button>
    </div>
    <div class="controls">
      <select :value="selectedType" @change="$emit('update:selectedType', $event.target.value)">
        <option value="all">全部类别</option>
        <option value="black">黑灰产</option>
        <option value="fraud">诈骗</option>
        <option value="attack">攻击</option>
      </select>
    </div>
    <div class="hot-list active">
      <PersonCard
        v-for="p in persons"
        :key="p.id"
        :person="p"
        :avatar-initial="avatarInitial"
        :score-class="scoreClass"
        @card-click="$emit('show-detail', p)"
      />
    </div>
  </div>
</template>

<script setup>
import PersonCard from './PersonCard.vue';

defineProps({
  persons: {
    type: Array,
    default: () => []
  },
  selectedType: {
    type: String,
    default: 'all'
  },
  avatarInitial: {
    type: Function,
    default: (name) => name ? name.charAt(0).toUpperCase() : 'U'
  },
  scoreClass: {
    type: Function,
    default: (score) => {
      if (score >= 90) return 'critical';
      if (score >= 70) return 'high';
      return 'medium';
    }
  }
});

defineEmits(['update:selectedType', 'view-all', 'show-detail']);
</script>

