<template>
  <div class="panel" style="grid-column: 2; grid-row: 3;">
    <div class="panel-title" style="justify-content:space-between;padding-right:15px;gap:15px;">
      <div class="title-text">态势地图</div>
      <div class="pill-tabs-container">
        <div
          class="pill-tab"
          :class="{ active: scene === 'global' }"
          @click="changeScene('global')"
        >全球态势</div>
        <div
          class="pill-tab"
          :class="{ active: scene === 'black' }"
          @click="changeScene('black')"
        >黑产网络</div>
        <div
          class="pill-tab"
          :class="{ active: scene === 'leak' }"
          @click="changeScene('leak')"
        >数据泄露</div>
        <div
          class="pill-tab"
          :class="{ active: scene === 'terror' }"
          @click="changeScene('terror')"
        >暴恐分布</div>
        <div
          class="pill-tab"
          :class="{ active: scene === 'smuggle' }"
          @click="changeScene('smuggle')"
        >走私链路</div>
        <div
          class="pill-tab"
          :class="{ active: scene === 'drug' }"
          @click="changeScene('drug')"
        >毒品流向</div>
      </div>
    </div>
    <div class="map-controls">
      <button id="btnBackWorld" class="view-all-btn" v-show="mode === 'china'" @click="changeMode('world')">
        <i class="fa-solid fa-earth-asia"></i> 返回全球
      </button>
    </div>
    <div ref="chartRef" id="mapChart" v-show="!fallback"></div>
    <div v-show="fallback" class="map-fallback">
      <div class="map-fallback-grid"></div>
      <div class="map-fallback-line line-a"></div>
      <div class="map-fallback-line line-b"></div>
      <div class="map-fallback-line line-c"></div>
      <div class="map-fallback-node node-cn">中国</div>
      <div class="map-fallback-node node-us">美国</div>
      <div class="map-fallback-node node-jp">日本</div>
      <div class="map-fallback-node node-sg">新加坡</div>
      <div class="map-fallback-tip">地图底图离线模式</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  scene: {
    type: String,
    default: 'global'
  },
  mode: {
    type: String,
    default: 'world'
  },
  warnings: {
    type: Array,
    default: () => []
  },
  countryCoordinates: {
    type: Object,
    default: () => ({
      中国: [116.4074, 39.9042],
      美国: [-95.7129, 37.0902],
      日本: [139.6917, 35.6895],
      新加坡: [103.8198, 1.3521]
    })
  },
  selectedSubscription: {
    type: String,
    default: ''
  },
  subscriptions: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:scene', 'update:mode', 'country-click', 'context-menu']);

const chartRef = ref(null);
const fallback = ref(false);
let chartInstance = null;

const worldNodeMap = {
  usWest: { name: '美国西岸', value: [-122.4194, 37.7749, 92], color: '#22d3ee' },
  usEast: { name: '美国东岸', value: [-74.006, 40.7128, 88], color: '#a855f7' },
  ru: { name: '东欧节点', value: [37.6173, 55.7558, 95], color: '#ef4444' },
  me: { name: '中东节点', value: [46.6753, 24.7136, 90], color: '#f59e0b' },
  sa: { name: '南美节点', value: [-74.0721, 4.711, 84], color: '#10b981' }
};

const sceneRoutes = {
  global: [
    { from: 'usWest', to: 'usEast', color: '#22d3ee' },
    { from: 'usEast', to: 'ru', color: '#a855f7' },
    { from: 'me', to: 'sa', color: '#10b981' },
    { from: 'ru', to: 'me', color: '#f59e0b' }
  ],
  black: [
    { from: 'usWest', to: 'usEast', color: '#06b6d4' },
    { from: 'usEast', to: 'ru', color: '#8b5cf6' },
    { from: 'ru', to: 'me', color: '#ef4444' }
  ],
  leak: [
    { from: 'usEast', to: 'ru', color: '#3b82f6' },
    { from: 'ru', to: 'me', color: '#60a5fa' },
    { from: 'usWest', to: 'sa', color: '#22d3ee' }
  ],
  terror: [
    { from: 'me', to: 'ru', color: '#ef4444' },
    { from: 'me', to: 'usEast', color: '#fb7185' },
    { from: 'ru', to: 'usWest', color: '#f97316' }
  ],
  smuggle: [
    { from: 'sa', to: 'usWest', color: '#10b981' },
    { from: 'usEast', to: 'me', color: '#f59e0b' },
    { from: 'me', to: 'ru', color: '#f97316' }
  ],
  drug: [
    { from: 'sa', to: 'usWest', color: '#34d399' },
    { from: 'sa', to: 'usEast', color: '#10b981' },
    { from: 'usEast', to: 'ru', color: '#22c55e' }
  ]
};

const sceneColorMap = {
  global: '#8b5cf6',
  black: '#22d3ee',
  leak: '#3b82f6',
  terror: '#ef4444',
  smuggle: '#f59e0b',
  drug: '#10b981'
};

const loadScript = (src) => {
  return new Promise((resolve, reject) => {
    const exists = Array.from(document.querySelectorAll('script')).some(s => s.src === src);
    if (exists) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(script);
  });
};

const loadFirstAvailableScript = async (sources = []) => {
  let lastError = null;
  for (const src of sources) {
    try {
      await loadScript(src);
      return;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error('No available script source');
};

const syncMapFromWindowEcharts = (mapName) => {
  if (!mapName || echarts.getMap(mapName)) return;
  const winEcharts = window.echarts;
  if (!winEcharts || typeof winEcharts.getMap !== 'function') return;
  const mapRecord = winEcharts.getMap(mapName);
  if (!mapRecord) return;
  const geoJSON = mapRecord.geoJSON || mapRecord.geoJson;
  if (!geoJSON) return;
  echarts.registerMap(mapName, geoJSON, mapRecord.specialAreas || {});
};

const ensureBaseMaps = async () => {
  if (typeof window !== 'undefined') {
    window.echarts = echarts;
  }
  const mapSources = {
    world: [
      'https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/js/world.js',
      'https://unpkg.com/echarts@4.9.0/map/js/world.js'
    ],
    china: [
      'https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/js/china.js',
      'https://unpkg.com/echarts@4.9.0/map/js/china.js'
    ]
  };
  await loadFirstAvailableScript(mapSources.world);
  await loadFirstAvailableScript(mapSources.china);
  syncMapFromWindowEcharts('world');
  syncMapFromWindowEcharts('china');
  return Boolean(echarts.getMap('world') && echarts.getMap('china'));
};

const buildOption = () => {
  const name = props.mode === 'china' ? 'china' : 'world';
  syncMapFromWindowEcharts(name);
  const lineColor = sceneColorMap[props.scene] || '#8b5cf6';
  const points = props.warnings
    .map(w => ({
      name: w.country,
      value: props.countryCoordinates[w.country] ? [...props.countryCoordinates[w.country], w.level === 'high' ? 90 : 65] : null,
      level: w.level
    }))
    .filter(p => p.value);

  const currentRoutes = sceneRoutes[props.scene] || sceneRoutes.global;
  const worldLines = currentRoutes.map((route) => ({
    coords: [worldNodeMap[route.from].value.slice(0, 2), worldNodeMap[route.to].value.slice(0, 2)],
    lineStyle: {
      color: route.color,
      width: 2.6,
      opacity: 0.95,
      curveness: 0.28
    }
  }));

  const worldNodes = Object.values(worldNodeMap);

  if (name === 'world') {
    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          if (Array.isArray(params.value)) {
            return `${params.name}<br/>风险值: ${params.value[2]}`;
          }
          return `${params.name}`;
        }
      },
      geo: {
        map: 'world',
        roam: true,
        zoom: 1,
        layoutCenter: ['50%', '56%'],
        layoutSize: '118%',
        scaleLimit: { min: 1, max: 10 },
        label: { show: false },
        itemStyle: {
          areaColor: '#071a45',
          borderColor: '#1e56c8',
          borderWidth: 1.4,
          shadowColor: 'rgba(30, 86, 200, 0.25)',
          shadowBlur: 10
        },
        emphasis: {
          disabled: true
        }
      },
      series: [
        {
          type: 'lines',
          coordinateSystem: 'geo',
          zlevel: 3,
          effect: {
            show: true,
            period: 4,
            trailLength: 0,
            symbol: 'circle',
            symbolSize: 4,
            color: '#e2e8f0'
          },
          lineStyle: {
            width: 2.4,
            opacity: 0.85,
            curveness: 0.28,
            color: lineColor
          },
          data: worldLines
        },
        {
          type: 'effectScatter',
          coordinateSystem: 'geo',
          zlevel: 4,
          data: worldNodes,
          symbolSize: (val) => Math.max(10, Math.round(val[2] / 8)),
          rippleEffect: {
            period: 3,
            scale: 3,
            brushType: 'stroke'
          },
          itemStyle: {
            color: (params) => params.data.color,
            shadowBlur: 14,
            shadowColor: 'rgba(255, 255, 255, 0.35)'
          },
          label: {
            show: false
          }
        }
      ]
    };
  }

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (Array.isArray(params.value)) {
          return `${params.name}<br/>风险值: ${params.value[2]}`;
        }
        return `${params.name}`;
      }
    },
    geo: {
      map: name,
      roam: true,
      zoom: props.mode === 'china' ? 1.08 : 1,
      center: props.mode === 'china' ? [104, 35.5] : [12, 25],
      layoutCenter: ['50%', '54%'],
      layoutSize: props.mode === 'china' ? '125%' : '118%',
      scaleLimit: { min: 1, max: 12 },
      label: { show: false, color: '#94a3b8' },
      itemStyle: {
        areaColor: '#10213f',
        borderColor: '#2d4d80',
        borderWidth: 1
      },
      emphasis: {
        label: { show: false },
        itemStyle: { areaColor: '#1d4b86' }
      }
    },
    series: [
      {
        type: 'lines',
        coordinateSystem: 'geo',
        zlevel: 2,
        effect: {
          show: true,
          period: 4,
          trailLength: 0.2,
          symbol: 'arrow',
          symbolSize: 6
        },
        lineStyle: {
          width: 2,
          opacity: 0.78,
          curveness: 0.28,
          color: lineColor
        },
        data: [
          { coords: [[-95.7129, 37.0902], [116.4074, 39.9042]] },
          { coords: [[139.6917, 35.6895], [116.4074, 39.9042]] },
          { coords: [[103.8198, 1.3521], [116.4074, 39.9042]] },
          { coords: [[-46.6333, -23.5505], [-95.7129, 37.0902]] }
        ]
      },
      {
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: points,
        symbolSize: (val) => Math.max(8, Math.round(val[2] / 10)),
        rippleEffect: { brushType: 'stroke' },
        itemStyle: { color: lineColor },
        label: {
          show: true,
          position: 'right',
          color: '#dbeafe',
          fontSize: 11,
          formatter: '{b}'
        }
      }
    ]
  };
};

const updateChart = () => {
  if (!chartInstance) return;
  try {
    const currentMap = props.mode === 'china' ? 'china' : 'world';
    syncMapFromWindowEcharts(currentMap);
    if (!echarts.getMap(currentMap)) {
      fallback.value = true;
      return;
    }
    chartInstance.setOption(buildOption(), true);
    fallback.value = false;
  } catch {
    fallback.value = true;
  }
};

const handleResize = () => {
  chartInstance?.resize();
};

const changeScene = (newScene) => {
  emit('update:scene', newScene);
  emit('update:mode', 'world');
};

const changeMode = (newMode) => {
  emit('update:mode', newMode);
};

onMounted(async () => {
  try {
    const loaded = await ensureBaseMaps();
    fallback.value = !loaded;
  } catch {
    fallback.value = true;
  }

  if (chartRef.value && !fallback.value) {
    chartInstance = echarts.init(chartRef.value);
    updateChart();
    chartInstance.on('click', (params) => {
      if (params && params.name) {
        emit('country-click', params.name);
      }
    });
    chartRef.value.addEventListener('contextmenu', (event) => {
      event.preventDefault();
      emit('context-menu', { x: event.clientX, y: event.clientY });
    });
    window.addEventListener('resize', handleResize);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance?.dispose();
});

watch(() => [props.mode, props.scene], updateChart);

defineExpose({
  resize: handleResize
});
</script>

