<template>
  <aside class="analysis-sidebar" :class="{ 'collapsed': collapsed }">
    <div class="analysis-header">
      <div class="time-tabs">
        <div class="time-tab" :class="{ active: filters.time === 'today' }" @click="setTime('today')">24H</div>
        <div class="time-tab" :class="{ active: filters.time === '7days' }" @click="setTime('7days')">7天</div>
        <div class="time-tab" :class="{ active: filters.time === '30days' }" @click="setTime('30days')">30天</div>
        <div class="time-tab" :class="{ active: filters.time === 'all' }" @click="setTime('all')">全部</div>
      </div>
      <i class="fa-regular fa-calendar-days text-gray-400"></i>
    </div>

    <select class="region-select" :value="filters.region" @change="setFilter('region', $event.target.value)">
      <option value="all">所有地区</option>
      <option v-for="r in availableRegions" :key="r" :value="r">{{ r }}</option>
    </select>

    <!-- 地区分布 -->
    <div>
      <div class="module-title"><i class="fa-solid fa-location-dot"></i> 地区分布</div>
      <div class="region-rank-container">
        <div class="region-rank-wrapper">
          <div class="region-rank-slide" :style="{ transform: `translateY(-${carousel.region * 180}px)` }">
            <div v-for="(region, index) in topRegions" :key="region.name"
                 class="rank-item"
                 :class="{ active: filters.region === region.name }"
                 @click="$emit('filter', 'region', region.name)">
              <div class="rank-num">{{ index + 1 < 10 ? '0' + (index + 1) : index + 1 }}</div>
              <div class="rank-name" style="color:var(--text-main); font-size:12px; min-width:60px;">{{ region.name }}</div>
              <div class="progress-bg">
                <div class="progress-bar" :style="{ width: region.percent + '%', background: getRegionColor(index) }"></div>
              </div>
              <span style="font-size:11px; color:var(--text-dim); margin-left:5px;">{{ region.count }}</span>
            </div>
          </div>
        </div>
        <div class="carousel-arrow prev" @click="prevRegion"><i class="fa-solid fa-chevron-left"></i></div>
        <div class="carousel-arrow next" @click="nextRegion"><i class="fa-solid fa-chevron-right"></i></div>
      </div>
    </div>

    <!-- 命中规则 -->
    <div>
      <div class="module-title"><i class="fa-solid fa-filter"></i> 命中规则 Top 5</div>
      <div class="region-rank-container" style="height: auto;">
        <div v-for="(rule, index) in topRules" :key="rule.name"
             class="rank-item"
             :class="{ active: filters.rule === rule.name }"
             @click="$emit('filter', 'rule', rule.name)"
             style="margin-bottom: 12px;">
          <div class="rank-num" style="background: rgba(59,130,246,0.2); border-color: var(--accent-blue);">{{ index + 1 }}</div>
          <div style="flex:1; display:flex; flex-direction:column; gap:4px;">
            <div style="display:flex; justify-content:space-between; font-size:12px;">
              <span style="color:var(--text-main);">{{ getRuleName(rule.name) }}</span>
              <span style="color:var(--text-dim)">{{ rule.count }}</span>
            </div>
            <div class="progress-bg" style="height:4px;">
              <div class="progress-bar" :style="{ width: rule.percent + '%', background: 'var(--accent-orange)' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 话题分布 -->
    <div>
      <div class="module-title"><i class="fa-regular fa-comment-dots"></i> 话题过滤</div>
      <div class="chart-container">
        <div class="donut-chart" :style="{ background: topicChartData.background }">
          <div class="donut-inner">
            <span class="donut-label">{{ topicChartData.total }}</span>
            <span class="donut-sub">Total</span>
          </div>
        </div>
      </div>
      <div class="chart-legend">
        <div v-for="item in topicChartData.legend" :key="item.key"
             class="legend-item"
             :class="{ active: filters.topic === item.key }"
             @click="$emit('filter', 'topic', item.key)">
          <div class="legend-dot" :style="{ background: item.color }"></div> {{ item.name }} ({{ item.count }})
        </div>
      </div>
    </div>

    <!-- 行业分布 -->
    <div>
      <div class="module-title"><i class="fa-solid fa-tag"></i> 行业分布</div>
      <div class="chart-container">
        <div class="donut-chart" :style="{ background: industryChartData.background }">
          <div class="donut-inner">
            <span class="donut-label">{{ industryChartData.total }}</span>
            <span class="donut-sub">Ind</span>
          </div>
        </div>
      </div>
      <div class="chart-legend">
        <div v-for="item in industryChartData.legend" :key="item.key"
             class="legend-item"
             :class="{ active: filters.industry === item.key }"
             @click="$emit('filter', 'industry', item.key)">
          <div class="legend-dot" :style="{ background: item.color }"></div> {{ item.name }} ({{ item.count }})
        </div>
      </div>
    </div>

    <!-- 作者统计 -->
    <div>
      <div class="module-title"><i class="fa-solid fa-user-pen"></i> 作者统计</div>
      <div class="author-list-container">
        <div class="author-list-wrapper">
          <div class="author-list-slide" :style="{ transform: `translateY(-${carousel.author * 230}px)` }">
            <div v-for="(author, index) in topAuthors" :key="author.name"
                 class="author-list-item"
                 :class="{ active: filters.author === author.name }"
                 @click="$emit('filter', 'author', author.name)">
              <div class="author-rank-num">{{ index + 1 }}</div>
              <div class="author-name">{{ author.name }}</div>
              <div class="author-count">{{ author.count }}<span class="author-count-unit">条</span></div>
            </div>
          </div>
        </div>
        <div class="carousel-arrow prev" @click="prevAuthor"><i class="fa-solid fa-chevron-left"></i></div>
        <div class="carousel-arrow next" @click="nextAuthor"><i class="fa-solid fa-chevron-right"></i></div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { reactive, computed } from 'vue';

const props = defineProps({
  filters: {
    type: Object,
    required: true
  },
  collapsed: {
    type: Boolean,
    default: false
  },
  availableRegions: {
    type: Array,
    default: () => []
  },
  topRegions: {
    type: Array,
    default: () => []
  },
  topRules: {
    type: Array,
    default: () => []
  },
  topAuthors: {
    type: Array,
    default: () => []
  },
  topicChartData: {
    type: Object,
    default: () => ({ total: 0, background: '', legend: [] })
  },
  industryChartData: {
    type: Object,
    default: () => ({ total: 0, background: '', legend: [] })
  },
  getRuleName: {
    type: Function,
    default: (r) => r
  }
});

const emit = defineEmits(['update:filters', 'filter']);

const carousel = reactive({
  region: 0,
  author: 0
});

const setTime = (value) => {
  emit('update:filters', { ...props.filters, time: value });
};

const setFilter = (key, value) => {
  emit('update:filters', { ...props.filters, [key]: value });
};

const getRegionColor = (index) => {
  const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#14b8a6'];
  return colors[index % colors.length];
};

const prevRegion = () => {
  if (carousel.region > 0) carousel.region--;
};

const nextRegion = () => {
  const maxSlide = Math.max(0, Math.ceil(props.topRegions.length / 5) - 1);
  if (carousel.region < maxSlide) carousel.region++;
};

const prevAuthor = () => {
  if (carousel.author > 0) carousel.author--;
};

const nextAuthor = () => {
  const maxSlide = Math.max(0, Math.ceil(props.topAuthors.length / 5) - 1);
  if (carousel.author < maxSlide) carousel.author++;
};
</script>

