<template>
  <article class="entity-card" @click="$emit('click')">
    <div class="person-card-head">
      <label class="person-pick" @click.stop>
        <input type="checkbox" :checked="isSelected" @change="$emit('toggle-basket')" />
      </label>

      <div class="person-main">
        <div class="person-title-row">
          <span class="person-icon"><i class="fa-solid fa-user-astronaut"></i></span>
          <strong class="person-title">{{ displayName }}</strong>
          <span class="risk-badge" :class="riskClass(item.risk)">{{ item.risk }}</span>
          <span class="topic-badge"># {{ item.topic }}</span>
        </div>

        <div class="person-desc" v-html="highlightKeyword(item.summary, keyword)"></div>

        <div class="person-alias-row">
          <button
            v-for="alias in aliases"
            :key="alias"
            class="person-alias-chip"
            @click.stop="$emit('drill-down', alias)"
          >
            <i class="fa-solid fa-user-tag"></i>
            Alias: {{ alias }}
          </button>
        </div>

        <div class="person-meta-row">
          <span class="meta-source"><i :class="getMediaIcon(item.media)"></i> {{ item.media }}</span>
          <span><i class="fa-regular fa-clock"></i> 最后活跃: {{ item.date }}</span>
          <span><i class="fa-solid fa-location-dot"></i> {{ item.region }}</span>
        </div>

        <div class="person-confidence-row">
          <span><i :class="getMediaIcon(item.media)"></i> {{ item.media }}</span>
          <span class="person-confidence-pill">置信度 {{ confidence }}%</span>
          <button class="entity-chip person-action-btn" @click.stop="$emit('toggle-basket')">
            <i class="fa-solid" :class="isSelected ? 'fa-circle-check' : 'fa-circle-plus'"></i>
            {{ isSelected ? '移出线索篮' : '加入线索篮' }}
          </button>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  keyword: {
    type: String,
    default: ''
  },
  displayName: {
    type: String,
    default: ''
  },
  aliases: {
    type: Array,
    default: () => []
  },
  confidence: {
    type: Number,
    default: 80
  },
  riskClass: {
    type: Function,
    default: (risk) => risk === '高危' ? 'high' : risk === '中危' ? 'mid' : 'low'
  },
  getMediaIcon: {
    type: Function,
    default: () => 'fa-solid fa-globe'
  },
  highlightKeyword: {
    type: Function,
    default: (text) => text
  }
});

defineEmits(['click', 'toggle-basket', 'drill-down']);
</script>

