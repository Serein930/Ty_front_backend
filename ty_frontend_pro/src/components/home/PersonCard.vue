<template>
  <div
    class="target-card"
    :class="{ 'level-critical': person.score >= 90 }"
    @click.stop="$emit('card-click', person)"
  >
    <div class="target-avatar-wrapper">
      <div class="avatar-fallback">{{ avatarInitial(person.alias) }}</div>
      <span class="target-status" :class="person.score >= 90 ? 'danger' : ''"></span>
    </div>
    <div class="target-info">
      <div class="target-header">
        <div class="target-alias">
          <i class="fa-solid fa-user-secret"></i> {{ person.alias }}
        </div>
        <div class="target-city">
          <i class="fa-solid fa-crosshairs"></i> {{ person.city }}
        </div>
      </div>
      <div class="target-loc">{{ person.summary || '疑似涉及大规模洗钱活动的核心人员。近期频繁跨平台活跃。' }}</div>
      <div class="target-desc">{{ person.desc }}</div>
      <div class="target-tags">
        <span class="target-tag" v-for="tag in person.tags" :key="tag">{{ tag }}</span>
      </div>
      <div class="target-threat-box">
        <span class="p-score-badge" :class="scoreClass(person.score)">P-{{ person.score }}</span>
        <span class="conf-badge">{{ person.confidence }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  person: {
    type: Object,
    required: true
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

defineEmits(['card-click']);
</script>

