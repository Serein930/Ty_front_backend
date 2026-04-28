<template>
  <div id="orgListModal" class="modal-overlay" v-show="visible" @click.self="$emit('close')">
    <div class="modal-content" style="max-width: 900px; height: 700px;">
      <div class="modal-header" style="background: #0f1729; border-bottom: 1px solid #1e293b;">
        <div class="modal-title" style="color:#fff;">群组列表 - {{ country }}</div>
        <button class="modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body" style="background: #0f1729; padding: 0;">
        <div class="org-tabs">
          <div class="org-tab-item" :class="{ active: tab === 'telegram' }" @click="$emit('update:tab', 'telegram')">Telegram群组</div>
          <div class="org-tab-item" :class="{ active: tab === 'forum' }" @click="$emit('update:tab', 'forum')">论坛频道</div>
          <div class="org-tab-item" :class="{ active: tab === 'social' }" @click="$emit('update:tab', 'social')">社媒社群</div>
        </div>
        <div class="org-filter-bar">
          <select class="org-select" :value="riskFilter" @change="$emit('update:riskFilter', $event.target.value)">
            <option value="all">风险等级: 全部</option>
            <option value="high">高危</option>
            <option value="medium">中危</option>
            <option value="low">低危</option>
          </select>
        </div>
        <div class="org-list-container">
          <div class="drawer-event-item" v-for="g in orgs" :key="g.id">
            <div class="drawer-event-title">{{ g.name }}</div>
            <div class="drawer-event-meta">
              <span>{{ g.platform }} · {{ g.members }} 成员</span>
              <span>{{ g.risk }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  country: {
    type: String,
    default: '中国'
  },
  tab: {
    type: String,
    default: 'telegram'
  },
  riskFilter: {
    type: String,
    default: 'all'
  },
  orgs: {
    type: Array,
    default: () => []
  }
});

defineEmits(['close', 'update:tab', 'update:riskFilter']);
</script>

