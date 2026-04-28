<template>
  <article class="entity-card" @click="$emit('click')">
    <div class="intel-card-head">
      <label class="intel-pick" @click.stop>
        <input type="checkbox" :checked="isSelected" @change="$emit('toggle-basket')" />
      </label>

      <div class="intel-main">
        <div class="intel-title-row">
          <span class="intel-icon"><i class="fa-solid fa-file-shield"></i></span>
          <strong class="intel-title">{{ displayTitle }}</strong>
          <span class="risk-badge" :class="riskClass(item.risk)">{{ item.risk }}</span>
          <span class="topic-badge"># {{ item.topic }}</span>
        </div>

        <div class="intel-desc" v-html="highlightKeyword(item.summary, keyword)"></div>

        <div class="intel-entity-row">
          <button
            v-for="ent in entities"
            :key="ent"
            class="intel-entity-chip"
            :class="`tone-${getEntityTone(ent)}`"
            @click.stop="$emit('drill-down', ent)"
          >
            <i class="fa-solid fa-tag"></i>
            {{ ent }}
          </button>
        </div>

        <div class="intel-footer">
          <div class="intel-meta-row">
            <span class="meta-source"><i :class="getMediaIcon(item.media)"></i> {{ item.media }} / {{ channel }}</span>
            <span><i class="fa-regular fa-clock"></i> {{ time }}</span>
            <span><i class="fa-solid fa-location-dot"></i> {{ item.region }}</span>
            <button class="entity-chip intel-basket-btn" @click.stop="$emit('toggle-basket')">
              <i class="fa-solid" :class="isSelected ? 'fa-circle-check' : 'fa-circle-plus'"></i>
              {{ isSelected ? '移出线索篮' : '加入线索篮' }}
            </button>
          </div>

          <div class="intel-social">
            <span class="intel-stats"><i class="fa-solid fa-share-nodes"></i> {{ stats.fwd }}</span>
            <span class="intel-stats"><i class="fa-solid fa-comment"></i> {{ stats.cmt }}</span>
          </div>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
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
  displayTitle: {
    type: String,
    default: ''
  },
  channel: {
    type: String,
    default: ''
  },
  time: {
    type: String,
    default: ''
  },
  stats: {
    type: Object,
    default: () => ({ fwd: 0, cmt: 0 })
  },
  entities: {
    type: Array,
    default: () => []
  },
  riskClass: {
    type: Function,
    default: (risk) => risk === '高危' ? 'high' : risk === '中危' ? 'mid' : 'low'
  },
  getMediaIcon: {
    type: Function,
    default: () => 'fa-solid fa-globe'
  },
  getEntityTone: {
    type: Function,
    default: () => 'id'
  },
  highlightKeyword: {
    type: Function,
    default: (text) => text
  }
});

defineEmits(['click', 'toggle-basket', 'drill-down']);
</script>

