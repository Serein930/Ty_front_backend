<template>
  <div id="sysToast" class="sys-toast" :class="{ show: visible }">
    <i class="fa-solid fa-circle-check"></i>
    <span>{{ message }}</span>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: ''
  }
});
</script>

