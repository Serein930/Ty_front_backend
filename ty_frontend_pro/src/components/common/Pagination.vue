<template>
  <div class="pagination" v-if="totalPages > 0">
    <i class="fa-solid fa-angle-left page-arrow" :class="{ disabled: currentPage <= 1 }" @click="changePage(currentPage - 1)"></i>
    <div class="page-num" :class="{ active: currentPage === 1 }" @click="changePage(1)">1</div>
    <span v-if="currentPage > 3">...</span>

    <template v-for="p in totalPages" :key="p">
      <div v-if="p !== 1 && p !== totalPages && Math.abs(p - currentPage) <= 1"
           class="page-num"
           :class="{ active: p === currentPage }"
           @click="changePage(p)">
        {{ p }}
      </div>
    </template>

    <span v-if="currentPage < totalPages - 2">...</span>
    <div v-if="totalPages > 1" class="page-num" :class="{ active: currentPage === totalPages }" @click="changePage(totalPages)">
      {{ totalPages }}
    </div>
    <i class="fa-solid fa-angle-right page-arrow" :class="{ disabled: currentPage >= totalPages }" @click="changePage(currentPage + 1)"></i>
    <div class="page-info">第 {{ currentPage }}/{{ totalPages }} 页，共 {{ total }} 条数据</div>
  </div>
</template>

<script setup>
const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  totalPages: {
    type: Number,
    default: 1
  },
  total: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['change']);

const changePage = (page) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('change', page);
  }
};
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  margin-top: auto;
}

.page-arrow {
  cursor: pointer;
  color: var(--text-dim);
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.2s;
}

.page-arrow:hover:not(.disabled) {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent-blue);
}

.page-arrow.disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-num {
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-dim);
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.2s;
}

.page-num:hover {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent-blue);
}

.page-num.active {
  background: var(--accent-blue);
  color: #fff;
  font-weight: 600;
}

.page-info {
  font-size: 12px;
  color: var(--text-dim);
  margin-left: 12px;
}
</style>
