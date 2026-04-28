<template>
  <aside class="right-sidebar panel">
    <div class="right-tabs">
      <button
        class="tab-btn"
        :class="{ active: leftTab === 'filters' }"
        @click="$emit('update:leftTab', 'filters')"
      >属性筛选</button>
      <button
        class="tab-btn"
        :class="{ active: leftTab === 'basket' }"
        @click="$emit('update:leftTab', 'basket')"
      >线索篮 ({{ basketCount }})</button>
    </div>

    <div v-if="leftTab === 'filters'" class="right-scroll-section custom-scrollbar">
      <slot name="filters"></slot>
    </div>

    <div v-else class="right-scroll-section custom-scrollbar">
      <slot name="basket"></slot>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  leftTab: {
    type: String,
    default: 'filters'
  },
  basketCount: {
    type: Number,
    default: 0
  }
});

defineEmits(['update:leftTab']);
</script>

