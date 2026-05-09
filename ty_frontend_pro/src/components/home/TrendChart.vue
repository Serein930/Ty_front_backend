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

    <div class="chart-wrapper">
      <!-- 图表始终挂载，避免 v-if 销毁 DOM 导致 ECharts 实例丢失 -->
      <div ref="chartRef" id="trendChart"></div>

      <!-- Loading 遮罩 -->
      <div v-if="trendLoading" class="trend-loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <!-- Error 遮罩 -->
      <div v-else-if="trendError" class="trend-error">
        <span>{{ trendError }}</span>
        <button class="retry-btn" @click="$emit('retry')">重试</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  typeFilter: { type: String, default: 'all' },
  rangeFilter: { type: String, default: '24' },
  trendData: { type: Array, default: () => [] },
  trendLoading: { type: Boolean, default: false },
  trendError: { type: String, default: '' }
});

const emit = defineEmits(['update:typeFilter', 'update:rangeFilter', 'retry']);

const chartRef = ref(null);
let chartInstance = null;

const buildOption = () => {
  const hours = Number(props.rangeFilter);
  const x = Array.from({ length: hours }, (_, i) => `${i}:00`);
  const dataMap = {};
  (props.trendData || []).forEach(d => { dataMap[d.hour] = d.count; });
  const data = x.map((_, i) => dataMap[i] || 0);

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
  if (chartInstance && !chartInstance.isDisposed()) {
    chartInstance.setOption(buildOption(), true);
  }
};

const initChart = async () => {
  await nextTick();
  if (chartRef.value) {
    if (chartInstance) chartInstance.dispose();
    chartInstance = echarts.init(chartRef.value);
    updateChart();
  }
};

const handleResize = () => {
  chartInstance?.resize();
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance?.dispose();
});

// 切换时间范围时 X 轴点数变化，需重建 chart
watch(() => props.rangeFilter, () => {
  initChart();
});

// 数据或类型筛选变化时更新
watch(() => [props.typeFilter, props.trendData], () => {
  updateChart();
});

// loading 结束后数据到达，确保 chart 已初始化
watch(() => props.trendLoading, (loading, wasLoading) => {
  if (!loading && wasLoading && props.trendData.length) {
    initChart();
  }
});
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  height: calc(100% - 40px);
}
#trendChart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
.trend-loading,
.trend-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(8, 20, 40, 0.85);
  z-index: 2;
  border-radius: 4px;
}
.trend-loading {
  color: #8c9db5;
  font-size: 13px;
  gap: 10px;
}
.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2px solid rgba(59,130,246,0.25);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.trend-error {
  color: #ff6b6b;
  font-size: 13px;
  gap: 10px;
}
.retry-btn {
  background: transparent;
  border: 1px solid rgba(255,107,107,0.5);
  color: #ff6b6b;
  padding: 4px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.retry-btn:hover {
  background: rgba(255,107,107,0.1);
}
</style>
