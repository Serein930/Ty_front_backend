<template>
  <div id="eventsListModal" class="modal-overlay" v-show="visible" @click.self="$emit('close')">
    <div class="modal-content" style="max-width: 1200px;">
      <div class="modal-header">
        <div class="modal-title">事件列表</div>
        <button class="modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <table class="events-table">
          <thead>
            <tr>
              <th>事件ID</th>
              <th>事件名称</th>
              <th>国家</th>
              <th>等级</th>
              <th>状态</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in events" :key="`ev-${row.id}`">
              <td>CASE-{{ String(row.id).padStart(4, '0') }}</td>
              <td>{{ row.name }}</td>
              <td>{{ row.country }}</td>
              <td>{{ row.level }}</td>
              <td>{{ row.status }}</td>
              <td>{{ row.time }}</td>
              <td>
                <button class="btn-action" @click="$emit('show-detail', row)">详情</button>
              </td>
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
  events: {
    type: Array,
    default: () => []
  }
});

defineEmits(['close', 'show-detail']);
</script>

