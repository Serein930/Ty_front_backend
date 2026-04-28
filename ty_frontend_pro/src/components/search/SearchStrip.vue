<template>
  <section class="top-search-panel">
    <div class="search-strip">
      <select v-model="currentView" class="control-input view-select">
        <option value="all">全域检索</option>
        <option value="intel">情报线索 (Event)</option>
        <option value="person">人物画像 (Entity)</option>
        <option value="account">账号视图 (Account)</option>
      </select>

      <div class="search-box-wrap">
        <i class="fa-solid fa-magnifying-glass"></i>
        <input
          v-model="inputKeyword"
          class="control-input search-input"
          type="text"
          placeholder="输入关键词、Hash、TG ID、实体或人员别名..."
          @keyup.enter="submitSearch('normal')"
        />
      </div>

      <button class="btn btn-primary" @click="submitSearch('normal')">
        <i class="fa-solid fa-magnifying-glass"></i>
        搜索
      </button>
      <button class="btn btn-ai" @click="submitSearch('ai')">
        <i class="fa-solid fa-wand-magic-sparkles"></i>
        AI深度分析
      </button>
      <button class="btn btn-ghost" @click="resetAll">
        <i class="fa-solid fa-rotate-right"></i>
        重置
      </button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  currentView: {
    type: String,
    default: 'all'
  },
  inputKeyword: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:currentView', 'update:inputKeyword', 'submit-search', 'reset']);

const submitSearch = (mode) => {
  emit('submit-search', mode);
};

const resetAll = () => {
  emit('reset');
};
</script>

