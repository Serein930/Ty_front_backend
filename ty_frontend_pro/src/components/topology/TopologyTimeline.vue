<template>
  <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-panelBg backdrop-blur-md p-4 rounded-xl border border-primary/30 shadow-glow flex flex-col gap-2 w-1/3 min-w-[450px] z-30 transition-transform duration-300">
    <div class="flex justify-between items-center text-[11px] font-bold text-textGray">
      <span id="time-start">{{ timeStart }}</span>
      <span id="time-current" class="text-white text-sm bg-primary/20 border border-primary/50 px-3 py-1 rounded-full shadow-glow">{{ timeCurrent }}</span>
      <span id="time-end">{{ timeEnd }}</span>
    </div>
    <input
      type="range"
      :value="sliderValue"
      @input="$emit('update:sliderValue', Number($event.target.value))"
      class="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-primary"
      min="0"
      max="100"
    />
    <div class="text-center text-[10px] text-gray-400 mt-1 uppercase tracking-widest">
      <i class="fa-solid fa-clock-rotate-left mr-1"></i> 证据链时间轴推演
    </div>
  </div>
</template>

<script setup>
defineProps({
  timeStart: {
    type: String,
    default: '--'
  },
  timeCurrent: {
    type: String,
    default: '--'
  },
  timeEnd: {
    type: String,
    default: '--'
  },
  sliderValue: {
    type: Number,
    default: 100
  }
});

defineEmits(['update:sliderValue']);
</script>

