<template>
  <div id="detailModal" class="modal-overlay" v-show="visible" @click.self="$emit('close')">
    <div class="modal-content" :style="mode === 'person' ? 'max-width: 1400px; min-height: 680px;' : 'max-width: 900px; min-height: 500px;'">
      <div class="modal-header">
        <div class="modal-title">{{ title }}</div>
        <button class="modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="mode === 'person' && person" class="person-detail-layout">
          <div class="person-detail-head">
            <div class="person-detail-avatar">{{ avatarInitial(person.alias) }}</div>
            <div class="person-detail-main">
              <div class="person-detail-name-row">
                <span class="person-detail-name">{{ person.alias }}</span>
                <span class="person-badge high">高危目标</span>
                <span class="p-score-badge" :class="scoreClass(person.score)">P-{{ person.score }}</span>
                <span class="conf-badge">{{ person.confidence }}% 综合置信度</span>
              </div>
              <div class="person-detail-meta">物理侧写: {{ person.city }} / {{ person.country }}</div>
              <div class="person-detail-desc">{{ person.desc }}</div>
            </div>
          </div>

          <div class="person-asset-row">
            <div class="asset-group">
              <div class="asset-title">虚拟身份与映射</div>
              <div class="asset-tags">
                <span class="asset-tag" v-for="tag in person.assets?.identities || []" :key="tag">
                  <i class="fa-solid fa-user"></i>{{ tag }}
                </span>
              </div>
            </div>
            <div class="asset-group">
              <div class="asset-title">通讯资产 (Comm Assets)</div>
              <div class="asset-tags">
                <span class="asset-tag" v-for="tag in person.assets?.comms || []" :key="tag">
                  <i class="fa-solid fa-envelope"></i>{{ tag }}
                </span>
              </div>
            </div>
            <div class="asset-group">
              <div class="asset-title">资金资产 (Financial Assets)</div>
              <div class="asset-tags">
                <span class="asset-tag" v-for="tag in person.assets?.finance || []" :key="tag">
                  <i class="fa-solid fa-wallet"></i>{{ tag }}
                </span>
              </div>
            </div>
            <div class="asset-group">
              <div class="asset-title">网络足迹 (Network Footprints)</div>
              <div class="asset-tags">
                <span class="asset-tag" v-for="tag in person.assets?.network || []" :key="tag">
                  <i class="fa-solid fa-globe"></i>{{ tag }}
                </span>
              </div>
            </div>
            <div class="asset-group">
              <div class="asset-title">历史关联案件 (Cases)</div>
              <div class="asset-tags">
                <span class="asset-tag" v-for="tag in person.assets?.cases || []" :key="tag">
                  <i class="fa-solid fa-link"></i>{{ tag }}
                </span>
              </div>
            </div>
          </div>

          <div class="person-chart-row">
            <div class="person-chart-card">
              <div class="person-chart-title">目标综合威胁指数 (Threat Index)</div>
              <div :id="`personRadar-${person.id}`" class="person-chart"></div>
            </div>
            <div class="person-chart-card">
              <div class="person-chart-title">全网行为活跃热力图 (UTC)</div>
              <div :id="`personHeat-${person.id}`" class="person-chart"></div>
            </div>
            <div class="person-chart-card">
              <div class="person-chart-title">目标核心关系图谱</div>
              <div :id="`personGraph-${person.id}`" class="person-chart"></div>
            </div>
          </div>

          <div class="person-detail-actions">
            <button class="btn-dash3 danger"><i class="fa-solid fa-circle-xmark"></i> 下发布控</button>
            <button class="btn-dash3 primary" @click="$emit('clone', person)"><i class="fa-solid fa-robot"></i> 生成数字身份</button>
            <button class="btn-dash3 success"><i class="fa-solid fa-download"></i> 导出画像简报</button>
          </div>
        </div>
        <div v-else class="detail-content-card" v-html="htmlContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '详情'
  },
  mode: {
    type: String,
    default: 'generic'
  },
  person: {
    type: Object,
    default: null
  },
  htmlContent: {
    type: String,
    default: ''
  },
  avatarInitial: {
    type: Function,
    default: (name) => name ? name.charAt(0).toUpperCase() : 'U'
  },
  scoreClass: {
    type: Function,
    default: (score) => {
      if (score >= 90) return 'p-score-critical';
      if (score >= 75) return 'p-score-high';
      if (score >= 50) return 'p-score-medium';
      return 'p-score-low';
    }
  }
});

defineEmits(['close', 'clone']);

const chartInstances = [];

const initCharts = (person) => {
  disposeCharts();
  const radarEl = document.getElementById(`personRadar-${person.id}`);
  const heatEl = document.getElementById(`personHeat-${person.id}`);
  const graphEl = document.getElementById(`personGraph-${person.id}`);
  if (!radarEl || !heatEl || !graphEl) return;

  const radar = echarts.init(radarEl);
  radar.setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator: [
        { name: '影响力', max: 100 },
        { name: '活跃度', max: 100 },
        { name: '隐蔽性', max: 100 },
        { name: '关联度', max: 100 },
        { name: '破坏性', max: 100 }
      ],
      axisName: { color: '#9fb6da' },
      splitLine: { lineStyle: { color: 'rgba(105,144,201,0.22)' } },
      splitArea: { areaStyle: { color: ['rgba(22,44,78,0.22)', 'rgba(13,30,56,0.08)'] } }
    },
    series: [{
      type: 'radar',
      data: [{ value: [person.score, 82, 76, 88, 91], areaStyle: { color: 'rgba(37,99,235,0.28)' }, lineStyle: { color: '#3b82f6' }, itemStyle: { color: '#60a5fa' } }]
    }]
  });

  const heat = echarts.init(heatEl);
  const heatData = [];
  for (let d = 0; d < 7; d += 1) {
    for (let h = 0; h < 24; h += 1) {
      heatData.push([h, d, Math.round(20 + Math.abs(Math.sin((h + d) / 4) * 60))]);
    }
  }
  heat.setOption({
    grid: { left: 36, right: 12, top: 20, bottom: 28 },
    xAxis: { type: 'category', data: Array.from({ length: 24 }, (_, i) => `${i}`), axisLabel: { color: '#8fa7cc', fontSize: 10 }, axisLine: { lineStyle: { color: '#2d4f7f' } } },
    yAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'], axisLabel: { color: '#8fa7cc', fontSize: 10 }, axisLine: { lineStyle: { color: '#2d4f7f' } } },
    visualMap: { min: 0, max: 100, show: false, inRange: { color: ['#0b1b3c', '#1d4ed8', '#22d3ee'] } },
    series: [{ type: 'heatmap', data: heatData }]
  });

  const graph = echarts.init(graphEl);
  graph.setOption({
    backgroundColor: 'transparent',
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      force: { repulsion: 180, edgeLength: [50, 110] },
      label: { show: true, color: '#d9e6ff', fontSize: 10 },
      lineStyle: { color: 'rgba(96,165,250,0.45)' },
      data: [
        { name: person.alias, symbolSize: 46, itemStyle: { color: '#f97316' } },
        { name: '钱包簇', symbolSize: 30, itemStyle: { color: '#3b82f6' } },
        { name: '中继节点', symbolSize: 26, itemStyle: { color: '#06b6d4' } },
        { name: '通信账号', symbolSize: 28, itemStyle: { color: '#10b981' } },
        { name: '关联案件', symbolSize: 32, itemStyle: { color: '#ef4444' } }
      ],
      links: [
        { source: person.alias, target: '钱包簇' },
        { source: person.alias, target: '中继节点' },
        { source: person.alias, target: '通信账号' },
        { source: person.alias, target: '关联案件' },
        { source: '通信账号', target: '中继节点' }
      ]
    }]
  });

  chartInstances.push(radar, heat, graph);
};

const disposeCharts = () => {
  while (chartInstances.length) {
    const chart = chartInstances.pop();
    chart?.dispose();
  }
};

watch(() => props.visible, (newVal) => {
  if (newVal && props.mode === 'person' && props.person) {
    nextTick(() => initCharts(props.person));
  }
});

onBeforeUnmount(() => {
  disposeCharts();
});
</script>

