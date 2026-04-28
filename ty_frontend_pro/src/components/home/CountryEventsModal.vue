<template>
  <div id="countryEventsListModal" class="modal-overlay" v-show="visible" @click.self="$emit('close')">
    <div class="modal-content" style="max-width: 1200px;">
      <div class="modal-header">
        <div class="modal-title">{{ title }}</div>
        <button class="modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <table class="events-table">
          <thead>
            <tr>
              <th>事件ID</th>
              <th>事件名称</th>
              <th>来源类型</th>
              <th>等级</th>
              <th>状态</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in events" :key="`country-ev-${row.id}`">
              <td>CASE-{{ String(row.id).padStart(4, '0') }}</td>
              <td>{{ row.name }}</td>
              <td>{{ row.type }}</td>
              <td>{{ row.level }}</td>
              <td>{{ row.status }}</td>
              <td>{{ row.time }}</td>
              <td><button class="btn-action" @click="$emit('show-detail', row)">详情</button></td>
            </tr>
            <tr v-if="events.length === 0">
              <td colspan="7" style="text-align:center;color:#8c9db5;">暂无事件数据</td>
            </tr>
          </tbody>
        </table>
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
  title: {
    type: String,
    default: '国家事件列表'
  },
  events: {
    type: Array,
    default: () => []
  }
});

defineEmits(['close', 'show-detail']);
</script>

