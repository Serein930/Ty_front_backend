<template>
  <div class="list-item-wrapper" style="margin-bottom: 10px;">
    <div class="list-item unified-card"
         :class="{
           'read': item.read,
           'selected': item.selected,
           'is-telegram': item.source === 'Telegram'
         }"
         @click="$emit('click', item)">
      <div class="checkbox-area">
        <input type="checkbox" v-model="item.selected" @click.stop>
      </div>
      <div class="item-content">
        <div class="item-header">
          <div class="item-title-wrap">
            <i class="item-source-icon fa-solid" :class="getSourceIcon(item.source)"></i>
            <span class="item-title">{{ getDisplayTitle(item) }}</span>
          </div>
          <span class="badge" :class="item.risk">{{ getRiskText(item.risk) }}</span>
        </div>
        <div class="item-desc">{{ item.content }}</div>
        <div class="item-meta">
          <span class="meta-item clickable-author" title="点击查看该作者所有动态" @click.stop="$emit('filter-author', item.author)">
            作者：<span class="meta-value">{{ item.author }}</span>
          </span>
          <span class="meta-item">
            来自：<span class="meta-value">{{ item.source }}</span>
          </span>
          <span v-if="item.siteName" class="meta-item">
            {{ getSiteLabel(item) }}：<span class="meta-value">{{ item.siteName }}</span>
          </span>
          <span class="item-meta-time">{{ formatTime(item.date) }}</span>
        </div>
        <div class="tag-row">
          <div class="tag clickable-tag" @click.stop="$emit('filter-region', item.region)">
            <i class="fa-solid fa-location-dot"></i> {{ getProvince(item.region) }}
          </div>
          <div class="tag clickable-tag tag-topic" @click.stop="$emit('filter-topic', item.topic)">
            <i class="fa-solid fa-tag"></i> {{ getTopicName(item.topic) }}
          </div>
          <div class="tag clickable-tag tag-industry" @click.stop="$emit('filter-industry', item.industry)">
            {{ getIndustryName(item.industry) }}
          </div>
          <span v-for="(ent, index) in item.entities" :key="index" class="entity-tag" :class="getEntityClass(ent.type)" @click.stop>
            <i :class="getEntityIcon(ent.type)"></i> {{ ent.value }}
          </span>
        </div>
        <div class="item-stats flex items-center" v-if="item.children && item.children.length">
          <button class="cluster-toggle-btn" :class="{ open: item.isExpanded }" @click.stop="$emit('toggle-expand', item)">
            <i class="fa-solid fa-layer-group"></i> {{ item.isExpanded ? '收起' : '展开' }} {{ item.children.length }} 条相似线索
            <i class="fa-solid fa-chevron-down ml-1"></i>
          </button>
        </div>
      </div>
      <div class="item-actions">
        <button class="follow-btn" :class="{ active: item.followed }" @click.stop="$emit('toggle-follow', item)">
          <i class="fa-regular" :class="item.followed ? 'fa-heart-circle-check' : 'fa-heart'"></i>
          {{ item.followed ? '已关注' : '关注' }}
        </button>
        <button class="fp-btn" @click.stop="$emit('mark-fp', item)">
          <i class="fa-solid fa-ban"></i> 误报
        </button>
        <button class="translate-btn" @click.stop="$emit('translate', item)">
          <i class="fa-solid fa-language"></i> 翻译
        </button>
        <button class="export-item-btn" @click.stop="$emit('export', item)">
          <i class="fa-solid fa-download"></i> 导出
        </button>
        <button class="detail-btn" @click.stop="$emit('view-detail', item)">
          <i class="fa-solid fa-eye"></i> 详情
        </button>
      </div>
    </div>

    <!-- 嵌套子线索 -->
    <div class="nested-alerts-container" :class="{ show: item.isExpanded }">
      <div v-for="child in item.children" :key="child.id" class="nested-item">
        <div class="nested-header">
          <span class="text-white font-bold">
            <i class="fa-solid fa-reply text-gray-500 mr-1"></i>{{ child.author }}
          </span>
          <span class="text-gray-500 font-mono">{{ child.date }}</span>
        </div>
        <div class="nested-content">{{ child.content }}</div>
        <div class="mt-2 text-right">
          <button class="detail-btn py-0.5 px-2 text-[10px]" @click.stop="$emit('view-detail', child, item)">独立查看</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  getSourceIcon: {
    type: Function,
    default: () => 'fa-globe'
  },
  getRiskText: {
    type: Function,
    default: (r) => r
  },
  getDisplayTitle: {
    type: Function,
    default: (i) => i.title || i.content?.slice(0, 50) || '无标题'
  },
  getSiteLabel: {
    type: Function,
    default: () => '来源'
  },
  formatTime: {
    type: Function,
    default: (d) => d
  },
  getProvince: {
    type: Function,
    default: (r) => r
  },
  getTopicName: {
    type: Function,
    default: (t) => t
  },
  getIndustryName: {
    type: Function,
    default: (i) => i
  },
  getEntityIcon: {
    type: Function,
    default: () => 'fa-tag'
  },
  getEntityClass: {
    type: Function,
    default: () => ''
  }
});

defineEmits([
  'click',
  'toggle-expand',
  'toggle-follow',
  'mark-fp',
  'translate',
  'export',
  'view-detail',
  'filter-author',
  'filter-region',
  'filter-topic',
  'filter-industry'
]);
</script>

