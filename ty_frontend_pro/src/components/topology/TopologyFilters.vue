<template>
  <div class="absolute bottom-8 right-8 flex flex-col gap-3 z-30">
    <button
      class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-green-400 hover:text-green-400 transition shadow-lg flex items-center justify-center group relative"
      @click="$emit('save-layout')"
      title="保存当前画布布局坐标"
    >
      <i class="fa-solid fa-floppy-disk"></i>
    </button>
    <button
      class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-blue-400 hover:text-blue-400 transition shadow-lg flex items-center justify-center group relative"
      @click="$emit('load-layout')"
      title="加载已存的画布布局"
    >
      <i class="fa-solid fa-upload"></i>
    </button>
    <div class="w-10 h-px bg-white/20 my-1"></div>
    <button
      id="btn-brush-mode"
      :class="[
        'w-10 h-10 bg-midBlue/90 backdrop-blur border rounded-full transition shadow-lg flex items-center justify-center',
        brushMode ? 'border-primary text-primary' : 'border-white/20 hover:border-primary hover:text-primary'
      ]"
      @click="$emit('toggle-brush')"
      title="开启/关闭实体战术框选 (Brush)"
    >
      <i class="fa-solid fa-object-group"></i>
    </button>
    <button
      class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-primary hover:text-primary transition shadow-lg flex items-center justify-center"
      @click="$emit('reset-zoom')"
      title="缩放自适应重置"
    >
      <i class="fa-solid fa-compress"></i>
    </button>
    <button
      class="w-10 h-10 bg-midBlue/90 backdrop-blur border border-white/20 rounded-full hover:border-warning hover:text-warning transition shadow-lg flex items-center justify-center"
      @click="$emit('toggle-physics')"
      title="暂停/恢复力导向引力"
    >
      <i :class="['fa-solid', physicsPaused ? 'fa-play' : 'fa-pause']" id="physics-icon"></i>
    </button>
  </div>
</template>

<script setup>
defineProps({
  brushMode: {
    type: Boolean,
    default: false
  },
  physicsPaused: {
    type: Boolean,
    default: false
  }
});

defineEmits(['save-layout', 'load-layout', 'toggle-brush', 'reset-zoom', 'toggle-physics']);
</script>

