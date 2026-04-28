<template>
  <div class="filter-block">
    <div class="filter-title">时间快捷筛选</div>
    <div class="chips-wrap">
      <button
        v-for="opt in quickTimeOptions"
        :key="opt.value"
        class="chip"
        :class="{ active: quickTime === opt.value }"
        @click="$emit('update:quickTime', opt.value)"
      >{{ opt.label }}</button>
    </div>
  </div>

  <div class="filter-block">
    <div class="filter-title">地区</div>
    <select v-model="region" class="control-input full" @change="$emit('update:region', $event.target.value)">
      <option value="all">全部地区</option>
      <option v-for="r in regionOptions" :key="r" :value="r">{{ r }}</option>
    </select>
  </div>

  <div class="filter-block">
    <div class="filter-title">风险评估</div>
    <div class="chips-wrap">
      <button
        v-for="risk in riskOptions"
        :key="risk"
        class="chip"
        :class="{ active: riskSet.includes(risk) }"
        @click="toggleFilter('riskSet', risk)"
      >{{ risk }}</button>
    </div>
  </div>

  <div class="filter-block">
    <div class="filter-title">媒介分布</div>
    <div class="chips-wrap">
      <button
        v-for="media in mediaOptions"
        :key="media"
        class="chip"
        :class="{ active: mediaSet.includes(media) }"
        @click="toggleFilter('mediaSet', media)"
      >{{ media }}</button>
    </div>
  </div>

  <div class="filter-block">
    <div class="filter-title">话题分类</div>
    <div class="chips-wrap topic-row">
      <button
        v-for="topic in topicOptions"
        :key="topic"
        class="chip"
        :class="{ active: topicSet.includes(topic) }"
        @click="toggleFilter('topicSet', topic)"
      >{{ topic }}</button>
    </div>
  </div>

  <div class="divider-line"></div>

  <div class="rank-module">
    <div class="module-title">地区分布排行</div>
    <div v-if="regionRank.length === 0" class="empty-block">暂无数据</div>
    <div v-else>
      <div
        v-for="(row, idx) in regionRank"
        :key="row.name"
        class="rank-row clickable"
        :class="{ active: region === row.name }"
        @click="applyRegionFilter(row.name)"
      >
        <span class="rank-num">{{ idx + 1 }}</span>
        <span class="rank-name">{{ row.name }}</span>
        <div class="progress-wrap"><div class="progress-bar" :style="{ width: `${row.percent}%` }"></div></div>
        <span class="rank-value">{{ row.count }}</span>
      </div>
    </div>
  </div>

  <div class="rank-module">
    <div class="module-title">命中规则 Top5</div>
    <div v-if="ruleTop5.length === 0" class="empty-block">暂无数据</div>
    <div v-else>
      <div
        v-for="(row, idx) in ruleTop5"
        :key="row.name"
        class="rank-row clickable"
        :class="{ active: selectedRule === row.name }"
        @click="applyRuleFilter(row.name)"
      >
        <span class="rank-num">{{ idx + 1 }}</span>
        <span class="rank-name">{{ row.name }}</span>
        <div class="progress-wrap"><div class="progress-bar warning" :style="{ width: `${row.percent}%` }"></div></div>
        <span class="rank-value">{{ row.count }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  quickTime: {
    type: String,
    default: 'all'
  },
  region: {
    type: String,
    default: 'all'
  },
  riskSet: {
    type: Array,
    default: () => []
  },
  mediaSet: {
    type: Array,
    default: () => []
  },
  topicSet: {
    type: Array,
    default: () => []
  },
  selectedRule: {
    type: String,
    default: 'all'
  },
  quickTimeOptions: {
    type: Array,
    default: () => []
  },
  riskOptions: {
    type: Array,
    default: () => []
  },
  mediaOptions: {
    type: Array,
    default: () => []
  },
  topicOptions: {
    type: Array,
    default: () => []
  },
  regionOptions: {
    type: Array,
    default: () => []
  },
  regionRank: {
    type: Array,
    default: () => []
  },
  ruleTop5: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits([
  'update:quickTime',
  'update:region',
  'update:riskSet',
  'update:mediaSet',
  'update:topicSet',
  'update:selectedRule'
]);

const toggleFilter = (field, value) => {
  emit(`update:${field}`, value);
};

const applyRegionFilter = (regionName) => {
  emit('update:region', regionName);
};

const applyRuleFilter = (ruleName) => {
  emit('update:selectedRule', ruleName);
};
</script>

