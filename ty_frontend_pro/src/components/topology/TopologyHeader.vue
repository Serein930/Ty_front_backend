<template>
  <header class="h-14 bg-midBlue border-b border-primary/30 flex items-center px-4 justify-between relative z-50 shadow-lg gap-3 overflow-hidden">
    <div class="flex items-center gap-3 shrink-0">
      <div class="w-9 h-9 rounded bg-primary/20 flex items-center justify-center border border-primary/50 text-primary shrink-0">
        <i class="fa-solid fa-radar text-lg animate-pulse-fast"></i>
      </div>
      <div class="shrink-0">
        <h1 class="font-bold text-lg tracking-wide text-white whitespace-nowrap">
          天眼情报 <span class="text-primary">OSINT 溯源引擎</span>
        </h1>
        <p class="text-[10px] text-textGray -mt-1 font-mono whitespace-nowrap">EngineCore v9.0 Multi-Dimensional</p>
      </div>
    </div>

    <div class="flex items-center bg-black/40 border border-white/20 rounded-md px-3 py-1.5 ml-4 w-56 min-w-0 focus-within:border-primary focus-within:shadow-glow transition shadow-inner shrink">
      <i class="fa-solid fa-magnifying-glass text-gray-400 text-xs"></i>
      <input type="text" id="global-search" v-model="searchQuery" placeholder="在当前图中检索..." class="bg-transparent border-none text-xs text-white outline-none w-full ml-2 font-mono" @keyup.enter="executeSearch" />
      <button @click="executeSearch" class="text-xs text-primary hover:text-white transition" title="执行搜索">
        <i class="fa-solid fa-crosshairs"></i>
      </button>
    </div>

    <div class="flex-1"></div>

    <div class="flex gap-2 items-center flex-nowrap whitespace-nowrap shrink-0 overflow-x-auto no-scrollbar">
      <router-link to="/dashboard" class="px-3 py-1.5 text-xs rounded hover:bg-white/10 text-gray-400 hover:text-white transition flex items-center gap-1 border border-transparent hover:border-gray-500 mr-1 whitespace-nowrap shrink-0">
        <i class="fa-solid fa-arrow-left"></i> 返回态势
      </router-link>

      <button @click="$emit('new-project')" class="px-3 py-1.5 text-xs rounded bg-white/10 hover:bg-white/20 border border-white/30 text-white font-bold transition flex items-center gap-2 whitespace-nowrap shrink-0">
        <i class="fa-solid fa-folder-plus text-blue-400"></i> 新建研判专案
      </button>
      <button @click="$emit('open-history')" class="px-3 py-1.5 text-xs rounded bg-white/10 hover:bg-white/20 border border-white/30 text-white font-bold transition flex items-center gap-2 whitespace-nowrap shrink-0">
        <i class="fa-solid fa-clock-rotate-left text-primary"></i> 历史档案库
      </button>
      <div class="w-px h-6 bg-white/20 mx-1 shrink-0"></div>

      <div class="flex bg-darkBlue rounded-lg p-1 border border-white/10 shrink-0 whitespace-nowrap">
        <button
          v-for="view in views"
          :key="view.key"
          :class="[
            'px-3 py-1.5 text-xs rounded transition-all whitespace-nowrap',
            currentView === view.key
              ? 'bg-primary text-darkBlue font-bold shadow-glow'
              : 'hover:bg-white/10 text-textGray hover:text-' + view.color
          ]"
          @click="$emit('switch-view', view.key)"
        >
          <i :class="view.icon" class="mr-1"></i>{{ view.label }}
        </button>
      </div>

      <button @click="$emit('open-report')" class="px-3 py-1.5 text-xs rounded bg-white/10 hover:bg-white/20 border border-white/30 text-white font-bold transition flex items-center gap-2 ml-1 whitespace-nowrap shrink-0">
        <i class="fa-solid fa-file-contract text-danger"></i> 案卷清单
      </button>

      <button @click="$emit('manual-entry')" class="px-3 py-1.5 text-xs rounded bg-white/10 hover:bg-white/20 border border-white/30 text-white font-bold transition flex items-center gap-2 whitespace-nowrap shrink-0">
        <i class="fa-solid fa-pen-to-square text-green-400"></i> 人工录入
      </button>
    </div>

    <div class="flex items-center gap-3 text-sm ml-3 shrink-0 whitespace-nowrap">
      <div class="flex items-center gap-2 cursor-pointer hover:text-white text-textGray border-l border-white/20 pl-3 whitespace-nowrap">
        <img src="/offline/avatar-default.svg" class="w-6 h-6 rounded-full border border-gray-500">
        <span class="text-xs whitespace-nowrap">分析师 (04291)</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  currentView: {
    type: String,
    default: 'all'
  }
});

const emit = defineEmits(['new-project', 'open-history', 'open-report', 'manual-entry', 'switch-view', 'execute-search']);

const searchQuery = ref('');

const views = [
  { key: 'all', label: '全维视界', icon: 'fa-solid fa-circle-nodes', color: 'primary' },
  { key: 'finance', label: '资金', icon: 'fa-solid fa-money-bill-transfer', color: 'warning' },
  { key: 'traffic', label: '基建', icon: 'fa-solid fa-server', color: 'traffic' },
  { key: 'propaganda', label: '宣发', icon: 'fa-solid fa-bullhorn', color: 'propaganda' }
];

const executeSearch = () => {
  emit('execute-search', searchQuery.value);
};
</script>

