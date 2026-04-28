<template>
  <div id="circleMenu" class="circle-menu" v-show="visible" :style="{ left: `${x}px`, top: `${y}px` }" @click.stop>
    <div class="circle-menu-item" style="top:8px;left:65px;" @click="$emit('open-drawer')"><i class="fa-solid fa-earth-asia"></i></div>
    <div class="circle-menu-item" style="top:65px;right:8px;" @click="$emit('show-events')"><i class="fa-solid fa-list"></i></div>
    <div class="circle-menu-item" style="bottom:8px;left:65px;" @click="$emit('show-persons')"><i class="fa-solid fa-user-group"></i></div>
    <div class="circle-menu-item" style="top:65px;left:8px;" @click="$emit('open-org-list')"><i class="fa-solid fa-users"></i></div>
    <div class="circle-menu-center" @click="$emit('close')"><i class="fa-solid fa-times"></i></div>
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
  }
});

defineEmits(['close', 'open-drawer', 'show-events', 'show-persons', 'open-org-list']);
</script>

