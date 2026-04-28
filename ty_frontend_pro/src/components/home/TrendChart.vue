<template>
  <div class="panel" style="grid-column: 3; grid-row: 1;">
    <div class="panel-title"><span class="title-text">今日情报趋势</span></div>
    <div class="controls">
      <select :value="typeFilter" @change="$emit('update:typeFilter', $event.target.value)">
        <option value="all">请选择来源</option>
        <option value="black">黑灰产</option>
        <option value="fraud">诈骗</option>
        <option value="attack">攻击</option>
      </select>
      <select :value="rangeFilter" @change="$emit('update:rangeFilter', $event.target.value)">
        <option value="24">今天</option>
        <option value="12">12小时</option>
      </select>
    </div>
    <div ref="chartRef" id="trendChart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  typeFilter: {
    type: String,
    default: 'all'
  },
  rangeFilter: {
    type: String,
    default: '24'
  }
});

defineEmits(['update:typeFilter', 'update:rangeFilter']);

const chartRef = ref(null);
let chartInstance = null;

const buildOption = () => {
  const points = Number(props.rangeFilter);
  const x = Array.from({ length: points }, (_, i) => `${i}:00`);
  const base = props.typeFilter === 'all' ? 18 : props.typeFilter === 'black' ? 22 : props.typeFilter === 'fraud' ? 16 : 20;
  const data = x.map((_, i) => Math.max(3, Math.round(base + Math.sin(i / 2.7) * 6 + (i % 3) * 1.5)));

  return {
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: x,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#8c9db5', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#8c9db5', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.14)' } }
    },
    series: [
      {
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data,
        lineStyle: { width: 3, color: '#3b82f6' },
        itemStyle: { color: '#60a5fa' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59,130,246,0.35)' },
            { offset: 1, color: 'rgba(59,130,246,0.02)' }
          ])
        }
      }
    ]
  };
};

const updateChart = () => {
  if (chartInstance) {
    chartInstance.setOption(buildOption(), true);
  }
};

const handleResize = () => {
  chartInstance?.resize();
};

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    updateChart();
    window.addEventListener('resize', handleResize);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance?.dispose();
});

watch(() => [props.typeFilter, props.rangeFilter], updateChart);

defineExpose({
  resize: handleResize
});
</script>

