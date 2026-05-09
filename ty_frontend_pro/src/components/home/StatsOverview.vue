<template>
  <div class="panel" style="grid-column: 2; grid-row: 1;">
    <div class="panel-title"><span class="title-text">主题情报总量</span></div>
    <div class="controls" style="left:auto;right:15px;">
      <select :value="selectedType" @change="$emit('update:selectedType', $event.target.value)">
        <option value="all">请选择类别</option>
        <option value="black">黑灰产</option>
        <option value="fraud">诈骗</option>
        <option value="attack">攻击</option>
      </select>
      <select :value="timeFilter" @change="$emit('update:timeFilter', $event.target.value)">
        <option value="all">全部时间</option>
        <option value="7d">近7天</option>
        <option value="30d">近30天</option>
      </select>
    </div>

    <!-- Loading 骨架 -->
    <div v-if="saLoading" class="center-stats">
      <div class="circle-stat">
        <div class="stat-num skeleton-text">--</div>
        <div class="stat-label">待处理</div>
      </div>
      <div class="main-stat">
        <div class="main-title">当前监测总数</div>
        <div class="main-num skeleton-text">--</div>
        <div class="main-time">{{ nowTimeDisplay }}</div>
      </div>
      <div class="circle-stat">
        <div class="stat-num skeleton-text">--</div>
        <div class="stat-label">已处置</div>
      </div>
    </div>

    <!-- Error 回退 -->
    <div v-else-if="saError" class="center-stats">
      <div class="circle-stat">
        <div class="stat-num" style="color:#888;">--</div>
        <div class="stat-label">待处理</div>
      </div>
      <div class="main-stat">
        <div class="main-title">当前监测总数</div>
        <div class="main-num" style="color:#ff4444;font-size:14px;">加载失败</div>
        <div class="main-time">{{ nowTimeDisplay }}</div>
      </div>
      <div class="circle-stat">
        <div class="stat-num" style="color:#888;">--</div>
        <div class="stat-label">已处置</div>
      </div>
    </div>

    <!-- 正常数据 -->
    <div v-else class="center-stats">
      <div class="circle-stat">
        <div class="stat-num">{{ saSummary.unread }}</div>
        <div class="stat-label">待处理</div>
      </div>
      <div class="main-stat">
        <div class="main-title">当前监测总数</div>
        <div class="main-num">{{ saSummary.total }}</div>
        <div class="main-time">{{ nowTimeDisplay }}</div>
      </div>
      <div class="circle-stat">
        <div class="stat-num">{{ saSummary.read }}</div>
        <div class="stat-label">已处置</div>
      </div>
    </div>

    <!-- 规则明细列表 -->
    <div v-if="!saLoading && filteredSaItems.length" class="rule-list">
      <div
        v-for="item in filteredSaItems"
        :key="item.rule_code"
        class="rule-item"
      >
        <span class="rule-name" :title="item.rule_name">{{ item.rule_name }}</span>
        <span class="rule-counts">
          <span class="rule-unread">{{ currentUnread(item) }} 未读</span>
          <span class="rule-read">{{ currentRead(item) }} 已读</span>
        </span>
      </div>
    </div>
    <div v-else-if="!saLoading && !saError && !filteredSaItems.length" class="rule-empty">
      暂无订阅规则数据
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  warningCount: { type: Number, default: 0 },
  handledCount: { type: Number, default: 0 },
  totalCount: { type: Number, default: 0 },
  nowTimeDisplay: { type: String, default: '' },
  selectedType: { type: String, default: 'all' },
  timeFilter: { type: String, default: 'all' },
  saItems: { type: Array, default: () => [] },
  saSummary: { type: Object, default: () => ({ read: 0, unread: 0, total: 0 }) },
  saLoading: { type: Boolean, default: false },
  saError: { type: String, default: '' },
  filteredSaItems: { type: Array, default: () => [] }
});

const emit = defineEmits(['update:selectedType', 'update:timeFilter']);

const timeKeyMap = { '7d': 'last_7_days', '30d': 'last_30_days', 'all': 'all_time' };

function currentUnread(item) {
  const key = timeKeyMap[props.timeFilter] || 'all_time';
  return item[key]?.unread_count ?? 0;
}

function currentRead(item) {
  const key = timeKeyMap[props.timeFilter] || 'all_time';
  return item[key]?.read_count ?? 0;
}
</script>

<style scoped>
.rule-list {
  max-height: 180px;
  overflow-y: auto;
  margin: 10px 12px 0;
  border-top: 1px solid rgba(71, 93, 132, 0.3);
  padding-top: 8px;
}
.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  font-size: 12px;
  border-bottom: 1px solid rgba(71, 93, 132, 0.15);
}
.rule-item:last-child { border-bottom: none; }
.rule-name {
  color: #9fc3ff;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
}
.rule-counts { display: flex; gap: 8px; flex-shrink: 0; }
.rule-unread { color: #ffaa00; }
.rule-read { color: #4caf50; }
.rule-empty {
  text-align: center;
  color: #666;
  font-size: 12px;
  padding: 20px 0 10px;
}
.skeleton-text { color: #555 !important; }
</style>
