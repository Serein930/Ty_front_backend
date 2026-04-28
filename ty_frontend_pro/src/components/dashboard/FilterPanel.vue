<template>
  <div class="filter-panel" :class="{ 'collapsed': collapsed }">
    <div class="tech-corner-tl"></div>
    <div class="tech-corner-tr"></div>
    <div class="tech-corner-bl"></div>
    <div class="tech-corner-br"></div>

    <div class="panel-header">
      <div class="panel-title">筛选条件</div>
      <div class="panel-actions">
        <button class="primary" @click="$emit('save')">保存</button>
        <button @click="$emit('reset')">重置</button>
      </div>
    </div>

    <div class="filter-content">
      <div class="filter-grid">
        <div class="filter-label">起止时间:</div>
        <div class="filter-options">
          <div class="chip" :class="{ active: filters.time === 'all' }" @click="setTime('all')">全部</div>
          <div class="chip" :class="{ active: filters.time === 'today' }" @click="setTime('today')">当天</div>
          <div class="chip" :class="{ active: filters.time === '7days' }" @click="setTime('7days')">近7天</div>
          <div class="chip" :class="{ active: filters.time === '30days' }" @click="setTime('30days')">近30天</div>
          <div class="time-picker-btn" :class="{ active: showCustomDate }" @click="toggleCustomDate">
            <i class="fa-regular fa-clock" style="margin-right:5px;"></i> 自定义时间
          </div>
          <div class="custom-date-range" :class="{ show: showCustomDate }">
            <input type="date" class="date-input" :value="filters.customStart" @input="$emit('update:filters', {...filters, customStart: $event.target.value})">
            <span>-</span>
            <input type="date" class="date-input" :value="filters.customEnd" @input="$emit('update:filters', {...filters, customEnd: $event.target.value})">
          </div>
        </div>

        <div class="filter-label">危害性:</div>
        <div class="filter-options">
          <div class="chip" :class="{ active: filters.risk === 'all' }" @click="setFilter('risk', 'all')">全部</div>
          <div class="chip" :class="{ active: filters.risk === 'high' }" @click="setFilter('risk', 'high')">高危</div>
          <div class="chip" :class="{ active: filters.risk === 'mid' }" @click="setFilter('risk', 'mid')">中危</div>
          <div class="chip" :class="{ active: filters.risk === 'low' }" @click="setFilter('risk', 'low')">低危</div>
        </div>

        <div class="filter-label">阅 读:</div>
        <div class="filter-options" style="grid-column: span 3;">
          <div class="chip" :class="{ active: filters.read === 'all' }" @click="setFilter('read', 'all')">全部</div>
          <div class="chip" :class="{ active: filters.read === 'read' }" @click="setFilter('read', 'read')">已读</div>
          <div class="chip" :class="{ active: filters.read === 'unread' }" @click="setFilter('read', 'unread')">未读</div>
        </div>

        <div class="filter-label">媒体类型:</div>
        <div class="filter-options" style="grid-column: span 3;">
          <div class="chip" :class="{ active: filters.media === 'all' }" @click="setFilter('media', 'all')">全部</div>
          <div class="chip" :class="{ active: filters.media === 'Tor' }" @click="setFilter('media', 'Tor')">Tor</div>
          <div class="chip" :class="{ active: filters.media === 'Telegram' }" @click="setFilter('media', 'Telegram')">Telegram</div>
          <div class="chip" :class="{ active: filters.media === 'I2P' }" @click="setFilter('media', 'I2P')">I2P</div>
        </div>

        <div class="filter-label">监测专题:</div>
        <div class="filter-options" style="grid-column: span 3;">
          <div class="chip" :class="{ active: filters.topic === 'all' }" @click="setFilter('topic', 'all')">全部</div>
          <div v-for="t in availableTopics" :key="t" class="chip" :class="{ active: filters.topic === t }" @click="setFilter('topic', t)">
            {{ getTopicName(t) }}
          </div>
        </div>
      </div>
    </div>

    <div class="toggle-btn" @click="$emit('toggle')">
      <i class="fa-solid" :class="collapsed ? 'fa-angle-down' : 'fa-angle-up'"></i>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  filters: {
    type: Object,
    required: true
  },
  collapsed: {
    type: Boolean,
    default: false
  },
  availableTopics: {
    type: Array,
    default: () => []
  },
  getTopicName: {
    type: Function,
    default: (t) => t
  }
});

const emit = defineEmits(['update:filters', 'save', 'reset', 'toggle']);

const showCustomDate = ref(false);

const setTime = (value) => {
  showCustomDate.value = false;
  emit('update:filters', { ...props.filters, time: value });
};

const setFilter = (key, value) => {
  emit('update:filters', { ...props.filters, [key]: value });
};

const toggleCustomDate = () => {
  showCustomDate.value = !showCustomDate.value;
  if (showCustomDate.value) {
    emit('update:filters', { ...props.filters, time: 'custom' });
  }
};
</script>

