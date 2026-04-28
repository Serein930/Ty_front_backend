<template>
  <div id="personsListModal" class="modal-overlay" v-show="visible" @click.self="$emit('close')">
    <div class="modal-content" style="max-width: 1200px;">
      <div class="modal-header">
        <div class="modal-title">重点人物列表 - {{ country === 'all' ? '全域' : country }}</div>
        <button class="modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <table class="events-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>别名</th>
              <th>地区</th>
              <th>平台</th>
              <th>风险分</th>
              <th>标签</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in persons" :key="`person-${row.id}`">
              <td>{{ row.id }}</td>
              <td>{{ row.alias }}</td>
              <td>{{ row.country }}</td>
              <td>{{ row.platform }}</td>
              <td>{{ row.score }}</td>
              <td>{{ row.tags?.join(' / ') || '' }}</td>
              <td>
                <button class="btn-action" @click="$emit('show-detail', row)">画像</button>
                <button class="btn-action" @click="$emit('clone', row)">分身</button>
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
  persons: {
    type: Array,
    default: () => []
  },
  country: {
    type: String,
    default: 'all'
  }
});

defineEmits(['close', 'show-detail', 'clone']);
</script>

