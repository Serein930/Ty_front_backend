<template>
  <div class="map-context-menu" v-show="visible" :style="{ left: `${x}px`, top: `${y}px` }" @click.stop>
    <div class="map-context-header">{{ country }} 快捷操作</div>
    <div class="map-context-body">
      <button class="btn-action" style="margin-bottom:8px; width:100%;" @click="$emit('open-circle-menu')">
        <i class="fa-solid fa-bullseye"></i> 打开战术菜单
      </button>
      <button class="btn-action" style="width:100%;" @click="$emit('open-drawer')">
        <i class="fa-solid fa-address-card"></i> 打开地区档案
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  x: {
    type: Number,
    default: 0
  },
  y: {
    type: Number,
    default: 0
  },
  country: {
    type: String,
    default: '中国'
  }
});

defineEmits(['close', 'open-circle-menu', 'open-drawer']);
</script>

